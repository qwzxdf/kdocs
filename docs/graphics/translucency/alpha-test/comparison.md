---
title: 方式の比較
tags:
  - 描画
---

# 方式の比較

**アルファ テスト系の方式は、縁の品質・コスト・必要な条件が違います**。このページでは、**方式の比較と、選び方**を説明します。

!!! tip "ポイント"
    - **clip のみ：最も軽いが、縁がギザギザ**。
    - **A2C：MSAA が必要。縁がなめらか**。
    - **ハッシュド：TAA が必要。遠くでも安定**。
    - **ディザ：フェード アウト向き**。

## 方式の比較
| 方式 | 縁 | 順序 | 深度 | コスト | 用途 |
| --- | --- | --- | --- | --- | --- |
| <strong>clip（アルファ テスト）</strong> | ギザギザ | 不要 | 書ける | 低〜中 | 草・葉・金網 |
| **Alpha to Coverage** | 滑らか（MSAA） | 不要 | 書ける | MSAA のコスト | 草・葉（MSAA 使用時） |
| **ハッシュド アルファ** | 滑らか（TAA） | 不要 | 書ける | 低 | 草・葉・髪（TAA 使用時） |
| **ディザ透明** | 網目状 | 不要 | 書ける | 低 | カメラ前の遮蔽物を透かす |
| **ブレンド** | 滑らか | **必要** | 書かない | 中〜大 | ガラス・煙 |

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

- [アルファ テスト](index.md)
- [アンチエイリアシング](../../postprocess/antialiasing/index.md)
