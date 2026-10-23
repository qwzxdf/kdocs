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

C 言語から使われている並べ替え関数です。`std::sort` が登場する前に書かれたコードや、C のライブラリとの境界で出会います。比較の関数を渡す形が古めかしく、型の安全性もありません。

!!! tip "ポイント"
    - 配列の先頭、要素数、要素の大きさ、比較関数を渡す
    - 比較関数は `int (*)(const void*, const void*)`。負・0・正を返す
    - 型が消えるので、`std::sort` より遅いことが多い
    - 新しいコードでは `std::sort` を使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::qsort {#qsort}

```cpp
void qsort(void* base, std::size_t num, std::size_t size,
           int (*compare)(const void*, const void*));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `base` | `void*` | 配列の先頭 |
| `num` | `size_t` | 要素の数 |
| `size` | `size_t` | 1 要素のバイト数 |
| `compare` | 関数ポインタ | 2 要素の比較。第 1 引数が小さければ負、等しければ 0、大きければ正 |

`base` から始まる `num` 個の要素（1 つが `size` バイト）を、`compare` の結果に従って昇順に並べます。並べ替えは安定ではありません（等しい要素の順序は保たれない）。

比較関数は `const void*` を受け取るので、中で正しい型にキャストして比べます。結果を整数の引き算（`a - b`）で返すと、`int` の範囲を超えて符号が逆になることがあります。`(a > b) - (a < b)` のように書くのが安全です。

関数ポインタを介した呼び出しになるため、`std::sort` のようにコンパイラが比較をインライン化できません。そのぶん遅くなります。また、C++ のオブジェクト（コンストラクターを持つ型）を `memcpy` 相当で動かすので、トリビアルにコピーできない型には使えません。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int Compare(const void* a, const void* b) {
  const int x = *static_cast<const int*>(a);
  const int y = *static_cast<const int*>(b);
  return (x > y) - (x < y);   // 引き算は桁あふれの恐れがある
}

int main() {
  int values[] = {5, 2, 9, 1};
  std::qsort(values, 4, sizeof(int), Compare);
  for (int v : values) std::print("{} ", v);
  std::println("");
}
```

```text title="実行結果"
1 2 5 9 
```

## ゲームでの使いどころ

C のライブラリが比較関数のコールバックを要求する場面で見かけます。自分で並べ替えるなら `std::sort` を使います。

```cpp
std::sort(std::begin(values), std::end(values));   // 型の安全と速さの両方で上
```

## よくあるミス

??? failure "比較関数を `a - b` で書いて、桁あふれで順序が壊れる"
    `(x > y) - (x < y)` と書きます。

??? failure "`std::string` のようなオブジェクトの配列に使う"
    `memcpy` で動かすため未定義動作です。`std::sort` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::sort`](../../algorithms/sort.md) | 型安全で速い |
| [`bsearch`](bsearch.md) | 並べ替えた配列の二分探索 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `qsort` は C の並べ替え。比較関数を渡す
    - [x] 型が消え、`std::sort` より遅い
    - [x] 新しいコードでは `std::sort`

## 関連ページ

- [cpprefjp: std::qsort](https://cpprefjp.github.io/reference/cstdlib/qsort.html)
- [cppreference: std::qsort](https://en.cppreference.com/w/cpp/numeric/math/qsort)
