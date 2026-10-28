---
title: std::begin
summary: "先頭と終端のイテレータを返す（配列にも使える）。"
order: 9
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::begin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

範囲 for を使わず、イテレーターでループを書くとき、`v.begin()` と書くのは配列には使えません。配列も、コンテナも、同じ書き方で扱えるのが、非メンバー関数の `std::begin` です。<strong>先頭を指すイテレーター</strong>を返します。

!!! tip "ポイント"
    - `std::begin(c)` は 先頭を指すイテレーター
    - コンテナにはメンバー関数 `c.begin()` を、配列にはポインターを返す
    - 汎用のテンプレートで、配列とコンテナを同じように扱える
    - 範囲 for の内部で使われている

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::begin {#begin}

<span class="ver ver-11">C++11</span>

```cpp
template <class C>
auto begin(C& c) -> decltype(c.begin());
template <class T, std::size_t N>
T* begin(T (&array)[N]) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナまたは配列 | 対象 |

`std::begin(c)` は、コンテナなら `c.begin()` を呼んだ結果を、配列なら配列の先頭のポインターを返します。

汎用のテンプレートで、配列とコンテナの両方を受け取る関数を書くときに使います。範囲 for は、内部でこの規則を使っています。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};
  int a[3] = {1, 2, 3};          // 配列にも使える
  std::println("begin(v) の先頭要素 : {}", *std::begin(v));
  std::println("配列の要素数 : {}", std::end(a) - std::begin(a));
}
```

```text title="実行結果"
begin(v) の先頭要素 : 10
配列の要素数 : 3
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
    - [x] `std::begin(c)` は先頭を指すイテレーター
    - [x] 配列にもコンテナにも使える
    - [x] 範囲 for の内部でも使われる

## 関連ページ

- [cpprefjp: std::begin / std::end](https://cpprefjp.github.io/reference/iterator/begin.html)
- [cppreference: std::begin / std::end](https://en.cppreference.com/w/cpp/iterator/begin)
