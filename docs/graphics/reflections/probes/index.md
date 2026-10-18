---
title: Reflection Probes
tags:
  - 描画
---

# Reflection Probes

<strong>反射プローブは、ある地点から周囲を撮影して、キューブマップとして保存しておき、反射に使う手法</strong>です。<strong>画面の外の物も映せ、とても安い</strong>のが利点ですが、撮影した場所と、反射を見る場所がずれる（視差）ので、補正が必要です。このセクションでは、発想・事前フィルタ（粗さ）・視差補正・複数プローブのブレンド・SSR との併用を、1 つずつ別のページで説明します。

## 発想
反射は、「<strong>反射方向 R に何が見えるか</strong>」です。<strong>R 方向の景色</strong>をシーンから、その場で求めるのは大変です（レイトレ・SSR）。空間の 1 点（プローブの位置）から見た景色をあらかじめ写真に撮っておけば、R 方向のピクセルを読むだけで済みます。

プローブの使い方は単純です。プローブの位置から 6 方向（上下左右前後）を描いて、キューブマップに保存します（撮影）。表面の反射方向 R で、そのキューブマップを引きます（`cube.Sample(sampler, R)`）。粗い面では、粗さに応じてぼかしたミップを引きます（次の節）。

## キューブマップの作成
| 手順 | 内容 |
| --- | --- |
| ① 位置を決める | 部屋の中央、広場の中央など。反射が映る面の近く |
| ② 6 面を描く | 90 度の視野角で+X, −X, +Y, −Y, +Z, −Z の 6 方向を、HDR で描く |
| <strong>③ ミップを作る（事前フィルタ）</strong> | 粗さごとに反射のぼけを事前計算 |
| ④ 保存 | ベイク（事前）または実行時に更新 |

保存は<strong>HDR（浮動小数点）</strong>でなければなりません。太陽や光源の明るさが、反射のハイライトに効くためです。8 ビットの LDR で保存すると、ハイライトが白飛びして、金属の鋭い反射が出ません。

<strong>HDR（浮動小数点）</strong>で保存します。<strong>太陽や光源の明るさ</strong>が<strong>反射のハイライト</strong>に効くためです。

### プローブの考え方と限界

プローブの本質は、<strong>「1 点から見た景色を、全方向の写真として固定する」</strong>ことです。これは、その点にいる観察者にとっては正確ですが、プローブの位置から離れた表面にとっては、近似にすぎません。たとえば、部屋の中央に置いたプローブで、壁際の床の反射を引くと、本来は壁際から見える景色であるべきところが、部屋の中央から見える景色になります。この位置のずれ（視差）の補正が、[Parallax Correction](parallax.md) の主題です。

もう 1 つの限界は、<strong>静的</strong>なことです。撮影時に存在した物だけが映り、後から動く物、変化する光は映りません。動的に再撮影すると重いので、プローブは「変化しない背景の反射」を担当し、動く物は SSR で補うのが一般的です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Prefiltering (Split-Sum)](prefilter.md) | 粗さごとに、ぼかしたキューブマップを用意 |
| [Parallax Correction](parallax.md) | 撮影位置と見る位置のずれを直す |
| [Probe Operation](blending.md) | ブレンド・ベイクと更新・スカイボックス |
| [Combining with SSR](combine-ssr.md) | 使い分けと長所短所 |

## 反射プローブとは

<strong>反射プローブ</strong>は、<strong>空間の、ある点</strong>から、周りの景色を、キューブマップに、撮影した、ものです。つるつるの、面（金属、水たまり、磨いた床）は、この、キューブマップを、引いて、周りの景色を、映します。画面の、外にある物も、映せて、安いので、反射の、土台として、使われます。

```text
 部屋の中央に、プローブを置く → 6 方向（上下左右前後）の景色を、キューブマップに撮影（事前、または、動的）
 床や金属の面は、「反射の向き」で、キューブマップを引く → 周りの景色が、映る
```

## 仕組み

| 段階 | 内容 | ページ |
| --- | --- | --- |
| ① 撮影 | プローブの位置で、6 面を、レンダリング（HDR） | このページ |
| ② 事前フィルタ | 粗さごとに、ぼかした、ミップを、作る | [Prefiltering (Split-Sum)](prefilter.md) |
| ③ 視差補正 | プローブの位置と、物の位置が、違うことによる、ずれを、補正 | [Parallax Correction](parallax.md) |
| ④ ブレンド | 複数の、プローブを、位置に応じて、混ぜる | [Probe Operation](blending.md) |
| ⑤ SSR との、併用 | 画面内の、近くの物は、SSR、画面外は、プローブ | [Combining with SSR](combine-ssr.md) |

## ①撮影

<strong>プローブの、位置に、カメラを、置き</strong>、<strong>6 方向を、レンダリング</strong>して、キューブマップに、書きます。

```cpp
// 反射プローブ用の、キューブマップ（HDR、ミップつき）。128×128 × 6 面。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 128;
desc.Height = 128;
desc.MipLevels = 0;                                         // 全ミップ（粗さに応じた、ぼかしのため）
desc.ArraySize = 6;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;               // HDR
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_RENDER_TARGET;
desc.MiscFlags = D3D11_RESOURCE_MISC_TEXTURECUBE | D3D11_RESOURCE_MISC_GENERATE_MIPS;
device->CreateTexture2D(&desc, nullptr, &probe_cube);
```

<strong>6 面の、行列</strong>は、<strong>点光源の、キューブ シャドウ</strong>と、同じ、視野角 90°の、透視投影です（[Point Lights: Cube Maps](../../shadows/local-lights/point-cubemap.md)）。HDR（`R16G16B16A16_FLOAT`）で、撮るのは、明るい光（太陽の反射）を、保つためです。

```cpp
// 6 面を、それぞれ、レンダリングする。反射プローブでは、プローブ自身の反射は、描かない（無限再帰を、避ける）。
for (int face = 0; face < 6; ++face) {
  context->OMSetRenderTargets(1, face_rtv[face].GetAddressOf(), probe_depth_dsv.Get());
  UpdateCameraCB(probe_position, kForward[face], kUp[face], DirectX::XM_PIDIV2);
  RenderSceneForProbe();                                    // 簡易なシーン（遠景、主要な物だけ。低品質でよい）
}
context->GenerateMips(probe_cube_srv.Get());                // いったん、ミップを作る（正式な、ぼかしは、次のページ）
```

## 静的と、動的

| 種類 | 内容 | コスト |
| --- | --- | --- |
| ベイク（静的） | 制作時に、撮影して、保存。実行時は、読むだけ | 最小 |
| 動的（実行時に、撮り直す） | 昼夜の、変化、動く物を、反映 | 重い（6 面を、描き直す） |
| 昼夜用に、複数ベイク | 朝・昼・夕・夜の、キューブマップを、補間 | 小 |

<strong>動的な、更新</strong>は、<strong>重い</strong>ので、1 フレームに、1 面だけ、数フレームで、一巡、カメラの近くの、プローブを、優先、などの、間引きを、行います。

## 反射プローブの、限界

| 限界 | 内容 |
| --- | --- |
| 位置の、ずれ | キューブマップは、プローブの、位置から、見た景色。物の位置は、プローブと、違うので、映る景色が、ずれる（視差。[Parallax Correction](parallax.md)） |
| 解像度が、有限 | 128×128 で、細かい景色は、ぼやける。つるつるの、鏡面では、粗さが、目立つ |
| 動く物が、映らない（ベイク） | プレイヤー、車が、映らない。SSR や、平面反射で、補う |
| 自分自身が、映らない | プローブは、物が、無い、状態で、撮る |
| 遠景が、中心 | 遠くの景色（空、山）は、正確。近くの物は、ずれる |

## これだけ覚える

!!! abstract "まとめ"
    - [x] プローブは、安くて、画面外も映せる
    - [x] 粗さは事前フィルタ、ずれは視差補正

## 参考

- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice
- Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice（split-sum 近似）
- Lagarde, Zanuttini, "Local Image-Based Lighting With Parallax-Corrected Cubemap", SIGGRAPH 2012 Talks（箱による、視差補正）
- Bjorke, "Image-Based Lighting", GPU Gems, Chapter 19, 2004（キューブマップの、視差補正のはしり）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）

## 関連ページ

- [Reflections](../index.md)
- [SSR Basics](../ssr-basics/index.md)
- [SSR Fallback and Compositing](../ssr-fallback.md)
