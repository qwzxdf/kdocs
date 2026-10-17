---
title: 外部ライブラリと文字コード
tags:
  - 文字コード
---

# 外部ライブラリと文字コード

ゲームでは、ウィンドウ、描画、音、GUI、JSON、画像など、**たくさんの外部ライブラリ**を使います。ライブラリごとに、**文字列を受け取るときの文字コード**（UTF-8 か、UTF-16 か、ANSI か）が決まっています。それを知らずに、文字列を渡すと、文字化けや、ファイルが開けない原因になります。このページは、**よく使うライブラリが、何を要求するか**を一覧にし、あわせて、**文字コードを本格的に扱うライブラリ**（utfcpp、simdutf、ICU）を紹介します。

!!! tip "ポイント"
    - <strong>ほとんどのライブラリは UTF-8（`char*`）</strong>。ゲームの文字列（UTF-8）を、そのまま渡せる。
    - <strong>Windows のネイティブ系（DirectX 関連、Win32）は UTF-16（`wchar_t*`）</strong>。境界で変換する。
    - <strong>パス（ファイル名）で、日本語が壊れやすい。</strong>内部で `fopen`（ANSI）を使うライブラリに注意。
    - 迷ったら、<strong>ライブラリのドキュメントで「UTF-8」「wide」「Unicode」を検索</strong>。
    - 文字の<strong>切り取り・数え方・並べ替え</strong>が必要なら、<strong>utfcpp / ICU</strong>。検証だけなら simdutf。

## ライブラリごとの要求

### UTF-8（char*）を要求するもの

| ライブラリ | 文字列の扱い | 注意 |
| --- | --- | --- |
| <strong>[Dear ImGui](../libs/imgui/index.md)</strong> | **UTF-8** | **日本語フォント**（グリフ範囲）を読み込まないと、`?` や四角になる（[ImGui のフォント](../libs/imgui/fonts.md)） |
| <strong>[nlohmann/json](../libs/serialization/nlohmann-json.md)</strong> | **UTF-8** | 不正な UTF-8 を `dump()` すると例外（`error_handler_t::replace` で、置き換えにできる）。BOM は、読む前に取り除く |
| <strong>[simdjson](../libs/serialization/simdjson.md)</strong> | UTF-8 | 不正な UTF-8 は、エラー |
| <strong>[rapidyaml](../libs/serialization/rapidyaml.md)</strong> | UTF-8 | |
| **SDL2 / SDL3** | **UTF-8**（ウィンドウ タイトル、パス） | Windows でも UTF-8 でよい。内部で変換する |
| **GLFW** | **UTF-8**（ウィンドウ タイトル、クリップボード） | 文字入力のコールバックは、<strong>コードポイント（`unsigned int`）</strong> で来る |
| **FMOD** | **UTF-8**（ファイル名） | Windows でも UTF-8 でよい |
| **Jolt Physics** | 文字列をほとんど扱わない | デバッグ名くらい |
| <strong>spdlog / {fmt}</strong> | UTF-8 | Windows のコンソールに出すとき、`/utf-8` が必要（{fmt} は、`/utf-8` を要求する） |
| **sqlite3** | **UTF-8**（`sqlite3_open`）、UTF-16 用の関数（`_16`）もある | |
| **OpenGL / Vulkan** | シェーダーは ASCII。ウィンドウ名は、ウィンドウ ライブラリ次第 | |

### UTF-16（wchar_t*）を要求するもの

| ライブラリ | 文字列の扱い | 注意 |
| --- | --- | --- |
| **Win32 API の `W` 版**（`CreateFileW`、`MessageBoxW`） | **UTF-16** | [Windows API](windows-api.md) |
| **Direct3D の `D3DCompileFromFile`** | `LPCWSTR`（UTF-16）のパス | |
| **DirectXTex / DirectXTK**（`LoadFromDDSFile`、`CreateDDSTextureFromFile`） | **`wchar_t*`（UTF-16）のパス** | UTF-8 のパスを、変換して渡す |
| **XAudio2 / Media Foundation** | UTF-16 のパス | |
| **`std::filesystem::path`**（Windows） | **内部は UTF-16** | `u8string()` / `wstring()` で取り出す |
| **Qt** | `QString`（UTF-16）。`QString::fromUtf8(...)` で変換 | |

### 注意が必要なもの（ANSI や、内部の `fopen`）

| ライブラリ | 問題 | 対策 |
| --- | --- | --- |
| **stb_image / stb_vorbis など** | `stbi_load(filename)` が、内部で `fopen` を使う。**Windows では、日本語パスが、ANSI として解釈されて失敗する** | ファイルを自分で読んで、`stbi_load_from_memory`。または、ワイド文字版の `fopen` に差し替える（`STBI_WINDOWS_UTF8` を定義して、`stbi_convert_wchar_to_utf8` を使う） |
| **`fopen` / `std::ifstream(const char*)`** | ANSI のパス | `std::filesystem::path`、`_wfopen` |
| **古い C ライブラリ**（zlib の `gzopen` など） | ANSI のパス | メモリに読んでから渡す。または、`gzopen_w` などの W 版 |
| **`main` の `argv`** | ANSI | `GetCommandLineW`、マニフェストの UTF-8 |
| **libpng / libjpeg** | ファイル ハンドル（`FILE*`）を受け取る | `_wfopen` で開いて渡す |
| **FreeType**（フォントの読み込み） | ファイル名は ANSI（`FT_New_Face`） | メモリに読んで `FT_New_Memory_Face` |

<strong>パスで困ったら、「ファイルを自分で（W 版で）読んで、メモリのデータをライブラリに渡す」</strong>のが、一番確実です。

## パスの方針

<div class="anim" data-type="graph" data-label="ライブラリには、メモリ上のデータを渡す">
n p パス_（UTF-8_std::string） 0 1
n f std::filesystem::path_で開く 1 0
n l ライブラリへ_メモリ上のデータ 1 2
l p f - 自分で読む
l p l - ファイル名は渡さない
</div>

| 方針 | 理由 |
| --- | --- |
| **ファイルは、自分で読む** | パスの文字コードの問題が、ライブラリに入らない |
| **ライブラリには、メモリ（`const void*` + サイズ）を渡す** | `stbi_load_from_memory`、`FT_New_Memory_Face`、`FMOD_CREATESOUNDEXINFO` など |
| **アセットのパスは、ASCII にする** | `data/textures/hero.png`。日本語のファイル名は、避ける |
| **ユーザーが選ぶパス**（セーブ、スクリーンショット）だけ、日本語を考慮する | `std::filesystem::path` と W 版 |

## 文字コードを扱うライブラリ

自分で文字コードの処理（変換、検証、切り取り、正規化）を書くのは大変で、間違いやすいので、**ライブラリに任せる**のが安全です。

### 比較

| ライブラリ | 向いていること | 大きさ | 導入 |
| --- | --- | --- | --- |
| **utfcpp**（`utf8cpp`） | UTF-8 の検証・変換・文字の走査。軽くて簡単 | ヘッダだけ | `vcpkg install utfcpp` |
| **simdutf** | **非常に速い**検証・変換（SIMD）。大量のデータ | ライブラリ | `vcpkg install simdutf` |
| **ICU** | **何でもできる**。正規化、照合（五十音順）、書記素の分割、大文字小文字（日本語対応）、変換、日付・数値の書式 | 大きい（数十 MB） | `vcpkg install icu` |
| **Boost.Locale** | ICU を使った、C++ らしい API | 大きい | `vcpkg install boost-locale` |
| **utf8proc** | **正規化**（NFC / NFD）、文字の分類。小さい | 小さい | `vcpkg install utf8proc` |
| **ztd.text**（将来の標準を見据えた） | 文字コードの変換の、標準提案の実装 | | |

### utfcpp の使い方

```cpp
#include <utf8.h>

#include <string>

std::string text = "勇者アリス";

// 検証：UTF-8 として正しいか
bool ok = utf8::is_valid(text);

// コードポイント数（文字数）
std::size_t count = utf8::distance(text.begin(), text.end());    // 5

// 先頭から N 文字だけ取り出す（文字の途中で切らない）
auto it = text.begin();
utf8::advance(it, 2, text.end());                                // 2 文字進む
std::string head(text.begin(), it);                              // "勇者"

// UTF-8 ⇔ UTF-16 ⇔ UTF-32
std::u16string u16 = utf8::utf8to16(text);
std::u32string u32 = utf8::utf8to32(text);

// コードポイントを 1 つずつ取り出す
for (auto p = text.begin(); p != text.end();) {
  char32_t cp = utf8::next(p, text.end());                       // U+52C7、U+8005、...
}
```

### simdutf の使い方

```cpp
#include <simdutf.h>

// 検証（非常に速い）
bool ok = simdutf::validate_utf8(text.data(), text.size());

// UTF-8 → UTF-16
std::u16string u16(text.size(), u'\0');
std::size_t written = simdutf::convert_utf8_to_utf16le(text.data(), text.size(),
                                                       u16.data());
u16.resize(written);            // 失敗すると 0 が返る
```

巨大なファイル（セーブ・シナリオ・ログ）の検証・変換に、威力を発揮します。

### ICU でできること

| 機能 | 使いどころ |
| --- | --- |
| **書記素クラスタの分割**（`BreakIterator`） | 「ユーザーが見る 1 文字」で、切り取る・数える（絵文字、結合文字） |
| **正規化**（`Normalizer2`） | NFC にそろえて、比較する |
| **照合**（`Collator`） | **五十音順などの、言語に合った並べ替え** |
| **大文字・小文字変換**（`toUpper`、`toLower`） | 全角英字や、ギリシャ文字を含む |
| **文字の性質**（`u_charType`、`u_isalpha`） | ひらがな・カタカナ・漢字・絵文字の判定 |
| **文字コード変換**（`ucnv`） | Shift_JIS、EUC-JP、ISO-2022-JP を含む、数百の文字コード |

導入のコストが大きいので、**必要になったとき**（文字数制限、並べ替え、検索の正規化）だけ入れます。

## ゲームでの使いどころ

| 場面 | 使うもの |
| --- | --- |
| UI の文字列を表示（ImGui） | UTF-8 の `std::string`。日本語フォントを読み込む |
| JSON のセーブ・設定 | nlohmann/json（UTF-8） |
| 名前入力の文字数制限（8 文字まで） | utfcpp でコードポイント数。絵文字まで厳密にするなら ICU |
| 吹き出しに 1 文字ずつ表示 | utfcpp で、コードポイントごとに進む |
| 名前の五十音順ソート | ICU の Collator。または、読み仮名のデータを別に持つ |
| ユーザーが貼った MOD のテキスト | simdutf で検証。不正なら CP932 として変換 |
| 画像・音の読み込み | 自分でファイルを読んで、メモリをライブラリに渡す |
| DirectX のテクスチャ読み込み | UTF-8 → UTF-16 に変換して、`wchar_t*` のパスを渡す |

## よくあるミス

??? failure "ライブラリの仕様を確認せずに、文字列を渡す"
    UTF-8 前提か、UTF-16 前提か、ANSI か、ドキュメントを確認します。確認せず、動いたから大丈夫と思うと、日本語のパスで失敗します。

??? failure "stb_image に、日本語のパスを渡す"
    `fopen`（ANSI）で開くため、失敗します（または、別のファイルを開く）。ファイルを自分で読んで、メモリから読み込みます。

??? failure "ImGui で、フォントを読み込まずに日本語を出す"
    文字コードは正しいのに、フォントにグリフがなく、`?` や四角になります。日本語のフォントと、グリフ範囲（`GetGlyphRangesJapanese()` など）を読み込みます。

??? failure "自分で、UTF-8 の切り取りや、文字数の処理を書く"
    不正な入力、サロゲート、結合文字で、間違いやすいです。utfcpp などを使います。

??? failure "ICU を、小さな用途のために入れて、配布サイズが膨らむ"
    ICU のデータ ファイルは大きいです。必要な機能だけ（正規化なら utf8proc）で足りないか、先に検討します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ほとんどのライブラリは <strong>UTF-8</strong>。<strong>DirectX 関連・Win32 の W 版は UTF-16</strong>
    - [x] <strong>パスで壊れやすい</strong>。内部で <strong>`fopen`（ANSI）</strong>を使うライブラリに注意
    - [x] <strong>ファイルは自分で（W 版で）読んで、メモリをライブラリに渡す</strong>のが確実
    - [x] 文字の処理は<strong>utfcpp（軽い）・simdutf（速い）・ICU（本格的）</strong>に任せる
    - [x] 迷ったら、ドキュメントで<strong>UTF-8 / wide / Unicode</strong> を検索する

## 関連ページ

- [文字コード（目次）](index.md)
- [Windows API と文字コード](windows-api.md)
- [文字コードの変換](conversion.md)
- [Dear ImGui](../libs/imgui/index.md)
- [外部ライブラリ](../libs/index.md)
