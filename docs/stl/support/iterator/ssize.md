---
title: std::ssize
summary: "要素数を符号つきの整数で返す。"
order: 6
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::ssize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`std::ssize(c)` は、**要素数を符号つきの整数（`ptrdiff_t`）で返す**関数です。`size()` は符号なしなので、`i < v.size() - 1` で 0 個のときに巨大な値になる事故が起きます。符号つきで扱いたいときに使います。

!!! tip "ポイント"
    - `for (ptrdiff_t i = 0; i < std::ssize(v); ++i)` が安全に書ける。
    - C++20 の機能。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::ssize {#ssize}

<span class="ver ver-20">C++20</span>

```cpp
template <class C>
constexpr auto ssize(const C& c);  // 符号付き
```

- 符号付き（`std::ptrdiff_t`）の要素数。`int` と比べたり、後ろから回したりするときに警告が出ません

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  for (auto i = std::ssize(v) - 1; i >= 0; --i) {  // 符号付きなので -1 で止まる
    std::print("{} ", v[i]);
  }
  std::println("/ 最後 {}", *std::prev(v.end()));
}
```

```text title="実行結果"
3 2 1 / 最後 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 符号つきのループ | `for (int i = 0; i < std::ssize(v); ++i)` |

## よくあるミス

??? failure "size() - 1 の落とし穴"
    空の `vector` で `v.size() - 1` は巨大な値になります。`ssize` を使うと −1 になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`size`](size.md) | 符号なし |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号つきの要素数
    - [x] `size() - 1` の事故を防ぐ
    - [x] C++20

## 関連ページ

- [cpprefjp: std::ssize](https://cpprefjp.github.io/reference/iterator/ssize.html)
- [cppreference: std::ssize](https://en.cppreference.com/w/cpp/iterator/ssize)
