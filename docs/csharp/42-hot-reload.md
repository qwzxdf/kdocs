---
title: 第 42 章 ホット リロード
tags:
  - C#連携
---

# 第 42 章 ホット リロード

この章では、<strong>エディタを動かしたまま、`Game.dll` を差し替える<strong>仕組み（ホット リロード）を作ります。ゲームのコードを書き換えて、ビルドすると、</strong>数秒後には動いているゲームに反映されています</strong>。ゲームの調整（数値、挙動）の試行錯誤の速さが、何倍にもなる機能です。

## この章の考え方

第 41 章で、ゲームを DLL に分けました。差し替えるには、次の手順が要ります。

```text
1. 新しい Game.dll ができる（ビルド）
2. 古いゲームの「状態」を保存する
3. 古いゲームを壊し、古い DLL を外す
4. 新しい DLL を読み込み、新しいゲームを作る
5. 保存した「状態」を、新しいゲームに戻す
```

簡単に見えますが、5 つの罠があります。

| 罠 | 内容 | 対処 |
| --- | --- | --- |
| <strong>ファイルのロック</strong> | 読み込み中の DLL は、Windows が<strong>上書きを禁止</strong>する。ビルドが「書き込めない」で失敗する | <strong>コピーを読み込む</strong>（シャドウ コピー） |
| <strong>PDB のロック</strong> | デバッガーが `.pdb` を掴む。リンカーが書けない | PDB の名前を<strong>毎回変える</strong> |
| <strong>状態が消える</strong> | DLL の中の `static` 変数やゲームのオブジェクトは、DLL を外すと消える | 状態を<strong>エンジンのメモリに保存</strong>して、戻す |
| <strong>古いコードへの参照</strong> | エンジンが、古い DLL の関数やクラスへのポインターを持ち続けると、外した後にクラッシュ | 差し替えの前に、<strong>参照を全部手放す</strong> |
| <strong>失敗したとき</strong> | 新しい DLL が壊れていたら、古いものも消えて、何もなくなる | <strong>新しい物を先に読み込み</strong>、成功してから古い物を捨てる |

## この章のゴール

- ゲームを書き換えてビルドすると、エディタが自動で検出して、差し替える。
- Play 中でも、差し替わり、<strong>回転の角度が飛ばない</strong>（状態を引き継ぐ）。
- 新しい DLL の読み込みに失敗しても、古いゲームが動き続ける。
- エディタから、ゲームのビルドと、手動のリロードができる。

## 手順 1：シャドウ コピーでロックを避ける

エンジンは、`Game.dll` そのものではなく、<strong>コピー</strong>を読み込みます。元の `Game.dll` は、誰にも掴まれないので、ビルドがいつでも上書きできます。

`Engine\src\GameModule.cpp` に追加します。

```cpp
#include <atomic>
#include <filesystem>

namespace {

// 元の DLL を、一時フォルダーにコピーする。ファイル名は、呼ぶたびに変わる。
std::wstring MakeShadowCopy(const std::wstring& original, std::string* error) {
  static std::atomic<int> counter{0};

  std::filesystem::path dir = std::filesystem::temp_directory_path() / L"MiniEngine" /
                              std::to_wstring(GetCurrentProcessId());
  std::error_code ec;
  std::filesystem::create_directories(dir, ec);

  std::filesystem::path copy = dir / (L"Game." + std::to_wstring(++counter) + L".dll");
  if (!CopyFileW(original.c_str(), copy.c_str(), FALSE)) {
    *error = "シャドウ コピーに失敗しました（Win32 エラー " + std::to_string(GetLastError()) + "）";
    return L"";
  }
  return copy.wstring();
}

}  // namespace
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `std::filesystem::temp_directory_path()` | 一時フォルダー（`C:\Users\<名前>\AppData\Local\Temp`）。C++17 の `<filesystem>` |
| `/ L"MiniEngine"` | パスの連結（`operator/`） |
| `GetCurrentProcessId()` | プロセス ID。複数のエディタを同時に起動しても、コピーが衝突しない |
| `std::atomic<int> counter` | 呼ぶたびに増える番号。`Game.1.dll`、`Game.2.dll`…と、<strong>名前が毎回違う</strong>。同じパスの DLL を、一度外してから読み直すと、OS がキャッシュを再利用して、新しい内容が反映されないことがある。名前を変えれば確実 |
| `CopyFileW(src, dst, FALSE)` | ファイルをコピーする。第 3 引数が `FALSE` なら、上書きを許す |

`GameLibrary::Load` を、シャドウ コピーを使う形に変えます。

```cpp
bool GameLibrary::Load(const std::wstring& original_path, IGameHost* host, std::string* error) {
  Unload();

  shadow_path_ = MakeShadowCopy(original_path, error);
  if (shadow_path_.empty()) return false;

  library_ = LoadLibraryW(shadow_path_.c_str());                // 元ではなく、コピーを読み込む
  // …（以降は第 41 章と同じ）
}

void GameLibrary::Unload() {
  // …（OnUnload、DestroyGame、FreeLibrary は第 41 章と同じ）
  if (!shadow_path_.empty()) {
    DeleteFileW(shadow_path_.c_str());                          // コピーを消す（失敗しても無視）
    shadow_path_.clear();
  }
}
```

`Engine` の終了時にも、`GameLibrary::Unload` が呼ばれ、コピーが消えます。クラッシュで消えなかったコピーは、一時フォルダーに残るので、<strong>起動時に古いプロセスのフォルダーを掃除する</strong>処理を足すと、きれいに保てます。

## 手順 2：PDB を毎回変える

デバッガー（Visual Studio）をアタッチしていると、DLL のシンボル ファイル（`.pdb`）を掴みます。リンカーが、同じ名前の `Game.pdb` を書こうとして、失敗します。<strong>PDB の名前を毎回変えます</strong>。

`Game.vcxproj`（プロジェクトの「リンカー → デバッグ → プログラム データベース ファイル名」）に、次を設定します。

```text
$(OutDir)Game_$([System.DateTime]::Now.ToString("HHmmss")).pdb
```

または、`.vcxproj` を直接編集します。

```xml
<ItemDefinitionGroup>
  <Link>
    <ProgramDatabaseFile>$(OutDir)Game_$([System.DateTime]::Now.ToString("HHmmss")).pdb</ProgramDatabaseFile>
  </Link>
</ItemDefinitionGroup>
```

さらに、ビルド前に、古い `Game_*.pdb` を掃除します（「ビルド イベント → ビルド前のイベント」）。

```text
del /Q "$(OutDir)Game_*.pdb" 2>nul
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `$([System.DateTime]::Now.ToString("HHmmss"))` | <strong>MSBuild のプロパティ関数</strong>。ビルドのたびに、時刻（時分秒）を文字列として挿入する |
| `ProgramDatabaseFile` | リンカーに、PDB の出力名を指定する |
| 古い PDB の掃除 | 放っておくと、ビルドのたびに増える。ロック中のファイルは、削除に失敗するが、`2>nul` でエラーを隠して、次回に回す |

DLL に埋め込まれる PDB のパスは、その時の名前になるので、デバッガーは、<strong>ビルドごとの正しい PDB</strong> を見つけます。

## 手順 3：リロードの処理（エンジン）

### 方針：新しいものを先に読む

`Engine` の `Impl` を、`std::unique_ptr<GameLibrary> game` を持つ形にします。

```cpp
bool Engine::ReloadGame() {
  auto& s = *impl_;
  if (s.game_path.empty()) {
    LogError("リロードできません：ゲームがまだ読み込まれていません");
    return false;
  }

  // ① 新しいものを先に読み込む。失敗したら、古いゲームをそのまま続ける。
  auto next = std::make_unique<GameLibrary>();
  std::string error;
  if (!next->Load(s.game_path, &s.host, &error)) {
    LogError("ホット リロードに失敗しました（以前のゲームを維持します）: {}", error);
    return false;
  }

  // ② 古いゲームの状態を保存して、止めて、外す。
  std::vector<std::byte> state;
  if (s.game && s.game->IsLoaded()) {
    IGameModule* old_module = s.game->Module();
    state.resize(old_module->GetStateSize());
    old_module->SaveState(state.data(), static_cast<std::uint32_t>(state.size()));
    if (s.playing) old_module->OnStop();
    s.game->Unload();                          // ここで、古い DLL への参照がなくなる
  }

  // ③ 新しいゲームに、入れ替える。Play 中なら、続きから。
  s.game = std::move(next);
  IGameModule* module = s.game->Module();
  if (s.playing) module->OnPlay();
  if (!state.empty()) module->LoadState(state.data(), static_cast<std::uint32_t>(state.size()));

  LogInfo("ホット リロードしました");
  return true;
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| ① 新しい物を先に | 新しい DLL が壊れていた（`CreateGame` がない、版が違う、`OnLoad` で例外）場合、古いゲームに<strong>手を付けていない</strong>ので、動き続ける |
| `std::vector<std::byte>` | 状態の入れ物。`std::byte` は、生のバイトを表す型（C++17） |
| ② 状態の保存 | 古いゲームに、自分の状態を書き出させる。<strong>ポインターは保存しない</strong>（差し替えで無効になる）。数値、ID（`ObjectId`）だけ保存する |
| `OnStop` → `OnPlay` | Play 中なら、古いゲームを止め、新しいゲームを始める。`OnPlay` が、物を集め直す |
| `OnPlay` の後に `LoadState` | <strong>順序が大事</strong>。`OnPlay` が初期値に戻すので、その後で、保存した状態を上書きする |
| `s.game = std::move(next)` | 古い `GameLibrary` は、ここで破棄される（すでに `Unload` 済み） |

### 状態の設計：何を保存するか

ホット リロードで最もバグが出るのが、<strong>状態の引き継ぎ</strong>です。保存のルールを決めておきます。

| 保存するもの | 保存してはいけないもの |
| --- | --- |
| 数値（角度、タイマー、スコア） | <strong>ポインター</strong>、参照（古い DLL のメモリを指す） |
| `ObjectId`（エンジンのオブジェクトの番号） | <strong>関数ポインター</strong>、仮想関数を持つオブジェクト（古い DLL のコードを指す） |
| 列挙値、フラグ | `std::vector` などの内部ポインター（そのままのバイト列は無効） |

複雑な状態は、<strong>単純な構造体（POD）にまとめて保存</strong>します。`std::vector` なら、要素数と中身を、並べて書き出す、といった工夫が要ります。

```cpp
struct SpinnerState {
  std::uint32_t version = 1;       // 状態の形の版。形を変えたら上げて、古い状態を捨てる
  float angle = 0.0f;
};
```

`LoadState` で、版が違う、または大きさが足りないときは、<strong>黙って初期値で続けます</strong>（クラッシュさせない）。

### 注意：エンジンの側が、古い DLL を指していないか

差し替えで壊れるのは、<strong>エンジンが覚えている、ゲームのポインター</strong>です。

| 確認する場所 | 内容 |
| --- | --- |
| `IGameHost` の実装 | ゲームから受け取ったコールバック（関数ポインター）を、<strong>保存していないか</strong> |
| `Scene` のオブジェクト | ゲームが作った物のうち、ゲームの型（`GameComponent*` のようなもの）を持っていないか |
| ログの出力先 | ゲームが登録した、ログ コールバック |
| スレッド | ゲームが作ったスレッドが、動き続けていないか |

今のエンジンは、`IGameModule*` を 1 つ持つだけなので、安全です。<strong>将来、ゲームの型をエンジンに登録する仕組み</strong>（コンポーネントなど）を足すときは、差し替えのたびに登録を解除し、登録し直す仕組みが要ります。

## 手順 4：C API を足す

```c
ME_API MeResult me_game_load(MeEngine* engine, const char* path_utf8);   /* 元のパス。シャドウ コピーは内部で */
ME_API MeResult me_game_reload(MeEngine* engine);
ME_API MeResult me_game_unload(MeEngine* engine);
ME_API MeResult me_game_is_loaded(const MeEngine* engine, int32_t* out_loaded);
```

実装は、`Guard` で包み、`Engine::LoadGame` / `ReloadGame` / `UnloadGame` を呼ぶだけです。`me_game_reload` は、失敗しても（古いゲームが続くので）エラー コードを返し、詳細は `me_get_last_error` で取れるようにします。

C# 側は、これまでと同じ手順で、P/Invoke の宣言と `IEngineService` の `GameLoad`、`GameReload`、`GameUnload`、`GameIsLoaded` を足します。

```csharp
[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_game_load(EngineHandle engine, string path);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_game_reload(EngineHandle engine);
```

## 手順 5：変更を検出して自動で差し替える（エディタ）

`Game.dll` が更新されたことを検出し、<strong>書き込みが終わるのを待ってから</strong>、リロードを依頼します。

`Services\IGameService.cs`:

```csharp
namespace Editor.Services;

public interface IGameService : IDisposable
{
    string? GamePath { get; }
    bool IsLoaded { get; }
    bool AutoReload { get; set; }

    void SetGamePath(string path);               // 読み込むゲーム DLL を決めて、読み込む
    Task<bool> ReloadAsync();                    // 手動のリロード
    event Action? StateChanged;                  // 読み込み状態が変わった
}
```

`Services\GameService.cs`:

```csharp
using System.IO;
using System.Windows.Threading;

namespace Editor.Services;

public sealed class GameService : IGameService
{
    private readonly IRenderLoop _loop;
    private readonly ILogService _log;
    private readonly DispatcherTimer _debounce;
    private FileSystemWatcher? _watcher;

    public GameService(IRenderLoop loop, ILogService log)
    {
        _loop = loop;
        _log = log;
        // ビルドは、ファイルを複数回に分けて書く。最後の通知から 0.5 秒おいてから反応する。
        _debounce = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(500) };
        _debounce.Tick += async (_, _) =>
        {
            _debounce.Stop();
            if (AutoReload) await ReloadAsync();
        };
    }

    public string? GamePath { get; private set; }
    public bool IsLoaded { get; private set; }
    public bool AutoReload { get; set; } = true;
    public event Action? StateChanged;

    public void SetGamePath(string path)
    {
        GamePath = path;

        _watcher?.Dispose();
        _watcher = new FileSystemWatcher(Path.GetDirectoryName(path)!, Path.GetFileName(path))
        {
            NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size | NotifyFilters.CreationTime,
            EnableRaisingEvents = true,
        };
        _watcher.Changed += OnFileChanged;
        _watcher.Created += OnFileChanged;

        _ = LoadFirstAsync(path);
    }

    private void OnFileChanged(object sender, FileSystemEventArgs e)
    {
        // 別のスレッドで呼ばれるので、UI スレッドに戻してタイマーを延長する
        System.Windows.Application.Current.Dispatcher.BeginInvoke(() =>
        {
            _debounce.Stop();
            _debounce.Start();
        });
    }

    private async Task LoadFirstAsync(string path)
    {
        if (!await WaitUntilReadableAsync(path)) return;
        bool ok = await Task.Run(() => _loop.Invoke(e => e.GameLoad(path)));
        IsLoaded = ok;
        StateChanged?.Invoke();
    }

    public async Task<bool> ReloadAsync()
    {
        if (GamePath == null) return false;
        if (!await WaitUntilReadableAsync(GamePath))
        {
            _log.Error("ゲーム DLL を読み取れませんでした（ビルドが終わっていない？）");
            return false;
        }
        // 実際のリロードは、描画スレッドで行う
        bool ok = await Task.Run(() => _loop.Invoke(e => e.GameReload()));
        IsLoaded = ok || IsLoaded;
        StateChanged?.Invoke();
        return ok;
    }

    // リンカーが書き終えるのを待つ（開けるようになるまで、最大 5 秒）
    private static async Task<bool> WaitUntilReadableAsync(string path)
    {
        for (int i = 0; i < 50; ++i)
        {
            try
            {
                using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
                return true;
            }
            catch (IOException)
            {
                await Task.Delay(100);
            }
        }
        return false;
    }

    public void Dispose() => _watcher?.Dispose();
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `FileSystemWatcher(dir, filter)` | フォルダーと、ファイル名のフィルターを指定する。ここでは `Game.dll` だけ |
| `NotifyFilters.LastWrite \| Size` | 更新日時と大きさの変化を見る |
| デバウンス（0.5 秒） | リンカーは、DLL を何度かに分けて書く。最初の通知で反応すると、書きかけの DLL を読んでしまう |
| `WaitUntilReadableAsync` | <strong>排他的に開けるか</strong>を、100 ms ごとに試す。リンカーが書いている間は `IOException` になるので、書き終えるまで待てる |
| `await Task.Delay(100)` | UI を止めずに待つ |
| `Task.Run(() => _loop.Invoke(…))` | `Invoke` は、描画スレッドの完了を<strong>同期で待つ</strong>（ブロックする）。UI スレッドでブロックしないよう、スレッド プールで待つ |
| `async (_, _) =>` | 非同期のラムダ。イベント ハンドラーに限り、`async void` 相当で許される |

## 手順 6：ゲームのビルド（エディタから）

エディタに「ビルド」ボタンを付けて、ゲームを MSBuild でビルドします。

```csharp
using System.Diagnostics;

namespace Editor.Services;

public interface IBuildService
{
    Task<bool> BuildGameAsync(string projectPath);
}

public sealed class BuildService : IBuildService
{
    private readonly ILogService _log;

    public BuildService(ILogService log) => _log = log;

    public async Task<bool> BuildGameAsync(string projectPath)
    {
        string? msbuild = FindMSBuild();
        if (msbuild == null)
        {
            _log.Error("MSBuild が見つかりません（Visual Studio をインストールしてください）");
            return false;
        }

        var info = new ProcessStartInfo(msbuild, $"\"{projectPath}\" /p:Configuration=Debug /p:Platform=x64 /nologo /v:minimal")
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardOutputEncoding = System.Text.Encoding.UTF8,
        };

        using var process = new Process { StartInfo = info, EnableRaisingEvents = true };
        process.OutputDataReceived += (_, e) => { if (e.Data != null) _log.Info(e.Data); };
        process.ErrorDataReceived += (_, e) => { if (e.Data != null) _log.Error(e.Data); };

        _log.Info("ゲームをビルドします…");
        process.Start();
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();
        await process.WaitForExitAsync();

        bool ok = process.ExitCode == 0;
        _log.Info(ok ? "ビルドに成功しました" : $"ビルドに失敗しました（終了コード {process.ExitCode}）");
        return ok;
    }

    // vswhere で、MSBuild の場所を調べる
    private static string? FindMSBuild()
    {
        string vswhere = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                                      "Microsoft Visual Studio", "Installer", "vswhere.exe");
        if (!File.Exists(vswhere)) return null;

        var info = new ProcessStartInfo(vswhere,
            "-latest -requires Microsoft.Component.MSBuild -find MSBuild\\**\\Bin\\MSBuild.exe")
        {
            RedirectStandardOutput = true,
            UseShellExecute = false,
            CreateNoWindow = true,
        };
        using var process = Process.Start(info);
        string? line = process?.StandardOutput.ReadLine();
        process?.WaitForExit();
        return string.IsNullOrWhiteSpace(line) ? null : line.Trim();
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Process` / `ProcessStartInfo` | 他のプログラムを起動して扱う標準クラス。C++ の `CreateProcess` に当たる |
| `RedirectStandardOutput` | 子プロセスの標準出力を、こちらで受け取る。`UseShellExecute = false` と組み合わせる |
| `OutputDataReceived` | 出力の 1 行ごとに呼ばれるイベント。`BeginOutputReadLine()` で開始。<strong>別のスレッド</strong>で呼ばれるが、`LogService` は安全 |
| `WaitForExitAsync()` | 終了を、UI を止めずに待つ |
| `vswhere.exe` | Visual Studio の場所を調べる、Microsoft 提供のツール。インストーラーに同梱されている |
| `/p:Configuration=Debug /p:Platform=x64` | MSBuild にプロパティを渡す。この教材の出力先（第 1 章）に合わせる |
| `/v:minimal` | 出力の詳しさを最小にする |

ビルドが成功して `Game.dll` が更新されると、`GameService` の `FileSystemWatcher` が検出し、<strong>自動でホット リロード</strong>が走ります。

## 手順 7：メニューと表示

`MainWindow` に、「ゲーム」メニューを足します。

```xml
<MenuItem Header="ゲーム(_G)">
    <MenuItem Header="ビルド(_B)" Command="{Binding BuildGameCommand}" InputGestureText="F7" />
    <MenuItem Header="今すぐリロード(_R)" Command="{Binding ReloadGameCommand}" InputGestureText="Ctrl+F5" />
    <MenuItem Header="自動でリロード(_A)" IsCheckable="True" IsChecked="{Binding AutoReload}" />
</MenuItem>
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IsCheckable` / `IsChecked` | チェック付きのメニュー項目。`IsChecked` に双方向でバインドして、設定の ON/OFF にする |

ステータス バーに、ゲームの状態（読み込み済み／未読み込み）を出すと、分かりやすくなります。

## 動作確認

次の手順で、<strong>ホット リロードの体験</strong>をします。

1. エディタを起動し、`Game.dll` を設定する。
2. シーンに、`Spin_A` という名前の物を作る。
3. <strong>Play</strong>（第 43 章で作る。それまでは、Player か、テスト用のコマンドで `SetPlaying(true)`）。箱が回る。
4. `SpinnerGame.h` の `kSpeed = 1.5f` を `kSpeed = 6.0f` に書き換える。
5. エディタの「ゲーム → ビルド」（または、Visual Studio で `Game` をビルド）。
6. <strong>約 1 秒後に、回転が速くなる</strong>。回転の途中で、<strong>箱が突然違う角度に飛ばない</strong>（`angle_` が引き継がれる）。

| 見る所 | 期待する結果 |
| --- | --- |
| ログ | 「ホット リロードしました」が出る |
| 角度 | リロードの前後で連続している |
| ビルドを失敗させる（構文エラー） | ビルド失敗が出て、<strong>古いゲームが動き続ける</strong> |
| `kGameApiVersion` を変えて再ビルド | 「API の版が違います」が出て、古いゲームが動き続ける |
| デバッグしながら | 再ビルドしても、リンクが「書き込めない」で失敗しない |
| `%TEMP%\MiniEngine\<pid>\` | `Game.1.dll`、`Game.2.dll`…と増え、古いものは消える |

## よくあるミス

??? failure "ビルドが `LNK1104: ファイル 'Game.dll' を開けません` で失敗する"
    シャドウ コピーを使っていない（元の DLL を直接読み込んでいる）。`LoadLibraryW` に渡すのが、コピーのパスか確認する。

??? failure "`LNK1201: PDB への書き込みエラー`"
    PDB の名前が毎回変わる設定になっていない。または、前回の PDB をデバッガーが掴んでいる。`ProgramDatabaseFile` を確認する。

??? failure "リロードしても、動作が変わらない"
    同じ名前の DLL を再ロードしている（OS が古いものを再利用）。シャドウ コピーの<strong>名前を毎回変える</strong>。ビルドの出力が、別の場所に出ていないか確認する。

??? failure "リロード直後に、エンジンごとクラッシュする"
    エンジンが、古い DLL のポインターを持っている。`IGameHost` に渡したコールバック、ゲームが作ったスレッド、`Scene` に残したゲームの型を確認する。`FreeLibrary` の<strong>前に</strong>、すべての参照を手放す。

??? failure "リロードの後、物が回らなくなる"
    `OnPlay` が呼ばれていない（`Play` 中の再読み込みで、新しいゲームに `OnPlay` を呼び忘れた）。または、`LoadState` を `OnPlay` の前に呼んで、上書きされた。

??? failure "状態を引き継ぐと、値が壊れる"
    ゲームの状態の構造が変わった（フィールドを足した）のに、古い状態を読んでいる。状態に<strong>版</strong>を持たせ、版が違えば、引き継がずに初期値で始める。

??? failure "ビルド中にリロードが走って、`LoadLibrary` が失敗する"
    書き込み途中の DLL を読んでいる。デバウンスと `WaitUntilReadableAsync` で待つ。

## ホット リロードの限界

| 限界 | 内容 |
| --- | --- |
| 構造を変えたとき | クラスのメンバーを足す・消すと、状態の引き継ぎが合わなくなる。その場合、Play をやり直す |
| ゲームのクラッシュ | ゲームは<strong>エンジンと同じプロセス</strong>で動く。アクセス違反があると、エディタごと落ちる。別プロセスで動かす方式（IPC）なら防げるが、複雑になる |
| テンプレートや static の初期化順 | DLL を読み直すと、`static` 変数が初期化し直される。順序に依存するコードは危ない |
| 最適化ビルド | Release では、インライン化などで、関数の中身が変わる。ホット リロードは、Debug で使うのが基本 |

## この章のまとめ

- ホット リロードは、<strong>シャドウ コピー</strong>（ロックの回避）、<strong>PDB の名前変更</strong>、<strong>状態の保存と復元</strong>、<strong>新しい物を先に読む</strong>の 4 つで成り立つ。
- 状態は、ポインターではなく、<strong>数値と ID</strong> で保存する。<strong>版</strong>を持たせる。
- リロードは、<strong>描画スレッド</strong>で行う（エンジンを触るのは 1 本）。
- ビルド完了の検出は、`FileSystemWatcher` + <strong>デバウンス</strong> + <strong>開けるまで待つ</strong>。

## 次の章へ

次の章（[第 43 章 Play モード](43-play-mode.md)）では、エディタの<strong>編集モード</strong>と<strong>Play モード</strong>を切り替えます。Play を止めると、シーンが<strong>元の状態に戻る</strong>仕組みと、Play 中の編集の扱いを作ります。
