---
title: Other Underwater Elements
tags:
  - 描画
---

# Other Underwater Elements

**水中の雰囲気は、霧や光だけでなく、粒子・色補正・音でも作れます**。このページでは、**水中の他の要素**を説明します。

!!! tip "ポイント"
    - **浮遊する粒子（マリン スノー）**で、深さの感じを出す。
    - **色補正で、全体を青緑に寄せる**。
    - **音を、こもらせる**（ローパス フィルタ）。
    - **画面の端を少し歪ませる**と、水中らしい。

## 水中の他の要素
| 要素 | 内容 |
| --- | --- |
| **視界** | **水中の霧で見える距離を制限** |
| **ゆらぎ** | **画面全体を法線の動きで少し歪ませる**（[ポストプロセス](../../postprocess/index.md)） |
| **泡の粒子** | **ゆっくり上がる泡**（パーティクル） |
| **マリン スノー** | **漂う小さな粒**（ほこり）。**奥行き感が出る** |
| **音** | **ローパス フィルタ**（こもった音） |
| **色補正** | **青緑に寄せる** |

## よくあるミス

??? failure "水中なのに、地上と同じ雰囲気"
    **粒子・色補正・音**も**切り替える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **粒子・色・音も、水中用に切り替える**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Underwater Rendering](index.md)
- [Color Grading](../../postprocess/color-grading/index.md)
