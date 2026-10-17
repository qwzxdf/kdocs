---
title: Special Cases
tags:
  - 描画
---

# Special Cases

**シャドウ マップは、不透明な立体には素直に使えますが、アルファ テストの葉・半透明のガラス・キャラクターの顔・遠景の雲など、そのままでは扱いにくい物**が**あります**。このセクションでは、**アルファ テストの影・半透明の影・ブロブ/平面投影の影・遠景の影・キャラクターの影と影の色**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **葉・柵のアルファ テスト**は**深度パスでも、切り抜く**。
    - **半透明の影**は**ステップリング（網点）**か**色付き影**で**近似**。
    - **安い影**：**ブロブ（丸い影）・平面投影**。
    - **遠景は**、**別の影**（**雲の影・距離でフェード**）。
    - **キャラクターは**、**専用の影の設定**（**顔・髪・肌**）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Alpha-Tested Shadows](alpha-test-shadows.md) | 葉・柵・金網の影 |
| [Translucent Shadows](translucent-shadows.md) | ガラス・水・煙の影 |
| [Blob and Planar Projected Shadows](blob-planar.md) | 安い影の技法 |
| [Distant Shadows](distant-shadows.md) | 雲の影・距離フェード |
| [Character Shadows and Color](character-shadows.md) | 顔・髪・肌・影の色と濃さ |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **特殊なケースは、専用の工夫で扱う**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadows](../index.md)
- [Shadow Map Basics](../shadow-map-basics/index.md)
