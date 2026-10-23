---
title: 早見表：状態と入力
tags:
  - 外部ライブラリ
  - GUI
---

# 早見表：状態と入力

**直前の部品がどういう状態か**（ホバー・押された・フォーカス）を調べる関数とマウス・キーボードの入力を扱う関数です。ゲームに組み込むとき、最も重要なのは「ImGui がマウスを使っているか」の判定です（ゲーム側の入力と取り合いになるため）。

!!! tip "ポイント"
    - <strong>`IsItem…` 系は、「直前に描いた 1 つの部品」</strong>について答える。<strong>部品を描いた直後に呼ぶ</strong>。
    - `GetIO().WantCaptureMouse` が true の間は、ゲーム側でマウス入力を処理しない（キーボードは `WantCaptureKeyboard`）。
    - キー入力は `ImGuiKey_` 列挙（1.87 以降の新方式）。`IsKeyPressed`・`IsKeyDown`・`IsKeyReleased`。
    - `ImGuiIO` に、毎フレームの状態（FPS・マウス座標）が入っている。

## 直前の項目の状態

| 関数 | 内容 | 戻り値 |
| --- | --- | --- |
| `IsItemHovered(flags)` | **マウスが乗っているか** | `bool` |
| `IsItemActive()` | 操作中か（ボタンを押している・スライダーをドラッグ中） | `bool` |
| `IsItemFocused()` | キーボード フォーカスがあるか | `bool` |
| `IsItemClicked(button)` | クリックされたか（押した瞬間） | `bool` |
| `IsItemVisible()` | 画面に見えているか（スクロールで外れていないか） | `bool` |
| `IsItemEdited()` | 値が編集されたか | `bool` |
| `IsItemActivated()` | 操作が始まった瞬間 | `bool` |
| `IsItemDeactivated()` | 操作が終わった瞬間 | `bool` |
| `IsItemDeactivatedAfterEdit()` | 編集して、操作が終わった瞬間（Undo の登録に便利） | `bool` |
| `IsItemToggledOpen()` | ツリーが開閉された瞬間 | `bool` |
| `IsAnyItemHovered()` / `IsAnyItemActive()` / `IsAnyItemFocused()` | どれかの項目が… | `bool` |
| `GetItemRectMin()` / `GetItemRectMax()` / `GetItemRectSize()` | 直前の項目の矩形 | `ImVec2` |

```cpp
ImGui::DragFloat("Speed", &speed);
if (ImGui::IsItemHovered()) ImGui::SetTooltip("単位：m/秒");
if (ImGui::IsItemDeactivatedAfterEdit()) PushUndo();
```

| 状態 | 説明 |
| --- | --- |
| Hovered | マウスが乗っている |
| Active | ボタンが押されている間・ドラッグ中 |
| Focused | キーボード入力の対象（Tab・矢印で移動） |
| Edited | 値が変わった（そのフレーム） |

`IsItemDeactivatedAfterEdit` は、スライダーをドラッグしている間は false、離した瞬間に trueになるので、「編集が確定した」時点で、Undo 履歴に積むのにぴったりです。

## ウィンドウの状態

| 関数 | 内容 |
| --- | --- |
| `IsWindowHovered(flags)` | **現在のウィンドウにマウスが乗っているか** |
| `IsWindowFocused(flags)` | 現在のウィンドウがフォーカスされているか |
| `IsWindowCollapsed()` | 折りたたまれているか |
| `IsWindowAppearing()` | そのフレームでウィンドウが現れたか |
| `IsRectVisible(size)` | 矩形が見えているか |

## マウス

| 関数 | 内容 |
| --- | --- |
| `IsMouseClicked(button, repeat)` | **ボタンを押した瞬間** |
| `IsMouseDown(button)` | 押している間 |
| `IsMouseReleased(button)` | 離した瞬間 |
| `IsMouseDoubleClicked(button)` | ダブルクリック |
| `IsMouseDragging(button, threshold)` | ドラッグ中（しきい値を超えたか） |
| `GetMousePos()` | マウスの画面座標 |
| `GetMouseDragDelta(button)` | ドラッグ開始からの移動量 |
| `ResetMouseDragDelta(button)` | ドラッグ量をリセット |
| `IsMouseHoveringRect(min, max)` | 指定の矩形にマウスが乗っているか |
| `GetMouseCursor()` / `SetMouseCursor(cursor)` | カーソルの形（`ImGuiMouseCursor_Hand` など） |

ボタン番号：0 ＝ 左、1 ＝ 右、2 ＝ 中。

## キーボード

| 関数 | 内容 |
| --- | --- |
| `IsKeyPressed(key, repeat)` | **押した瞬間**（`repeat` で長押しのリピート） |
| `IsKeyDown(key)` | 押している間 |
| `IsKeyReleased(key)` | 離した瞬間 |
| `GetKeyName(key)` | キーの名前 |
| `Shortcut(key_chord, flags)` | ショートカット（`ImGuiMod_Ctrl \| ImGuiKey_S`）。1.89 以降 |
| `SetNextFrameWantCaptureKeyboard(b)` | 次フレームでキーボードを占有するか |

```cpp
if (ImGui::IsKeyPressed(ImGuiKey_Space)) Jump();
if (ImGui::Shortcut(ImGuiMod_Ctrl | ImGuiKey_S)) Save();
```

## ゲームとの入力の取り合い

**ImGui のウィンドウの上でクリックしたとき、ゲームのキャラクターが反応してはいけません**。`ImGuiIO` のフラグで判定します。

```cpp
ImGuiIO& io = ImGui::GetIO();
if (!io.WantCaptureMouse) {
  ProcessGameMouse();
}
if (!io.WantCaptureKeyboard) {
  ProcessGameKeyboard();
}
```

| フラグ | true になる条件 |
| --- | --- |
| `WantCaptureMouse` | マウスが ImGui のウィンドウ上にある／ImGui がドラッグ中 |
| `WantCaptureKeyboard` | `InputText` などが、フォーカスされている |
| `WantTextInput` | 文字入力が必要（IME・画面キーボードを出す合図） |
| `WantSetMousePos` | マウス カーソルを動かしたい（ゲームパッド ナビゲーション時） |

Win32 のメッセージ ループでは、`ImGui_ImplWin32_WndProcHandler` に先に渡すことで、入力が ImGui に届きます（[基礎](../basics.md)）。

## ImGuiIO（毎フレームの情報）

| メンバー | 内容 |
| --- | --- |
| `io.DeltaTime` | <strong>前フレームからの時間（秒）</strong>（自分で設定する場合もある） |
| `io.Framerate` | FPS（移動平均） |
| `io.DisplaySize` | 画面の大きさ |
| `io.MousePos` | マウス座標 |
| `io.MouseWheel` / `MouseWheelH` | ホイール（縦・横） |
| `io.ConfigFlags` | 設定フラグ（`NavEnableKeyboard`・`DockingEnable` など） |
| `io.IniFilename` | レイアウト保存ファイル（`nullptr` で保存しない） |
| `io.Fonts` | フォント アトラス |
| `io.FontGlobalScale` | 全体のフォント倍率 |
| `io.MetricsRenderVertices` / `MetricsRenderIndices` / `MetricsRenderWindows` | 描画した頂点・インデックス・ウィンドウの数 |

## 設定フラグ（ImGuiConfigFlags）

| フラグ | 内容 |
| --- | --- |
| `NavEnableKeyboard` | **キーボードで操作**（矢印・Tab・Enter） |
| `NavEnableGamepad` | ゲームパッドで操作 |
| `NoMouse` | マウスを無視 |
| `NoMouseCursorChange` | カーソル形状を変えない |
| `DockingEnable` | ドッキングを有効（docking ブランチ） |
| `ViewportsEnable` | ウィンドウを OS の外に出せる（マルチビューポート） |

```cpp
ImGuiIO& io = ImGui::GetIO();
io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;
```

## スタイルの読み書き

| 関数 | 内容 |
| --- | --- |
| `GetStyle()` | **`ImGuiStyle&`**（色・余白・丸み） |
| `StyleColorsDark()` / `StyleColorsLight()` / `StyleColorsClassic()` | 標準テーマを適用 |
| `GetStyleColorVec4(idx)` | ある色を取得 |
| `GetColorU32(idx / col)` | `ImU32`（描画リスト用の色）に変換 |
| `ShowStyleEditor()` | スタイル エディタを表示（調整に便利） |
| `ShowDemoWindow(&open)` | デモ ウィンドウ（全機能のサンプル） |
| `ShowMetricsWindow(&open)` | 内部の状態を表示（デバッグ） |
| `ShowDebugLogWindow(&open)` | ImGui 内部のログ |
| `ShowIDStackToolWindow(&open)` | ID スタックの確認 |

`ShowDemoWindow` は、ImGui に付属する、全機能のサンプルでソースが `imgui_demo.cpp`にあります。「あの部品、どう書くのか」は、まずここを見るのが最速です。

## ID・メモリ・文字

| 関数 | 内容 |
| --- | --- |
| `GetID(str)` | **ID を計算** |
| `GetStateStorage()` | ウィンドウごとのキー・値の保存領域 |
| `SetClipboardText(text)` / `GetClipboardText()` | クリップボード |
| `MemAlloc(size)` / `MemFree(ptr)` | ImGui のメモリ確保（アロケータ差し替え可） |
| `SetAllocatorFunctions(alloc, free, user)` | ImGui の確保・解放関数を設定 |
| `GetTime()` / `GetFrameCount()` | 経過時間・フレーム番号 |

## 関連ページ

- [関数早見表](index.md)
- [レイアウトとウィンドウ](layout.md)
- [描画（ImDrawList）](draw.md)
- [ゲームでのデバッグ画面](../debug-ui.md)
