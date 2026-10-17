---
title: Terrain
tags:
  - 描画
---

# Terrain

**地形**は**ゲームの舞台の土台**です。**地平線まで続く広大な地面を、メモリと描画コストの範囲で、近くは細かく・遠くは粗く表現する**のが**中心の課題**です。このセクションでは、**高さマップからメッシュを作る方法**、<strong>距離に応じた細かさの切り替え（LOD）</strong>、**地面のテクスチャの重ね方**、**草や木の大量配置**、<strong>地形そのものの生成（ノイズ・侵食）</strong>を、順に説明します。

!!! tip "ポイント"
    - 地形 ＝ <strong>高さマップ（2D の高さの表）</strong>から作る<strong>起伏のある面</strong>。<strong>XZ は格子、Y が高さ</strong>。
    - <strong>広い地形は、遠くを粗く</strong>する（<strong>LOD</strong>）。<strong>近くは細かく、遠くは少ない三角形</strong>。
    - <strong>地面の見た目</strong>は<strong>複数のテクスチャ（草・土・岩・雪）を、重みマップで混ぜる</strong>（<strong>スプラット</strong>）。
    - <strong>急な斜面には、トライプラナー</strong>で<strong>テクスチャの引き伸ばしを防ぐ</strong>。
    - <strong>草・木</strong>は<strong>インスタンシング</strong>で<strong>大量に置き</strong>、<strong>距離でカリング・LOD</strong>。
    - <strong>地形の生成</strong>は<strong>ノイズ（fBm）</strong> ＋ <strong>侵食</strong>で<strong>自然な形</strong>にする。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Heightmaps and Meshes](heightmap-mesh/index.md) | 高さマップ・格子メッシュ・法線・高さの取得・チャンク |
| [LOD](lod/index.md) | クリップマップ・CDLOD・四分木・テッセレーション・継ぎ目 |
| [Terrain Texturing](texturing/index.md) | スプラット・トライプラナー・高さブレンド・仮想テクスチャ |
| [草と木](vegetation/index.md) | インスタンシング・カリング・風・ビルボード・LOD |
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

## 関連ページ

- [描画](../index.md)
- [Water](../water/index.md)
- [Shadows](../shadows/index.md)
- [描画最適化](../../rendering/index.md)
