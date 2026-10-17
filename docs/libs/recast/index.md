---
title: Recast & Detour
tags:
  - 外部ライブラリ
  - AI
---

# Recast & Detour

**Recast Navigation** は、ゲームの 3D 空間で、**キャラクターが歩ける場所（ナビゲーション メッシュ）を自動で作り、経路探索をする**ためのライブラリです。**Recast** がナビメッシュを**作る**側、**Detour** がナビメッシュの上で**経路を探す**側、**DetourCrowd** が**多数のエージェントを動かす**側です。Unreal Engine・Unity・Godot など、多くのエンジンの内部でも使われています。

!!! tip "ポイント"
    - <strong>Recast</strong> ＝ <strong>ワールドのメッシュから、ナビメッシュを作る</strong>（ビルド時または実行時）。
    - <strong>Detour</strong> ＝ <strong>ナビメッシュの上で、経路探索・位置の検索・レイ判定</strong>をする。
    - <strong>DetourCrowd</strong> ＝ <strong>多数のキャラの移動と、お互いの回避</strong>を管理する。
    - <strong>DetourTileCache</strong> ＝ <strong>動く障害物</strong>（ドア・バリケード）にナビメッシュを追従させる。
    - 入れ方は <strong>vcpkg</strong>（`recastnavigation`）か、ソースを入れる。
    - ナビメッシュは<strong>ビルド時に作って保存</strong>するのが基本。実行時は読み込むだけ。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [ナビメッシュとは](overview.md) | 考え方・経路探索との関係・ライブラリの構成・導入 |
| [Recast：ナビメッシュを作る](build.md) | 三角形から、ボクセル化 → 領域 → ポリゴンまでの工程と、設定値 |
| [Detour：経路を探す](query.md) | ナビメッシュの読み込み、最寄りの点・経路・直線化・レイ |
| [群衆と動的な障害物](crowd.md) | DetourCrowd・TileCache・オフメッシュ リンク・エリアと通行コスト |

## 関連ページ

- [外部ライブラリ](../index.md)
- [3D の衝突判定](../../3d/collision-3d.md)
- [ベイク](../../optimize/baking.md)
- [Jolt Physics](../jolt/index.md)
