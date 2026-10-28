---
title: std::wcstombs
summary: "wchar_t の文字列をマルチバイト文字列に変換する。"
order: 900
tags:
  - 数値
---

# std::wcstombs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

Windows の API が返したワイド文字列（`wchar_t`）をゲームの内部で使うマルチバイトの文字列に戻すのが `std::wcstombs` です。`std::mbstowcs` の逆の変換です。

!!! tip "ポイント"
    - `std::wcstombs(dest, src, n)` は文字列全体を変換する
    - 戻り値は書き込んだバイト数（null を除く）。変換できなければ `(size_t)-1`
    - `dest` が `nullptr` なら、必要なバイト数だけを返す
    - MSVC は安全版の `wcstombs_s` を勧める（警告 C4996）

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::wcstombs {#wcstombs}

```cpp
std::size_t wcstombs(char* dest, const wchar_t* src, std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | 書き込み先。`nullptr` なら長さだけ調べる |
| `src` | `const wchar_t*` | 変換元（null で終わる） |
| `n` | `size_t` | `dest` に書き込める最大のバイト数 |

`src` を現在のロケールのマルチバイト表現に変換して `dest` に書き込みます。戻り値は書き込んだバイト数で、終端の null は数えません。変換できない文字があれば `static_cast<std::size_t>(-1)` を返します。

1 つのワイド文字が複数バイトになるので、必要な大きさは文字数より大きくなります。先に `dest = nullptr` で呼んで必要なバイト数を調べ、`+ 1` で確保します。

既定の "C" ロケールでは、ASCII 以外の文字は変換できず、−1 を返します。Windows で UTF-8 に変換するなら `WideCharToMultiByte(CP_UTF8, ...)` を使います。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  const std::size_t length = std::wcstombs(nullptr, L"abc", 0);   // 必要なバイト数を調べる
  std::println("必要なバイト数 = {}", length);

  char buffer[4];
  const std::size_t written = std::wcstombs(buffer, L"abc", 4);
  std::println("書き込んだバイト数 = {}", written);
}
```

```text title="実行結果"
必要なバイト数 = 3
書き込んだバイト数 = 3
```

## ゲームでの使いどころ

Windows API から受け取ったワイド文字列をログに出すために変換するときなどに使います。UTF-8 の日本語は `WideCharToMultiByte` を使います。

## よくあるミス

??? failure "変換先が小さくてあふれる"
    先に必要なバイト数を調べます。

??? failure "日本語が変換できず −1 になる"
    ロケールを設定するか、`WideCharToMultiByte` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbstowcs`](mbstowcs.md) | 逆の変換 |
| [`wctomb`](wctomb.md) | 1 文字だけ変換 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcstombs` はワイド文字列をマルチバイト文字列に変換する
    - [x] `dest = nullptr` で必要なバイト数を調べる
    - [x] Windows の UTF-8 は `WideCharToMultiByte`

## 関連ページ

- [cpprefjp: std::wcstombs](https://cpprefjp.github.io/reference/cstdlib/wcstombs.html)
- [cppreference: std::wcstombs](https://en.cppreference.com/w/cpp/c/wcstombs)
