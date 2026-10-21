---
title: std::boolalpha
summary: "bool を `1` / `0` ではなく `true` / `false` で出力する。"
order: 81
tags:
  - 入出力・文字列
---

# std::boolalpha

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

`std::boolalpha` は、**`bool` を `1` / `0` ではなく、`true` / `false` の文字で出力する**マニピュレーターです。`std::println` は既定で `true` / `false` と出力するので、新しいコードでは不要です。**設定は残り続ける**ので、戻すには `std::noboolalpha` を使います。

!!! tip "ポイント"
    - `std::cout << std::boolalpha << true;` → `true`。
    - 設定は残り続ける。
    - `std::println("{}", flag)` は最初から `true` / `false`。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) などの出力ストリームの設定です。新しいコードでは [`std::println`](../utilities/print.md) の書式が簡単です。

## 関数の詳しい説明

### std::boolalpha {#boolalpha}

```cpp
std::ios_base& boolalpha(std::ios_base& str);
std::ios_base& noboolalpha(std::ios_base& str);
```

- 戻り値: `str`
- 計算量: O(1)

```cpp
#include <iostream>

int main() {
  std::cout << true << ' ' << std::boolalpha << true << '\n';
}
```

```text title="実行結果"
1 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードで、bool を読める形で出す | `std::cout << std::boolalpha << flag;` |

## よくあるミス

??? failure "設定が残る"
    後の bool もすべて文字で出ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | 最初から true / false |
| [`fixed`](fixed.md) | 小数の形 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] bool を文字で出す
    - [x] 設定は残る
    - [x] println は不要

## 関連ページ

- [cpprefjp: std::boolalpha](https://cpprefjp.github.io/reference/ios/boolalpha.html)
- [cppreference: std::boolalpha](https://en.cppreference.com/w/cpp/io/manip/boolalpha)
