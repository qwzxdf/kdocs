---
title: 第 39 章 保存と読み込み
tags:
  - C#連携
---

# 第 39 章 保存と読み込み

この章で、シーンをファイルに保存して、読み込み直せるようにします。JSON の読み書き（`System.Text.Json`）、ファイルを開く／保存するダイアログ、非同期の入出力（`async`/`await`）、未保存のときの確認、ウィンドウを閉じるときの確認を扱います。ファイル形式の設計（バージョン、壊れたファイルへの備え）もここで考えます。

## 保存するのは「エディタのドキュメント」

第 34 章で、データの持ち主はエディタ（`SceneDocument`）と決めました。保存するのも、このドキュメントです。エンジンのシーンはただの写しなので、保存しません。読み込みのときは、ドキュメントを作り直すだけで、`SceneEngineSync` が自動でエンジンへ同期してくれます。

```text
保存： SceneDocument ─▶ DTO（保存用のデータ）─▶ JSON 文字列 ─▶ ファイル
読込： ファイル ─▶ JSON 文字列 ─▶ DTO ─▶ 検証 ─▶ SceneDocument（作り直し）─▶ （自動）エンジンへ
```

途中に DTO（Data Transfer Object、保存専用のデータ型）を挟むのには、理由があります。`SceneObject` をそのまま JSON にすることもできますが、`SceneObject` には画面の状態（`IsSelected`、`IsExpanded`、`IsEditing`）や、親への参照（`Parent`、循環していて JSON にできません）が含まれています。それに、`SceneObject` に項目を足したときに、ファイルの形式が勝手に変わってしまうのも困ります。保存形式は DTO が決める、と切り分けておきます。

## ファイル形式

保存するファイルは、次のような JSON にします。

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

設計の理由を並べます。

| 設計 | 理由 |
| --- | --- |
| `version` を持つ | 将来、形式を変えたとき、古いファイルを読み分けられる |
| 木構造のまま入れ子にする | 親子関係が構造として表れ、`parent` の ID が要らない。読み込みで、親が先に作られる |
| ベクトルは配列 `[x, y, z]` | 短く読みやすい。`{"x":…}` より小さい |
| ID を保存する | Undo や参照のために ID を保つ。読み込み後の採番は、最大の ID の次から |
| 人が読める（インデント付き） | Git の差分で見られる。手で直せる |

## DTO とシリアライザー

```csharp title="Services/Serialization/SceneFileFormat.cs"
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

`System.Text.Json` は .NET 標準の JSON ライブラリで、NuGet は要りません（C++ の nlohmann/json に当たります）。`[JsonPropertyName("version")]` は、C# のプロパティ名（`Version`）と JSON のキー名（`version`）を別にするための属性です。シリアライザーが読み書きするので、プロパティには `set` が要ります。保存用の型は、このように素朴に作ります。`= new()` や `= { 0, 0, 0 }` で初期値を入れておけば、ファイルにキーがなくても `null` になりません。

次が、変換と読み書きです。まず保存の側です。

```csharp title="Services/Serialization/SceneSerializer.cs"
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

`JsonSerializerOptions` は作るのにコストがかかるので、`static readonly` で 1 つを使い回します。`WriteIndented` で改行とインデントを付け、`ReadCommentHandling` と `AllowTrailingCommas` で、手で編集したファイルを少しゆるく読めるようにしています。

読み込みの側は、検証が大事です。

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

外から来るデータは、必ず疑います。ファイルは壊れますし、手で編集されますし、古い版で書かれています。配列の長さを確かめずに `Position[2]` を読めば、例外で落ちます。そこで `Parse`（JSON の解析と検証）と `Apply`（ドキュメントへの反映）を 2 段階に分けています。検証が全部通ってから反映するので、壊れたファイルを開いても、今のドキュメントは壊れません。

`HashSet<uint>.Add` は、追加できたら `true`、すでにあれば `false` を返すので、ID の重複の検出に使えます。ファイルの問題には専用の `SceneFileException` を用意して、他の例外と区別し、利用者に見せるメッセージを持たせました。

## ファイルの読み書き（非同期）

```csharp title="Services/ISceneFileService.cs"
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

実装は、保存と開くに分けて見ます。まず保存です。

```csharp title="Services/SceneFileService.cs"
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

保存先のファイルへ直接書かず、一時ファイル（`.tmp`）に書いてから `File.Move` で置き換えています。書き込み中にクラッシュしたり電源が落ちたりしても、保存先が半分だけ書かれた壊れたファイルになりません。壊れるのは一時ファイルだけで、元のファイルは無事です。定番の方法なので覚えておいてください。

`new UTF8Encoding(false)` は BOM（先頭の目印）なしの UTF-8 です。JSON は BOM なしが標準です（[文字コード](../encoding/index.md)）。`File.WriteAllTextAsync` は非同期版なので、書き込みを待つ間も UI が止まりません。

`catch (Exception e) when (...)` は例外フィルターで、条件に合うときだけ `catch` します。`IOException`（ディスクが満杯、他で使用中など）と `UnauthorizedAccessException`（書き込み権限がない）だけを受け止め、想定外の例外は握りつぶさずに外へ出します。成功したら `_history.MarkSaved()` で、履歴に「ここが保存点」と教えます（第 38 章）。

続いて、開く側です。

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

開く処理の流れは、「未保存なら確認」→「ファイルを選ぶ」→「別のスレッドで読んで検証する」→「UI スレッドでドキュメントを作り直す」です。`Task.Run(() => ...)` は、処理をスレッド プールの別のスレッドで実行して、`await` で結果を待ちます。大きなファイルでも UI が固まりません。

ここで大事なのが、どのスレッドで何を触るかです。ドキュメントを触るのは UI スレッドだけにします。WPF では `await` のあと、実行は元のスレッド（UI スレッド）に戻ります。だから、`await Task.Run(...)` の次の行で、ドキュメントを触ってよいのです。`Parse` を別スレッドで済ませてから、`Apply` をこちらで行う 2 段階の形が、ここで活きます。

`_document.Clear()` は、既存の物をすべて空にします。全部の物について `Destroyed` が発行されるので、エンジンのシーンも空になります。読み込んだあとは `_history.Clear()` で履歴を捨てます。別のシーンの Undo 履歴を引き継ぐと、混乱するからです。

### メッセージ ボックスのサービス

確認のメッセージ ボックスも、ビューモデルから直接呼ばず、サービスの後ろに隠します（第 18 章）。ビューモデルが `MessageBox` を直接呼ぶと、テストできなくなるからです。

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

`MessageBox.Show` は標準のメッセージ ボックスで、ボタンの種類（`YesNoCancel`）とアイコンを指定できます。

## メニュー、キー、タイトル

`MainWindowViewModel` に、ファイル操作のコマンドを足します。

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

`DelegateCommand.FromAsync` は、非同期の処理を持つコマンドを作ります。`async void` に頼らないので例外の扱いが安全で、実行中は `CanExecute` が自動で `false` になり、二重に実行されません。`Title` の補間文字列の中の式は、`( )` で囲んで条件式を書いています。

## ウィンドウを閉じるときの確認

`Window.Closing` は、閉じるのをキャンセルできるイベントです。ただ、このイベントの中では、非同期の確認（ダイアログ）を待てません。そこで、いったん閉じるのを止めて、確認が済んだら閉じ直す、という方式にします。

```csharp title="MainWindow.xaml.cs"
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

`async void` は、イベント ハンドラーにだけ許される書き方です。戻り値がなく、例外が呼び出し元に伝わらないので、普通の関数には使いません。

## 設定の保存（最近開いたファイル）

アプリの設定（最近開いたファイルなど）は、`%APPDATA%` に保存します。

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

`SpecialFolder.ApplicationData` は `C:\Users\<名前>\AppData\Roaming` で、ユーザーごとの設定の置き場所です。`Directory.CreateDirectory` は、フォルダーがあれば何もしません。`GetDirectoryName(...)!` の `!` は、「`null` は返らないと分かっている」という警告の抑制です。設定は「なくても動く」情報なので、壊れていたら既定で始めて、利用者の作業を止めません。シーンのファイルと違って、設定は握りつぶしてよい失敗です。

## 動かして確かめる

| 操作 | 期待する結果 |
| --- | --- |
| 物をいくつか作って `Ctrl+S` | ファイル ダイアログが出る。保存すると、タイトル バーの `*` が消えて、ファイル名が出る |
| 保存したファイルをメモ帳で開く | 読める JSON になっている |
| 編集して `Ctrl+S` | 上書き保存（ダイアログなし） |
| `Ctrl+N`（未保存の変更あり） | 「保存しますか？」が出る。キャンセルで何も起きない |
| `Ctrl+O` で開く | シーンが復元される。親子、色、位置も同じ。Undo の履歴は空 |
| ファイルを壊して（`{` だけにして）開く | エラー メッセージが出て、今のシーンはそのまま |
| ID を重複させたファイルを開く | 「ID が重複しています」のエラー。シーンは壊れない |
| 未保存でウィンドウを閉じる | 確認が出る。「キャンセル」で閉じない |

??? failure "保存したファイルの日本語が化ける"
    BOM 付き UTF-8 や ANSI で書いています。`new UTF8Encoding(false)` を指定します。

??? failure "読み込んだあと、エンジンに物が出ない"
    `Apply` で `Create` したときの `Changed` が、`SceneEngineSync` に届く必要があります。`SceneEngineSync` が解決（作成）されているかを確認します。

??? failure "読み込み後に新規作成した物の ID が、既存と衝突する"
    `SceneDocument.Create(…, id)` が、`_nextId` を最大 ID の次に更新していません（第 34 章）。

??? failure "「保存しますか？」が、保存直後にも出る"
    `MarkSaved` を呼んでいないか、保存のあとの合体で保存点の中身が変わっています。

??? failure "`await` の後で `InvalidOperationException`（別のスレッドが所有）"
    `ConfigureAwait(false)` を付けて、UI スレッドに戻っていません。UI を触る処理の前では付けません。

??? failure "保存の途中で落ちて、ファイルが空になった"
    一時ファイルを経由せず、直接上書きしています。

## この章のまとめ

- 保存は DTO を通して、保存形式と内部表現を分ける。
- ファイルは外部入力。必ず検証して、失敗したとき今のシーンを壊さない（読み込みは 2 段階）。
- 書き込みは、一時ファイルから置き換えて、壊れた保存ファイルを避ける。
- `async`/`await` と `Task.Run` で、UI を止めずに入出力する。
- 閉じる前の確認は、「止めて、確認して、閉じ直す」。

次の章では、プロジェクトのフォルダーのファイルを一覧にして、ビューポートへドラッグ アンド ドロップできるようにします。

[第 40 章 アセット ブラウザ](40-asset-browser.md) へ進みます。
