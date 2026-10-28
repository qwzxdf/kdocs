---
title: std::crbegin
summary: "const の逆順イテレータで、末尾の要素を指す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::crbegin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <iterator>`
</div>

範囲 for を使わず、イテレーターでループを書くとき、`v.crbegin()` と書くのは配列には使えません。配列も、コンテナも、同じ書き方で扱えるのが、非メンバー関数の `std::crbegin` です。<strong>逆順の先頭を指す読み取り専用のイテレーター</strong>を返します。

!!! tip "ポイント"
    - `std::crbegin(c)` は 逆順の先頭を指す読み取り専用のイテレーター
    - コンテナにはメンバー関数 `c.crbegin()` を、配列にはポインターを返す
    - 汎用のテンプレートで、配列とコンテナを同じように扱える
    - 範囲 for の内部で使われている

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::crbegin {#crbegin}

<span class="ver ver-11">C++11</span>

```cpp
template <class C>
auto crbegin(C& c) -> decltype(c.crbegin());
template <class T, std::size_t N>
T* crbegin(T (&array)[N]) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナまたは配列 | 対象 |

`std::crbegin(c)` は、コンテナなら `c.crbegin()` を呼んだ結果を、配列なら配列の先頭のポインターを返します。読み取り専用なので、要素を書き換えられません。逆順の走査に使います。

汎用のテンプレートで、配列とコンテナの両方を受け取る関数を書くときに使います。範囲 for は、内部でこの規則を使っています。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3};
  for (auto it = std::crbegin(v); it != std::crend(v); ++it) std::print("{} ", *it);
  std::println("");
}
```

```text title="実行結果"
3 2 1 
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

C++11 から使えます。`<iterator>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::crbegin(c)` は逆順の先頭を指す読み取り専用のイテレーター
    - [x] 配列にもコンテナにも使える
    - [x] 範囲 for の内部でも使われる

## 関連ページ

- [cpprefjp: std::crbegin](https://cpprefjp.github.io/reference/iterator/crbegin.html)
- [cppreference: std::crbegin](https://en.cppreference.com/w/cpp/iterator/crbegin)
