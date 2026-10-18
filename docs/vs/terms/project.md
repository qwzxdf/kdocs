---
title: プロジェクト（.vcxproj）
tags:
  - Visual Studio
---

# プロジェクト（.vcxproj）

プロジェクトは、<strong>1 つの成果物（`.exe`、`.dll`、`.lib`）を作るための、ファイルと設定のまとまり</strong>です。ファイルとしては `.vcxproj` で、中身は <strong>MSBuild という、ビルド ツールが読む XML</strong> です。プロパティ画面で変えている設定は、すべてこの XML に書き込まれています。

!!! tip "ポイント"
    - プロジェクトは「どのソースを、どんな設定でコンパイルして、何を作るか」を持つ
    - `.vcxproj` は XML。プロパティ画面の操作は、この XML を書き換えているだけ
    - 作るものは <strong>構成の種類（`ConfigurationType`）</strong>で決まる。アプリケーション（exe）、静的ライブラリ（lib）、動的ライブラリ（dll）など
    - ほかのプロジェクトの成果物を使うときは、<strong>プロジェクトの参照</strong>が簡単。ビルドの順番と、リンクを、まとめて済ませられる
    - ゲームでは、HLSL（シェーダー）も、プロジェクトの中でコンパイルできる

## このページを読む前に

- [ソリューション（.sln）](solution.md)

## プロジェクトの種類 {#type}

プロジェクトを作るとき、成果物の種類を選びます。あとから、プロパティの <strong>全般 → 構成の種類</strong>で変えられます。

| 構成の種類 | 作られるもの | 使いどころ |
| --- | --- | --- |
| アプリケーション（`.exe`） | 実行ファイル | ゲーム本体、ツール |
| スタティック ライブラリ（`.lib`） | 実行ファイルに、まるごと取り込まれる部品 | エンジンの共通部分 |
| ダイナミック ライブラリ（`.dll`） | 実行時に読み込まれる部品（`.lib` も一緒にできる） | プラグイン、ゲームと分けて更新したい部分 |
| ユーティリティ | コンパイルもリンクもしない | ビルド前後のスクリプトだけを実行したいとき |
| メイクファイル | 外部のビルド コマンドを呼ぶだけ | CMake や別のビルド システムを、Visual Studio から呼ぶとき |

静的ライブラリは、リンクするときに、使われた部分が、実行ファイルへコピーされます。ダイナミック ライブラリは、`.exe` と同じフォルダーに `.dll` を置く必要があります。DLL の置き忘れは、「`xxx.dll が見つからないため、コードの実行を続行できません`」になります（[よくあるエラー](../errors.md)）。

## .vcxproj の中身 {#file}

`.vcxproj` は、次のような構造をしています（読みやすいように、省略してあります）。

```xml
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">

  <!-- ① このプロジェクトが持つ、構成とプラットフォームの組 -->
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>

  <!-- ② プロジェクト全体の情報 -->
  <PropertyGroup Label="Globals">
    <ProjectGuid>{1A2B3C4D-0000-0000-0000-000000000002}</ProjectGuid>
    <RootNamespace>Game</RootNamespace>
    <WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />

  <!-- ③ 構成ごとの、基本の設定（何を作るか、どのツールセットか） -->
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v143</PlatformToolset>
    <CharacterSet>Unicode</CharacterSet>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />

  <!-- ④ コンパイラとリンカーの設定 -->
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <ClCompile>
      <WarningLevel>Level4</WarningLevel>
      <LanguageStandard>stdcpplatest</LanguageStandard>
      <AdditionalOptions>/utf-8 %(AdditionalOptions)</AdditionalOptions>
    </ClCompile>
    <Link>
      <SubSystem>Console</SubSystem>
    </Link>
  </ItemDefinitionGroup>

  <!-- ⑤ プロジェクトに含まれるファイル -->
  <ItemGroup>
    <ClCompile Include="main.cpp" />
    <ClCompile Include="game.cpp" />
  </ItemGroup>
  <ItemGroup>
    <ClInclude Include="game.h" />
  </ItemGroup>

  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
</Project>
```

| 部分 | 意味 |
| --- | --- |
| ① `ProjectConfiguration` | 構成とプラットフォームの組を、すべて宣言する |
| ② `Globals` | プロジェクトの ID、名前空間、使う Windows SDK のバージョン |
| ③ `ConfigurationType` | 成果物の種類（`Application`、`StaticLibrary`、`DynamicLibrary`、`Utility`、`Makefile`） |
| ③ `PlatformToolset` | 使うコンパイラ一式の版。`v143` が Visual Studio 2022、`v145` が 2026（[MSVC](msvc.md#toolset)） |
| ④ `ItemDefinitionGroup` | ファイルの種類ごとの、設定。`ClCompile` がコンパイラ、`Link` がリンカー |
| ⑤ `ClCompile` / `ClInclude` | プロジェクトに入っているファイル。`ClCompile` は、コンパイルされる |
| `Condition=...` | 「この構成のときだけ」という条件。構成ごとに値を変えるのに使う |

!!! note "プロパティ画面は、この XML の編集画面"
    C/C++ → 言語 → C++ 言語標準を変えると、`<LanguageStandard>` の値が変わります。分からない設定があったとき、`.vcxproj` をテキストで開くと、何がどこに書かれているかが分かります。直接書き換えることもできますが、Visual Studio を閉じてから行います。

## プロパティの引き継ぎ（継承） {#inherit}

プロパティ画面の入力欄に、`%(AdditionalOptions)` や `$(IncludePath)` のような記号が、よく出てきます。これは、<strong>もともとの値を、残したまま足す</strong>ための書き方です。

| 書き方 | 意味 |
| --- | --- |
| `$(名前)` | MSBuild のプロパティ（変数）の値を、ここに入れる。例：`$(Configuration)`、`$(SolutionDir)` |
| `%(名前)` | 項目（ファイル）の、メタデータの値。`%(AdditionalOptions)` は、すでに入っているオプション |

たとえば、追加のインクルード ディレクトリに、次のように書きます。

```text
$(SolutionDir)Engine\include;%(AdditionalIncludeDirectories)
```

最後に `%(AdditionalIncludeDirectories)` を付けないと、<strong>ほかのプロパティ シートや、既定値で決まっていたものが、全部消えます</strong>。プロパティ画面で、「継承」のチェックが付いていれば、同じことです。

使えるマクロの例です。

| マクロ | 値の例 |
| --- | --- |
| `$(SolutionDir)` | `C:\Users\you\MyGame\` |
| `$(ProjectDir)` | `C:\Users\you\MyGame\Game\` |
| `$(Configuration)` | `Debug` / `Release` |
| `$(Platform)` | `x64` |
| `$(OutDir)` | 成果物を出すフォルダー |
| `$(TargetName)` | 成果物の名前（拡張子なし） |

プロパティ画面で、値の欄を選んで、右の ▼ から「編集」を開くと、<strong>評価した後の値</strong>を、確認できます。

## プロジェクトの参照 {#reference}

ゲームがエンジンのライブラリを使うとき、プロジェクトを参照すると、手間が減ります。

1. ゲーム本体のプロジェクトを右クリック → <strong>追加 → 参照</strong>
2. `Engine` にチェックを入れる

これだけで、次の 2 つが起きます。

- ビルド順が決まる（`Engine` を先に作る）
- ゲーム側のリンクで、`Engine.lib` が自動的に使われる

`.vcxproj` の中では、次のように記録されます。

```xml
<ItemGroup>
  <ProjectReference Include="..\Engine\Engine.vcxproj">
    <Project>{1A2B3C4D-0000-0000-0000-000000000001}</Project>
  </ProjectReference>
</ItemGroup>
```

!!! warning "インクルード パスは足されない"
    プロジェクトの参照が自動でやるのは、「ビルド順」と「`.lib` のリンク」だけです。`#include "engine/renderer.h"` を通すには、<strong>`追加のインクルード ディレクトリ` に、`$(SolutionDir)Engine\include` を足す</strong>必要があります。

自分のプロジェクトではない `.lib`（外部ライブラリ）は、プロジェクトの参照にできません。リンカーの入力に、`.lib` の名前を書きます（[外部ライブラリの入れ方](../libraries.md)）。

## ファイルの種類（項目の種類） {#items}

ソリューション エクスプローラーでファイルを追加すると、`.vcxproj` の中に、その種類が記録されます。

| 項目の種類 | 拡張子の例 | 扱い |
| --- | --- | --- |
| `ClCompile` | `.cpp` | コンパイラに渡す |
| `ClInclude` | `.h`、`.hpp` | ビルドには関係ないが、一覧に出す |
| `None` | `.md`、`.json` | 何もしない |
| `FxCompile` | `.hlsl` | シェーダー コンパイラ（FXC）に渡す |
| `ResourceCompile` | `.rc` | リソース コンパイラに渡す |
| `Image`、`Manifest` | `.ico`、`.manifest` | リソースとして取り込む |

ソース ファイルの <strong>右クリック → プロパティ</strong>で、その 1 ファイルだけの設定を変えられます。「ビルドから除外」を「はい」にすると、そのファイルは、コンパイルされません。

### HLSL をプロジェクトで、コンパイルする

`.hlsl` ファイルをプロジェクトに追加すると、「HLSL コンパイラ」の項目になって、<strong>ビルドのたびに `.cso`（コンパイル済みのシェーダー）</strong>が作られます。ファイルごとに、プロパティを設定します。

| 設定 | 値の例 | 意味 |
| --- | --- | --- |
| シェーダーの種類 | 頂点シェーダー（/vs）、ピクセル シェーダー（/ps） | どのステージか |
| シェーダー モデル | 5.0（`/5_0`） | DirectX 11 は、シェーダー モデル 5.0 |
| エントリポイント名 | `VSMain` | シェーダーの関数名 |
| 出力ファイル | `$(OutDir)Shaders\%(Filename).cso` | 出力先 |

ビルドが成功すると、`.cso` を、実行時に読み込めます。HLSL の文法エラーは、C++ のエラーと同じように、「エラー一覧」に出ます。1 ファイルに複数のステージ（頂点とピクセル）があるときは、`.hlsl` を 2 回追加して、それぞれステージを分けて設定します。

## ビルドの前後に処理を足す {#events}

プロジェクトのプロパティ → <strong>ビルド イベント</strong>で、ビルドの前後に、コマンドを実行できます。

| イベント | 実行されるとき | 例 |
| --- | --- | --- |
| ビルド前イベント | コンパイルの前 | コードを自動生成するスクリプト |
| ビルド後イベント | リンクの後 | `Assets` フォルダーを、実行ファイルの横へコピー |

```text
xcopy /Y /D /E /I "$(ProjectDir)Assets" "$(OutDir)Assets"
```

`/Y` は上書きの確認をしない、`/D` は新しいものだけコピー、`/E` はサブフォルダーも、`/I` はコピー先をフォルダーとして扱う、という意味です。`$(OutDir)` に出力フォルダーを入れておくと、Debug と Release で、自動的に出し分けられます。

## 実行・デバッグの設定 {#debugging}

プロパティ → <strong>デバッグ</strong>に、F5 で実行するときの設定があります。<strong>この設定は、`.vcxproj.user` に保存されます</strong>（個人用のファイルなので、Git に入れません）。

| 設定 | 意味 |
| --- | --- |
| コマンド | 実行するファイル。通常は `$(TargetPath)` |
| コマンド引数 | `main` に渡す引数 |
| 作業ディレクトリ | 実行するときの、カレント フォルダー。相対パスでファイルを読むとき、重要 |
| 環境 | 実行時の環境変数 |

`assets/model.fbx` を相対パスで読むとき、<strong>作業ディレクトリ</strong>が違うと、見つかりません。Visual Studio から実行するときの既定は `$(ProjectDir)`（プロジェクトのフォルダー）です。`.exe` をダブルクリックで実行するときは、`.exe` のあるフォルダーです。この違いで、「Visual Studio からは動くのに、`.exe` を直接実行すると動かない」ことが起きます。

## 1 プロジェクトに、たくさんのファイルを入れるとき {#large}

| 工夫 | 内容 |
| --- | --- |
| プリコンパイル済みヘッダー（`pch.h`） | 標準ライブラリなど、変わらないヘッダーを、一度だけ解析して、使い回す。ビルドが速くなる（[ビルド](build.md#pch)） |
| `/MP` | 複数のコアで、ファイルを並列にコンパイルする |
| プロジェクトを分ける | 変更が少ない部分を、ライブラリにする。変更がない部分は、再コンパイルされない |
| ユニティ ビルド | 複数の `.cpp` を、1 つにまとめてコンパイルする。リンクは速いが、デバッグしにくい |

## よくあるミス

??? failure "ファイルを追加したのに、ビルドされない"
    ソリューション エクスプローラー上では見えているのに、<strong>項目の種類が `None`</strong> になっていると、コンパイルされません。右クリック → プロパティ → 全般 → <strong>項目の種類</strong>を「C/C++ コンパイラ」にします。

??? failure "`LNK2005`（すでに定義されています）が出る"
    同じ名前の関数やグローバル変数が、2 つの `.cpp` で定義されています。ヘッダーに、関数の本体を書いて、複数の `.cpp` から読み込んでいる場合は、`inline` を付けるか、`.cpp` に移します。

??? failure "Debug では動くが、Release だと実行できない（DLL・アセットが見つからない）"
    ビルド後イベントや、`.dll` のコピー先が、Debug だけ設定されていることがあります。プロパティを開くときは、構成を「すべての構成」にして設定します（[C++23 を使えるようにする設定](../settings.md#open)）。

??? failure "新しい `.cpp` の中だけ、設定が違う"
    その 1 ファイルのプロパティに、プロジェクト全体と違う設定が入っています（`ClCompile` の項目の中に、個別の値が書かれている）。ファイルのプロパティで、該当の欄を「継承」に戻します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プロジェクトは、1 つの成果物を作る単位。実体は MSBuild の XML
    - [x] プロパティ画面の設定は、`.vcxproj` に書き込まれている
    - [x] `%(…)` を残して書く。消すと、継承された値が失われる
    - [x] 自分のライブラリは、プロジェクトの参照。外部ライブラリは、`.lib` をリンカーに書く
    - [x] HLSL は、プロジェクトに追加すれば、ビルドのたびに `.cso` が作られる
    - [x] 作業ディレクトリが違うと、相対パスで読むファイルが見つからなくなる

## 関連ページ

- [ソリューション（.sln）](solution.md)
- [構成（Configuration）](configuration.md)
- [ビルド](build.md)
- [C++23 を使えるようにする設定](../settings.md)
- [外部ライブラリの入れ方](../libraries.md)
- [Visual Studio の目次](../index.md)
