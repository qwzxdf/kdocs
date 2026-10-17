---
title: レイアウトとウィンドウ
tags:
  - 外部ライブラリ
  - GUI
---

# レイアウトとウィンドウ

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

ウィジェットの並べ方と、ウィンドウの作り方を説明するページです。

## これから書くこと

- ウィンドウの位置と大きさ（`SetNextWindowPos`、`SetNextWindowSize`、初回だけの `ImGuiCond_FirstUseEver`）
- ウィンドウのフラグ（`NoTitleBar`、`NoMove`、`AlwaysAutoResize` など）
- 並べ方（`SameLine`、`Separator`、`Spacing`、`Indent`）
- 列と表（`Columns`、`BeginTable`）
- 子ウィンドウ（`BeginChild`）とスクロール
- ID の管理（`PushID`、`##`、`###`）
- メインメニュー バー、ステータス バー

## 関連ページ

- [Dear ImGui](index.md)
- [ImGuizmo](imguizmo.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
