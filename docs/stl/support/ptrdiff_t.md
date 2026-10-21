---
title: std::ptrdiff_t
summary: "2 つのポインターの差を表す、符号つきの整数型。"
order: 22
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# std::ptrdiff_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstddef>`
</div>

`std::ptrdiff_t` は、**2 つのポインター（やイテレータ）の差を表す、符号つきの整数型**です。`size_t` の符号つき版にあたります。`std::ssize` や、`std::distance` の戻り値がこの型です。

!!! tip "ポイント"
    - `p2 - p1` の型。
    - 符号つきなので、負の値も正しく扱える。
    - 配列の添字を符号つきで扱いたいときに使える。

## 関数の詳しい説明

### std::ptrdiff_t {#ptrdiff_t}

```cpp
using ptrdiff_t = /* 符号つき整数 */;
```

- 戻り値: （型）
- 計算量: O(1)

```cpp
#include <cstddef>
#include <print>

int main() {
  int a[] = {0, 1, 2, 3, 4};
  std::ptrdiff_t d = &a[3] - &a[1];
  std::println("{}", d);
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| イテレータ間の距離 | `std::ptrdiff_t n = it2 - it1;` |

## よくあるミス

??? failure "size_t と混ぜて比べる"
    符号つきと符号なしの比較は警告になります。`std::cmp_less` で比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`size_t`](size_t.md) | 符号なし |
| [`std::cmp_less`](cmp_less.md) | 安全な比較 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ポインターの差の型
    - [x] 符号つき
    - [x] ssize / distance の戻り値

## 関連ページ

- [cpprefjp: std::ptrdiff_t](https://cpprefjp.github.io/reference/cstddef/ptrdiff_t.html)
- [cppreference: std::ptrdiff_t](https://en.cppreference.com/w/cpp/types/ptrdiff_t)
