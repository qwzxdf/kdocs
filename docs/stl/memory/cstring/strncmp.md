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

文字列の先頭の何文字かだけが一致するかを調べたい。`"load:level1"` が `"load:"` で始まるかのような判定です。`std::strncmp(a, b, n)` は、最大 `n` 文字までを比べます。

!!! tip "ポイント"
    - 先頭の最大 `n` 文字だけを比べる
    - 戻り値の規則は `strcmp` と同じ
    - 前方一致の判定に使える（`strncmp(s, prefix, strlen(prefix)) == 0`）
    - `n` 文字より前に終端があれば、そこで比べるのをやめる

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strncmp {#strncmp}

```cpp
int strncmp(const char* lhs, const char* rhs, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs`, `rhs` | `const char*` | 比べる文字列 |
| `count` | `std::size_t` | 比べる最大の文字数 |

`count` が 0 なら、何も比べず 0（等しい）を返します。

前方一致の判定では、`prefix` の長さを `count` に渡します。C++20 以降の `std::string_view::starts_with` のほうが、読みやすい書き方です。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* cmd = "load:level1";
  const char* prefix = "load:";
  std::println("load: で始まる: {}", std::strncmp(cmd, prefix, std::strlen(prefix)) == 0);
  std::println("save: で始まる: {}", std::strncmp(cmd, "save:", 5) == 0);
  std::println("先頭 3 文字: {}", std::strncmp("abcX", "abcY", 3) == 0);
}
```

```text title="実行結果"
load: で始まる: true
save: で始まる: false
先頭 3 文字: true
```

## ゲームでの使いどころ

コマンド文字列の先頭を見て、処理を分けるときに使います。

## よくあるミス

??? failure "count を比べる側の長さにしない"
    `prefix` より長い `count` を渡すと、終端も比べるので、意図と違う結果になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcmp`](strcmp.md) | 全体を比べる |
| `std::string_view::starts_with` | C++20 の前方一致 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strncmp](https://cpprefjp.github.io/reference/cstring/strncmp.html)
- [cppreference: strncmp](https://en.cppreference.com/w/cpp/string/byte/strncmp)
