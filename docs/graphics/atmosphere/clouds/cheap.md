---
title: Cheap Alternatives
tags:
  - 描画
---

# Cheap Alternatives

<strong>レイマーチが重い環境では、簡易な代替があります</strong>。<strong>スカイボックスのテクスチャ・ビルボード・平面に貼る雲</strong>などで、雰囲気を出します。このページでは、簡易な雲の表現を説明します。

!!! tip "ポイント"
    - スカイボックスに、雲を描いておく。
    - 平面に、雲のテクスチャを流す（スクロール）。
    - ビルボードの雲を配置する。
    - モバイルでは、これが標準。

## 簡易な代替
<strong>重いレイマーチが使えない場面</strong>の<strong>代替</strong>です。

| 方式 | 内容 |
| --- | --- |
| 雲のスカイボックス | 事前に描いた雲のキューブマップを回す |
| <strong>2D の雲（スカイドームの絵）</strong> | スクロールする雲のテクスチャ ＋ 法線マップで凹凸 |
| フローマップで動かす | 雲の絵を流れの向きに動かす（[Water Interaction](../../water/interaction/index.md)） |
| <strong>ボリューム テクスチャ（事前焼き）</strong> | 雲の塊を 3D テクスチャに焼き、ビルボードで描く |
| <strong>雲の板（インポスター）</strong> | 遠景の雲を板で置く |

### どれを選ぶか

簡易な方式の選択は、「雲をどれだけ近くから見るか」で決まります。地上の視点から、ほぼ動かない遠くの空として見るだけなら、スカイボックスか 2D のスクロールで十分です。2D の雲に<strong>視差</strong>（視点移動で見え方が変わる効果）を足したければ、雲の高さのテクスチャをもとに、視線の方向に UV をずらす「パララックス マッピング」を雲のドームに適用します。雲の層を 2〜3 枚、高さを変えて重ねれば、奥行きが生まれます。

飛行機や気球のように、雲に近づく、雲の中を通る場面があるなら、板では限界があります。その場面だけ、ボリューム テクスチャを貼ったビルボードか、本物のレイマーチに切り替えます。近づくほど板が分かりやすくなるので、見る距離に応じて方式を切り替える（LOD）設計が現実的です。

モバイルでは、スカイボックスと 2D の雲が標準的な選択です。これに時刻に応じた色の変化（ライティングの色を空の色に合わせる）を足せば、静的な絵でも、昼から夕方への移り変わりを違和感なく表現できます。

## ボリューム雲は、重い

レイマーチの、ボリューム雲（[Cloud Raymarching](raymarch.md)）は、<strong>美しい</strong>が、<strong>重く</strong>、実装も、複雑です。モバイル、低スペック、カメラが、雲に、近づかないゲームでは、もっと、安い方法が、十分です。

| 方式 | 立体感 | コスト | 向く場面 |
| --- | --- | --- | --- |
| ボリューム（レイマーチ） | 完全 | 重い | 高品質、飛行、カメラが、雲に、近づく |
| スカイドーム テクスチャ | なし（平面） | 最小 | モバイル、遠景だけ |
| 2D の、層（視差） | わずか（視差） | 小 | 中程度の品質 |
| 雲の、板（ビルボード） | 中（個々の、雲は、立体的に、見える） | 小〜中 | 空の、雲が、少なく、近づける |
| フリップブック（アニメーションする、雲の板） | 中 | 中 | 動きのある、局所的な雲 |

## 方法 1：スカイドーム テクスチャ

<strong>空全体</strong>を、<strong>1 枚の（または、数枚の）、画像</strong>で、覆います。雲が、描かれた、画像を、空の、ドームに、貼るだけです。

```hlsl
// 空の方向（球面）を、平面の UV に、割り当てて、雲のテクスチャを、引く。
float2 CloudUv(float3 view_dir, float time) {
  // 平面への投影: 視線が、水平に近づくほど、遠くに、投影される（雲が、地平線に向かって、縮む）。
  float2 uv = view_dir.xz / max(view_dir.y + 0.1, 0.05);
  return uv * g_cloud_scale + g_wind_direction * time * g_wind_speed;
}
float4 cloud = g_cloud_tex.Sample(g_linear_wrap, CloudUv(view_dir, g_time));
float3 sky_with_cloud = lerp(sky_color, cloud.rgb, cloud.a);
```

<strong>視線の、`y` で、割る</strong>ことで、<strong>平らな、雲の層</strong>を、見上げた、ような、遠近感（地平線に、近い雲ほど、小さく、密）が、出ます。風で、UV を、ずらすと、雲が、流れます。最も、安く、どんな、プラットフォームでも、動きます。立体感は、ありません。

### 太陽の方向での、色づけ

<strong>雲の絵</strong>を、<strong>そのまま</strong>、貼ると、太陽の方向と、関係なく、同じ色で、平板です。太陽の、方向を、見るほど、雲の縁が、明るく、光るように、色を、補うと、立体感が、増します。

```hlsl
float sun_glow = pow(saturate(dot(view_dir, g_sun_dir)), 8.0);
float3 cloud_color = cloud.rgb * (1.0 + sun_glow * 2.0);                // 太陽の方を見ると、雲が、明るくなる
```

## 方法 2：2D の層を、重ねる（視差）

<strong>雲の、テクスチャの層を、2〜3 枚</strong>、<strong>高さを、変えて</strong>、重ねます。カメラが、動くと、層ごとに、見える位置が、ずれる（視差）ので、奥行きが、感じられます。

```hlsl
// 3 層の、雲。各層は、異なる高さ（= 異なる、投影スケール）と、風の速さを、持つ。
float4 c0 = SampleCloudLayer(view_dir, /*height*/ 1.0, /*speed*/ 0.010);
float4 c1 = SampleCloudLayer(view_dir, /*height*/ 1.5, /*speed*/ 0.015);
float4 c2 = SampleCloudLayer(view_dir, /*height*/ 2.2, /*speed*/ 0.022);
// 奥の層から、順に、重ねる。
float3 color = sky_color;
color = lerp(color, c2.rgb, c2.a);
color = lerp(color, c1.rgb, c1.a);
color = lerp(color, c0.rgb, c0.a);
```

<strong>手前の層</strong>ほど、<strong>速く動き</strong>、大きく見えます。奥行きの、手がかり（視差）が、増え、平板さが、減ります。

### 雲の、厚みの、近似（疑似的な、立体感）

<strong>1 枚の、テクスチャ</strong>から、<strong>光の、方向へ、少し、ずらして、もう 1 回読み</strong>、厚みを、近似する、方法が、あります。

```hlsl
// 光の方向へ、UV を、少しずらして、もう一度読む。その差から、雲の、明暗（厚みの手がかり）を、作る。
float density = g_cloud_tex.Sample(g_linear_wrap, uv).a;
float density_toward_sun = g_cloud_tex.Sample(g_linear_wrap, uv + sun_dir_uv * 0.02).a;
float shade = saturate(1.0 - (density_toward_sun - density) * 3.0);      // 太陽側に、雲が、続いているほど、暗い（影の中）
float3 lit_cloud = lerp(g_cloud_shadow_color, g_cloud_lit_color, shade);
```

<strong>太陽の方向に、雲が、続いている</strong>（<strong>光を、遮る</strong>）なら、暗く、続いていない（縁）なら、明るくします。1 回の、余計な、テクスチャ読み込みで、雲の、陰影が、出ます。

## 方法 3：雲の板（ビルボード）

<strong>個々の、雲</strong>を、<strong>カメラを、向く、板</strong>に、雲の絵を、貼って、空に、点在させます。積雲（もこもこ）の、数個だけ、空に、浮かべる用途に、向きます。

| 要素 | 内容 |
| --- | --- |
| 板の数 | 数十〜数百 |
| 絵 | ライティング済みの、雲の画像（複数の、バリエーション） |
| 向き | 常に、カメラを向く（ビルボード） |
| 太陽の方向 | 画像の明暗を、太陽の位置に応じて、切り替える、または、法線マップで、ライティング |
| ソート | 奥から手前（半透明）。加算でなく、アルファ ブレンド（[Sorting](../../translucency/blending-sorting/sorting.md)） |

<strong>近づく</strong>と、<strong>板だと、分かる</strong>ので、近づけない場面（遠景の、雲）に、限ります。

## 方法 4：雲の、事前計算（フリップブック）

<strong>ボリューム雲</strong>を、<strong>事前に、レンダリング</strong>して、複数の角度から、画像にしておき、カメラの向きに、近い画像を、板に、貼る方法です（インポスター。[Trees](../../terrain/vegetation/trees.md) の、インポスターと、同じ）。実時間の、レイマーチなしで、ボリュームらしい、見た目が、得られます。

## 切り替え：近くは、ボリューム、遠くは、安く

<strong>近く</strong>（<strong>カメラの周り</strong>）の、雲だけ、ボリュームで、遠くは、安い方法に、切り替える、ハイブリッドです。

| 距離 | 方式 |
| --- | --- |
| 〜10 km | ボリューム（レイマーチ。低解像度 + 時間方向の、更新） |
| 10 km〜 | 2D の層、スカイドーム テクスチャ |
| 超遠景（地平線） | 霧の色に、フェード |

<strong>境目</strong>は、<strong>フェード</strong>で、なめらかに、つなぎます。ボリュームの、遠景が、重い（視線が、殻を、長く通る）ので、遠景を、安い方法に、することで、大幅に、軽くなります。

## よくあるミス

??? failure "簡易な雲が、動かず、不自然"
    <strong>テクスチャを、ゆっくりスクロール</strong>させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重い環境では、テクスチャとビルボードで代替

## 参考

- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Clouds](index.md)
- [Gradient Sky](../sky-models/gradient.md)
