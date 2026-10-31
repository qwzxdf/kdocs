---
title: memcpy
summary: "メモリのバイト列を、別の場所へコピーする（重なっていてはいけない）。"
order: 1
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memcpy

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

配列や構造体の中身を、別の領域に、まとめてコピーしたい。`std::memcpy(dst, src, n)` は、`src` から `dst` へ `n` バイトをコピーします。速いのですが、領域が重なっていると壊れます。

!!! tip "ポイント"
    - `n` バイトを、そのままコピーする
    - コピー元とコピー先が重なっていると未定義動作。重なるなら `memmove`
    - コピーできる型（トリビアルにコピー可能）だけに使う
    - 型の変換のコピーは `std::bit_cast`（C++20）

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::memcpy {#memcpy}

```cpp
void* memcpy(void* dest, const void* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | コピー先 |
| `src` | `const void*` | コピー元 |
| `count` | `std::size_t` | コピーするバイト数 |

戻り値は `dest` です。

`std::string` や `std::vector` のような、内部にポインタを持つ型を `memcpy` でコピーすると、同じポインタを 2 つのオブジェクトが持ち、二重に解放されます。`std::is_trivially_copyable_v<T>` が真の型だけに使います。

バイト数は `sizeof(T) * 個数` で求めます。個数だけを渡す間違いが多いです。

`float` のビット列を `uint32_t` として読みたい、といった型の変換は、`memcpy` で行うのが、従来の安全な方法でした。C++20 の `std::bit_cast` が、これをより明確に書けます。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

struct Vec2 {
  float x;
  float y;
};

int main() {
  const Vec2 a{1.5f, 2.5f};
  Vec2 b{};
  std::memcpy(&b, &a, sizeof(Vec2));
  std::println("{} {}", b.x, b.y);

  // 配列のコピー: バイト数は sizeof(要素) * 個数
  int src[3] = {1, 2, 3};
  int dst[3] = {};
  std::memcpy(dst, src, sizeof(src));
  std::println("{} {} {}", dst[0], dst[1], dst[2]);
}
```

```text title="実行結果"
1.5 2.5
1 2 3
```

## ゲームでの使いどころ

バイナリ データの読み書きや、頂点データをバッファにコピーするときに使います。

## よくあるミス

??? failure "バイト数を個数にする"
    `memcpy(dst, src, 3)` は 3 バイトです。

??? failure "領域が重なる"
    `memmove` を使います。

??? failure "std::string をコピーする"
    二重解放になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memmove`](memmove.md) | 重なっていてもよい |
| `std::copy` | 型に合わせたコピー。普段はこちら |
| `std::bit_cast` | 型の変換 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: memcpy](https://cpprefjp.github.io/reference/cstring/memcpy.html)
- [cppreference: memcpy](https://en.cppreference.com/w/cpp/string/byte/memcpy)
