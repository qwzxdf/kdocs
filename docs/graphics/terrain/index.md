---
title: Terrain
tags:
  - 描画
---

# Terrain

**地形**は**ゲームの舞台の土台**です。**地平線まで続く広大な地面を、メモリと描画コストの範囲で、近くは細かく・遠くは粗く表現する**のが**中心の課題**です。このセクションでは、**高さマップからメッシュを作る方法**、<strong>距離に応じた細かさの切り替え（LOD）</strong>、**地面のテクスチャの重ね方**、**草や木の大量配置**、<strong>地形そのものの生成（ノイズ・侵食）</strong>を、順に説明します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Heightmaps and Meshes](heightmap-mesh/index.md) | 高さマップ・格子メッシュ・法線・高さの取得・チャンク |
| [LOD](lod/index.md) | クリップマップ・CDLOD・四分木・テッセレーション・継ぎ目 |
| [Terrain Texturing](texturing/index.md) | スプラット・トライプラナー・高さブレンド・仮想テクスチャ |
| [Vegetation](vegetation/index.md) | インスタンシング・カリング・風・ビルボード・LOD |
| [Terrain Generation](generation/index.md) | ノイズ・fBm・侵食・川・手続き的な配置 |

## 全体の構成

| 要素 | 担当する技術 |
| --- | --- |
| **形** | **高さマップ**（ファイルまたは生成）。**メッシュ化** |
| **細かさの制御** | **LOD**（距離で三角形の数を変える） |
| **見た目** | **スプラット マップ ＋ 複数のテクスチャ ＋ 法線マップ** |
| **植生** | **インスタンシング ＋ カリング ＋ 風** |
| **光** | **影・AO・GI**（[Shadows](../shadows/index.md)・[AO](../ao/index.md)） |
| **水** | **湖・海・川**（[Water](../water/index.md)） |
| **当たり判定** | **高さマップから直接、地面の高さを引く** |

## 地形データの規模

**地形は非常にデータが大きい**です。**規模の感覚**です。

| サイズ | 高さマップの解像度 | 16 ビットのメモリ |
| --- | --- | --- |
| **1 km 四方、1 m 刻み** | 1024×1024 | 約 2 MB |
| **4 km 四方、1 m 刻み** | 4096×4096 | 約 32 MB |
| **16 km 四方、1 m 刻み** | 16384×16384 | 約 512 MB |

**高さマップだけでも大きい**ので、**ストリーミング**（近くだけ読み込む）や**圧縮**が必要になります。**テクスチャ（色・法線・素材）は、さらに桁違いに大きい**ので、**重ねて使い回す**（スプラット）か、**必要な部分だけ読む**（仮想テクスチャ）工夫が要ります。

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009
- Ebert, Musgrave, Peachey, Perlin, Worley, "Texturing and Modeling: A Procedural Approach", 3rd Edition, Morgan Kaufmann, 2002
- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007（幹・枝・葉の 3 層の揺れ、葉の透過）

## 関連ページ

- [描画](../index.md)
- [Water](../water/index.md)
- [Shadows](../shadows/index.md)
- [描画最適化](../../rendering/index.md)
