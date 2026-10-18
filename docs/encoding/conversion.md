---
title: 文字コードの変換
tags:
  - 文字コード
---

# 文字コードの変換

内部では UTF-8 を使うと決めても、**境界では変換が必要**です。Windows API には UTF-16（`wchar_t`）を渡し、古いファイルは Shift_JIS（CP932）で書かれていて、外部のツールの出力は別の文字コードかもしれません。このページは**UTF-8、UTF-16、Shift_JIS の間を変換する方法**と**変換で失敗したとき（不正なバイト、表せない文字）の扱い**をまとめます。Windows では**Win32 API の `MultiByteToWideChar` / `WideCharToMultiByte`** が、一番手軽で確実です。

!!! tip "ポイント"
    - <strong>変換は境界でだけ</strong>。Windows API を呼ぶ直前に UTF-8 → UTF-16、返ってきたら UTF-16 → UTF-8。
    - Windows では<strong>`MultiByteToWideChar` / `WideCharToMultiByte`</strong>（コード ページを指定）。<strong>2 回呼ぶ</strong>（まず大きさを聞く → 変換）。
    - <strong>標準の `std::codecvt` / `std::wstring_convert` は、非推奨</strong>。使わない。
    - 移植性が必要なら<strong>ライブラリ</strong>（utfcpp、simdutf、ICU）。
    - <strong>失敗を検出する</strong>。不正な入力は <strong>エラーにするか `U+FFFD`（�）に置き換える</strong>かを決める。
    - Shift_JIS などの<strong>古いファイルを読むときだけ</strong>、CP932 から UTF-8 に変換して、以降は UTF-8 で扱う。

## 変換の全体像

<svg class="fig flow" viewBox="0 0 560 280" role="img" aria-label="変換が必要なのは、境界だけ"><defs><marker id="fl23855" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">変換が必要なのは、境界だけ</text><line x1="243.5" y1="56.0" x2="329.0" y2="56.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl23855)"/><text x="286.2" y="76.0" text-anchor="middle" style="font-size:12px">Windows API との境界</text><line x1="329.0" y1="56.0" x2="243.5" y2="56.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl23855)"/><text x="286.2" y="42.0" text-anchor="middle" style="font-size:12px">戻す</text><line x1="148.0" y1="209.0" x2="148.0" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl23855)"/><text x="148.0" y="142.0" text-anchor="middle" style="font-size:12px">古いファイルを読むときだけ</text><rect x="55.5" y="44.0" width="185" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="148.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">std::string （UTF-8）</text><rect x="332.0" y="44.0" width="200" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="432.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">std::wstring （UTF-16）</text><rect x="28.0" y="212.0" width="240" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="148.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Shift JIS （CP932）のバイト列</text></svg>

| 変換 | 場面 |
| --- | --- |
| **UTF-8 → UTF-16** | Windows API（`CreateFileW`、`MessageBoxW`）、DirectX のファイル名に渡す |
| **UTF-16 → UTF-8** | Windows API から受け取った文字列（ファイル ダイアログ、コマンド ライン）をゲームの文字列に |
| **Shift_JIS（CP932）→ UTF-8** | 古いテキスト ファイル、昔のツールの出力、別の PC のファイル名 |
| **UTF-8 → Shift_JIS** | 古いツールに渡す（できるだけ避ける。**表せない文字がある**） |

## Windows API で変換する（おすすめ）

### UTF-8 ⇔ UTF-16

```cpp
#include <windows.h>

#include <stdexcept>
#include <string>
#include <string_view>

// UTF-8 → UTF-16
std::wstring Utf8ToWide(std::string_view utf8) {
  if (utf8.empty()) {
    return {};
  }
  // ① 必要な大きさ（wchar_t の数）を聞く
  int size = ::MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, utf8.data(),
                                   static_cast<int>(utf8.size()), nullptr, 0);
  if (size <= 0) {
    throw std::runtime_error("UTF-8 として不正な文字列です");
  }
  // ② 実際に変換する
  std::wstring wide(static_cast<std::size_t>(size), L'\0');
  ::MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, utf8.data(),
                        static_cast<int>(utf8.size()), wide.data(), size);
  return wide;
}

// UTF-16 → UTF-8
std::string WideToUtf8(std::wstring_view wide) {
  if (wide.empty()) {
    return {};
  }
  int size = ::WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, wide.data(),
                                   static_cast<int>(wide.size()), nullptr, 0, nullptr, nullptr);
  if (size <= 0) {
    throw std::runtime_error("UTF-16 として不正な文字列です");
  }
  std::string utf8(static_cast<std::size_t>(size), '\0');
  ::WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, wide.data(),
                        static_cast<int>(wide.size()), utf8.data(), size, nullptr, nullptr);
  return utf8;
}
```

| 部分 | 意味 |
| --- | --- |
| `CP_UTF8` | 変換元（または先）のコード ページを UTF-8 に |
| `MB_ERR_INVALID_CHARS` / `WC_ERR_INVALID_CHARS` | <strong>不正な入力があれば、失敗（0 を返す）</strong>。付けないと黙って `U+FFFD`（�）に置き換える |
| 第 3、4 引数 | 変換元の文字列と長さ（**`-1` にすると、終端の `\0` まで**。`std::string` の `size()` を渡すほうが安全） |
| 第 5、6 引数 | 出力先とその大きさ。**`nullptr`, 0 を渡すと必要な大きさだけを返す** |
| 戻り値 | 書いた（または必要な）文字数。**0 は失敗**（`GetLastError()` で原因） |

**2 回呼ぶ**（まず大きさを聞き確保してから変換）のが、Windows の変換 API の定番の使い方です。

### Shift_JIS（CP932）→ UTF-8

古いファイルを読んだときの変換は**一度 UTF-16 を経由**します。

```cpp
// CP932（日本語 Windows の ANSI）→ UTF-8
std::string Cp932ToUtf8(std::string_view cp932) {
  if (cp932.empty()) {
    return {};
  }
  int size = ::MultiByteToWideChar(932, 0, cp932.data(),
                                   static_cast<int>(cp932.size()), nullptr, 0);   // 932 = CP932
  std::wstring wide(static_cast<std::size_t>(size), L'\0');
  ::MultiByteToWideChar(932, 0, cp932.data(), static_cast<int>(cp932.size()),
                        wide.data(), size);
  return WideToUtf8(wide);
}
```

| コード ページ | 値 |
| --- | --- |
| **UTF-8** | `CP_UTF8`（65001） |
| <strong>Shift_JIS（CP932）</strong> | `932` |
| <strong>ANSI（今の PC の既定）</strong> | `CP_ACP`（0）。日本語版は 932。**PC ごとに変わるのでデータには使わない** |
| **EUC-JP** | `51932` |
| **ISO-2022-JP** | `50220` |
| **UTF-16** | `wchar_t` の並びそのもの（変換不要） |

!!! warning "CP_ACP は、データに使わない"
    `CP_ACP` は**実行する PC の設定**に依存します。同じプログラムでも日本の PC と韓国の PC で、結果が変わります。データの変換には明示的なコード ページ（932、`CP_UTF8`）を使います。

### 表せない文字（UTF-8 → Shift_JIS）

UTF-8 から Shift_JIS に変換すると、**Shift_JIS にない文字**（絵文字、一部の漢字、外国語）は変換できません。

```cpp
BOOL used_default = FALSE;
int size = ::WideCharToMultiByte(932, 0, wide.data(), static_cast<int>(wide.size()),
                                 out.data(), out_size, "?", &used_default);
// used_default が TRUE なら、表せない文字が '?' に置き換わっている
```

古いツールに渡すために Shift_JIS にする必要がなければ、**変換しません**。

## 標準 C++ での変換（使えるもの・使えないもの）

| 方法 | 状態 | 説明 |
| --- | --- | --- |
| `std::wstring_convert` / `std::codecvt_utf8_utf16` | **C++17 で非推奨**（C++26 で削除予定）。MSVC は警告を出す | 使わない。既存コードで警告を消すには `_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING` |
| `std::mbrtoc8` / `std::c8rtomb`（C++23、`<cuchar>`） | 新しい。**ロケール依存**で対応も途中 | 実用には、まだ早い |
| `std::filesystem::path` | UTF-8 ↔ UTF-16 の変換を**内部で行う**（Windows） | パスだけなら便利（[Windows API](windows-api.md)） |
| `std::format` / `std::print` | UTF-8 をそのまま扱う（`/utf-8` の環境） | 変換機能は、持たない |

**標準の変換機能は現在も弱い**ので、Windows では Win32 API、移植性が必要ならライブラリを使います。

## ライブラリで変換する

| ライブラリ | 特徴 | 例 |
| --- | --- | --- |
| **utfcpp**（`utf8cpp`） | ヘッダだけ。軽い。UTF-8 / 16 / 32 の変換と文字の走査 | `utf8::utf8to16(s)`、`utf8::utf16to8(w)`、`utf8::is_valid(s)` |
| **simdutf** | **非常に速い**（SIMD）。変換と**検証** | `simdutf::validate_utf8(p, n)`、`convert_utf8_to_utf16le(...)` |
| **ICU** | 本格的。変換、正規化、照合、書記素の分割、全部できる。大きい | `icu::UnicodeString::fromUTF8(s)` |
| **Boost.Locale** | ICU や OS の機能を使った、変換とロケール | `boost::locale::conv::utf_to_utf<wchar_t>(s)` |
| <strong>{fmt}</strong>（`std::format` の元） | UTF-8 の書式化。`fmt::to_string` | 変換は持たない |

```cpp
// utfcpp：Windows でなくても使える変換（例外で失敗を知らせる）
#include <utf8.h>

std::u16string wide = utf8::utf8to16(utf8_string);     // UTF-8 → UTF-16
std::string back = utf8::utf16to8(wide);                // UTF-16 → UTF-8
bool ok = utf8::is_valid(utf8_string);                   // UTF-8 として正しいか
```

[外部ライブラリと文字コード](libraries.md) も見てください。

## 失敗の扱い：不正な入力

変換元が**その文字コードとして不正**なバイトを含むことがあります（壊れたファイル、違う文字コードのファイル）。

| 方針 | 説明 | 向いている場面 |
| --- | --- | --- |
| **エラーにする** | 変換に失敗して、呼び出し元に伝える | ゲームのデータ（壊れているのは、バグ） |
| **`U+FFFD`（�）に置き換える** | 不正な部分を「置換文字」にして、続行する | ユーザーの入力・ログの表示（壊れていても、動かしたい） |
| **無視して捨てる** | 不正なバイトを消す | 基本使わない（問題を隠す） |

Win32 では `MB_ERR_INVALID_CHARS` を付けると失敗、付けないと置換です。

## 変換の注意点

| 注意 | 説明 |
| --- | --- |
| **長さ（`-1`）に注意** | `-1` は、終端（`\0`）までを意味し**戻り値に終端ぶんが含まれる**。`size()` を渡すと含まれない |
| **変換後の大きさは元と違う** | UTF-8 の日本語は 3 バイト、UTF-16 は 2 バイト、Shift_JIS は 2 バイト。余裕を持って確保する（2 回呼ぶなら不要） |
| **サロゲート ペアの途中で、切らない** | UTF-16 の絵文字（2 単位）を途中で切ると壊れる |
| **変換の回数を減らす** | 毎フレーム変換すると遅い。境界で 1 回だけ。結果をキャッシュ |
| **`wchar_t` の大きさ** | Windows 専用のコードなら UTF-16 と決めてよい。移植するなら `char16_t` やライブラリ |
| **終端の `\0` を含めない** | `std::string` の `size()` に `\0` は含まれない |
| **往復変換で元に戻るか** | UTF-8 ⇔ UTF-16 は、正しい入力なら完全に戻る。Shift_JIS は表せない文字で戻らない |

## ゲームでの使いどころ

| 場面 | 変換 |
| --- | --- |
| ファイルの読み書き（`CreateFileW`、`_wfopen`） | UTF-8 のパス → UTF-16（`Utf8ToWide`） |
| ウィンドウのタイトル・メッセージ ボックス | UTF-8 → UTF-16（`SetWindowTextW`、`MessageBoxW`） |
| ファイル ダイアログで選んだパス | UTF-16 → UTF-8 で、ゲームに渡す |
| 古いシナリオ・CSV の読み込み | CP932 → UTF-8（読み込み時に 1 回） |
| コマンド ライン引数 | `wmain` / `GetCommandLineW` の UTF-16 → UTF-8 |
| ネットワーク | 常に UTF-8（JSON など）。変換は不要 |

<!-- fig:utf8-pack:begin -->

<svg class="fig illust motion" data-fig="utf8-pack" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-utf8-pack" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">「あ」(U+3042) を UTF-8 の 3 バイトに詰める</text>
<text x="100" y="90" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">コードポイント U+3042 を 2 進数に(16 ビット)</text>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="100" y="100" width="26" height="26" fill="#2563eb" opacity="0.85"/>
<text x="113.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="128" y="100" width="26" height="26" fill="#2563eb" opacity="0.85"/>
<text x="141.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="156" y="100" width="26" height="26" fill="#2563eb" opacity="0.85"/>
<text x="169.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="184" y="100" width="26" height="26" fill="#2563eb" opacity="0.85"/>
<text x="197.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="220" y="100" width="26" height="26" fill="#2ea043" opacity="0.85"/>
<text x="233.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="248" y="100" width="26" height="26" fill="#2ea043" opacity="0.85"/>
<text x="261.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="276" y="100" width="26" height="26" fill="#2ea043" opacity="0.85"/>
<text x="289.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="304" y="100" width="26" height="26" fill="#2ea043" opacity="0.85"/>
<text x="317.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="332" y="100" width="26" height="26" fill="#2ea043" opacity="0.85"/>
<text x="345.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="360" y="100" width="26" height="26" fill="#2ea043" opacity="0.85"/>
<text x="373.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="396" y="100" width="26" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="409.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="424" y="100" width="26" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="437.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="452" y="100" width="26" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="465.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="480" y="100" width="26" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="493.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="508" y="100" width="26" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="521.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="536" y="100" width="26" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="549.0" y="119" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#ffffff">0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;1.0000" values="0;0;1;1"/><rect x="100" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="111.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<rect x="125" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="136.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<rect x="150" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="161.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<rect x="175" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="186.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="200" y="230" width="23" height="26" fill="#2563eb" opacity="0.85"/>
<text x="211.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="225" y="230" width="23" height="26" fill="#2563eb" opacity="0.85"/>
<text x="236.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="250" y="230" width="23" height="26" fill="#2563eb" opacity="0.85"/>
<text x="261.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<rect x="275" y="230" width="23" height="26" fill="#2563eb" opacity="0.85"/>
<text x="286.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<text x="200" y="285" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#2563eb">= E3</text>
</g>
<line x1="156.0" y1="132" x2="200" y2="224" stroke="#2563eb" stroke-width="2" marker-end="url(#arr-utf8-pack)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;1.0000" values="0;0;1;1"/></line>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4255;0.4258;1.0000" values="0;0;1;1"/><rect x="330" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="341.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<rect x="355" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="366.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="380" y="230" width="23" height="26" fill="#2ea043" opacity="0.85"/>
<text x="391.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="405" y="230" width="23" height="26" fill="#2ea043" opacity="0.85"/>
<text x="416.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="430" y="230" width="23" height="26" fill="#2ea043" opacity="0.85"/>
<text x="441.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="455" y="230" width="23" height="26" fill="#2ea043" opacity="0.85"/>
<text x="466.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="480" y="230" width="23" height="26" fill="#2ea043" opacity="0.85"/>
<text x="491.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="505" y="230" width="23" height="26" fill="#2ea043" opacity="0.85"/>
<text x="516.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<text x="430" y="285" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#2ea043">= 81</text>
</g>
<line x1="304.0" y1="132" x2="430" y2="224" stroke="#2ea043" stroke-width="2" marker-end="url(#arr-utf8-pack)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4255;0.4258;1.0000" values="0;0;1;1"/></line>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5933;0.5935;1.0000" values="0;0;1;1"/><rect x="560" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="571.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<rect x="585" y="230" width="23" height="26" fill="#64748b" opacity="0.85"/>
<text x="596.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="610" y="230" width="23" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="621.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="635" y="230" width="23" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="646.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="660" y="230" width="23" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="671.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="685" y="230" width="23" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="696.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<rect x="710" y="230" width="23" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="721.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">1</text>
<rect x="735" y="230" width="23" height="26" fill="#e5aa28" opacity="0.85"/>
<text x="746.5" y="249" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">0</text>
<text x="660" y="285" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5aa28">= 82</text>
</g>
<line x1="480.0" y1="132" x2="660" y2="224" stroke="#e5aa28" stroke-width="2" marker-end="url(#arr-utf8-pack)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5933;0.5935;1.0000" values="0;0;1;1"/></line>
<text x="100" y="215" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">3 バイト形式の枠（灰色 = 目印のビット、色付き = 中身）</text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">文字に番号(コードポイント)が付いている<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">16 ビットを 4 + 6 + 6 に分ける<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">先頭バイト: 目印 1110 + 上位 4 ビット = E3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4255;0.4258;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 バイト目: 目印 10 + 次の 6 ビット = 81<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4255;0.4258;0.5933;0.5935;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="350" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 バイト目: 目印 10 + 残りの 6 ビット = 82。「あ」 = E3 81 82<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5933;0.5935;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:utf8-pack:end -->

## よくあるミス

??? failure "戻り値を確認せずに使う"
    変換が失敗すると 0 が返ります。確認せずに `wstring(0, ...)` で進むと空の文字列になって、原因が分かりにくくなります。

??? failure "`CP_ACP` で変換して、環境で結果が変わる"
    開発 PC（日本語）では動くのに、海外の PC で化けます。UTF-8（`CP_UTF8`）か明示的な 932 を使います。

??? failure "文字数をバイト数のつもりで渡す"
    `MultiByteToWideChar` の長さは**入力のバイト数**、出力は**`wchar_t` の数**です。取り違えるとバッファ オーバーランになります。

??? failure "`wstring_convert` が非推奨の警告で埋まる"
    使わずに Win32 API か utfcpp などに置き換えます。

??? failure "表せない文字を Shift_JIS に変換して、`?` になる"
    UTF-8 の絵文字や珍しい漢字は、Shift_JIS にはありません。Shift_JIS が必要な相手（古いツール）には、**事前に文字を制限する**か相手を UTF-8 対応にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 変換は<strong>境界でだけ</strong>。内部は UTF-8
    - [x] Windows は<strong>`MultiByteToWideChar` / `WideCharToMultiByte`</strong>。<strong>2 回呼ぶ</strong>、<strong>戻り値を確認</strong>
    - [x] <strong>`CP_ACP` はデータに使わない</strong>。<strong>`CP_UTF8`</strong> と <strong>932</strong> を明示
    - [x] 標準の <strong>`codecvt` / `wstring_convert` は使わない</strong>（非推奨）。移植するなら utfcpp / simdutf / ICU
    - [x] 不正な入力は<strong>エラーにするか�に置き換える</strong>かを決める

## 関連ページ

- [文字コード（目次）](index.md)
- [C++ の文字型と文字列型](string-types.md)
- [Windows API と文字コード](windows-api.md)
- [外部ライブラリと文字コード](libraries.md)
- [コンソールとファイルの入出力](console-file-io.md)
