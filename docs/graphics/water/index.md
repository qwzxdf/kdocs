---
title: Water
tags:
  - 描画
---

# Water

**水の表現**はゲームの絵作りの**見せ場**です。しかし、<strong>水は、「動く形（波）」・「透ける（屈折・吸収）」・「映す（反射・フレネル）」・「泡立つ（フォーム）」</strong>と、**いくつもの要素の重ね合わせ**です。**1 つの魔法の方法があるわけではなく、それぞれを分けて作って、足し合わせる**のが基本です。このセクションでは、<strong>波のジオメトリ（Gerstner・FFT）</strong>、<strong>シェーディング（フレネル・屈折・深度による色）</strong>、**岸辺の泡**、**波紋などのインタラクション**、<strong>水中の表現（コースティクス・霧）</strong>を、順に説明します。

!!! tip "ポイント"
    - 水 ＝ <strong>波（形）</strong> ＋ <strong>シェーディング（反射・屈折・色）</strong> ＋ <strong>泡・波紋（細部）</strong>。
    - <strong>波</strong>は<strong>サイン波の重ね合わせ</strong>（Gerstner）か、<strong>周波数空間から作る（FFT）</strong>。
    - <strong>見た目の大半は、フレネルで決まる</strong>：<strong>浅い角度は反射、深い角度は透過</strong>。
    - <strong>水深（水面と底の深度差）</strong>から、<strong>色・透明度・岸の泡</strong>を<strong>決める</strong>。
    - <strong>法線の細かい動き（法線マップの重ね）</strong>で、<strong>ジオメトリが粗くても細かい波に見せる</strong>。
    - <strong>水は半透明・屈折・反射・深度を全部使う</strong>ので<strong>描画パイプラインの中で、特殊な位置</strong>に置く。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [波のジオメトリ](waves/index.md) | サイン波・Gerstner 波・FFT 海面・法線の計算 |
| [水のシェーディング](shading/index.md) | フレネル・屈折・水深による色・スペキュラ・SSS 風の色 |
| [岸辺と泡（フォーム）](shore-foam/index.md) | 深度差による泡・波の頂点の泡・テクスチャ |
| [波紋と水面のインタラクション](interaction/index.md) | 高さマップのシミュレーション・フローマップ・ぶつかる物 |
| [Underwater Rendering](underwater/index.md) | 水中の霧・コースティクス・光の筋・水面の裏側 |

## 全体の構成

水の見た目は、複数の技術の組み合わせです。大きな波の形は、頂点シェーダーでメッシュを動かして作ります（Gerstner 波や FFT の高さ）。細かい波の凹凸は、法線マップを複数重ねて流します。映り込みは、環境マップ・SSR・平面反射が担当します（[Reflections](../reflections/index.md)）。水中の見え方は、屈折（[Refraction](../translucency/refraction/index.md)）と深度による吸収で表します。岸の泡は、水深が浅い所に泡のテクスチャを置きます。波紋や水しぶきは、高さマップのシミュレーションやパーティクルで作ります。

## 描画の順序

描画の順序は 4 段階です。最初に、地形・岩・水中の物など不透明を描きます。次に、屈折の背景と水深の計算に使うため、画面と深度をコピーします。水面を描くときは、屈折・反射・フレネル・泡を 1 回のシェーダーで合成します。最後に、水しぶきなどの半透明やパーティクルを描きます。

<strong>水面は、「不透明の後・コピーを取った後」</strong>に描きます（[Refraction](../translucency/refraction/index.md)と同じ構成）。

## 関連ページ

- [描画](../index.md)
- [屈折とガラス](../translucency/refraction/index.md)
- [Reflections](../reflections/index.md)
- [Terrain](../terrain/index.md)
