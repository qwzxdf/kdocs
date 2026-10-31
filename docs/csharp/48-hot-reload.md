---
title: 第 48 章 ホット リロード
tags:
  - C#連携
---

# 第 48 章 ホット リロード

この章で、エディタを動かしたまま `Game.dll` を差し替える仕組み（ホット リロード）を作ります。ゲームのコードを書き換えてビルドすると、数秒後には、動いているゲームに反映されます。数値や挙動の調整を試行錯誤する速さが、何倍にもなる機能です。

!!! info "このページを読む前に"
    - [第 47 章 Game DLL のインターフェース](47-game-interface.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Engine/src/GameModule.cpp`（変更） | DLL のコピーを読み込み、差し替えられるようにする |
    | `Play/IGameService.cs`（新規） | ゲームの読み込みと再読み込みの窓口 |
    | `Play/GameService.cs`（新規） | ファイルの更新を検出して、再読み込みを依頼する |


## 差し替えの手順と、5 つの罠

第 47 章でゲームを DLL に分けました。差し替えるには、次の手順が要ります。

```text
1. 新しい Game.dll ができる（ビルド）
2. 古いゲームの「状態」を保存する
3. 古いゲームを壊し、古い DLL を外す
4. 新しい DLL を読み込み、新しいゲームを作る
5. 保存した「状態」を、新しいゲームに戻す
```

簡単に見えますが、罠が 5 つあります。

| 罠 | 内容 | 対処 |
| --- | --- | --- |
| ファイルのロック | 読み込み中の DLL は、Windows が上書きを禁止する。ビルドが「書き込めない」で失敗する | コピーを読み込む（シャドウ コピー） |
| PDB のロック | デバッガーが `.pdb` を掴む。リンカーが書けない | PDB の名前を毎回変える |
| 状態が消える | DLL の中の `static` 変数やゲームのオブジェクトは、DLL を外すと消える | 状態をエンジンのメモリに保存して、戻す |
| 古いコードへの参照 | エンジンが古い DLL の関数やクラスへのポインターを持ち続けると、外したあとにクラッシュする | 差し替えの前に参照を全部手放す |
| 失敗したとき | 新しい DLL が壊れていたら、古いものも消えて、何もなくなる | 新しい物を先に読み込み、成功してから古い物を捨てる |

この章のゴールは次のとおりです。

- ゲームを書き換えてビルドすると、エディタが自動で検出して、差し替える。
- Play 中でも差し替わり、回転の角度が飛ばない（状態を引き継ぐ）。
- 新しい DLL の読み込みに失敗しても、古いゲームが動き続ける。
- エディタから、ゲームのビルドと手動のリロードができる。

## シャドウ コピーでロックを避ける

エンジンは、`Game.dll` そのものではなく、そのコピーを読み込みます。元の `Game.dll` は誰にも掴まれないので、ビルドがいつでも上書きできます。`GameModule.cpp` に、コピーを作る関数を足します。

```cpp title="Engine/src/GameModule.cpp（変更）"
#include <atomic>
#include <filesystem>

namespace {

// 元の DLL を一時フォルダーにコピーする。ファイル名は、呼ぶたびに変わる。
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

コピー先は、一時フォルダー（`std::filesystem::temp_directory_path()`）の下の、プロセス ID 別のフォルダーです。プロセス ID を入れておけば、エディタを複数同時に起動しても、コピーが衝突しません。

ファイル名を `Game.1.dll`、`Game.2.dll` と毎回変えるのが、重要な工夫です。同じパスの DLL を一度外してから読み直すと、OS が前のキャッシュを再利用して、新しい内容が反映されないことがあるからです。名前を変えれば確実に読み直されます。`CopyFileW` の第 3 引数 `FALSE` は、上書きを許す指定です。

`GameLibrary::Load` をコピーを読み込む形に変えます。

```cpp
bool GameLibrary::Load(const std::wstring& original_path, IGameHost* host, std::string* error) {
  Unload();

  shadow_path_ = MakeShadowCopy(original_path, error);
  if (shadow_path_.empty()) return false;

  library_ = LoadLibraryW(shadow_path_.c_str());                // 元ではなく、コピーを読み込む
  // …（以降は第 47 章と同じ）
}

void GameLibrary::Unload() {
  // …（OnUnload、DestroyGame、FreeLibrary は第 47 章と同じ）
  if (!shadow_path_.empty()) {
    DeleteFileW(shadow_path_.c_str());                          // コピーを消す（失敗しても無視）
    shadow_path_.clear();
  }
}
```

`Engine` の終了時にも `Unload` が呼ばれ、コピーが消えます。クラッシュすると消えずに残るので、起動時に古いプロセスのフォルダーを掃除する処理を足しておくと、一時フォルダーがきれいに保てます。

## PDB を毎回変える

デバッガー（Visual Studio）をアタッチしていると、DLL のシンボル ファイル（`.pdb`）を掴みます。リンカーが同じ名前の `Game.pdb` を書こうとして、失敗します。PDB の名前を毎回変えて、これを避けます。

`Game` プロジェクトの「リンカー → デバッグ → プログラム データベース ファイル名」に次を設定します。

```text
$(OutDir)Game_$([System.DateTime]::Now.ToString("HHmmss")).pdb
```

`.vcxproj` を直接編集するなら、こう書きます。

```xml
<ItemDefinitionGroup>
  <Link>
    <ProgramDatabaseFile>$(OutDir)Game_$([System.DateTime]::Now.ToString("HHmmss")).pdb</ProgramDatabaseFile>
  </Link>
</ItemDefinitionGroup>
```

`$([System.DateTime]::Now.ToString("HHmmss"))` は MSBuild のプロパティ関数で、ビルドのたびに、時刻（時分秒）を文字列として埋め込みます。DLL に埋め込まれる PDB のパスは、その時の名前になるので、デバッガーは、ビルドごとの正しい PDB を見つけます。

放っておくと PDB がビルドのたびに増えるので、ビルド前のイベントで、古いものを掃除します。

```text
del /Q "$(OutDir)Game_*.pdb" 2>nul
```

ロック中のファイルは消せずに失敗しますが、`2>nul` でエラーを隠して、次回に回します。

## リロードの処理（エンジン側）

### 新しいものを先に読む

リロードの方針は、新しいものを先に読み込むことです。`Engine` の `Impl` は、`std::unique_ptr<GameLibrary> game` を持つ形にします。

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

  // ③ 新しいゲームに入れ替える。Play 中なら、続きから。
  s.game = std::move(next);
  IGameModule* module = s.game->Module();
  if (s.playing) module->OnPlay();
  if (!state.empty()) module->LoadState(state.data(), static_cast<std::uint32_t>(state.size()));

  LogInfo("ホット リロードしました");
  return true;
}
```

3 つの段階の意味を見ていきます。

①で、新しい DLL を先に読み込みます。新しい DLL が壊れていた（`CreateGame` がない、版が違う、`OnLoad` で例外が出た）としても、古いゲームにはまだ手を付けていないので、古いゲームが動き続けます。

②で、古いゲームに自分の状態を書き出させ、止めて、外します。状態の入れ物は `std::vector<std::byte>` で、`std::byte` は生のバイトを表す型です（C++17）。

③で、新しいゲームに入れ替えます。Play 中なら `OnStop` → `OnPlay` の順で止めて始め直します（`OnPlay` が、物を集め直します）。そのあとで `LoadState` を呼ぶ順序が大事です。`OnPlay` は初期値に戻すので、その後に保存した状態で上書きしなければなりません。

### 何を保存するか

ホット リロードで最もバグが出るのが、状態の引き継ぎです。保存のルールを決めておきます。

| 保存するもの | 保存してはいけないもの |
| --- | --- |
| 数値（角度、タイマー、スコア） | ポインター、参照（古い DLL のメモリを指す） |
| `ObjectId`（エンジンのオブジェクトの番号） | 関数ポインター、仮想関数を持つオブジェクト（古い DLL のコードを指す） |
| 列挙値、フラグ | `std::vector` などの内部ポインター（そのままのバイト列は無効） |

複雑な状態は、単純な構造体（POD）にまとめて保存します。`std::vector` なら、要素数と中身を並べて書き出す、といった工夫が要ります。

```cpp
struct SpinnerState {
  std::uint32_t version = 1;       // 状態の形の版。形を変えたら上げて、古い状態を捨てる
  float angle = 0.0f;
};
```

`LoadState` で、版が違うときや、大きさが足りないときは、黙って初期値で続けます。クラッシュさせないことのほうが大切です。

### エンジンの側が古い DLL を指していないか

差し替えで壊れるのは、エンジンが覚えている、ゲームのポインターです。確認する場所を挙げます。

| 確認する場所 | 内容 |
| --- | --- |
| `IGameHost` の実装 | ゲームから受け取ったコールバック（関数ポインター）を保存していないか |
| `Scene` のオブジェクト | ゲームが作った物のうち、ゲームの型（`GameComponent*` のようなもの）を持っていないか |
| ログの出力先 | ゲームが登録した、ログ コールバック |
| スレッド | ゲームが作ったスレッドが動き続けていないか |

今のエンジンは `IGameModule*` を 1 つ持つだけなので、安全です。将来、ゲームの型をエンジンに登録する仕組み（コンポーネントなど）を足すときは、差し替えのたびに登録を解除して、登録し直す仕組みが要ります。

## C API を足す

```c
ME_API MeResult me_game_load(MeEngine* engine, const char* path_utf8);   /* 元のパス。シャドウ コピーは内部で */
ME_API MeResult me_game_reload(MeEngine* engine);
ME_API MeResult me_game_unload(MeEngine* engine);
ME_API MeResult me_game_is_loaded(const MeEngine* engine, int32_t* out_loaded);
```

実装は、`Guard` で包んで、`Engine::LoadGame`、`ReloadGame`、`UnloadGame` を呼ぶだけです。`me_game_reload` は、失敗したら（古いゲームは続いていても）エラー コードを返し、詳細は `me_get_last_error` で取れるようにします。

C# 側も、これまでと同じ手順で、P/Invoke の宣言と、`IEngineService` の `GameLoad`、`GameReload`、`GameUnload`、`GameIsLoaded` を足します。

```csharp
[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_game_load(EngineHandle engine, string path);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_game_reload(EngineHandle engine);
```

## 変更を検出して、自動で差し替える（エディタ側）

`Game.dll` が更新されたのを検出して、書き込みが終わるのを待ってから、リロードを依頼します。

```csharp title="Play/IGameService.cs（新規）"
namespace Editor.Play;

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

```csharp title="Play/GameService.cs（新規）"
using System.IO;
using System.Windows.Threading;
using Editor.Log;
using Editor.Viewport;

namespace Editor.Play;

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

第 46 章のアセット ブラウザと同じく、`FileSystemWatcher` の通知を UI スレッドに戻して、デバウンスしています。ここで待ち時間が 2 段あるのは、リンカーが DLL を何度かに分けて書くからです。最初の通知ですぐ反応すると、書きかけの DLL を読んでしまいます。そこで、最後の通知から 0.5 秒おき、さらに `WaitUntilReadableAsync` で、ファイルを開けるようになるまで 100 ms ごとに試します。リンカーが書いている間は `IOException` になるので、書き終えるまで待てます。`await Task.Delay(100)` は、UI を止めずに待ちます。

`_loop.Invoke(...)` は、描画スレッドの完了を同期で待つ（ブロックする）ので、UI スレッドで直接呼ぶと固まります。そこで `Task.Run` で、スレッド プール側で待っています。リロードそのものは、描画スレッドで行います（エンジンを触るのは 1 本だけ、という約束）。

## ゲームのビルド（エディタから）

エディタに「ビルド」ボタンを付けて、ゲームを MSBuild でビルドします。

```csharp
using System.Diagnostics;

namespace Editor.Play;

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

`Process` と `ProcessStartInfo` は、他のプログラムを起動して扱う標準クラスです（C++ の `CreateProcess` に当たります）。`RedirectStandardOutput` で子プロセスの出力をこちらで受け取れますが、`UseShellExecute = false` と組み合わせる必要があります。出力は 1 行ごとに `OutputDataReceived` が呼ばれ（`BeginOutputReadLine()` で開始）、別のスレッドで呼ばれますが、`LogService` はスレッド安全に作ってあります。`WaitForExitAsync()` は、UI を止めずに終了を待ちます。

MSBuild の場所は、`vswhere.exe`（Visual Studio のインストーラーに同梱された、場所を調べるツール）で探します。`/p:Configuration=Debug /p:Platform=x64` は、第 1 章の出力先に合わせたプロパティで、`/v:minimal` は出力の詳しさを最小にします。

ビルドが成功して `Game.dll` が更新されると、`GameService` の `FileSystemWatcher` がそれを検出して、自動でホット リロードが走ります。

`MainWindow` には、「ゲーム」メニューを足します。

```xml
<MenuItem Header="ゲーム(_G)">
    <MenuItem Header="ビルド(_B)" Command="{Binding BuildGameCommand}" InputGestureText="F7" />
    <MenuItem Header="今すぐリロード(_R)" Command="{Binding ReloadGameCommand}" InputGestureText="Ctrl+F5" />
    <MenuItem Header="自動でリロード(_A)" IsCheckable="True" IsChecked="{Binding AutoReload}" />
</MenuItem>
```

`IsCheckable` と `IsChecked` は、チェック付きのメニュー項目です。`IsChecked` に双方向でバインドして、設定の ON/OFF にします。ステータス バーにゲームの状態（読み込み済み／未読み込み）を出すと、分かりやすくなります。

## ホット リロードを体験する

次の手順で、ホット リロードを確かめます。

1. エディタを起動して、`Game.dll` を設定する。
2. シーンに `Spin_A` という名前の物を作る。
3. Play する（第 49 章で作ります。それまでは、Player か、テスト用のコマンドで `SetPlaying(true)`）。箱が回る。
4. `SpinnerGame.h` の `kSpeed = 1.5f` を `kSpeed = 6.0f` に書き換える。
5. エディタの「ゲーム → ビルド」（または、Visual Studio で `Game` をビルド）。
6. 約 1 秒後に回転が速くなる。回転の途中で、箱が突然違う角度に飛ばない（`angle_` が引き継がれている）。

| 見る所 | 期待する結果 |
| --- | --- |
| ログ | 「ホット リロードしました」が出る |
| 角度 | リロードの前後で連続している |
| ビルドを失敗させる（構文エラー） | ビルド失敗が出て、古いゲームが動き続ける |
| `kGameApiVersion` を変えて再ビルド | 「API の版が違います」が出て、古いゲームが動き続ける |
| デバッグしながら | 再ビルドしても、リンクが「書き込めない」で失敗しない |
| `%TEMP%\MiniEngine\<pid>\` | `Game.1.dll`、`Game.2.dll`…と増え、古いものは消える |

??? failure "ビルドが `LNK1104: ファイル 'Game.dll' を開けません` で失敗する"
    シャドウ コピーを使っていません（元の DLL を直接読み込んでいます）。`LoadLibraryW` に渡すのが、コピーのパスか確認します。

??? failure "`LNK1201: PDB への書き込みエラー`"
    PDB の名前が毎回変わる設定になっていないか、前回の PDB をデバッガーが掴んでいます。`ProgramDatabaseFile` を確認します。

??? failure "リロードしても、動作が変わらない"
    同じ名前の DLL を再ロードしていて、OS が古いものを再利用しています。シャドウ コピーの名前を毎回変えます。ビルドの出力が別の場所に出ていないかも確認します。

??? failure "リロード直後にエンジンごとクラッシュする"
    エンジンが古い DLL のポインターを持っています。`IGameHost` に渡したコールバック、ゲームが作ったスレッド、`Scene` に残したゲームの型を確認します。`FreeLibrary` の前にすべての参照を手放します。

??? failure "リロードのあと、物が回らなくなる"
    新しいゲームに `OnPlay` を呼び忘れたか、`LoadState` を `OnPlay` の前に呼んで、上書きされています。

??? failure "状態を引き継ぐと、値が壊れる"
    ゲームの状態の構造が変わった（フィールドを足した）のに、古い状態を読んでいます。状態に版を持たせて、版が違えば引き継がずに初期値で始めます。

??? failure "ビルド中にリロードが走って、`LoadLibrary` が失敗する"
    書き込み途中の DLL を読んでいます。デバウンスと `WaitUntilReadableAsync` で待ちます。

## ホット リロードの限界

| 限界 | 内容 |
| --- | --- |
| 構造を変えたとき | クラスのメンバーを足したり消したりすると、状態の引き継ぎが合わなくなる。その場合は Play をやり直す |
| ゲームのクラッシュ | ゲームはエンジンと同じプロセスで動く。アクセス違反があると、エディタごと落ちる。別プロセスで動かす方式（IPC）なら防げるが、複雑になる |
| テンプレートや static の初期化順 | DLL を読み直すと `static` 変数が初期化し直される。順序に依存するコードは危ない |
| 最適化ビルド | Release ではインライン化などで関数の中身が変わる。ホット リロードは Debug で使うのが基本 |

## この章のまとめ

- ホット リロードは、シャドウ コピー（ロックの回避）、PDB の名前変更、状態の保存と復元、新しい物を先に読む、の 4 つで成り立つ。
- 状態は、ポインターではなく、数値と ID で保存する。版を持たせる。
- リロードは描画スレッドで行う（エンジンを触るのは 1 本）。
- ビルド完了の検出は、`FileSystemWatcher` と、デバウンスと、開けるまで待つ、の組み合わせ。

次の章では、エディタの編集モードと Play モードを切り替えます。

[第 49 章 Play モード](49-play-mode.md) へ進みます。
