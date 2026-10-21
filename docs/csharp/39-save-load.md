---
title: 第 39 章 保存と読み込み
tags:
  - C#連携
---

# 第 39 章 保存と読み込み

この章では、シーンを<strong>ファイルに保存</strong>し、<strong>読み込み直せる</strong>ようにします。JSON の読み書き（`System.Text.Json`）、ファイルを開く／保存のダイアログ、非同期の入出力（`async`/`await`）、未保存のときの確認、ウィンドウを閉じるときの確認を扱います。ファイル形式の設計（バージョン、壊れたファイルへの備え）も、ここで考えます。

## この章の考え方

### 保存するのは「エディタのドキュメント」

第 34 章で、<strong>データの持ち主はエディタ</strong>（`SceneDocument`）と決めました。保存するのも、このドキュメントです。エンジンのシーンは、写しにすぎないので、保存しません。読み込みは、ドキュメントを作り直すと、<strong>エンジンへの同期が自動で走ります</strong>（`SceneEngineSync`）。

```text
保存： SceneDocument ─▶ DTO（保存用のデータ）─▶ JSON 文字列 ─▶ ファイル
読込： ファイル ─▶ JSON 文字列 ─▶ DTO ─▶ 検証 ─▶ SceneDocument（作り直し）─▶ （自動）エンジンへ
```

### なぜ DTO を挟むのか

`SceneObject` を、そのまま JSON にすることもできます。しかし、

- `SceneObject` には、<strong>画面の状態</strong>（`IsSelected`、`IsExpanded`、`IsEditing`）や、<strong>親への参照</strong>（`Parent`）が含まれる。これらは保存したくないし、参照が循環していて JSON にできない。
- 保存形式を、`SceneObject` の内部の変更から<strong>切り離したい</strong>。`SceneObject` に項目を足しても、ファイル形式が勝手に変わらないようにする。

そこで、<strong>保存専用のデータ型（DTO、Data Transfer Object）</strong>を作ります。保存形式は、DTO が決めます。

## この章のゴール

- 新規、開く、保存、名前を付けて保存ができる。
- 保存したファイルを開くと、同じシーンが復元される。
- 未保存のまま「新規」「開く」「閉じる」をしようとすると、確認が出る。
- 壊れたファイルを開いても、アプリが落ちず、今の作業が失われない。

## 手順 1：ファイル形式

保存するファイルは、このような JSON にします。

```json
{
  "version": 1,
  "objects": [
    {
      "id": 1,
      "name": "Cube",
      "position": [0, 0.5, 0],
      "rotationDegrees": [0, 45, 0],
      "scale": [1, 1, 1],
      "color": [0.8, 0.2, 0.2, 1],
      "children": [
        { "id": 2, "name": "Child", "position": [0, 1, 0], "rotationDegrees": [0, 0, 0],
          "scale": [0.5, 0.5, 0.5], "color": [0.8, 0.8, 0.8, 1], "children": [] }
      ]
    }
  ]
}
```

| 設計 | 理由 |
| --- | --- |
| `version` を持つ | 将来、形式を変えたとき、古いファイルを読み分けられる |
| 木構造のまま入れ子 | 親子関係が、構造として表れ、`parent` の ID が不要。読み込みで、親が先に作られる |
| ベクトルは配列 `[x, y, z]` | 短く、読みやすい。`{"x":…}` より小さい |
| ID を保存する | Undo や参照のため、ID を保つ。読み込み後の採番は、最大の ID の次から |
| 人が読める（インデント付き） | Git の差分で見られる。手で直せる |

## 手順 2：DTO とシリアライザー

`Services\Serialization\SceneFileFormat.cs`:

```csharp
using System.Text.Json.Serialization;

namespace Editor.Services.Serialization;

// 保存ファイル全体
public sealed class SceneFileDto
{
    [JsonPropertyName("version")]
    public int Version { get; set; }

    [JsonPropertyName("objects")]
    public List<ObjectDto> Objects { get; set; } = new();
}

// 物 1 つ分（子を含む）
public sealed class ObjectDto
{
    [JsonPropertyName("id")] public uint Id { get; set; }
    [JsonPropertyName("name")] public string Name { get; set; } = "";
    [JsonPropertyName("position")] public float[] Position { get; set; } = { 0, 0, 0 };
    [JsonPropertyName("rotationDegrees")] public float[] RotationDegrees { get; set; } = { 0, 0, 0 };
    [JsonPropertyName("scale")] public float[] Scale { get; set; } = { 1, 1, 1 };
    [JsonPropertyName("color")] public float[] Color { get; set; } = { 0.8f, 0.8f, 0.8f, 1f };
    [JsonPropertyName("children")] public List<ObjectDto> Children { get; set; } = new();
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `System.Text.Json` | .NET 標準の JSON ライブラリ（NuGet 不要）。C++ の nlohmann/json に当たる |
| `[JsonPropertyName("version")]` | C# のプロパティ名（`Version`）と、JSON のキー名（`version`）を、<strong>別にする</strong>属性 |
| `{ get; set; }` の DTO | シリアライザーが読み書きするので、`set` が要る。保存用の型は、このように素朴にする |
| 配列の初期化 `= { 0, 0, 0 }` | プロパティの初期値として、配列初期化子を直接書ける |
| `= new()` | `List<T>` の初期化。ファイルにキーが無くても、`null` にならない |

### 変換と読み書き

`Services\Serialization\SceneSerializer.cs`:

```csharp
using System.Numerics;
using System.Text.Json;
using Editor.Models;

namespace Editor.Services.Serialization;

public static class SceneSerializer
{
    public const int CurrentVersion = 1;

    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,                          // 人が読める形で書く
        ReadCommentHandling = JsonCommentHandling.Skip, // 手で書き足したコメントは読み飛ばす
        AllowTrailingCommas = true,                    // 手で編集した末尾のカンマを許す
    };

    // ── 保存：ドキュメント → JSON 文字列 ──
    public static string Serialize(SceneDocument document)
    {
        var dto = new SceneFileDto { Version = CurrentVersion };
        foreach (var root in document.Roots) dto.Objects.Add(ToDto(root));
        return JsonSerializer.Serialize(dto, Options);
    }

    private static ObjectDto ToDto(SceneObject o)
    {
        var dto = new ObjectDto
        {
            Id = o.Id,
            Name = o.Name,
            Position = new[] { o.Position.X, o.Position.Y, o.Position.Z },
            RotationDegrees = new[] { o.RotationDegrees.X, o.RotationDegrees.Y, o.RotationDegrees.Z },
            Scale = new[] { o.Scale.X, o.Scale.Y, o.Scale.Z },
            Color = new[] { o.Color.X, o.Color.Y, o.Color.Z, o.Color.W },
        };
        foreach (var child in o.Children) dto.Children.Add(ToDto(child));
        return dto;
    }
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `JsonSerializerOptions` | 読み書きの設定。作成にはコストがかかるので、`static readonly` で<strong>1 つを使い回す</strong> |
| `WriteIndented` | 改行とインデントを付けて書く |
| `JsonSerializer.Serialize(obj, options)` | オブジェクトを JSON 文字列にする |
| `new[] { a, b, c }` | 型を推論した配列の作成（この場合は `float[]`） |
| `ReadCommentHandling`、`AllowTrailingCommas` | 厳密な JSON より、少しゆるく読む設定。手で編集するファイルに向く |

### 読み込みと検証

```csharp
    // ── 読み込み：JSON 文字列 → DTO（検証つき）──
    public static SceneFileDto Parse(string json)
    {
        SceneFileDto? dto;
        try
        {
            dto = JsonSerializer.Deserialize<SceneFileDto>(json, Options);
        }
        catch (JsonException e)
        {
            throw new SceneFileException($"JSON の形式が正しくありません: {e.Message}", e);
        }
        if (dto == null) throw new SceneFileException("ファイルが空です");
        if (dto.Version < 1 || dto.Version > CurrentVersion)
        {
            throw new SceneFileException($"対応していないバージョンです（{dto.Version}）。このエディタは {CurrentVersion} まで対応しています");
        }
        Validate(dto);
        return dto;
    }

    // ID の重複、不正な配列の長さを調べる
    private static void Validate(SceneFileDto dto)
    {
        var ids = new HashSet<uint>();
        void Check(ObjectDto o)
        {
            if (o.Id == 0) throw new SceneFileException("ID が 0 の物があります");
            if (!ids.Add(o.Id)) throw new SceneFileException($"ID {o.Id} が重複しています");
            if (o.Position.Length != 3 || o.RotationDegrees.Length != 3 || o.Scale.Length != 3 || o.Color.Length != 4)
            {
                throw new SceneFileException($"物 {o.Id} の数値の個数が正しくありません");
            }
            foreach (var c in o.Children) Check(c);
        }
        foreach (var root in dto.Objects) Check(root);
    }

    // DTO → ドキュメント（ドキュメントは空にしてから呼ぶ）
    public static void Apply(SceneFileDto dto, SceneDocument document)
    {
        void Build(ObjectDto o, SceneObject? parent)
        {
            var obj = document.Create(o.Name, parent, o.Id);
            obj.Position = new Vector3(o.Position[0], o.Position[1], o.Position[2]);
            obj.RotationDegrees = new Vector3(o.RotationDegrees[0], o.RotationDegrees[1], o.RotationDegrees[2]);
            obj.Scale = new Vector3(o.Scale[0], o.Scale[1], o.Scale[2]);
            obj.Color = new Vector4(o.Color[0], o.Color[1], o.Color[2], o.Color[3]);
            document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
            document.NotifyChanged(SceneChangeKind.ColorChanged, obj);
            foreach (var child in o.Children) Build(child, obj);
        }
        foreach (var root in dto.Objects) Build(root, null);
    }
}

// 保存ファイルの問題を表す例外（利用者に見せるメッセージを持つ）
public sealed class SceneFileException : Exception
{
    public SceneFileException(string message) : base(message) { }
    public SceneFileException(string message, Exception inner) : base(message, inner) { }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `JsonSerializer.Deserialize<T>(json, options)` | JSON 文字列から、型 `T` のオブジェクトを作る。形式が不正だと `JsonException` |
| 結果が `T?` | JSON が `null` のとき、`null` を返す |
| 検証 | <strong>外部から来たデータは、必ず疑う</strong>。ファイルは壊れる、手で編集される、古い版で書かれる。配列の長さを確かめずに `[2]` を読むと、例外で落ちる |
| `HashSet<uint>.Add` | 追加できたら `true`。すでにあれば `false`。重複の検出に使える |
| 専用の例外 | `SceneFileException` で、「ファイルの問題」を、他の例外と区別して、利用者に見せられるようにする |
| 先に `Parse`、検証が通ってから `Apply` | <strong>検証に失敗したとき、ドキュメントを壊さない</strong>ために、2 段階にする |

## 手順 3：ファイルの読み書き（非同期）

`Services\ISceneFileService.cs`:

```csharp
namespace Editor.Services;

public interface ISceneFileService
{
    string? CurrentPath { get; }
    string DisplayName { get; }               // タイトル バーに出す名前

    Task<bool> NewAsync();                    // false なら、キャンセルされた
    Task<bool> OpenAsync();
    Task<bool> SaveAsync();
    Task<bool> SaveAsAsync();

    // 閉じる前などに、未保存の確認をする。続けてよければ true
    Task<bool> ConfirmDiscardAsync();

    event Action? FileChanged;
}
```

### 実装：保存

```csharp
using System.IO;
using Editor.Models;
using Editor.Services.Serialization;
using Editor.Services.Undo;

namespace Editor.Services;

public sealed class SceneFileService : ISceneFileService
{
    private const string Filter = "シーン (*.scene)|*.scene|すべてのファイル (*.*)|*.*";

    private readonly SceneDocument _document;
    private readonly IHistoryService _history;
    private readonly IFileDialogService _dialogs;
    private readonly IMessageService _messages;
    private readonly ILogService _log;

    public SceneFileService(SceneDocument document, IHistoryService history, IFileDialogService dialogs,
                            IMessageService messages, ILogService log)
    {
        _document = document;
        _history = history;
        _dialogs = dialogs;
        _messages = messages;
        _log = log;
    }

    public string? CurrentPath { get; private set; }
    public string DisplayName => CurrentPath == null ? "無題" : Path.GetFileName(CurrentPath);
    public event Action? FileChanged;

    public async Task<bool> SaveAsync()
    {
        if (CurrentPath == null) return await SaveAsAsync();
        return await WriteAsync(CurrentPath);
    }

    public async Task<bool> SaveAsAsync()
    {
        string? path = _dialogs.SaveFile(Filter, DisplayName == "無題" ? "scene1.scene" : DisplayName);
        if (path == null) return false;
        return await WriteAsync(path);
    }

    private async Task<bool> WriteAsync(string path)
    {
        try
        {
            string json = SceneSerializer.Serialize(_document);

            // 一時ファイルに書いてから、置き換える。書き込み中に落ちても、元のファイルは壊れない。
            string temp = path + ".tmp";
            await File.WriteAllTextAsync(temp, json, new System.Text.UTF8Encoding(false));
            File.Move(temp, path, overwrite: true);

            CurrentPath = path;
            _history.MarkSaved();
            _log.Info($"保存しました: {path}");
            FileChanged?.Invoke();
            return true;
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException)
        {
            _messages.Error($"保存に失敗しました。\n{e.Message}");
            _log.Error($"保存に失敗: {e.Message}");
            return false;
        }
    }
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Task<bool>` | 非同期の関数が返す型。`await` で、結果の `bool` を取り出す（第 5 章） |
| `async` / `await` | ファイルの書き込みを待つ間、UI スレッドを止めない。`File.WriteAllTextAsync` が非同期版 |
| `new UTF8Encoding(false)` | <strong>BOM なし</strong>の UTF-8。`false` は、BOM（先頭の目印）を付けない指定。JSON は BOM なしが標準（[文字コード](../encoding/index.md)） |
| 一時ファイル → `File.Move` | 書き込み中のクラッシュや電源断で、保存先が<strong>半分だけ書かれた壊れたファイル</strong>になるのを防ぐ定番の方法。`overwrite: true` で上書き |
| `catch (Exception e) when (…)` | <strong>例外フィルター</strong>。条件に合うときだけ `catch` する。`e is IOException or UnauthorizedAccessException` は、型のパターンの `or` |
| `IOException` | ファイルの読み書きの失敗（ディスクが満杯、ファイルが他で使用中、など） |
| `UnauthorizedAccessException` | 書き込み権限がない |
| `Path.GetFileName` | パスからファイル名だけを取り出す |
| `_history.MarkSaved()` | 履歴に、「ここが保存点」と教える（第 38 章）。これでダーティ フラグが消える |

### 実装：開く

```csharp
    public async Task<bool> OpenAsync()
    {
        if (!await ConfirmDiscardAsync()) return false;
        string? path = _dialogs.OpenFile(Filter);
        if (path == null) return false;

        try
        {
            // 重い処理（読み込みと解析）を、別のスレッドで行う
            SceneFileDto dto = await Task.Run(() => SceneSerializer.Parse(File.ReadAllText(path)));

            // 検証が通ったので、ドキュメントを作り直す（UI スレッドで）
            _document.Clear();
            SceneSerializer.Apply(dto, _document);
            _history.Clear();

            CurrentPath = path;
            _log.Info($"開きました: {path}");
            FileChanged?.Invoke();
            return true;
        }
        catch (Exception e) when (e is SceneFileException or IOException or UnauthorizedAccessException)
        {
            _messages.Error($"開けませんでした。\n{e.Message}");
            _log.Error($"読み込みに失敗: {e.Message}");
            return false;
        }
    }

    public async Task<bool> NewAsync()
    {
        if (!await ConfirmDiscardAsync()) return false;
        _document.Clear();
        _history.Clear();
        CurrentPath = null;
        FileChanged?.Invoke();
        return true;
    }

    public async Task<bool> ConfirmDiscardAsync()
    {
        if (!_history.IsDirty) return true;
        switch (_messages.AskSave(DisplayName))
        {
            case SaveChoice.Save: return await SaveAsync();
            case SaveChoice.DontSave: return true;
            default: return false;                    // キャンセル
        }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Task.Run(() => …)` | 処理を<strong>スレッド プール</strong>の別のスレッドで実行し、`await` で結果を待つ。UI を止めずに、重い解析ができる |
| 2 段階の読み込み | 別のスレッドで、読み込みと検証（`Parse`）を行い、<strong>成功してから</strong>、UI スレッドでドキュメントを作り直す（`Apply`）。ドキュメントを触るのは、UI スレッドだけにする |
| `_document.Clear()` | 既存を空にする。`Destroyed` が全物に対して発行され、<strong>エンジンのシーンも空になる</strong> |
| `_history.Clear()` | 読み込んだ後は、Undo の履歴を捨てる（別のシーンの履歴を、引き継がない） |
| `await` の後の実行スレッド | WPF では、`await` の後は<strong>元のスレッド（UI スレッド）</strong>に戻る。だから、`await Task.Run(…)` の後ろで、ドキュメントを触ってよい |
| `switch (…) { case … }` | `AskSave` の結果で分岐 |

### メッセージ ボックスのサービス

確認のメッセージ ボックスも、ビューモデルから直接呼ばず、サービスにします。

```csharp
namespace Editor.Services;

public enum SaveChoice { Save, DontSave, Cancel }

public interface IMessageService
{
    void Error(string message);
    SaveChoice AskSave(string documentName);
}

public sealed class MessageService : IMessageService
{
    public void Error(string message) =>
        System.Windows.MessageBox.Show(message, "MiniEngine Editor", System.Windows.MessageBoxButton.OK,
            System.Windows.MessageBoxImage.Error);

    public SaveChoice AskSave(string documentName)
    {
        var result = System.Windows.MessageBox.Show(
            $"「{documentName}」への変更を保存しますか？", "MiniEngine Editor",
            System.Windows.MessageBoxButton.YesNoCancel, System.Windows.MessageBoxImage.Question);
        return result switch
        {
            System.Windows.MessageBoxResult.Yes => SaveChoice.Save,
            System.Windows.MessageBoxResult.No => SaveChoice.DontSave,
            _ => SaveChoice.Cancel,
        };
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `MessageBox.Show` | 標準のメッセージ ボックス。ボタンの種類（`YesNoCancel`）、アイコンを指定できる |
| サービスにする理由 | ビューモデルが `MessageBox` を直接呼ぶと、テストできない。ダイアログ類は、サービスの後ろに隠す（第 18 章） |

## 手順 4：メニューとキー、タイトル

`MainWindowViewModel`:

```csharp
public MainWindowViewModel(ISceneFileService files, IHistoryService history /* ほか */)
{
    NewCommand = DelegateCommand.FromAsync(async () => await files.NewAsync());
    OpenCommand = DelegateCommand.FromAsync(async () => await files.OpenAsync());
    SaveCommand = DelegateCommand.FromAsync(async () => await files.SaveAsync());
    SaveAsCommand = DelegateCommand.FromAsync(async () => await files.SaveAsAsync());

    files.FileChanged += () => RaisePropertyChanged(nameof(Title));
    history.Changed += () => RaisePropertyChanged(nameof(Title));
}

public string Title => $"{(_history.IsDirty ? "*" : "")}{_files.DisplayName} - MiniEngine Editor";
```

```xml
<Window.InputBindings>
    <KeyBinding Key="N" Modifiers="Control" Command="{Binding NewCommand}" />
    <KeyBinding Key="O" Modifiers="Control" Command="{Binding OpenCommand}" />
    <KeyBinding Key="S" Modifiers="Control" Command="{Binding SaveCommand}" />
    <KeyBinding Key="S" Modifiers="Control+Shift" Command="{Binding SaveAsCommand}" />
</Window.InputBindings>
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DelegateCommand.FromAsync(Func<Task>)` | 非同期の処理を持つコマンドを作る。`async void` に頼らず、例外の扱いが安全。実行中は、`CanExecute` が自動で `false` になり、<strong>二重実行を防ぐ</strong> |
| `$"{(cond ? "*" : "")}…"` | 補間文字列の中に、式を書く。条件式は `( )` で囲む |

## 手順 5：ウィンドウを閉じるときの確認

`Window.Closing` は、キャンセルできるイベントです。ビューモデルの非同期の確認は、イベントの中では待てないので、<strong>一度キャンセルして、確認が済んだら閉じ直す</strong>方式にします。

`MainWindow.xaml.cs`:

```csharp
private bool _closeConfirmed;

protected override async void OnClosing(System.ComponentModel.CancelEventArgs e)
{
    if (_closeConfirmed)
    {
        base.OnClosing(e);
        return;
    }
    e.Cancel = true;                                      // いったん閉じるのを止める
    if (DataContext is MainWindowViewModel vm && await vm.ConfirmCloseAsync())
    {
        _closeConfirmed = true;
        Close();                                          // もう一度閉じる（今度は通る）
    }
}
```

```csharp
// MainWindowViewModel
public Task<bool> ConfirmCloseAsync() => _files.ConfirmDiscardAsync();
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `OnClosing` | ウィンドウが閉じられる直前に呼ばれる。`e.Cancel = true` で、閉じるのを止められる |
| `async void` | イベント ハンドラーに限り許される書き方。戻り値のない非同期メソッド。例外が呼び出し元に伝わらないので、通常の関数には使わない |
| 「いったん止めて、後で閉じ直す」 | `OnClosing` は同期的に答えを要求する。非同期の確認（ダイアログ）を挟むには、先に止めておくしかない |

## 手順 6：設定の保存（最近開いたファイル）

アプリの設定（最近開いたファイルなど）を、`%APPDATA%` に保存します。

```csharp
using System.Text.Json;

namespace Editor.Services;

public sealed class AppSettings
{
    public List<string> RecentFiles { get; set; } = new();
}

public static class AppSettingsStore
{
    private static string FilePath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "MiniEngine", "settings.json");

    public static AppSettings Load()
    {
        try
        {
            if (File.Exists(FilePath))
                return JsonSerializer.Deserialize<AppSettings>(File.ReadAllText(FilePath)) ?? new AppSettings();
        }
        catch (Exception e) when (e is JsonException or IOException) { /* 壊れていたら、既定で始める */ }
        return new AppSettings();
    }

    public static void Save(AppSettings settings)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(FilePath)!);
        File.WriteAllText(FilePath, JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true }));
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Environment.GetFolderPath(SpecialFolder.ApplicationData)` | `C:\Users\<名前>\AppData\Roaming`。ユーザーごとの設定の置き場所 |
| `Directory.CreateDirectory` | フォルダーを作る（あれば何もしない） |
| `!`（null 許容の抑制） | `GetDirectoryName` は `null` を返しうるが、ここでは返らないと分かっているので、警告を消す |
| 壊れた設定ファイル | 設定は「無くても動く」情報。壊れていたら、<strong>既定で始める</strong>（利用者の作業を止めない） |

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 物をいくつか作って `Ctrl+S` | ファイル ダイアログが出る。保存すると、タイトル バーの `*` が消え、ファイル名が出る |
| 保存したファイルをエディタ（メモ帳）で開く | 読める JSON になっている |
| 編集して `Ctrl+S` | 上書き保存（ダイアログなし） |
| `Ctrl+N`（未保存の変更あり） | 「保存しますか？」が出る。キャンセルで、何も起きない |
| `Ctrl+O` で開く | シーンが復元される。親子、色、位置も同じ。Undo の履歴は空 |
| ファイルを壊して（`{`だけにして）開く | エラー メッセージが出て、今のシーンはそのまま |
| ID を重複させたファイルを開く | 「ID が重複しています」のエラー。シーンは壊れない |
| 未保存でウィンドウを閉じる | 確認が出る。「キャンセル」で閉じない |

## よくあるミス

??? failure "保存したファイルが読めない（日本語が化ける）"
    BOM 付き UTF-8 や、ANSI で書いている。`new UTF8Encoding(false)` を指定する。`File.WriteAllText` の既定は BOM なし UTF-8 だが、明示するのが安全。

??? failure "読み込んだ後、エンジンに物が出ない"
    `Apply` で `Create` したときの `Changed` が、`SceneEngineSync` に届いている必要がある。`SceneEngineSync` が解決されているか確認する。

??? failure "読み込み後に、新規作成した物の ID が、既存と衝突する"
    `SceneDocument.Create(…, id)` が、`_nextId` を最大 ID の次に更新している（第 34 章）。更新が漏れていると、衝突する。

??? failure "「保存しますか？」が、保存直後でも出る"
    `MarkSaved` を呼んでいない。または、保存の後に、合体で保存点の中身が変わっている。

??? failure "`await` の後で、`InvalidOperationException`（別のスレッドが所有）"
    `ConfigureAwait(false)` を付けて、UI スレッドに戻っていない。UI を触る処理の前では、付けない。

??? failure "保存の途中で落ちて、ファイルが空になった"
    一時ファイルを経由せず、直接上書きしている。書き込み中のクラッシュで、元のデータが失われる。

## この章のまとめ

- 保存は <strong>DTO</strong> を通して、保存形式と内部表現を分ける。
- ファイルは<strong>外部入力</strong>。必ず検証し、失敗したとき今のシーンを壊さない（読み込みは 2 段階）。
- 書き込みは、<strong>一時ファイル → 置き換え</strong>で、壊れた保存ファイルを避ける。
- `async`/`await` と `Task.Run` で、UI を止めずに入出力する。
- 閉じる前の確認は、「止めて、確認して、閉じ直す」。

## 次の章へ

次の章（[第 40 章 アセット ブラウザ](40-asset-browser.md)）では、プロジェクトのフォルダーのファイルを一覧にして、ビューポートへドラッグ アンド ドロップできるようにします。フォルダーの変更の監視（`FileSystemWatcher`）、サムネイルの非同期生成、仮想化を扱います。
