# K-HLSL

Visual Studio 2022 / 2026 用の HLSL 拡張です。Shader Model 6.9 までの構文と組み込み関数に対応します。

既存の HLSL 拡張は、独自のパーサーでエラーを判定するため、`ResourceDescriptorHeap` のような新しい構文を「宣言されていない」と誤検出します。K-HLSL は、エラーの判定を本物の DXC（`dxc.exe`）に任せます。DXC が通すコードは、エラーになりません。

## 機能

- 色付け。VS の C++ と同じ分類名（`cppFunction` `cppLocalVariable` `cppControlKeyword` など）を使うので、テーマの C++ の色が、そのまま HLSL に使われる。Viasfora を入れていると、C++ で効いている物も同じ色になる
    - 関数・メンバー関数・型・マクロ・名前空間・グローバル変数・ローカル変数・引数・メンバー変数・列挙子・ラベル・演算子・数値・文字列（引用符を含む）・`#` ディレクティブ。変数は、スコープを見て、引数・ローカル・メンバー・グローバルに分ける
    - 制御キーワード（`if` `else` `for` `while` `do` `switch` `case` `default` `break` `continue` `return` `goto` `discard` `throw` `try` `catch`）は、`K-HLSL 制御キーワード`（既定は VS の C++ と同じ紫）。`#include` `#define` などは `K-HLSL プリプロセッサ キーワード`（同じく灰色）。C++ の分類名に頼らず、専用の表示項目に既定色を持たせている
    - 組み込み関数（`mul` `saturate` やリソースの `Sample` など）は `K-HLSL 組み込み関数`（橙）、独自の関数は C++ の関数の色（黄）
    - `#include` した先で定義された構造体は、このファイルから見えないので、「型 名前」の形から推測して、型・変数・メンバーに色を付ける
    - Tab や空白で字下げした `#if` `#  endif` も、ディレクティブとして色が付く
- Viasfora の色付け（C++ で実際に効いている物）
    - レインボー括弧: `( ) [ ] { }` を 1 つのスタックで数えて、深さ 4 の色（橙・ピンク・黄緑・紫）を循環させる。対応しない閉じ括弧は背景が薄い赤になる。コメントと文字列の中は数えない
    - 可視性キーワード（`public` `private` `protected` `friend`）は DimGray
    - 文字列のエスケープ（`\n` `\x41` `\u0041` など）は Magenta、書式指定子（`%d` `%5` など）は MediumSlateBlue
    - 括弧・エスケープ・書式指定子の検出と、色・書式の定義は、Viasfora 自身の DLL と突き合わせて、一致を確認している。色付け全体は、VS の C++ エディターの分類と、トークンごとに突き合わせて、一致を確認している（[tests/compare](tests/compare/README.md)）
- 補完。組み込み関数、リソースのメソッド（`tex.Sample` など）、構造体のメンバー、スウィズル、セマンティクス（`:` の後）、属性（`[` の後）、`#` ディレクティブ、`#include` のファイル名、`dx::`
- ホバー（日本語の説明、シグネチャ、必要な Shader Model）
- シグネチャ ヘルプ（組み込み関数、メソッド、自分で書いた関数）
- 定義へ移動（`#include` のファイルも）と、アウトライン
- DXC による診断（保存時と、入力が止まった 0.7 秒後）

対応している新しい機能: `ResourceDescriptorHeap` / `SamplerDescriptorHeap`（SM 6.6）、パック 8 ビット演算、64 ビット アトミック、`WaveSize`、クアッド / ウェーブの全関数、メッシュ / 増幅シェーダー、DXR 1.1 の `RayQuery`、ワーク グラフ（SM 6.8）、`SampleCmpBias` / `SampleCmpGrad`、SM 6.9 の `dx::HitObject` と `dx::MaybeReorderThread`（Shader Execution Reordering）。

## インストール

`bin\K-HLSL.vsix` をダブルクリックして、Visual Studio を再起動します。

HLSL のファイル（`.hlsl` `.hlsli` `.fx` `.fxh` `.vsh` `.psh` `.gsh` `.hsh` `.dsh` `.csh` `.msh` `.ash` `.usf` `.ush` `.compute`）を開くと、K-HLSL は、そのバッファのコンテンツ タイプを `khlsl` に切り替えます。古い HLSL 拡張（HLSL Tools for Visual Studio など）は `hlsl` コンテンツ タイプに従来型の補完を登録していて、同じバッファでは LSP の補完が使えないからです。切り替えたファイルでは、古い拡張の補完・エラー表示・色付けは働かないので、同時に入れていても、古い拡張の誤検出は出ません。

## DXC

診断には `dxc.exe` が要ります。次の順で探します。

1. `.khlsl.json` の `"dxc"`
2. 環境変数 `KHLSL_DXC`
3. `PATH`
4. `VULKAN_SDK\Bin`
5. Windows SDK（`Windows Kits\10\bin\<最新>\x64`）

SM 6.9 を使うには、DXC 1.9 以降が必要です。見つかった DXC が新しいプロファイルを知らないときは、`lib_6_9` → `lib_6_8` → … と順に下げて試します。

## 設定（`.khlsl.json`）

ファイルのあるフォルダーから上へ向かって探します。どの項目も省略できます。

```json
{
  "dxc": "C:/tools/dxc/bin/x64/dxc.exe",
  "target": "lib_6_9",
  "entry": "main",
  "hlslVersion": "2021",
  "defines": ["USE_FOG=1"],
  "includeDirs": ["../shaders/common"],
  "args": ["-enable-16bit-types"],
  "diagnostics": true
}
```

`target` を決めないと、ライブラリ ターゲット（`lib_6_x`）で検証します。エントリ ポイントがなくても、構文と型のエラーを確認できます。

ファイルの先頭 30 行に、1 ファイルだけの指定を書けます。

```hlsl
// khlsl: -T ps_6_6 -E PSMain -D USE_FOG=1
```

## 色を変える

色は、テーマが C++ に付けている色です。ツール → オプション → 環境 → フォントおよび色 で、`C++ 関数` `C++ ローカル変数` `C++ 制御キーワード` などを変えると、C++ と HLSL の両方に効きます。

K-HLSL 専用の表示項目は、Viasfora の既定色を持つ物と、`K-HLSL 制御キーワード` `K-HLSL プリプロセッサ キーワード` `K-HLSL 組み込み関数` です。`K-HLSL 可視性キーワード` `K-HLSL 文字列のエスケープ` `K-HLSL 書式指定子` `K-HLSL Rainbow 括弧 1`〜`9` `K-HLSL Rainbow 括弧(対応なし)`。レインボー括弧は、Viasfora の既定と同じく 4 色（`Rainbow 括弧 1`〜`4`）を使います。Viasfora のレインボー行（インデントの縦線）と、キャレット位置の括弧ペアの強調は、作っていません。

`#if 0` や、定義されていないマクロの `#ifdef` で無効になる範囲を、薄く表示する機能（C++ の「非アクティブ コード」）は、まだありません。

## うまく動かないとき

ログは `%LOCALAPPDATA%\K-HLSL\` に出ます。

- `server.log`: 言語サーバーが VS から受け取った要求（`initialize`、`didOpen`、`hover`、`completion`）と、かかった時間。ファイルを開いても `didOpen` が出なければ、言語クライアントが起動していません。
- `vsix.log`: コンテンツ タイプの切り替え（`switched to khlsl`）。

補完が出ないときは、ツール → オプション → テキスト エディター → すべての言語 → 全般 の「自動メンバー一覧」がオンか確認してください。Ctrl+J（編集 → IntelliSense → メンバーの一覧）でも出せます。

## データの検証

組み込み関数・メソッド・型・定数・属性のデータ（`data/`）は、DXC に照らして確かめています。

- `data/ref/audit_dxc.py`: DXC の定義表（`utils/hct/gen_intrin_main.txt`。`data/ref/` に置いてある）と、関数・メソッドの名前を突き合わせる。DXC にあって K-HLSL に無い物と、その逆を出す
- `data/ref/verify_dxc.py`: メソッド・型・定数・属性の名前を、実際の `dxc.exe` に聞いて、実在するかを確かめる（関数は、DXC が引数の数の違いにも「未宣言」と返すので、この方法では確かめられない）
- `tests/dxr.hlsl`: DXR 1.0・1.1（RayQuery）・SM 6.9 の SER を、ひととおり使うシェーダー。DXC（`lib_6_9`）でコンパイルでき、`tests/lsp_hover_all.py tests/dxr.hlsl` で、使っている API すべてにホバーの説明が出ることを確かめる

DXC の表と突き合わせたことで、実在しない名前（`EvaluateAttributeAtCentroid`。正しくは `EvaluateAttributeCentroid`）と、不足していた物（`NonUniformResourceIndex` `CheckAccessFullyMapped` など）を直した。
Vulkan 専用の関数（`vk::` の一部）と、DXC の内部用の関数（`__builtin_LinAlg_*` など）は、載せていない。Shader Model 6.10 は DXC のプレビューなので、載せている物（`ClusterID` など）には、「6.10 以降」と表示する。

## ビルド

Visual Studio の「Visual Studio extension development」ワークロードと Python が必要です。

```powershell
./build.ps1
```

`data/` の表（`d_intrinsics.py`、`d_lang.py`）から、言語サーバーのデータ（`hlsl.json`）を作ります。関数やセマンティクスを足すときは、この表を直して `build.ps1` を実行します。

`tests/lsp_smoke.py` は、ビルドした言語サーバーを起動して、ホバー・補完・シグネチャ ヘルプ・アウトライン・診断を一通り呼びます（先に `build.ps1` を実行してください）。

実験用インスタンスで試すには、次のとおり展開します。

```powershell
& "$env:ProgramFiles\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe" src\KHlsl.Vsix\KHlsl.Vsix.csproj /p:Configuration=Release /p:DeployExtension=true
devenv /rootSuffix Exp tests\sample.hlsl
```

## 構成

| フォルダー | 内容 |
| --- | --- |
| `data/` | 組み込み関数・型・セマンティクスなどの表と、生成スクリプト |
| `src/KHlsl.Server/` | 言語サーバー（C#、.NET Framework 4.7.2、stdio の LSP） |
| `src/KHlsl.Vsix/` | VSIX。コンテンツ タイプ、言語クライアント、色付け（classifier）、切り替えを行うパッケージ |
| `tests/` | スモーク テスト |
