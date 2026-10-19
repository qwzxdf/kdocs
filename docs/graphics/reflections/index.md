---
title: Reflections
tags:
  - 描画
---

# Reflections

水たまり・磨かれた床・金属・ガラス・濡れた路面では、<strong>周囲の景色が映り込みます</strong>。これが<strong>鏡面反射</strong>です。拡散反射（ざらっとした面の明るさ）は、面のどこから見ても同じ明るさでしたが、鏡面反射は見る方向によって、映るものが変わります。周囲の景色を画面の中でどう調達するかが描画手法の分かれ目です。このセクションでは、平面反射・リフレクション プローブ・スクリーン空間反射（SSR）・レイトレース反射を原理から順に説明します。

## 学び方

反射の分野は、「何をどこから持ってくるか」という調達の問題です。4 つの方式は、調達先が違うだけで、反射方向の景色を拾って BRDF の山で平均するという、やることは同じです。そのため、この順で読むとよいでしょう。

最初に[プローブ](probes/index.md)です。反射の基本は、周囲の写真を撮って、反射方向を引くことです。このとき、粗さに応じてぼかした写真（事前フィルタ）を用意する仕組みが、すべての方式の出発点になります。次に、プローブの限界（近くの物が映らない、視差がずれる）を補う SSR に進みます。SSR は、画面の中の情報をレイで探す方法で、線形マーチから Hi-Z、確率的 SSR へと、高速化と品質向上が進みます。最後に、画面外を扱えない SSR の弱点を、プローブで補う[フォールバック](ssr-fallback.md)と、そもそも画面に頼らない[レイトレ反射](rt-reflections/index.md)を読みます。平面反射は、水面や鏡に特化した別の道として、独立して読めます。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Planar Reflections](planar.md) | 鏡の向こうからシーンを描き直す。完全な反射・高コスト |
| [Reflection Probes](probes/index.md) | 全方向の写真（キューブマップ）。事前フィルタ・視差補正 |
| [SSR Basics](ssr-basics/index.md) | 深度バッファでレイを進める。線形マーチ・厚み |
| [Hi-Z SSR](ssr-hiz.md) | 階層的な深度でレイを高速に進める |
| [Stochastic SSR](ssr-stochastic.md) | 粗さに合わせたレイ・ノイズ除去・再利用 |
| [SSR Fallback and Compositing](ssr-fallback.md) | 画面外・見えない部分をプローブで補う |
| [Ray-Traced Reflections](rt-reflections/index.md) | 画面に頼らない反射。ハイブリッド・デノイズ |
| [Reflection Comparison](comparison.md) | 原理・コスト・弱点の一覧と選び方 |

## 鏡面反射とは何を計算するのか

[AO Theory](../ao/theory/index.md)では<strong>拡散反射</strong>（方向によらず一定の反射）を考えました。<strong>鏡面反射</strong>の出射光は、入射方向によって、反射の強さが変わるBRDF を使います。

<div class="formula">L_o(ω_o) = ∫ f_spec(ω_i, ω_o) · L_i(ω_i) · (n·ω_i) dω_i</div>

式の項は、次のとおりです。f_spec は鏡面の BRDF（GGX など）で、反射方向の近くだけが大きい山の形をしています。L_i(ω_i) は方向 ω_i から届く光、つまり周囲の景色です。

### 粗さと反射の「ぼけ」

| 面 | f_spec の形 | 見た目 |
| --- | --- | --- |
| 完全な鏡（粗さ 0） | 反射方向の 1 点だけ | 周囲の景色がくっきり |
| 少し粗い | 反射方向の周りの小さな山 | 少しぼけた反射 |
| とても粗い | 広い山 | ぼんやりした反射（拡散に近づく） |

鏡面反射を求めるとは、<strong>「反射方向の周りの、BRDF の山の範囲の景色」を、重み付きで平均する</strong>ことです。<strong>粗いほど、広い範囲を平均</strong>します。<strong>この平均をどう安く近似するか</strong>が各方式の工夫の中心です。

## 4 つの景色の調達方法

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="反射の景色の調達方法">
<text x="20" y="24" class="fig-title">反射方向に「何が見えるか」を、どこから持ってくるか</text>
<rect x="20" y="50" width="180" height="170" rx="10" fill="rgba(76,139,245,0.2)" stroke="currentColor" stroke-width="2"/><text x="110" y="78" text-anchor="middle" style="font-weight:700">平面反射</text><text x="110" y="104" text-anchor="middle" style="font-size:12px">鏡の向こうから</text><text x="110" y="122" text-anchor="middle" style="font-size:12px">シーンを描き直す</text><text x="110" y="156" text-anchor="middle" style="font-size:12px">正確・平面だけ</text><text x="110" y="174" text-anchor="middle" style="font-size:12px">コスト：大</text>
<rect x="215" y="50" width="180" height="170" rx="10" fill="rgba(46,160,67,0.2)" stroke="currentColor" stroke-width="2"/><text x="305" y="78" text-anchor="middle" style="font-weight:700">プローブ</text><text x="305" y="104" text-anchor="middle" style="font-size:12px">事前に撮った</text><text x="305" y="122" text-anchor="middle" style="font-size:12px">全方向の写真</text><text x="305" y="156" text-anchor="middle" style="font-size:12px">安い・位置がずれる</text><text x="305" y="174" text-anchor="middle" style="font-size:12px">コスト：小</text>
<rect x="410" y="50" width="180" height="170" rx="10" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="2"/><text x="500" y="78" text-anchor="middle" style="font-weight:700">SSR</text><text x="500" y="104" text-anchor="middle" style="font-size:12px">画面の中の</text><text x="500" y="122" text-anchor="middle" style="font-size:12px">見えている物から</text><text x="500" y="156" text-anchor="middle" style="font-size:12px">画面外は映らない</text><text x="500" y="174" text-anchor="middle" style="font-size:12px">コスト：中</text>
<rect x="605" y="50" width="175" height="170" rx="10" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="2"/><text x="692" y="78" text-anchor="middle" style="font-weight:700">レイトレ</text><text x="692" y="104" text-anchor="middle" style="font-size:12px">シーンに</text><text x="692" y="122" text-anchor="middle" style="font-size:12px">直接レイを飛ばす</text><text x="692" y="156" text-anchor="middle" style="font-size:12px">正確・ノイズ除去</text><text x="692" y="174" text-anchor="middle" style="font-size:12px">コスト：大</text>
<text x="20" y="250" style="font-size:12px">実際のゲームは、これらを重ねて使う（SSR で足りない所を、プローブで補う、など）</text>
</svg>

| 方式 | 景色の出どころ | 向く場面 |
| --- | --- | --- |
| 平面反射 | 鏡の裏側から見た、シーン全体の再描画 | 水面・床・鏡（平面のみ） |
| プローブ | 事前に撮った、全方向のキューブマップ | 広い範囲の粗い反射（あらゆる面） |
| SSR | 画面の深度・色 | 近くの映り込み（地面・壁の接地部） |
| レイトレ | シーン全体（BVH） | 高品質な反射（ハードウェア対応） |

## 反射方向の求め方

視線ベクトル V（面から、カメラへ向かう向き）と、法線 N から、<strong>鏡面反射の方向</strong> R を求めます。

<div class="formula">R = 2 (N·V) N − V　（HLSL では reflect(−V, N)）</div>

```hlsl
float3 view_dir = normalize(camera_pos - world_pos);
float3 reflect_dir = reflect(-view_dir, normal);
```

<strong>粗い面</strong>では、R は「中心」で、<strong>実際には、R の周りの方向</strong>（法線を微小面の分布でずらした方向）の景色を重み付きで足します。

## 反射と他の効果の関係

| 効果 | 関係 |
| --- | --- |
| <strong>PBR の IBL（鏡面）</strong> | プローブの反射が、IBL の鏡面項（[PBR](../../3d/pbr.md)） |
| スペキュラ遮蔽 | 隅で反射を弱める（[GTAO](../ao/gtao.md)） |
| フレネル | 斜めから見るほど、反射が強い（反射の強さ） |
| <strong>半透明（水・ガラス）</strong> | 反射と屈折の合成（[シェーダー](../index.md)） |

## よくある誤解

??? failure "SSR を入れれば、反射は全部解決する"
    SSR は<strong>画面に映っている物だけ</strong>を反射します。<strong>画面外・物の裏側</strong>は映りません（[フォールバック](ssr-fallback.md)）。

??? failure "プローブの反射は、いつでも正しい位置に映る"
    プローブは<strong>1 点で撮った写真</strong>なので、<strong>視差</strong>（位置のずれ）が出ます。視差補正が必要です（[プローブ](probes/index.md)）。

??? failure "反射は、粗さに関係なく同じように計算できる"
    粗さによって、<strong>必要な範囲の平均</strong>が変わります。<strong>ぼけ方の扱い</strong>が各方式の難所です。

## 参考

- Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice（split-sum 近似）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice
- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014
- Stachowiak, Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Frostbite の SSR）
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019

## 関連ページ

- [シェーダー](../index.md)
- [PBR](../../3d/pbr.md)
- [法線とライティング](../../3d/lighting-normals.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
- [Ambient Occlusion (AO)](../ao/index.md)
- [描画最適化](../../rendering/index.md)
