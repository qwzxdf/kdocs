---
title: memmove
summary: "メモリのバイト列を、別の場所へコピーする（重なっていてもよい）。"
order: 3
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memmove

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`memcpy` は、コピー元とコピー先が重なっていると結果が保証されません。配列の中身を 1 つずらすような、重なるコピーに使えるのが `std::memmove(dst, src, n)` です。重なりを正しく扱います。

!!! tip "ポイント"
    - 重なっていてもよい。結果は、いったん別の場所に退避してからコピーしたのと同じ
    - `memcpy` より少し遅いことがある
    - 配列の要素を詰める、挿入するための空きを作る、といった用途
    - 戻り値は `dst`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::memmove {#memmove}

```cpp
void* memmove(void* dest, const void* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | コピー先 |
| `src` | `const void*` | コピー元 |
| `count` | `std::size_t` | コピーするバイト数 |

コピーの向き（前から、後ろから）を、重なり方に応じて選びます。

`std::vector::insert` や `erase` が、内部で要素をずらすときと同じ考え方です。自分の型には、トリビアルにコピーできるときだけ使います。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  // 1 つ後ろにずらして、先頭に空きを作る
  int a[5] = {1, 2, 3, 4, 0};
  std::memmove(a + 1, a, 4 * sizeof(int));
  a[0] = 9;
  std::println("{} {} {} {} {}", a[0], a[1], a[2], a[3], a[4]);
}
```

```text title="実行結果"
9 1 2 3 4
```

## ゲームでの使いどころ

配列の途中に要素を挿入するための空きを作るときに使います。

## よくあるミス

??? failure "重なるのに memcpy を使う"
    結果が保証されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memcpy`](memcpy.md) | 重なると未定義 |
| `std::copy_backward` | 型に合わせた後ろからのコピー |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: memmove](https://cpprefjp.github.io/reference/cstring/memmove.html)
- [cppreference: memmove](https://en.cppreference.com/w/cpp/string/byte/memmove)
