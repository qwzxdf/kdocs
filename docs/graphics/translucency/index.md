---
title: Translucency
tags:
  - 描画
---

# Translucency

<strong>ガラス・水・煙・炎・葉っぱ・髪の毛</strong>のように、<strong>向こう側が透けて見える物</strong>の描画は、不透明な物とはまったく別の問題です。不透明な物は、深度バッファで「一番手前」を決めれば、描く順番は関係ありません。半透明は、色を混ぜ合わせる（ブレンド）ので、「どの順番で混ぜるか」で結果が変わります。描く順番が結果を左右するため、ソート・OIT・アルファ テストといった、専用の方法が必要になります。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Alpha Blending and Sorting](blending-sorting/index.md) | アルファ ブレンドの式・ブレンド ステート・ソートの方法と限界 |
| [Alpha Testing](alpha-test/index.md) | clip・Alpha to Coverage・ハッシュド アルファ・ミップの罠 |
| [Order-Independent Transparency (OIT)](oit/index.md) | Weighted Blended・Depth Peeling・Per-Pixel Linked List・確率的 |
| [Refraction](refraction/index.md) | 背景のコピー・歪み・厚み・色収差・フレネル |

## なぜ難しいのか

| 不透明 | 半透明 |
| --- | --- |
| 深度テストで、一番手前だけが残る | すべての層が少しずつ寄与する |
| 描く順番は、関係ない | 順番で、色が変わる |
| 深度バッファに書ける | 深度は、1 つの値では表せない（層が複数） |
| ライティングは、画素ごとに 1 回 | 層ごとに計算が必要 |
| ポストプロセスの対象が明確 | 深度がないので、DOF・SSAO などと相性が悪い |

## 描画の流れ（典型）

| 順序 | 内容 |
| --- | --- |
| ① 不透明 | 深度バッファに書きながら描く |
| ② アルファ テスト | 不透明と同じパスで、`clip` しながら描く |
| ③ 半透明 | 深度は読むだけ。奥から手前へ描く |
| ④ ポストプロセス | 半透明も含めた画像にトーンマップなど |

<strong>半透明は、不透明の後・ポストプロセスの前</strong>に<strong>描く</strong>のが基本です。

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（屈折、フレネル、透過の章）
- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005
- McGuire, Bavoil, "Weighted Blended Order-Independent Transparency", Journal of Computer Graphics Techniques, Vol. 2, No. 2, 2013
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017

## 関連ページ

- [シェーダー](../index.md)
- [パーティクルと半透明](../../rendering/particles.md)
- [オーバードロー](../../rendering/overdraw.md)
- [Post-Processing](../postprocess/index.md)
- [描画最適化](../../rendering/index.md)
