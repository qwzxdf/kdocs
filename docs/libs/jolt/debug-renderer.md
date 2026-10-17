---
title: デバッグ描画
tags:
  - 外部ライブラリ
  - 物理演算
---

# デバッグ描画

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

物理の形を、画面に線で出して確認する方法の説明です。

## これから書くこと

- `JPH_DEBUG_RENDERER` の有効化
- `DebugRenderer` を継承して、自分の描画（DirectX など）につなぐ
- `PhysicsSystem::DrawBodies`、`DrawConstraints`
- [Dear ImGui](../imgui/index.md) のデバッグ画面との組み合わせ
- Release で無効にする方法

## 関連ページ

- [Jolt Physics](index.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
