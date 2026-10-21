---
title: strncmp
summary: "C 文字列の先頭 n 文字だけを比べる。"
order: 7
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strncmp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strncmp` は、[`strcmp`](strcmp.md) の「先頭 n 文字だけ比べる」版です。接頭辞（プレフィックス）が一致するかを調べるときに使います。

!!! tip "ポイント"
    - `strncmp(s, "cmd_", 4) == 0` で「cmd_ で始まるか」。
    - C++20 以降は `std::string_view::starts_with`。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strncmp {#strncmp}

```cpp
int strncmp(const char* lhs, const char* rhs, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const char*` | 比べる C 文字列 |
| `count` | `std::size_t` | 先頭から最大でこの文字数だけ比べる |

- 戻り値: `strcmp` と同じ
- 「先頭が `"enemy_"` で始まるか」の判定に使えます（`std::string_view::starts_with` のほうが簡単です）

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{} {}", std::strncmp("cmd_load", "cmd_save", 4) == 0, std::strncmp("cmd_load", "cmd_save", 8) != 0);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コマンド名の先頭を判定する | `strncmp(line, "load ", 5)` |

## よくあるミス

??? failure "n を文字数と合わせ間違える"
    `"cmd_"` は 4 文字です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcmp`](strcmp.md) | 全体を比べる |
| [`std::ranges::starts_with`](../../algorithms/starts_with.md) | C++23 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭 n 文字を比べる
    - [x] 接頭辞の判定に
    - [x] C++ では starts_with

## 関連ページ

- [cpprefjp: strncmp](https://cpprefjp.github.io/reference/cstring/strncmp.html)
- [cppreference: strncmp](https://en.cppreference.com/w/cpp/string/byte/strncmp)
