---
title: 第 1 章 全体像とソリューションの設計
tags:
  - C#連携
---

# 第 1 章 全体像とソリューションの設計

この章ではコードを 1 行も書きません。ソリューションの形を決めて、空のプロジェクトを 5 つ作るだけです。ここで役割をきちんと分けておくと、後の章で効いてきます。

!!! info "このページを読む前に"
    - [第 0 章 はじめる前に：道具と言葉の準備](00-prepare.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## この章の考え方

家を建てる前に間取りを決めるように、まずプロジェクトの分け方を決めます。ゲーム エンジンのような大きなプログラムは、1 つのプロジェクトに全部を入れると、すぐに手に負えなくなります。「描画はどこまでが仕事か」「エディタはエンジンの中身をどこまで知ってよいか」があいまいになるからです。

そこで、役割ごとにプロジェクトを分けて、誰が誰を使ってよいか（依存の向き）を先に決めます。決まりを守っていれば、エディタを作り直してもエンジンは壊れませんし、ゲームのコードを差し替えてもエディタは壊れません。この決まりを Visual Studio の設定（プロジェクトの依存関係と出力先）として形にするのが、この章の作業です。

途中で用語が分からなくなったら、[第 0 章](00-prepare.md)の言葉の表に戻ってください。

## この章のゴール

- 5 つのプロジェクト（Engine、EngineApi、Game、Player、Editor）の役割と依存の向きを説明できる。
- Visual Studio で、5 つの空のプロジェクトを持つソリューション `MiniEngine` を作れる。
- すべての成果物（`.dll`、`.exe`）が同じフォルダーに出力されるように設定できる。

## なぜエディタだけを C# にするのか

エディタの仕事は、ボタン、ツリー、リスト、入力欄、ダイアログといった画面をたくさん作ることです。この種の仕事は、C++ よりも C# と WPF のほうが、ずっと少ないコードで書けます。

| 仕事 | C++ で書くと | C# + WPF で書くと |
| --- | --- | --- |
| 画面の部品（ツリー、リスト、スプリッター、ダイアログ） | 自前で描くか、ImGui などのライブラリを使う | 標準の部品がそろっている |
| データと画面の同期 | 自分で更新処理を書く | データバインディングが自動で同期する |
| ファイルを開く・保存のダイアログ | Win32 API（COM）を直接 | 数行 |
| JSON の読み書き | ライブラリを導入 | 標準ライブラリ（`System.Text.Json`） |
| 文字列、コレクション、非同期処理 | 標準ライブラリ（`std::`）でできるが、冗長 | 言語の機能として組み込まれている |

逆に、エンジンの中核（描画、物理、シーンの更新）は C++ のままにします。毎フレーム何百万回も動く処理には、メモリの配置や速さを細かく制御できる C++ が向いているからです。

!!! note "エディタを C++ で作る選択肢もある"
    ImGui のようなライブラリで、エディタを C++ で作ることもできます（[Dear ImGui](../libs/imgui/index.md)）。C# + WPF を選ぶ利点は、画面作りの生産性、データバインディング、Prism による大きなアプリの設計の型です。欠点は、言語の境界（C++ と C# の間の連携）を自分で設計しなければならないことです。この教材では、その連携を学ぶことも目的の 1 つにしています。

## 5 つのプロジェクト

| プロジェクト | 言語 | 種類 | 役割 |
| --- | --- | --- | --- |
| Engine | C++ | DLL | エンジンの中核。DirectX 12 の描画、シーン、アセット、入力。どのプロジェクトにも依存しない |
| EngineApi | C++ | DLL | Engine を C の関数として公開する入口。C# の Editor はこれだけを見る |
| Game | C++ | DLL | ゲームのコード（コンポーネント、ゲーム ルール）。エンジンの機能で書く。実行中に差し替えできる（第 42 章） |
| Player | C++ | EXE | ゲームを動かす実行側。ウィンドウを作り Engine と Game を読み込んで、ループを回す |
| Editor | C# | EXE | WPF + Prism のエディタ。EngineApi.dll を P/Invoke で呼ぶ |

### 依存の向き

```text
Editor ──▶ EngineApi ──▶ Engine ◀── Game
                           ▲
                        Player ──（実行時に読み込む）──▶ Game
```

| 規則 | 理由 |
| --- | --- |
| Engine は他のプロジェクトを知らない | 中核がエディタやゲームの都合で変わらないようにする。再利用できる |
| Editor は EngineApi の C 関数だけを呼ぶ | C++ の型（クラス、`std::string`、例外）は言語の境界を越えられない（第 25 章） |
| Game は Engine の公開ヘッダーだけを使う | ゲームのコードが Engine の内部に依存しない。DLL として差し替えられる |
| Player と Editor は、互いに依存しない | どちらも Engine を使う別々の「入口」。同じゲームを別の形で動かす |

### 3 つの境界

この構成には、言語やビルドの「境界」が 3 つあります。境界ごとに、気をつけることが違います。

| 境界 | どこ | 越えるもの | 気をつけること |
| --- | --- | --- | --- |
| ① C# ↔ C++ | Editor ↔ EngineApi | C の関数、構造体、ポインター、文字列 | 型の大きさ、文字列の文字コード、メモリの所有者、呼び出し規約（第 25〜27 章） |
| ② 実行側 ↔ ゲーム | Player/Editor ↔ Game | C++ のクラス（仮想関数） | 同じコンパイラ、同じランタイムで作ること。再読み込みの扱い（第 41〜42 章） |
| ③ Engine ↔ その利用者 | Engine ↔ Game/Player/EngineApi | C++ の公開ヘッダー | DLL の境界を越える、C++ の型（`std::string` など）の扱い（第 2 章） |

## 手順 1：空のソリューションを作る

1. Visual Studio 2026 を起動し、「新しいプロジェクトの作成」を選ぶ。
2. 検索欄に「空のソリューション」と入れて、出てきた「空のソリューション」を選び、「次へ」。
3. プロジェクト名（ソリューション名）を `MiniEngine` にする。場所は短いパス（`C:\Dev\` など）にする。「ソリューションとプロジェクトを同じディレクトリに配置する」にチェックを入れて、作成する。

| 新しく出てきたもの | 説明 |
| --- | --- |
| ソリューション（`.sln`） | 複数のプロジェクトをまとめる入れ物（[Solution](../vs/terms/solution.md)） |
| プロジェクト（`.vcxproj`、`.csproj`） | 1 つの成果物（DLL や EXE）を作る単位（[Project](../vs/terms/project.md)） |

## 手順 2：C++ のプロジェクトを 4 つ追加する

ソリューション エクスプローラーで、ソリューションを右クリックし、「追加 → 新しいプロジェクト」を選びます。

| 名前 | テンプレート（検索語） | 備考 |
| --- | --- | --- |
| `Engine` | ダイナミック リンク ライブラリ (DLL)（C++） | DLL を作る |
| `EngineApi` | ダイナミック リンク ライブラリ (DLL)（C++） | DLL を作る |
| `Game` | ダイナミック リンク ライブラリ (DLL)（C++） | DLL を作る |
| `Player` | 空のプロジェクト（C++） | EXE を作る。あとで `main` を足す |

各プロジェクトの場所はソリューション フォルダーの直下（`MiniEngine\Engine\` など）になるようにします。

!!! note "テンプレートが作る余計なファイル"
    DLL のテンプレートは `dllmain.cpp`、`framework.h`、`pch.h`、`pch.cpp` を作ります。この教材では使わないので、削除して構いません（プリコンパイル済みヘッダーも使いません）。右クリックして、「プロジェクトから除外」ではなく「削除」を選びます。

## 手順 3：C# の WPF プロジェクトを追加する

1. もう一度、「追加 → 新しいプロジェクト」を開く。
2. 言語を C# に絞って、「WPF アプリケーション」を選ぶ（.NET Framework 版ではなく、`.NET` のほうです）。
3. 名前を `Editor` にする。フレームワークは `.NET 8.0 (長期的なサポート)` を選んで、作成する。

| 新しく出てきたもの | 説明 |
| --- | --- |
| WPF（Windows Presentation Foundation） | Windows のデスクトップ アプリの UI フレームワーク。画面を XAML（XML ベースの言語）で、動きを C# で書く（第 6 章） |
| .NET | C# の実行環境と標準ライブラリ。この教材は .NET 8 |
| .NET Framework | 古い Windows 専用の .NET。こちらは選ばない（新しい機能が使えない） |
| LTS（長期的なサポート） | 長い期間、更新が提供される版。.NET 8 のサポートは 2026 年まで |

## 手順 4：構成を x64 だけにそろえる

このエンジンは、64 ビット（x64）だけを対象にします。C++ の DLL と C# の EXE のビット数が違うと、DLL を読み込めないからです（第 29 章）。

1. メニューの「ビルド → 構成マネージャー」を開く。
2. 「アクティブ ソリューション プラットフォーム」のドロップダウンから「新規作成」を選んで、`x64` を作る（「設定のコピー元」は `Win32` か `Any CPU`）。
3. 一覧のすべてのプロジェクトで、「プラットフォーム」が `x64` になっていることを確認する。`Editor` も `x64` にする（`Any CPU` のままにしない）。
4. `x86`（`Win32`）と `Any CPU` のプラットフォームは、削除して構わない。

| 新しく出てきたもの | 説明 |
| --- | --- |
| 構成（Configuration） | Debug / Release のように、ビルドの設定の組（[Configuration](../vs/terms/configuration.md)） |
| プラットフォーム（Platform） | x64 / Win32 / Any CPU。対象の CPU（[Platform](../vs/terms/platform.md)） |
| `Any CPU` | C# が 32 ビットでも 64 ビットでも動く設定。x64 だけのネイティブ DLL と組むと、32 ビットで起動して失敗することがあるので使わない |

## 手順 5：全プロジェクトの出力先をそろえる

C++ の DLL と C# の EXE が別々のフォルダーに出力されると、実行のたびに DLL をコピーしなければなりません。そこで、全部を同じフォルダーに出力します。ソリューション フォルダーの直下に `Directory.Build.props` というファイルを作ってください（エクスプローラーで作ってから、「ソリューション項目」に追加しても構いません）。

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

保存したら、ソリューションを開き直します（`Directory.Build.props` は、プロジェクトを開くときに読まれるからです）。

| 新しく出てきたもの | 説明 |
| --- | --- |
| MSBuild | Visual Studio のビルド エンジン。`.vcxproj` や `.csproj` は MSBuild の設定ファイル（XML） |
| `Directory.Build.props` | そのフォルダー以下の全プロジェクトに共通で適用される、MSBuild の設定。自動で読み込まれる |
| `$(MSBuildThisFileDirectory)` | この `.props` ファイルがある、フォルダーのパス（最後に `\` が付く） |
| `$(Platform)`、`$(Configuration)` | 今のプラットフォーム（`x64`）と構成（`Debug`）に置き換わる変数 |
| `$(MSBuildProjectName)`、`$(MSBuildProjectExtension)` | 今ビルドしているプロジェクトの名前、拡張子（`.vcxproj`、`.csproj`） |
| `OutDir`・`IntDir`（C++） | 出力先、中間ファイルのフォルダー |
| `OutputPath`（C#） | C# の出力先 |
| `AppendTargetFrameworkToOutputPath` | `true` だと出力先の末尾に `net8.0-windows\` が付く。`false` で付けない |
| `PlatformTarget` | C# の対象 CPU。`x64` で 64 ビット専用 |

## 手順 6：ビルドの順序と依存を設定する

Editor は実行時に `EngineApi.dll` を必要とします。C# から C++ の DLL へはプロジェクト参照が使えないので、「ビルドの順序」だけを設定します。

1. ソリューションを右クリック → 「プロジェクトの依存関係」を開く。
2. プロジェクトに `Editor` を選んで、`EngineApi` にチェックを入れる（これで、Editor の前に EngineApi がビルドされる）。
3. 同様に `EngineApi` → `Engine`、`Game` → `Engine`、`Player` → `Engine` にチェックを入れる。

| プロジェクト | 依存する先 |
| --- | --- |
| Engine | なし |
| EngineApi | Engine |
| Game | Engine |
| Player | Engine |
| Editor | EngineApi |

C++ のプロジェクトどうし（`EngineApi → Engine` など）は、「参照の追加」を使うと、インポート ライブラリ（`Engine.lib`）のリンクまで自動になります（第 2 章）。

## 手順 7：ビルドして確かめる

1. 構成を Debug、プラットフォームを x64 にして、「ビルド → ソリューションのビルド」を実行する。
2. エクスプローラーで `MiniEngine\bin\x64\Debug\` を開く。

次のファイルが並んでいれば成功です。

```text
bin\x64\Debug\
  Engine.dll  Engine.lib  Engine.pdb
  EngineApi.dll  EngineApi.lib  EngineApi.pdb
  Game.dll  Game.lib  Game.pdb
  Editor.exe  Editor.dll  Editor.pdb  Editor.deps.json  Editor.runtimeconfig.json
```

`Player.exe` は、まだ `main` が無いのでリンクに失敗します。この時点では問題ありません（第 4 章で作ります）。`Player` のエラーが邪魔なときは、一時的にビルドの対象から外します（構成マネージャーで「ビルド」のチェックを外す）。

| 新しく出てきたファイル | 説明 |
| --- | --- |
| `.dll` | 実行時に読み込まれるライブラリ |
| `.lib`（DLL と同名） | インポート ライブラリ。DLL を使う側がリンクするための目録（第 2 章） |
| `.pdb` | デバッグ情報（変数名、行番号） |
| `Editor.dll` | C# のコードをコンパイルした本体。C# の `.exe` は起動用の小さな入口で、中身は `.dll` |
| `Editor.runtimeconfig.json` | 実行に必要な .NET の版の情報 |
| `Editor.deps.json` | 依存するライブラリの一覧 |

## よくあるミス

??? failure "`Editor` の出力が `bin\\x64\\Debug\\net8.0-windows\\` に出る"
    `AppendTargetFrameworkToOutputPath` が `false` になっていないか、`Directory.Build.props` が読まれていません。ソリューションを開き直してください。

??? failure "`Directory.Build.props` が効かない"
    ファイル名の大文字・小文字と、置き場所を確認します。`Directory.Build.props` は、プロジェクトと同じフォルダーか、それより上のフォルダーに置かないと読まれません。

??? failure "構成マネージャーで `Editor` が `Any CPU` のまま"
    `PlatformTarget` が x64 でも、構成のプラットフォームが `Any CPU` のままだと、出力先が `bin\Any CPU\Debug\` になります。ソリューションのプラットフォームを x64 にそろえてください。

??? failure "C++ のプロジェクトが `x64` を持っていない"
    DLL のテンプレートは、`Win32` と `x64` の両方を作ります。構成マネージャーで `x64` を足したのにプロジェクト側に無いときは、「新しいプロジェクト プラットフォームを作成」にチェックが入っていたかを確認してください。

## この章で作ったもの

```text
MiniEngine\
  MiniEngine.sln
  Directory.Build.props      ← 出力先を共通化
  Engine\      EngineApi\      Game\      Player\      Editor\
  bin\x64\Debug\             ← すべての成果物がここに集まる
```

## 次の章へ

次の章（[第 2 章 Engine プロジェクト：DLL の骨組み](02-engine-skeleton.md)）では、`Engine` プロジェクトに最初のコードを書きます。DLL から関数やクラスを公開する方法と、公開ヘッダーの作り方を学びます。
