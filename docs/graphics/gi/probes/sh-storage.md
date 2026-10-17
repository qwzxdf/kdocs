---
title: SH の持ち方
tags:
  - 描画
---

# SH の持ち方

**プローブには、SH の係数を保存します**。**次数（L1 か L2）と、保存の形式（浮動小数点・圧縮）で、メモリと品質が変わります**。このページでは、**SH の持ち方の選択肢**を説明します。

!!! tip "ポイント"
    - **L1（4 係数）**：**軽い**が、**方向性が弱い**。
    - **L2（9 係数）**：**標準**。
    - **色ごと（RGB）に係数を持つ**ので、**L2 では 27 個**。
    - **テクスチャ（3D）に保存**して、**ハードウェア補間を使う**。

## SH をどう持つか
| 形式 | 係数 | 内容 |
| --- | --- | --- |
| <strong>SH L2（9 係数 × RGB）</strong> | 27 | **最も精度が高い**。**重い** |
| <strong>SH L1（4 係数 × RGB）</strong> | 12 | **軽い**。**やや粗い向き依存** |
| <strong>アンビエント キューブ（6 方向）</strong> | 18 | **6 方向（±X, ±Y, ±Z）の色**。**法線で、3 方向を混ぜる**。**非常に安い**（Source エンジンなど） |
| <strong>八面体マップ（小さなテクスチャ）</strong> | 可変 | **各プローブに小さな方向テクスチャ**。**DDGI などで採用**（[DDGI](../ddgi.md)） |

<strong>SH のリンギング（符号が負になる）</strong>に**注意**：**SH で表すと負の値が出る**ことがあり、<strong>ウィンドウ関数（ハンニング窓）</strong>で**抑える**・**クランプ**する対策があります。

## よくあるミス

??? failure "SH の次数が低く、方向による明暗の差が出ない"
    **L2 に上げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **L1 は軽い、L2 は標準**
    - [x] **3D テクスチャに入れて、補間をハードウェアに任せる**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [プローブ GI](index.md)
- [球面調和関数（SH）](../theory/spherical-harmonics.md)
- [補間の方式](interpolation.md)
