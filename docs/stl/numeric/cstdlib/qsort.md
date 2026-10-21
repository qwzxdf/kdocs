---
title: std::qsort
summary: "C 由来の並べ替え（比較関数を渡す）。"
order: 8
group: <cstdlib> の関数
tags:
  - 数値
---

# std::qsort

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

`std::qsort` は、**配列を並べ替える**C 由来の関数です。比較関数（`void*` を受け取る）を渡します。型安全でなく、C++ の `std::sort` より遅いので、C のライブラリが「`qsort` 形式の比較関数」を要求する場面以外では使いません。

!!! tip "ポイント"
    - 比較関数は、負・0・正を返す。
    - `std::sort` のほうが速く、型安全。
    - `bsearch` と組み合わせて使う古い形。

## 関数の詳しい説明

### std::qsort {#qsort}

```cpp
void qsort(void* base, std::size_t n, std::size_t size, int (*cmp)(const void*, const void*));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `base` | `void*` | 配列の先頭 |
| `n` | `size_t` | 要素数 |
| `size` | `size_t` | 1 要素のバイト数 |
| `cmp` | 関数 | 比較関数 |

- 戻り値: なし
- 計算量: O(n)

```cpp
#include <cstdlib>
#include <print>

int main() {
  int a[] = {3, 1, 2};
  std::qsort(a, 3, sizeof(int), [](const void* x, const void* y) {
    return *static_cast<const int*>(x) - *static_cast<const int*>(y);
  });
  std::println("{} {} {}", a[0], a[1], a[2]);
}
```

```text title="実行結果"
1 2 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `std::ranges::sort` に置き換える |

## よくあるミス

??? failure "比較で引き算する"
    桁あふれで結果が壊れることがあります。`<` / `>` で比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sort`](../../algorithms/sort.md) | 型安全で速い |
| [`bsearch`](bsearch.md) | 二分探索 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 由来の並べ替え
    - [x] 型安全でない
    - [x] 新しいコードは std::sort

## 関連ページ

- [cpprefjp: std::qsort](https://cpprefjp.github.io/reference/cstdlib/qsort.html)
- [cppreference: std::qsort](https://en.cppreference.com/w/cpp/numeric/math/qsort)
