---
title: std::cbegin
summary: "コンテナや配列の先頭を指す、const のイテレータを返す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::cbegin

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-14">C++14</span>
`#include <iterator>`
</div>

範囲 for を使わず、イテレーターでループを書くとき、`v.cbegin()` と書くのは配列には使えません。配列も、コンテナも、同じ書き方で扱えるのが、非メンバー関数の `std::cbegin` です。<strong>先頭を指す読み取り専用のイテレーター</strong>を返します。

!!! tip "ポイント"
    - `std::cbegin(c)` は 先頭を指す読み取り専用のイテレーター
    - コンテナにはメンバー関数 `c.cbegin()` を、配列にはポインターを返す
    - 汎用のテンプレートで、配列とコンテナを同じように扱える
    - 範囲 for の内部で使われている

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cbegin {#cbegin}

<span class="ver ver-14">C++14</span>

```cpp
template <class C>
auto cbegin(C& c) -> decltype(c.cbegin());
template <class T, std::size_t N>
T* cbegin(T (&array)[N]) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナまたは配列 | 対象 |

`std::cbegin(c)` は、コンテナなら `c.cbegin()` を呼んだ結果を、配列なら配列の先頭のポインターを返します。読み取り専用なので、要素を書き換えられません。

汎用のテンプレートで、配列とコンテナの両方を受け取る関数を書くときに使います。範囲 for は、内部でこの規則を使っています。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <type_traits>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};
  using Ref = decltype(*std::cbegin(v));
  std::println("要素は const 参照: {}", std::is_same_v<Ref, const int&>);
  std::println("先頭から末尾までの距離: {}", std::cend(v) - std::cbegin(v));
}
```

```text title="実行結果"
要素は const 参照: true
先頭から末尾までの距離: 3
```

## ゲームでの使いどころ

汎用のテンプレートで、配列とコンテナを同じ書き方で走査します。

```cpp
template <class Range>
void Dump(const Range& r) {
  for (auto it = std::begin(r); it != std::end(r); ++it) Print(*it);
}
```

コンテナだけを扱うなら、`v.begin()` と書いても同じです。

## よくあるミス

??? failure "空のコンテナの先頭を参照する"
    `begin() == end()` のとき、`*begin()` は未定義動作です。

??? failure "末尾を指すイテレーターを参照する"
    `end()` は最後の要素の 1 つ後ろです。参照できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`size`](ssize.md) | 要素数 |
| [`next`](next.md) | イテレーターを進める |

## コンパイラ対応

C++14 から使えます。`<iterator>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::cbegin(c)` は先頭を指す読み取り専用のイテレーター
    - [x] 配列にもコンテナにも使える
    - [x] 範囲 for の内部でも使われる

## 関連ページ

- [cpprefjp: std::cbegin](https://cpprefjp.github.io/reference/iterator/cbegin.html)
- [cppreference: std::cbegin](https://en.cppreference.com/w/cpp/iterator/cbegin)
