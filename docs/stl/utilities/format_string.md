---
title: std::format_string
summary: "書式文字列を、コンパイル時に検査する型（char 版の別名）。"
order: 900
tags:
  - ユーティリティ
---

# std::format_string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

自作のログ関数で、書式文字列を引数に受けたいとき、`std::string` で受けるとコンパイル時の検査が効きません。`std::format_string<Args...>` で受けると、`std::format` と同じように、書式の誤りをコンパイル時に検出できます。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::format_string {#format_string}

```cpp
template <class... Args>
using format_string = basic_format_string<char, type_identity_t<Args>...>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Args...` | 型 | 書式に渡す引数の型 |

- 戻り値: 書式文字列の検査つきの引数型
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <utility>

template <class... Args>
void Log(std::format_string<Args...> fmt, Args&&... args) {
  std::println(fmt, std::forward<Args>(args)...);
}

int main() {
  Log("value={}", 5);
}
```

```text title="実行結果"
value=5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 型安全な自作のログ関数 |

## よくあるミス

??? failure "`std::string` で受ける"
    コンパイル時の検査が効かなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_format_string`](basic_format_string.md) | 元のテンプレート |
| [`vformat`](vformat.md) | 実行時の書式文字列 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式文字列をコンパイル時に検査する型（char 版の別名）
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::format_string](https://cpprefjp.github.io/reference/format/format_string.html)
- [cppreference: std::format_string](https://en.cppreference.com/w/cpp/utility/format/format_string)
