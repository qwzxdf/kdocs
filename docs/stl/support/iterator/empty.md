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

`std::empty(c)` は、**コンテナが空かを調べる**関数です。`c.empty()` と同じですが、**配列や `initializer_list` にも使える**のが利点です。

!!! tip "ポイント"
    - テンプレートで、コンテナも配列も同じ書き方で扱える。
    - 普段は `c.empty()` で足りる。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::empty {#empty}

```cpp
template <class C>
constexpr auto empty(const C& c) -> decltype(c.empty());
```

- 空か。C の配列は常に false

```cpp
#include <iterator>
#include <print>

int main() {
  int a[] = {4, 5, 6};
  int sum = 0;
  for (auto it = std::begin(a); it != std::end(a); ++it) {
    sum += *it;
  }
  std::println("{} {} {}", sum, *std::data(a), std::empty(a));
}
```

```text title="実行結果"
15 4 false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで、何でも空か調べる | `std::empty(c)` |

## よくあるミス

??? failure "size() == 0 と書く"
    `empty()` のほうが速いコンテナがあります（`list` など）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`size`](size.md) | 要素数 |
| [`data`](data.md) | 先頭のポインター |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空かを調べる
    - [x] 配列にも使える
    - [x] 普段は c.empty()

## 関連ページ

- [cpprefjp: std::empty](https://cpprefjp.github.io/reference/iterator/empty.html)
- [cppreference: std::empty](https://en.cppreference.com/w/cpp/iterator/empty)
