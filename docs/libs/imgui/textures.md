---
title: テクスチャと画像
tags:
  - 外部ライブラリ
  - GUI
---

# テクスチャと画像

!!! warning "TODO"
    このページは**構成だけ**を用意していて、内容はこれから書きます。

ゲームの画像や、レンダリング結果を ImGui のウィンドウに出す方法の説明です。

## これから書くこと

- `ImGui::Image` と `ImTextureID`
- DirectX 11 の Shader Resource View を渡す
- 画像ファイルの読み込み（stb_image）
- ゲームの画面をレンダー ターゲットに描いて、ウィンドウの中に出す（シーン ビュー）
- 画像ボタン、アイコン
- UV と、スプライト シート

## 関連ページ

- [Dear ImGui](index.md)
- [ImGuizmo](imguizmo.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
