---
title: std::ignore
summary: "tie や構造化束縛的な代入で、「この値は使わない」と書くための印。"
order: 58
tags:
  - ユーティリティ
---

# std::ignore

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`std::ignore` は、**`std::tie` の中で「この要素は受け取らない」ことを表す印**です。pair や tuple の一部だけが欲しいときに、不要な要素の置き場として使います。何を代入しても捨てられます。

!!! tip "ポイント"
    - `std::tie(x, std::ignore) = pair;` で、2 つ目を捨てる。
    - `[[maybe_unused]]` の代わりに、関数の戻り値を捨てる印としても使われる（`std::ignore = f();`）。
    - 構造化束縛では、名前を付けない書き方は無いので、`_` などの変数にする。

## 関数の詳しい説明

### std::ignore {#ignore}

```cpp
inline constexpr /*unspecified*/ ignore;
```

- 戻り値: （変数。代入された値を捨てる）
- 計算量: O(1)

```cpp
#include <print>
#include <tuple>
#include <utility>

int main() {
  int x = 0;
  // 2 つ目は要らない
  std::tie(x, std::ignore) = std::make_pair(10, 20);
  std::println("{}", x);
}
```

```text title="実行結果"
10
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| pair の片方だけ欲しいとき | `std::tie(pos, std::ignore) = GetPosAndVel();` |

## よくあるミス

??? failure "構造化束縛で使おうとする"
    `auto [a, std::ignore] = p;` は書けません。`std::ignore` は `std::tie` の代入先専用です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tie`](tie.md) | 変数の参照をまとめる |
| `[[maybe_unused]]` | 使わない変数に付ける属性 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `tie` の中で「受け取らない」印
    - [x] 何を代入しても捨てられる
    - [x] 構造化束縛では使えない

## 関連ページ

- [cpprefjp: std::ignore](https://cpprefjp.github.io/reference/tuple/ignore.html)
- [cppreference: std::ignore](https://en.cppreference.com/w/cpp/utility/tuple/ignore)
