---
title: Distant Shadows
tags:
  - 描画
---

# Distant Shadows

**遠くまで、シャドウ マップを広げる**と**解像度が足りず、コストも大きい**ので、**遠景は別の方法**で**影を表します**。**雲の影（地面を流れる雲の影）や、遠くの山の影**など、**大きなスケールの影**は、**事前計算や、専用の簡易な方式**で**表現**します。このページでは、**遠景の影の扱い・雲の影・距離によるフェード**を説明します。

!!! tip "ポイント"
    - **シャドウ マップは、距離とともに解像度が落ちる**。**遠景は別の仕組み**。
    - **雲の影**：**雲の密度テクスチャを、太陽方向から地面へ投影**して**暗くする**。
    - **距離フェード**：**シャドウ マップの最大距離で、影を滑らかに消す**。
    - **遠くの影は、ベイク・距離場・簡易方式**。

## 遠景の影
**カスケードの最大距離**を超えた先は、**影がなくなります**。**遠景の山・建物**の**大きな影**を**どう扱うか**です。

遠景の影の扱いは 5 通りあります。最大距離で影を徐々に消すフェードアウト（[カスケード](../cascaded.md)）。静的な遠景をライトマップや影のマスクにベイクする方法。遠景に距離場の影を使う方法（[Distance Field Shadows](../sdf-shadows.md)）。最後のカスケードを非常に大きくして、粗くても遠くの大きな影を捉える方法。雲のテクスチャを地面に投影して、大規模で移動する影を安く表現する方法です。

### 雲の影

**雲のアルファ テクスチャ**を、**太陽の方向**から**地面に投影**し、**ライティングに乗算**します。**時間でスクロール**させれば、**雲の影がゆっくり動く**様子になります。

```hlsl
float2 cloud_uv = world_pos.xz * cloud_scale + wind * time;
float cloud_shadow = lerp(1.0, cloud_tex.Sample(linear_sampler, cloud_uv).r, cloud_strength);
lit *= cloud_shadow;
```

## よくあるミス

??? failure "シャドウ マップの最大距離で、影が急に消える"
    **最大距離の手前から、滑らかにフェード**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **遠景は別の方法で影を表す**
    - [x] **雲の影・距離フェードが定番**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Special Cases](index.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
- [Clouds](../../atmosphere/clouds/index.md)
