---
title: 早見表：フラグ
tags:
  - 外部ライブラリ
  - GUI
---

# 早見表：フラグ

ImGui の関数には、<strong>動作を細かく変える「フラグ」</strong>が付きます。`ImGuiXxxFlags_Yyy` という名前で、ビット OR（`|`）で組み合わせます。種類が多く、覚えきれないのでよく使うものを関数ごとに一覧にしました。

!!! tip "ポイント"
    - <strong>フラグは `|` で組み合わせる</strong>。<strong>`0` は「何も付けない」</strong>。
    - `ImGuiWindowFlags_`・`ImGuiInputTextFlags_`・`ImGuiTreeNodeFlags_`・`ImGuiTableFlags_`・`ImGuiSelectableFlags_`・`ImGuiComboFlags_`など、関数ごとに専用の型がある。
    - 型が違うフラグを渡すと、意味が変わる（コンパイルは通る）。名前の接頭辞を確認する。

!!! info "このページを読む前に"
    - [Dear ImGui](../index.md)（このセクション全体の地図と、読む順番）
    - [Dear ImGui の導入（Visual Studio）](../install.md)（ImGui の入れ方）

## ウィンドウ（ImGuiWindowFlags_）

| フラグ | 内容 |
| --- | --- |
| `NoTitleBar` | **タイトル バーなし** |
| `NoResize` | 大きさを変えられない |
| `NoMove` | 動かせない |
| `NoScrollbar` | スクロール バーなし |
| `NoScrollWithMouse` | ホイールでスクロールしない |
| `NoCollapse` | 折りたたみ不可 |
| `AlwaysAutoResize` | 中身に合わせて、自動で大きさを変える |
| `NoBackground` | 背景を描かない |
| `NoSavedSettings` | `.ini` に位置・大きさを保存しない |
| `NoMouseInputs` | マウス入力を受けない |
| `MenuBar` | メニュー バーを持つ |
| `HorizontalScrollbar` | 横スクロール バーを許可 |
| `NoFocusOnAppearing` | 現れたとき、フォーカスを奪わない |
| `NoBringToFrontOnFocus` | フォーカスしても手前に出さない |
| `NoNav` | キー・ゲームパッドの操作を受けない |
| `NoDecoration` | タイトル・スクロール・リサイズ・折りたたみを全部なし |
| `NoInputs` | 入力を全部受けない |
| `NoDocking` | ドッキング不可 |

```cpp
constexpr ImGuiWindowFlags kOverlayFlags =
    ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_AlwaysAutoResize |
    ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoFocusOnAppearing |
    ImGuiWindowFlags_NoNav | ImGuiWindowFlags_NoMove;
```

## 子ウィンドウ（ImGuiChildFlags_）

| フラグ | 内容 |
| --- | --- |
| `Borders` | **枠線を付ける**（旧 `border = true`） |
| `AlwaysUseWindowPadding` | ウィンドウの余白を使う |
| `ResizeX` / `ResizeY` | マウスで横／縦にリサイズ可能 |
| `AutoResizeX` / `AutoResizeY` | 中身に合わせて、横／縦を自動リサイズ |
| `FrameStyle` | 入力欄の見た目 |

## 文字入力（ImGuiInputTextFlags_）

| フラグ | 内容 |
| --- | --- |
| `CharsDecimal` | **数字と `.` `+` `-` だけ** |
| `CharsHexadecimal` | 16 進の文字だけ |
| `CharsUppercase` | 大文字に変換 |
| `CharsNoBlank` | 空白を受けない |
| `AutoSelectAll` | フォーカス時に全選択 |
| `EnterReturnsTrue` | Enter を押したときだけ true を返す |
| `CallbackCompletion` / `CallbackHistory` / `CallbackAlways` / `CallbackCharFilter` / `CallbackResize` | コールバックを呼ぶタイミング |
| `ReadOnly` | 読み取り専用 |
| `Password` | **`*` で隠す** |
| `NoUndoRedo` | Undo/Redo を無効 |
| `AllowTabInput` | Tab キーを文字として受ける |
| `CtrlEnterForNewLine` | 複数行で、Ctrl+Enter を改行に |
| `AlwaysOverwrite` | 上書きモード |

```cpp
ImGui::InputText("Name", buf, sizeof(buf), ImGuiInputTextFlags_EnterReturnsTrue);
ImGui::InputText("Pass", pass, sizeof(pass), ImGuiInputTextFlags_Password);
```

## ツリー（ImGuiTreeNodeFlags_）

| フラグ | 内容 |
| --- | --- |
| `Selected` | **選択状態の見た目** |
| `Framed` | 背景付き（`CollapsingHeader` の見た目） |
| `Leaf` | 葉（▶ なし・開閉しない） |
| `Bullet` | ▶ の代わりに「・」 |
| `OpenOnArrow` | ▶ をクリックしたときだけ開く |
| `OpenOnDoubleClick` | ダブルクリックで開く |
| `DefaultOpen` | 最初から開いておく |
| `NoTreePushOnOpen` | 開いても `TreePop` を要求しない（葉・独自処理） |
| `SpanAvailWidth` | 行全体をクリック可能に（幅いっぱい） |
| `SpanFullWidth` | ウィンドウの端まで |
| `FramePadding` | フレームの余白を使う |
| `AllowOverlap` | 他の項目との重なりを許す |

```cpp
ImGuiTreeNodeFlags flags = ImGuiTreeNodeFlags_OpenOnArrow | ImGuiTreeNodeFlags_SpanAvailWidth;
if (node.children.empty()) flags |= ImGuiTreeNodeFlags_Leaf | ImGuiTreeNodeFlags_NoTreePushOnOpen;
if (node.id == selected) flags |= ImGuiTreeNodeFlags_Selected;
bool open = ImGui::TreeNodeEx(node.name.c_str(), flags);
```

## 選択（ImGuiSelectableFlags_）

| フラグ | 内容 |
| --- | --- |
| `SpanAllColumns` | **全ての列にわたる** |
| `AllowDoubleClick` | ダブルクリックも検出 |
| `Disabled` | 選べない |
| `AllowOverlap` | 重なりを許す |
| `DontClosePopups` | ポップアップを閉じない |

## コンボ（ImGuiComboFlags_）

| フラグ | 内容 |
| --- | --- |
| `PopupAlignLeft` | **ポップアップを左揃え** |
| `HeightSmall` / `Regular` / `Large` / `Largest` | 一覧の高さ |
| `NoArrowButton` | 矢印ボタンなし |
| `NoPreview` | プレビュー文字なし |

## テーブル（ImGuiTableFlags_）

| フラグ | 内容 |
| --- | --- |
| `Resizable` | **列の幅をドラッグで変えられる** |
| `Reorderable` | 列を並べ替えられる |
| `Hideable` | 列を右クリックで隠せる |
| `Sortable` | ヘッダーのクリックで並べ替え |
| `RowBg` | 行を交互に色付け |
| `Borders` | 全ての枠線（`BordersH`・`BordersV`・`BordersOuter`・`BordersInner`） |
| `ScrollX` / `ScrollY` | スクロール可能 |
| `SizingFixedFit` | 列の幅を内容に合わせて固定 |
| `SizingStretchProp` | 列の幅を割合で伸縮 |
| `NoSavedSettings` | 設定を保存しない |
| `ContextMenuInBody` | 右クリック メニューを本文でも出す |
| `PadOuterX` | 外側の余白 |

### テーブルの列（ImGuiTableColumnFlags_）

| フラグ | 内容 |
| --- | --- |
| `WidthFixed` | 固定幅 |
| `WidthStretch` | 残りを伸縮 |
| `NoSort` | この列は並べ替え不可 |
| `DefaultSort` | 最初の並べ替え列 |
| `PreferSortDescending` | 最初に降順 |
| `NoResize` | この列はリサイズ不可 |
| `NoHide` | この列は隠せない |
| `DefaultHide` | 最初は隠しておく |

## 色の編集（ImGuiColorEditFlags_）

| フラグ | 内容 |
| --- | --- |
| `NoAlpha` | **アルファなし** |
| `AlphaBar` | アルファ バーを出す |
| `NoInputs` | 数値入力欄なし（見本だけ） |
| `NoLabel` | ラベルなし |
| `NoPicker` | ピッカーを出さない |
| `NoTooltip` | ツールチップなし |
| `DisplayRGB` / `DisplayHSV` / `DisplayHex` | 表示形式 |
| `Float` | 0〜1 の実数で表示 |
| `PickerHueBar` / `PickerHueWheel` | ピッカーの形式 |
| `HDR` | HDR（1 を超える値）を許す |

## スライダー（ImGuiSliderFlags_）

| フラグ | 内容 |
| --- | --- |
| `AlwaysClamp` | **直接入力でも範囲に収める** |
| `Logarithmic` | 対数スケール（桁の違う値） |
| `NoRoundToFormat` | 表示形式で丸めない |
| `NoInput` | Ctrl+クリックの入力を無効 |

## ホバー判定（ImGuiHoveredFlags_）

| フラグ | 内容 |
| --- | --- |
| `AllowWhenBlockedByPopup` | ポップアップが上にあっても、true |
| `AllowWhenBlockedByActiveItem` | 他の項目がアクティブでも、true |
| `AllowWhenOverlappedByItem` | 他の項目に重なっていても、true |
| `DelayNormal` / `DelayShort` | 一定時間ホバーして初めて true（ツールチップ向け） |
| `ForTooltip` | ツールチップ用の標準的な設定 |
| `RootAndChildWindows` | 子ウィンドウも含める |

## ドラッグ＆ドロップ（ImGuiDragDropFlags_）

| フラグ | 内容 |
| --- | --- |
| `SourceNoPreviewTooltip` | ドラッグ中のプレビューを出さない |
| `SourceAllowNullID` | ID なしの項目もソースにできる |
| `AcceptBeforeDelivery` | 離す前から、ターゲットが受け取る（プレビュー用） |
| `AcceptNoDrawDefaultRect` | ターゲットの強調枠を描かない |

## 設定・方向

| 型 | 主な値 |
| --- | --- |
| `ImGuiDir_` | `Left` `Right` `Up` `Down`（`ArrowButton` など） |
| `ImGuiMouseButton_` | `Left`(0) `Right`(1) `Middle`(2) |
| `ImGuiCond_` | `Always` `Once` `FirstUseEver` `Appearing`（`SetNextWindow…`） |
| `ImGuiConfigFlags_` | `NavEnableKeyboard` `DockingEnable` `ViewportsEnable` など（`io.ConfigFlags`） |
| `ImGuiDockNodeFlags_` | `PassthruCentralNode` `NoResize` `AutoHideTabBar` など（`DockSpace`） |

## 色の名前（ImGuiCol_）

| 色の名前 | どこの色か |
| --- | --- |
| `Text` / `TextDisabled` | 文字／無効な文字 |
| `WindowBg` / `ChildBg` / `PopupBg` | ウィンドウ／子／ポップアップの背景 |
| `Border` | 枠線 |
| `FrameBg` / `FrameBgHovered` / `FrameBgActive` | 入力欄・スライダーの下地 |
| `TitleBg` / `TitleBgActive` / `TitleBgCollapsed` | タイトル バー |
| `MenuBarBg` | メニュー バー |
| `ScrollbarBg` / `ScrollbarGrab` | スクロール バー |
| `CheckMark` | チェックの印 |
| `SliderGrab` / `SliderGrabActive` | スライダーのつまみ |
| `Button` / `ButtonHovered` / `ButtonActive` | ボタン |
| `Header` / `HeaderHovered` / `HeaderActive` | 折りたたみ・選択行 |
| `Separator` | 区切り線 |
| `Tab` / `TabHovered` / `TabSelected`（旧 `TabActive`） | タブ |
| `DockingPreview` / `DockingEmptyBg` | ドッキングのプレビュー |
| `PlotLines` / `PlotHistogram` | グラフの線・棒 |
| `TableHeaderBg` / `TableRowBg` / `TableRowBgAlt` | テーブル |
| `DragDropTarget` | ドロップ先の強調 |
| `NavHighlight` | キー操作のハイライト |

## 関連ページ

- [関数早見表](index.md)
- [ウィジェット](widgets.md)
- [コンテナ](containers.md)
- [スタイルとテーマ（解説）](../style.md)
