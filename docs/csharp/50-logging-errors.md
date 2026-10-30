---
title: 第 50 章 ログとエラー処理
tags:
  - C#連携
---

# 第 50 章 ログとエラー処理

エディタが大きくなると、失敗の種類が増えます。ファイルが壊れている、ゲームの DLL が読み込めない、GPU が応答しない、C# の例外、C++ の例外、ネイティブのクラッシュ…。この章では、それらをどこで受け止めて、どう記録して、どう利用者に知らせるか、という方針を整えて、実装します。

!!! info "このページを読む前に"
    - [第 49 章 Play モード](49-play-mode.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## 失敗を 4 つに分ける

失敗の扱いは、誰の責任かで変わります。

| 種類 | 例 | 対応 |
| --- | --- | --- |
| ① 想定内の失敗（利用者の操作・環境） | ファイルが無い、壊れている、ディスクが満杯、権限がない | 捕まえて、分かりやすいメッセージを出す。作業は続ける |
| ② 想定内の失敗（外部のコード） | ゲーム DLL の版違い、ビルド失敗 | 捕まえてログに出す。古い状態を保つ（第 48 章） |
| ③ プログラムのバグ | `NullReferenceException`、範囲外、不正な状態 | 記録して、続けるか終了する。握りつぶさない |
| ④ 致命的な失敗 | ネイティブのアクセス違反、GPU のデバイス消失 | 記録して終了。クラッシュ レポートを残す |

①②は、例外を捕まえて処理します。③④は、捕まえきれないか、捕まえても直せないので、記録を残すことが最も大切です。

そのための原則を 4 つ決めておきます。

| 原則 | 内容 |
| --- | --- |
| 握りつぶさない | `catch { }` で何もしない例外処理は、バグを隠す。想定内の型に絞って、必ずログを残す |
| 近い所で捕まえない | 例外は「何をすべきか決められる場所」まで投げ上げる。低い層（ファイル読み込み）は投げ、高い層（コマンド）が利用者に知らせる |
| ログは再現のための記録 | 「何が起きたか」だけでなく、「その時、何をしていたか」（直前の操作）が分かるようにする |
| 利用者のメッセージと開発者のログを分ける | 利用者には「ファイルを開けませんでした」、ログには例外の全文とスタック トレースを書く |

この章のゴールは次のとおりです。

- すべての未処理の例外を拾って、ログに残して、利用者に知らせる。
- ログをファイルに書く（日付ごとに分け、古いものは自動で消す）。
- ログ パネルを重大度のフィルター、コピー、クリア付きに改良する。
- ネイティブのクラッシュのとき、ミニダンプを残す。

## 未処理の例外を拾う

.NET には、未処理の例外を拾う場所が 3 つあります。拾える対象がそれぞれ違います。

| 場所 | 拾える例外 | 続行できるか |
| --- | --- | --- |
| `Application.DispatcherUnhandledException` | UI スレッドで起きた未処理の例外 | `e.Handled = true` で続行できる |
| `AppDomain.CurrentDomain.UnhandledException` | どのスレッドでも、最終的に未処理の例外 | 続行不可（プロセスは終了する） |
| `TaskScheduler.UnobservedTaskException` | 誰も `await` しなかった `Task` の例外 | 続行できる（観察済みにする） |

```csharp title="App.xaml.cs"
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

①の `e.Handled = true` は、例外を処理済みにして、アプリを続けます。ただし、状態が壊れている可能性があるので、続けるかどうかは利用者に選ばせています。

②は、どのスレッドの例外でも最後に拾う網です。ここに来たらプロセスは終了するので、記録できる最後の機会になります。引数が `object` なのは、`Exception` 以外が投げられることもあるからです（C++/CLI など）。

③は、`Task` の例外を誰も見ないまま、その `Task` が GC されたときに呼ばれます。`_ = SomeAsync();` のように放置した `Task` の失敗を拾えます。`e.SetObserved()` で観察済みにしますが、呼ばなくても .NET Core 以降は、プロセスは終了しません。

`_ = LoadThumbnailAsync(entry);`（第 46 章）のように `Task` を待たずに放置する書き方は、例外が黙って消える危険があります。`UnobservedTaskException` はその安全網ですが、タイミングが GC に依存します。根本的には、`await` するか、内部で `try/catch` するほうが正しい作りです。

## ログをファイルに書く

画面のログ パネルは、アプリを閉じると消えます。クラッシュの調査には、ファイルのログが欠かせません。

```csharp title="Log/FileLogWriter.cs"
using System.Collections.Concurrent;
using System.IO;
using System.Text;

namespace Editor.Log;

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

ディスクへの書き込みは遅いので、呼び出し側（UI スレッド、描画スレッド）を待たせないように、専用のスレッドで書きます。スレッド間の受け渡しに使っている `BlockingCollection<T>` は、待ち行列です。`GetConsumingEnumerable()` は、要素が来るまで待ち、`CompleteAdding()` で終わります。「入れる側」と「取り出す側」を別のスレッドにする、定番の部品です。`boundedCapacity`（上限）を付けて、`TryAdd` が満杯のときは捨てることで、ログのためにプログラムを止めないようにしています。

`AutoFlush = true` は、1 行書くたびにディスクへ出す設定です。クラッシュ直前のログが失われません。`FileShare.Read` は、書き込み中のログを他のプログラム（メモ帳など）が読めるようにします。`{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff}` は、補間文字列の中の書式指定です。起動時に 14 日より古いログを消します。

`LogService`（第 24 章）は、これに書くように変えます。

```csharp
public sealed class LogService : ILogService
{
    private readonly FileLogWriter _file;
    public LogService(FileLogWriter file) { _file = file; }

    private void Add(LogLevel level, string source, string message)
    {
        _file.Write(level.ToString().ToUpperInvariant(), source, message);     // ファイルへ
        // …（第 24 章：画面のコレクションへ UI スレッドで追加）
    }

    public void Info(string message) => Add(LogLevel.Info, "Editor", message);
    // …
}
```

エンジンからのログは `source` を `"Engine"`、ゲームからは `"Game"` にします（第 32 章でエンジンのログを受け取るコールバックの中で、`log.InfoFrom("Engine", message)` のように、ソースを指定できる関数を足します）。

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

`Exception.ToString()` は、型名、メッセージ、スタック トレース、内側の例外までまとめて文字列にします。ログには、`Message` だけでなく、これを書きます。`StringBuilder` は文字列を効率よく組み立てるクラスで、`{DateTime.Now:O}` は ISO 8601 形式（`2026-10-21T12:34:56.789+09:00`）です。

空の `catch` が出てきますが、ここだけは例外です。クラッシュ レポートを書く処理自体が失敗したときに、さらに例外を投げても、意味がないからです。

## ログ パネルを改良する

ログ パネル（第 24 章）に重大度のフィルター、コピー、クリア、自動スクロールを足します。

```csharp
public partial class LogViewModel : ObservableObject
{
    private readonly ILogService _log;

    public LogViewModel(ILogService log)
    {
        _log = log;
        Entries = log.Entries;
        EntriesView = CollectionViewSource.GetDefaultView(Entries);
        EntriesView.Filter = o => o is LogEntry e && e.Level >= MinimumLevel;
    }

    public string Title => "ログ";
    public ObservableCollection<LogEntry> Entries { get; }
    public ICollectionView EntriesView { get; }

    // フィルター：この重大度以上を表示
    [ObservableProperty]
    private LogLevel _minimumLevel = LogLevel.Info;

    partial void OnMinimumLevelChanged(LogLevel value) => EntriesView.Refresh();

    [ObservableProperty]
    private bool _autoScroll = true;

    public IEnumerable<LogLevel> Levels { get; } = Enum.GetValues<LogLevel>();

    [RelayCommand]
    private void Clear() => Entries.Clear();                  // ClearCommand が生成される

    [RelayCommand]
    private void Copy(LogEntry entry) =>                      // CopyCommand が生成される
        Clipboard.SetText($"{entry.Time:HH:mm:ss} [{entry.Level}] {entry.Message}");
}
```

絞り込みの仕組みは、第 46 章の検索と同じ `ICollectionView` です。`e.Level >= MinimumLevel` は列挙型の比較で、`Info(0) < Warning(1) < Error(2)` なので、`>=` で「この重大度以上」になります。`Enum.GetValues<T>()` は、列挙型のすべての値を取るので、`ComboBox` の選択肢に使えます。`Entries` が無限に増えないよう、上限（たとえば 5000）を超えたら古いものを消す処理も、`LogService.Add` に足してください。

ログの行の色は、重大度で変えます。

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

自動スクロール（新しい行が来たら一番下まで送る）は、`CollectionChanged` イベントで `ScrollIntoView` を呼びます。ビューのコードビハインドで書きます。

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

## ネイティブのクラッシュに備える

C++ のアクセス違反（`nullptr` の参照など）は、C# の `try/catch` では捕まりません。.NET Core 以降、`AccessViolationException` は捕まえられない例外として扱われ、プロセスが終了します。調査のために、クラッシュした瞬間のダンプを残します。

`EngineApi` に、次の関数を足します。

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

`SetUnhandledExceptionFilter` は、どこからも処理されなかった構造化例外（SEH、アクセス違反など）を最後に受ける関数を登録する Win32 API です。`MiniDumpWriteDump`（`dbghelp.dll`）がプロセスのメモリ、スレッド、スタックを `.dmp` ファイルに書きます。`MiniDumpWithDataSegs` などは、ダンプに含める情報の指定で、大きくなりすぎない範囲で、役に立つものを選んでいます。`EXCEPTION_EXECUTE_HANDLER` を返すと、例外を処理したことにして、プロセスが終了します。

限界も知っておいてください。クラッシュ ハンドラーの中は、プロセスが壊れかけています。ヒープを確保する処理（`std::wstring` の連結など）が危険な場合があります。本格的な製品では、別プロセスのクラッシュ ハンドラー（Crashpad、Breakpad、Sentry など）を使います。

C# 側は、起動時に呼びます。

```csharp
[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_install_crash_handler(string dumpDir);

// App.OnInitialized
NativeMethods.me_install_crash_handler(Path.Combine(
    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MiniEngine", "crashes"));
```

残ったダンプは、Visual Studio にドラッグして開くと、クラッシュした位置と、そのときの変数が見られます。

1. `.dmp` を開いて、「混合でデバッグ」（C# と C++ の両方）を押す。
2. シンボル（`.pdb`）が必要なので、ビルドごとに `.pdb` を保存しておく。
3. コール スタックの一番上がクラッシュした位置。

## 利用者への知らせ方

エラーの種類で、知らせる強さを変えます。

| 場面 | 方法 |
| --- | --- |
| 操作の失敗（保存できない） | メッセージ ボックス（操作を止めて、確認を求める） |
| 軽い警告（Play できない） | ステータス バーとログ。邪魔をしない |
| 情報（保存した） | ステータス バーだけ |
| バグ・致命的 | クラッシュ ダイアログ（ログのフォルダーを開くボタン） |

ステータス バーに一時的なメッセージを出す仕組みは、`IEventAggregator` で `StatusMessageEvent` を発行し、`MainWindowViewModel` が購読して 5 秒後に消す形にできます（第 24 章）。

## 動かして確かめる

| 操作 | 期待する結果 |
| --- | --- |
| 例外を投げるボタン（テスト用） | ダイアログが出る。「はい」で続行、「いいえ」で終了。クラッシュ レポートが `crashes\` に残る |
| 起動して操作 | `%LOCALAPPDATA%\MiniEngine\logs\editor-YYYYMMDD.log` に行が増える |
| 古いログ | 15 日以上前のファイルが起動時に消える |
| ログ パネルのフィルターを Warning に | Info の行が消える |
| 行を右クリック → コピー | クリップボードに入る |
| ネイティブにわざと null を参照させる | プロセスが終了し、`crashes\*.dmp` が残る |

??? failure "ログがファイルに書かれない"
    `FileLogWriter` を DI のシングルトンとして登録していないか、ログの書き込みスレッドが例外で止まっています。

??? failure "終了時にログの最後が欠ける"
    アプリの終了時に `FileLogWriter.Dispose()` が呼ばれていません。`OnExit` で呼んで `Join` します。

??? failure "`DispatcherUnhandledException` が呼ばれない"
    別のスレッドの例外です。UI スレッド以外の例外は `AppDomain.UnhandledException` に来ます。`Task` の中の例外は、`await` していない限り `UnobservedTaskException` に来ます。

??? failure "未処理の例外で続行を選ぶと、さらに壊れる"
    例外が状態の更新の途中で起きました。続行を許すのは利用者の選択にして、既定は終了にするほうが安全です。保存していない作業を守るために、自動バックアップを足すのも手です。

??? failure "ダンプが空、または小さすぎる"
    `MiniDumpWithFullMemory` を使えば大きいが詳しく、`MiniDumpNormal` は小さいが変数が読めません。用途で選びます。

??? failure "ダイアログの中で、例外が重なって無限に出る"
    例外ハンドラーの中で、さらに例外が起きています。ハンドラーの中の処理は最小限にして、`try/catch` で包みます。

## この章のまとめ

- 失敗を 4 種類に分け、想定内は捕まえて処理し、バグと致命的な失敗は記録を残す。
- 未処理の例外を拾う場所は 3 つ（UI スレッド、AppDomain、Task）。
- ログはファイルにも書く。書き込みは専用スレッドで、呼び出し側を待たせない。
- ネイティブのクラッシュは `try/catch` で捕まらない。ミニダンプを残す。

次の章では、これまで散らばって出てきたスレッドの約束とメモリの扱いを整理します。

[第 51 章 スレッド、メモリ、IDisposable](51-threads-memory.md) へ進みます。
