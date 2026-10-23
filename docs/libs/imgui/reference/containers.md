---
title: 早見表：コンテナ
tags:
  - 外部ライブラリ
  - GUI
---

# 早見表：コンテナ

**他の部品を「入れる」部品**（ツリー・タブ・テーブル・メニュー・ポップアップ）の関数です。これらは `Begin…` / `End…` の対になっており、「`End` を呼ぶ条件」が関数ごとに違います。ここを間違えるとアサートで落ちるので、「閉じ方」の列を必ず確認してください。

!!! tip "ポイント"
    - <strong>`Begin…` が true を返したときだけ `End…` を呼ぶ</strong>のが<strong>大半</strong>（`BeginTable`・`BeginMenu`・`BeginTabItem`・`BeginPopup`・`BeginCombo`）。
    - 例外：`Begin`（ウィンドウ）と `BeginChild`は戻り値に関係なく、必ず `End` / `EndChild`。
    - `TreeNode` が true を返したら、最後に `TreePop`。
    - ポップアップ系は、`OpenPopup` で開き、`BeginPopup` で中身を書く（2 段階）。

## ツリー・折りたたみ

| 関数 | 出るもの | 戻り値 | 閉じ方 |
| --- | --- | --- | --- |
| `TreeNode(label)` | **折りたたみ可能な行**（▶ 付き） | 開いている | true のとき `TreePop()` |
| `TreeNode(id, fmt, ...)` | 同上（ID と表示文字を別に） | 開いている | true のとき `TreePop()` |
| `TreeNodeEx(label, flags)` | フラグ付きのツリー | 開いている | フラグ次第（`NoTreePushOnOpen` なら不要） |
| `TreePush(id)` / `TreePop()` | インデントだけ（ノードなし） | `void` | 対で呼ぶ |
| `CollapsingHeader(label, flags)` | 幅いっぱいの折りたたみ見出し | 開いている | 不要（`TreePop` なし） |
| `CollapsingHeader(label, &visible, flags)` | 閉じるボタン付きの見出し | 開いている | 不要 |
| `SetNextItemOpen(is_open, cond)` | 次のノードの開閉を指定 | `void` | — |
| `GetTreeNodeToLabelSpacing()` | ノードとラベルの間隔 | `float` | — |

```cpp
if (ImGui::TreeNode("Enemies")) {
  for (const Enemy& e : enemies) ImGui::BulletText("%s", e.name.c_str());
  ImGui::TreePop();
}

if (ImGui::CollapsingHeader("Transform", ImGuiTreeNodeFlags_DefaultOpen)) {
  ImGui::DragFloat3("Position", &pos.x);
}
```

| 比べ方 | `TreeNode` | `CollapsingHeader` |
| --- | --- | --- |
| 見た目 | ▶ ＋ ラベル（インデントされる） | 背景付きの幅いっぱいの見出し |
| 子のインデント | 自動でインデント | なし |
| 閉じ方 | `TreePop` が必要 | 不要 |
| 用途 | 階層（ヒエラルキー） | セクション分け（インスペクター） |

## タブ

| 関数 | 出るもの | 戻り値 | 閉じ方 |
| --- | --- | --- | --- |
| `BeginTabBar(id, flags)` | **タブ バー** | 開いている | true のとき `EndTabBar()` |
| `BeginTabItem(label, &open, flags)` | タブ 1 枚 | 選択中 | true のとき `EndTabItem()` |
| `TabItemButton(label, flags)` | タブ列にあるボタン（`+` など） | 押された | 不要 |
| `SetTabItemClosed(label)` | タブを閉じた扱いにする | `void` | — |

```cpp
if (ImGui::BeginTabBar("MainTabs")) {
  if (ImGui::BeginTabItem("Scene")) {
    DrawSceneTab();
    ImGui::EndTabItem();
  }
  if (ImGui::BeginTabItem("Assets")) {
    DrawAssetsTab();
    ImGui::EndTabItem();
  }
  ImGui::EndTabBar();
}
```

## テーブル

| 関数 | 出るもの | 戻り値 | 閉じ方 |
| --- | --- | --- | --- |
| `BeginTable(id, columns, flags, size)` | **表** | 描画中 | true のとき `EndTable()` |
| `TableSetupColumn(label, flags, width)` | 列の設定（名前・幅・フラグ） | `void` | — |
| `TableSetupScrollFreeze(cols, rows)` | スクロールで固定する列・行 | `void` | — |
| `TableHeadersRow()` | ヘッダー行（クリックで並べ替え） | `void` | — |
| `TableHeader(label)` | ヘッダー 1 つ | `void` | — |
| `TableNextRow(flags, min_height)` | 次の行へ | `void` | — |
| `TableNextColumn()` | 次の列へ（行末なら次の行へ） | 列が有効 | — |
| `TableSetColumnIndex(n)` | 列番号を指定 | 列が有効 | — |
| `TableGetSortSpecs()` | 並べ替えの指定（どの列・昇降順） | `ImGuiTableSortSpecs*` | — |
| `TableSetBgColor(target, color, col)` | 行・セルの背景色 | `void` | — |
| `TableGetColumnCount()` / `TableGetRowIndex()` | 現在の列数・行番号 | `int` | — |

```cpp
if (ImGui::BeginTable("Enemies", 3, ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg)) {
  ImGui::TableSetupColumn("Name");
  ImGui::TableSetupColumn("HP");
  ImGui::TableSetupColumn("Lv");
  ImGui::TableHeadersRow();
  for (const Enemy& e : enemies) {
    ImGui::TableNextRow();
    ImGui::TableNextColumn(); ImGui::TextUnformatted(e.name.c_str());
    ImGui::TableNextColumn(); ImGui::Text("%d", e.hp);
    ImGui::TableNextColumn(); ImGui::Text("%d", e.level);
  }
  ImGui::EndTable();
}
```

行が非常に多いときは、`ImGuiListClipper`で、見える行だけを描きます（下記）。

## 大量の行を速く描く（ListClipper）

| 関数 | 内容 |
| --- | --- |
| `ImGuiListClipper clipper;` | **クリッパー**を作る |
| `clipper.Begin(count, item_height)` | 全体の個数と1 行の高さを渡す |
| `clipper.Step()` | 次に描く範囲があるか（ループ条件） |
| `clipper.DisplayStart` / `DisplayEnd` | 描く範囲（`[Start, End)`） |
| `clipper.End()` | 終了（`Step` が false を返せば自動） |

```cpp
ImGuiListClipper clipper;
clipper.Begin(static_cast<int>(lines.size()));
while (clipper.Step()) {
  for (int i = clipper.DisplayStart; i < clipper.DisplayEnd; ++i) {
    ImGui::TextUnformatted(lines[i].c_str());
  }
}
```

10 万行のログでも画面に見える数十行だけを描くので軽いです。

## メニュー

| 関数 | 出るもの | 戻り値 | 閉じ方 |
| --- | --- | --- | --- |
| `BeginMainMenuBar()` | **画面上端のメニュー バー** | 描画中 | true のとき `EndMainMenuBar()` |
| `BeginMenuBar()` | ウィンドウ内のメニュー バー（`MenuBar` フラグが必要） | 描画中 | true のとき `EndMenuBar()` |
| `BeginMenu(label, enabled)` | メニュー（`File` など） | 開いている | true のとき `EndMenu()` |
| `MenuItem(label, shortcut, selected, enabled)` | メニューの項目 | 選ばれた | 不要 |
| `MenuItem(label, shortcut, &selected)` | チェック付きの項目 | 選ばれた | 不要 |

```cpp
if (ImGui::BeginMainMenuBar()) {
  if (ImGui::BeginMenu("File")) {
    if (ImGui::MenuItem("Open", "Ctrl+O")) Open();
    if (ImGui::MenuItem("Save", "Ctrl+S")) Save();
    ImGui::Separator();
    if (ImGui::MenuItem("Quit")) running = false;
    ImGui::EndMenu();
  }
  ImGui::EndMainMenuBar();
}
```

## ポップアップ

**ポップアップは、2 段階**です。「開く（`OpenPopup`）」と「中身を書く（`BeginPopup`）」。

| 関数 | 出るもの | 戻り値 | 閉じ方 |
| --- | --- | --- | --- |
| `OpenPopup(id)` | ポップアップを開く（予約） | `void` | — |
| `BeginPopup(id, flags)` | 通常のポップアップ（外をクリックで閉じる） | 開いている | true のとき `EndPopup()` |
| `BeginPopupModal(name, &open, flags)` | モーダル ダイアログ（背面を操作不可） | 開いている | true のとき `EndPopup()` |
| `BeginPopupContextItem(id)` | 直前の項目の右クリック メニュー | 開いている | true のとき `EndPopup()` |
| `BeginPopupContextWindow(id)` | ウィンドウの右クリック メニュー | 開いている | true のとき `EndPopup()` |
| `CloseCurrentPopup()` | 現在のポップアップを閉じる | `void` | — |
| `IsPopupOpen(id)` | 開いているか | `bool` | — |

```cpp
if (ImGui::Button("Delete")) ImGui::OpenPopup("Confirm");

if (ImGui::BeginPopupModal("Confirm", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
  ImGui::Text("Delete this item?");
  if (ImGui::Button("Yes")) { Delete(); ImGui::CloseCurrentPopup(); }
  ImGui::SameLine();
  if (ImGui::Button("No")) ImGui::CloseCurrentPopup();
  ImGui::EndPopup();
}
```

## ツールチップ

| 関数 | 出るもの | 戻り値 | 閉じ方 |
| --- | --- | --- | --- |
| `SetTooltip(fmt, ...)` | **簡単な文字だけのツールチップ** | `void` | 不要 |
| `BeginTooltip()` | 自由な中身のツールチップ | 描画中 | `EndTooltip()` |
| `SetItemTooltip(fmt, ...)` | 直前の項目にホバーしたときのツールチップ | `void` | 不要（1.89 以降） |
| `BeginItemTooltip()` | 同上（自由な中身） | 描画中 | true のとき `EndTooltip()` |
| `IsItemHovered()` | 直前の項目にマウスが乗っているか | `bool` | — |

```cpp
ImGui::Button("Save");
if (ImGui::IsItemHovered()) ImGui::SetTooltip("Ctrl+S");
```

## ドラッグ＆ドロップ

<strong>ドラッグの元（ソース）とドロップの先（ターゲット）</strong>を、それぞれ指定します。

| 関数 | 内容 | 閉じ方 |
| --- | --- | --- |
| `BeginDragDropSource(flags)` | 直前の項目をドラッグ元にする | true のとき `EndDragDropSource()` |
| `SetDragDropPayload(type, data, size)` | 運ぶデータを設定（ソースの中で） | — |
| `BeginDragDropTarget()` | 直前の項目をドロップ先にする | true のとき `EndDragDropTarget()` |
| `AcceptDragDropPayload(type, flags)` | ドロップされたデータを受け取る | — |
| `GetDragDropPayload()` | 現在ドラッグ中のデータ | — |

```cpp
ImGui::Button(item.name.c_str());
if (ImGui::BeginDragDropSource()) {
  ImGui::SetDragDropPayload("ITEM", &item_id, sizeof(item_id));
  ImGui::Text("%s", item.name.c_str());
  ImGui::EndDragDropSource();
}

ImGui::Button("Slot");
if (ImGui::BeginDragDropTarget()) {
  if (const ImGuiPayload* payload = ImGui::AcceptDragDropPayload("ITEM")) {
    int dropped_id = *static_cast<const int*>(payload->Data);
    Equip(dropped_id);
  }
  ImGui::EndDragDropTarget();
}
```

`SetDragDropPayload` のデータは「コピー」されるので小さなもの（ID・インデックス）を渡します（ポインタや大きな構造体ではなく）。

## 一目で分かる「閉じ方」表

| 開く関数 | 閉じ方 |
| --- | --- |
| `Begin` | **戻り値に関係なく、必ず `End`** |
| `BeginChild` | 戻り値に関係なく、必ず `EndChild` |
| `BeginTable` / `BeginTabBar` / `BeginTabItem` / `BeginMenu` / `BeginMenuBar` / `BeginMainMenuBar` / `BeginCombo` / `BeginListBox` / `BeginPopup*` / `BeginTooltip` | true のときだけ `End…` |
| `TreeNode` | true のときだけ `TreePop` |
| `BeginDragDropSource` / `BeginDragDropTarget` | true のときだけ `End…` |
| `BeginGroup` | 常に `EndGroup` |
| `PushID` / `PushStyleColor` / `PushStyleVar` / `PushItemWidth` / `PushFont` | 常に対になる `Pop…` |

## 関連ページ

- [関数早見表](index.md)
- [ウィジェット](widgets.md)
- [レイアウトとウィンドウ](layout.md)
- [ウィジェット一覧（解説）](../widgets.md)
