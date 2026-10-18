---
title: Water
tags:
  - 描画
---

# Water

**水の表現**はゲームの絵作りの**見せ場**です。しかし、<strong>水は、「動く形（波）」・「透ける（屈折・吸収）」・「映す（反射・フレネル）」・「泡立つ（フォーム）」</strong>と、**いくつもの要素の重ね合わせ**です。**1 つの魔法の方法があるわけではなく、それぞれを分けて作って、足し合わせる**のが基本です。このセクションでは、<strong>波のジオメトリ（Gerstner・FFT）</strong>、<strong>シェーディング（フレネル・屈折・深度による色）</strong>、**岸辺の泡**、**波紋などのインタラクション**、<strong>水中の表現（コースティクス・霧）</strong>を、順に説明します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Water Waves](waves/index.md) | サイン波・Gerstner 波・FFT 海面・法線の計算 |
| [Water Shading](shading/index.md) | フレネル・屈折・水深による色・スペキュラ・SSS 風の色 |
| [Shore Foam](shore-foam/index.md) | 深度差による泡・波の頂点の泡・テクスチャ |
| [Water Interaction](interaction/index.md) | 高さマップのシミュレーション・フローマップ・ぶつかる物 |
| [Underwater Rendering](underwater/index.md) | 水中の霧・コースティクス・God Rays・水面の裏側 |

## 全体の構成

| 要素 | 担当する技術 |
| --- | --- |
| **大きな波の形** | **頂点シェーダー**で**メッシュを動かす**（Gerstner・FFT の高さ） |
| **細かい波の凹凸** | **法線マップを複数重ねて流す** |
| **映り込み** | **環境マップ・SSR・平面反射**（[Reflections](../reflections/index.md)） |
| **水中の見え方** | **屈折**（[Refraction](../translucency/refraction/index.md)） ＋ **深度による吸収** |
| **岸の泡** | **水深が浅い所**に**泡のテクスチャ** |
| **波紋・水しぶき** | **高さマップのシミュレーション・パーティクル** |

## 描画の順序

| 手順 | 内容 |
| --- | --- |
| **① 不透明を描く** | **地形・岩・水中の物** |
| **② 画面と深度をコピー** | **屈折の背景**・**水深の計算**に使う |
| **③ 水面を描く** | **屈折・反射・フレネル・泡**を**1 回のシェーダーで合成** |
| **④ 半透明・パーティクル** | **水しぶきなど** |

<strong>水面は、「不透明の後・コピーを取った後」</strong>に描きます（[Refraction](../translucency/refraction/index.md)と同じ構成）。

## 参考

- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（FFT による海面の合成。ほとんどの FFT 海面の、出発点）
- Finch, "Effective Water Simulation from Physical Models", GPU Gems, Chapter 1, 2004（サイン波と Gerstner 波の、GPU 実装）
- Vlachos, "Water Flow in Portal 2", SIGGRAPH 2010, Advances in Real-Time Rendering in 3D Graphics and Games
- Kerner, "Water Interaction Model for Boats in Video Games", Gamedeveloper.com (Gamasutra), 2015（船の浮力・抗力・水しぶき）

## 関連ページ

- [描画](../index.md)
- [Refraction](../translucency/refraction/index.md)
- [Reflections](../reflections/index.md)
- [Terrain](../terrain/index.md)
