---
title: Global Illumination (GI)
tags:
  - 描画
---

# Global Illumination (GI)

光源から出た光は、**面に当たって反射し、別の面を照らします**。この<strong>跳ね返った光（間接光）</strong>まで含めて計算することを、**グローバル イルミネーション**（**GI**、大域照明）と呼びます。**赤い壁の隣の白い床がほんのり赤くなる**（カラー ブリーディング）、**日陰でも真っ暗にならない**といった現実感は、**間接光**が作ります。しかし、<strong>直接光（光源 → 面 → 目）</strong>と違い、**間接光はシーン全体が互いに影響し合う**ため、**リアルタイムで正確に解くのは非常に難しい**問題です。このセクションでは、<strong>「何を解いているのか」</strong>から、**ライトマップ・プローブ・SSGI・ボクセル・DDGI・レイトレ**まで**方式ごとの発想とトレードオフ**を説明します。

!!! tip "ポイント"
    - GI ＝ <strong>面から面へ跳ね返る光</strong>（レンダリング方程式の再帰的な部分）。
    - 直接光は<strong>局所</strong>、間接光は<strong>大域</strong>（シーン全体が関わる）。だから難しい。
    - 手法は<strong>「いつ計算するか」</strong>で分かれる：<strong>事前（ベイク）</strong>・<strong>準動的（プローブ）</strong>・<strong>完全動的（SSGI・ボクセル・RT）</strong>。
    - 保存先は<strong>「どこに情報を持つか」</strong>で分かれる：<strong>テクスチャ（ライトマップ）</strong>・<strong>空間の点（プローブ）</strong>・<strong>画面</strong>・<strong>ボクセル</strong>。
    - <strong>拡散反射の間接光</strong>は低周波（なめらか）なので<strong>粗く保存</strong>できる（球面調和関数など）。
    - <strong>正解はない</strong>。<strong>静的か・動的か・ハードウェア</strong>で選ぶ。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [GI Theory](theory/index.md) | レンダリング方程式・拡散/鏡面の間接光・放射照度・SH・モンテカルロ |
| [Lightmaps](lightmaps/index.md) | 事前計算して、テクスチャに焼く。UV・ベイク・方向情報 |
| [ライト プローブ](probes/index.md) | 空間の点に放射照度を保存。SH・補間・動的物体への適用 |
| [SSGI](ssgi.md) | 画面空間で近くの面からの跳ね返りを拾う |
| [Voxel GI](voxel-gi.md) | シーンをボクセル化し、コーン トレースで間接光を得る |
| [DDGI](ddgi.md) | レイトレで更新する動的プローブ。可視性の扱い |
| [レイトレ GI・Radiance Cascades](rt-gi/index.md) | パス トレース的な GI・ReSTIR・Lumen 系の考え方 |
| [GI Comparison](comparison.md) | 方式の選び方・組み合わせ |

## 読む順序

**理論 → ライトマップ → プローブ**が、**基本**です。その後、**SSGI・ボクセル・DDGI・レイトレ**は**必要なものから**読んで構いません。

## 関連ページ

- [描画](../index.md)
- [Ambient Occlusion (AO)](../ao/index.md)
- [Reflections](../reflections/index.md)
- [Shadows](../shadows/index.md)
