---
title: std::basic_ostream
summary: "出力ストリームの元になるテンプレート（`ostream` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_ostream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ostream>`
</div>

`std::ostream` は、`basic_ostream<char>` の別名です。文字の型を選べるように、元になるクラステンプレートがあります。ふつうは別名の `ostream` を使います。

!!! tip "ポイント"
    - `basic_ostream` は `basic_ios` から派生。
    - ふつうは別名（`istream`・`ostream`）を使う。
    - 関数の引数には、参照で受ける。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_ostream {#basic_ostream}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_ostream;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_class_v<std::basic_ostream>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ストリームを引数で受ける関数 | `void Save(std::ostream& os);` |

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
    - [x] 出力ストリームの元になるテンプレート（`ostream` の元）
    - [x] コピーできないので参照で受ける
    - [x] ふつうは別名を使う

## 関連ページ

- [cpprefjp: std::basic_ostream](https://cpprefjp.github.io/reference/ostream/basic_ostream.html)
- [cppreference: std::basic_ostream](https://en.cppreference.com/w/cpp/io/basic_ostream)
