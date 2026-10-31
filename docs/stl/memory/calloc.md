---
title: calloc
summary: "0 で初期化して、メモリを確保する。"
order: 22
group: C の確保関数（<cstdlib>）
tags:
  - メモリ
---

# calloc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`malloc` は、確保した領域を初期化しません。0 で埋めた配列が欲しいときは、`std::calloc(n, size)` が便利です。`n` 個の要素（各 `size` バイト）の領域を確保し、全部を 0 で埋めます。

!!! tip "ポイント"
    - `n * size` バイトを確保して、全部 0 で埋める
    - かけ算のオーバーフローを検査してくれる（`malloc(n * size)` と違う）
    - 失敗すると `nullptr`
    - 解放は `free`。C++ では `new` と混ぜない

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::calloc {#calloc}

```cpp
void* calloc(std::size_t num, std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `num` | `std::size_t` | 要素の個数 |
| `size` | `std::size_t` | 1 要素のバイト数 |

0 で埋まるのは、全ビットが 0 の状態です。整数と、ほとんどの環境の浮動小数点数やポインターは、全ビット 0 で 0 や `nullptr` になりますが、C++ の規格はポインターの `nullptr` が全ビット 0 であることを保証しません。

`malloc(num * size)` は、かけ算が `size_t` を超えて巻き戻ると、小さな領域を返してしまい、バッファ オーバーランになります。`calloc` は、これを検査して `nullptr` を返します。

C++ のクラスのオブジェクトには、使えません。コンストラクターが呼ばれないので、使うと未定義動作です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  int* a = static_cast<int*>(std::calloc(4, sizeof(int)));
  if (a == nullptr) return 1;

  std::println("{} {} {} {}", a[0], a[1], a[2], a[3]);
  std::free(a);

  // 巨大な要求は、かけ算のオーバーフローで失敗する
  void* big = std::calloc(static_cast<std::size_t>(-1), 2);
  std::println("失敗: {}", big == nullptr);
}
```

```text title="実行結果"
0 0 0 0
失敗: true
```

## ゲームでの使いどころ

C のライブラリに渡す、ゼロクリア済みのバッファを確保するときに使います。C++ では `std::vector<int>(n)` で足ります。

## よくあるミス

??? failure "new で確保したものを free する"
    混ぜると壊れます。`calloc` には `free`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`malloc`](malloc.md) | 初期化しない |
| [`free`](free.md) | 解放 |
| [`realloc`](realloc.md) | 大きさを変える |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: calloc](https://cpprefjp.github.io/reference/cstdlib/calloc.html)
- [cppreference: calloc](https://en.cppreference.com/w/cpp/memory/c/calloc)
