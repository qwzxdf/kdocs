---
title: std::nullptr_t
summary: "`nullptr` の型。"
order: 20
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# std::nullptr_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstddef>`
</div>

`std::nullptr_t` は、**`nullptr` の型**です。「どのポインターでもない、空のポインター」を表す専用の型で、関数のオーバーロードで「`nullptr` が渡された場合」だけを区別するときに使います。普段は意識しません。

!!! tip "ポイント"
    - `nullptr` は `0` や `NULL` と違い、整数にならない。
    - `nullptr_t` の引数を取ると、`nullptr` だけを受け付ける。
    - どのポインター型にも変換できる。

## 関数の詳しい説明

### std::nullptr_t {#nullptr_t}

```cpp
using nullptr_t = decltype(nullptr);
```

- 戻り値: （型）
- 計算量: O(1)

```cpp
#include <cstddef>
#include <print>

void Draw(int*) { std::println("ポインター版"); }
void Draw(std::nullptr_t) { std::println("nullptr 版"); }

int main() {
  Draw(nullptr);
}
```

```text title="実行結果"
nullptr 版
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| nullptr を明示的に受ける関数 | `void Set(std::nullptr_t)` |

## よくあるミス

??? failure "NULL や 0 を使う"
    整数と区別できずに、意図しないオーバーロードが選ばれます。`nullptr` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::unique_ptr`](../utilities/unique_ptr.md) | `nullptr` と比べられる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] nullptr の型
    - [x] 整数にならない
    - [x] 普段は意識しない

## 関連ページ

- [cpprefjp: std::nullptr_t](https://cpprefjp.github.io/reference/cstddef/nullptr_t.html)
- [cppreference: std::nullptr_t](https://en.cppreference.com/w/cpp/types/nullptr_t)
