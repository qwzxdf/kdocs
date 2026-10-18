---
title: Hybrid Approaches and Choosing
tags:
  - 描画
---

# Hybrid Approaches and Choosing

**OIT の方式は、用途によって向き不向きがあります**。**近くの重要な半透明は正確な方式、遠くの煙や粒子は軽い方式**、というように、**組み合わせる**ことも多いです。このページでは、**ハイブリッド構成と、方式の選び方**を説明します。

!!! tip "ポイント"
    - **重要な半透明（ガラス・水）は、ソート ＋ 正確な方式**。
    - **煙・粒子は、WBOIT**。
    - **ハードウェアや予算で、選択が変わる**。
    - **ほとんどのゲームは、ソート ＋ WBOIT で十分**。

## Hybrid {#ハイブリッド}
**実用では、正確な方式と、軽い方式を、組み合わせ**ます。

ハイブリッドの方式は 3 つです。上位 N 層だけ正確にする方法は、手前の数層を PPLL か Peeling で正確に扱い、残りを Weighted Blended で処理します。重要な物だけ OIT にする方法は、ガラスや髪などは OIT にして、パーティクルは加算ブレンド（順序不要）にします。距離で切り替える方法は、近くは正確に、遠くは近似にします。

## Choosing a Method {#方式の選び方}
| 状況 | おすすめ |
| --- | --- |
| **パーティクルが大量・加算で済む** | <strong>加算ブレンド（OIT 不要）</strong> |
| **ガラス・水が少数** | <strong>ソート ＋ 2 パス（前面・背面）</strong> |
| **髪・草など、細かい重なり** | **ハッシュド アルファ ＋ TAA**・**Weighted Blended** |
| <strong>精度が重要（CAD・可視化）</strong> | **PPLL・Depth Peeling** |
| **ゲームで、広く使える軽い OIT** | **Weighted Blended OIT** |

## Common Mistakes {#よくあるミス}

??? failure "すべてを PPLL にして、重くなる"
    **重要な所だけ**正確な方式にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **重要度で、方式を使い分ける**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [OIT](index.md)
- [WBOIT](wboit.md)
- [PPLL](ppll.md)
