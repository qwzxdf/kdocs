---
title: 外部ライブラリと文字コード
tags:
  - 文字コード
---

# 外部ライブラリと文字コード

ゲームではウィンドウ、描画、音、GUI、JSON、画像など**たくさんの外部ライブラリ**を使います。ライブラリごとに文字列を受け取るときの文字コード（UTF-8 か、UTF-16 か ANSI か）が決まっています。それを知らずに文字列を渡すと文字化けやファイルが開けない原因になります。このページはよく使うライブラリが、何を要求するかを一覧にし、あわせて文字コードを本格的に扱うライブラリ（utfcpp、simdutf、ICU）を紹介します。

!!! tip "ポイント"
    - <strong>ほとんどのライブラリは UTF-8（`char*`）</strong>。ゲームの文字列（UTF-8）をそのまま渡せる。
    - <strong>Windows のネイティブ系（DirectX 関連、Win32）は UTF-16（`wchar_t*`）</strong>。境界で変換する。
    - パス（ファイル名）で、日本語が壊れやすい。内部で `fopen`（ANSI）を使うライブラリに注意。
    - 迷ったら ライブラリのドキュメントで「UTF-8」「wide」「Unicode」を検索。
    - 文字の切り取り・数え方・並べ替えが必要なら utfcpp / ICU。検証だけなら simdutf。

## ライブラリごとの要求

ライブラリが受け取る文字列は大きく 3 つの流派に分かれます。**UTF-8 の `char*`**（ほとんどのクロスプラットフォームなライブラリ）、**UTF-16 の `wchar_t*`（Windows 由来の API）、そしてANSI（実行環境のコード ページ）**（古い C の関数）です。自分のゲームの文字列を UTF-8 に統一していれば、1 つ目はそのまま渡せ 2 つ目は境界で変換し、3 つ目は使わないように避けます。

次の表はよく使うライブラリがどの流派かをまとめたものです。表のあとに特に事故が多い「パス」の扱いを説明します。

### UTF-8（char*）を要求するもの

| ライブラリ | 文字列の扱い | 注意 |
| --- | --- | --- |
| [Dear ImGui](../libs/imgui/index.md) | UTF-8 | 日本語フォント（グリフ範囲）を読み込まないと、`?` や四角になる（[ImGui のフォント](../libs/imgui/fonts.md)） |
| [nlohmann/json](../libs/serialization/nlohmann-json.md) | UTF-8 | 不正な UTF-8 を `dump()` すると例外（`error_handler_t::replace` で、置き換えにできる）。BOM は読む前に取り除く |
| [simdjson](../libs/serialization/simdjson.md) | UTF-8 | 不正な UTF-8 は、エラー |
| [rapidyaml](../libs/serialization/rapidyaml.md) | UTF-8 | |
| SDL2 / SDL3 | UTF-8（ウィンドウ タイトル、パス） | Windows でも UTF-8 でよい。内部で変換する |
| GLFW | UTF-8（ウィンドウ タイトル、クリップボード） | 文字入力のコールバックは、コードポイント（`unsigned int`） で来る |
| FMOD | UTF-8（ファイル名） | Windows でも UTF-8 でよい |
| Jolt Physics | 文字列をほとんど扱わない | デバッグ名くらい |
| spdlog / {fmt} | UTF-8 | Windows のコンソールに出すとき、`/utf-8` が必要（{fmt} は `/utf-8` を要求する） |
| sqlite3 | UTF-8（`sqlite3_open`）、UTF-16 用の関数（`_16`）もある | |
| OpenGL / Vulkan | シェーダーは ASCII。ウィンドウ名はウィンドウ ライブラリ次第 | |

### UTF-16（wchar_t*）を要求するもの

| ライブラリ | 文字列の扱い | 注意 |
| --- | --- | --- |
| Win32 API の `W` 版（`CreateFileW`、`MessageBoxW`） | UTF-16 | [Windows API](windows-api.md) |
| Direct3D の `D3DCompileFromFile` | `LPCWSTR`（UTF-16）のパス | |
| DirectXTex / DirectXTK（`LoadFromDDSFile`、`CreateDDSTextureFromFile`） | **`wchar_t*`（UTF-16）のパス** | UTF-8 のパスを変換して渡す |
| XAudio2 / Media Foundation | UTF-16 のパス | |
| `std::filesystem::path`（Windows） | 内部は UTF-16 | `u8string()` / `wstring()` で取り出す |
| Qt | `QString`（UTF-16）。`QString::fromUtf8(...)` で変換 | |

### 注意が必要なもの（ANSI や内部の `fopen`）

| ライブラリ | 問題 | 対策 |
| --- | --- | --- |
| stb_image / stb_vorbis など | `stbi_load(filename)` が、内部で `fopen` を使う。Windows では日本語パスが、ANSI として解釈されて失敗する | ファイルを自分で読んで `stbi_load_from_memory`。または、ワイド文字版の `fopen` に差し替える（`STBI_WINDOWS_UTF8` を定義して、`stbi_convert_wchar_to_utf8` を使う） |
| **`fopen` / `std::ifstream(const char*)`** | ANSI のパス | `std::filesystem::path`、`_wfopen` |
| 古い C ライブラリ（zlib の `gzopen` など） | ANSI のパス | メモリに読んでから渡す。または、`gzopen_w` などの W 版 |
| `main` の `argv` | ANSI | `GetCommandLineW`、マニフェストの UTF-8 |
| libpng / libjpeg | ファイル ハンドル（`FILE*`）を受け取る | `_wfopen` で開いて渡す |
| FreeType（フォントの読み込み） | ファイル名は ANSI（`FT_New_Face`） | メモリに読んで `FT_New_Memory_Face` |

パスで困ったら「ファイルを自分で（W 版で）読んで、メモリのデータをライブラリに渡す」のが、一番確実です。

## パスの方針

文字コードの事故で最も多いのは、文字列の表示ではなく**ファイルパス**です。表示なら化けるだけですがパスが壊れると「ファイルが開けない」という動作そのものの失敗になります。しかも開発者の PC（英数字のユーザー名）では動き日本語のユーザー名の PC でだけ失敗する、という再現しにくい形で出ます。

対策は単純でライブラリにパスを渡さないことです。ファイルは自分で（`std::filesystem::path` か W 版 API で）読み込み中身のバイト列だけをライブラリに渡します。下の表に方針とその理由をまとめます。

<svg class="fig flow" viewBox="0 0 578 280" role="img" aria-label="ライブラリには、メモリ上のデータを渡す"><defs><marker id="fl90924" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ライブラリには、メモリ上のデータを渡す</text><line x1="218.7" y1="125.0" x2="351.3" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl90924)"/><text x="285.0" y="100.0" text-anchor="middle" style="font-size:12px">自分で読む</text><line x1="218.7" y1="171.0" x2="351.3" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl90924)"/><text x="285.0" y="184.0" text-anchor="middle" style="font-size:12px">ファイル名は渡さない</text><rect x="28.0" y="128.0" width="221" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="138.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">パス （UTF-8 std::string）</text><rect x="313.0" y="44.0" width="237" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="431.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">std::filesystem::path で開く</text><rect x="316.5" y="212.0" width="230" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="431.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ライブラリへ メモリ上のデータ</text></svg>

| 方針 | 理由 |
| --- | --- |
| ファイルは自分で読む | パスの文字コードの問題が、ライブラリに入らない |
| **ライブラリにはメモリ（`const void*` + サイズ）を渡す** | `stbi_load_from_memory`、`FT_New_Memory_Face`、`FMOD_CREATESOUNDEXINFO` など |
| アセットのパスは ASCII にする | `data/textures/hero.png`。日本語のファイル名は避ける |
| ユーザーが選ぶパス（セーブ、スクリーンショット）だけ日本語を考慮する | `std::filesystem::path` と W 版 |

## 文字コードを扱うライブラリ

自分で文字コードの処理（変換、検証、切り取り正規化）を書くのは大変で、間違いやすいので**ライブラリに任せる**のが安全です。

### 比較

| ライブラリ | 向いていること | 大きさ | 導入 |
| --- | --- | --- | --- |
| utfcpp（`utf8cpp`） | UTF-8 の検証・変換・文字の走査。軽くて簡単 | ヘッダだけ | `vcpkg install utfcpp` |
| simdutf | 非常に速い検証・変換（SIMD）。大量のデータ | ライブラリ | `vcpkg install simdutf` |
| ICU | 何でもできる。正規化、照合（五十音順）、書記素の分割、大文字小文字（日本語対応）、変換、日付・数値の書式 | 大きい（数十 MB） | `vcpkg install icu` |
| Boost.Locale | ICU を使った、C++ らしい API | 大きい | `vcpkg install boost-locale` |
| utf8proc | 正規化（NFC / NFD）、文字の分類。小さい | 小さい | `vcpkg install utf8proc` |
| ztd.text（将来の標準を見据えた） | 文字コードの変換の、標準提案の実装 | | |

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

巨大なファイル（セーブ・シナリオ・ログ）の検証・変換に威力を発揮します。

### ICU でできること

| 機能 | 使いどころ |
| --- | --- |
| 書記素クラスタの分割（`BreakIterator`） | 「ユーザーが見る 1 文字」で、切り取る・数える（絵文字、結合文字） |
| 正規化（`Normalizer2`） | NFC にそろえて、比較する |
| 照合（`Collator`） | 五十音順などの言語に合った並べ替え |
| 大文字・小文字変換（`toUpper`、`toLower`） | 全角英字やギリシャ文字を含む |
| 文字の性質（`u_charType`、`u_isalpha`） | ひらがな・カタカナ・漢字・絵文字の判定 |
| 文字コード変換（`ucnv`） | Shift_JIS、EUC-JP、ISO-2022-JP を含む数百の文字コード |

導入のコストが大きいので必要になったとき（文字数制限、並べ替え検索の正規化）だけ入れます。

## ゲームでの使いどころ

ここまでの内容をゲームを作る場面に当てはめると次のようになります。基本は「内部は UTF-8」「境界で変換」「パスはアセットなら ASCII」の 3 つで、場面ごとにどれが効くかを表にしました。

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

??? failure "ライブラリの仕様を確認せずに文字列を渡す"
    UTF-8 前提か UTF-16 前提か ANSI かドキュメントを確認します。確認せず動いたから大丈夫と思うと日本語のパスで失敗します。

??? failure "stb_image に日本語のパスを渡す"
    `fopen`（ANSI）で開くため、失敗します（または別のファイルを開く）。ファイルを自分で読んでメモリから読み込みます。

??? failure "ImGui で、フォントを読み込まずに日本語を出す"
    文字コードは正しいのに、フォントにグリフがなく `?` や四角になります。日本語のフォントとグリフ範囲（`GetGlyphRangesJapanese()` など）を読み込みます。

??? failure "自分で、UTF-8 の切り取りや文字数の処理を書く"
    不正な入力、サロゲート、結合文字で間違いやすいです。utfcpp などを使います。

??? failure "ICU を小さな用途のために入れて、配布サイズが膨らむ"
    ICU のデータ ファイルは大きいです。必要な機能だけ（正規化なら utf8proc）で足りないか先に検討します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ほとんどのライブラリは <strong>UTF-8</strong>。DirectX 関連・Win32 の W 版は UTF-16
    - [x] パスで壊れやすい。内部で `fopen`（ANSI）を使うライブラリに注意
    - [x] ファイルは自分で（W 版で）読んで、メモリをライブラリに渡すのが確実
    - [x] 文字の処理はutfcpp（軽い）・simdutf（速い）・ICU（本格的）に任せる
    - [x] 迷ったら、ドキュメントでUTF-8 / wide / Unicode を検索する

## 関連ページ

- [文字コード（目次）](index.md)
- [Windows API と文字コード](windows-api.md)
- [文字コードの変換](conversion.md)
- [Dear ImGui](../libs/imgui/index.md)
- [外部ライブラリ](../libs/index.md)
