---
title: 日本語フォントとアイコン
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のフォント（日本語）

ImGui の**既定のフォント**は、英数字と一部の記号だけで、日本語を表示すると `?` になります。日本語を出すには、日本語を含むフォントファイル（`.ttf` / `.otf`）を読み込んで登録します。このページは日本語が `?` になる理由、フォントの読み込み方、文字範囲、大きさとぼやけ、複数フォントの結合（日本語 + アイコン）、新しい版の変更点をまとめます。

!!! tip "ポイント"
    - 既定のフォントは<strong>日本語を持たない</strong>。<strong>日本語フォントを読み込む</strong>。
    - 読み込みは `io.Fonts->AddFontFromFileTTF(パス, 大きさ, nullptr, 文字範囲)`。日本語は `GetGlyphRangesJapanese()`。
    - 読み込みは、初期化のとき、最初の `NewFrame` より前に行う（古い版）。
    - フォントの大きさは、ピクセル単位で指定。拡大（`FontGlobalScale`）するとぼやける。高 DPI は、大きなサイズで読み込む。
    - 日本語 + アイコンは、「結合（MergeMode）」で 1 つのフォントにまとめる。
    - 読み込む文字が多いほど、メモリを使う。必要な文字だけに絞ることもできる。
    - ImGui 1.92 以降は、動的フォントで文字範囲の指定が不要になった（バージョンで違う）。

!!! info "このページを読む前に"
    - [Dear ImGui](index.md)（このセクション全体の地図と、読む順番）
    - [Dear ImGui の導入（Visual Studio）](install.md)（ImGui の入れ方）

## 日本語が `?` になる理由

ImGui は、<strong>フォントのデータから、文字の絵（グリフ）を 1 枚の大きなテクスチャ（フォント アトラス）</strong>にまとめて、描画します。既定のフォント（`ProggyClean`）は、ASCII（英数字・記号）だけを含み、ひらがな・カタカナ・漢字の絵がありません。絵がない文字は、`?` で表示されます。

```text
既定のフォント：  A B C a b c 1 2 3 ...    （日本語の絵なし → ? に）
日本語フォント：  A B C あ い う 漢 字 ...   （日本語の絵あり）
```

日本語を出すには、日本語の絵を持つフォントを読み込む必要があります。

## 日本語フォントを読み込む

```cpp
ImGuiIO& io = ImGui::GetIO();

io.Fonts->AddFontFromFileTTF(
    "C:/Windows/Fonts/meiryo.ttc",
    18.0f,
    nullptr,
    io.Fonts->GetGlyphRangesJapanese());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| **フォントのパス** | `const char*` | `.ttf` / `.otf` / `.ttc`（`.ttc` は複数のフォントを 1 ファイルに入れたもの。最初のフォントが使われる） |
| 大きさ | `float` | ピクセル単位（`18.0f` ＝ 約 18 ピクセルの高さ） |
| **`ImFontConfig*`** | `const ImFontConfig*` | 追加の設定（結合・サイズなど）。`nullptr` で既定 |
| 文字範囲 | `const ImWchar*` | どの文字をアトラスに入れるか。`GetGlyphRangesJapanese()` は、日本語の一般的な文字 |

### フォントファイルの置き場所

| 方法 | 説明 |
| --- | --- |
| OS のフォントを使う（`C:/Windows/Fonts/...`） | 手軽。ただし、環境でフォントがないことがある（メイリオ・游ゴシックは、Windows に標準） |
| ゲームにフォントを同梱 | 確実。`assets/fonts/NotoSansJP-Regular.ttf` など。ライセンスを確認（Noto Sans JP は OFL。再配布できる） |

配布するゲームでは、フォントを同梱します（OS のフォントを再配布できない場合もあります）。

### 読み込みのタイミング

```cpp
ImGui::CreateContext();
ImGuiIO& io = ImGui::GetIO();

io.Fonts->AddFontFromFileTTF("assets/fonts/NotoSansJP-Regular.ttf", 18.0f, nullptr,
                             io.Fonts->GetGlyphRangesJapanese());

ImGui_ImplWin32_Init(hwnd);
ImGui_ImplDX11_Init(device, context);
```

フォントの登録は、バックエンドの初期化（`ImGui_ImplDX11_Init`）の前、または後でも最初の `NewFrame` より前に行います（古い版）。最初の描画の後に追加すると、アトラスの再構築が必要になります。

## 文字の範囲

| 関数 | 含まれる文字 |
| --- | --- |
| `GetGlyphRangesDefault()` | **基本のラテン文字**（既定） |
| `GetGlyphRangesJapanese()` | ひらがな・カタカナ・一般的な漢字（約 2500 字） |
| `GetGlyphRangesChineseSimplifiedCommon()` | 簡体字中国語 |
| `GetGlyphRangesKorean()` | 韓国語 |
| `GetGlyphRangesCyrillic()` | キリル文字 |

!!! warning "「一般的な漢字」だけ"
    `GetGlyphRangesJapanese()` は、日常的によく使う漢字（約 2500 字）だけを含みます。人名・地名の珍しい漢字は`?` になることがあります。もっと必要なら、自分で範囲を作るか、新しい版の動的フォントを使います。

### 自分で範囲を作る

```cpp
ImFontGlyphRangesBuilder builder;
builder.AddRanges(io.Fonts->GetGlyphRangesJapanese());
builder.AddText("髙﨑");
static ImVector<ImWchar> ranges;
builder.BuildRanges(&ranges);

io.Fonts->AddFontFromFileTTF("font.ttf", 18.0f, nullptr, ranges.Data);
```

ゲームで実際に使う文字だけ（シナリオ・UI の文字列を集めて）`AddText` で追加すると、アトラスが小さくなります。

## フォントの大きさと、ぼやけ

**フォントは読み込んだ大きさでアトラスに描かれます**。

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| 文字がぼやける | `io.FontGlobalScale` で、後から拡大している | 最初から、大きなサイズで読み込む |
| 高 DPI で文字が小さい | ピクセル数が足りない | **`18.0f * dpi_scale`** で読み込む（[スタイル](style.md#dpi)） |
| 小さい文字が読みにくい | フォントが薄い・ヒンティングなし | 大きさを上げる、`OversampleH = 2`（既定）、太めのフォント |

```cpp
ImFontConfig config;
config.OversampleH = 3;
config.OversampleV = 2;
config.PixelSnapH = true;

io.Fonts->AddFontFromFileTTF("font.ttf", 18.0f, &config, io.Fonts->GetGlyphRangesJapanese());
```

| 設定 | 意味 |
| --- | --- |
| `OversampleH` / `OversampleV` | アトラスに大きめに描いてから縮小して、滑らかに（メモリは増える） |
| `PixelSnapH` | 文字の位置をピクセルの境界に揃える（くっきり） |
| `GlyphOffset` | 文字を上下左右にずらす（フォントによる、ずれの補正） |

## 複数のフォントを結合する（日本語 + アイコン）

**1 つのフォントに日本語もアイコンも**入れたいときは、結合（MergeMode）します。

```cpp
io.Fonts->AddFontFromFileTTF("NotoSansJP-Regular.ttf", 18.0f, nullptr,
                             io.Fonts->GetGlyphRangesJapanese());

static const ImWchar icon_ranges[] = {0xf000, 0xf3ff, 0};
ImFontConfig icon_config;
icon_config.MergeMode = true;
icon_config.PixelSnapH = true;
icon_config.GlyphMinAdvanceX = 18.0f;
io.Fonts->AddFontFromFileTTF("fa-solid-900.ttf", 16.0f, &icon_config, icon_ranges);
```

| 設定 | 意味 |
| --- | --- |
| `MergeMode = true` | 直前に読み込んだフォントに文字を足す（新しいフォントを作らない） |
| `GlyphMinAdvanceX` | アイコンの最小の幅（等幅にそろえて、並べやすく） |
| アイコンの範囲 | Font Awesome の場合、`0xf000`〜`0xf3ff`（私用領域） |

### アイコン フォント（Font Awesome など） {#icons}

Font Awesome（無料版あり）などのアイコン フォントを使うと、ボタンやメニューにアイコンを付けられます。

```cpp
#include "IconsFontAwesome6.h"

if (ImGui::Button(ICON_FA_FLOPPY_DISK " 保存")) Save();
ImGui::Text(ICON_FA_TRASH " 削除");
```

`IconsFontAwesome6.h`（IconFontCppHeaders で配布）にアイコンの名前と文字コードがマクロとして定義されています。文字列にそのまま連結します。

## 複数のフォントを使い分ける

**見出しだけ、大きなフォント**にしたいときは、複数のフォントを登録して、`PushFont` で切り替えます。

```cpp
ImFont* font_normal = io.Fonts->AddFontFromFileTTF("font.ttf", 18.0f, nullptr, ranges);
ImFont* font_large = io.Fonts->AddFontFromFileTTF("font.ttf", 32.0f, nullptr, ranges);

ImGui::PushFont(font_large);
ImGui::Text("タイトル");
ImGui::PopFont();
```

| 点 | 説明 |
| --- | --- |
| サイズごとに別のフォントとして登録 | アトラスが大きくなる |
| `PushFont` / `PopFont` | 一時的に切り替える（個数をそろえる） |
| `io.FontDefault` | 既定のフォントを指定する |

## アトラスの大きさとメモリ

**フォント アトラスは、全文字の絵を詰めた、1 枚のテクスチャ**です。

| 要素 | 影響 |
| --- | --- |
| 日本語フォント（2500 字） | 数 MB のテクスチャ（サイズによる） |
| フォントの大きさ | 大きいほど、メモリを使う（面積に比例） |
| フォントの数・サイズの種類 | 増えるほど、アトラスが大きくなる |
| オーバーサンプル | 増やすとメモリが増える |
| 起動時間 | 文字が多いとアトラスの構築が数百ミリ秒かかる |

対策：文字を必要なものだけに絞る、フォントのサイズを少なくする、構築をロード中に済ませる。

## 新しい版（動的フォント）

**ImGui 1.92 以降**では、フォントの仕組みが大きく変わりました。

| 項目 | 旧（〜1.91） | 新（1.92〜） |
| --- | --- | --- |
| 文字範囲の指定 | 必要（`GetGlyphRanges...`） | 不要（使われた文字をその場でアトラスに追加） |
| フォントの大きさ | 読み込み時に固定（サイズごとに別のフォント） | `PushFont(font, size)` などで動的に変えられる |
| アトラスの構築 | 最初に全部 | 必要な文字だけ、実行時に |

新しい版では日本語の漢字を全部入れる必要がなくなり、メモリと起動時間が減ります。使っているバージョンの、`docs/FONTS.md` と変更履歴を確認してください（API が変わっているため、このページの旧版の書き方は、そのままでは動かない場合があります）。

## よくあるミス

??? failure "日本語が `?` のまま"
    **日本語フォントを読み込んでいません**。`GetGlyphRangesJapanese()` を渡します（旧版）。

??? failure "フォントが見つからず、アサートで落ちる"
    パスが違う（相対パスは実行ファイルの場所ではなく、カレントディレクトリから）。パスを確かめます。

??? failure "`io.FontGlobalScale` で拡大して、ぼやける"
    大きなサイズで読み込みます。

??? failure "最初の描画の後にフォントを追加して、反映されない"
    古い版は最初の `NewFrame` の前に登録します。

??? failure "漢字の一部だけ `?` になる"
    一般的な漢字の範囲外です。`AddText` で必要な文字を足すか、新しい版の動的フォントにします。

??? failure "アイコンが枠だけ・文字化けする"
    結合（`MergeMode`）の順番（日本語の後にアイコン）と、範囲を確認します。アイコン フォントの文字コードの範囲が違う場合もあります。

??? failure "OS のフォントを同梱せずに配布して、他の PC で表示されない"
    フォントをゲームに同梱します（ライセンスを確認）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日本語が `?` なのは、既定のフォントに日本語の絵がないから
    - [x] `AddFontFromFileTTF(パス, 大きさ, nullptr, GetGlyphRangesJapanese())` で、日本語フォントを読み込む
    - [x] フォントは、ゲームに同梱（ライセンスに注意）。読み込みは最初の `NewFrame` の前（旧版）
    - [x] 拡大は、ぼやける。最初から、大きなサイズ（DPI 倍）で読み込む
    - [x] 日本語 + アイコンは、`MergeMode`。見出し用の大きなフォントは、`PushFont`
    - [x] 1.92 以降は、動的フォント（文字範囲の指定が不要）

## 関連ページ

- [Dear ImGui](index.md)
- [スタイルとテーマ](style.md)
- [ウィジェット一覧](widgets.md)
- [文字コードの基礎](../../encoding/unicode-basics.md)
- [Windows API と文字コード](../../encoding/windows-api.md)
