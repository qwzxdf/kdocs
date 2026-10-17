---
title: レイヤー
tags:
  - 外部ライブラリ
  - 物理演算
---

# レイヤー

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

「何と何が衝突するか」を決めるレイヤーの作り方の説明です。

## これから書くこと

- `ObjectLayer` と `BroadPhaseLayer` の違い
- `BroadPhaseLayerInterface`、`ObjectVsBroadPhaseLayerFilter`、`ObjectLayerPairFilter` の書き方
- 最小の例（`NON_MOVING` と `MOVING`）
- ゲーム向けの設計（プレイヤー、敵、弾、地形、トリガー）
- レイヤー・マスクとの組み合わせ（ビット フラグ）

## 関連ページ

- [Jolt Physics](index.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
