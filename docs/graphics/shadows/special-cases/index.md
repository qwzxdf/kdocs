---
title: Special Cases
tags:
  - 描画
---

# Special Cases

<strong>シャドウ マップは、不透明な立体には素直に使えますが、アルファ テストの葉・半透明のガラス・キャラクターの顔・遠景の雲など、そのままでは扱いにくい物</strong>が<strong>あります</strong>。このセクションでは、アルファ テストの影・半透明の影・ブロブ/平面投影の影・遠景の影・キャラクターの影と影の色を、1 つずつ別のページで説明します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Alpha-Tested Shadows](alpha-test-shadows.md) | 葉・柵・金網の影 |
| [Translucent Shadows](translucent-shadows.md) | ガラス・水・煙の影 |
| [Blob and Planar Projected Shadows](blob-planar.md) | 安い影の技法 |
| [Distant Shadows](distant-shadows.md) | 雲の影・距離フェード |
| [Character Shadows and Color](character-shadows.md) | 顔・髪・肌・影の色と濃さ |

## 特殊なケース：通常の、シャドウ マップでは、うまくいかない物

通常の、シャドウ マップは、<strong>不透明で、閉じた、メッシュ</strong>を、前提にしています。実際の、ゲームには、次のような、<strong>例外</strong>が、あります。

| ケース | 問題 | ページ |
| --- | --- | --- |
| アルファ テストの物（葉、柵、金網） | 透明部分も、影になる | [Alpha-Tested Shadows](alpha-test-shadows.md) |
| 半透明の物（ガラス、煙、色付きの窓） | 光を、一部、通す | [Translucent Shadows](translucent-shadows.md) |
| キャラクター | 小さな、動く物。接地と、自己影が、重要。色の、問題も | [Character Shadows and Color](character-shadows.md) |
| 遠景 | シャドウ マップの、範囲外。遠くの影を、どう、扱うか | [Distant Shadows](distant-shadows.md) |
| 簡易な影（接地、軽量） | シャドウ マップが、重すぎる、要らない | [Blob and Planar Projected Shadows](blob-planar.md) |

## 共通の、考え方

| 考え方 | 内容 |
| --- | --- |
| 影の目的を、考える | その影は、何のためか。物が、地面に、接していることを、示す（接地感）のか、光の方向を、見せるのか、雰囲気か |
| 物ごとに、方法を、変える | 主役（キャラクター）には、高品質。背景には、簡易 |
| 見えない、差は、省く | 遠く、小さい、暗い影は、簡易な方法で、十分。本物のシャドウ マップを、使わない |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 特殊なケースは、専用の工夫で扱う

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Blinn, "Me and My (Fake) Shadow", IEEE Computer Graphics and Applications, Vol. 8, No. 1, 1988（平面への、投影影）
- Lokovic, Veach, "Deep Shadow Maps", SIGGRAPH 2000（半透明の、影）
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017

## 関連ページ

- [Shadows](../index.md)
- [Shadow Map Basics](../shadow-map-basics/index.md)
