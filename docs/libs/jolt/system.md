---
title: 世界の初期化と更新
tags:
  - 外部ライブラリ
  - 物理演算
---

# 世界の初期化と更新

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

`PhysicsSystem` の作り方と、時間の進め方の説明です。

## これから書くこと

- `PhysicsSystem::Init` の引数（最大の物体数、ペア数、接触数）
- `TempAllocatorImpl` と `JobSystemThreadPool` の大きさ
- `Update(dt, collision_steps, ...)` の引数の意味
- 固定ステップと、可変フレームレートの扱い
- `OptimizeBroadPhase` を呼ぶタイミング
- 重力の設定（`SetGravity`）
- 物理の設定（`PhysicsSettings`）

## 関連ページ

- [Jolt Physics](index.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
