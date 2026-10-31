---
title: std::make_wformat_args
summary: "引数を、wchar_t 用の書式化引数リストにまとめる。"
order: 900
tags:
  - ユーティリティ
---

# std::make_wformat_args

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::make_format_args` の `wchar_t` 版が `std::make_wformat_args` です。`std::vformat(L"...", ...)` に渡す引数を包みます。使い方は `make_format_args` と同じで、書式と結果が `wchar_t` になります。

!!! tip "ポイント"
    - `wformat_args` を作る。`vformat(wstring_view, ...)` に渡す
    - 引数は左辺値の変数
    - 返したオブジェクトは参照を持つ
    - 結果は `std::wstring`

!!! info "このページを読む前に"
    [`std::make_format_args`](make_format_args.md) を先に読んでください。

## 関数の詳しい説明

### std::make_wformat_args {#make_wformat_args}

<span class="ver ver-20">C++20</span>

```cpp
template <class... Args>
/* format_arg_store<wformat_context, Args...> */ make_wformat_args(Args&... args);
```

`make_format_args<std::wformat_context>(args...)` の短い書き方です。

`char` の文字列を `wchar_t` の書式に渡すことは、できません（`std::string` を `wformat` に渡すとコンパイル エラー）。引数の文字列も `wchar_t` のものにします。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  int hp = 30;
  std::wstring name = L"Hero";

  const std::wstring s = std::vformat(L"{}: HP {}", std::make_wformat_args(name, hp));
  std::println("一致: {}", s == L"Hero: HP 30");
  std::println("長さ: {}", s.size());
}
```

```text title="実行結果"
一致: true
長さ: 11
```

## ゲームでの使いどころ

Windows API 用の `wchar_t` のメッセージを、実行時の書式で整形するときに使います。

## よくあるミス

??? failure "char の文字列を渡す"
    `std::string` の引数は、`wformat` では使えません。`std::wstring` にそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_format_args`](make_format_args.md) | `char` 版 |
| [`wformat_string`](wformat_string.md) | `wchar_t` の書式文字列 |
| [`vformat`](vformat.md) | これを受け取る |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::make_wformat_args](https://cpprefjp.github.io/reference/format/make_wformat_args.html)
- [cppreference: std::make_wformat_args](https://en.cppreference.com/w/cpp/utility/format/make_wformat_args)
