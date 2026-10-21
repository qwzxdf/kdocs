---
title: 第 1 章 全体像とソリューションの設計
tags:
  - C#連携
---

# 第 1 章 全体像とソリューションの設計

最初の章ではコードを 1 行も書かず <strong>ソリューションの形</strong>を決めて、空のプロジェクトを 5 つ作ります。ここで役割をきちんと分けておくことが、後の章で効いてきます。

## この章の考え方

最初にコードを書かず、<strong>家の間取りを決める</strong>ように、プロジェクトの分け方を決めます。ゲーム エンジンのような大きなプログラムは、1 つのプロジェクトに全部を入れると、すぐに手に負えなくなります。「描画はどこまでが仕事か」「エディタはエンジンの中身をどこまで知ってよいか」が、あいまいになるからです。

そこで、<strong>役割ごとにプロジェクトを分け、誰が誰を使ってよいか（依存の向き）を先に決めます</strong>。決まりを守る限り、エディタを作り直してもエンジンは壊れず、ゲームのコードを差し替えてもエディタは壊れません。この決まりを、Visual Studio の設定（プロジェクトの依存関係、出力先）で、実際の形にするのが、この章の作業です。

もし途中で用語が分からなくなったら、[第 0 章](00-prepare.md)の言葉の表に戻ってください。

## この章のゴール

- 5 つのプロジェクト（Engine、EngineApi、Game、Player、Editor）の役割と依存の向きを説明できる。
- Visual Studio で、5 つの空のプロジェクトを持つソリューション `MiniEngine` を作れる。
- すべての成果物（`.dll`、`.exe`）が <strong>同じフォルダー</strong>に出力されるように設定できる。

## なぜエディタだけを C# にするのか

エディタの仕事は <strong>ボタン、ツリー、リスト、入力欄、ダイアログ</strong>といった画面をたくさん作ることです。この種の仕事は C++ より C# と WPF のほうが、はるかに少ないコードで書けます。

| 仕事 | C++ で書くと | C# + WPF で書くと |
| --- | --- | --- |
| 画面の部品（ツリー、リスト、スプリッター、ダイアログ） | 自前で描くか ImGui などのライブラリ | 標準の部品が、そろっている |
| データと画面の同期 | 自分で更新処理を書く | データバインディングが、自動で同期する |
| ファイルを開く・保存のダイアログ | Win32 API（COM）を直接 | 数行 |
| JSON の読み書き | ライブラリを導入 | 標準ライブラリ（`System.Text.Json`） |
| 文字列、コレクション、非同期処理 | 標準ライブラリ（`std::`）で、できるが冗長 | 言語機能として、組み込み済み |

逆に、<strong>エンジンの中核（描画、物理、シーンの更新）は C++ のまま</strong>にします。毎フレーム、数百万回動く処理はメモリの配置や速さを細かく制御できる C++ が、向いているからです。

!!! note "エディタを C++ で作る選択肢もある"
    ImGui のようなライブラリで、エディタを C++ で作ることもできます（[Dear ImGui](../libs/imgui/index.md)）。C# + WPF を選ぶ利点は <strong>画面作りの生産性</strong>、<strong>データバインディング</strong>、<strong>Prism による大きなアプリの設計の型</strong>です。欠点は <strong>言語の境界</strong>（C++ と C# の間の連携）を自分で、設計する必要がある点でこの教材はその連携を学ぶことが、目的の 1 つです。

## 5 つのプロジェクト

| プロジェクト | 言語 | 種類 | 役割 |
| --- | --- | --- | --- |
| <strong>Engine</strong> | C++ | DLL | エンジンの中核。DirectX 12 の描画、シーン、アセット、入力。<strong>どのプロジェクトにも依存しない</strong> |
| <strong>EngineApi</strong> | C++ | DLL | Engine を、<strong>C の関数</strong>として公開する入口。C# の Editor はこれだけを見る |
| <strong>Game</strong> | C++ | DLL | ゲームのコード（コンポーネント、ゲーム ルール）。エンジンの機能で書く。<strong>実行中に差し替え</strong>できる（第 28 章） |
| <strong>Player</strong> | C++ | EXE | ゲームを動かす実行側。ウィンドウを作り Engine と Game を読み込んで、ループを回す |
| <strong>Editor</strong> | C# | EXE | WPF + Prism のエディタ。EngineApi.dll を P/Invoke で呼ぶ |

### 依存の向き

```text
Editor ──▶ EngineApi ──▶ Engine ◀── Game
                           ▲
                        Player ──（実行時に読み込む）──▶ Game
```

| 規則 | 理由 |
| --- | --- |
| <strong>Engine は他のプロジェクトを知らない</strong> | 中核が、エディタやゲームの都合で変わらないようにする。再利用できる |
| <strong>Editor は EngineApi の C 関数だけを呼ぶ</strong> | C++ の型（クラス、`std::string`、例外）は言語の境界を越えられない（第 11 章） |
| <strong>Game は Engine の公開ヘッダーだけを使う</strong> | ゲームのコードが、Engine の内部に依存しない。DLL として差し替えられる |
| <strong>Player と Editor は、互いに依存しない</strong> | どちらも Engine を使う別々の「入口」。同じゲームを別の形で動かす |

### 3 つの境界

この構成には <strong>言語やビルドの「境界」</strong>が 3 つあります。それぞれで気をつける物が違います。

| 境界 | どこ | 越えるもの | 気をつけること |
| --- | --- | --- | --- |
| ① C# ↔ C++ | Editor ↔ EngineApi | C の関数、構造体、ポインター、文字列 | 型の大きさ文字列の文字コード、メモリの所有者、呼び出し規約（第 11〜13 章） |
| ② 実行側 ↔ ゲーム | Player/Editor ↔ Game | C++ のクラス（仮想関数） | 同じコンパイラ、同じランタイムで作ること。再読み込みの扱い（第 27〜28 章） |
| ③ Engine ↔ その利用者 | Engine ↔ Game/Player/EngineApi | C++ の公開ヘッダー | DLL の境界を越える、C++ の型（`std::string` など）の扱い（第 2 章） |

## 手順 1：空のソリューションを作る

1. Visual Studio 2022 を起動し、<strong>「新しいプロジェクトの作成」</strong>を選ぶ。
2. 検索欄に「空のソリューション」と入れ <strong>「空のソリューション」</strong>を選んで、「次へ」。
3. プロジェクト名（ソリューション名）を <strong>`MiniEngine`</strong> にする。場所は短いパス（`C:\Dev\` など）を選び <strong>「ソリューションとプロジェクトを同じディレクトリに配置する」にチェック</strong>を入れて、作成する。

| 新しく出てきたもの | 説明 |
| --- | --- |
| ソリューション（`.sln`） | 複数のプロジェクトをまとめる入れ物（[Solution](../vs/terms/solution.md)） |
| プロジェクト（`.vcxproj`、`.csproj`） | 1 つの成果物（DLL や EXE）を作る単位（[Project](../vs/terms/project.md)） |

## 手順 2：C++ のプロジェクトを 4 つ追加する

ソリューション エクスプローラーで、ソリューションを右クリックし、<strong>「追加 → 新しいプロジェクト」</strong>を選びます。

| 名前 | テンプレート（検索語） | 備考 |
| --- | --- | --- |
| `Engine` | <strong>ダイナミック リンク ライブラリ (DLL)</strong>（C++） | DLL を作る |
| `EngineApi` | <strong>ダイナミック リンク ライブラリ (DLL)</strong>（C++） | DLL を作る |
| `Game` | <strong>ダイナミック リンク ライブラリ (DLL)</strong>（C++） | DLL を作る |
| `Player` | <strong>空のプロジェクト</strong>（C++） | EXE を作る。あとで `main` を足す |

各プロジェクトの場所はソリューション フォルダーの直下（`MiniEngine\Engine\` など）になるようにします。

!!! note "テンプレートが作る余計なファイル"
    DLL のテンプレートは `dllmain.cpp`、`framework.h`、`pch.h`、`pch.cpp` を作ります。この教材では <strong>使わないので削除</strong>して構いません（プリコンパイル済みヘッダーは、使いません）。プロジェクトを右クリック → 「プロジェクトからの除外」ではなく、「削除」を選びます。

## 手順 3：C# の WPF プロジェクトを追加する

1. もう一度、「追加 → 新しいプロジェクト」を開く。
2. 言語を C# に絞り <strong>「WPF アプリケーション」</strong>（<strong>.NET Framework ではなく、`.NET` のほう</strong>）を選ぶ。
3. 名前を <strong>`Editor`</strong> にして、フレームワークは <strong>`.NET 8.0 (長期的なサポート)`</strong> を選んで、作成する。

| 新しく出てきたもの | 説明 |
| --- | --- |
| WPF（Windows Presentation Foundation） | Windows の、デスクトップ アプリの UI フレームワーク。画面を XAML（XML ベースの言語）で書き動きを C# で書く（第 6 章） |
| .NET | C# の実行環境と標準ライブラリ。この教材は <strong>.NET 8</strong> |
| .NET Framework | 古い Windows 専用の.NET。<strong>こちらは選ばない</strong>（新しい機能が、使えない） |
| LTS（長期的なサポート） | 長く、更新が提供される版。.NET 8 は 2026 年まで |

## 手順 4：構成を x64 だけにそろえる

DirectX 12 のエンジンは <strong>64 ビット（x64）だけ</strong>を対象にします。C++ の DLL と C# の EXE のビット数が違うと読み込めません（第 15 章）。

1. メニューの <strong>「ビルド → 構成マネージャー」</strong>を開く。
2. <strong>「アクティブ ソリューション プラットフォーム」</strong>のドロップダウンから、<strong>「新規作成」</strong>を選び `x64` を作る（「設定のコピー元」は、`Win32` か `Any CPU`）。
3. 一覧の各プロジェクトの「プラットフォーム」が、すべて `x64` になっていることを確認する。<strong>`Editor` も `x64`</strong>（`Any CPU` のままにしない）。
4. `x86`（`Win32`）と `Any CPU` のプラットフォームは、削除して構わない。

| 新しく出てきたもの | 説明 |
| --- | --- |
| 構成（Configuration） | Debug / Release のように、ビルドの設定の組（[Configuration](../vs/terms/configuration.md)） |
| プラットフォーム（Platform） | x64 / Win32 / Any CPU。対象の CPU（[Platform](../vs/terms/platform.md)） |
| `Any CPU` | C# が 32 ビットでも 64 ビットでも動く設定。<strong>ネイティブの DLL（x64 のみ）と組むと 32 ビットで起動して、失敗することがある</strong>ので使わない |

## 手順 5：全プロジェクトの出力先をそろえる

C++ の DLL と C# の EXE が、<strong>別々のフォルダー</strong>に出力されると、実行のたびに DLL をコピーする必要が出ます。<strong>全部を同じフォルダー</strong>に出力します。ソリューション フォルダーの直下に `Directory.Build.props` というファイルを作ります（Visual Studio の「ソリューション フォルダーに、ファイルを追加」ではなくエクスプローラーで作って、「ソリューション項目」に追加しても構いません）。

```xml
<Project>
  <PropertyGroup>
    <!-- 成果物は、すべて bin\x64\Debug\（または Release）に集める。中間ファイルは、プロジェクトごと。 -->
    <OutRoot>$(MSBuildThisFileDirectory)bin\$(Platform)\$(Configuration)\</OutRoot>
    <IntRoot>$(MSBuildThisFileDirectory)obj\$(MSBuildProjectName)\$(Platform)\$(Configuration)\</IntRoot>
  </PropertyGroup>

  <!-- C++ プロジェクト（.vcxproj） -->
  <PropertyGroup Condition="'$(MSBuildProjectExtension)' == '.vcxproj'">
    <OutDir>$(OutRoot)</OutDir>
    <IntDir>$(IntRoot)</IntDir>
  </PropertyGroup>

  <!-- C# プロジェクト（.csproj） -->
  <PropertyGroup Condition="'$(MSBuildProjectExtension)' == '.csproj'">
    <OutputPath>$(OutRoot)</OutputPath>
    <AppendTargetFrameworkToOutputPath>false</AppendTargetFrameworkToOutputPath>
    <AppendRuntimeIdentifierToOutputPath>false</AppendRuntimeIdentifierToOutputPath>
    <PlatformTarget>x64</PlatformTarget>
  </PropertyGroup>
</Project>
```

保存してソリューションを開き直します（`Directory.Build.props` は、プロジェクトを開くときに読まれます）。

| 新しく出てきたもの | 説明 |
| --- | --- |
| MSBuild | Visual Studio のビルド エンジン。`.vcxproj` や `.csproj` は MSBuild の設定ファイル（XML） |
| `Directory.Build.props` | <strong>そのフォルダー以下の全プロジェクトに共通で適用される、MSBuild の設定</strong>。自動で読み込まれる |
| `$(MSBuildThisFileDirectory)` | この `.props` ファイルがある、フォルダーのパス（最後に `\` が付く） |
| `$(Platform)`、`$(Configuration)` | 今のプラットフォーム（`x64`）と構成（`Debug`）に置き換わる変数 |
| `$(MSBuildProjectName)`、`$(MSBuildProjectExtension)` | 今ビルドしているプロジェクトの名前、拡張子（`.vcxproj`、`.csproj`） |
| `OutDir`・`IntDir`（C++） | 出力先、中間ファイルのフォルダー |
| `OutputPath`（C#） | C# の出力先 |
| `AppendTargetFrameworkToOutputPath` | `true` だと出力先の末尾に `net8.0-windows\` が付く。`false` で付けない |
| `PlatformTarget` | C# の対象 CPU。`x64` で 64 ビット専用 |

## 手順 6：ビルドの順序と依存を設定する

Editor は実行時に `EngineApi.dll` を必要とします。C# から C++ の DLL へは <strong>プロジェクト参照</strong>が、使えないので「ビルドの順序」だけを設定します。

1. ソリューションを右クリック → <strong>「プロジェクトの依存関係」</strong>を開く。
2. プロジェクトを `Editor` にして、<strong>`EngineApi` にチェック</strong>を入れる（これで、Editor の前に EngineApi が、ビルドされる）。
3. 同様に、`EngineApi` → `Engine`、`Game` → `Engine`、`Player` → `Engine` にチェックを入れる。

| プロジェクト | 依存する先 |
| --- | --- |
| Engine | なし |
| EngineApi | Engine |
| Game | Engine |
| Player | Engine |
| Editor | EngineApi |

C++ のプロジェクトどうし（`EngineApi → Engine` など）は、後の章で「参照の追加」でインポート ライブラリ（`Engine.lib`）のリンクも自動化します（第 2 章）。

## 手順 7：ビルドして確かめる

1. 構成を <strong>Debug</strong>、プラットフォームを <strong>x64</strong> にして、<strong>「ビルド → ソリューションのビルド」</strong>。
2. エクスプローラーで `MiniEngine\bin\x64\Debug\` を開く。

次のファイルが並んでいれば成功です。

```text
bin\x64\Debug\
  Engine.dll  Engine.lib  Engine.pdb
  EngineApi.dll  EngineApi.lib  EngineApi.pdb
  Game.dll  Game.lib  Game.pdb
  Editor.exe  Editor.dll  Editor.pdb  Editor.deps.json  Editor.runtimeconfig.json
```

`Player.exe` はまだ `main` が無いのでリンクに失敗します。<strong>この時点では問題ありません</strong>（第 4 章で作ります）。`Player` のビルドだけエラーが出るなら一時的にビルドの対象から、外します（構成マネージャーで「ビルド」のチェックを外す）。

| 新しく出てきたファイル | 説明 |
| --- | --- |
| `.dll` | 実行時に読み込まれる、ライブラリ |
| `.lib`（DLL と同名） | <strong>インポート ライブラリ</strong>。DLL を使う側がリンクするための目録（第 2 章） |
| `.pdb` | デバッグ情報（変数名、行番号） |
| `Editor.dll` | C# のコードが、コンパイルされた本体。C# の `.exe` は起動用の小さな入口で中身は `.dll` |
| `Editor.runtimeconfig.json` | 実行に必要な.NET の版の情報 |
| `Editor.deps.json` | 依存するライブラリの一覧 |

## よくあるミス

??? failure "`Editor` の出力が、`bin\\x64\\Debug\\net8.0-windows\\` に出る"
    `AppendTargetFrameworkToOutputPath` が `false` になっていないまたは、`Directory.Build.props` が読まれていない（ソリューションを開き直す）。

??? failure "`Directory.Build.props` が効かない"
    ファイル名の大文字・小文字、置き場所（ソリューションと同じフォルダー、またはその上）を確認する。プロジェクトが `Directory.Build.props` より上の階層にあると、読まれない。

??? failure "構成マネージャーで `Editor` が `Any CPU` のまま"
    `PlatformTarget` が x64 でも構成のプラットフォームが `Any CPU` だと出力先が `bin\\Any CPU\\Debug\\` になる。ソリューションのプラットフォームを x64 にそろえる。

??? failure "C++ のプロジェクトが `x64` を持っていない"
    DLL のテンプレートは `Win32` と `x64` を作る。「新規作成」で `x64` を足したのに、プロジェクト側に無い場合は「新しいプロジェクト プラットフォームを作成」にチェックが入っているかを確認する。

## この章で作ったもの

```text
MiniEngine\
  MiniEngine.sln
  Directory.Build.props      ← 出力先を共通化
  Engine\      EngineApi\      Game\      Player\      Editor\
  bin\x64\Debug\             ← すべての成果物が、ここに集まる
```

## 次の章へ

次の章（[第 2 章 Engine プロジェクト：DLL の骨組み](02-engine-skeleton.md)）では、`Engine` プロジェクトに最初のコードを書きます。<strong>DLL から関数やクラスを公開する方法</strong>と公開ヘッダーの作り方を学びます。
