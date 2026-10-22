---
title: std::basic_string_view
summary: "string_view / wstring_view などの元になる、文字の型を選べるテンプレート。"
order: 900
tags:
  - ユーティリティ
---

# std::basic_string_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <string_view>`
</div>

`std::string_view` は、実は `basic_string_view<char>` の別名です。文字の型が `wchar_t` や `char8_t` のときも同じ仕組みで使えるように、元になるクラステンプレートがあります。自分で直接書くことは少なく、別名を使います。

!!! tip "ポイント"
    - `string_view` = `basic_string_view<char>`。
    - 文字の型を `CharT` で選ぶ。
    - テンプレートの引数で任意の文字型を受けるとき（ジェネリックな関数）に書く。

!!! info "このページを読む前に"
    [`std::string_view`](string_view.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_string_view {#basic_string_view}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_string_view;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharT` | 型 | 文字の型 |
| `Traits` | 型 | 省略可。比較などの規則 |

- 戻り値: string_view と同じ関数をもつ
- 計算量: string_view と同じ


## 実際に動かしてみる

```cpp
#include <print>
#include <string_view>

int main() {
  std::basic_string_view<char> v = "hello";
  std::println("{}", v.substr(1, 3));
}
```

```text title="実行結果"
ell
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 文字の型を問わない関数 | `template <class CharT> void F(std::basic_string_view<CharT> s);` |

## よくあるミス

??? failure "別名と取り違える"
    関数の引数には `std::string_view` を書けば、たいていは足ります。`basic_string_view` は、型を問わない関数を書くときだけ登場します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`string_view`](string_view.md) | char の版 |
| [`wstring_view`](wstring_view.md) | wchar_t の版 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] string_view の元のテンプレート
    - [x] CharT で文字の型を選ぶ
    - [x] ふつうは別名を使う

## 関連ページ

- [cpprefjp: std::basic_string_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::basic_string_view](https://en.cppreference.com/w/cpp/string/basic_string_view)
