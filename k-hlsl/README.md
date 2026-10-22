# K-HLSL

Visual Studio 2022 / 2026 用の HLSL 拡張です。Shader Model 6.9 までの構文と組み込み関数に対応します。

既存の HLSL 拡張は、独自のパーサーでエラーを判定するため、`ResourceDescriptorHeap` のような新しい構文を「宣言されていない」と誤検出します。K-HLSL は、エラーの判定を本物の DXC（`dxc.exe`）に任せます。DXC が通すコードは、エラーになりません。

## 機能

- 構文の色付け。関数・数値・セマンティクス・属性・定数・マクロは K-HLSL の色、キーワードと型はテーマの色
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

ツール → オプション → 環境 → フォントおよび色 の「表示項目」に、`K-HLSL 関数` `K-HLSL 数値` `K-HLSL セマンティクス` `K-HLSL 属性` `K-HLSL 定数・列挙値` `K-HLSL マクロ` があります。キーワード・型・コメント・文字列は、テーマの色（`キーワード` `クラス名` など）に従います。

## うまく動かないとき

ログは `%LOCALAPPDATA%\K-HLSL\` に出ます。

- `server.log`: 言語サーバーが VS から受け取った要求（`initialize`、`didOpen`、`hover`、`completion`）と、かかった時間。ファイルを開いても `didOpen` が出なければ、言語クライアントが起動していません。
- `vsix.log`: コンテンツ タイプの切り替え（`switched to khlsl`）。

補完が出ないときは、ツール → オプション → テキスト エディター → すべての言語 → 全般 の「自動メンバー一覧」がオンか確認してください。Ctrl+J（編集 → IntelliSense → メンバーの一覧）でも出せます。

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
