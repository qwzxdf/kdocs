---
title: Order-Independent Transparency (OIT)
tags:
  - 描画
---

# Order-Independent Transparency (OIT)

**半透明は、ソートしないと崩れますが、入り組んだ形では、ソートで解決できません**。**OIT（Order-Independent Transparency）は、描く順序に依存せず、正しい半透明を作る手法の総称**です。このセクションでは、**問題の整理・Depth Peeling・PPLL・WBOIT・確率的透明・ハイブリッド**を、**1 つずつ別のページ**で説明します。

## 問題の整理
**画素ごとに、複数の半透明の層が重なる**場合、**正しい色は、奥から手前の順に合成した結果**です。

<div class="formula">C = C₁α₁ + (1−α₁)(C₂α₂ + (1−α₂)(C₃α₃ + …))　（1 が最も手前）</div>

**この式は、層の順序に依存**します。**OIT は、「層の順序」を知らなくても、この結果を近似または再現**します。

| 方式 | 順序の扱い | 精度 | コスト | メモリ |
| --- | --- | --- | --- | --- |
| <strong>ソート（従来）</strong> | **オブジェクト単位で並べる** | 交差で破綻 | 小 | 小 |
| **Depth Peeling** | **深度を使って、1 層ずつ取り出す** | **正確** | **N 回の描画**（N 層） | 中（N 枚） |
| **PPLL** | **全層を保存して、最後に並べる** | **正確** | <strong>中（ソートが重い）</strong> | **大**（画素 × 層数） |
| **Weighted Blended** | **順序を無視し、重みで近似** | **近似** | **小**（1 パス） | 小（2 枚） |
| **確率的** | **アルファを確率にして、TAA で平均** | 収束すれば正確 | 小〜中 | 小 |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Depth Peeling](depth-peeling.md) | 手前の層から、1 枚ずつ剥ぐ |
| [PPLL](ppll.md) | 画素ごとのリストに集めて、並べ替える |
| [WBOIT](wboit.md) | 重み付き平均で、近似する |
| [Stochastic Transparency](stochastic.md) | ランダムに捨てて、平均する |
| [Hybrid Approaches and Choosing](hybrid.md) | 組み合わせと、選択の目安 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **OIT は、順序に依存しない半透明**
    - [x] **正確さとコストのトレードオフ**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Translucency](../index.md)
- [Alpha Blending and Sorting](../blending-sorting/index.md)
- [Refraction](../refraction/index.md)
