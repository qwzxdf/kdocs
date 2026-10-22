---
title: std::basic_istream
summary: "入力ストリームの元になるテンプレート（`istream` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_istream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <istream>`
</div>

`std::istream` は、`basic_istream<char>` の別名です。文字の型（`char`・`wchar_t`）を選べるように、元になるクラステンプレートがあります。ふつうは別名の `istream` を使います。

!!! tip "ポイント"
    - `basic_istream` は `basic_ios` から派生。
    - ふつうは別名（`istream`・`ostream`）を使う。
    - 関数の引数には、参照で受ける。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_istream {#basic_istream}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_istream;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_class_v<std::basic_istream>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ストリームを引数で受ける関数 | `void Load(std::istream& is);` |

## よくあるミス

??? failure "値で受ける"
    ストリームはコピーできません。参照（`&`）で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`istream`](istream.md) | 入力ストリーム |
| [`ostream`](ostream.md) | 出力ストリーム |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力ストリームの元になるテンプレート（`istream` の元）
    - [x] コピーできないので参照で受ける
    - [x] ふつうは別名を使う

## 関連ページ

- [cpprefjp: std::basic_istream](https://cpprefjp.github.io/reference/istream/basic_istream.html)
- [cppreference: std::basic_istream](https://en.cppreference.com/w/cpp/io/basic_istream)
