---
title: std::sentinel_for
summary: "あるイテレータの終端として使える型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::sentinel_for

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

範囲の終わりは、必ずしも、始まりと同じ型のイテレータとは限りません。C 文字列の終端（`\0`）や、無限の範囲の終端を、イテレータと比べる専用の型（番兵、sentinel）で表せます。`std::sentinel_for<S, I>` は、型 `S` が、イテレータ `I` の終わりを表す番兵として使えるかを調べます。

!!! tip "ポイント"
    - `S` を `I` と `==` で比べられる
    - `S` が `std::semiregular`（コピー、既定の構築ができる）
    - `I` が `input_or_output_iterator`
    - `vector` の `end()` は `iterator` と同じ型なので、そのまま満たす

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::sentinel_for {#sentinel_for}

<span class="ver ver-20">C++20</span>

```cpp
template <class S, class I>
concept sentinel_for = std::semiregular<S> && std::input_or_output_iterator<I>
                    && /* S と I が == で比べられる */;
```

満たすべき条件は、次のとおりです。

- `std::semiregular<S>`
- `std::input_or_output_iterator<I>`
- `S` と `I` が `==` と `!=` で比べられる

`std::default_sentinel_t`、`std::unreachable_sentinel_t`、`std::ranges::sentinel_t` などが、番兵の例です。

C++20 の範囲ライブラリ（`std::ranges::sort(r)` など）は、`begin()` と `end()` の型が違ってもよいように設計されています。そのため、アルゴリズムは「イテレータと番兵の組」を引数に取ります。

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
  // 同じ型の end()
  std::println("vector: {}",
               std::sentinel_for<std::vector<int>::iterator, std::vector<int>::iterator>);

  // 終わりのない番兵
  std::println("unreachable_sentinel: {}",
               std::sentinel_for<std::unreachable_sentinel_t, int*>);

  // istream_iterator の終端は同じ型のデフォルト構築
  std::println("istream_iterator: {}",
               std::sentinel_for<std::istream_iterator<int>, std::istream_iterator<int>>);

  std::println("int と int*: {}", std::sentinel_for<int, int*>);
}
```

```text title="実行結果"
vector: true
unreachable_sentinel: true
istream_iterator: true
int と int*: false
```

## ゲームでの使いどころ

終端が型で特別な範囲（無限の `iota`、C 文字列）を、アルゴリズムに渡せるようにします。

## よくあるミス

??? failure "begin と end が同じ型だと決めつける"
    C++20 では、違ってもよい設計です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sized_sentinel_for`](sized_sentinel_for.md) | 距離も求められる |
| [`input_or_output_iterator`](input_or_output_iterator.md) | イテレータ側の条件 |
| [`default_sentinel`](../iterator/default_sentinel.md) | 標準の番兵 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::sentinel_for](https://cpprefjp.github.io/reference/iterator/sentinel_for.html)
- [cppreference: std::sentinel_for](https://en.cppreference.com/w/cpp/iterator/sentinel_for)
