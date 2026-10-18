---
title: Special Cases
tags:
  - 描画
---

# Special Cases

<strong>シャドウ マップは不透明な立体には素直に使えますが、アルファ テストの葉・半透明のガラス・キャラクターの顔・遠景の雲など、そのままでは扱いにくい物</strong>が<strong>あります</strong>。このセクションではアルファ テストの影・半透明の影・ブロブ/平面投影の影・遠景の影・キャラクターの影と影の色を、1 つずつ別のページで説明します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Alpha-Tested Shadows](alpha-test-shadows.md) | 葉・柵・金網の影 |
| [Translucent Shadows](translucent-shadows.md) | ガラス・水・煙の影 |
| [Blob and Planar Projected Shadows](blob-planar.md) | 安い影の技法 |
| [Distant Shadows](distant-shadows.md) | 雲の影・距離フェード |
| [Character Shadows and Color](character-shadows.md) | 顔・髪・肌・影の色と濃さ |

## 特殊なケース：通常のシャドウ マップでは、うまくいかない物

通常の、シャドウ マップは <strong>不透明で閉じた、メッシュ</strong>を前提にしています。実際の、ゲームには次のような <strong>例外</strong>が、あります。

| ケース | 問題 | ページ |
| --- | --- | --- |
| アルファ テストの物（葉、柵、金網） | 透明部分も影になる | [Alpha-Tested Shadows](alpha-test-shadows.md) |
| 半透明の物（ガラス、煙、色付きの窓） | 光を一部、通す | [Translucent Shadows](translucent-shadows.md) |
| キャラクター | 小さな、動く物。接地と自己影が重要。色の問題も | [Character Shadows and Color](character-shadows.md) |
| 遠景 | シャドウ マップの、範囲外。遠くの影をどう扱うか | [Distant Shadows](distant-shadows.md) |
| 簡易な影（接地、軽量） | シャドウ マップが、重すぎる要らない | [Blob and Planar Projected Shadows](blob-planar.md) |

## 共通の考え方

| 考え方 | 内容 |
| --- | --- |
| 影の目的を考える | その影は、何のためか。物が地面に接していることを示す（接地感）のか、光の方向を見せるのか雰囲気か |
| 物ごとに方法を変える | 主役（キャラクター）には、高品質。背景には簡易 |
| 見えない差は省く | 遠く小さい、暗い影は簡易な方法で十分。本物のシャドウ マップを使わない |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 特殊なケースは、専用の工夫で扱う

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Blinn, "Me and My (Fake) Shadow", IEEE Computer Graphics and Applications, Vol. 8, No. 1, 1988（平面への、投影影）
- Lokovic, Veach, "Deep Shadow Maps", SIGGRAPH 2000（半透明の影）
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017

## 関連ページ

- [Shadows](../index.md)
- [Shadow Map Basics](../shadow-map-basics/index.md)
