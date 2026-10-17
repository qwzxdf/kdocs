---
title: Reflections
tags:
  - 描画
---

# Reflections

水たまり・磨かれた床・金属・ガラス・濡れた路面では、**周囲の景色が映り込みます**。これが**鏡面反射**です。拡散反射（ざらっとした面の明るさ）は、**面のどこから見ても同じ明るさ**でしたが、鏡面反射は**見る方向によって、映るものが変わります**。周囲の景色を**画面の中でどう調達するか**が描画手法の分かれ目です。このセクションでは、**平面反射・リフレクション プローブ・スクリーン空間反射（SSR）・レイトレース反射**を**原理から**順に説明します。

!!! tip "ポイント"
    - 鏡面反射は<strong>「視線を面で反射した方向に、何が見えるか」</strong>を調べること。<strong>方向ごとに景色が必要</strong>。
    - 調達先は 4 つ：<strong>平面を鏡にして描き直す（平面反射）</strong>・<strong>あらかじめ撮った全方向の写真（プローブ）</strong>・<strong>画面の中の見えている物（SSR）</strong>・<strong>シーンに直接レイ（レイトレ）</strong>。
    - <strong>粗い面</strong>ほど、<strong>ぼけた反射</strong>になる。<strong>粗さ（ラフネス）の扱い</strong>が各方式の難所。
    - <strong>SSR は画面に映っている物しか反射できない</strong>。<strong>画面外・裏側が弱点</strong>。プローブでフォールバックする。
    - 実際のゲームは<strong>複数の方式を組み合わせる</strong>（ハイブリッド）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Planar Reflections](planar.md) | 鏡の向こうからシーンを描き直す。完全な反射・高コスト |
| [リフレクション プローブ](probes/index.md) | 全方向の写真（キューブマップ）。事前フィルタ・視差補正 |
| [SSR の基礎](ssr-basics/index.md) | 深度バッファでレイを進める。線形マーチ・厚み |
| [Hi-Z SSR](ssr-hiz.md) | 階層的な深度でレイを高速に進める |
| [Stochastic SSR](ssr-stochastic.md) | 粗さに合わせたレイ・ノイズ除去・再利用 |
| [SSR Fallback and Compositing](ssr-fallback.md) | 画面外・見えない部分をプローブで補う |
| [レイトレース反射](rt-reflections/index.md) | 画面に頼らない反射。ハイブリッド・デノイズ |
| [方式の比較](comparison.md) | 原理・コスト・弱点の一覧と選び方 |

## 鏡面反射とは何を計算するのか

[AO Theory](../ao/theory/index.md)では**拡散反射**（方向によらず一定の反射）を考えました。**鏡面反射**の出射光は、**入射方向によって、反射の強さが変わる**BRDF を使います。

<div class="formula">L_o(ω_o) = ∫ f_spec(ω_i, ω_o) · L_i(ω_i) · (n·ω_i) dω_i</div>

| 項 | 意味 |
| --- | --- |
| **f_spec** | 鏡面の BRDF（GGX など）。**反射方向の近くだけ**が大きい山の形 |
| <strong>L_i(ω_i)</strong> | 方向 ω_i から届く光。**周囲の景色** |

### 粗さと反射の「ぼけ」

| 面 | f_spec の形 | 見た目 |
| --- | --- | --- |
| **完全な鏡**（粗さ 0） | **反射方向の 1 点だけ** | 周囲の景色が**くっきり** |
| **少し粗い** | 反射方向の周りの**小さな山** | **少しぼけた**反射 |
| **とても粗い** | 広い山 | **ぼんやり**した反射（拡散に近づく） |

鏡面反射を求めるとは、<strong>「反射方向の周りの、BRDF の山の範囲の景色」を、重み付きで平均する</strong>ことです。**粗いほど、広い範囲を平均**します。**この平均をどう安く近似するか**が各方式の工夫の中心です。

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
| **平面反射** | 鏡の裏側から見た、シーン全体の再描画 | **水面・床・鏡**（平面のみ） |
| **プローブ** | 事前に撮った、全方向のキューブマップ | **広い範囲の粗い反射**（あらゆる面） |
| **SSR** | 画面の深度・色 | **近くの映り込み**（地面・壁の接地部） |
| **レイトレ** | シーン全体（BVH） | **高品質な反射**（ハードウェア対応） |

## 反射方向の求め方

視線ベクトル V（面から、カメラへ向かう向き）と、法線 N から、**鏡面反射の方向** R を求めます。

<div class="formula">R = 2 (N·V) N − V　（HLSL では reflect(−V, N)）</div>

```hlsl
float3 view_dir = normalize(camera_pos - world_pos);
float3 reflect_dir = reflect(-view_dir, normal);
```

**粗い面**では、R は「中心」で、**実際には、R の周りの方向**（法線を微小面の分布でずらした方向）の景色を重み付きで足します。

## 反射と他の効果の関係

| 効果 | 関係 |
| --- | --- |
| <strong>PBR の IBL（鏡面）</strong> | **プローブの反射**が、IBL の鏡面項（[PBR](../../3d/pbr.md)） |
| **スペキュラ遮蔽** | **隅で反射を弱める**（[GTAO](../ao/gtao.md)） |
| **フレネル** | **斜めから見るほど、反射が強い**（反射の強さ） |
| <strong>半透明（水・ガラス）</strong> | 反射と屈折の**合成**（[半透明](../index.md)） |

## よくある誤解

??? failure "SSR を入れれば、反射は全部解決する"
    SSR は**画面に映っている物だけ**を反射します。**画面外・物の裏側**は映りません（[フォールバック](ssr-fallback.md)）。

??? failure "プローブの反射は、いつでも正しい位置に映る"
    プローブは**1 点で撮った写真**なので、**視差**（位置のずれ）が出ます。**視差補正**が必要です（[プローブ](probes/index.md)）。

??? failure "反射は、粗さに関係なく同じように計算できる"
    粗さによって、**必要な範囲の平均**が変わります。**ぼけ方の扱い**が各方式の難所です。

## 関連ページ

- [描画](../index.md)
- [PBR](../../3d/pbr.md)
- [法線とライティング](../../3d/lighting-normals.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
- [Ambient Occlusion (AO)](../ao/index.md)
