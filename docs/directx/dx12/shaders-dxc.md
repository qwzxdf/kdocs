---
title: Shaders and DXC
tags:
  - DirectX
---

# Shaders and DXC

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 の、シェーダーは、HLSL で、書き、<strong>DXC</strong>（DirectX Shader Compiler）で、<strong>DXIL</strong>（バイトコード）に、コンパイルします。DXC は、シェーダー モデル 6.0 以上（SM 6.x）に、対応した、新しい、コンパイラーで、<strong>ウェーブ命令、64 ビット整数、ビンドレス（SM 6.6）、レイトレーシング（DXR）、メッシュ シェーダー</strong>は、DXC が、必要です。古い、`fxc`（SM 5.1 まで）でも、基本的な、シェーダーは、動きます。

!!! tip "ポイント"
    - HLSL を、<strong>`dxc`</strong> で、DXIL に、コンパイルして、`.cso`（または `.dxil`）に、保存し、実行時に、読み込む。
    - ターゲット: 頂点 `vs_6_0`、ピクセル `ps_6_0`、計算 `cs_6_0`、DXR `lib_6_3`、メッシュ `ms_6_5`。
    - コンパイルは、<strong>ビルド時</strong>が、標準。実行時に、コンパイルするなら、`IDxcCompiler3` の API。
    - GPU が、対応する、SM を、`CheckFeatureSupport` で、確認する。
    - シェーダーを、PSO に、渡す。バイトコードを、`D3D12_SHADER_BYTECODE` に、入れる（[PSO](pso.md)）。

## シェーダー モデル

シェーダー モデル（SM）は、HLSL の、機能の、バージョンです。

| SM | コンパイラー | 主な、追加 |
| --- | --- | --- |
| 5.0・5.1 | `fxc` | 従来の世代。5.1 は、リソース配列、レジスタ スペース（D3D12 向け） |
| 6.0 | `dxc` | ウェーブ命令（`WaveActiveSum` など） |
| 6.2 | `dxc` | 16 ビットの、浮動小数点、整数 |
| 6.3 | `dxc` | DXR（レイトレーシング） |
| 6.5 | `dxc` | メッシュ・増幅シェーダー、DXR 1.1（`RayQuery`） |
| 6.6 | `dxc` | ビンドレス（`ResourceDescriptorHeap`）、64 ビット アトミック |
| 6.7・6.8 | `dxc` | 拡張（ウェーブ行列、ワーク グラフ など） |

SM 6 の機能は、<strong>GPU・ドライバーが、対応して、いないと、使えません</strong>。`CheckFeatureSupport(D3D12_FEATURE_SHADER_MODEL)` で、確認します（[Device and Factory](factory-device.md)）。

## dxc を、使う（ビルド時）

```text
dxc -T vs_6_0 -E VSMain -Fo triangle_vs.cso triangle.hlsl
dxc -T ps_6_0 -E PSMain -Fo triangle_ps.cso triangle.hlsl
dxc -T cs_6_0 -E MainCS -Fo blur_cs.cso blur.hlsl
```

| オプション | 内容 |
| --- | --- |
| `-T` | ターゲット（`vs_6_0`、`ps_6_0`、`cs_6_0`、`lib_6_3`、`ms_6_5`） |
| `-E` | 入口の関数名 |
| `-Fo` | 出力ファイル（DXIL） |
| `-Zi` | デバッグ情報（PIX、RenderDoc で、ソースが見える） |
| `-Od` | 最適化なし（デバッグ） |
| `-O3` | 最大の、最適化（既定） |
| `-I dir` | `#include` の、検索パス |
| `-D NAME=value` | `#define` |
| `-Qembed_debug` | デバッグ情報を、バイトコードに、埋め込む |
| `-enable-16bit-types` | 16 ビット型を、有効に（SM 6.2 以上） |

`dxc.exe` は、Windows SDK（`bin\<version>\x64\dxc.exe`）に、含まれています。Visual Studio の、HLSL コンパイラの、項目は、`fxc` を、使うので、SM 6 の、シェーダーは、<strong>カスタム ビルド ステップ</strong>で、`dxc` を、呼びます。

### Visual Studio の、カスタム ビルド

HLSL ファイルの、プロパティで、「項目の種類」を「カスタム ビルド ツール」に、して、次を、設定します。

| 設定 | 値 |
| --- | --- |
| コマンド ライン | `dxc -T ps_6_0 -E PSMain -Fo "$(OutDir)%(Filename)_ps.cso" "%(FullPath)"` |
| 出力 | `$(OutDir)%(Filename)_ps.cso` |

CMake の、プロジェクトでは、`add_custom_command` で、`dxc` を、呼びます。

## 実行時に、コンパイルする

DXC は、ライブラリ（`dxcompiler.dll`）としても、使えます。ホット リロードに、便利です。

```cpp
#include <dxcapi.h>
#pragma comment(lib, "dxcompiler.lib")

ComPtr<IDxcBlob> CompileShader(const wchar_t* path, const wchar_t* entry, const wchar_t* target) {
  ComPtr<IDxcUtils> utils;
  ComPtr<IDxcCompiler3> compiler;
  DxcCreateInstance(CLSID_DxcUtils, IID_PPV_ARGS(&utils));
  DxcCreateInstance(CLSID_DxcCompiler, IID_PPV_ARGS(&compiler));

  ComPtr<IDxcBlobEncoding> source;
  utils->LoadFile(path, nullptr, &source);                       // HLSL を読む
  DxcBuffer buffer = {source->GetBufferPointer(), source->GetBufferSize(), DXC_CP_ACP};

  const wchar_t* args[] = {L"-E", entry, L"-T", target, L"-Zi", L"-Qembed_debug"};
  ComPtr<IDxcResult> result;
  compiler->Compile(&buffer, args, ARRAYSIZE(args), nullptr, IID_PPV_ARGS(&result));

  ComPtr<IDxcBlobUtf8> errors;
  result->GetOutput(DXC_OUT_ERRORS, IID_PPV_ARGS(&errors), nullptr);
  if (errors && errors->GetStringLength() > 0) OutputDebugStringA(errors->GetStringPointer());   // エラー・警告

  ComPtr<IDxcBlob> bytecode;
  result->GetOutput(DXC_OUT_OBJECT, IID_PPV_ARGS(&bytecode), nullptr);
  return bytecode;                                               // DXIL（D3D12_SHADER_BYTECODE に、渡す）
}
```

`IDxcCompiler3::Compile` に、引数の、文字列を、配列で、渡します。<strong>エラー文字列</strong>（`DXC_OUT_ERRORS`）は、必ず、表示します。

## バイトコードを、PSO に、渡す

```cpp
// .cso を読む、または、上の CompileShader の結果を使う。
D3D12_SHADER_BYTECODE vs = {vs_blob->GetBufferPointer(), vs_blob->GetBufferSize()};
pso_desc.VS = vs;
```

D3D12 では、シェーダーは、<strong>単体の、オブジェクトでは、なく</strong>、バイトコードの、ポインターと、大きさを、PSO の、記述子に、入れます（[PSO](pso.md)）。

## HLSL の、書き方の、違い（D3D12 向け）

D3D12 の、シェーダーは、リソースを、<strong>レジスタ スペース</strong>つきで、宣言できます。

```hlsl
// ルート シグネチャの、パラメータと、対応する宣言。space0 は、省略できる。
Texture2D<float4> g_albedo : register(t0, space0);
SamplerState g_sampler : register(s0, space0);
cbuffer PerObject : register(b0, space0) {
  row_major float4x4 world_view_projection;
};
```

`register(t0, space0)` の、`space` は、リソースの、論理的な、グループです。ビンドレスや、配列で、使い分けます（[Root Signature](root-signature.md)）。

### ルート シグネチャを、HLSL に、埋め込む

```hlsl
// シェーダーの中に、ルート シグネチャを、書ける（dxc が、DXIL に、埋め込む）。
#define RS "RootFlags(ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT), " \
           "CBV(b0), " \
           "DescriptorTable(SRV(t0, numDescriptors = 1)), " \
           "StaticSampler(s0, filter = FILTER_MIN_MAG_MIP_LINEAR)"

[RootSignature(RS)]
VSOutput VSMain(VSInput input) { ... }
```

C++ で、ルート シグネチャを、組み立てる代わりに、HLSL に、文字列で、書く方法です。短く書けますが、C++ 側の、動的な、制御が、できません（[Root Signature](root-signature.md)）。

## ウェーブ命令（SM 6.0）

GPU は、32 または 64 スレッドを、1 組（ウェーブ、ワープ）で、実行します。SM 6.0 は、<strong>ウェーブの中の、スレッド同士</strong>で、値を、やり取りする、命令を、追加しました。

```hlsl
// ウェーブ全体で、合計を求める（groupshared と、バリアなしで、速い）。
float sum = WaveActiveSum(value);
uint lane = WaveGetLaneIndex();                                  // ウェーブ内での、自分の番号
bool any = WaveActiveAnyTrue(condition);
```

ヒストグラム、リダクション（合計・最大）、ライトの、カリングで、`groupshared` より、速く、書けます。

## デバッグ情報

```text
dxc -T ps_6_0 -E PSMain -Zi -Qembed_debug -Fo shader.cso shader.hlsl     # PIX で、ソースを見る
```

`-Zi` と `-Qembed_debug` を、付けると、PIX や RenderDoc が、HLSL の、ソース行を、表示できます。製品では、デバッグ情報を、別ファイル（`-Fd`）に、分けて、リリースの、サイズを、減らします。

## よくあるミス

??? failure "SM 6 の機能（ウェーブ命令、DXR）を、使ったら、PSO の、作成が、失敗する"
    GPU・ドライバーが、その SM に、対応していない。`CheckFeatureSupport` で、確認し、非対応なら、別の、シェーダーに、切り替える。

??? failure "Visual Studio の、HLSL コンパイラで、`vs_6_0` を、指定して、エラー"
    VS の、標準の、HLSL コンパイラは、`fxc`（SM 5.1 まで）。SM 6 は、`dxc` を、カスタム ビルドで、呼ぶ。

??? failure "実行ファイルを、別の場所に、置くと、`dxcompiler.dll` が、見つからない"
    実行時コンパイルを、使う場合、`dxcompiler.dll` と `dxil.dll` を、実行ファイルの、隣に、置く（署名に、`dxil.dll` が、必要）。

??? failure "PIX で、シェーダーの、ソースが、見えない"
    `-Zi` を、付けていない、または、`-Qembed_debug` が、無く、デバッグ情報が、別ファイルのまま、見つからない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 の、シェーダーは、HLSL を `dxc` で、DXIL に、コンパイルする
    - [x] ターゲットは `vs_6_0`、`ps_6_0`、`cs_6_0`、`lib_6_3`（DXR）、`ms_6_5`
    - [x] ビルド時にコンパイルするのが、標準（`-T`、`-E`、`-Fo`、`-Zi`）
    - [x] SM 6 の機能は、GPU の対応を、`CheckFeatureSupport` で、確認
    - [x] バイトコードは、`D3D12_SHADER_BYTECODE` で、PSO に、渡す
    - [x] ウェーブ命令で、`groupshared` より、速い、リダクションが、書ける

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Root Signature](root-signature.md)
- [PSO](pso.md)
- [Device and Factory](factory-device.md)
- [Microsoft Learn: DirectX Shader Compiler](https://learn.microsoft.com/ja-jp/windows/win32/direct3dhlsl/dx-graphics-hlsl-part1)
