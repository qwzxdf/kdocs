---
title: malloc
summary: "C 由来のメモリ確保（初期化しない）。"
order: 20
group: C の確保関数（<cstdlib>）
tags:
  - メモリ
---

# malloc

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstdlib>`
</div>

`malloc` は、**指定したバイト数のメモリを確保して、先頭のポインターを返す**C 由来の関数です。中身は**初期化されません**。C のライブラリが「`free` で解放してね」と要求するときに使います。C++ では `new` や `std::vector`、`std::make_unique` を使うのが基本です。

!!! tip "ポイント"
    - 確保したら、必ず `free` で解放する。
    - 失敗すると `nullptr`。
    - C++ のオブジェクトの確保には使わない（コンストラクターが呼ばれない）。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### malloc {#malloc}

```cpp
void* malloc(std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `size` | `std::size_t` | 確保する**バイト数**（要素の数ではない） |

- 戻り値: 確保した領域の先頭。失敗したら `nullptr`。**中身は不定**（0 とは限らない）
- 計算量: ヒープ管理の実装による（普通は `new` と同程度）
- 返る領域は、どの基本型にも使える**アラインメント**（`alignof(std::max_align_t)`、普通は 16 バイト）にそろっています
- `size` が 0 のときは、`nullptr` か、使えないポインタが返ります（実装による）。`free` はできますが、使わないでください
- **C++ では `void*` を自動で他の型に変換できない**ので、`static_cast<int*>(malloc(...))` のようにキャストが必要です

```cpp
int* a = static_cast<int*>(std::malloc(10 * sizeof(int)));  // int を 10 個ぶん
if (a == nullptr) {
  return;  // 失敗（メモリ不足）。必ず確認する
}
a[0] = 5;
std::free(a);
```

!!! warning "sizeof の間違い"
    `std::malloc(sizeof(a))` の `a` がポインタだと、ポインタ自身の大きさ（8 バイト）しか確保されません。`sizeof(int) * 10` か、`sizeof(*a) * 10` と書きます。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  int* p = static_cast<int*>(std::malloc(3 * sizeof(int)));
  p[0] = 1;
  p[1] = 2;
  p[2] = 3;
  std::println("{}", p[0] + p[1] + p[2]);
  std::free(p);
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリに渡すバッファの確保 | `void* p = malloc(size);` |

## よくあるミス

??? failure "戻り値を調べない"
    失敗すると `nullptr` で、書き込むとクラッシュします。

??? failure "new で作ったものを free する"
    `new` には `delete`、`malloc` には `free`。混ぜると未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`free`](free.md) | 解放する |
| [`calloc`](calloc.md) | 0 で初期化する |
| [`std::make_unique`](../utilities/make_unique.md) | C++ の確保 |

## コンパイラ対応

C 由来の関数です。`aligned_alloc` は C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト数のメモリを確保
    - [x] `free` で解放
    - [x] C++ では new / vector

## 関連ページ

- [cpprefjp: malloc](https://cpprefjp.github.io/reference/cstdlib/malloc.html)
- [cppreference: malloc](https://en.cppreference.com/w/cpp/memory/c/malloc)
