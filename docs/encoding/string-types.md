---
title: C++ の文字型と文字列型
tags:
  - 文字コード
---

# C++ の文字型と文字列型

C++ には、文字を表す型が**たくさん**あります（`char`、`wchar_t`、`char8_t`、`char16_t`、`char32_t`）。それぞれに文字列型（`std::string`、`std::wstring`、`std::u8string`…）と、文字列リテラル（`"..."`、`L"..."`、`u8"..."`…）があります。初心者が混乱するのは、<strong>「型の名前」と「文字コード」が、直接は対応していない</strong>ことです。`std::string` は、UTF-8 かもしれないし、Shift_JIS かもしれません。**型は、バイトの入れ物の大きさを決めるだけで、文字コードは、別に決めて管理する**のが、C++ の流儀です。このページでは、各型の意味と、**ゲーム制作ではどれを使うか**を、整理します。

!!! tip "ポイント"
    - <strong>基本は `std::string`（中身は UTF-8）</strong>。ゲーム内の文字列は、全部これ。
    - <strong>`std::wstring` は、Windows API に渡すときだけ</strong>（Windows では UTF-16）。長く持たない。
    - <strong>`char8_t` / `std::u8string` は、あまり使わない</strong>。標準ライブラリの対応が薄く、<strong>`std::string` に UTF-8 を入れる</strong>ほうが扱いやすい。
    - <strong>`wchar_t` の大きさは環境で違う</strong>（Windows は 2 バイト、Linux は 4 バイト）。ゲームのデータに使わない。
    - 文字列リテラルの文字コードは、<strong>コンパイラのオプション</strong>（MSVC の `/utf-8`）で決まる。

## 文字型

| 型 | 大きさ | 意味 | 導入 |
| --- | --- | --- | --- |
| **`char`** | 1 バイト | バイトの単位。文字コードは決まっていない | 昔から |
| **`wchar_t`** | **環境による**（Windows 2 バイト、Linux / Mac 4 バイト） | ワイド文字。Windows では UTF-16 の 1 単位 | 昔から |
| **`char8_t`** | 1 バイト（`unsigned char` 相当） | **UTF-8 の 1 単位** | C++20 |
| **`char16_t`** | 2 バイト | **UTF-16 の 1 単位** | C++11 |
| **`char32_t`** | 4 バイト | **UTF-32 の 1 単位**（コードポイントそのもの） | C++11 |

- `char8_t`、`char16_t`、`char32_t` は、**文字コードが決まっている**型です
- `char` と `wchar_t` は、**文字コードが、環境（コンパイラの設定、ロケール）で決まります**

## 文字列型

| 型 | 中身 | 説明 |
| --- | --- | --- |
| **`std::string`** | `char` の並び | **普通の文字列**。文字コードは、使う人が決める（ゲームでは UTF-8） |
| **`std::wstring`** | `wchar_t` の並び | Windows の API 用。Windows では UTF-16 |
| `std::u8string` | `char8_t` の並び | UTF-8 と、型で明示（C++20） |
| `std::u16string` | `char16_t` の並び | UTF-16 と、型で明示 |
| `std::u32string` | `char32_t` の並び | UTF-32（コードポイントの並び） |
| `std::string_view` | `char` の借り物 | コピーしない、読むだけの文字列（[string_view](../stl/utilities/string_view.md)） |
| `std::wstring_view` など | 同様 | |

<strong>どの型も、文字コードの検査はしません。</strong>`std::string` に、壊れた UTF-8 を入れても、エラーにはなりません。

## 文字列リテラル

ソースコードに書く文字列の、**前に付ける印**で、型が決まります。

| 書き方 | 型 | 例 |
| --- | --- | --- |
| `"..."` | `const char[]` | `"こんにちは"` |
| `L"..."` | `const wchar_t[]` | `L"こんにちは"` |
| `u8"..."` | **`const char8_t[]`**（C++20 以降） | `u8"こんにちは"` |
| `u"..."` | `const char16_t[]` | `u"こんにちは"` |
| `U"..."` | `const char32_t[]` | `U"こんにちは"` |
| `R"(...)"` | 生文字列（エスケープなし） | `R"(C:\game\data)"` |

### 普通の `"..."` の文字コードは、コンパイラ次第

`"こんにちは"` が、どの文字コードのバイトになるかは、**コンパイラの設定**（実行文字集合）で決まります。

| コンパイラ | 既定 | UTF-8 にする方法 |
| --- | --- | --- |
| **MSVC** | **ANSI**（日本語版は CP932） | **`/utf-8`**（または `/execution-charset:utf-8`） |
| GCC / Clang | UTF-8 | 既定のまま（`-fexec-charset=UTF-8`） |

つまり、**MSVC で `/utf-8` を付けないと、`"こんにちは"` は Shift_JIS のバイトになり**、UTF-8 前提のライブラリ（ImGui、JSON）に渡すと、文字化けします。**`/utf-8` は必ず付けます**（[ソースファイルの設定](source-files.md)）。

### `u8"..."` と `char8_t`（C++20 の変更）

C++20 から、`u8"..."` の型が、`const char[]` から **`const char8_t[]`** に変わりました。

```cpp
const char* a = "こんにちは";       // /utf-8 なら、UTF-8 のバイト
const char8_t* b = u8"こんにちは";  // C++20：char8_t の配列
// const char* c = u8"こんにちは";   // C++20 ではエラー（C++17 までは OK だった）
```

`char8_t` は、`char` と**別の型**なので、**`std::string` や `printf`、`std::println` に、そのまま渡せません**。標準ライブラリや、多くの外部ライブラリが、`char` を前提にしているからです。

| 方法 | 説明 |
| --- | --- |
| **普通の `"..."` + `/utf-8`** | <strong>おすすめ。</strong> `char` のまま、UTF-8 の文字列になる |
| `u8"..."` を使うなら | `reinterpret_cast<const char*>(u8"...")` で `char` に変換する |
| `/Zc:char8_t-`（MSVC） | `u8"..."` を、C++17 のとき通り `char` にする。古いコードを、そのまま動かすとき |

```cpp
// u8 リテラルを std::string に変換する（必要なとき）
std::string ToString(std::u8string_view s) {
  return std::string(reinterpret_cast<const char*>(s.data()), s.size());
}
```

結局、**ゲームでは、普通の `"..."` に `/utf-8`** にして、`char8_t` は避けるのが、実用的です。

## 型と文字コードの対応（ゲームでの方針）

| 場面 | 型 | 文字コード |
| --- | --- | --- |
| ゲームの中の文字列、データ、ログ | `std::string` / `std::string_view` | **UTF-8** |
| Windows API への引数 | `std::wstring` / `const wchar_t*` | UTF-16（その場で変換） |
| `std::filesystem::path` | （内部は、Windows ではワイド文字） | [Windows API](windows-api.md) で説明 |
| 外部ライブラリ（ImGui、JSON、SDL…） | `const char*` | UTF-8 |
| ファイル（JSON、セーブ、シナリオ） | バイト列 | UTF-8（BOM なし） |

## wchar_t を、データに使ってはいけない理由

| 理由 | 説明 |
| --- | --- |
| **大きさが違う** | Windows は 2 バイト、Linux は 4 バイト。ファイルに `wchar_t` をそのまま書くと、環境で読めない |
| **Windows の `wchar_t` は、UTF-16** | サロゲート ペアがあるので、1 つの `wchar_t` ＝ 1 文字ではない |
| **標準ライブラリの対応が弱い** | `std::format`、JSON ライブラリ、ImGui など、`char`（UTF-8）が前提 |

`wchar_t` は、**Windows API との境界でだけ**使います。

## std::string の、文字コードに関する性質

| 操作 | 注意 |
| --- | --- |
| `size()` / `length()` | **バイト数**。日本語 3 文字で 9 |
| `s[i]` | i 番目の**バイト**。文字の途中かもしれない |
| `substr(a, n)` | バイト単位で切る。**文字の途中で切ると、壊れる** |
| `find("あ")` | UTF-8 同士なら、バイト列として正しく探せる（先頭バイトで区別できる設計のため） |
| `==`、`<` | バイト単位の比較。**辞書順（五十音順）にはならない** |
| `std::toupper` など | **ASCII だけ**が対象。日本語は何もしない |
| `std::getline` / `cin` | バイトとして読むだけ。文字コードの変換はしない |
| `std::format("{}", s)` | UTF-8 として、そのまま出す（`/utf-8` の環境で） |

### 大文字・小文字、文字の種類の判定

`std::toupper`、`std::isalpha` などは、**ASCII（または現在のロケール）だけ**が対象です。日本語（ひらがな・カタカナ・漢字の判定）や、全角英字の大文字化は、標準では**できません**。必要なら、コードポイントの範囲で判定するか、ICU などを使います。

```cpp
// ひらがな（U+3041〜U+3096）かの判定（コードポイントで）
bool IsHiragana(char32_t cp) { return cp >= 0x3041 && cp <= 0x3096; }
```

## ゲームでの使いどころ

| 場面 | 方針 |
| --- | --- |
| 台詞・UI の文字列 | `std::string`（UTF-8）。リソース ファイルから読む |
| ファイル名・パス | UTF-8 の `std::string` で持ち、API を呼ぶときに `std::filesystem::path` / `wstring` に変換 |
| 文字の切り取り（吹き出しの 1 文字ずつ表示） | コードポイント（または書記素クラスタ）の単位で進める |
| 文字数制限（名前は 8 文字まで） | コードポイント数で数える |
| ソート（五十音順） | バイト比較ではダメ。読み仮名のデータを持つか、ICU の照合順序 |
| 文字列の検索・置換 | UTF-8 同士なら `find` で OK |

## よくあるミス

??? failure "`std::wstring` を、ゲームの標準の文字列にする"
    ライブラリが `char` 前提で、変換だらけになります。Windows でしか動かないコードにもなります。標準は UTF-8 の `std::string` です。

??? failure "`char8_t` に統一しようとして、全部の関数が通らなくなる"
    標準ライブラリや外部ライブラリが、`char8_t` に対応していません。普通の `std::string` + `/utf-8` が、現実的です。

??? failure "`/utf-8` を付けずに、「こんにちは」を ImGui に渡す"
    MSVC では、Shift_JIS のバイトが渡されて、`?` や文字化けになります。`/utf-8` を付けて、UTF-8 にします。

??? failure "`std::toupper` で、日本語の大文字小文字を扱おうとする"
    ASCII 以外は、何も起きません（または、ロケールで壊れます）。

??? failure "`wchar_t` の大きさを、2 バイトと決めつける"
    Linux では 4 バイトです。ファイル形式にするなら、`char16_t` か UTF-8 の `char` を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列は<strong>`std::string`（UTF-8）</strong>で統一。<strong>`/utf-8` を付ける</strong>
    - [x] <strong>`std::wstring` は、Windows API との境界だけ</strong>（UTF-16）
    - [x] <strong>`char8_t` は避ける</strong>。外部ライブラリが対応していない
    - [x] <strong>`size()` はバイト数</strong>。切る・数える・大文字化は、文字の単位で考える
    - [x] 型は文字コードを保証しない。<strong>ルールで決めて、強制する</strong>

## 関連ページ

- [文字コード（目次）](index.md)
- [文字コードの基礎](unicode-basics.md)
- [文字コードの変換](conversion.md)
- [Windows API と文字コード](windows-api.md)
- [std::string](../stl/containers/string.md)
- [std::string_view](../stl/utilities/string_view.md)
