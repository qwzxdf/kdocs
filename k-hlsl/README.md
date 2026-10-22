# K-HLSL

Visual Studio 2022 / 2026 用の HLSL 拡張です。Shader Model 6.9 までの構文と組み込み関数に対応します。

既存の HLSL 拡張は、独自のパーサーでエラーを判定するため、`ResourceDescriptorHeap` のような新しい構文を「宣言されていない」と誤検出します。K-HLSL は、エラーの判定を本物の DXC（`dxc.exe`）に任せます。DXC が通すコードは、エラーになりません。

## 機能

- 構文の色付け（TextMate 文法）。SM 6.9 までのキーワード、型、組み込み関数、セマンティクス、属性
- 補完。組み込み関数、リソースのメソッド（`tex.Sample` など）、構造体のメンバー、スウィズル、セマンティクス（`:` の後）、属性（`[` の後）、`#` ディレクティブ、`#include` のファイル名、`dx::`
- ホバー（日本語の説明、シグネチャ、必要な Shader Model）
- シグネチャ ヘルプ（組み込み関数、メソッド、自分で書いた関数）
- 定義へ移動（`#include` のファイルも）と、アウトライン
- DXC による診断（保存時と、入力が止まった 0.7 秒後）

対応している新しい機能: `ResourceDescriptorHeap` / `SamplerDescriptorHeap`（SM 6.6）、パック 8 ビット演算、64 ビット アトミック、`WaveSize`、クアッド / ウェーブの全関数、メッシュ / 増幅シェーダー、DXR 1.1 の `RayQuery`、ワーク グラフ（SM 6.8）、`SampleCmpBias` / `SampleCmpGrad`、SM 6.9 の `dx::HitObject` と `dx::MaybeReorderThread`（Shader Execution Reordering）。

## インストール

`bin\K-HLSL.vsix` をダブルクリックします。インストールのあと、古い HLSL 拡張（HLSL Tools for Visual Studio など）は無効にしてください。同じファイルに 2 つの拡張が診断を出すと、古いほうの誤検出が残ります。

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

## ビルド

Visual Studio の「Visual Studio extension development」ワークロードと Python が必要です。

```powershell
./build.ps1
```

`data/` の表（`d_intrinsics.py`、`d_lang.py`）から、言語サーバーのデータ（`hlsl.json`）と文法（`KHlsl.json`）を作ります。関数やセマンティクスを足すときは、この表を直して `build.ps1` を実行します。

`tests/lsp_smoke.py` は、ビルドした言語サーバーを起動して、ホバー・補完・シグネチャ ヘルプ・アウトライン・診断を一通り呼びます（先に `build.ps1` を実行してください）。

## 構成

| フォルダー | 内容 |
| --- | --- |
| `data/` | 組み込み関数・型・セマンティクスなどの表と、生成スクリプト |
| `src/KHlsl.Server/` | 言語サーバー（C#、.NET Framework 4.7.2、stdio の LSP） |
| `src/KHlsl.Vsix/` | VSIX。コンテンツ タイプ、言語クライアント、TextMate 文法の登録 |
| `tests/` | スモーク テスト |
