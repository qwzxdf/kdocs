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

`bool` を出力すると、`1` や `0` と出ます。ログに「フラグ: 1」と出ても意味が分かりにくい。`true` や `false` と書いてほしい。`std::boolalpha` は、<strong>`bool` を文字で出し入れする</strong>操作子です。

!!! tip "ポイント"
    - `std::boolalpha` で、`bool` を `true` / `false` で出力する
    - 入力にも効く。`true` / `false` の文字列を `bool` として読む
    - 設定は残る。戻すには `std::noboolalpha`
    - ロケールによっては、`true` / `false` が別の言葉になる

!!! info "このページを読む前に"
    [`std::cout`](cout.md) などの出力ストリームの設定です。新しいコードでは [`std::println`](../utilities/print.md) の書式が簡単です。

## 関数の詳しい説明

### std::boolalpha {#boolalpha}

```cpp
std::ios_base& boolalpha(std::ios_base& str);
```

既定では、`bool` は整数の `1` と `0` で出入力されます。`boolalpha` を立てると、ロケールで決まる文字列、つまり "C" ロケールなら `true` と `false` を使います。

入力では、`true` / `false` の文字列だけを受け付けます。`boolalpha` を立てたまま `1` を読み込もうとすると、失敗します。設定ファイルの読み込みで、期待する形式に合わせて設定します。

日本語ロケールを設定しても、標準のロケールには `true` / `false` の日本語訳が用意されていないことが多く、結果は英語のままです。

`std::print` / `std::format` は、`bool` を既定で `true` / `false` と出すので、`boolalpha` は不要です。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <sstream>

int main() {
  bool alive = true;
  std::cout << alive << '\n';                           // 1
  std::cout << std::boolalpha << alive << '\n';         // true
  std::cout << false << '\n';                           // false
  std::cout << std::noboolalpha << false << '\n';       // 0

  // 入力にも効く
  std::istringstream in("true false");
  bool a, b;
  in >> std::boolalpha >> a >> b;
  std::cout << a << b << '\n';                          // 10
}
```

```text title="実行結果"
1
true
false
0
10
```

## ゲームでの使いどころ

ログに真偽値を出すときに使います。「alive: true」と出ると、一目で分かります。設定ファイルから `true` / `false` を読むときにも使えます。

## よくあるミス

??? failure "`boolalpha` を立てたまま、`1` を読み込んで失敗する"
    入力の形式に合わせて、設定を切り替えます。

??? failure "戻し忘れて、他の `bool` も文字になる"
    `noboolalpha` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::format` | C++20 で `bool` を `true`/`false` と出す |
| `std::print` | C++23。同上 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bool` を `true` / `false` で出し入れする
    - [x] 入力にも効く
    - [x] 戻すのは `noboolalpha`

## 関連ページ

- [cpprefjp: std::boolalpha](https://cpprefjp.github.io/reference/ios/boolalpha.html)
- [cppreference: std::boolalpha](https://en.cppreference.com/w/cpp/io/manip/boolalpha)
