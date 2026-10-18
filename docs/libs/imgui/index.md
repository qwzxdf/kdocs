---
title: Dear ImGui
tags:
  - 外部ライブラリ
  - GUI
---

# Dear ImGui

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11〜</span>
`#include "imgui.h"`
</div>

**Dear ImGui**（ディア・イムグイ）は、ゲームの**デバッグ画面**や**エディタ**を**とても少ないコードで作れる GUI ライブラリ**です。ボタンもスライダーも `if (ImGui::Button("Reset")) { ... }` のように**毎フレーム、関数を呼ぶだけ**で出せます。ウィンドウの部品を作って保持する、という普通の GUI の面倒さがありません。この仕組みを <strong>即時モード GUI（Immediate Mode GUI）</strong> と言います。ゲームのパラメータを実行中に変えるオブジェクトの一覧を出すフレーム時間のグラフを出す、といった用途でゲーム業界で広く使われています。ここからギズモ（[ImGuizmo](imguizmo.md)）、タイムライン（[ImSequencer](imsequencer.md)）、ノード エディタ（[imgui-node-editor](node-editor.md)）などの拡張ライブラリも広がっています。

## ページ一覧

**読む順番**：導入 → 仕組みと最小のコード → 部品・レイアウト → 見た目 → 応用。

| ページ | 内容 |
| --- | --- |
| [導入（Visual Studio）](install.md) | ソースを入れる・vcpkg・CMake での入れ方 |
| [仕組みと最小のコード](basics.md) | 即時モード、1 フレームの流れ DirectX 11 + Win32 の最小コード、よくあるミス |
| [DirectX 12 での初期化まとめ](dx12.md) | ディスクリプタ ヒープ・フレーム数・リサイズと終了の注意 |
| [ウィジェット一覧](widgets.md) | ボタン、スライダー、入力、リスト、コンボ、テーブル |
| [レイアウトとウィンドウ](layout.md) | 配置、`SameLine`、ウィンドウのフラグ、子ウィンドウ |
| [ドッキングとビューポート](docking.md) | ウィンドウのドッキング、ウィンドウをアプリの外に出す |
| [日本語フォントとアイコン](fonts.md) | 日本語の表示、アイコン フォント、フォントのサイズ |
| [スタイルとテーマ](style.md) | 色、角の丸み余白、ダーク / ライト |
| [テクスチャと画像](textures.md) | `ImGui::Image`、ゲームの画面をウィンドウの中に出す |
| [ゲームでのデバッグ画面](debug-ui.md) | フレーム時間のグラフ、ログ、エンティティのインスペクター |
| [ImGuizmo](imguizmo.md) | 3D のギズモ（移動・回転・拡大の矢印） |
| [ImSequencer](imsequencer.md) | タイムラインの編集 |
| [imgui-node-editor](node-editor.md) | ノード エディタ |
| [関数早見表](reference/index.md) | **関数と出てくる部品の一覧**。見た目のギャラリーと動きのアニメーション付き |

## 関連ページ

- [ImGuizmo](imguizmo.md)
- [ImSequencer](imsequencer.md)
- [imgui-node-editor](node-editor.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
- [Dear ImGui（GitHub）](https://github.com/ocornut/imgui)
- [ImGui の Wiki](https://github.com/ocornut/imgui/wiki)
