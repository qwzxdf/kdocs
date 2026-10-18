---
title: Method Comparison
tags:
  - 描画
---

# Method Comparison

**アルファ テスト系の方式は、縁の品質・コスト・必要な条件が違います**。このページでは、**方式の比較と、選び方**を説明します。

!!! tip "ポイント"
    - **clip のみ：最も軽いが、縁がギザギザ**。
    - **A2C：MSAA が必要。縁がなめらか**。
    - **ハッシュド：TAA が必要。遠くでも安定**。
    - **ディザ：フェード アウト向き**。

## 方式の比較
方式を比べます。clip（アルファ テスト）は、縁がギザギザで、順序が不要、深度が書け、コストは低〜中で、草・葉・金網に使います。Alpha to Coverage は、縁が滑らか（MSAA）で、順序不要、深度が書け、MSAA のコストがかかり、MSAA 使用時の草や葉に使います。ハッシュド アルファは、縁が滑らか（TAA）で、順序不要、深度が書け、コストは低く、TAA 使用時の草・葉・髪に使います。ディザ透明は、網目状で、順序不要、深度が書け、コストは低く、カメラ前の遮蔽物を透かすために使います。ブレンドは、滑らかですが、順序が必要で、深度を書かず、コストは中〜大で、ガラスや煙に使います。

## よくあるミス

??? failure "MSAA も TAA も無いのに、A2C やハッシュドを選ぶ"
    **アンチエイリアスの方式に合わせて選ぶ**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **AA の方式に合わせて、選ぶ**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Alpha Testing](index.md)
- [Anti-Aliasing](../../postprocess/antialiasing/index.md)
