---
title: 日本語フォントとアイコン
tags:
  - 外部ライブラリ
  - GUI
---

# ImGui のフォント（日本語）

ImGui の**既定のフォント**は、**英数字と一部の記号だけ**で、**日本語を表示すると `?` になります**。**日本語を出すには、日本語を含むフォントファイル**（`.ttf` / `.otf`）を、**読み込んで登録**します。このページは、**日本語が `?` になる理由**、**フォントの読み込み方**、**文字範囲**、**大きさとぼやけ**、<strong>複数フォントの結合（日本語 + アイコン）</strong>、**新しい版の変更点**をまとめます。

!!! tip "ポイント"
    - 既定のフォントは<strong>日本語を持たない</strong>。<strong>日本語フォントを、読み込む</strong>。
    - 読み込みは <strong>`io.Fonts->AddFontFromFileTTF(パス, 大きさ, nullptr, 文字範囲)`</strong>。日本語は <strong>`GetGlyphRangesJapanese()`</strong>。
    - 読み込みは、<strong>初期化のとき、最初の `NewFrame` より前</strong>に行う（古い版）。
    - <strong>フォントの大きさは、ピクセル単位で指定</strong>。<strong>拡大（`FontGlobalScale`）すると、ぼやける</strong>。<strong>高 DPI は、大きなサイズで読み込む</strong>。
    - <strong>日本語 + アイコンは、「結合（MergeMode）」で 1 つのフォントにまとめる</strong>。
    - <strong>読み込む文字が多いほど、メモリを使う</strong>。<strong>必要な文字だけに絞る</strong>こともできる。
    - <strong>ImGui 1.92 以降は、動的フォント</strong>で、<strong>文字範囲の指定が不要</strong>になった（バージョンで違う）。

## 日本語が `?` になる理由

ImGui は、<strong>フォントのデータから、文字の絵（グリフ）を、1 枚の大きなテクスチャ（フォント アトラス）</strong>にまとめて、描画します。**既定のフォント**（`ProggyClean`）は、**ASCII**（英数字・記号）だけを含み、**ひらがな・カタカナ・漢字の絵がありません**。**絵がない文字は、`?` で表示**されます。

```text
既定のフォント：  A B C a b c 1 2 3 ...    （日本語の絵なし → ? に）
日本語フォント：  A B C あ い う 漢 字 ...   （日本語の絵あり）
```

**日本語を出すには、日本語の絵を持つフォントを、読み込む**必要があります。

## 日本語フォントを読み込む

```cpp
ImGuiIO& io = ImGui::GetIO();

io.Fonts->AddFontFromFileTTF(
    "C:/Windows/Fonts/meiryo.ttc",
    18.0f,
    nullptr,
    io.Fonts->GetGlyphRangesJapanese());
```

| 引数 | 意味 |
| --- | --- |
| **フォントのパス** | `.ttf` / `.otf` / `.ttc`（`.ttc` は、**複数のフォントを 1 ファイル**に入れたもの。最初のフォントが使われる） |
| **大きさ** | **ピクセル単位**（`18.0f` ＝ 約 18 ピクセルの高さ） |
| **`ImFontConfig*`** | **追加の設定**（結合・サイズなど）。`nullptr` で既定 |
| **文字範囲** | **どの文字を、アトラスに入れるか**。**`GetGlyphRangesJapanese()`** は、**日本語の、一般的な文字** |

### フォントファイルの置き場所

| 方法 | 説明 |
| --- | --- |
| **OS のフォントを使う**（`C:/Windows/Fonts/...`） | **手軽**。ただし、**環境で、フォントがない**ことがある（**メイリオ・游ゴシック**は、Windows に標準） |
| **ゲームに、フォントを同梱** | **確実**。**`assets/fonts/NotoSansJP-Regular.ttf`** など。**ライセンスを確認**（Noto Sans JP は OFL。再配布できる） |

**配布するゲームでは、フォントを、同梱**します（OS のフォントを、再配布できない場合もあります）。

### 読み込みのタイミング

```cpp
ImGui::CreateContext();
ImGuiIO& io = ImGui::GetIO();

io.Fonts->AddFontFromFileTTF("assets/fonts/NotoSansJP-Regular.ttf", 18.0f, nullptr,
                             io.Fonts->GetGlyphRangesJapanese());

ImGui_ImplWin32_Init(hwnd);
ImGui_ImplDX11_Init(device, context);
```

**フォントの登録は、バックエンドの初期化（`ImGui_ImplDX11_Init`）の前、または後でも、最初の `NewFrame` より前**に行います（**古い版**）。**最初の描画の後**に追加すると、**アトラスの再構築**が必要になります。

## 文字の範囲

| 関数 | 含まれる文字 |
| --- | --- |
| `GetGlyphRangesDefault()` | **基本のラテン文字**（既定） |
| **`GetGlyphRangesJapanese()`** | <strong>ひらがな・カタカナ・一般的な漢字（約 2500 字）</strong> |
| `GetGlyphRangesChineseSimplifiedCommon()` | 簡体字中国語 |
| `GetGlyphRangesKorean()` | 韓国語 |
| `GetGlyphRangesCyrillic()` | キリル文字 |

!!! warning "「一般的な漢字」だけ"
    `GetGlyphRangesJapanese()` は、**日常的によく使う漢字**（約 2500 字）だけを含みます。**人名・地名の、珍しい漢字**は、**`?`** になることがあります。**もっと必要**なら、**自分で範囲を作る**か、**新しい版の動的フォント**を使います。

### 自分で範囲を作る

```cpp
ImFontGlyphRangesBuilder builder;
builder.AddRanges(io.Fonts->GetGlyphRangesJapanese());
builder.AddText("髙﨑");
static ImVector<ImWchar> ranges;
builder.BuildRanges(&ranges);

io.Fonts->AddFontFromFileTTF("font.ttf", 18.0f, nullptr, ranges.Data);
```

**ゲームで実際に使う文字だけ**（**シナリオ・UI の文字列を集めて**）**`AddText`** で追加すると、**アトラスが、小さく**なります。

## フォントの大きさと、ぼやけ

**フォントは、読み込んだ大きさで、アトラスに描かれます**。

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| **文字がぼやける** | **`io.FontGlobalScale` で、後から拡大**している | **最初から、大きなサイズで読み込む** |
| **高 DPI で、文字が小さい** | **ピクセル数が、足りない** | **`18.0f * dpi_scale`** で読み込む（[スタイル](style.md#dpi)） |
| **小さい文字が、読みにくい** | **フォントが、薄い・ヒンティングなし** | **大きさを上げる**、**`OversampleH = 2`**（既定）、**太めのフォント** |

```cpp
ImFontConfig config;
config.OversampleH = 3;
config.OversampleV = 2;
config.PixelSnapH = true;

io.Fonts->AddFontFromFileTTF("font.ttf", 18.0f, &config, io.Fonts->GetGlyphRangesJapanese());
```

| 設定 | 意味 |
| --- | --- |
| **`OversampleH` / `OversampleV`** | **アトラスに、大きめに描いてから縮小**して、**滑らかに**（メモリは増える） |
| **`PixelSnapH`** | **文字の位置を、ピクセルの境界に**揃える（くっきり） |
| `GlyphOffset` | **文字を、上下左右に、ずらす**（フォントによる、ずれの補正） |

## 複数のフォントを結合する（日本語 + アイコン）

**1 つのフォントに、日本語もアイコンも**入れたいときは、<strong>結合（MergeMode）</strong>します。

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
| **`MergeMode = true`** | **直前に読み込んだフォントに、文字を足す**（新しいフォントを作らない） |
| **`GlyphMinAdvanceX`** | **アイコンの、最小の幅**（等幅にそろえて、並べやすく） |
| **アイコンの範囲** | Font Awesome の場合、**`0xf000`〜`0xf3ff`**（私用領域） |

### アイコン フォント（Font Awesome など） {#icons}

**Font Awesome**（無料版あり）などの**アイコン フォント**を使うと、**ボタンやメニューに、アイコン**を付けられます。

```cpp
#include "IconsFontAwesome6.h"

if (ImGui::Button(ICON_FA_FLOPPY_DISK " 保存")) Save();
ImGui::Text(ICON_FA_TRASH " 削除");
```

**`IconsFontAwesome6.h`**（**IconFontCppHeaders** で配布）に、**アイコンの名前と、文字コード**が、**マクロ**として定義されています。**文字列に、そのまま連結**します。

## 複数のフォントを使い分ける

**見出しだけ、大きなフォント**にしたいときは、**複数のフォントを登録**して、**`PushFont`** で切り替えます。

```cpp
ImFont* font_normal = io.Fonts->AddFontFromFileTTF("font.ttf", 18.0f, nullptr, ranges);
ImFont* font_large = io.Fonts->AddFontFromFileTTF("font.ttf", 32.0f, nullptr, ranges);

ImGui::PushFont(font_large);
ImGui::Text("タイトル");
ImGui::PopFont();
```

| 点 | 説明 |
| --- | --- |
| **サイズごとに、別のフォント**として登録 | **アトラスが大きく**なる |
| **`PushFont` / `PopFont`** | **一時的に切り替える**（**個数をそろえる**） |
| **`io.FontDefault`** | **既定のフォント**を、指定する |

## アトラスの大きさとメモリ

**フォント アトラスは、全文字の絵を詰めた、1 枚のテクスチャ**です。

| 要素 | 影響 |
| --- | --- |
| **日本語フォント**（2500 字） | **数 MB** のテクスチャ（サイズによる） |
| **フォントの大きさ** | **大きいほど、メモリを使う**（面積に比例） |
| **フォントの数・サイズの種類** | **増えるほど、アトラスが大きく**なる |
| **オーバーサンプル** | **増やすと、メモリが増える** |
| **起動時間** | **文字が多いと、アトラスの構築が、数百ミリ秒かかる** |

**対策**：**文字を、必要なものだけに絞る**、**フォントのサイズを、少なくする**、**構築を、ロード中に済ませる**。

## 新しい版（動的フォント）

**ImGui 1.92 以降**では、**フォントの仕組みが、大きく変わり**ました。

| 項目 | 旧（〜1.91） | 新（1.92〜） |
| --- | --- | --- |
| **文字範囲の指定** | **必要**（`GetGlyphRanges...`） | **不要**（**使われた文字を、その場で、アトラスに追加**） |
| **フォントの大きさ** | **読み込み時に固定**（サイズごとに別のフォント） | **`PushFont(font, size)` などで、動的に変えられる** |
| **アトラスの構築** | **最初に、全部** | **必要な文字だけ、実行時に** |

**新しい版では、日本語の漢字を、全部入れる必要がなくなり**、**メモリと起動時間が減ります**。**使っているバージョンの、`docs/FONTS.md` と変更履歴**を、確認してください（**API が変わっている**ため、このページの旧版の書き方は、そのままでは動かない場合があります）。

## よくあるミス

??? failure "日本語が `?` のまま"
    **日本語フォントを、読み込んでいません**。**`GetGlyphRangesJapanese()`** を渡します（旧版）。

??? failure "フォントが見つからず、アサートで落ちる"
    **パスが違う**（相対パスは、**実行ファイルの場所**ではなく、**カレントディレクトリ**から）。**パスを、確かめます**。

??? failure "`io.FontGlobalScale` で拡大して、ぼやける"
    **大きなサイズで読み込みます**。

??? failure "最初の描画の後に、フォントを追加して、反映されない"
    **古い版は、最初の `NewFrame` の前**に登録します。

??? failure "漢字の一部だけ `?` になる"
    **一般的な漢字の範囲外**です。**`AddText` で、必要な文字を足す**か、**新しい版の動的フォント**にします。

??? failure "アイコンが、枠だけ・文字化けする"
    **結合（`MergeMode`）の順番**（日本語の後にアイコン）と、**範囲**を確認します。**アイコン フォントの、文字コードの範囲**が違う場合もあります。

??? failure "OS のフォントを、同梱せずに配布して、他の PC で表示されない"
    **フォントを、ゲームに同梱**します（**ライセンスを確認**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日本語が `?` なのは、<strong>既定のフォントに日本語の絵がないから</strong>
    - [x] <strong>`AddFontFromFileTTF(パス, 大きさ, nullptr, GetGlyphRangesJapanese())`</strong> で、<strong>日本語フォントを、読み込む</strong>
    - [x] <strong>フォントは、ゲームに同梱</strong>（ライセンスに注意）。<strong>読み込みは、最初の `NewFrame` の前</strong>（旧版）
    - [x] <strong>拡大は、ぼやける</strong>。<strong>最初から、大きなサイズ（DPI 倍）</strong>で読み込む
    - [x] <strong>日本語 + アイコンは、`MergeMode`</strong>。<strong>見出し用の大きなフォントは、`PushFont`</strong>
    - [x] <strong>1.92 以降は、動的フォント</strong>（<strong>文字範囲の指定が、不要</strong>）

## 関連ページ

- [Dear ImGui](index.md)
- [スタイルとテーマ](style.md)
- [ウィジェット一覧](widgets.md)
- [文字コードの基礎](../../encoding/unicode-basics.md)
- [Windows API と文字コード](../../encoding/windows-api.md)
