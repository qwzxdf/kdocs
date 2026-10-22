---
title: std::wistream
summary: "`wchar_t` の入力ストリーム。"
order: 900
tags:
  - 入出力・文字列
---

# std::wistream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <istream>`
</div>

`std::wistream` は、`basic_istream<wchar_t>` の別名です。`wchar_t` の文字列を入力するときに使います（`std::wcin` の型）。

!!! tip "ポイント"
    - `wistream` は `basic_istream<wchar_t>` から派生。
    - ふつうは別名（`istream`・`ostream`）を使う。
    - 関数の引数には、参照で受ける。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::wistream {#wistream}

```cpp
using wistream = /* basic_istream<wchar_t> */;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_class_v<std::wistream>);
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
    - [x] `wchar_t` の入力ストリーム
    - [x] コピーできないので参照で受ける
    - [x] ふつうは別名を使う

## 関連ページ

- [cpprefjp: std::wistream](https://cpprefjp.github.io/reference/istream/wistream.html)
- [cppreference: std::wistream](https://en.cppreference.com/w/cpp/io/wistream)
