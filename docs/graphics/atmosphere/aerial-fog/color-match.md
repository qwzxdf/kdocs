---
title: Matching Fog Color to the Sky
tags:
  - 描画
---

# Matching Fog Color to the Sky

**フォグの色が、地平線の空の色と違うと、地平線に境目が見えて、不自然**です。**フォグの色を、空の色から取る**ことで、**自然につながります**。このページでは、**フォグの色の決め方**を説明します。

!!! tip "ポイント"
    - **地平線の空の色を、フォグの色にする**。
    - **空のキューブマップの低いミップを使う**。
    - **時刻とともに、自動で変わる**。
    - **夜は、暗い青に**。

## Matching the Fog Color to the Sky {#フォグの色を空に合わせる}
**フォグの色が空と違う**と、<strong>遠景の山が「浮いて」</strong>見えます。

フォグの色の決め方は 3 通りあります。1 つ目は、<strong>空の色を引いてくる</strong>方法です。視線の向きの空の色（スカイビュー LUT など）をフォグの色に使います。地平線付近の色を使うのがポイントです。2 つ目は、<strong>環境マップの低いミップ</strong>を引く方法です。環境マップの平均色、あるいは視線方向の粗いミップを使えば、空の色が方向ごとに滑らかに変わります。3 つ目は、<strong>手動設定</strong>です。時間帯ごとに色を設定して、補間します。

### Thinking About Color {#色の考え方}

フォグの色は、「視線上の空気が散乱して目に届ける光」の色です。昼間の青い空の下では、地平線に近い空は白っぽい水色になります。これは、地平線の方向では、視線が空気を長く通過するので、青だけでなく他の色も散乱を繰り返して、混ざり合うためです。夕方は、太陽の側の地平線がオレンジや赤に、反対側が青紫になります。フォグの色が、この<strong>方向と時刻</strong>に追従していれば、遠景は空に自然に溶け込みます。逆に、一定の灰色のフォグでは、夕焼けの中でも遠景が灰色のままで、不自然です。

実用的な設計は、「フォグの色 = 視線方向の地平線近くの空の色」とすることです。空を描くための LUT や環境マップがすでにあるなら、フォグにも同じものを引けば、追加の設定なしで時刻や天候に追従します（[Physically Based Aerial Perspective](physical.md)）。

### Relation to Exposure {#露出との関係}

フォグの色は HDR のリニア空間で扱い、露出（トーンマップ）の前に適用します。空は非常に明るい値を持っているので、フォグの色を LDR の見た目で決めて足すと、空とのつながりが合いません。

## Common Mistakes {#よくあるミス}

??? failure "遠景と空の間に、境目が見える"
    **フォグの色を、空から取る**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **空の色を取って、フォグの色にする**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Aerial Perspective and Fog](index.md)
- [Sky Models](../sky-models/index.md)
