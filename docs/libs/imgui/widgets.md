---
title: ImGui のウィジェット一覧
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のウィジェット一覧

ImGui の<strong>部品（ウィジェット）</strong>は、**関数を 1 回呼ぶだけ**で、画面に出て、**操作の結果が戻り値と、渡した変数に返ってきます**（[即時モード](index.md)）。このページは、**よく使う部品**を、**種類ごとに、使い方と戻り値**で説明します。**部品の「ラベル」が ID を兼ねる**ことと、**`Begin` と `End` の対応**が、最初の落とし穴です。

!!! tip "ポイント"
    - 部品は<strong>「描く」と「入力を受け取る」を、1 回の関数呼び出し</strong>で行う。<strong>戻り値 ＝ 今フレームで、変更・クリックされたか</strong>。
    - 値は<strong>ポインタ（`float*`、`bool*`）で渡す</strong>。ImGui が、その変数を直接書き換える。
    - <strong>ラベル（文字列）が、部品の ID</strong>。<strong>同じラベルが 2 つあると、同じ部品として扱われる</strong>（`##` で、見えない ID を付ける）。
    - <strong>`Begin...` が `true` を返したときだけ、`End...` を呼ぶ</strong>もの（`BeginCombo`、`BeginTable` など）と、<strong>常に `End` を呼ぶ</strong>もの（`Begin` / `End`）がある。
    - <strong>数値の調整は、`Drag`（ドラッグで増減）が便利</strong>。<strong>範囲があるなら `Slider`</strong>。
    - <strong>`std::string` を `InputText` に渡すには、`imgui_stdlib.h`</strong>。

## 基本の考え方

```cpp
static float speed = 3.0f;
static bool godmode = false;

ImGui::Begin("デバッグ");

if (ImGui::Button("リセット")) {
  Reset();
}
ImGui::SliderFloat("速さ", &speed, 0.0f, 10.0f);
ImGui::Checkbox("無敵", &godmode);

ImGui::End();
```

| 点 | 説明 |
| --- | --- |
| **`ImGui::Button(...)`** | **クリックされたフレームだけ `true`** を返す |
| **`ImGui::SliderFloat(..., &speed, ...)`** | **変更されたフレームだけ `true`**。**`speed` が、直接書き換わる** |
| **`static` や、メンバ変数** | **値を、フレームをまたいで持つ**必要がある（ローカル変数は、毎フレーム初期化される） |
| **`Begin` / `End`** | **ウィンドウを作る**。`End` は、`Begin` の戻り値に**関係なく**必ず呼ぶ |

## テキスト

| 関数 | 用途 |
| --- | --- |
| **`Text(fmt, ...)`** | 文字を表示（`printf` 形式：`"%d"`、`"%.2f"`） |
| **`TextColored(ImVec4, fmt, ...)`** | **色付き**の文字 |
| **`TextDisabled(fmt, ...)`** | **薄い色**（無効に見える） |
| **`TextWrapped(fmt, ...)`** | **ウィンドウの幅で、折り返す** |
| **`TextUnformatted(str)`** | **書式なし**で、そのまま表示（**`%` を含む文字列に安全。速い**） |
| **`LabelText(label, fmt, ...)`** | **左に値、右にラベル**（読み取り専用の項目） |
| **`BulletText(fmt, ...)`** | **箇条書きの点**付き |
| **`SeparatorText("見出し")`** | **見出し付きの区切り線**（1.89 以降） |

```cpp
ImGui::Text("HP: %d / %d", hp, max_hp);
ImGui::TextColored(ImVec4(1, 0.3f, 0.3f, 1), "警告: 残りわずか");
ImGui::TextUnformatted(log_line.c_str());
```

!!! warning "ユーザーの文字列を、そのまま `Text` に渡さない"
    **`ImGui::Text(user_string)`** は、**`%` を書式として解釈**して、**クラッシュ**します。**`TextUnformatted`**、または **`Text("%s", str)`** にします。

## ボタンと選択

| 関数 | 戻り値 | 用途 |
| --- | --- | --- |
| **`Button("ラベル", ImVec2(w, h))`** | クリックで `true` | 普通のボタン |
| `SmallButton("ラベル")` | 同上 | **小さなボタン**（文章の中に入れる） |
| **`Checkbox("ラベル", &flag)`** | 変更で `true` | **オン・オフ** |
| **`RadioButton("ラベル", &value, 番号)`** | 選択で `true` | **複数の中から 1 つ**（同じ `value` に、番号違いで並べる） |
| **`Selectable("ラベル", selected)`** | クリックで `true` | **リストの項目**（選択状態の見た目） |
| `ArrowButton("##id", ImGuiDir_Left)` | クリックで `true` | **矢印ボタン** |

```cpp
static int mode = 0;
ImGui::RadioButton("移動", &mode, 0);
ImGui::SameLine();
ImGui::RadioButton("回転", &mode, 1);
ImGui::SameLine();
ImGui::RadioButton("拡大", &mode, 2);

for (int i = 0; i < items.size(); ++i) {
  if (ImGui::Selectable(items[i].name.c_str(), selected_index == i)) {
    selected_index = i;
  }
}
```

## 数値の入力

| 関数 | 操作 | 向く場面 |
| --- | --- | --- |
| **`SliderFloat("ラベル", &v, min, max, "%.2f")`** | **つまみを動かす** | **範囲がある**値（0〜1、角度） |
| `SliderInt` / `SliderAngle` | 同上（整数／**度で表示、ラジアンで保持**） | 整数・角度 |
| **`DragFloat("ラベル", &v, 速さ, min, max)`** | **ドラッグで増減**（ダブルクリックで直接入力） | **範囲が広い・不明**な値。**調整に最も使う** |
| `DragFloat3("ラベル", &v.x)` / `SliderFloat3` | **3 つ**まとめて | **位置・回転・拡大**（`Vector3`） |
| **`InputFloat` / `InputInt`** | **キーボードで入力**（+/- ボタン） | **正確な値** |
| `InputFloat3("ラベル", &v.x)` | 3 つ | |

```cpp
ImGui::DragFloat3("位置", &transform.position.x, 0.1f);
ImGui::DragFloat3("回転", &euler.x, 1.0f, -180.0f, 180.0f);
ImGui::SliderFloat("FOV", &camera.fov, 30.0f, 120.0f, "%.0f 度");
```

| 点 | 説明 |
| --- | --- |
| **書式文字列**（`"%.2f"`） | **表示の桁数・単位**を決める |
| **`ImGuiSliderFlags_Logarithmic`** | **対数スケール**（広い範囲の値に） |
| **`&v.x`** | **`Vector3` の先頭**（3 つの `float` が、連続して並んでいる前提） |
| **ダブルクリック / Ctrl + クリック** | **スライダーに、直接数値を入力**できる |

## 文字の入力

```cpp
static char name[64] = "";
ImGui::InputText("名前", name, sizeof(name));
```

| 関数 | 用途 |
| --- | --- |
| **`InputText(label, char* buf, size, flags)`** | **1 行の文字入力<strong>。</strong>バッファの大きさを渡す** |
| `InputTextMultiline(label, buf, size, ImVec2)` | **複数行** |
| `InputTextWithHint(label, hint, buf, size)` | **薄い説明文（ヒント）付き** |

### std::string で使う

**固定長の `char` 配列**は不便です。**`misc/cpp/imgui_stdlib.h`**（ImGui に同梱）を include すれば、**`std::string`** を、そのまま渡せます。

```cpp
#include "misc/cpp/imgui_stdlib.h"

static std::string name;
ImGui::InputText("名前", &name);
```

| フラグ | 意味 |
| --- | --- |
| `ImGuiInputTextFlags_EnterReturnsTrue` | **Enter を押したときだけ `true`** を返す |
| `ImGuiInputTextFlags_ReadOnly` | **読み取り専用** |
| `ImGuiInputTextFlags_Password` | 入力を、`*` で隠す |
| `ImGuiInputTextFlags_CharsDecimal` | **数字だけ**を入力できる |

## 色

| 関数 | 用途 |
| --- | --- |
| **`ColorEdit3("ラベル", &color.x)`** | **色の編集**（小さな色見本 + 数値。クリックでピッカー） |
| `ColorEdit4` | **アルファ付き** |
| `ColorPicker4("ラベル", &color.x)` | **大きな色のピッカー**を、直接表示 |
| `ColorButton("##id", ImVec4)` | **色のボタン**（押せる色見本） |

```cpp
ImGui::ColorEdit3("ライトの色", &light.color.x);
```

## リストとコンボボックス

### Combo

```cpp
static int current = 0;
const char* items[] = {"スライム", "ゴブリン", "ドラゴン"};
ImGui::Combo("敵の種類", &current, items, IM_ARRAYSIZE(items));
```

**項目を動的に作る**ときは、**`BeginCombo` / `EndCombo`**を使います。

```cpp
if (ImGui::BeginCombo("敵の種類", enemy_names[current].c_str())) {
  for (int i = 0; i < enemy_names.size(); ++i) {
    bool selected = (current == i);
    if (ImGui::Selectable(enemy_names[i].c_str(), selected)) current = i;
    if (selected) ImGui::SetItemDefaultFocus();
  }
  ImGui::EndCombo();
}
```

**`Begin...` が `true` のときだけ、`End...` を呼びます**。

### ListBox

```cpp
if (ImGui::BeginListBox("##list", ImVec2(-FLT_MIN, 8 * ImGui::GetTextLineHeightWithSpacing()))) {
  for (int i = 0; i < items.size(); ++i) {
    if (ImGui::Selectable(items[i].c_str(), i == selected)) selected = i;
  }
  ImGui::EndListBox();
}
```

## ツリーと折りたたみ

| 関数 | 用途 |
| --- | --- |
| **`TreeNode("ラベル")` … `TreePop()`** | **開閉できる木**（`true` のときだけ中身を出し、`TreePop` を呼ぶ） |
| **`CollapsingHeader("ラベル")`** | **大きな折りたたみ見出し**（`TreePop` は不要） |
| `TreeNodeEx(label, flags)` | **フラグ付き**（`ImGuiTreeNodeFlags_DefaultOpen`、`Leaf`、`Selected`） |

```cpp
if (ImGui::TreeNode("Transform")) {
  ImGui::DragFloat3("位置", &t.position.x);
  ImGui::TreePop();
}

if (ImGui::CollapsingHeader("Physics", ImGuiTreeNodeFlags_DefaultOpen)) {
  ImGui::DragFloat("質量", &mass);
}
```

**エンティティの階層表示**（シーンのツリー）に、**`TreeNodeEx` の `Leaf` / `OpenOnArrow`** を、よく使います。

## テーブル {#table}

**表形式**の表示です。**ソート・スクロール・列の幅の変更**ができます。

```cpp
ImGuiTableFlags flags = ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg |
                        ImGuiTableFlags_Resizable | ImGuiTableFlags_ScrollY |
                        ImGuiTableFlags_Sortable;

if (ImGui::BeginTable("enemies", 3, flags, ImVec2(0, 200))) {
  ImGui::TableSetupScrollFreeze(0, 1);
  ImGui::TableSetupColumn("名前");
  ImGui::TableSetupColumn("HP", ImGuiTableColumnFlags_WidthFixed, 60.0f);
  ImGui::TableSetupColumn("位置");
  ImGui::TableHeadersRow();

  for (const Enemy& e : enemies) {
    ImGui::TableNextRow();
    ImGui::TableNextColumn();
    ImGui::TextUnformatted(e.name.c_str());
    ImGui::TableNextColumn();
    ImGui::Text("%d", e.hp);
    ImGui::TableNextColumn();
    ImGui::Text("%.1f, %.1f", e.x, e.y);
  }
  ImGui::EndTable();
}
```

| 関数 | 意味 |
| --- | --- |
| **`BeginTable(id, 列数, フラグ, サイズ)`** | 表を始める（`true` のときだけ中身を出し、`EndTable`） |
| `TableSetupColumn(名前, フラグ, 幅)` | **列の設定** |
| `TableHeadersRow()` | **ヘッダ行**を出す |
| **`TableNextRow()` / `TableNextColumn()`** | **次の行・次の列**へ |
| `TableGetSortSpecs()` | **ソートの指定**を取得（クリックされた列と向き） |
| `ImGuiListClipper` | **大量の行**で、**見えている行だけ**を描く（高速化） |

!!! note "大量の行は、ListClipper"
    数千行を毎フレーム全部描くと、**重い**です。**`ImGuiListClipper`** で、**見える範囲だけ**を描きます。

## プロット（グラフ）

```cpp
static float frame_times[120] = {};
static int offset = 0;
frame_times[offset] = ImGui::GetIO().DeltaTime * 1000.0f;
offset = (offset + 1) % IM_ARRAYSIZE(frame_times);

ImGui::PlotLines("フレーム時間(ms)", frame_times, IM_ARRAYSIZE(frame_times), offset,
                 nullptr, 0.0f, 33.0f, ImVec2(0, 80));
```

| 関数 | 用途 |
| --- | --- |
| **`PlotLines`** | **折れ線グラフ** |
| `PlotHistogram` | **棒グラフ** |
| `ProgressBar(fraction, ImVec2, overlay)` | **進行バー**（HP・ロード進捗） |

**リングバッファ**（`offset`）で、**新しい値を書き続ける**使い方が、定番です（[フレーム時間の設計](../../optimize/frame-budget.md)）。**本格的なグラフ**が必要なら、**ImPlot** などの拡張があります。

## メニュー・ポップアップ・ツールチップ

### メニュー {#menu}

```cpp
if (ImGui::BeginMainMenuBar()) {
  if (ImGui::BeginMenu("ファイル")) {
    if (ImGui::MenuItem("保存", "Ctrl+S")) Save();
    if (ImGui::MenuItem("終了")) quit = true;
    ImGui::EndMenu();
  }
  if (ImGui::BeginMenu("表示")) {
    ImGui::MenuItem("デバッグ", nullptr, &show_debug);
    ImGui::EndMenu();
  }
  ImGui::EndMainMenuBar();
}
```

**`MenuItem` の第 3 引数に `bool*`<strong> を渡すと、</strong>チェック付きの項目**になります。

### ポップアップ

```cpp
if (ImGui::Button("削除")) ImGui::OpenPopup("確認");

if (ImGui::BeginPopupModal("確認", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
  ImGui::Text("本当に削除しますか？");
  if (ImGui::Button("はい")) { Delete(); ImGui::CloseCurrentPopup(); }
  ImGui::SameLine();
  if (ImGui::Button("いいえ")) ImGui::CloseCurrentPopup();
  ImGui::EndPopup();
}
```

| 関数 | 用途 |
| --- | --- |
| **`OpenPopup(id)`** | ポップアップを**開く**（1 回） |
| **`BeginPopup(id)`** | **普通のポップアップ**（外をクリックで閉じる） |
| **`BeginPopupModal(id)`** | **モーダル**（閉じるまで、他を触れない） |
| `BeginPopupContextItem()` | **右クリックのメニュー** |
| **`CloseCurrentPopup()`** | 閉じる |

### ツールチップ

```cpp
ImGui::Button("攻撃");
if (ImGui::IsItemHovered()) {
  ImGui::SetTooltip("敵に、%d のダメージを与える", damage);
}
```

**直前の部品**にマウスが乗ったときに、**説明を出します**（`IsItemHovered`）。

## ID と、ラベルの重複

**部品の ID は、ラベル文字列から作られます**。**同じラベルが複数あると、同じ部品**と扱われて、**片方しか反応しません**。

```cpp
for (Enemy& e : enemies) {
  if (ImGui::Button("削除")) Remove(e);
}
```

**このコードは、1 つ目のボタンしか、反応しません**。

| 方法 | 書き方 | 説明 |
| --- | --- | --- |
| **`##` で、見えない ID を足す** | `"削除##" + 番号` | **`##` より後ろは、画面に出ない**が、ID になる |
| **`###`** | `"表示名###固定ID"` | **`###` の後ろだけが ID**（表示名が変わっても、ID は同じ） |
| **`PushID` / `PopID`** | `ImGui::PushID(i); ...; ImGui::PopID();` | **ID の、前置き**を積む（ループに最適） |

```cpp
for (int i = 0; i < enemies.size(); ++i) {
  ImGui::PushID(i);
  if (ImGui::Button("削除")) Remove(i);
  ImGui::PopID();
}
```

## Begin / End の対応

| 組 | `End` を呼ぶ条件 |
| --- | --- |
| **`Begin` / `End`**（ウィンドウ） | **`Begin` の戻り値に関係なく、必ず `End`** |
| **`BeginChild` / `EndChild`** | **同様に、必ず `EndChild`** |
| **`BeginCombo`・`BeginListBox`・`BeginTable`・`BeginMenu`・`BeginPopup`・`BeginTabBar`・`TreeNode`** | **`true` のときだけ、対応する `End` / `Pop`** |

**対応が崩れる**と、**assert**で止まります（デバッグビルドで分かる）。

## よくあるミス

??? failure "同じラベルのボタンが複数あり、1 つしか反応しない"
    **`PushID` か `##` で、ID を変えます**。

??? failure "`BeginCombo` が `false` なのに `EndCombo` を呼ぶ"
    **`true` のときだけ**、`End` を呼びます。

??? failure "ローカル変数を、スライダーに渡して、値が戻る"
    **毎フレーム、初期化**されます。**`static` かメンバ変数**にします。

??? failure "`ImGui::Text(user_string)` でクラッシュする"
    **`TextUnformatted`** か、`Text("%s", ...)`。

??? failure "`DragFloat3(..., &v)` で、構造体が壊れる"
    **`float` 3 つが連続**している型（`&v.x`）にだけ使います。

??? failure "大量の行を、毎フレーム全部描いて遅い"
    **`ImGuiListClipper`** を使います。

??? failure "日本語のラベルが `?` になる"
    **日本語フォント**が必要です（[フォント](fonts.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 部品は<strong>関数 1 回で、描画と入力</strong>。<strong>戻り値 ＝ 変更・クリックされたか</strong>。<strong>値はポインタで渡す</strong>
    - [x] 調整は<strong>`DragFloat`</strong>、範囲があれば<strong>`SliderFloat`</strong>。<strong>`Vector3` は `DragFloat3(&v.x)`</strong>
    - [x] <strong>`std::string` は `imgui_stdlib.h`</strong>。<strong>ユーザー文字列は `TextUnformatted`</strong>
    - [x] <strong>`BeginXxx` が `true` のときだけ `EndXxx`</strong>（ただし、`Begin` / `End` ウィンドウは必ず）
    - [x] <strong>ラベルが ID</strong>。<strong>重複は `PushID` / `##`</strong>
    - [x] <strong>大量の行は `ImGuiListClipper`</strong>

## 関連ページ

- [Dear ImGui](index.md)
- [レイアウトとウィンドウ](layout.md)
- [日本語フォントとアイコン](fonts.md)
- [ゲームでのデバッグ画面](debug-ui.md)
- [スタイルとテーマ](style.md)
- [ImGuizmo](imguizmo.md)
