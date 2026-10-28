---
title: std::empty
summary: "コンテナが空かを調べる（配列・initializer_list にも使える）。"
order: 7
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::empty

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

配列とコンテナの両方を受け取る関数で、「空かどうか」を調べたい。コンテナは `c.empty()` ですが、配列にはメンバー関数がありません。`std::empty` は、<strong>配列にもコンテナにも使える「空か」の判定</strong>です。

!!! tip "ポイント"
    - `std::empty(c)` はコンテナなら `c.empty()`、配列なら `false`
    - 要素数 0 の `std::initializer_list` にも使える
    - 汎用のテンプレートで使える
    - `<iterator>` で宣言される

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::empty {#empty}

<span class="ver ver-17">C++17</span>

```cpp
template <class C>
constexpr auto empty(const C& c) -> decltype(c.empty());
template <class T, std::size_t N>
constexpr bool empty(const T (&array)[N]) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナまたは配列 | 対象 |

コンテナなら `c.empty()` の結果を返します。配列は、要素数が型に含まれていて、長さ 0 の配列は作れないので、常に `false` です。

`size() == 0` と書くより `empty()` のほうが、意図が明確で、コンテナによっては速いです（`std::list` など）。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v;
  int a[3] = {1, 2, 3};
  std::println("空の vector: {}", std::empty(v));
  std::println("配列は常に false: {}", std::empty(a));
}
```

```text title="実行結果"
空の vector: true
配列は常に false: false
```

## ゲームでの使いどころ

汎用のテンプレートで、空の入力を早めに弾きます。

```cpp
template <class Range>
void Process(const Range& r) {
  if (std::empty(r)) return;
}
```

## よくあるミス

??? failure "`size() == 0` で書いて遅い"
    `empty()` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ssize`](ssize.md) | 符号つきの要素数 |
| [`begin`](begin.md) | 先頭のイテレーター |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::empty(c)` は空かを調べる
    - [x] 配列にも使える（常に `false`）
    - [x] `size() == 0` より `empty()`

## 関連ページ

- [cpprefjp: std::empty](https://cpprefjp.github.io/reference/iterator/empty.html)
- [cppreference: std::empty](https://en.cppreference.com/w/cpp/iterator/empty)
