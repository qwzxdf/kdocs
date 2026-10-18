---
title: レイアウトとウィンドウ
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のレイアウトとウィンドウ

ImGui は、<strong>部品を、呼んだ順に、上から下へ並べます</strong>（自動レイアウト）。<strong>ウィンドウの位置・大きさ</strong>、<strong>部品を横に並べる方法</strong>、<strong>表・列・子ウィンドウ</strong>、<strong>メニューバー</strong>など、<strong>レイアウトの道具</strong>をまとめます。<strong>何も指定しなくても動きますが、少し指定すると、見やすい画面</strong>になります。

!!! tip "ポイント"
    - <strong>ウィンドウは `Begin("名前") … End()`</strong>。<strong>名前がウィンドウの ID</strong>。
    - <strong>位置・大きさは、`SetNextWindowPos` / `SetNextWindowSize`</strong>（<strong>`Begin` の直前</strong>に）。<strong>`ImGuiCond_FirstUseEver` で、最初だけ</strong>。
    - <strong>部品は、縦に並ぶ</strong>。<strong>横に並べるのは `SameLine()`</strong>。
    - <strong>表は `BeginTable`</strong>（`Columns` は古い）。<strong>区切りは `Separator`、余白は `Spacing`</strong>。
    - <strong>ウィンドウの中に、スクロールする領域</strong>を作るのは<strong>`BeginChild`</strong>。
    - <strong>固定のオーバーレイ（FPS 表示など）</strong>は、<strong>フラグでタイトルバーなしにして、位置を固定</strong>。

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
| <strong>`Begin("名前", &open, flags)`</strong> | ウィンドウを始める。<strong>第 2 引数に `bool*`<strong> を渡すと、</strong>閉じるボタン（×）</strong>が付く |
| <strong>`End()`</strong> | <strong>`Begin` の戻り値に関係なく</strong>、必ず呼ぶ |
| <strong>戻り値</strong> | <strong>ウィンドウが、折りたたまれていなければ `true`</strong>。`false` なら、<strong>中身の処理を飛ばして</strong>、軽くできる |
| <strong>ウィンドウの名前</strong> | <strong>同じ名前は、同じウィンドウ</strong>。<strong>位置・大きさは、`imgui.ini` に、名前で保存</strong>される |

### 位置と大きさ

| 関数 | 説明 |
| --- | --- |
| <strong>`SetNextWindowPos(pos, cond, pivot)`</strong> | <strong>次の `Begin` のウィンドウの位置</strong>。`pivot` で、基準点（右下 `(1,1)` など） |
| <strong>`SetNextWindowSize(size, cond)`</strong> | <strong>次のウィンドウの大きさ</strong> |
| `SetNextWindowSizeConstraints(min, max)` | <strong>大きさの、最小・最大</strong> |
| `SetNextWindowBgAlpha(alpha)` | <strong>背景の透明度</strong> |
| `SetNextWindowCollapsed(bool, cond)` | 折りたたみ |

<strong>これらは、`Begin` の直前</strong>に呼びます（「次のウィンドウ用」の設定）。

### 条件（ImGuiCond）

| 値 | 意味 |
| --- | --- |
| <strong>`ImGuiCond_Always`</strong> | <strong>毎フレーム</strong>、強制する（ユーザーが動かしても戻る） |
| <strong>`ImGuiCond_Once`</strong> | <strong>アプリの起動ごとに、最初の 1 回</strong> |
| <strong>`ImGuiCond_FirstUseEver`</strong> | <strong>`imgui.ini` に記録がなければ、最初の 1 回</strong>（<strong>ユーザーが動かした位置は、保持される</strong>） |
| `ImGuiCond_Appearing` | <strong>ウィンドウが、表示されるたび</strong> |

<strong>普通は、`FirstUseEver`</strong>を使います（<strong>初期位置だけを決めて、あとはユーザーに任せる</strong>）。

### ウィンドウのフラグ

| フラグ | 意味 |
| --- | --- |
| `ImGuiWindowFlags_NoTitleBar` | <strong>タイトルバーなし</strong> |
| `ImGuiWindowFlags_NoResize` | 大きさを変えられない |
| `ImGuiWindowFlags_NoMove` | <strong>動かせない</strong> |
| `ImGuiWindowFlags_NoCollapse` | 折りたためない |
| <strong>`ImGuiWindowFlags_AlwaysAutoResize`</strong> | <strong>中身に合わせて、自動でサイズを変える</strong> |
| `ImGuiWindowFlags_NoSavedSettings` | <strong>`imgui.ini` に、保存しない</strong> |
| `ImGuiWindowFlags_NoBackground` | 背景を描かない |
| `ImGuiWindowFlags_MenuBar` | <strong>メニューバー</strong>を持つ |
| `ImGuiWindowFlags_HorizontalScrollbar` | 横スクロールバー |
| `ImGuiWindowFlags_NoInputs` | <strong>入力を、受け付けない</strong>（マウスを通す） |
| `ImGuiWindowFlags_NoFocusOnAppearing` / `NoNav` | <strong>フォーカスを奪わない</strong> |

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

<strong>右上に、半透明の FPS 表示</strong>を出す例です。<strong>`pivot (1, 0)`</strong>で、<strong>ウィンドウの右上を、指定位置に合わせます</strong>。

## 部品を並べる

| 関数 | 動き |
| --- | --- |
| <strong>`SameLine(offset, spacing)`</strong> | <strong>次の部品を、同じ行（右）</strong>に置く |
| `NewLine()` | <strong>改行</strong>（空の 1 行） |
| <strong>`Separator()`</strong> | <strong>横線</strong> |
| <strong>`Spacing()`</strong> | <strong>少しの縦の余白</strong> |
| `Dummy(ImVec2)` | <strong>見えない場所</strong>を確保（余白） |
| <strong>`Indent(w)` / `Unindent(w)`</strong> | <strong>字下げ</strong> |
| <strong>`BeginGroup()` / `EndGroup()`</strong> | <strong>複数の部品を、1 つの塊</strong>として扱う（`SameLine` や、ホバー判定の単位） |

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
| <strong>`SetNextItemWidth(w)`</strong> | <strong>次の 1 つの部品</strong>の幅 |
| <strong>`PushItemWidth(w)` / `PopItemWidth()`</strong> | <strong>ここから先の部品</strong>の幅 |
| `w < 0` | <strong>右端から、`-w` 手前まで</strong>（`-FLT_MIN` で、右端まで） |
| `CalcItemWidth()` | 現在の幅 |

```cpp
ImGui::SetNextItemWidth(-FLT_MIN);
ImGui::InputText("##name", &name);
```

### 空き領域・ウィンドウの大きさ

| 関数 | 返すもの |
| --- | --- |
| <strong>`GetContentRegionAvail()`</strong> | <strong>今の位置から、ウィンドウの端までの、残りの領域</strong> |
| `GetWindowSize()` / `GetWindowPos()` | <strong>ウィンドウの大きさ・位置</strong> |
| `GetCursorScreenPos()` | <strong>次の部品の描画位置</strong>（画面座標） |
| `GetTextLineHeightWithSpacing()` | <strong>1 行の高さ</strong> |

## 表（Table）と列

<strong>表形式</strong>でそろえて並べるなら、<strong>`BeginTable`</strong>です（[ウィジェット一覧](widgets.md#table)）。<strong>古い `Columns`</strong> は、<strong>機能が少なく</strong>、<strong>`BeginTable`</strong> を使います。

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

<strong>「ラベル」と「値」を、きれいにそろえる</strong>（インスペクター）ときに、<strong>2 列の表</strong>が便利です。

## 子ウィンドウとスクロール

<strong>ウィンドウの中に、独立してスクロールする領域</strong>を作ります。

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
| <strong>`BeginChild(id, size, flags)`</strong> | <strong>子ウィンドウ</strong>。<strong>`size` の `0`</strong> は、<strong>残りの領域いっぱい</strong> |
| <strong>`EndChild()`</strong> | <strong>`BeginChild` の戻り値に関係なく、必ず呼ぶ</strong> |
| <strong>`ImGuiChildFlags_Borders`</strong>（旧 `border = true`） | <strong>枠線</strong>を付ける |
| <strong>`SetScrollHereY(1.0f)`</strong> | <strong>一番下までスクロール</strong>（ログの自動スクロール） |
| `GetScrollY()` / `GetScrollMaxY()` | スクロール位置の取得 |

!!! note "バージョンで、引数が変わる"
    `BeginChild` の `bool border` 引数は、<strong>新しい版（1.90 以降）で `ImGuiChildFlags`</strong> に変わっています。<strong>使っているバージョンのヘッダ</strong>で、確認してください。

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

<strong>画面の上端のメニューバー</strong>は、<strong>`BeginMainMenuBar`</strong>（[ウィジェット一覧](widgets.md#menu)）です。<strong>下端のステータスバー</strong>は、<strong>メイン ビューポートに沿った、固定のウィンドウ</strong>で作ります。

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

<strong>`WorkPos` / `WorkSize`</strong> は、<strong>メニューバーなどを除いた、使える領域</strong>です。

## ID（ウィンドウと部品）

<strong>ID は、`ID スタック`</strong>で管理されます（<strong>ウィンドウ名 → `PushID` の値 → ラベル</strong>）。

| 書き方 | 意味 |
| --- | --- |
| `"ラベル"` | 表示と ID が同じ |
| `"ラベル##固定"` | <strong>表示は「ラベル」、ID は「ラベル##固定」</strong> |
| `"##固定"` | <strong>表示なし</strong>、ID だけ |
| <strong>`"表示名###ID"`</strong> | <strong>ID は、`###` 以降だけ</strong>（<strong>表示名が動的に変わっても、ウィンドウの位置が保たれる</strong>） |
| `PushID(i)` / `PopID()` | <strong>ループの中の、同じラベルを区別</strong> |

<strong>ウィンドウのタイトルに、動的な値（FPS など）</strong>を入れたい場合は、<strong>`"FPS: 60###fps"`</strong> のように、<strong>`###` で ID を固定</strong>します。<strong>固定しないと、タイトルが変わるたびに、別のウィンドウ</strong>になって、位置が戻ります。

## DPI とスケール

<strong>高 DPI のディスプレイ</strong>では、<strong>ImGui の文字や部品が、小さく見えます</strong>。

| 対策 | 説明 |
| --- | --- |
| <strong>`io.FontGlobalScale`</strong> | <strong>全体の拡大率</strong>（フォントのぼやけに注意） |
| <strong>フォントの大きさを、DPI に合わせる</strong> | `AddFontFromFileTTF(path, 16.0f * dpi_scale)`（[フォント](fonts.md)） |
| <strong>`style.ScaleAllSizes(scale)`</strong> | <strong>余白・角丸など、すべての大きさ</strong>を拡大（[スタイル](style.md#dpi)） |

## よくあるミス

??? failure "`SetNextWindowPos` を、`Begin` の後に呼ぶ"
    <strong>効きません</strong>。<strong>`Begin` の直前</strong>に呼びます。

??? failure "`SetNextWindowPos(..., ImGuiCond_Always)` で、ユーザーが動かせない"
    <strong>毎フレーム、戻されます</strong>。<strong>`FirstUseEver`</strong> にします。

??? failure "`BeginChild` が `false` のとき、`EndChild` を呼ばない"
    <strong>`BeginChild` は、戻り値に関係なく</strong>、`EndChild` が必要です。

??? failure "タイトルに動的な値を入れて、ウィンドウの位置が毎回リセットされる"
    <strong>`###` で、ID を固定</strong>します。

??? failure "`SameLine` の位置が、ずれる"
    <strong>`SameLine(0, 5)`</strong> のように、<strong>位置と間隔</strong>を指定します。<strong>幅の違う部品</strong>は、`SetNextItemWidth` で、そろえます。

??? failure "`Columns` を使って、機能が足りない"
    <strong>`BeginTable`</strong> に置き換えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>`Begin` / `End`</strong> でウィンドウ。<strong>位置・大きさは、`Begin` の直前に `SetNextWindow...`（`FirstUseEver`）</strong>
    - [x] <strong>縦に並ぶ</strong>。<strong>横は `SameLine`</strong>、<strong>まとまりは `BeginGroup`</strong>、<strong>幅は `SetNextItemWidth`</strong>
    - [x] 表は<strong>`BeginTable`</strong>、スクロール領域は<strong>`BeginChild`</strong>
    - [x] <strong>オーバーレイは、フラグ（`NoDecoration` など）と、位置の固定</strong>
    - [x] <strong>ID：`##`（見えない ID）、`###`（ID 固定）、`PushID`（ループ）</strong>
    - [x] <strong>高 DPI は、フォントとスタイルを、拡大</strong>

## 関連ページ

- [Dear ImGui](index.md)
- [ウィジェット一覧](widgets.md)
- [ドッキングとビューポート](docking.md)
- [スタイルとテーマ](style.md)
- [日本語フォントとアイコン](fonts.md)
