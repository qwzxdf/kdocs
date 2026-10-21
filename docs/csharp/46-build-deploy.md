---
title: 第 46 章 ビルド、テスト、配布
tags:
  - C#連携
---

# 第 46 章 ビルド、テスト、配布

この章で、エディタをほかの人に渡せる形にします。リリース ビルドの設定、配布するフォルダーの構成、コマンドラインからのビルド（自動化の入口）、そしてビューモデルのテストを扱います。「自分の PC では動く」から「他の PC でも動く」へ進むための章です。

## 何がないと動かないのか

自分の開発 PC には、Visual Studio、.NET SDK、Windows SDK、VC++ のランタイムなど、大量の道具が入っています。そのため、自分の PC で動いても、道具のない他の PC では動かないことがあります。配布の準備とは、「何がないと動かないか」を洗い出して、同梱するか、要件として伝える作業です。

エディタ（C# + C++）が動くための条件を整理します。

| 必要な物 | 内容 | 同梱の方法 |
| --- | --- | --- |
| .NET ランタイム | `Editor.exe` の実行に必要。8.0 のデスクトップ ランタイム | ①利用者にインストールしてもらう ②アプリに同梱する（自己完結型） |
| VC++ ランタイム | `Engine.dll` などが依存する（`VCRUNTIME140.dll`、`MSVCP140.dll`） | 再頒布可能パッケージを入れてもらう、または DLL を同梱する |
| DirectX 12 対応の GPU とドライバー | エンジンの実行 | 動作要件として明記する |
| Windows のバージョン | Windows 10 以降（64 ビット） | 動作要件 |
| Graphics Tools | デバッグ レイヤー（Debug のみ） | Release では不要 |
| エンジンの DLL | `Engine.dll`、`EngineApi.dll`（`Game.dll`） | 同じフォルダーに置く |

この章のゴールは次のとおりです。

- Release 構成で、全プロジェクトをビルドできる。
- 配布用のフォルダー構成を決めて、スクリプトで作れる。
- コマンドラインから、ビルド一式を実行できる。
- ビューモデルの単体テストを書ける。

## Release ビルド

Debug と Release では、次のような違いがあります。

| 項目 | Debug | Release |
| --- | --- | --- |
| 最適化 | なし（`/Od`） | あり（`/O2`） |
| デバッグ情報 | 完全 | 別ファイル（`.pdb`）に出せる |
| ランタイム ライブラリ（C++） | `/MDd`（`MSVCP140D.dll`） | `/MD`（`MSVCP140.dll`） |
| アサート、`_DEBUG` | 有効 | 無効 |
| DX12 デバッグ レイヤー | 有効 | 無効 |
| 速度 | 遅い（数倍〜数十倍） | 速い |
| 配布 | しない（Debug ランタイムが他の PC にない） | する |

Release の設定を確認します。

| プロジェクト | 確認する項目 |
| --- | --- |
| C++（Engine、EngineApi、Game、Player） | 構成「Release」、プラットフォーム「x64」。C/C++ → 最適化 = 速度を優先 (`/O2`)。コード生成 → ランタイム ライブラリ = マルチスレッド DLL (`/MD`) |
| C#（Editor） | 構成「Release」。`Optimize` = true（Release の既定） |
| 全体 | `Directory.Build.props` の出力先が、`bin\x64\Release\` になる（第 1 章） |

Release でも `pdb` を作る設定にしておくと、クラッシュ ダンプ（第 44 章）が読めます。

| 設定 | 値 |
| --- | --- |
| C/C++ → 全般 → デバッグ情報の形式 | プログラム データベース (`/Zi`) |
| リンカー → デバッグ → デバッグ情報の生成 | はい (`/DEBUG`) |
| リンカー → 最適化 | 参照されていないデータを除外 (`/OPT:REF`)、COMDAT 折りたたみ (`/OPT:ICF`) |

Debug では動いて、Release では動かない、ということがあります。よくある原因です。

| 症状 | 原因 |
| --- | --- |
| Release だけクラッシュする | 初期化されていない変数（Debug では 0 で初期化される場合がある）、未定義動作が最適化で表面化 |
| Release だけ、値がずれる | 浮動小数の計算順序（`/fp:fast`）、構造体のパディング |
| Release のデバッグで、変数が見えない | 最適化で消えた。その場合は `/Od` を一時的に付ける |
| `assert` に頼ったエラー検査が消えた | Release では `assert` が無効。必須の検査は `if` で書く |
| C# の `Debug.Assert`、`#if DEBUG` の中の処理 | Release では無効 |

Release でも、定期的に動かす習慣をつけます。最後にまとめて試すと、原因の特定が大変です。

## 配布のフォルダー構成

配布するフォルダーは、次の構成にします。

```text
MiniEngine-1.0.0\
  Editor.exe                  ← エディタ（C#）
  Editor.dll
  Editor.deps.json
  Editor.runtimeconfig.json   ← 必要な .NET の版
  Prism.dll  Prism.Wpf.dll  DryIoc.dll  ...   ← NuGet のライブラリ
  Engine.dll                  ← エンジン本体（C++）
  EngineApi.dll               ← C# から見える入口
  Game.dll                    ← 既定のゲーム（置き換えられる）
  Player.exe                  ← ゲームの実行側
  Assets\                     ← サンプルのアセット
  README.txt                  ← 動作要件、起動方法
  symbols\                    ← .pdb（ダンプの調査用。配布しなくてもよい）
```

`bin\x64\Release\` に全部が出力される（第 1 章）ので、そこから不要なものを除いてコピーするだけです。PowerShell のスクリプトにします。

```powershell title="tools/package.ps1"
# 配布用のフォルダーを作る：  .\tools\package.ps1 -Version 1.0.0
param(
    [Parameter(Mandatory = $true)] [string] $Version
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$bin = Join-Path $root 'bin\x64\Release'
$out = Join-Path $root "dist\MiniEngine-$Version"

if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Path $out | Out-Null

# 実行に必要なファイルだけをコピーする（.pdb、.lib、.exp、.ilk は除く）
Get-ChildItem $bin -File | Where-Object {
    $_.Extension -notin '.pdb', '.lib', '.exp', '.ilk', '.iobj', '.ipdb'
} | Copy-Item -Destination $out

# サンプルのアセット
Copy-Item (Join-Path $root 'Assets') (Join-Path $out 'Assets') -Recurse

# シンボルは別フォルダー（配布しない場合は、社内に保管する）
$sym = Join-Path $root "dist\symbols-$Version"
New-Item -ItemType Directory -Path $sym -Force | Out-Null
Get-ChildItem $bin -Filter *.pdb | Copy-Item -Destination $sym

Compress-Archive -Path "$out\*" -DestinationPath "$out.zip" -Force
Write-Host "作成しました: $out.zip"
```

`param(...)` は PowerShell スクリプトの引数の宣言で、`[Parameter(Mandatory = $true)]` は必須の指定です。`$ErrorActionPreference = 'Stop'` は、エラーが出たらそこで止める設定です（既定は続行します）。`$PSScriptRoot` は、このスクリプトのあるフォルダーです。`Where-Object { … }` で、条件に合うものだけを通します（`-notin` は「含まれない」）。`Compress-Archive` が、フォルダーを `.zip` にします。

## .NET ランタイムをどうするか

`Editor.exe` を動かすための .NET を、同梱するかどうかを選びます。

| 方式 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| フレームワーク依存 | 利用者の PC に、.NET 8 デスクトップ ランタイムを入れてもらう | 配布が小さい（数 MB）。ランタイムの更新が OS で行われる | 利用者が先にインストールする必要がある |
| 自己完結型 | .NET のランタイムも一緒にフォルダーに入れる | 何も入れなくても動く | 大きい（約 70〜150 MB）。ランタイムの更新はアプリごと |

```bash
# フレームワーク依存（既定）
dotnet publish Editor/Editor.csproj -c Release -r win-x64 --self-contained false -o publish/

# 自己完結型
dotnet publish Editor/Editor.csproj -c Release -r win-x64 --self-contained true -o publish/
```

`dotnet publish` は、配布用に必要なファイルを 1 つのフォルダーに集めます。`-r win-x64` は Windows の 64 ビット向けというランタイム識別子で、`--self-contained` はランタイムを同梱するかどうかです。

いくつか、使わないほうがよいオプションがあります。`PublishTrimmed`（使われないコードの削除）は、リフレクションを多用する WPF では、サポートされていません。`PublishSingleFile`（単一ファイル化）は、WPF とネイティブ DLL の組み合わせだと、ネイティブ DLL が別ファイルのままになるか、実行時に展開されて、扱いが複雑になります。最初は使いません。`PublishReadyToRun` は、事前に機械語へ変換して起動を速くするもので、起動時間が気になるときに使えます。

この教材の構成（C# の EXE と C++ の DLL）では、`dotnet publish` で C# の分を集めて、C++ の DLL は `bin\x64\Release\` から手でコピーするのが、最も分かりやすい形です。

### VC++ ランタイム

`Engine.dll` などは `/MD` でビルドしているので、`VCRUNTIME140.dll` と `MSVCP140.dll` に依存します。

| 方法 | 内容 |
| --- | --- |
| 再頒布可能パッケージを案内する | 「Microsoft Visual C++ 再頒布可能パッケージ（x64）を入れてください」と README に書く。多くの PC で、すでに入っている |
| アプリ ローカルで同梱 | `VCRUNTIME140.dll`、`MSVCP140.dll`、`VCRUNTIME140_1.dll` を `Editor.exe` の隣にコピーする。ライセンス上、再頒布が許可されている |
| 静的にリンクする（`/MT`） | ランタイムを DLL に埋め込む。ただし `Engine.dll` と `Game.dll` の間で CRT が別々になり、メモリの受け渡しが危険になる。この教材の構成では避ける |

## コマンドラインでビルドする

Visual Studio を開かなくてもビルドできるようにします。自動化（CI）の第一歩です。

```bash
# すべてをビルド（Release / x64）
msbuild MiniEngine.sln /p:Configuration=Release /p:Platform=x64 /m /nologo /v:minimal
```

`msbuild` は Visual Studio のビルド エンジンで、「Developer Command Prompt for VS」から呼べます。`/m` は並列ビルド、`/v:minimal` は出力を最小限にする指定です。

GitHub Actions を使うと、push のたびに、クラウドの Windows でビルドとテストを走らせられます。実行環境 `windows-latest` には、Visual Studio が入っています。

```yaml title=".github/workflows/build.yml"
name: build

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: .NET をセットアップ
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 8.0.x

      - name: MSBuild をセットアップ
        uses: microsoft/setup-msbuild@v2

      - name: NuGet パッケージを復元
        run: dotnet restore MiniEngine.sln

      - name: ビルド（Release / x64）
        run: msbuild MiniEngine.sln /p:Configuration=Release /p:Platform=x64 /m /nologo /v:minimal

      - name: テスト
        run: dotnet test Editor.Tests/Editor.Tests.csproj -c Release --no-build

      - name: 配布フォルダーを作る
        run: pwsh tools/package.ps1 -Version ci-${{ github.run_number }}

      - uses: actions/upload-artifact@v4
        with:
          name: MiniEngine
          path: dist/*.zip
```

`actions/checkout` はリポジトリを取得する公式の部品、`upload-artifact` は成果物（zip）を実行結果から取り出せるようにする部品です。CI の価値は、「自分の PC では動く」問題を、他の環境でもビルドが通ることで検出できる点にあります。

## ビューモデルのテスト

MVVM の利点の 1 つが、ビューモデルを画面なしでテストできることです。ビューモデルは `IEngineService` などのインターフェースだけに依存しているので、偽物（フェイク）に差し替えて、動作を確かめられます。

テスト プロジェクトは、次の手順で作ります。

1. ソリューションに「xUnit テスト プロジェクト」を追加する。名前は `Editor.Tests`、.NET 8。
2. `Editor` へのプロジェクト参照を追加する。
3. テスト プロジェクトの `TargetFramework` を `net8.0-windows` にする（WPF の型を使うため）。

```xml
<PropertyGroup>
  <TargetFramework>net8.0-windows</TargetFramework>
  <UseWPF>true</UseWPF>
</PropertyGroup>
```

フェイクは、何もしない偽物で、呼ばれた内容だけを覚えます。

```csharp
using Editor.Services;

namespace Editor.Tests;

// 何もしない、ログ サービスの偽物（呼ばれた内容だけを覚える）
public sealed class FakeLogService : ILogService
{
    public List<string> Messages { get; } = new();
    public System.Collections.ObjectModel.ObservableCollection<LogEntry> Entries { get; } = new();

    public void Info(string message) => Messages.Add("INFO " + message);
    public void Warning(string message) => Messages.Add("WARN " + message);
    public void Error(string message) => Messages.Add("ERROR " + message);
}
```

履歴（Undo/Redo）は、画面にもエンジンにも依存しない、純粋なロジックです。テストに最適です。

```csharp
using Editor.Services.Undo;
using Xunit;

namespace Editor.Tests;

public class HistoryServiceTests
{
    // テスト用の単純なコマンド：値を足し、Undo で引く
    private sealed class AddCommand : IUndoCommand
    {
        private readonly int[] _box;
        private readonly int _amount;
        public AddCommand(int[] box, int amount) { _box = box; _amount = amount; }
        public string Name => "足す";
        public void Do() => _box[0] += _amount;
        public void Undo() => _box[0] -= _amount;
        public bool TryMerge(IUndoCommand next) => false;
    }

    [Fact]
    public void Execute_then_Undo_restores_value()
    {
        var history = new HistoryService();
        var box = new[] { 10 };

        history.Execute(new AddCommand(box, 5));
        Assert.Equal(15, box[0]);

        history.Undo();
        Assert.Equal(10, box[0]);
        Assert.False(history.CanUndo);
        Assert.True(history.CanRedo);
    }

    [Fact]
    public void Redo_reapplies_command()
    {
        var history = new HistoryService();
        var box = new[] { 0 };
        history.Execute(new AddCommand(box, 3));
        history.Undo();

        history.Redo();

        Assert.Equal(3, box[0]);
    }

    [Fact]
    public void New_edit_after_undo_discards_redo_history()
    {
        var history = new HistoryService();
        var box = new[] { 0 };
        history.Execute(new AddCommand(box, 1));
        history.Undo();

        history.Execute(new AddCommand(box, 2));

        Assert.False(history.CanRedo);
    }

    [Fact]
    public void Transaction_groups_commands_into_one_undo()
    {
        var history = new HistoryService();
        var box = new[] { 0 };

        history.BeginTransaction("まとめて足す");
        history.Execute(new AddCommand(box, 1));
        history.Execute(new AddCommand(box, 2));
        history.CommitTransaction();
        Assert.Equal(3, box[0]);

        history.Undo();               // 1 回の Undo で、両方戻る

        Assert.Equal(0, box[0]);
        Assert.False(history.CanUndo);
    }

    [Fact]
    public void IsDirty_is_false_after_save_and_true_after_edit()
    {
        var history = new HistoryService();
        var box = new[] { 0 };
        history.Execute(new AddCommand(box, 1));

        history.MarkSaved();
        Assert.False(history.IsDirty);

        history.Execute(new AddCommand(box, 1));
        Assert.True(history.IsDirty);
    }
}
```

xUnit は、.NET の定番のテスト フレームワークです（ほかに NUnit、MSTest があります）。`[Fact]` は「このメソッドは 1 つのテスト」という属性、`Assert.Equal(期待, 実際)` は値が等しいことの確認で、違えばテスト失敗になります。テスト名は、`Execute_then_Undo_restores_value` のように、何をしたら何になるかを名前にします。中身は、準備、実行、確認の 3 段階（Arrange / Act / Assert）で、空行で区切ると読みやすくなります。実行は、Visual Studio の「テスト → テスト エクスプローラー」か、コマンドラインの `dotnet test` です。

シーンの読み書きも、純粋なロジックなので、同じようにテストできます。

```csharp
public class SceneDocumentTests
{
    [Fact]
    public void Destroy_removes_children_too()
    {
        var doc = new SceneDocument();
        var parent = doc.Create("parent");
        doc.Create("child", parent);

        doc.Destroy(parent);

        Assert.Empty(doc.AllObjects);
    }

    [Fact]
    public void Reparent_to_own_descendant_throws()
    {
        var doc = new SceneDocument();
        var parent = doc.Create("parent");
        var child = doc.Create("child", parent);

        Assert.Throws<InvalidOperationException>(() => doc.Reparent(parent, child));
    }

    [Fact]
    public void Serialize_then_apply_restores_the_scene()
    {
        var doc = new SceneDocument();
        var a = doc.Create("A");
        a.Position = new System.Numerics.Vector3(1, 2, 3);
        doc.Create("B", a);

        string json = SceneSerializer.Serialize(doc);
        var restored = new SceneDocument();
        SceneSerializer.Apply(SceneSerializer.Parse(json), restored);

        Assert.Equal(2, restored.AllObjects.Count());
        Assert.Equal(new System.Numerics.Vector3(1, 2, 3), restored.Find(a.Id)!.Position);
    }

    [Fact]
    public void Parse_rejects_duplicate_ids()
    {
        string json = """{"version":1,"objects":[{"id":1,"name":"a","children":[]},{"id":1,"name":"b","children":[]}]}""";
        Assert.Throws<SceneFileException>(() => SceneSerializer.Parse(json));
    }
}
```

`Assert.Throws<T>(() => …)` は、指定の例外が投げられることを確かめます。`""" … """` は、C# 11 の生文字列リテラルで、エスケープなしで複数行の文字列を書けます。JSON のように引用符が多い文字列に便利です。

テストしやすい所と、しにくい所があります。

| テストしやすい（純粋なロジック） | テストしにくい（外部に依存） |
| --- | --- |
| 履歴、スナップショット、コマンド | `HwndHost`、ウィンドウ、描画 |
| `SceneDocument`、シリアライザー | ネイティブのエンジン（DLL）の呼び出し |
| ビューモデル（サービスをフェイクにして） | `FileSystemWatcher`、実際のファイル |
| 数学（`MakeRay`、`ClosestOnAxis`） | GPU の動作、見た目 |

見た目や GPU は、スクリーンショット比較や目視で確かめます。ロジックをできるだけ純粋な部分に寄せることが、テストしやすい設計の鍵です。C++ 側（`Scene`、`Picking`）にも、同じ考えで、GoogleTest や Catch2 などの単体テストを書けます。

## バージョンと互換性

配布すると、古いエディタと新しいエンジンの組み合わせが生まれます。版を確認する場所を決めておきます。

| 確認すること | 方法 |
| --- | --- |
| C# と C++ の API の版 | 起動時に `me_get_api_version()` と、C# 側が期待する版を比べる。違えば、エラーを出して起動を中止する |
| ゲーム DLL の版 | 第 41 章の `kGameApiVersion` |
| シーン ファイルの版 | 第 39 章の `version` |
| アプリの版 | `Editor.csproj` の `<Version>1.0.0</Version>`。メニューの「バージョン情報」とクラッシュ レポートに出す |

```csharp
// App.OnInitialized の最初
const int ExpectedApiVersion = 1;
int actual = NativeMethods.me_get_api_version();
if (actual != ExpectedApiVersion)
{
    MessageBox.Show($"EngineApi の版が合いません（エディタ {ExpectedApiVersion}、DLL {actual}）。\n配布物が壊れています。",
                    "MiniEngine Editor", MessageBoxButton.OK, MessageBoxImage.Error);
    Shutdown(1);
    return;
}
```

## 動かして確かめる

| 操作 | 期待する結果 |
| --- | --- |
| `msbuild … Release x64` | エラーなしで、`bin\x64\Release\` に一式ができる |
| `tools\package.ps1 -Version 1.0.0` | `dist\MiniEngine-1.0.0.zip` ができる。`.pdb` や `.lib` が入っていない |
| 別の PC（または Windows Sandbox）に zip を展開して `Editor.exe` | 起動する（必要なランタイムが入っていれば） |
| `dotnet test` | すべて合格 |
| DLL を 1 つ消して起動 | 「見つからない」旨のエラー（`DllNotFoundException` ではなく、分かりやすいメッセージ） |

Windows Sandbox（Windows の機能の 1 つ）を使うと、まっさらな Windows で、配布物が動くかを手軽に確かめられます。

??? failure "別の PC で `VCRUNTIME140D.dll が見つかりません`"
    Debug 版を配布しています。`D` 付きのランタイムは、開発機にしかありません。Release 版を配布します。

??? failure "別の PC で `.NET ランタイムが見つかりません` と出る"
    フレームワーク依存で配布して、利用者が .NET 8 デスクトップ ランタイムを入れていません。README に要件を書くか、自己完結型にします。

??? failure "Release だけ、アプリが起動しない"
    C# 側の `Debug.Assert` に必要な処理を書いていたか、C++ の未初期化変数です。Release でも、日常的に動かします。

??? failure "CI で `windows-latest` のビルドが、ローカルと違う結果になる"
    Visual Studio の版や Windows SDK の版の差です。`.vcxproj` の `PlatformToolset` と `WindowsTargetPlatformVersion` を明示して、そろえます。

??? failure "テスト プロジェクトが `Editor` を参照できない"
    `Editor` が `net8.0-windows` なのに、テスト側が `net8.0` です。`TargetFramework` をそろえます。

## この章のまとめ

- 配布は、「何がないと動かないか」を洗い出す作業。Release 版を配布し、ランタイムの扱い（.NET、VC++）を決める。
- 配布物の作成はスクリプト化して、ビルドはコマンドラインや CI でも通るようにする。
- ビューモデルはインターフェースに依存しているので、フェイクで単体テストできる。
- 起動時に、各 API の版を確認する。

最後の章では、作ったものの全体を振り返って、次に進むための道筋を示します。

[第 47 章 まとめと、これから](47-next-steps.md) へ進みます。
