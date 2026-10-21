---
title: std::invalid_argument
summary: "引数の値が不正なときの例外。"
order: 4
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::invalid_argument

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <stdexcept>`
</div>

`std::invalid_argument` は、**関数に渡された引数の値が不正だった**ことを表す例外です。`std::stoi("abc")` が、数字として読めない文字列に対して投げます。自作の関数でも、引数の検査に使えます。

!!! tip "ポイント"
    - `std::stoi` / `std::stof` は、変換できないと投げる。
    - `logic_error` の派生クラス。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::invalid_argument {#invalid_argument}

```cpp
class invalid_argument : public logic_error;
```

- 引数がおかしいことを表します。`std::stoi` などに数字で始まらない文字列を渡すと投げられます

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>
#include <string>

int main() {
  try {
    std::stoi("abc");   // 数字として読めない
  } catch (const std::invalid_argument&) {
    std::println("不正な引数");
  }
}
```

```text title="実行結果"
不正な引数
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定値が不正なときに投げる | `throw std::invalid_argument("hp must be positive");` |

## よくあるミス

??? failure "例外を握りつぶす"
    `catch (...) {}` で黙殺すると、原因が分からなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`out_of_range`](out_of_range.md) | 範囲外 |
| [`std::from_chars`](../../io/from_chars.md) | 例外なしの変換 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数が不正
    - [x] `stoi` が投げる
    - [x] logic_error の仲間

## 関連ページ

- [cpprefjp: std::invalid_argument](https://cpprefjp.github.io/reference/stdexcept/invalid_argument.html)
- [cppreference: std::invalid_argument](https://en.cppreference.com/w/cpp/error/invalid_argument)
