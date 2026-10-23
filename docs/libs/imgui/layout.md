---
title: レイアウトとウィンドウ
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のレイアウトとウィンドウ

ImGui は <strong>部品を呼んだ順に上から下へ並べます</strong>（自動レイアウト）。ウィンドウの位置・大きさ、部品を横に並べる方法、表・列・子ウィンドウ、メニューバーなど レイアウトの道具をまとめます。何も指定しなくても動きますが、少し指定すると見やすい画面になります。

!!! tip "ポイント"
    - <strong>ウィンドウは `Begin("名前") … End()`</strong>。<strong>名前がウィンドウの ID</strong>。
    - 位置・大きさは `SetNextWindowPos` / `SetNextWindowSize`（`Begin` の直前に）。`ImGuiCond_FirstUseEver` で最初だけ。
    - 部品は縦に並ぶ。横に並べるのは `SameLine()`。
    - 表は `BeginTable`（`Columns` は古い）。区切りは `Separator`、余白は `Spacing`。
    - ウィンドウの中にスクロールする領域を作るのは`BeginChild`。
    - 固定のオーバーレイ（FPS 表示など）は、フラグでタイトルバーなしにして、位置を固定。

## ウィンドウ

```cpp
ImGui::SetNextWindowPos(ImVec2(10, 10), ImGuiCond_FirstUseEver);
ImGui::SetNextWindowSize(ImVec2(300, 200), ImGuiCond_FirstUseEver);

bool open = true;
if (ImGui::Begin("プレイヤー", &open)) {
  ImGui::Text("HP: %d", hp);
}
ImGui::End();
```

| 点 | 説明 |
| --- | --- |
| <strong>`Begin("名前", &open, flags)`</strong> | ウィンドウを始める。第 2 引数に `bool*`<strong> を渡すと 閉じるボタン（×）</strong>が付く |
| `End()` | `Begin` の戻り値に関係なく、必ず呼ぶ |
| 戻り値 | ウィンドウが、折りたたまれていなければ `true`。`false` なら 中身の処理を飛ばして、軽くできる |
| ウィンドウの名前 | 同じ名前は、同じウィンドウ。位置・大きさは `imgui.ini` に名前で保存される |

### 位置と大きさ

| 関数 | 説明 |
| --- | --- |
| `SetNextWindowPos(pos, cond, pivot)` | 次の `Begin` のウィンドウの位置。`pivot` で基準点（右下 `(1,1)` など） |
| `SetNextWindowSize(size, cond)` | 次のウィンドウの大きさ |
| `SetNextWindowSizeConstraints(min, max)` | 大きさの最小・最大 |
| `SetNextWindowBgAlpha(alpha)` | 背景の透明度 |
| `SetNextWindowCollapsed(bool, cond)` | 折りたたみ |

これらは `Begin` の直前に呼びます（「次のウィンドウ用」の設定）。

### 条件（ImGuiCond）

| 値 | 意味 |
| --- | --- |
| `ImGuiCond_Always` | 毎フレーム、強制する（ユーザーが動かしても戻る） |
| `ImGuiCond_Once` | アプリの起動ごとに最初の 1 回 |
| `ImGuiCond_FirstUseEver` | `imgui.ini` に記録がなければ、最初の 1 回（ユーザーが動かした位置は、保持される） |
| `ImGuiCond_Appearing` | ウィンドウが表示されるたび |

普通は `FirstUseEver`を使います（初期位置だけを決めて、あとはユーザーに任せる）。

### ウィンドウのフラグ

| フラグ | 意味 |
| --- | --- |
| `ImGuiWindowFlags_NoTitleBar` | タイトルバーなし |
| `ImGuiWindowFlags_NoResize` | 大きさを変えられない |
| `ImGuiWindowFlags_NoMove` | 動かせない |
| `ImGuiWindowFlags_NoCollapse` | 折りたためない |
| `ImGuiWindowFlags_AlwaysAutoResize` | 中身に合わせて、自動でサイズを変える |
| `ImGuiWindowFlags_NoSavedSettings` | `imgui.ini` に保存しない |
| `ImGuiWindowFlags_NoBackground` | 背景を描かない |
| `ImGuiWindowFlags_MenuBar` | メニューバーを持つ |
| `ImGuiWindowFlags_HorizontalScrollbar` | 横スクロールバー |
| `ImGuiWindowFlags_NoInputs` | 入力を受け付けない（マウスを通す） |
| `ImGuiWindowFlags_NoFocusOnAppearing` / `NoNav` | フォーカスを奪わない |

### 固定のオーバーレイ（FPS 表示など）

```cpp
ImGuiWindowFlags flags = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_AlwaysAutoResize |
                         ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoFocusOnAppearing |
                         ImGuiWindowFlags_NoNav | ImGuiWindowFlags_NoMove;

const ImGuiViewport* viewport = ImGui::GetMainViewport();
ImGui::SetNextWindowPos(ImVec2(viewport->WorkPos.x + viewport->WorkSize.x - 10, viewport->WorkPos.y + 10),
                        ImGuiCond_Always, ImVec2(1.0f, 0.0f));
ImGui::SetNextWindowBgAlpha(0.35f);

if (ImGui::Begin("オーバーレイ", nullptr, flags)) {
  ImGui::Text("FPS: %.1f", ImGui::GetIO().Framerate);
}
ImGui::End();
```

右上に半透明の FPS 表示を出す例です。`pivot (1, 0)`で ウィンドウの右上を指定位置に合わせます。

## 部品を並べる

| 関数 | 動き |
| --- | --- |
| <strong>`SameLine(offset, spacing)`</strong> | 次の部品を同じ行（右）に置く |
| `NewLine()` | 改行（空の 1 行） |
| `Separator()` | 横線 |
| `Spacing()` | 少しの縦の余白 |
| `Dummy(ImVec2)` | 見えない場所を確保（余白） |
| `Indent(w)` / `Unindent(w)` | 字下げ |
| `BeginGroup()` / `EndGroup()` | 複数の部品を 1 つの塊として扱う（`SameLine` やホバー判定の単位） |

```cpp
ImGui::Button("保存");
ImGui::SameLine();
ImGui::Button("読み込み");

ImGui::BeginGroup();
ImGui::Text("左");
ImGui::Button("A");
ImGui::EndGroup();
ImGui::SameLine();
ImGui::BeginGroup();
ImGui::Text("右");
ImGui::Button("B");
ImGui::EndGroup();
```

### 幅の指定

| 関数 | 説明 |
| --- | --- |
| `SetNextItemWidth(w)` | 次の 1 つの部品の幅 |
| `PushItemWidth(w)` / `PopItemWidth()` | ここから先の部品の幅 |
| `w < 0` | 右端から `-w` 手前まで（`-FLT_MIN` で、右端まで） |
| `CalcItemWidth()` | 現在の幅 |

```cpp
ImGui::SetNextItemWidth(-FLT_MIN);
ImGui::InputText("##name", &name);
```

### 空き領域・ウィンドウの大きさ

| 関数 | 返すもの |
| --- | --- |
| `GetContentRegionAvail()` | 今の位置から、ウィンドウの端までの残りの領域 |
| `GetWindowSize()` / `GetWindowPos()` | ウィンドウの大きさ・位置 |
| `GetCursorScreenPos()` | 次の部品の描画位置（画面座標） |
| `GetTextLineHeightWithSpacing()` | 1 行の高さ |

## 表（Table）と列

<strong>表形式</strong>でそろえて並べるなら `BeginTable`です（[ウィジェット一覧](widgets.md#table)）。古い `Columns` は 機能が少なく、`BeginTable` を使います。

```cpp
if (ImGui::BeginTable("props", 2, ImGuiTableFlags_SizingStretchProp)) {
  ImGui::TableNextRow();
  ImGui::TableNextColumn(); ImGui::TextUnformatted("名前");
  ImGui::TableNextColumn(); ImGui::TextUnformatted(entity.name.c_str());
  ImGui::TableNextRow();
  ImGui::TableNextColumn(); ImGui::TextUnformatted("HP");
  ImGui::TableNextColumn(); ImGui::DragInt("##hp", &entity.hp);
  ImGui::EndTable();
}
```

「ラベル」と「値」をきれいにそろえる（インスペクター）ときに 2 列の表が便利です。

## 子ウィンドウとスクロール

<strong>ウィンドウの中に独立してスクロールする領域</strong>を作ります。

```cpp
if (ImGui::BeginChild("ログ", ImVec2(0, 150), ImGuiChildFlags_Borders)) {
  for (const std::string& line : log_lines) {
    ImGui::TextUnformatted(line.c_str());
  }
  if (scroll_to_bottom) ImGui::SetScrollHereY(1.0f);
}
ImGui::EndChild();
```

| 点 | 説明 |
| --- | --- |
| `BeginChild(id, size, flags)` | 子ウィンドウ。`size` の `0` は 残りの領域いっぱい |
| `EndChild()` | `BeginChild` の戻り値に関係なく、必ず呼ぶ |
| `ImGuiChildFlags_Borders`（旧 `border = true`） | 枠線を付ける |
| `SetScrollHereY(1.0f)` | 一番下までスクロール（ログの自動スクロール） |
| `GetScrollY()` / `GetScrollMaxY()` | スクロール位置の取得 |

!!! note "バージョンで、引数が変わる"
    `BeginChild` の `bool border` 引数は 新しい版（1.90 以降）で `ImGuiChildFlags` に変わっています。使っているバージョンのヘッダで、確認してください。

## タブ

```cpp
if (ImGui::BeginTabBar("tabs")) {
  if (ImGui::BeginTabItem("基本")) {
    ImGui::Text("基本の設定");
    ImGui::EndTabItem();
  }
  if (ImGui::BeginTabItem("物理")) {
    ImGui::Text("物理の設定");
    ImGui::EndTabItem();
  }
  ImGui::EndTabBar();
}
```

## メインメニューバーとステータスバー

<strong>画面の上端のメニューバー</strong>は `BeginMainMenuBar`（[ウィジェット一覧](widgets.md#menu)）です。下端のステータスバーは メイン ビューポートに沿った、固定のウィンドウで作ります。

```cpp
ImGuiViewport* viewport = ImGui::GetMainViewport();
ImGui::SetNextWindowPos(ImVec2(viewport->WorkPos.x, viewport->WorkPos.y + viewport->WorkSize.y - 24));
ImGui::SetNextWindowSize(ImVec2(viewport->WorkSize.x, 24));
ImGuiWindowFlags flags = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
                         ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoBringToFrontOnFocus;
if (ImGui::Begin("##statusbar", nullptr, flags)) {
  ImGui::Text("FPS: %.0f   オブジェクト: %d", ImGui::GetIO().Framerate, object_count);
}
ImGui::End();
```

`WorkPos` / `WorkSize` は メニューバーなどを除いた、使える領域です。

## ID（ウィンドウと部品）

<strong>ID は `ID スタック`</strong>で管理されます（ウィンドウ名 → `PushID` の値 → ラベル）。

| 書き方 | 意味 |
| --- | --- |
| `"ラベル"` | 表示と ID が同じ |
| `"ラベル##固定"` | 表示は「ラベル」、ID は「ラベル##固定」 |
| `"##固定"` | 表示なし、ID だけ |
| `"表示名###ID"` | ID は `###` 以降だけ（表示名が動的に変わっても、ウィンドウの位置が保たれる） |
| `PushID(i)` / `PopID()` | ループの中の同じラベルを区別 |

ウィンドウのタイトルに動的な値（FPS など）を入れたい場合は、`"FPS: 60###fps"` のように `###` で ID を固定します。固定しないとタイトルが変わるたびに別のウィンドウになって、位置が戻ります。

## DPI とスケール

<strong>高 DPI のディスプレイ</strong>では ImGui の文字や部品が、小さく見えます。

| 対策 | 説明 |
| --- | --- |
| `io.FontGlobalScale` | 全体の拡大率（フォントのぼやけに注意） |
| フォントの大きさを DPI に合わせる | `AddFontFromFileTTF(path, 16.0f * dpi_scale)`（[フォント](fonts.md)） |
| `style.ScaleAllSizes(scale)` | 余白・角丸などすべての大きさを拡大（[スタイル](style.md#dpi)） |

## よくあるミス

??? failure "`SetNextWindowPos` を `Begin` の後に呼ぶ"
    <strong>効きません</strong>。`Begin` の直前に呼びます。

??? failure "`SetNextWindowPos(..., ImGuiCond_Always)` で、ユーザーが動かせない"
    毎フレーム、戻されます。`FirstUseEver` にします。

??? failure "`BeginChild` が `false` のとき `EndChild` を呼ばない"
    `BeginChild` は戻り値に関係なく、`EndChild` が必要です。

??? failure "タイトルに動的な値を入れて、ウィンドウの位置が毎回リセットされる"
    `###` で ID を固定します。

??? failure "`SameLine` の位置が、ずれる"
    `SameLine(0, 5)` のように 位置と間隔を指定します。幅の違う部品は `SetNextItemWidth` でそろえます。

??? failure "`Columns` を使って、機能が足りない"
    `BeginTable` に置き換えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`Begin` / `End`</strong> でウィンドウ。位置・大きさは `Begin` の直前に `SetNextWindow...`（`FirstUseEver`）
    - [x] 縦に並ぶ。横は `SameLine`、まとまりは `BeginGroup`、幅は `SetNextItemWidth`
    - [x] 表は`BeginTable`、スクロール領域は`BeginChild`
    - [x] オーバーレイは、フラグ（`NoDecoration` など）と位置の固定
    - [x] ID：`##`（見えない ID）、`###`（ID 固定）、`PushID`（ループ）
    - [x] 高 DPI は、フォントとスタイルを拡大

## 関連ページ

- [Dear ImGui](index.md)
- [ウィジェット一覧](widgets.md)
- [ドッキングとビューポート](docking.md)
- [スタイルとテーマ](style.md)
- [日本語フォントとアイコン](fonts.md)
