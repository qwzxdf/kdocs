---
title: C++ の文字型と文字列型
tags:
  - 文字コード
---

# C++ の文字型と文字列型

C++ には文字を表す型が**たくさん**あります（`char`、`wchar_t`、`char8_t`、`char16_t`、`char32_t`）。それぞれに文字列型（`std::string`、`std::wstring`、`std::u8string`…）と文字列リテラル（`"..."`、`L"..."`、`u8"..."`…）があります。初心者が混乱するのは 「型の名前」と「文字コード」が直接は対応していないことです。`std::string` は UTF-8 かもしれないし、Shift_JIS かもしれません。型はバイトの入れ物の大きさを決めるだけで、文字コードは別に決めて管理するのが、C++ の流儀です。このページでは各型の意味とゲーム制作ではどれを使うかを整理します。

!!! tip "ポイント"
    - <strong>基本は `std::string`（中身は UTF-8）</strong>。ゲーム内の文字列は全部これ。
    - <strong>`std::wstring` は Windows API に渡すときだけ</strong>（Windows では UTF-16）。長く持たない。
    - `char8_t` / `std::u8string` はあまり使わない。標準ライブラリの対応が薄く `std::string` に UTF-8 を入れるほうが扱いやすい。
    - `wchar_t` の大きさは環境で違う（Windows は 2 バイト、Linux は 4 バイト）。ゲームのデータに使わない。
    - 文字列リテラルの文字コードは、コンパイラのオプション（MSVC の `/utf-8`）で決まる。

!!! info "このページを読む前に"
    - [encoding/index.md](index.md)（このセクション全体の地図と、読む順番）
    - [文字コードの基礎](unicode-basics.md)（文字コードの基礎）

## 文字型

| 型 | 大きさ | 意味 | 導入 |
| --- | --- | --- | --- |
| **`char`** | 1 バイト | バイトの単位。文字コードは決まっていない | 昔から |
| `wchar_t` | 環境による（Windows 2 バイト、Linux / Mac 4 バイト） | ワイド文字。Windows では UTF-16 の 1 単位 | 昔から |
| `char8_t` | 1 バイト（`unsigned char` 相当） | UTF-8 の 1 単位 | C++20 |
| `char16_t` | 2 バイト | UTF-16 の 1 単位 | C++11 |
| `char32_t` | 4 バイト | UTF-32 の 1 単位（コードポイントそのもの） | C++11 |

- `char8_t`、`char16_t`、`char32_t` は文字コードが決まっている型です
- `char` と `wchar_t` は文字コードが環境（コンパイラの設定、ロケール）で決まります

## 文字列型

| 型 | 中身 | 説明 |
| --- | --- | --- |
| **`std::string`** | `char` の並び | 普通の文字列。文字コードは使う人が決める（ゲームでは UTF-8） |
| `std::wstring` | `wchar_t` の並び | Windows の API 用。Windows では UTF-16 |
| `std::u8string` | `char8_t` の並び | UTF-8 と型で明示（C++20） |
| `std::u16string` | `char16_t` の並び | UTF-16 と型で明示 |
| `std::u32string` | `char32_t` の並び | UTF-32（コードポイントの並び） |
| `std::string_view` | `char` の借り物 | コピーしない、読むだけの文字列（[string_view](../stl/utilities/string_view.md)） |
| `std::wstring_view` など | 同様 | |

どの型も文字コードの検査はしません。`std::string` に壊れた UTF-8 を入れても、エラーにはなりません。

## 文字列リテラル

ソースコードに書く文字列の**前に付ける印**で、型が決まります。

| 書き方 | 型 | 例 |
| --- | --- | --- |
| `"..."` | `const char[]` | `"こんにちは"` |
| `L"..."` | `const wchar_t[]` | `L"こんにちは"` |
| `u8"..."` | `const char8_t[]`（C++20 以降） | `u8"こんにちは"` |
| `u"..."` | `const char16_t[]` | `u"こんにちは"` |
| `U"..."` | `const char32_t[]` | `U"こんにちは"` |
| `R"(...)"` | 生文字列（エスケープなし） | `R"(C:\game\data)"` |

### 普通の `"..."` の文字コードはコンパイラ次第

`"こんにちは"` がどの文字コードのバイトになるかは、コンパイラの設定（実行文字集合）で決まります。

| コンパイラ | 既定 | UTF-8 にする方法 |
| --- | --- | --- |
| MSVC | ANSI（日本語版は CP932） | `/utf-8`（または `/execution-charset:utf-8`） |
| GCC / Clang | UTF-8 | 既定のまま（`-fexec-charset=UTF-8`） |

つまり、MSVC で `/utf-8` を付けないと `"こんにちは"` は Shift_JIS のバイトになり、UTF-8 前提のライブラリ（ImGui、JSON）に渡すと文字化けします。`/utf-8` は必ず付けます（[ソースファイルの設定](source-files.md)）。

### `u8"..."` と `char8_t`（C++20 の変更）

C++20 から `u8"..."` の型が `const char[]` から `const char8_t[]` に変わりました。

```cpp
const char* a = "こんにちは";       // /utf-8 なら、UTF-8 のバイト
const char8_t* b = u8"こんにちは";  // C++20：char8_t の配列
// const char* c = u8"こんにちは";   // C++20 ではエラー（C++17 までは OK だった）
```

`char8_t` は `char` と別の型なので、`std::string` や `printf`、`std::println` にそのまま渡せません。標準ライブラリや多くの外部ライブラリが `char` を前提にしているからです。

| 方法 | 説明 |
| --- | --- |
| 普通の `"..."` + `/utf-8` | おすすめ。 `char` のまま UTF-8 の文字列になる |
| `u8"..."` を使うなら | `reinterpret_cast<const char*>(u8"...")` で `char` に変換する |
| `/Zc:char8_t-`（MSVC） | `u8"..."` を C++17 のとき通り `char` にする。古いコードをそのまま動かすとき |

```cpp
// u8 リテラルを std::string に変換する（必要なとき）
std::string ToString(std::u8string_view s) {
  return std::string(reinterpret_cast<const char*>(s.data()), s.size());
}
```

結局、ゲームでは普通の `"..."` に `/utf-8` にして、`char8_t` は避けるのが実用的です。

## 型と文字コードの対応（ゲームでの方針）

| 場面 | 型 | 文字コード |
| --- | --- | --- |
| ゲームの中の文字列、データ、ログ | `std::string` / `std::string_view` | **UTF-8** |
| Windows API への引数 | `std::wstring` / `const wchar_t*` | UTF-16（その場で変換） |
| `std::filesystem::path` | （内部は Windows ではワイド文字） | [Windows API](windows-api.md) で説明 |
| 外部ライブラリ（ImGui、JSON、SDL…） | `const char*` | UTF-8 |
| ファイル（JSON、セーブ、シナリオ） | バイト列 | UTF-8（BOM なし） |

## wchar_t をデータに使ってはいけない理由

| 理由 | 説明 |
| --- | --- |
| **大きさが違う** | Windows は 2 バイト、Linux は 4 バイト。ファイルに `wchar_t` をそのまま書くと環境で読めない |
| Windows の `wchar_t` は UTF-16 | サロゲート ペアがあるので、1 つの `wchar_t` ＝ 1 文字ではない |
| 標準ライブラリの対応が弱い | `std::format`、JSON ライブラリ、ImGui など `char`（UTF-8）が前提 |

`wchar_t` はWindows API との境界でだけ使います。

## std::string の文字コードに関する性質

| 操作 | 注意 |
| --- | --- |
| `size()` / `length()` | **バイト数**。日本語 3 文字で 9 |
| `s[i]` | i 番目のバイト。文字の途中かもしれない |
| `substr(a, n)` | バイト単位で切る。文字の途中で切ると壊れる |
| `find("あ")` | UTF-8 同士ならバイト列として正しく探せる（先頭バイトで区別できる設計のため） |
| `==`、`<` | バイト単位の比較。辞書順（五十音順）にはならない |
| `std::toupper` など | ASCII だけが対象。日本語は何もしない |
| `std::getline` / `cin` | バイトとして読むだけ。文字コードの変換はしない |
| `std::format("{}", s)` | UTF-8 として、そのまま出す（`/utf-8` の環境で） |

### 大文字・小文字、文字の種類の判定

`std::toupper`、`std::isalpha` などはASCII（または現在のロケール）だけが対象です。日本語（ひらがな・カタカナ・漢字の判定）や全角英字の大文字化は、標準ではできません。必要ならコードポイントの範囲で判定するか ICU などを使います。

```cpp
// ひらがな（U+3041〜U+3096）かの判定（コードポイントで）
bool IsHiragana(char32_t cp) { return cp >= 0x3041 && cp <= 0x3096; }
```

## ゲームでの使いどころ

| 場面 | 方針 |
| --- | --- |
| 台詞・UI の文字列 | `std::string`（UTF-8）。リソース ファイルから読む |
| ファイル名・パス | UTF-8 の `std::string` で持ち API を呼ぶときに `std::filesystem::path` / `wstring` に変換 |
| 文字の切り取り（吹き出しの 1 文字ずつ表示） | コードポイント（または書記素クラスタ）の単位で進める |
| 文字数制限（名前は 8 文字まで） | コードポイント数で数える |
| ソート（五十音順） | バイト比較ではダメ。読み仮名のデータを持つか ICU の照合順序 |
| 文字列の検索・置換 | UTF-8 同士なら `find` で OK |

<!-- fig:encoding-sizes:begin -->

<svg class="fig illust motion" data-fig="encoding-sizes" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-encoding-sizes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">同じ 1 文字でも、文字コードで必要なバイト数が違う</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><text x="70" y="130" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">A  半角英字</text>
<rect x="250" y="90" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<text x="310" y="107" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">UTF-8: 1 バイト</text>
<rect x="250" y="118" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<rect x="302" y="118" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<text x="362" y="135" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">UTF-16: 2 バイト</text>
<rect x="250" y="146" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="302" y="146" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="354" y="146" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="406" y="146" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<text x="466" y="163" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">UTF-32: 4 バイト</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3108;0.3111;1.0000" values="0;0;1;1"/><text x="70" y="225" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">あ  ひらがな</text>
<rect x="250" y="185" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<rect x="302" y="185" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<rect x="354" y="185" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<text x="414" y="202" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">UTF-8: 3 バイト</text>
<rect x="250" y="213" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<rect x="302" y="213" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<text x="362" y="230" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">UTF-16: 2 バイト</text>
<rect x="250" y="241" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="302" y="241" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="354" y="241" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="406" y="241" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<text x="466" y="258" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">UTF-32: 4 バイト</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;1.0000" values="0;0;1;1"/><text x="70" y="320" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">😀  絵文字</text>
<rect x="250" y="280" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<rect x="302" y="280" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<rect x="354" y="280" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<rect x="406" y="280" width="48" height="22" fill="#2563eb" opacity="0.9"/>
<text x="466" y="297" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">UTF-8: 4 バイト</text>
<rect x="250" y="308" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<rect x="302" y="308" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<rect x="354" y="308" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<rect x="406" y="308" width="48" height="22" fill="#2ea043" opacity="0.9"/>
<text x="466" y="325" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">UTF-16: 4 バイト</text>
<rect x="250" y="336" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="302" y="336" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="354" y="336" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<rect x="406" y="336" width="48" height="22" fill="#e5aa28" opacity="0.9"/>
<text x="466" y="353" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">UTF-32: 4 バイト</text>
</g>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 バイト = 1 つの四角<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">英字: UTF-8 が最小(1 バイト)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3108;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">日本語: UTF-8 は 3 バイト、UTF-16 は 2 バイト<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3108;0.3111;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">絵文字: どれも 4 バイト(UTF-16 では 2 つで 1 文字)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:encoding-sizes:end -->

## よくあるミス

??? failure "`std::wstring` をゲームの標準の文字列にする"
    ライブラリが `char` 前提で、変換だらけになります。Windows でしか動かないコードにもなります。標準は UTF-8 の `std::string` です。

??? failure "`char8_t` に統一しようとして、全部の関数が通らなくなる"
    標準ライブラリや外部ライブラリが `char8_t` に対応していません。普通の `std::string` + `/utf-8` が現実的です。

??? failure "`/utf-8` を付けずに「こんにちは」を ImGui に渡す"
    MSVC では Shift_JIS のバイトが渡されて、`?` や文字化けになります。`/utf-8` を付けて UTF-8 にします。

??? failure "`std::toupper` で、日本語の大文字小文字を扱おうとする"
    ASCII 以外は何も起きません（または、ロケールで壊れます）。

??? failure "`wchar_t` の大きさを 2 バイトと決めつける"
    Linux では 4 バイトです。ファイル形式にするなら `char16_t` か UTF-8 の `char` を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列は<strong>`std::string`（UTF-8）</strong>で統一。`/utf-8` を付ける
    - [x] `std::wstring` は Windows API との境界だけ（UTF-16）
    - [x] `char8_t` は避ける。外部ライブラリが対応していない
    - [x] `size()` はバイト数。切る・数える・大文字化は文字の単位で考える
    - [x] 型は文字コードを保証しない。ルールで決めて強制する

## 関連ページ

- [文字コード（目次）](index.md)
- [文字コードの基礎](unicode-basics.md)
- [文字コードの変換](conversion.md)
- [Windows API と文字コード](windows-api.md)
- [std::string](../stl/containers/string.md)
- [std::string_view](../stl/utilities/string_view.md)
