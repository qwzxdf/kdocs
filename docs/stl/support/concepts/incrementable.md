---
title: std::incrementable
summary: "`++` で進められ、何度でも同じ範囲を走査できる型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::incrementable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`weakly_incrementable` は、1 回きりの通過も許しますが、`incrementable` は、<strong>同じ位置を何度でもたどれる</strong>（コピーを残して進めても、コピーは元の位置を指し続ける）ことを求めます。`==` で比べられ、`i++` が古い値のコピーを返します。

!!! tip "ポイント"
    - `weakly_incrementable` に加えて、`std::regular`（コピーと比較ができる）
    - `i++` の戻り値が `I`（進める前のコピー）
    - 整数、ポインター、`vector` のイテレータが満たす
    - 満たしても、複数回たどれる保証は、構文だけでは確かめられない。`istream_iterator` は構文上は満たす

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::incrementable {#incrementable}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept incrementable = std::regular<I> && std::weakly_incrementable<I> && requires(I i) {
  { i++ } -> std::same_as<I>;
};
```

満たすべき条件は、次のとおりです。

- `std::weakly_incrementable<I>` を満たす
- `std::regular<I>` を満たす（コピー・既定の構築・比較ができる）
- `i++` が `I` を返す

`forward_iterator` 以上のイテレータは、この `incrementable` を満たします。複数回たどれることが、前方イテレータの定義だからです。

コンセプトが調べられるのは、書き方（構文）です。「進めたあとも、コピーが元の位置を指し続ける」という意味の条件は、型の作者が守る約束で、コンパイラは確かめません。`std::istream_iterator<int>` は、コピーできて、`i++` が値を返す、という構文を満たすので `incrementable` ですが、ストリームを読み進めるため、意味の上では複数回たどれません。そのため、`forward_iterator` にはなりません（`iterator_concept` が入力イテレータ止まり）。

`std::ranges::iota_view<W, Bound>` の `W` は `weakly_incrementable` で足りますが、`iota_view` を前方範囲にするには、`W` が `incrementable` である必要があります。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <sstream>
#include <vector>

int main() {
  std::println("int: {}", std::incrementable<int>);
  std::println("vector のイテレータ: {}", std::incrementable<std::vector<int>::iterator>);
  std::println("istream_iterator: {}", std::incrementable<std::istream_iterator<int>>);
}
```

```text title="実行結果"
int: true
vector のイテレータ: true
istream_iterator: true
```

## ゲームでの使いどころ

自作の連番の型を、`iota_view` で前方範囲にしたいときに、満たす必要があります。

## よくあるミス

??? failure "`i++` が古い値を返さない"
    戻り値が `I` でないと、満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weakly_incrementable`](weakly_incrementable.md) | 弱い条件 |
| [`forward_iterator`](forward_iterator.md) | 複数回たどれるイテレータ |
| [`regular`](regular.md) | コピーと比較ができる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::incrementable](https://cpprefjp.github.io/reference/iterator/incrementable.html)
- [cppreference: std::incrementable](https://en.cppreference.com/w/cpp/iterator/incrementable)
