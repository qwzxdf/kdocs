---
title: Matching Fog Color to the Sky
tags:
  - 描画
---

# Matching Fog Color to the Sky

<strong>フォグの色が地平線の空の色と違うと、地平線に境目が見えて不自然</strong>です。<strong>フォグの色を空の色から取る</strong>ことで、自然につながります。このページではフォグの色の決め方を説明します。

!!! tip "ポイント"
    - 地平線の空の色を、フォグの色にする。
    - 空のキューブマップの低いミップを使う。
    - 時刻とともに自動で変わる。
    - 夜は暗い青に。

## フォグの色を空に合わせる
<strong>フォグの色が空と違う</strong>と <strong>遠景の山が「浮いて」</strong>見えます。

フォグの色の決め方は 3 通りあります。1 つ目は <strong>空の色を引いてくる</strong>方法です。視線の向きの空の色（スカイビュー LUT など）をフォグの色に使います。地平線付近の色を使うのがポイントです。2 つ目は <strong>環境マップの低いミップ</strong>を引く方法です。環境マップの平均色、あるいは視線方向の粗いミップを使えば、空の色が方向ごとに滑らかに変わります。3 つ目は <strong>手動設定</strong>です。時間帯ごとに色を設定して補間します。

### 色の考え方

フォグの色は「視線上の空気が散乱して目に届ける光」の色です。昼間の青い空の下では地平線に近い空は白っぽい水色になります。これは地平線の方向では視線が空気を長く通過するので、青だけでなく他の色も散乱を繰り返して、混ざり合うためです。夕方は太陽の側の地平線がオレンジや赤に、反対側が青紫になります。フォグの色がこの<strong>方向と時刻</strong>に追従していれば、遠景は空に自然に溶け込みます。逆に、一定の灰色のフォグでは夕焼けの中でも遠景が灰色のままで、不自然です。

実用的な設計は「フォグの色 = 視線方向の地平線近くの空の色」とすることです。空を描くための LUT や環境マップがすでにあるなら、フォグにも同じものを引けば追加の設定なしで時刻や天候に追従します（[Physically Based Aerial Perspective](physical.md)）。

### 露出との関係

フォグの色は HDR のリニア空間で扱い、露出（トーンマップ）の前に適用します。空は非常に明るい値を持っているので、フォグの色を LDR の見た目で決めて足すと、空とのつながりが合いません。

## 霧の色と空の色がずれると

遠景の <strong>山や建物</strong>は <strong>霧の色</strong>に、向かって霞んで消えていきます。その霧の色が空の地平線の色と違うと山の頂上の、すぐ上で色の境目が見えて不自然です。

| 状況 | 見え方 |
| --- | --- |
| 霧の色 = 空の地平線の色 | 遠景が空に自然に、溶け込む |
| 霧の色 ≠ 空の色 | 遠くの山が、「貼り付いた絵」に見える。輪郭が浮く |

## 方法 1：霧の色を空から取る

<strong>視線の方向</strong>の <strong>空の色</strong>（地平線付近）を、霧の色として使います。

```hlsl
// 霧の色を、視線の方向の、空の色から、取る（空を、キューブマップや、LUT に描いているとき）。
float3 FogColorFromSky(float3 view_dir) {
  // 地平線に近い方向の、空の色。視線が、上向きでも、地平線に、近い色を使う（霧は、地面近くの現象）。
  float3 horizon_dir = normalize(float3(view_dir.x, max(view_dir.y, 0.0) * 0.2, view_dir.z));
  return g_sky_cube.SampleLevel(g_linear_clamp, horizon_dir, 4).rgb;      // ぼかした（高いミップ）空の色
}
```

視線が <strong>上向きでも</strong>、<strong>水平方向の空の色</strong>に寄せます（`y` を、小さく）。霧は地面の近くの現象なので上空の、青い空の色を霧に使うと霧が青くなりすぎます。ミップの高い（ぼやけた）段を読んで空の、細かい模様（雲）を霧の色に持ち込まないようにします。

## 方法 2：空と霧を同じ大気から

<strong>物理ベース</strong>の方式（[Physically Based Aerial Perspective](physical.md)）では <strong>空と霧が、同じ大気の計算</strong>から決まるので自動で、一致します。空の色を霧の色にコピーする必要が、ありません。

## 方法 3：平均色を定数に

<strong>簡易な方法</strong>は <strong>空の地平線の、平均の色</strong>を CPU で計算し、定数バッファで霧の色として渡します。

```cpp
// 時間帯ごとに、地平線の色を、キーフレームで持ち、霧の色にも、同じキーフレームを、使う。
float3 horizon_color = SampleSkyKeyframes(time_of_day).horizon;
fog_color = horizon_color;                 // 空と、霧が、同じキーフレームから、決まる
```

<strong>空と霧が同じデータ</strong>（キーフレーム）から、決まるので <strong>必ず揃います</strong>。グラデーション スカイ（[Gradient Sky](../sky-models/gradient.md)）と、組み合わせる簡易な構成でよく使われます。

## 太陽の方向の考慮

空の地平線は <strong>太陽の方向</strong>で <strong>色が、変わります</strong>（太陽側が明るく橙）。霧の色も方向で変えると遠景が空に自然に、溶け込みます。

```hlsl
float3 horizon = lerp(g_horizon_color_away, g_horizon_color_sun, pow(saturate(dot(view_dir, g_sun_dir)), 4.0));
```

<strong>太陽に向かう</strong>方向の <strong>霧の色</strong>を空の、太陽側の地平線の色（橙、明るい）に寄せます。反対側は青〜灰色です。空のグラデーション（[Gradient Sky](../sky-models/gradient.md)）の、同じ式を霧にも使います。

## HDR と露出

<strong>空の色</strong>は <strong>HDR の値</strong>（明るい）で、霧の色も同じスケールでなければ霧が、浮きます。夜は霧の色も暗くします。

| 問題 | 内容 |
| --- | --- |
| 霧が夜でも明るい | 霧の色が昼の、固定値。時間帯で霧の色（と明るさ）も、変える |
| 霧が昼に暗い | 霧の色が、LDR の値（1 以下）。HDR の空の明るさに合わせる |
| 遠景が空より明るい | 霧の色が、空の地平線より明るすぎ。霧の色を空の地平線の色にそろえる |

## よくあるミス

??? failure "遠景と空の間に、境目が見える"
    <strong>フォグの色を空から取る</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の色を取って、フォグの色にする

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight", SIGGRAPH 1999
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [Sky Models](../sky-models/index.md)
