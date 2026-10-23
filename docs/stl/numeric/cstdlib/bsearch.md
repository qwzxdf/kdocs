---
title: std::bsearch
summary: "C 由来の二分探索（整列済みの配列から探す）。"
order: 9
group: <cstdlib> の関数
tags:
  - 数値
---

# std::bsearch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::bsearch` は、**整列済みの配列から、二分探索で要素を探す**C 由来の関数です。比較関数を渡します。見つかればそのポインター、無ければ `nullptr` を返します。新しいコードでは [`lower_bound`](../../algorithms/lower_bound.md) や [`binary_search`](../../algorithms/binary_search.md) を使います。

!!! tip "ポイント"
    - 配列は整列済みであること。
    - 見つからないと `nullptr`。
    - C++ の ranges 版のほうが、型安全で簡単。

!!! info "このページを読む前に"
    - [stl/index.md](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::bsearch {#bsearch}

```cpp
void* bsearch(const void* key, const void* base, std::size_t n, std::size_t size, int (*cmp)(const void*, const void*));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const void*` | 探す値 |
| `base` | `const void*` | 配列の先頭 |
| `n` | `size_t` | 要素数 |
| `size` | `size_t` | 1 要素のバイト数 |
| `cmp` | 関数 | 比較関数 |

- 戻り値: 見つかった要素へのポインター（無ければ `nullptr`）
- 計算量: O(n)

```cpp
#include <cstdlib>
#include <print>

int main() {
  int a[] = {1, 3, 5};
  int key = 3;
  auto cmp = [](const void* x, const void* y) {
    int l = *static_cast<const int*>(x);
    int r = *static_cast<const int*>(y);
    return (l > r) - (l < r);
  };
  auto* p = static_cast<int*>(std::bsearch(&key, a, 3, sizeof(int), cmp));
  std::println("{}", p - a);
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `std::ranges::lower_bound` に置き換える |

## よくあるミス

??? failure "整列していない配列に使う"
    結果は不定です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::binary_search`](../../algorithms/binary_search.md) | 新しい書き方 |
| [`qsort`](qsort.md) | 並べ替え |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 由来の二分探索
    - [x] 整列済みが前提
    - [x] 新しいコードは lower_bound

## 関連ページ

- [cpprefjp: std::bsearch](https://cpprefjp.github.io/reference/cstdlib/bsearch.html)
- [cppreference: std::bsearch](https://en.cppreference.com/w/cpp/numeric/math/bsearch)
