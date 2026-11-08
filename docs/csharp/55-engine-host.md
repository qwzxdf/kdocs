---
title: 第 55 章 エンジンをサーバーにする：EngineHost
tags:
  - C#連携
---

# 第 55 章 エンジンをサーバーにする：EngineHost

前の章までで、エディタから命令を送る側は揃いました。受ける側がまだありません。この章では、エンジンを動かす専用の exe、`EngineHost` を作ります。やることは 3 つです。パイプで受けた命令を `EngineApi` の関数に振り分けること、エディタが起動して見張ること、エディタが消えたらエンジンも消えることです。

もう 1 つこの章で決めておくことがあります。エンジンを触るスレッドです。第 38 章ではエンジンを触るのは描画スレッドだけという約束を作りました。パイプの受け口が別のスレッドにあると、この約束を守るために命令を描画スレッドへ渡す仕組みがまた要ります。そこで、パイプを読むスレッドがそのままエンジンを動かすスレッドになる作りにします。

!!! info "このページを読む前に"
    - [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)（`ServeOnce` と、メッセージの形）
    - [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)（命令の名前と形）
    - [第 32 章 EngineApi：C の入口を作る](32-engine-api.md)（振り分け先の `me_*` 関数）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）


!!! abstract "この章で足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `EngineHost/EngineHost.vcxproj`（新規） | exe のプロジェクト。`EngineApi` に依存する |
    | `EngineHost/Server.cpp`（第 53 章から移す） | パイプの読み書きと `ServeOnce` |
    | `EngineHost/Dispatch.cpp`（新規） | 命令の名前から、`me_*` の呼び出しへ振り分ける |
    | `EngineHost/main.cpp`（新規） | 起動の引数、終了コード、ログ |
    | `Editor/Engine/EngineProcess.cs`（新規） | エンジンの起動、接続の待ち、見張り、後始末 |


## プロセスとスレッドの配置

最初に、全体の配置を決めます。

<svg class="fig flow" viewBox="0 0 720 290" role="img" aria-label="エディタがエンジンのプロセスを起動し、ジョブ オブジェクトに入れる。エンジンはパイプのスレッドがそのままエンジンのスレッド"><defs><marker id="ehA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">プロセスとスレッドの配置</text><rect x="16" y="44" width="300" height="190" rx="14" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="166" y="66" text-anchor="middle" style="font-size:12px;font-weight:600">Editor.exe</text><rect x="32" y="80" width="130" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="97" y="99" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">UI スレッド</text><rect x="172" y="80" width="130" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="237" y="99" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">描画スレッド</text><rect x="32" y="130" width="270" height="38" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="167" y="149" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">EngineProcess ＋ EngineClient</text><text x="167" y="196" text-anchor="middle" style="font-size:11px;font-weight:400">起動・見張り・後始末（ジョブ オブジェクト）</text><text x="167" y="214" text-anchor="middle" style="font-size:11px;font-weight:400">描画スレッドが Call で待つ。UI スレッドは待たない</text><rect x="404" y="44" width="300" height="190" rx="14" fill="rgba(148,163,184,0.10)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6 5"/><text x="554" y="66" text-anchor="middle" style="font-size:12px;font-weight:600">EngineHost.exe</text><rect x="420" y="80" width="268" height="38" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="554" y="99" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">メイン スレッド ＝ パイプ ＝ エンジン</text><rect x="420" y="130" width="268" height="38" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="554" y="149" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">Dispatch → me_* → Engine</text><text x="554" y="196" text-anchor="middle" style="font-size:11px;font-weight:400">命令は届いた順に 1 つずつ実行される</text><text x="554" y="214" text-anchor="middle" style="font-size:11px;font-weight:400">エンジンを触るスレッドは 1 つだけ</text><line x1="316" y1="99" x2="404" y2="99" stroke="currentColor" stroke-width="2" marker-end="url(#ehA)"/><line x1="404" y1="123" x2="316" y2="123" stroke="currentColor" stroke-width="2" marker-end="url(#ehA)"/><text x="360" y="90" text-anchor="middle" style="font-size:11px;font-weight:400">パイプ</text><text x="360" y="270" text-anchor="middle" style="font-size:12px;font-weight:400">エディタがエンジンを起動する。エディタが消えたら、OS がエンジンも終了させる。</text></svg>

`EngineHost` のメイン スレッドがパイプを読み命令を実行し、返事を書くという 1 本の流れをすべて受け持ちます。第 53 章の `ServeOnce` は 1 つの接続を 1 つのスレッドで読み書きしているので、そのまま使えます。エンジンの作成も描画も破棄も同じスレッドで起きます。スレッドの約束を構造で守る作りです。

この作りの代償は命令の実行中は次の命令を読めないことです。1 フレームの描画に 10 ms かかる `tick` を実行している間、エディタの別の命令は待たされます。エディタの描画スレッドが 1 本の流れで 1 つずつ送るなら問題になりません。複数のスレッドから同時に命令が来る設計にしたくなったときは、パイプのスレッドとエンジンのスレッドを分けて、間に命令のキューを置きます。

## 命令を振り分ける

第 53 章の `HandleRequest` は、`if` を並べて命令を振り分けていました。命令が増えると長くなるので、命令の名前から関数を引く表（`unordered_map`）に変えます。

```cpp title="EngineHost/Dispatch.cpp（新規。コンパイルしていない）"
#include <functional>
#include <stdexcept>
#include <string>
#include <unordered_map>

#include <nlohmann/json.hpp>

#include "EngineApi/EngineApi.h"

using json = nlohmann::json;
using Handler = std::function<json(const json& args)>;

namespace {

// EngineApi の失敗（エラー コード）を、例外に変える。Dispatch が捕まえて、ok:false の返事にする
void Check(MeResult result) {
  if (result != ME_OK) throw std::runtime_error(me_get_last_error());
}

// initialize の前に呼ばれた命令は、分かりやすく失敗させる
MeEngine* Need(MeEngine* engine) {
  if (engine == nullptr) throw std::runtime_error("engine is not initialized");
  return engine;
}

}  // namespace
```

`Check` は第 33 章の `ThrowIfFailed` の C++ 版です。`EngineApi` の関数は失敗をエラー コードで返し、理由を `me_get_last_error` で渡します。それを例外にしておくと各命令の中身を成功した場合だけ書けます。例外は次の `Dispatch` で止まります。

`Need` は `initialize` より前に `tick` や `scene_create` が届いた場合の備えです。エンジンが `nullptr` のまま `me_engine_tick` に渡すと `EngineApi` 側が `ME_ERROR_INVALID_ARGUMENT` を返す設計ですが、そこで返る理由より「初期化されていません」のほうが、エディタ側の人には分かりやすくなります。

```cpp title="EngineHost/Dispatch.cpp（続き）"
std::unordered_map<std::string, Handler> BuildHandlers(MeEngine*& engine) {
  std::unordered_map<std::string, Handler> h;

  h["ping"] = [](const json&) { return json("pong"); };

  h["initialize"] = [&engine](const json& a) {
    if (engine != nullptr) throw std::runtime_error("already initialized");
    MeEngineDesc desc = {};
    desc.window = nullptr;                      // 画面外の描画先を使う（第 56 章）
    desc.width = a.at("width");
    desc.height = a.at("height");
    Check(me_engine_create(&desc, &engine));
    return json(nullptr);
  };

  h["resize"] = [&engine](const json& a) {
    Check(me_engine_resize(Need(engine), a.at("width"), a.at("height")));
    return json(nullptr);
  };

  h["tick"] = [&engine](const json& a) {
    Check(me_engine_tick(Need(engine), a.at("dt")));
    return json(nullptr);
  };

  h["get_frame_count"] = [&engine](const json&) {
    uint64_t count = 0;
    Check(me_engine_get_frame_count(Need(engine), &count));
    return json{{"count", count}};
  };

  h["scene_create"] = [&engine](const json& a) {
    const std::string name = a.at("name");
    Check(me_scene_create_object(Need(engine), a.at("id"), a.at("parent"), name.c_str()));
    return json(nullptr);
  };

  h["scene_destroy"] = [&engine](const json& a) {
    Check(me_scene_destroy_object(Need(engine), a.at("id")));
    return json(nullptr);
  };

  h["shutdown"] = [](const json&) { return json(nullptr); };   // 返事だけ返す。接続が閉じれば、ループは自然に終わる

  // scene_set_parent、scene_set_name、scene_set_transform、scene_set_color も同じ形
  return h;
}
```

どの命令も `a.at("...")` で `args` から値を取り `me_*` を呼び `Check` で失敗を例外にして、結果を返すという同じ形です。`at` はキーがないと例外を投げるので、「引数が足りない」命令も `ok: false` の返事になります。

`engine` を参照（`MeEngine*&`）で受け取っているのは、`initialize` が `engine` を作るからです。エンジンは、`main` が持ちます。`BuildHandlers` はそれを借りるだけです。

`shutdown` が何もしないのは意図的です。エディタは `shutdown` を送ったあとパイプを閉じます。すると、`ReadMessage` が `false` を返し、`ServeOnce` から抜けて、`main` がエンジンを破棄して終わります。終了の道が「エディタが消えた」場合と同じ 1 本になります。

```cpp title="EngineHost/Dispatch.cpp（続き）"
std::string Dispatch(const std::unordered_map<std::string, Handler>& handlers, const std::string& text) {
  json reply = {{"id", nullptr}, {"ok", false}};
  try {
    const json req = json::parse(text);
    reply["id"] = req.at("id");
    const std::string cmd = req.at("cmd");

    const auto it = handlers.find(cmd);
    if (it == handlers.end()) throw std::runtime_error("unknown cmd: " + cmd);

    const json args = req.contains("args") ? req["args"] : json::object();
    reply["result"] = it->second(args);
    reply["ok"] = true;
  } catch (const std::exception& e) {
    reply["ok"] = false;
    reply["error"] = e.what();                  // 例外はここで止める（境界の約束）
  }
  return reply.dump();
}
```

第 53 章の `HandleRequest` と比べて、`if` の列が表の検索に変わっただけです。未知の命令は `unknown cmd` の失敗で返ります。`args` がない命令（`ping` など）には空のオブジェクトを渡して、`at` で落ちないようにしています。

## main：起動の引数、終了コード、ログ

```cpp title="EngineHost/main.cpp（新規。コンパイルしていない）"
#include <windows.h>

#include <cstdio>
#include <functional>
#include <string>
#include <unordered_map>

#include <nlohmann/json.hpp>

#include "EngineApi/EngineApi.h"

using Handler = std::function<nlohmann::json(const nlohmann::json&)>;

bool ServeOnce(const wchar_t* pipe_name, const std::function<std::string(const std::string&)>& handler);
std::unordered_map<std::string, Handler> BuildHandlers(MeEngine*& engine);
std::string Dispatch(const std::unordered_map<std::string, Handler>& handlers, const std::string& text);

namespace {

void OnEngineLog(MeLogLevel level, const char* message, void*) {
  // 標準エラーに 1 行ずつ書く。エディタが読んで、ログ パネルに出す（出所は Engine）
  fprintf(stderr, "[%d] %s\n", level, message);
  fflush(stderr);
}

}  // namespace

int wmain(int argc, wchar_t** argv) {
  std::wstring pipe_name = L"\\\\.\\pipe\\MiniEngine";
  for (int i = 1; i + 1 < argc; ++i) {
    if (std::wstring(argv[i]) == L"--pipe") pipe_name = L"\\\\.\\pipe\\" + std::wstring(argv[i + 1]);
  }

  me_set_log_callback(&OnEngineLog, nullptr);

  MeEngine* engine = nullptr;
  auto handlers = BuildHandlers(engine);

  const bool served = ServeOnce(pipe_name.c_str(), [&](const std::string& request) {
    return Dispatch(handlers, request);
  });

  me_engine_destroy(engine);                 // nullptr でも安全（第 32 章）
  return served ? 0 : 2;                     // 2 = パイプを作れなかった（同じ名前の EngineHost が先にいる）
}
```

起動の引数は `--pipe 名前` だけです。エディタが毎回違う名前を渡せば、エディタを 2 つ開いてもエンジンが取り合いになりません（名前の決め方は、第 57 章で扱います）。

終了コードは 2 つだけ決めます。`0` はエディタとの接続が終わって、普通に終わったことを表します。`2` はパイプを作れなかったことです。第 53 章で確かめたとおり同じ名前のパイプが先にあると、`CreateNamedPipeW` が失敗します。エディタの `EngineProcess` は起動の途中でエンジンが終わったとき、この終了コードを例外に載せます。落ちた場合は OS が `0xC0000005` のような値を入れるので、同じ場所で原因の見当がつきます。

`me_set_log_callback` に標準エラーへ書く関数を渡しています。エンジンの `LogInfo` がエディタのログ パネルに出る流れは、第 33 章で C# のコールバックとして作りました。別プロセスでは関数ポインターを渡せないので、標準エラーに出してエディタの側で拾います。次の節の `EngineProcess` がその受け口です。

`main` を `wmain` にしているのは引数を UTF-16 で受けるためです。パイプの名前は ASCII だけの前提でも動きますが、Windows の API に渡す文字列と同じ型のほうが、変換の事故が起きません。

## エディタ側：EngineProcess

エンジンを起動しパイプが繋がるまで待ち見張って、終わるときに後始末をするクラスです。

```csharp title="Editor/Engine/EngineProcess.cs（新規）"
using System.Diagnostics;
using System.Runtime.InteropServices;

namespace Editor.Engine;

// エンジンのプロセス（EngineHost.exe）を起動して、見張る。
// エディタが強制終了しても、エンジンが残らないように、ジョブ オブジェクトに入れる。
public sealed partial class EngineProcess : IDisposable
{
    private readonly Process _process;
    private readonly nint _job;

    public EngineClient Client { get; }

    // エンジンが標準エラーに書いた 1 行ごとに呼ばれる（ログ パネルへ流す用）
    public event Action<string>? LogLine;
    public int ProcessId => _process.Id;
    public bool HasExited => _process.HasExited;

    private EngineProcess(Process process, nint job, EngineClient client)
    {
        _process = process;
        _job = job;
        Client = client;
    }
```

`EngineProcess` は `EngineClient` を持ちます。エンジンを起動する責任とエンジンと話す道具を 1 つのオブジェクトにまとめています。第 54 章の `RemoteEngineService` にはこの `Client` を渡します。

```csharp title="Editor/Engine/EngineProcess.cs（続き）"
    // エンジンを起動して、パイプが繋がるまで待つ。繋がる前にエンジンが終わったら、例外にする
    public static async Task<EngineProcess> StartAsync(string exePath, string pipeName, TimeSpan timeout)
    {
        var info = new ProcessStartInfo(exePath, $"--pipe {pipeName}")
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardError = true,
        };
        Process process = Process.Start(info) ?? throw new InvalidOperationException("エンジンを起動できません");
        nint job = CreateKillOnCloseJob(process);

        var engineProcess = new EngineProcess(process, job, new EngineClient(pipeName));
        process.ErrorDataReceived += (_, e) => { if (e.Data is not null) engineProcess.LogLine?.Invoke(e.Data); };
        process.BeginErrorReadLine();                              // 起動直後から読む（読まないと、書き込みがたまって止まる）

        var deadline = DateTime.UtcNow + timeout;
        try
        {
            while (true)
            {
                if (process.HasExited)
                {
                    throw new InvalidOperationException($"エンジンが起動中に終了しました（終了コード 0x{process.ExitCode:X}）");
                }
                try
                {
                    await engineProcess.Client.ConnectAsync(timeoutMs: 300);   // 短く待っては、プロセスの生死を確かめる
                    return engineProcess;
                }
                catch (TimeoutException) when (DateTime.UtcNow < deadline) { }
            }
        }
        catch
        {
            engineProcess.Dispose();                               // 起動に失敗したら、エンジンを残さない
            throw;
        }
    }
```

`StartAsync` の要は接続の待ち方です。第 53 章の `ConnectAsync` はパイプができるまで待ち続けます。エンジンが起動の途中で落ちると、パイプは永遠にできないので時間切れまで待つだけになります。そこで、300 ミリ秒ずつ短く待って、そのたびに `process.HasExited` を見ます。終わっていたらすぐに「終了コード 0x…」つきの例外にします。起動の失敗が「5 秒待たされたあとの時間切れ」ではなく、「すぐに分かる理由つきの失敗」になります。

`RedirectStandardError` と `BeginErrorReadLine` はエンジンの標準エラーを 1 行ずつ `LogLine` イベントに流すための設定です。`BeginErrorReadLine` を接続を待つ前の起動の直後に呼ぶのには理由があります。標準エラーの書き込みは読み手がいないと OS のバッファーが満杯になった時点で、書き込む側（エンジン）が止まってしまうからです。

`catch` で `Dispose` を呼ぶのは失敗したときに、起動したエンジンのプロセスを残さないためです。起動に失敗してからエンジンが 5 秒間生きたままパイプの名前を握り続けると、次の起動が `2` で失敗します。

```csharp title="Editor/Engine/EngineProcess.cs（続き）"
    public void Dispose()
    {
        try { if (!_process.HasExited) _process.Kill(entireProcessTree: true); } catch (InvalidOperationException) { }
        _process.Dispose();
        if (_job != 0) CloseHandle(_job);
    }
```

`Dispose` は、エンジンを強制的に終了させます。穏やかに終わらせたいときは、先に `RemoteEngineService.Dispose`（`shutdown` を送る）を呼びます。そのあとでも、`Dispose` はプロセスが残っていないことを保証します。

### ジョブ オブジェクトで、エンジンを残さない

エディタが強制終了すると `Dispose` は呼ばれません。そのとき、固まっていたエンジンがプロセスとして残る可能性があります。エンジンがパイプを読んでいれば、パイプが切れて自分で終わります。しかし、固まっていて読んでいないといつまでも残ります。そこで、エンジンを Windows のジョブ オブジェクトに入れます。ジョブ オブジェクトはプロセスのグループで、ジョブのハンドルが閉じられたとき、中のプロセスをまとめて終了させる設定ができます。エディタが消えれば、OS がハンドルを閉じるので、エンジンも一緒に終わります。

```csharp title="Editor/Engine/EngineProcess.cs（続き）"
    private const int JobObjectExtendedLimitInformation = 9;
    private const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000;

    [StructLayout(LayoutKind.Sequential)]
    private struct JobBasicLimit
    {
        public long PerProcessUserTimeLimit, PerJobUserTimeLimit;
        public uint LimitFlags;
        public nuint MinimumWorkingSetSize, MaximumWorkingSetSize;
        public uint ActiveProcessLimit;
        public nuint Affinity;
        public uint PriorityClass, SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct IoCounters
    {
        public ulong ReadOperationCount, WriteOperationCount, OtherOperationCount;
        public ulong ReadTransferCount, WriteTransferCount, OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct JobExtendedLimit
    {
        public JobBasicLimit Basic;
        public IoCounters Io;
        public nuint ProcessMemoryLimit, JobMemoryLimit, PeakProcessMemoryUsed, PeakJobMemoryUsed;
    }

    private static nint CreateKillOnCloseJob(Process process)
    {
        nint job = CreateJobObjectW(0, null);
        if (job == 0) return 0;                                   // 失敗しても、エンジンは動かせる（保険が効かないだけ）

        var limit = new JobExtendedLimit();
        limit.Basic.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        if (!SetInformationJobObject(job, JobObjectExtendedLimitInformation, ref limit, (uint)Marshal.SizeOf<JobExtendedLimit>())
            || !AssignProcessToJobObject(job, process.Handle))
        {
            CloseHandle(job);
            return 0;
        }
        return job;
    }

    [LibraryImport("kernel32.dll", StringMarshalling = StringMarshalling.Utf16)]
    private static partial nint CreateJobObjectW(nint attributes, string? name);

    [LibraryImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool SetInformationJobObject(nint job, int infoClass, ref JobExtendedLimit info, uint size);

    [LibraryImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool AssignProcessToJobObject(nint job, nint process);

    [LibraryImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool CloseHandle(nint handle);
}
```

構造体 3 つは Win32 の `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` と同じ並びです。`LimitFlags` の `0x2000`（`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`）が「ジョブのハンドルが閉じたら、中のプロセスを終了する」の指定です。`SetInformationJobObject` に渡す情報の種類 `9` は拡張の制限情報（`JobObjectExtendedLimitInformation`）を表します。`Marshal.SizeOf` で構造体の大きさを渡しているのは、x64 で 144 バイトになる並びを `SetInformationJobObject` が検査するからです。大きさが違うと呼び出しが失敗します。

ジョブへの登録が失敗してもエンジンの起動は止めません。保険が効かなくなるだけで普通の動作に影響しないからです。ハンドルは `EngineProcess` が持つ間、閉じません。閉じるのは `Dispose` かエディタのプロセスが終わったときです。

## 動かして確かめる

エンジンの本物の代わりに前の章のテスト用のサーバー（`ServeOnce` に `ping` などを返すだけのハンドラーを付けたもの）を、`EngineHost.exe` の代役にして `EngineProcess` を動かしました。

```csharp title="確認用のコンソール（Editor には入れない）"
using var engine = await EngineProcess.StartAsync(server, "MiniEngineTest", TimeSpan.FromSeconds(5));
var reply = await engine.Client.RequestAsync("ping");
Console.WriteLine($"started pid={engine.ProcessId}, ping -> {reply.GetProperty("result").GetString()}");
int pid = engine.ProcessId;
engine.Dispose();
await Task.Delay(300);
Console.WriteLine("after Dispose, process exists: " + Process.GetProcesses().Any(p => p.Id == pid));

// 存在しない exe を指定すると
try { using var e = await EngineProcess.StartAsync(@"C:\no\such\engine.exe", "X", TimeSpan.FromSeconds(1)); }
catch (Exception e) { Console.WriteLine($"missing exe -> {e.GetType().Name}"); }
```

```text title="実行結果"
started pid=18076, ping -> pong
after Dispose, process exists: False
missing exe -> Win32Exception
```

エンジンが起動しパイプが繋がって `ping` に `pong` が返り `Dispose` でプロセスが消えることを確かめました。存在しない exe を指定すると、`Process.Start` が `Win32Exception` を投げます。

ジョブ オブジェクトへの登録が成功すること（ハンドルが 0 でないこと）と、`JobExtendedLimit` の大きさが 144 バイトになることも実際に動かして確かめました。

確かめていないことが 2 つあります。1 つはエディタが強制終了したとき、固まったエンジンがジョブ オブジェクトで確実に消えることです。テスト用のサーバーはパイプが切れると自分で終わる作りなので、手元の確認ではジョブ オブジェクトの効果と区別がつきませんでした。もう 1 つは `EngineHost` 本体（`Dispatch.cpp` と `main.cpp`）で、nlohmann と `EngineApi` が要るため、コンパイルしていません。`EngineProcess` は、.NET 8 向けのコンソール アプリで、コンパイルして実行しました。

## 2 つのプロセスをデバッグする

エディタがエンジンを起動する作りでは、Visual Studio のデバッグは、エディタだけに付きます。エンジンの中で止めたいときは 2 つの方法があります。

1 つは Visual Studio の「デバッグ」→「プロセスにアタッチ」で、`EngineHost.exe` を選ぶ方法です。エンジンはエディタが起動した直後にすぐ動き出すので、起動の途中の問題を調べるには向きません。

もう 1 つはエディタに起動の引数 `--no-spawn` を足して、エンジンを起動せずにすでにあるパイプに繋ぐだけにする方法です。ソリューションの「複数のスタートアップ プロジェクト」で、`EngineHost` を先に `Editor` を後に両方「開始」にします。エンジンは Visual Studio のデバッガーの下で起動し、`main` の最初から止められます。`EngineProcess.StartAsync` に起動を省いて接続だけをする版を足す作りです。この章では書きません。

## よくあるミス

??? failure "EngineHost が、起動した直後に終了コード 2 で終わる"
    同じ名前のパイプを持つ `EngineHost` が、すでにいます。前に起動したエンジンが残っているか、エディタを 2 つ開いて同じ名前を使っています。タスク マネージャーで古い `EngineHost.exe` を終了させるか、起動のたびに違うパイプ名を使います。

??? failure "エンジンのログが、ログ パネルに出ない"
    `RedirectStandardError = true` にしていないか `BeginErrorReadLine` を呼んでいません。呼んでいても `LogLine` の購読が起動の後だと起動直後の行が捨てられます。`StartAsync` の戻り値を受ける前に出た行はどこにも届きません。起動のログを残したいときは `EngineHost` のほうでファイルにも書きます。

??? failure "エンジンの起動中に、エディタが数秒固まる"
    `StartAsync` を UI スレッドで `.Result` で待っています。`await` して呼び起動中は「エンジンを起動しています」の表示を出してください。エンジンの起動は GPU の初期化を含むので、数百ミリ秒から数秒かかります。

??? failure "エンジンのウィンドウが、一瞬だけ見える"
    `CreateNoWindow = true` を付け忘れています。`EngineHost` はウィンドウを持たない作りですが、コンソール アプリとして起動すると、黒い窓が出ます。プロジェクトのサブシステムを「Windows」にする方法もあります。

??? failure "命令に、`engine is not initialized` と答える"
    `Initialize` より前に、別の命令を送っています。`RemoteEngineService` の `Initialize` が成功してから、`SceneEngineSync` などの購読を始めてください。

## この章のまとめ

- `EngineHost` はパイプを読む 1 本のスレッドが、そのままエンジンを動かす。エンジンを触るスレッドが 1 つだけになり、第 38 章の約束が構造で守られる。
- 命令は名前から関数を引く表で振り分ける。`EngineApi` のエラー コードは例外にして、`Dispatch` で止め `ok: false` の返事にする。
- 終了の道は 1 本。エディタがパイプを閉じる（または消える）と、エンジンは自分で終わる。
- `EngineProcess` が起動、接続の待ち、見張り、後始末を受け持つ。待つときは短く区切ってプロセスの生死を見る。
- エディタが強制終了してもエンジンが残らないように、ジョブ オブジェクトに入れる。ただし、効果は手元では確かめていない。

次の章では別のプロセスのエンジンが描いた絵をエディタのビューポートに出します。

[第 56 章 ビューポートを別プロセスから受ける](56-remote-viewport.md) へ進みます。
