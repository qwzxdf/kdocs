---
title: 第 30 章 ログとエラー処理
tags:
  - C#連携
---

# 第 30 章 ログとエラー処理

エディタが大きくなると<strong>失敗の種類が増えます</strong>。ファイルが壊れていたゲームの DLL が読み込めない、GPU が応答しない C# の例外、C++ の例外、ネイティブのクラッシュ…。この章ではそれらを<strong>どこで、どう受け止めどう記録しどう利用者に知らせるか</strong>の方針を整え実装します。

## この章の考え方

### 失敗を 4 つに分ける

失敗の扱いは<strong>誰の責任か</strong>で変わります。

| 種類 | 例 | 対応 |
| --- | --- | --- |
| <strong>① 想定内の失敗</strong>（利用者の操作・環境） | ファイルが無い壊れている、ディスクが満杯、権限がない | <strong>捕まえて</strong>、分かりやすいメッセージを出す。作業は続ける |
| <strong>② 想定内の失敗</strong>（外部のコード） | ゲーム DLL の版違い、ビルド失敗 | 捕まえてログに出す。古い状態を保つ（第 28 章） |
| <strong>③ プログラムのバグ</strong> | `NullReferenceException`、範囲外、不正な状態 | <strong>記録して</strong>、できれば作業を保存し続けるか終了する。握りつぶさない |
| <strong>④ 致命的な失敗</strong> | ネイティブのアクセス違反、GPU のデバイス消失 | <strong>記録して</strong>終了。クラッシュ レポートを残す |

①②は<strong>例外を捕まえて処理する</strong>。③④は<strong>捕まえきれない・捕まえても直せない</strong>ので、<strong>記録を残す</strong>ことが最重要です。

### 原則

| 原則 | 内容 |
| --- | --- |
| <strong>握りつぶさない</strong> | `catch { }` で何もしない例外処理は、バグを隠す。想定内の型に絞り必ずログを残す |
| <strong>近い所で捕まえない</strong> | 例外は、「何をすべきか決められる場所」まで投げ上げる。低い層（ファイル読み込み）は投げ高い層（コマンド）が、利用者に知らせる |
| <strong>ログは再現のための記録</strong> | 「何が起きたか」だけでなく、「その時、何をしていたか」（直前の操作）が分かるように |
| <strong>利用者のメッセージと開発者のログを分ける</strong> | 利用者には「ファイルを開けませんでした」、ログには例外の全文とスタック トレース |

## この章のゴール

- すべての未処理の例外を拾って、ログに残し利用者に知らせる。
- ログをファイルに書く（日付ごと古いものは自動で消す）。
- ログ パネルを重大度のフィルター、コピー、クリアつきに改良する。
- ネイティブのクラッシュのときミニダンプを残す。

## 手順 1：未処理の例外を拾う

.NET には未処理の例外を拾う場所が、<strong>3 つ</strong>あります。それぞれ拾える対象が違います。

| 場所 | 拾える例外 | 続行できるか |
| --- | --- | --- |
| `Application.DispatcherUnhandledException` | <strong>UI スレッド</strong>で起きた未処理の例外 | `e.Handled = true` で続行できる |
| `AppDomain.CurrentDomain.UnhandledException` | <strong>どのスレッドでも</strong>、最終的に未処理の例外 | 続行不可（プロセスは終了する） |
| `TaskScheduler.UnobservedTaskException` | 誰も `await` しなかった `Task` の例外 | 続行できる（観察済みにする） |

`App.xaml.cs`:

```csharp
protected override void OnStartup(StartupEventArgs e)
{
    // 例外の捕捉は、できるだけ最初に設定する
    DispatcherUnhandledException += OnDispatcherUnhandledException;
    AppDomain.CurrentDomain.UnhandledException += OnDomainUnhandledException;
    TaskScheduler.UnobservedTaskException += OnUnobservedTaskException;
    base.OnStartup(e);
}

// ① UI スレッドの例外：記録して、利用者に知らせ、続行するか選ばせる
private void OnDispatcherUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
{
    CrashReporter.Report("UI スレッドの未処理例外", e.Exception);
    var result = MessageBox.Show(
        $"予期しないエラーが起きました。\n\n{e.Exception.Message}\n\nこのまま続けますか？（続けると不安定になる場合があります）",
        "MiniEngine Editor", MessageBoxButton.YesNo, MessageBoxImage.Error);
    e.Handled = result == MessageBoxResult.Yes;      // いいえ なら、そのまま終了
}

// ② どこかのスレッドの例外：もう続行できない。記録だけ残す
private void OnDomainUnhandledException(object sender, UnhandledExceptionEventArgs e)
{
    CrashReporter.Report("未処理例外（終了します）", e.ExceptionObject as Exception);
}

// ③ 見失われた Task の例外：記録して、観察済みにする
private void OnUnobservedTaskException(object? sender, UnobservedTaskExceptionEventArgs e)
{
    CrashReporter.Report("見失われた Task の例外", e.Exception);
    e.SetObserved();
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DispatcherUnhandledException` | WPF の UI スレッドの例外を拾う。`DispatcherUnhandledExceptionEventArgs.Exception` に例外が入る |
| `e.Handled = true` | 例外を処理済みにして、アプリを続ける。<strong>状態が壊れている可能性</strong>があるので、利用者に選ばせる |
| `AppDomain.CurrentDomain.UnhandledException` | どのスレッドでも最後に拾う網。ここに来たらプロセスは終了する。<strong>記録できる最後の機会</strong> |
| `e.ExceptionObject as Exception` | 引数は `object`。`Exception` 以外が投げられることもある（C++/CLI など） |
| `UnobservedTaskException` | `Task` の例外を誰も見ないまま `Task` が GC されたときに呼ばれる。`async void` 以外の `_ = SomeAsync();` の失敗を拾える |
| `e.SetObserved()` | 観察済みにする。これを呼ばなくても.NET Core 以降は、プロセスは終了しない |

`_ = LoadThumbnailAsync(entry);` のように `Task` を待たずに放置する書き方は、例外が<strong>黙って消える</strong>危険があります。`UnobservedTaskException` はその安全網です。ただし、タイミングが GC に依存するので、<strong>根本的には `await` するか内部で `try/catch` する</strong>ほうが正しい作りです。

## 手順 2：ログをファイルに書く

画面のログ パネルはアプリを閉じると消えます。クラッシュの調査には<strong>ファイルのログ</strong>が欠かせません。

### ファイル ログ

`Services\FileLogWriter.cs`:

```csharp
using System.Collections.Concurrent;
using System.IO;
using System.Text;

namespace Editor.Services;

// ログを日付ごとのファイルに書く。書き込みは、専用のスレッドで行う（呼び出し側を待たせない）。
public sealed class FileLogWriter : IDisposable
{
    private readonly string _directory;
    private readonly BlockingCollection<string> _queue = new(boundedCapacity: 10000);
    private readonly Thread _thread;

    public FileLogWriter()
    {
        _directory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MiniEngine", "logs");
        Directory.CreateDirectory(_directory);
        DeleteOldLogs(keepDays: 14);

        _thread = new Thread(WriteLoop) { Name = "LogWriter", IsBackground = true };
        _thread.Start();
    }

    public string LogDirectory => _directory;

    public void Write(string level, string source, string message)
    {
        string line = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} [{level}] [{source}] {message}";
        _queue.TryAdd(line);                                   // 満杯なら捨てる（呼び出し側を止めない）
    }

    private void WriteLoop()
    {
        string? currentPath = null;
        StreamWriter? writer = null;
        try
        {
            foreach (string line in _queue.GetConsumingEnumerable())
            {
                string path = Path.Combine(_directory, $"editor-{DateTime.Now:yyyyMMdd}.log");
                if (path != currentPath)
                {
                    writer?.Dispose();
                    writer = new StreamWriter(new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.Read),
                                              new UTF8Encoding(false)) { AutoFlush = true };
                    currentPath = path;
                }
                writer!.WriteLine(line);
            }
        }
        finally
        {
            writer?.Dispose();
        }
    }

    private void DeleteOldLogs(int keepDays)
    {
        foreach (var file in new DirectoryInfo(_directory).GetFiles("editor-*.log"))
        {
            if (file.LastWriteTime < DateTime.Now.AddDays(-keepDays))
            {
                try { file.Delete(); } catch (IOException) { /* 使用中なら、次回 */ }
            }
        }
    }

    public void Dispose()
    {
        _queue.CompleteAdding();
        _thread.Join(2000);
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `BlockingCollection<T>` | スレッド間の待ち行列。`GetConsumingEnumerable()` は要素が来るまで<strong>待ち</strong>、`CompleteAdding()` で終わる。<strong>生産者・消費者</strong>の定番の部品 |
| `boundedCapacity` | 上限。`TryAdd` は満杯のとき `false` を返す。ログのためにプログラムを止めない |
| 専用スレッド | ディスクへの書き込みは遅い。呼び出し側（UI スレッド、描画スレッド）を<strong>待たせない</strong>ように別のスレッドで書く |
| `AutoFlush = true` | 1 行書くたびにディスクに出す。クラッシュ直前のログが失われない |
| `FileShare.Read` | 書き込み中のログを他のプログラム（メモ帳など）が<strong>読める</strong>ようにする |
| `{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff}` | 補間文字列の中の書式指定 |
| 古いログの削除 | 起動時に 14 日より古いものを消す |

### ILogService に結びつける

```csharp
public sealed class LogService : ILogService
{
    private readonly FileLogWriter _file;
    public LogService(FileLogWriter file) { _file = file; }

    private void Add(LogLevel level, string source, string message)
    {
        _file.Write(level.ToString().ToUpperInvariant(), source, message);     // ファイルへ
        // …（第 10 章：画面のコレクションへ、UI スレッドで追加）
    }

    public void Info(string message) => Add(LogLevel.Info, "Editor", message);
    // …
}
```

エンジンからのログは `source` を `"Engine"` にします（第 13 章の `NativeLog.Install` で渡すコールバックの中で、`log.InfoFrom("Engine", message)` のようにソースを指定できる関数を足す）。ゲームは `"Game"`。

### クラッシュ レポート

```csharp
public static class CrashReporter
{
    public static void Report(string title, Exception? exception)
    {
        try
        {
            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                                      "MiniEngine", "crashes");
            Directory.CreateDirectory(dir);
            string path = Path.Combine(dir, $"crash-{DateTime.Now:yyyyMMdd-HHmmss}.txt");

            var sb = new System.Text.StringBuilder();
            sb.AppendLine($"{title}");
            sb.AppendLine($"時刻: {DateTime.Now:O}");
            sb.AppendLine($"OS: {Environment.OSVersion}  64bit: {Environment.Is64BitProcess}");
            sb.AppendLine($"スレッド: {Environment.CurrentManagedThreadId}");
            sb.AppendLine();
            sb.AppendLine(exception?.ToString() ?? "(例外なし)");   // ToString はスタック トレースと、内側の例外を含む
            File.WriteAllText(path, sb.ToString());
        }
        catch
        {
            // レポートの書き込みで失敗しても、もうできることはない
        }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Exception.ToString()` | 型名、メッセージ、<strong>スタック トレース</strong>、<strong>内側の例外</strong>までまとめて文字列にする。ログには `Message` だけでなくこれを書く |
| `StringBuilder` | 文字列を効率よく組み立てるクラス |
| `{DateTime.Now:O}` | ISO 8601 形式（`2026-10-21T12:34:56.789+09:00`） |
| 空の `catch` | ここだけは例外。<strong>クラッシュ レポートの処理自体が失敗</strong>したときにさらに例外を投げても、意味がない |

## 手順 3：ログ パネルを改良する

ログ パネル（第 10 章）に重大度のフィルター、コピー、クリア、自動スクロールを足します。

```csharp
public class LogViewModel : BindableBase
{
    private readonly ILogService _log;
    private LogLevel _minimumLevel = LogLevel.Info;
    private bool _autoScroll = true;

    public LogViewModel(ILogService log)
    {
        _log = log;
        Entries = log.Entries;
        EntriesView = CollectionViewSource.GetDefaultView(Entries);
        EntriesView.Filter = o => o is LogEntry e && e.Level >= _minimumLevel;

        ClearCommand = new DelegateCommand(Entries.Clear);
        CopyCommand = new DelegateCommand<LogEntry>(entry =>
            Clipboard.SetText($"{entry.Time:HH:mm:ss} [{entry.Level}] {entry.Message}"));
    }

    public string Title => "ログ";
    public ObservableCollection<LogEntry> Entries { get; }
    public ICollectionView EntriesView { get; }

    // フィルター：この重大度以上を表示
    public LogLevel MinimumLevel
    {
        get => _minimumLevel;
        set { if (SetProperty(ref _minimumLevel, value)) EntriesView.Refresh(); }
    }

    public bool AutoScroll { get => _autoScroll; set => SetProperty(ref _autoScroll, value); }

    public IEnumerable<LogLevel> Levels { get; } = Enum.GetValues<LogLevel>();

    public DelegateCommand ClearCommand { get; }
    public DelegateCommand<LogEntry> CopyCommand { get; }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `e.Level >= _minimumLevel` | 列挙型の比較。`Info(0) < Warning(1) < Error(2)` なので `>=` で「以上」になる |
| `Enum.GetValues<T>()` | 列挙型のすべての値を取る。`ComboBox` の選択肢に使う |
| `Clipboard.SetText` | クリップボードにコピー |
| ログの上限 | `Entries` が無限に増えないよう<strong>上限（例：5000）を超えたら、古いものを消す</strong>（`LogService.Add` に足す） |

ログの行の色を重大度で変えます。

```xml
<ListBox.ItemContainerStyle>
    <Style TargetType="ListBoxItem">
        <Style.Triggers>
            <DataTrigger Binding="{Binding Level}" Value="Warning">
                <Setter Property="Foreground" Value="#FFF1C40F" />
            </DataTrigger>
            <DataTrigger Binding="{Binding Level}" Value="Error">
                <Setter Property="Foreground" Value="#FFE74C3C" />
            </DataTrigger>
        </Style.Triggers>
    </Style>
</ListBox.ItemContainerStyle>
```

自動スクロール（新しい行が来たら、一番下まで送る）は `CollectionChanged` イベントで `ScrollIntoView` を呼びます。ビューのコードビハインドで書きます。

```csharp
// LogView.xaml.cs
((INotifyCollectionChanged)LogList.Items).CollectionChanged += (_, e) =>
{
    if (e.Action == NotifyCollectionChangedAction.Add && ViewModel?.AutoScroll == true && LogList.Items.Count > 0)
    {
        LogList.ScrollIntoView(LogList.Items[^1]);
    }
};
```

## 手順 4：ネイティブのクラッシュに備える

C++ のアクセス違反（`nullptr` の参照など）は、<strong>C# の `try/catch` では捕まりません</strong>。.NET Core 以降、`AccessViolationException` は捕まえられない例外に分類されプロセスが終了します。調査のために<strong>クラッシュした瞬間のダンプ</strong>を残します。

### エンジン側にダンプを書く仕組み

`EngineApi` に次の関数を足します。

```c
/* クラッシュしたとき、dump_dir に .dmp を書く。起動の最初に 1 度だけ呼ぶ。 */
ME_API MeResult me_install_crash_handler(const char* dump_dir_utf8);
```

```cpp
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")

namespace {
std::wstring g_dump_dir;

LONG WINAPI CrashFilter(EXCEPTION_POINTERS* info) {
  SYSTEMTIME t;
  GetLocalTime(&t);
  wchar_t name[64];
  swprintf_s(name, L"\\crash-%04d%02d%02d-%02d%02d%02d.dmp", t.wYear, t.wMonth, t.wDay, t.wHour, t.wMinute, t.wSecond);
  std::wstring path = g_dump_dir + name;

  HANDLE file = CreateFileW(path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
  if (file != INVALID_HANDLE_VALUE) {
    MINIDUMP_EXCEPTION_INFORMATION mei = {GetCurrentThreadId(), info, FALSE};
    MiniDumpWriteDump(GetCurrentProcess(), GetCurrentProcessId(), file,
                      MiniDumpWithDataSegs | MiniDumpWithHandleData | MiniDumpWithThreadInfo, &mei, nullptr, nullptr);
    CloseHandle(file);
  }
  return EXCEPTION_EXECUTE_HANDLER;                  // ダンプを書いたら、そのまま終了する
}
}  // namespace

MeResult me_install_crash_handler(const char* dump_dir_utf8) {
  return Guard([&]() -> MeResult {
    g_dump_dir = Utf8ToWide(dump_dir_utf8);
    std::filesystem::create_directories(g_dump_dir);
    SetUnhandledExceptionFilter(&CrashFilter);
    return ME_OK;
  });
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `SetUnhandledExceptionFilter` | どこからも処理されなかった、構造化例外（SEH、アクセス違反など）を最後に受ける関数を登録する Win32 API |
| `MiniDumpWriteDump` | プロセスのメモリ、スレッド、スタックを `.dmp` ファイルに書く（`dbghelp.dll`） |
| `MiniDumpWithDataSegs` など | ダンプに含める情報の指定。大きくなりすぎない範囲で有用な物を選ぶ |
| `EXCEPTION_EXECUTE_HANDLER` | 例外を処理したことにして、プロセスを終了する |
| 限界 | クラッシュ ハンドラーの中は、<strong>プロセスが壊れかけている</strong>。ヒープを確保する処理（`std::wstring` の連結など）が危険な場合がある。本格的な製品は<strong>別プロセスのクラッシュ ハンドラー</strong>（Crashpad、Breakpad、Sentry など）を使う |

C# 側の起動で呼びます。

```csharp
[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_install_crash_handler(string dumpDir);

// App.OnInitialized
NativeMethods.me_install_crash_handler(Path.Combine(
    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MiniEngine", "crashes"));
```

### ダンプを読む

`.dmp` を Visual Studio にドラッグして開くとクラッシュした位置と、その時の変数が見られます。

1. `.dmp` を開く → 「<strong>混合でデバッグ</strong>」（C# と C++ の両方）を押す。
2. シンボル（`.pdb`）が必要。<strong>ビルドごとに `.pdb` を保存</strong>しておく。
3. コール スタックの一番上が、クラッシュした位置。

## 手順 5：利用者に知らせる方法

エラーの種類で知らせる<strong>強さ</strong>を変えます。

| 場面 | 方法 |
| --- | --- |
| 操作の失敗（保存できない） | <strong>メッセージ ボックス</strong>（操作を止めて、確認を求める） |
| 軽い警告（Play できない） | <strong>ステータス バー</strong>＋ログ。邪魔をしない |
| 情報（保存した） | ステータス バーだけ |
| バグ・致命的 | クラッシュ ダイアログ（ログのフォルダーを開くボタン） |

ステータス バーに一時的なメッセージを出す仕組みは `IEventAggregator` で、`StatusMessageEvent` を発行し `MainWindowViewModel` が購読して 5 秒後に消す形にできます（第 10 章）。

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 例外を投げるボタン（テスト用） | ダイアログが出て、「はい」で続行、「いいえ」で終了。クラッシュ レポートが `crashes\` に残る |
| 起動して操作 | `%LOCALAPPDATA%\MiniEngine\logs\editor-YYYYMMDD.log` に行が増える |
| 古いログ | 15 日以上前のファイルが、起動時に消える |
| ログ パネルのフィルターを Warning に | Info の行が消える |
| 行を右クリック → コピー | クリップボードに入る |
| ネイティブにわざと null を参照させる | プロセスが終了し、`crashes\*.dmp` が残る |

## よくあるミス

??? failure "ログがファイルに書かれない"
    `FileLogWriter` を DI のシングルトンとして登録していない。または、ログの書き込みスレッドが例外で止まっている。

??? failure "終了時にログの最後が欠ける"
    アプリの終了時に `FileLogWriter.Dispose()` が呼ばれていない。`OnExit` で呼んで `Join` する。

??? failure "`DispatcherUnhandledException` が呼ばれない"
    別のスレッドの例外。UI スレッド以外の例外は `AppDomain.UnhandledException` に来る。`Task` の中の例外は `await` していない限り `UnobservedTaskException`。

??? failure "未処理の例外で続行を選ぶとさらに壊れる"
    例外が状態の更新の途中で起きた。<strong>続行を許すのは利用者の選択</strong>にしておき既定は終了にするほうが安全。保存していない作業を守るため、<strong>自動バックアップ</strong>を足すのも手。

??? failure "ダンプが空／小さすぎる"
    `MiniDumpWithFullMemory` を使えば大きいが詳しい。`MiniDumpNormal` は小さいが変数が読めない。用途で選ぶ。

??? failure "ダイアログの中で、例外が重なって無限に出る"
    例外ハンドラーの中で、さらに例外が起きている。ハンドラーの中の処理は最小限にして、`try/catch` で包む。

## この章のまとめ

- 失敗を <strong>4 種類</strong>に分け想定内は捕まえて処理、バグと致命的は<strong>記録を残す</strong>。
- 未処理の例外を拾う場所は <strong>3 つ</strong>（UI スレッド、AppDomain、Task）。
- ログは<strong>ファイルにも</strong>書く。書き込みは専用スレッドで呼び出し側を待たせない。
- ネイティブのクラッシュは `try/catch` で捕まらない。<strong>ミニダンプ</strong>を残す。

## 次の章へ

次の章（[第 31 章 スレッド、メモリ、IDisposable](31-threads-memory.md)）ではこれまでに散らばって出てきた<strong>スレッドの約束</strong>と<strong>メモリの扱い</strong>（リーク、破棄、イベントの購読）を整理し長時間動かしても安定するエディタにします。
