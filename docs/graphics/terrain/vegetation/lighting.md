---
title: Vegetation Lighting
tags:
  - 描画
---

# Vegetation Lighting

**葉は薄く、光が透けるので、普通の面のライティングでは、暗く見えます**。**裏側からの光を足す（透過）**ことで、**自然な明るさ**になります。このページでは、**植生のライティング**を説明します。

!!! tip "ポイント"
    - **葉の裏から当たった光を、表側に透過させる**。
    - **法線を、地面や球の向きに寄せて、均一にする**。
    - **影は、アルファ テストで、切り抜く**。
    - **環境光（AO）で、根元を暗くする**。

## Lighting {#ライティング}
| 要素 | 内容 |
| --- | --- |
| **法線** | **草の法線を地形の法線に寄せる**と**草原が面として一様に照らされ、ごちゃつかない** |
| **透過光** | **葉は光を通す**。**太陽が背後にあると明るい** |
| **AO** | **根元を暗く**（高さで）。**木の内側も暗く** |
| **影** | **草は影を落とさない・受けるだけ**にして、**軽くする** |

## Common Mistakes {#よくあるミス}

??? failure "逆光の葉が、真っ暗"
    **透過のライティング**を足す。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **透過と、法線の調整で、自然な明るさ**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Vegetation](index.md)
- [影のアルファ テスト](../../shadows/special-cases/alpha-test-shadows.md)
