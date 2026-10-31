---
title: std::strncat
summary: "文字列の末尾に、最大 n 文字を連結する。"
order: 900
tags:
  - メモリ
---

# std::strncat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

`strcat` に、追加する最大の文字数を付けたのが `std::strncat(dst, src, n)` です。`strncpy` と違い、<strong>必ず終端を付けます</strong>。ただし、`n` は追加する文字数の上限で、`dst` 全体の大きさではありません。

!!! tip "ポイント"
    - `src` から最大 `n` 文字を、`dst` の終端の後ろに追加する
    - 追加したあとに、必ず `'\0'` を付ける
    - `n` は `dst` の残りの大きさではない。計算は自分で行う
    - 残りは `sizeof(dst) - strlen(dst) - 1`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strncat {#strncat}

```cpp
char* strncat(char* dest, const char* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | つなげられる側 |
| `src` | `const char*` | つなげる文字列 |
| `count` | `std::size_t` | 追加する最大の文字数 |

`count` を、`dst` の残りの大きさに合わせて計算すれば、あふれません。ただし、終端のための 1 を引き忘れると、あふれます。

`strncpy` のように、短い文字列で残りを埋めることはしません。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char buf[8] = "ab";
  const std::size_t room = sizeof(buf) - std::strlen(buf) - 1;  // 残り（終端の分を除く）
  std::strncat(buf, "cdefghij", room);
  std::println("{}", buf);
}
```

```text title="実行結果"
abcdefg
```

## ゲームでの使いどころ

固定長のバッファに、あふれない範囲で追記するときに使います。

## よくあるミス

??? failure "count をバッファ全体の大きさにする"
    `dst` の既存の文字列の分が考慮されず、あふれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcat`](strcat.md) | 長さを制限しない |
| [`strncpy`](strncpy.md) | 終端が付かないことがある |
| `std::string` | 普段はこちら |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strncat](https://cpprefjp.github.io/reference/cstring/strncat.html)
- [cppreference: std::strncat](https://en.cppreference.com/w/cpp/string/byte/strncat)
