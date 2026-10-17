---
title: 物体（Body）
tags:
  - 外部ライブラリ
  - 物理演算
---

# 物体（Body）

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

物体の作成と操作の説明です。

## これから書くこと

- `BodyCreationSettings` の項目（位置、向き、動き方、レイヤー、質量、摩擦、反発）
- `BodyInterface` の関数（`CreateBody`、`AddBody`、`RemoveBody`、`DestroyBody`）
- 力・衝撃・速度（`AddForce`、`AddImpulse`、`SetLinearVelocity`）
- キネマティックな物体の動かし方（`MoveKinematic`）
- スリープ（休止）と、`ActivateBody`
- センサー（衝突はせず、重なりだけ知る）
- 接触リスナー（衝突の通知）

## 関連ページ

- [Jolt Physics](index.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
