---
title: 早見表：レイアウトとウィンドウ
tags:
  - 外部ライブラリ
  - GUI
---

# 早見表：レイアウトとウィンドウ

**ウィンドウを作る**・**部品を並べる**・**間隔や幅を決める**・**スクロールさせる**・**ID を管理する**関数です。<strong>ImGui のレイアウトは「カーソルが 1 つあり、部品を置くたびに下へ進む」</strong>という、**単純な規則**です。**この規則を関数でずらす**のが**レイアウトの全て**です。

!!! tip "ポイント"
    - <strong>カーソルが部品を置くたびに、1 行下へ進む</strong>。<strong>`SameLine` で同じ行に戻る</strong>。
    - <strong>`Begin` は、戻り値に関係なく必ず `End`</strong>。
    - <strong>幅は、`SetNextItemWidth`（次の 1 個）</strong>か<strong>`PushItemWidth`（Pop まで）</strong>。<strong>負の値は「右端から何ピクセル空けるか」</strong>。
    - <strong>ウィンドウの位置・大きさは、`SetNextWindow…` を、`Begin` の前に呼ぶ</strong>。
    - <strong>ID が重なる部品は、`PushID` / `##` で区別</strong>。

## ウィンドウ

| 関数 | 内容 | 閉じ方 |
| --- | --- | --- |
| `Begin(name, &open, flags)` | **ウィンドウを開く**（同じ名前は同じウィンドウ） | **常に `End()`** |
| `End()` | **ウィンドウを閉じる** | — |
| `SetNextWindowPos(pos, cond, pivot)` | **次のウィンドウの位置** | — |
| `SetNextWindowSize(size, cond)` | **次のウィンドウの大きさ** | — |
| `SetNextWindowSizeConstraints(min, max)` | **大きさの上限・下限** | — |
| `SetNextWindowContentSize(size)` | **中身の大きさ**（スクロール範囲） | — |
| `SetNextWindowCollapsed(b, cond)` | **折りたたみ状態** | — |
| `SetNextWindowFocus()` | **次のウィンドウを手前に** | — |
| `SetNextWindowBgAlpha(alpha)` | **背景の透明度** | — |
| `SetWindowPos/Size(...)` | **現在のウィンドウの位置・大きさ**（`Begin` の中で） | — |
| `GetWindowPos()` / `GetWindowSize()` | **位置・大きさを取得** | — |
| `GetContentRegionAvail()` | **残りの描ける領域** | — |
| `IsWindowFocused(flags)` / `IsWindowHovered(flags)` | **フォーカス・ホバー中か** | — |
| `GetMainViewport()` | **メイン ビューポート**（画面全体の情報） | — |

```cpp
ImGui::SetNextWindowPos(ImVec2(10, 10), ImGuiCond_FirstUseEver);
ImGui::SetNextWindowSize(ImVec2(300, 200), ImGuiCond_FirstUseEver);
if (ImGui::Begin("Inspector")) {
  ImGui::Text("Hello");
}
ImGui::End();
```

**`ImGuiCond_FirstUseEver`** は、<strong>「初回だけ」位置・大きさを決める</strong>指定です（**ユーザーが動かしたあとは、尊重**します）。

| `ImGuiCond_` | いつ設定するか |
| --- | --- |
| `Always` | **毎フレーム**（ユーザーの操作を上書き） |
| `Once` | **実行中の最初の 1 回だけ** |
| `FirstUseEver` | **`.ini` に記録がないとき**（初めて使うとき） |
| `Appearing` | **ウィンドウが出現したとき** |

## 子ウィンドウ（スクロール領域）

| 関数 | 内容 | 閉じ方 |
| --- | --- | --- |
| `BeginChild(id, size, child_flags, window_flags)` | **ウィンドウの中の独立した領域**（スクロール可） | **常に `EndChild()`** |
| `EndChild()` | **子ウィンドウを閉じる** | — |

```cpp
if (ImGui::BeginChild("Log", ImVec2(0, 150), ImGuiChildFlags_Borders)) {
  for (const auto& line : lines) ImGui::TextUnformatted(line.c_str());
  if (auto_scroll) ImGui::SetScrollHereY(1.0f);
}
ImGui::EndChild();
```

<strong>`size` の 0 は「残りを全部」</strong>、<strong>負の値は「端から何ピクセル空ける」</strong>です。

## 並べる

| 関数 | 内容 |
| --- | --- |
| `SameLine(offset, spacing)` | **次の部品を同じ行の右に置く** |
| `NewLine()` | **改行**（`SameLine` を解除） |
| `Separator()` | **区切り線** |
| `Spacing()` | **縦の余白** |
| `Dummy(size)` | **見えない領域**（場所取り） |
| `Indent(w)` / `Unindent(w)` | **インデントを増やす／戻す** |
| `BeginGroup()` / `EndGroup()` | **複数の部品を、1 つの塊として扱う**（`SameLine`・ホバー判定がまとめて効く） |
| `AlignTextToFramePadding()` | **文字の高さを入力欄に合わせる** |

```cpp
ImGui::Button("A");
ImGui::SameLine();
ImGui::Button("B");

ImGui::BeginGroup();
ImGui::Text("Left");
ImGui::Button("X");
ImGui::EndGroup();
ImGui::SameLine();
ImGui::BeginGroup();
ImGui::Text("Right");
ImGui::Button("Y");
ImGui::EndGroup();
```

## カーソルの直接操作

| 関数 | 内容 |
| --- | --- |
| `GetCursorPos()` / `SetCursorPos(pos)` | **ウィンドウ内の座標**でカーソルを読む／動かす |
| `GetCursorPosX/Y()` / `SetCursorPosX/Y(v)` | **X だけ・Y だけ** |
| `GetCursorScreenPos()` / `SetCursorScreenPos(pos)` | **画面全体の座標**で読む／動かす（**描画リストと同じ座標系**） |
| `GetCursorStartPos()` | **ウィンドウの描画開始位置** |

**`SetCursorPos`** は**ウィンドウの左上が原点**、**`SetCursorScreenPos`** は**画面の左上が原点**です。**`ImDrawList` に描くときは、画面座標**を使います。

## 幅・大きさ

| 関数 | 内容 |
| --- | --- |
| `SetNextItemWidth(w)` | **次の 1 個の部品の幅** |
| `PushItemWidth(w)` / `PopItemWidth()` | **Pop するまでの部品の幅** |
| `CalcItemWidth()` | **現在の部品の幅**を計算 |
| `CalcTextSize(text)` | **文字の大きさ**（幅・高さ） |
| `GetTextLineHeight()` | **1 行の高さ** |
| `GetTextLineHeightWithSpacing()` | **行間込みの高さ** |
| `GetFrameHeight()` | **入力欄の高さ** |
| `GetFontSize()` | **フォントの大きさ** |

| 幅の値 | 意味 |
| --- | --- |
| <strong>正（例 200）</strong> | **200 ピクセル** |
| **0** | **既定の幅**（ウィンドウ幅の約 65%） |
| <strong>負（例 -1）</strong> | **右端まで**（`-1` は余白なし。`-100` は右端から 100 空ける） |

```cpp
ImGui::SetNextItemWidth(-1);
ImGui::InputText("##filter", filter, sizeof(filter));

ImGui::SetNextItemWidth(120.0f);
ImGui::DragFloat("##x", &x);
```

## スクロール

| 関数 | 内容 |
| --- | --- |
| `GetScrollX/Y()` / `SetScrollX/Y(v)` | **スクロール位置を読む／設定** |
| `GetScrollMaxX/Y()` | **最大スクロール量** |
| `SetScrollHereY(ratio)` | **現在のカーソル位置が見える**ようスクロール（0 上端・0.5 中央・1 下端） |
| `SetScrollFromPosY(y, ratio)` | **指定位置が見える**ようスクロール |

**ログの自動スクロール**は、**`GetScrollY() >= GetScrollMaxY()`（最下端にいる）ときだけ `SetScrollHereY(1.0f)`**とすると**ユーザーが上へ遡っている間は、勝手に動かない**ので**親切**です。

## ID の管理

| 関数 | 内容 |
| --- | --- |
| `PushID(str / int / ptr)` / `PopID()` | **ID の階層を 1 つ積む／戻す** |
| `GetID(str)` | **現在の階層での ID** を計算 |
| `"label##id"` | **表示は `label`、ID は `label##id`** |
| `"##id"` | **ラベルを表示せず、ID だけ** |
| `"label###id"` | **ラベルが変わっても、ID を固定**（`###` 以降が ID） |

```cpp
for (int i = 0; i < count; ++i) {
  ImGui::PushID(i);
  ImGui::Button("Delete");
  ImGui::PopID();
}
```

**`PushID` を使わない**と、**同じ "Delete" ボタンが全部同じ ID**になり、**最初の 1 個しか反応しません**。

## スタイル・色の一時変更

| 関数 | 内容 |
| --- | --- |
| `PushStyleColor(idx, color)` / `PopStyleColor(n)` | **色を一時的に変える** |
| `PushStyleVar(idx, value)` / `PopStyleVar(n)` | **余白・丸みなどを一時的に変える** |
| `PushFont(font)` / `PopFont()` | **フォントを一時的に変える** |
| `PushItemFlag(flag, bool)` / `PopItemFlag()` | **項目のフラグを一時的に変える** |
| `BeginDisabled(bool)` / `EndDisabled()` | **まとめて灰色にして、操作を無効にする** |
| `PushTextWrapPos(x)` / `PopTextWrapPos()` | **折り返す位置** |

```cpp
ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.8f, 0.2f, 0.2f, 1.0f));
ImGui::Button("Danger");
ImGui::PopStyleColor();

ImGui::BeginDisabled(!can_save);
ImGui::Button("Save");
ImGui::EndDisabled();
```

**`Push` と `Pop` の個数は、必ず合わせます**（`PopStyleColor(2)` のようにまとめて Pop 可能）。

## 1 つの項目に付ける操作

| 関数 | 内容 |
| --- | --- |
| `SetItemDefaultFocus()` | **この項目に最初のフォーカス**（コンボの選択項目など） |
| `SetKeyboardFocusHere(offset)` | **次の項目にキーボード フォーカス**（`InputText` の自動選択） |
| `SetNextItemOpen(b, cond)` | **次のツリーの開閉** |
| `SetNextItemAllowOverlap()` | **次の項目の上に別の項目を重ねる** |
| `SetItemTooltip(...)` | **ツールチップ** |

## 関連ページ

- [関数早見表](index.md)
- [コンテナ](containers.md)
- [状態と入力](state-io.md)
- [レイアウトとウィンドウ（解説）](../layout.md)
