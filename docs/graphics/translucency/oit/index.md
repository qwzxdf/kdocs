---
title: Order-Independent Transparency (OIT)
tags:
  - 描画
---

# Order-Independent Transparency (OIT)

**半透明は、ソートしないと崩れますが、入り組んだ形では、ソートで解決できません**。**OIT（Order-Independent Transparency）は、描く順序に依存せず、正しい半透明を作る手法の総称**です。このセクションでは、**問題の整理・Depth Peeling・PPLL・WBOIT・確率的透明・ハイブリッド**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **ソートでは、入り組んだ半透明を直せない**。
    - **OIT ＝ 描く順序に依存しない半透明**。
    - **正確な方式（PPLL・Depth Peeling）は重く、近似の方式（WBOIT）は軽い**。
    - **用途に合わせて選ぶ**。

## 問題の整理
**画素ごとに、複数の半透明の層が重なる**場合、**正しい色は、奥から手前の順に合成した結果**です。

<div class="formula">C = C₁α₁ + (1−α₁)(C₂α₂ + (1−α₂)(C₃α₃ + …))　（1 が最も手前）</div>

**この式は、層の順序に依存**します。**OIT は、「層の順序」を知らなくても、この結果を近似または再現**します。

OIT 方式を比べます。従来のソートは、オブジェクト単位で並べるので、交差で破綻しますが、コストもメモリも小さいです。Depth Peeling は、深度を使って 1 層ずつ取り出すので、正確ですが、N 層分の描画（N 回）が必要で、メモリは中程度（N 枚）です。PPLL は、全層を保存して最後に並べるので正確ですが、ソートが重く、メモリは大きい（画素 × 層数）です。Weighted Blended は、順序を無視して重みで近似するので近似ですが、1 パスで軽く、メモリも小さい（2 枚）です。確率的な方式は、アルファを確率にして TAA で平均するので、収束すれば正確で、コストは小〜中、メモリは小です。

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
