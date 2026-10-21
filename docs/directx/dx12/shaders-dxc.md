---
title: Shaders and DXC
tags:
  - DirectX
---

# Shaders and DXC

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 のシェーダーは HLSL で書き <strong>DXC</strong>（DirectX Shader Compiler）で、<strong>DXIL</strong>（バイトコード）にコンパイルします。DXC はシェーダー モデル 6.0 以上（SM 6.x）に対応した新しいコンパイラーで、<strong>ウェーブ命令、64 ビット整数、バインドレス（SM 6.6）、レイトレーシング（DXR）、メッシュ シェーダー</strong>は DXC が、必要です。古い `fxc`（SM 5.1 まで）でも基本的なシェーダーは動きます。

!!! tip "ポイント"
    - HLSL を <strong>`dxc`</strong> で、DXIL にコンパイルして `.cso`（または `.dxil`）に保存し、実行時に読み込む。
    - ターゲット: 頂点 `vs_6_0`、ピクセル `ps_6_0`、計算 `cs_6_0`、DXR `lib_6_3`、メッシュ `ms_6_5`。
    - コンパイルは <strong>ビルド時</strong>が標準。実行時にコンパイルするなら `IDxcCompiler3` の API。
    - GPU が対応する、SM を `CheckFeatureSupport` で確認する。
    - シェーダーを PSO に渡す。バイトコードを `D3D12_SHADER_BYTECODE` に入れる（[PSO](pso.md)）。

## シェーダー モデル

シェーダー モデル（SM）は HLSL の機能のバージョンです。

| SM | コンパイラー | 主な追加 |
| --- | --- | --- |
| 5.0・5.1 | `fxc` | 従来の世代。5.1 はリソース配列、レジスタ スペース（D3D12 向け） |
| 6.0 | `dxc` | ウェーブ命令（`WaveActiveSum` など） |
| 6.2 | `dxc` | 16 ビットの浮動小数点、整数 |
| 6.3 | `dxc` | DXR（レイトレーシング） |
| 6.5 | `dxc` | メッシュ・増幅シェーダー、DXR 1.1（`RayQuery`） |
| 6.6 | `dxc` | バインドレス（`ResourceDescriptorHeap`）、64 ビット アトミック |
| 6.7・6.8 | `dxc` | 拡張（ウェーブ行列、ワーク グラフ など） |

SM 6 の機能は <strong>GPU・ドライバーが、対応していないと使えません</strong>。`CheckFeatureSupport(D3D12_FEATURE_SHADER_MODEL)` で確認します（[Device and Factory](factory-device.md)）。

## dxc を使う（ビルド時）

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
| `-Zi` | デバッグ情報（PIX、RenderDoc でソースが見える） |
| `-Od` | 最適化なし（デバッグ） |
| `-O3` | 最大の最適化（既定） |
| `-I dir` | `#include` の検索パス |
| `-D NAME=value` | `#define` |
| `-Qembed_debug` | デバッグ情報をバイトコードに埋め込む |
| `-enable-16bit-types` | 16 ビット型を有効に（SM 6.2 以上） |

`dxc.exe` は Windows SDK（`bin\<version>\x64\dxc.exe`）に含まれています。Visual Studio の HLSL コンパイラの項目は `fxc` を使うので SM 6 のシェーダーは、<strong>カスタム ビルド ステップ</strong>で `dxc` を呼びます。

### Visual Studio のカスタム ビルド

HLSL ファイルのプロパティで、「項目の種類」を「カスタム ビルド ツール」にして次を設定します。

| 設定 | 値 |
| --- | --- |
| コマンド ライン | `dxc -T ps_6_0 -E PSMain -Fo "$(OutDir)%(Filename)_ps.cso" "%(FullPath)"` |
| 出力 | `$(OutDir)%(Filename)_ps.cso` |

CMake のプロジェクトでは `add_custom_command` で `dxc` を呼びます。

## 実行時にコンパイルする

DXC はライブラリ（`dxcompiler.dll`）としても、使えます。ホット リロードに便利です。

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

`IDxcCompiler3::Compile` に引数の文字列を配列で渡します。<strong>エラー文字列</strong>（`DXC_OUT_ERRORS`）は必ず表示します。

## バイトコードを PSO に渡す

```cpp
// .cso を読む、または、上の CompileShader の結果を使う。
D3D12_SHADER_BYTECODE vs = {vs_blob->GetBufferPointer(), vs_blob->GetBufferSize()};
pso_desc.VS = vs;
```

D3D12 ではシェーダーは <strong>単体のオブジェクトではなく</strong>、バイトコードのポインターと大きさを PSO の記述子に入れます（[PSO](pso.md)）。

## HLSL の書き方の違い（D3D12 向け）

D3D12 のシェーダーはリソースを <strong>レジスタ スペース</strong>つきで、宣言できます。

```hlsl
// ルート シグネチャの、パラメータと、対応する宣言。space0 は、省略できる。
Texture2D<float4> g_albedo : register(t0, space0);
SamplerState g_sampler : register(s0, space0);
cbuffer PerObject : register(b0, space0) {
  row_major float4x4 world_view_projection;
};
```

`register(t0, space0)` の `space` はリソースの論理的なグループです。バインドレスや配列で使い分けます（[Root Signature](root-signature.md)）。

### ルート シグネチャを HLSL に埋め込む

```hlsl
// シェーダーの中に、ルート シグネチャを、書ける（dxc が、DXIL に、埋め込む）。
#define RS "RootFlags(ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT), " \
           "CBV(b0), " \
           "DescriptorTable(SRV(t0, numDescriptors = 1)), " \
           "StaticSampler(s0, filter = FILTER_MIN_MAG_MIP_LINEAR)"

[RootSignature(RS)]
VSOutput VSMain(VSInput input) { ... }
```

C++ でルート シグネチャを組み立てる代わりに HLSL に文字列で書く方法です。短く書けますが C++ 側の動的な制御が、できません（[Root Signature](root-signature.md)）。

## ウェーブ命令（SM 6.0）

GPU は 32 または 64 スレッドを 1 組（ウェーブ、ワープ）で実行します。SM 6.0 は <strong>ウェーブの中のスレッド同士</strong>で値をやり取りする命令を、追加しました。

```hlsl
// ウェーブ全体で、合計を求める（groupshared と、バリアなしで、速い）。
float sum = WaveActiveSum(value);
uint lane = WaveGetLaneIndex();                                  // ウェーブ内での、自分の番号
bool any = WaveActiveAnyTrue(condition);
```

ヒストグラム、リダクション（合計・最大）、ライトのカリングで `groupshared` より速く、書けます。

## デバッグ情報

```text
dxc -T ps_6_0 -E PSMain -Zi -Qembed_debug -Fo shader.cso shader.hlsl     # PIX で、ソースを見る
```

`-Zi` と `-Qembed_debug` を付けると PIX や RenderDoc が、HLSL のソース行を表示できます。製品ではデバッグ情報を別ファイル（`-Fd`）に分けて、リリースのサイズを減らします。

## よくあるミス

??? failure "SM 6 の機能（ウェーブ命令、DXR）を使ったら PSO の作成が、失敗する"
    GPU・ドライバーが、その SM に対応していない。`CheckFeatureSupport` で確認し非対応なら別のシェーダーに切り替える。

??? failure "Visual Studio の HLSL コンパイラで `vs_6_0` を、指定してエラー"
    VS の標準の HLSL コンパイラは、`fxc`（SM 5.1 まで）。SM 6 は `dxc` をカスタム ビルドで呼ぶ。

??? failure "実行ファイルを別の場所に置くと `dxcompiler.dll` が見つからない"
    実行時コンパイルを使う場合、`dxcompiler.dll` と `dxil.dll` を実行ファイルの隣に置く（署名に `dxil.dll` が必要）。

??? failure "PIX で、シェーダーのソースが見えない"
    `-Zi` を付けていないまたは `-Qembed_debug` が無く、デバッグ情報が別ファイルのまま見つからない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 のシェーダーは HLSL を `dxc` で、DXIL にコンパイルする
    - [x] ターゲットは `vs_6_0`、`ps_6_0`、`cs_6_0`、`lib_6_3`（DXR）、`ms_6_5`
    - [x] ビルド時にコンパイルするのが、標準（`-T`、`-E`、`-Fo`、`-Zi`）
    - [x] SM 6 の機能は、GPU の対応を `CheckFeatureSupport` で確認
    - [x] バイトコードは `D3D12_SHADER_BYTECODE` で、PSO に渡す
    - [x] ウェーブ命令で、`groupshared` より速いリダクションが書ける

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Root Signature](root-signature.md)
- [PSO](pso.md)
- [Device and Factory](factory-device.md)
- [Microsoft Learn: DirectX Shader Compiler](https://learn.microsoft.com/ja-jp/windows/win32/direct3dhlsl/dx-graphics-hlsl-part1)
