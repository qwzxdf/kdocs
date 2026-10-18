---
title: Translucency
tags:
  - 描画
---

# Translucency

**ガラス・水・煙・炎・葉っぱ・髪の毛**のように、**向こう側が透けて見える物**の描画は、**不透明な物とはまったく別の問題**です。**不透明な物は、深度バッファで「一番手前」を決めれば、描く順番は関係ありません**。**半透明は、色を混ぜ合わせる（ブレンド）ので、「どの順番で混ぜるか」で結果が変わります**。**描く順番が結果を左右する**ため、**ソート・OIT・アルファ テスト**といった、**専用の方法**が必要になります。

!!! tip "ポイント"
    - 半透明 ＝ <strong>背景と自分の色を、透明度（アルファ）で混ぜる</strong>。<strong>混ぜる順序で、結果が変わる</strong>。
    - <strong>奥から手前の順（Back-to-Front）</strong>に描くのが、<strong>正しい合成</strong>の基本。
    - <strong>深度は、読むが書かない</strong>（<strong>深度テスト ON・深度書き込み OFF</strong>）。
    - <strong>ソートは、オブジェクト単位</strong>。<strong>交差・自己重なり</strong>で<strong>破綻</strong>する。
    - <strong>アルファ テスト</strong>（<strong>捨てるか残すか</strong>）は、<strong>順序に依存しない</strong>。<strong>草・葉・金網</strong>向き。
    - <strong>OIT</strong>（Order-Independent Transparency）は、<strong>順序に依存せず</strong>半透明を合成する手法。
    - <strong>屈折</strong>は、<strong>背景を画像として取っておき、歪めて読む</strong>。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [ブレンドとソート](blending-sorting/index.md) | アルファ ブレンドの式・ブレンド ステート・ソートの方法と限界 |
| [Alpha Testing](alpha-test/index.md) | clip・Alpha to Coverage・ハッシュド アルファ・ミップの罠 |
| [OIT（順序非依存の半透明）](oit/index.md) | Weighted Blended・Depth Peeling・Per-Pixel Linked List・確率的 |
| [屈折とガラス](refraction/index.md) | 背景のコピー・歪み・厚み・色収差・フレネル |

## なぜ難しいのか

不透明と半透明の違いを整理します。不透明は、深度テストで一番手前だけが残り、描く順番が関係なく、深度バッファに書け、ライティングも画素ごとに 1 回で済み、ポストプロセスの対象も明確です。半透明は、すべての層が少しずつ寄与し、順番で色が変わり、深度は 1 つの値では表せず（層が複数）、ライティングは層ごとに計算が必要で、深度がないので DOF や SSAO などと相性が悪くなります。

## 描画の流れ（典型）

描画の流れ（典型）は 4 段階です。最初に不透明を描き、深度バッファに書きます。次に、アルファ テストの物を、不透明と同じパスで `clip` しながら描きます。その次に半透明を、深度を読むだけにして、奥から手前へ描きます。最後に、半透明も含めた画像にポストプロセス（トーンマップなど）をかけます。

**半透明は、不透明の後・ポストプロセスの前**に**描く**のが**基本**です。

## 関連ページ

- [描画](../index.md)
- [パーティクルの最適化](../../rendering/particles.md)
- [オーバードロー](../../rendering/overdraw.md)
- [Post-Processing](../postprocess/index.md)
