---
title: Shaders and DXC
tags:
  - DirectX
---

# Shaders and DXC

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

GPU は C++ のコードを直接実行できません。頂点を変換したりピクセルの色を決めたりする小さなプログラム（シェーダー）は、HLSL という専用の言語で書き GPU が読める命令列にコンパイルしてから、渡します。

D3D12 ではそのコンパイラーに <strong>DXC</strong>（DirectX Shader Compiler）を使い、コンパイル結果の形式は <strong>DXIL</strong> です。DXC はシェーダー モデル 6.0 以上（SM 6.x）に対応した新しいコンパイラーで、ウェーブ命令、64 ビット整数、バインドレス（SM 6.6）、レイトレーシング（DXR）、メッシュ シェーダーは DXC がないと使えません。古い `fxc`（SM 5.1 まで）でも基本的なシェーダーは動きます。

!!! tip "ポイント"
    - HLSL を `dxc` で DXIL にコンパイルして、`.cso`（または `.dxil`）に保存し実行時に読み込む。
    - ターゲットは頂点が `vs_6_0`、ピクセルが `ps_6_0`、計算が `cs_6_0`、DXR が `lib_6_3`、メッシュが `ms_6_5`。
    - コンパイルはビルド時に行うのが標準。実行時にコンパイルするなら `IDxcCompiler3` を使う。
    - GPU が対応しているシェーダー モデルは、`CheckFeatureSupport` で確認する。
    - コンパイル結果は `D3D12_SHADER_BYTECODE` に入れて PSO に渡す（[PSO](pso.md)）。

!!! info "このページを読む前に"
    HLSL の基本（`cbuffer`、`Texture2D`、`SamplerState`）が分かると読みやすくなります。コンパイル結果は[ID3DBlob](api/id3dblob.md) に入って返ってきます。シェーダーを渡す先は [PSO](pso.md)、リソースの宣言と結びつくのは [Root Signature](root-signature.md) です。

## シェーダー モデル

シェーダー モデル（SM）は HLSL の機能のバージョンです。SM 5.0 と 5.1 は `fxc` で、SM 6.0 以降は `dxc` でコンパイルします。

SM 5.1 は D3D12 向けにリソースの配列とレジスタ スペースが加わった版です。SM 6.0 でウェーブ命令（`WaveActiveSum` など）が入りました。6.2 は 16 ビットの浮動小数点と整数、6.3 は DXR、6.5 はメッシュ シェーダーと増幅シェーダー、それに DXR 1.1（`RayQuery`）を加えました。6.6 はバインドレス（`ResourceDescriptorHeap`）と 64 ビットのアトミックです。6.7 と 6.8 にはウェーブ行列やワーク グラフなどの拡張があります。

SM 6 の機能は GPU とドライバーが対応していないと使えません。`CheckFeatureSupport` の `D3D12_FEATURE_SHADER_MODEL` で対応する最大の SM を調べます（[Device and Factory](factory-device.md#checkfeaturesupport)）。

## dxc でビルド時にコンパイルする

コマンド ラインからシェーダーを 1 つずつコンパイルします。

```text
dxc -T vs_6_0 -E VSMain -Fo triangle_vs.cso triangle.hlsl
dxc -T ps_6_0 -E PSMain -Fo triangle_ps.cso triangle.hlsl
dxc -T cs_6_0 -E MainCS -Fo blur_cs.cso blur.hlsl
```

主なオプションは次のとおりです。

`-T` はターゲット（`vs_6_0`、`ps_6_0`、`cs_6_0`、`lib_6_3`、`ms_6_5`）、`-E` は入口になる関数の名前、`-Fo` は出力ファイルの名前です。`-Zi` はデバッグ情報を付けて PIX や RenderDoc でソースが見えるようにします。`-Od` は最適化なし `-O3` は最大の最適化（既定）です。

`-I dir` は `#include` の検索パス、`-D NAME=value` は `#define` を渡します。`-Qembed_debug` はデバッグ情報をバイトコードの中へ埋め込みます。`-enable-16bit-types` は SM 6.2 以上で 16 ビットの型を使えるようにします。

`dxc.exe` は Windows SDK（`bin\<version>\x64\dxc.exe`）に含まれています。Visual Studio の標準の HLSL コンパイラーは `fxc` を使うので、SM 6 のシェーダーはカスタム ビルド ステップで `dxc` を呼びます。

### Visual Studio のカスタム ビルドにする

HLSL ファイルのプロパティで、「項目の種類」を「カスタム ビルド ツール」にして、次を設定します。

```text
コマンド ライン:  dxc -T ps_6_0 -E PSMain -Fo "$(OutDir)%(Filename)_ps.cso" "%(FullPath)"
出力:            $(OutDir)%(Filename)_ps.cso
```

CMake のプロジェクトでは `add_custom_command` で `dxc` を呼びます。

## 実行時にコンパイルする

DXC はライブラリ（`dxcompiler.dll`）としても使えます。シェーダーの書き換えをすぐ反映する、ホット リロードに便利です。

```cpp
#include <dxcapi.h>
#pragma comment(lib, "dxcompiler.lib")

ComPtr<IDxcBlob> CompileShader(const wchar_t* path, const wchar_t* entry, const wchar_t* target) {
  ComPtr<IDxcUtils> utils;
  ComPtr<IDxcCompiler3> compiler;
  DxcCreateInstance(CLSID_DxcUtils, IID_PPV_ARGS(&utils));
  DxcCreateInstance(CLSID_DxcCompiler, IID_PPV_ARGS(&compiler));

  ComPtr<IDxcBlobEncoding> source;
  utils->LoadFile(path, nullptr, &source);  // HLSL を読む
  DxcBuffer buffer = {source->GetBufferPointer(), source->GetBufferSize(), DXC_CP_ACP};

  const wchar_t* args[] = {L"-E", entry, L"-T", target, L"-Zi", L"-Qembed_debug"};
  ComPtr<IDxcResult> result;
  compiler->Compile(&buffer, args, ARRAYSIZE(args), nullptr, IID_PPV_ARGS(&result));

  ComPtr<IDxcBlobUtf8> errors;
  result->GetOutput(DXC_OUT_ERRORS, IID_PPV_ARGS(&errors), nullptr);
  if (errors && errors->GetStringLength() > 0) {
    OutputDebugStringA(errors->GetStringPointer());  // エラーと警告
  }

  ComPtr<IDxcBlob> bytecode;
  result->GetOutput(DXC_OUT_OBJECT, IID_PPV_ARGS(&bytecode), nullptr);
  return bytecode;  // DXIL。D3D12_SHADER_BYTECODE に渡す
}
```

`IDxcCompiler3::Compile` にはコマンド ラインと同じ引数を文字列の配列で渡します。エラーと警告の文字列（`DXC_OUT_ERRORS`）は必ず表示します。コンパイルに失敗してもこの関数自体はエラーを返さないことがありエラー文字列を見ないと、原因が分かりません。

## バイトコードを PSO に渡す

D3D12 のシェーダーは単独のオブジェクトにはなりません。バイトコードの先頭ポインターと大きさを PSO の記述子に入れて渡します。

```cpp
// .cso を読み込む、または上の CompileShader の結果を使う。
D3D12_SHADER_BYTECODE vs = {vs_blob->GetBufferPointer(), vs_blob->GetBufferSize()};
pso_desc.VS = vs;
```

詳しくは [PSO](pso.md) で説明しています。

## D3D12 向けの HLSL の書き方

D3D12 のシェーダーはリソースを**レジスタ スペース**つきで宣言できます。

```hlsl
// ルート シグネチャのパラメーターに対応する宣言。space0 は省略できる。
Texture2D<float4> g_albedo : register(t0, space0);
SamplerState g_sampler : register(s0, space0);
cbuffer PerObject : register(b0, space0) {
  row_major float4x4 world_view_projection;
};
```

`register(t0, space0)` の `space` はリソースを論理的にグループ分けする番号です。バインドレスやリソースの配列で使い分けます（[Root Signature](root-signature.md)）。

### ルート シグネチャを HLSL に埋め込む

ルート シグネチャは C++ で組み立てる代わりにシェーダーの中に文字列で書けます。`dxc` が DXIL に埋め込みます。

```hlsl
#define RS "RootFlags(ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT), " \
           "CBV(b0), " \
           "DescriptorTable(SRV(t0, numDescriptors = 1)), " \
           "StaticSampler(s0, filter = FILTER_MIN_MAG_MIP_LINEAR)"

[RootSignature(RS)]
VSOutput VSMain(VSInput input) { /* ... */ }
```

短く書けますが C++ 側で動的に変える制御はできません。

## ウェーブ命令（SM 6.0）

GPU は 32 または 64 スレッドを 1 組（ウェーブ）にして実行します。SM 6.0 で同じウェーブの中のスレッドどうしで値をやり取りする命令が加わりました。

```hlsl
// ウェーブ全体で合計を求める。groupshared とバリアなしで、速い。
float sum = WaveActiveSum(value);
uint lane = WaveGetLaneIndex();  // ウェーブの中での自分の番号
bool any = WaveActiveAnyTrue(condition);
```

ヒストグラム、合計や最大を求める処理（リダクション）、ライトのカリングで `groupshared` を使うより速く書けます。

## デバッグ情報

```text
dxc -T ps_6_0 -E PSMain -Zi -Qembed_debug -Fo shader.cso shader.hlsl
```

`-Zi` と `-Qembed_debug` を付けると PIX や RenderDoc が、HLSL のソースの行を表示できます。製品ではデバッグ情報を別のファイル（`-Fd`）に分けて、実行ファイルを小さくします。

## よくあるミス

??? failure "SM 6 の機能（ウェーブ命令、DXR）を使ったら PSO の作成が失敗する"
    GPU かドライバーがその SM に対応していません。`CheckFeatureSupport` で確認して対応していなければ別のシェーダーに切り替えます。

??? failure "Visual Studio の HLSL コンパイラーで `vs_6_0` を指定してエラーになる"
    標準の HLSL コンパイラーは `fxc`（SM 5.1 まで）です。SM 6 は `dxc` をカスタム ビルドで呼びます。

??? failure "実行ファイルを別の場所へ置いたら `dxcompiler.dll` が見つからない"
    実行時にコンパイルするときは、`dxcompiler.dll` と `dxil.dll` を実行ファイルの隣に置きます。署名に `dxil.dll` が必要です。

??? failure "PIX でシェーダーのソースが見えない"
    `-Zi` を付けていないか `-Qembed_debug` がなくて、デバッグ情報の別ファイルが見つかっていません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 のシェーダーは、HLSL を `dxc` で DXIL にコンパイルする
    - [x] ターゲットは `vs_6_0`、`ps_6_0`、`cs_6_0`、`lib_6_3`（DXR）、`ms_6_5`
    - [x] ビルド時にコンパイルするのが標準（`-T`、`-E`、`-Fo`、`-Zi`）
    - [x] SM 6 の機能は、GPU の対応を `CheckFeatureSupport` で確認する
    - [x] バイトコードは `D3D12_SHADER_BYTECODE` に入れて、PSO に渡す
    - [x] ウェーブ命令で、`groupshared` より速い合計などが書ける

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3DBlob](api/id3dblob.md)
- [Root Signature](root-signature.md)
- [PSO](pso.md)
- [Device and Factory](factory-device.md)
- [Microsoft Learn: DirectX Shader Compiler](https://learn.microsoft.com/ja-jp/windows/win32/direct3dhlsl/dx-graphics-hlsl-part1)
