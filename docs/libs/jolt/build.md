---
title: Jolt のビルドと設定
tags:
  - 外部ライブラリ
  - 物理演算
---

# Jolt のビルドと設定

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

Jolt を、自分のプロジェクトでビルドするときの設定の説明です。

## これから書くこと

- プリプロセッサの定義の一覧と意味（`JPH_DEBUG_RENDERER`、`JPH_PROFILE_ENABLED`、`JPH_DOUBLE_PRECISION` など）
- Debug / Release で定義がずれたときの症状
- vcpkg でのビルドと、CMake（FetchContent）でのビルドの違い
- ランタイム ライブラリ（/MD と /MT）
- 決定性（クロスプラットフォームで同じ結果にする設定）
- SIMD の設定（AVX2、SSE4.2 など）

## 関連ページ

- [Jolt Physics](index.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
