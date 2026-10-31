---
title: std::wformat_string
summary: "書式文字列を、コンパイル時に検査する型（wchar_t 版の別名）。"
order: 900
tags:
  - ユーティリティ
---

# std::wformat_string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format_string` の `wchar_t` 版が `std::wformat_string<Args...>` です。`std::format(L"{}", x)` の第 1 引数の型で、`L"..."` の書式文字列を、コンパイル時に検査します。Windows API の `wchar_t` の文字列に合わせて、整形するときに使います。

!!! tip "ポイント"
    - `basic_format_string<wchar_t, type_identity_t<Args>...>` の別名
    - `std::format(L"...", ...)` の第 1 引数の型
    - 結果は `std::wstring`
    - `std::println` は `wstring` を直接出せない

!!! info "このページを読む前に"
    [`std::format_string`](format_string.md) を先に読んでください。

## 関数の詳しい説明

### std::wformat_string {#wformat_string}

<span class="ver ver-20">C++20</span>

```cpp
template <class... Args>
using wformat_string = std::basic_format_string<wchar_t, std::type_identity_t<Args>...>;
```

使い方は `format_string` と同じで、書式と結果が `wchar_t` になるだけです。

```cpp
std::wstring s = std::format(L"HP {} / MP {}", 30, 12);
```

結果の `std::wstring` を、画面や `std::println` に出すには、UTF-8 に変換するか、`std::wcout` を使います。環境により、コンソールでの扱いが違います。

自作の関数で包むなら、`wformat_string<Args...>` を第 1 引数にします。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>
#include <utility>

template <class... Args>
std::wstring WFormat(std::wformat_string<Args...> fmt, Args&&... args) {
  return std::format(fmt, std::forward<Args>(args)...);
}

int main() {
  const std::wstring s = WFormat(L"HP {} / MP {}", 30, 12);
  std::println("一致: {}", s == L"HP 30 / MP 12");
  std::println("長さ: {}", s.size());
}
```

```text title="実行結果"
一致: true
長さ: 13
```

## ゲームでの使いどころ

Windows API に `wchar_t` のメッセージを渡す場面（`MessageBoxW` など）で、整形に使います。

## よくあるミス

??? failure "char の書式に wchar_t を渡す"
    `std::format("{}", L"abc")` は、コンパイルできません。書式と引数の文字の型を合わせます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_string`](format_string.md) | `char` 版 |
| [`basic_format_string`](basic_format_string.md) | 元のテンプレート |
| [`make_wformat_args`](make_wformat_args.md) | `wchar_t` の引数を作る |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::wformat_string](https://cpprefjp.github.io/reference/format/wformat_string.html)
- [cppreference: std::wformat_string](https://en.cppreference.com/w/cpp/utility/format/wformat_string)
