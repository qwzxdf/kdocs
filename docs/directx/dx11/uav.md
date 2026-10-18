---
title: Unordered Access View (UAV)
tags:
  - DirectX
---

# Unordered Access View (UAV)

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

<strong>アンオーダード アクセス ビュー（UAV）</strong>は、テクスチャやバッファを、シェーダーから、<strong>自由な位置に、読み書き</strong>するための、窓です。「アンオーダード」は、複数のスレッドが、<strong>順序の決まらない</strong>まま、同時に、アクセスしてよい、という意味です。計算シェーダーの、出力の、標準で、ピクセル シェーダーからも、使えます。RTV が、「描画の、決まった位置（ピクセル）」にしか、書けないのに対し、UAV は、<strong>どこにでも</strong>書けます。

!!! tip "ポイント"
    - UAV ＝ 読み書き可能なビュー。HLSL では `RWTexture2D`、`RWStructuredBuffer`、`RWByteAddressBuffer`。
    - 作成は `CreateUnorderedAccessView`。リソースの `BindFlags` に `UNORDERED_ACCESS`。
    - 束縛は `CSSetUnorderedAccessViews`（計算シェーダー）、`OMSetRenderTargetsAndUnorderedAccessViews`（ピクセル シェーダー）。
    - <strong>`_SRGB` フォーマットは、使えない</strong>。型つきの、読み込みは、`R32_*` だけ。
    - 同じリソースを、UAV と SRV で、同時に、束ねられない。

## 作る

```cpp
// テクスチャの UAV。
D3D11_UNORDERED_ACCESS_VIEW_DESC desc = {};
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
desc.ViewDimension = D3D11_UAV_DIMENSION_TEXTURE2D;
desc.Texture2D.MipSlice = 0;                                // どのミップに、書くか
device->CreateUnorderedAccessView(texture.Get(), &desc, &uav);
```

| `ViewDimension` | 内容 | HLSL の型 |
| --- | --- | --- |
| `TEXTURE2D` | 2D テクスチャの、1 つのミップ | `RWTexture2D<T>` |
| `TEXTURE2DARRAY` | 配列の、一部の面 | `RWTexture2DArray<T>` |
| `TEXTURE3D` | 3D テクスチャ（froxel、ボクセル） | `RWTexture3D<T>` |
| `BUFFER` | バッファ（構造化、型つき、生） | `RWStructuredBuffer<T>`、`RWBuffer<T>`、`RWByteAddressBuffer` |

UAV は、<strong>1 つのミップ</strong>しか、見せられません（SRV と違い、ミップの範囲は、指定できない）。ミップ チェーンを、計算シェーダーで、作るときは、ミップごとに、UAV を、作ります。

## 型つき UAV の、制約

テクスチャの UAV には、フォーマットの、制約があります。

| できること | フォーマット |
| --- | --- |
| 書き込み | ほとんどの、非圧縮フォーマット（`R8G8B8A8_UNORM`、`R16G16B16A16_FLOAT`、`R11G11B10_FLOAT` など） |
| 読み込み・アトミック | `R32_FLOAT`、`R32_UINT`、`R32_SINT` のみ（機能レベル 11.0 で保証） |
| 使えない | `_SRGB`、圧縮（BC）、深度、MSAA |

`RWTexture2D<float4>` の、<strong>読み込み</strong>（`g_texture[id.xy]` を、右辺に書く）を、したいとき、`R16G16B16A16_FLOAT` などは、保証されません。ハードウェアが、対応しているかを、`CheckFeatureSupport` で、確認します。

```cpp
// 型つき UAV の、読み込みに、対応しているフォーマットを、調べる。
D3D11_FEATURE_DATA_FORMAT_SUPPORT2 support = {DXGI_FORMAT_R16G16B16A16_FLOAT};
device->CheckFeatureSupport(D3D11_FEATURE_FORMAT_SUPPORT2, &support, sizeof(support));
bool can_load = support.OutFormatSupport2 & D3D11_FORMAT_SUPPORT2_UAV_TYPED_LOAD;
```

対応していない場合は、<strong>入力と出力を、別のテクスチャにする</strong>（ピンポン）か、`R32_UINT` に、パックして、持ちます。

## 計算シェーダーで、使う

```cpp
ID3D11UnorderedAccessView* uavs[] = {output_uav.Get()};
context->CSSetUnorderedAccessViews(0, 1, uavs, nullptr);   // スロット 0 から。最後の引数: カウンターの初期値
context->Dispatch(groups_x, groups_y, 1);

ID3D11UnorderedAccessView* none[] = {nullptr};
context->CSSetUnorderedAccessViews(0, 1, none, nullptr);   // 終わったら、外す
```

```hlsl
RWTexture2D<float4> g_output : register(u0);                // u# が、UAV のスロット
g_output[id.xy] = result;                                   // 好きな位置に、書ける
```

UAV の、スロットは、`register(u#)` です。SRV（`t#`）、サンプラー（`s#`）、定数バッファ（`b#`）とは、別の、番号の空間です。

## ピクセル シェーダーから、使う

ピクセル シェーダーでも、UAV に、書けます（順序なしの、書き込み。ヒストグラム、PPLL、ヒットの記録など）。UAV は、レンダー ターゲットと、同じ、番号の、空間を、<strong>共有</strong>します（RTV が 0 番〜、その後ろに、UAV）。

```cpp
// ピクセル シェーダーで、UAV を使う: レンダー ターゲットと、UAV を、同時に、束ねる。
ID3D11RenderTargetView* rtvs[] = {scene_rtv.Get()};
ID3D11UnorderedAccessView* uavs[] = {head_uav.Get(), node_uav.Get()};
context->OMSetRenderTargetsAndUnorderedAccessViews(
    1, rtvs, depth_dsv.Get(),            // レンダー ターゲット 1 枚（スロット 0）
    1,                                   // UAV の開始スロット（RTV の、数の後ろ）
    2, uavs, nullptr);                   // UAV を、スロット 1 から、2 個
```

<strong>UAV の開始スロットは、レンダー ターゲットの、数以上</strong>にします。HLSL では、`register(u1)`、`register(u2)` のように、RTV の、後ろの番号を、使います（[PPLL](../../graphics/translucency/oit/ppll.md)）。

## カウンター（Append / Consume）

構造化バッファの UAV に、カウンターを、付けられます（[Structured and Raw Buffers](structured-buffer.md)）。

```cpp
UINT counts[] = {0};                                        // 束縛時に、カウンターを 0 にする（-1 で維持）
context->CSSetUnorderedAccessViews(0, 1, append_uav.GetAddressOf(), counts);
```

## UAV を、クリアする

```cpp
const UINT zero[4] = {0, 0, 0, 0};
context->ClearUnorderedAccessViewUint(uav.Get(), zero);          // 整数フォーマット（R32_UINT など）を、0 で埋める

const float clear[4] = {0, 0, 0, 0};
context->ClearUnorderedAccessViewFloat(uav.Get(), clear);        // 浮動小数・UNORM を、埋める
```

ヒストグラムの、バッファや、間接描画の、引数バッファを、毎フレーム、0 に戻すときに、使います。

## UAV と SRV の、切り替え

同じ、テクスチャを、計算シェーダーで、書いて（UAV）、次のパスで、読む（SRV）、という、<strong>パスの、つなぎ</strong>が、よくあります。

```cpp
// パス 1: 計算シェーダーで、書く。
context->CSSetUnorderedAccessViews(0, 1, uav.GetAddressOf(), nullptr);
context->Dispatch(gx, gy, 1);

// パス 2 の前: UAV の束縛を外して、SRV で読む。
ID3D11UnorderedAccessView* null_uav = nullptr;
context->CSSetUnorderedAccessViews(0, 1, &null_uav, nullptr);
context->PSSetShaderResources(0, 1, srv.GetAddressOf());
```

D3D11 は、UAV の書き込みと、次の、パスの読み込みの、<strong>順序</strong>を、ドライバーが、自動で、保証します（DirectX 12 では、リソース バリアが、要ります）。

## よくあるミス

??? failure "`CreateUnorderedAccessView` が、失敗する"
    テクスチャに `D3D11_BIND_UNORDERED_ACCESS` が、無い。フォーマットが、`_SRGB`、圧縮、深度。バッファの種類（構造化・生）と、ビューの、`Format` の、組み合わせが、違う。

??? failure "`RWTexture2D` の、読み込みが、真っ黒（または、未定義）"
    型つき UAV の、読み込みに、そのフォーマットが、対応していない。`R32_FLOAT` などに、するか、入力と出力を、別のテクスチャに、する。

??? failure "ピクセル シェーダーで、UAV が、効かない"
    `OMSetRenderTargetsAndUnorderedAccessViews` の、UAV の開始スロットが、RTV の数より、小さい。通常の `OMSetRenderTargets` は、UAV を、外してしまう。

??? failure "書いた結果が、次のパスで、読めない"
    UAV の束縛を、外さずに、同じリソースを、SRV として、束ねた。D3D11 は、SRV の、束縛を、黙って、外す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] UAV ＝ 読み書き可能な、ビュー。順序なしで、好きな位置に、書ける
    - [x] `RWTexture2D`、`RWStructuredBuffer`、`RWByteAddressBuffer`、`register(u#)`
    - [x] `_SRGB`・圧縮・深度は、不可。型つき読み込みは、`R32_*` だけ
    - [x] 計算シェーダーは `CSSetUnorderedAccessViews`、ピクセル シェーダーは `OMSetRenderTargetsAndUnorderedAccessViews`
    - [x] 次のパスで読む前に、UAV を、外す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Compute Shader](compute-shader.md)
- [Structured and Raw Buffers](structured-buffer.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [Resources and Views](../concepts/resources-views.md)
- [Microsoft Learn: ID3D11Device::CreateUnorderedAccessView](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createunorderedaccessview)
