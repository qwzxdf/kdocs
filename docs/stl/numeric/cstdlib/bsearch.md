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

並べ替え済みの配列から、目的の要素を高速に見つける二分探索。C 言語由来の `std::bsearch` は、`qsort` と同じ形式で比較関数を受け取ります。

!!! tip "ポイント"
    - 配列は、`compare` の順に並べ替え済みであること
    - 見つかれば要素へのポインタ、なければ `nullptr`
    - O(log n)
    - 新しいコードでは `std::lower_bound` か `std::binary_search`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bsearch {#bsearch}

```cpp
void* bsearch(const void* key, const void* base, std::size_t num,
              std::size_t size, int (*compare)(const void*, const void*));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const void*` | 探す値へのポインタ |
| `base` | `const void*` | 配列の先頭 |
| `num` | `size_t` | 要素の数 |
| `size` | `size_t` | 1 要素のバイト数 |
| `compare` | 関数ポインタ | `key` と要素の比較。`qsort` と同じ規則 |

並べ替え済みの配列に対して、二分探索で `key` と等しい要素を探します。見つかった要素へのポインタを返し、なければ `nullptr` を返します。複数が一致する場合、どれが返るかは決まっていません。

配列が `compare` の順序で並んでいないと、結果は不定です。`qsort` と同じ比較関数を使うのが基本です。

C++ では、`std::lower_bound` や `std::binary_search` のほうが型の安全が保たれ、位置も取れるので、好まれます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int Compare(const void* a, const void* b) {
  const int x = *static_cast<const int*>(a);
  const int y = *static_cast<const int*>(b);
  return (x > y) - (x < y);
}

int main() {
  const int sorted[] = {1, 2, 5, 9};
  int key = 5;
  const void* found = std::bsearch(&key, sorted, 4, sizeof(int), Compare);
  std::println("5 は見つかった: {}", found != nullptr);

  key = 3;
  found = std::bsearch(&key, sorted, 4, sizeof(int), Compare);
  std::println("3 は見つかった: {}", found != nullptr);
}
```

```text title="実行結果"
5 は見つかった: true
3 は見つかった: false
```

## ゲームでの使いどころ

C のライブラリとの境界で見かけます。自分のコードでは、`std::binary_search` や `std::lower_bound` を使います。

## よくあるミス

??? failure "並べ替えていない配列で探して、結果が不定"
    先に `qsort` か `std::sort` で並べ替えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::binary_search`](../../algorithms/binary_search.md) | 型安全な二分探索 |
| [`qsort`](qsort.md) | 並べ替え |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bsearch` は並べ替え済みの配列の二分探索
    - [x] 見つからなければ `nullptr`
    - [x] 新しいコードでは `std::binary_search` か `lower_bound`

## 関連ページ

- [cpprefjp: std::bsearch](https://cpprefjp.github.io/reference/cstdlib/bsearch.html)
- [cppreference: std::bsearch](https://en.cppreference.com/w/cpp/numeric/math/bsearch)
