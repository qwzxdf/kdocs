---
title: std::mbstowcs
summary: "マルチバイト文字列を wchar_t の文字列に変換する。"
order: 900
tags:
  - 数値
---

# std::mbstowcs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

Windows の API の多くは、ワイド文字列（`wchar_t`）を要求します。ゲームの内部で持つマルチバイトの文字列（`char`）をワイド文字列に変換するのが `std::mbstowcs` です。

!!! tip "ポイント"
    - `std::mbstowcs(dest, src, n)` は文字列全体を変換する
    - 戻り値は変換したワイド文字数（null を除く）。不正なら `(size_t)-1`
    - `dest` が `nullptr` なら、必要な長さだけを返す
    - MSVC は安全版の `mbstowcs_s` を勧める（警告 C4996）

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::mbstowcs {#mbstowcs}

```cpp
std::size_t mbstowcs(wchar_t* dest, const char* src, std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `wchar_t*` | 変換結果の書き込み先。`nullptr` なら長さだけ調べる |
| `src` | `const char*` | 変換元（null で終わる） |
| `n` | `size_t` | `dest` に書き込める最大のワイド文字数 |

`src` を現在のロケールのマルチバイト規則で解釈し、ワイド文字列に変換して `dest` に書き込みます。戻り値は書き込んだ文字数で、終端の null は数えません。不正なバイト列があれば `static_cast<std::size_t>(-1)` を返します。

`n` に達しても null を書けなかった場合は、`dest` が null で終わらないので注意します。必要な長さは、先に `dest = nullptr` で呼んで調べ、`+ 1` で確保するのが安全な手順です。

既定の "C" ロケールでは ASCII しか正しく変換されません。Windows の UTF-8 の文字列を扱うなら、`MultiByteToWideChar(CP_UTF8, ...)` が確実です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  const std::size_t length = std::mbstowcs(nullptr, "abc", 0);   // 必要な長さだけを調べる
  std::println("必要な長さ = {}", length);

  wchar_t buffer[4];
  const std::size_t written = std::mbstowcs(buffer, "abc", 4);
  std::println("書き込んだ数 = {}", written);
}
```

```text title="実行結果"
必要な長さ = 3
書き込んだ数 = 3
```

## ゲームでの使いどころ

Windows API にファイル名を渡す前の変換などで使われます。UTF-8 が前提のゲームでは、変換用の自作関数（`MultiByteToWideChar` を包む）を 1 つ用意して使います。

## よくあるミス

??? failure "`n` ぎりぎりで null が書かれず、文字列が壊れる"
    先に長さを調べ、`+ 1` で確保します。

??? failure "UTF-8 の日本語が文字化けする"
    ロケールの設定か、`MultiByteToWideChar` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wcstombs`](wcstombs.md) | 逆の変換 |
| [`mbtowc`](mbtowc.md) | 1 文字だけ変換 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mbstowcs` はマルチバイト文字列をワイド文字列に変換する
    - [x] `dest = nullptr` で必要な長さを調べる
    - [x] Windows の UTF-8 は `MultiByteToWideChar`

## 関連ページ

- [cpprefjp: std::mbstowcs](https://cpprefjp.github.io/reference/cstdlib/mbstowcs.html)
- [cppreference: std::mbstowcs](https://en.cppreference.com/w/cpp/c/mbstowcs)
