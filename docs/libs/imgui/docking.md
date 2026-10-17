---
title: ドッキングとビューポート
tags:
  - 外部ライブラリ
  - GUI
---

# ドッキングとビューポート

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

ウィンドウをタブのように重ねたり、アプリの外に出したりする機能の説明です。

## これから書くこと

- ドッキング ブランチと、`ImGuiConfigFlags_DockingEnable` の有効化
- `DockSpace` で、メイン ウィンドウ全体をドッキング領域にする
- レイアウトの保存と読み込み（`imgui.ini`）
- マルチ ビューポート（ウィンドウをアプリの外に出す）
- ゲームの画面を、ドッキングできるウィンドウの中に出す方法
- vcpkg の `docking-experimental` 機能

## 関連ページ

- [Dear ImGui](index.md)
- [ImGuizmo](imguizmo.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
