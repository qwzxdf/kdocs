---
title: Point and Spot Light Shadows
tags:
  - 描画
---

# Point and Spot Light Shadows

**太陽のような平行光は、1 枚のシャドウ マップ（またはカスケード）で足ります**が、**点光源やスポットライトは、数が多く、影の向きも多様**です。**ライトごとにシャドウ マップを作ると、数が増えるほど、描画が重くなります**。このセクションでは、**スポットライトの影・点光源のキューブ マップ・デュアル パラボロイド・多数のライトの管理とキャッシュ**を、**1 つずつ別のページ**で説明します。

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [Spot Lights](spot-light.md) | 透視投影 1 枚で、円錐の影 |
| [Point Lights: Cube Maps](point-cubemap.md) | 6 方向のマップ・サンプル・面の境 |
| [Dual Paraboloid](dual-paraboloid.md) | 2 枚で全方向を覆う方法 |
| [Shadows for Many Lights](many-lights.md) | アトラス・解像度の割り当て・キャッシュ・バイアス |

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **ローカル ライトは、スポット ＝ 1 枚、点 ＝ 6 枚**
    - [x] **多数のライトは、管理とキャッシュが鍵**

## References {#参考}

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## Related Pages {#関連ページ}

- [Shadows](../index.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
- [ライト カリング](../../../rendering/light-culling.md)
