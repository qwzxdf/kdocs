---
title: std::size
summary: "コンテナや配列の要素数を返す（配列にも使える）。"
order: 5
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::size

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <iterator>`
</div>

配列の要素数を調べるとき、昔は `sizeof(a) / sizeof(a[0])` と書いていました。見慣れた書き方ですが、ポインターに変換された配列に使うと、間違った値が静かに返ってきます。`std::size(c)` は、コンテナや配列の要素数を返す関数です。`c.size()` と同じ意味ですが、生の配列 `int a[5]` にも使えます。ポインターに変換された配列に使うと、コンパイルエラーで教えてくれます。

!!! tip "ポイント"
    - 生の配列では `sizeof(a) / sizeof(a[0])` の代わりに。
    - 符号つきが欲しければ [`ssize`](ssize.md)。
    - ポインターに変換された配列には使えない。

!!! info "このページを読む前に"
    配列とポインターの違いが分かると読みやすいです。配列は、関数の引数に渡すとポインターに変換されて、大きさの情報が消えます。

## 関数の詳しい説明

### std::size {#size}

<span class="ver ver-17">C++17</span>

```cpp
template <class C>
constexpr auto size(const C& c) -> decltype(c.size());
template <class T, std::size_t N>
constexpr std::size_t size(const T (&array)[N]) noexcept;
```

- C の配列でもコンテナでも要素数を返します。`sizeof(a) / sizeof(a[0])` の代わり

## しくみ

`std::size(c)` は、`c.size()` を呼びます。生の配列には、専用のオーバーロードが用意されていて、テンプレートの引数から大きさを取り出して返します。

ポインターに変換された配列は、大きさの情報がないので、`std::size` を呼ぶとコンパイルエラーになります。`sizeof(p) / sizeof(p[0])` のように書いて、ポインターのサイズを要素数と取り違える事故がなくなります。

戻り値は符号なしの `size_t` です。符号付きの値が欲しいときは、`std::ssize(c)` を使います。ループの条件 `i < std::size(a)` で、`int` の `i` と比べると、符号の警告が出る場合に便利です。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  int a[5] = {};
  std::vector<int> v = {1, 2, 3};
  std::println("{} {}", std::size(a), std::size(v));
}
```

```text title="実行結果"
5 3
```

## ゲームでの使いどころ

固定長の配列の要素数を取るときに使います。`constexpr int kSlots[] = {...};` のような定数の配列を、`for (size_t i = 0; i < std::size(kSlots); ++i)` で回せます。要素を増やしても、数を書き直す必要がありません。

`array` と `vector` のどちらでも同じ書き方になるので、テンプレート関数の中で、どちらのコンテナも受け付けるときに便利です。

C の API とやり取りするときは、配列がポインターになっていないか注意します。関数の引数で受けた配列には、`std::size` が使えません。`std::span` で受ければ、大きさも一緒に持ち運べます。

## よくあるミス

??? failure "関数の引数で受けた配列に使う"
    `void F(int a[10])` は、引数 `a` が `int*` になっているので、`std::size(a)` はコンパイルエラーになります。`std::span<int>` や `std::array` で受けます。

??? failure "符号なしの戻り値を、`int` と比べて警告になる"
    `int i = ...; i < std::size(a)` は、符号の違う比較の警告になります。`std::ssize(a)` を使うか、`i` を `size_t` にします。

??? failure "`sizeof` との取り違え"
    `sizeof(a)` はバイト数で、要素数ではありません。`std::size(a)` が要素数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ssize`](ssize.md) | 符号付きの要素数を返す |
| `c.size()` | コンテナのメンバー関数。生の配列には使えない |
| [`std::span`](../../containers/span.md) | 大きさも一緒に持ち運べる |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::size(c)` で、コンテナにも生の配列にも使える。
    - [x] ポインターに変換された配列はコンパイルエラー。
    - [x] 符号付きが欲しいときは `ssize`。

## 関連ページ

- [cpprefjp: std::size](https://cpprefjp.github.io/reference/iterator/size.html)
- [cppreference: std::size](https://en.cppreference.com/w/cpp/iterator/size)
