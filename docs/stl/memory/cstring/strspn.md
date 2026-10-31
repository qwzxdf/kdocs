---
title: std::strspn
summary: "先頭から、指定した文字だけが続く長さを返す。"
order: 900
tags:
  - メモリ
---

# std::strspn

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

文字列の先頭から、指定した文字の集まりだけが続く長さを知りたい。数字だけが続く部分の長さ、といった用途です。`std::strspn(s, accept)` は、`accept` に含まれる文字だけが連続する、先頭の長さを返します。

!!! tip "ポイント"
    - 先頭から、`accept` の文字だけが続く長さを返す
    - `accept` に含まれない文字に当たった所で止まる
    - 数字だけ、英数字だけの部分の切り出しに使える
    - 逆の働きは `strcspn`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strspn {#strspn}

```cpp
std::size_t strspn(const char* dest, const char* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `const char*` | 調べる文字列 |
| `src` | `const char*` | 許す文字の集まり |

戻り値は、先頭から数えた個数です。先頭の文字がすでに `src` になければ 0 です。

文字の集まりは、並び順に意味がありません。数字なら `"0123456789"` と書きます。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  const char* s = "123abc";
  std::println("先頭の数字の長さ: {}", std::strspn(s, "0123456789"));
  std::println("数字で始まらない: {}", std::strspn("abc123", "0123456789"));
  std::println("全部が許す文字: {}", std::strspn("aaa", "a"));
}
```

```text title="実行結果"
先頭の数字の長さ: 3
数字で始まらない: 0
全部が許す文字: 3
```

## ゲームでの使いどころ

簡易な字句解析で、数字や英字の連なりを切り出すときに使います。

## よくあるミス

??? failure "許す文字を含めすぎる"
    `accept` に余計な文字を入れると、長さが伸びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcspn`](strcspn.md) | 逆。指定した文字が現れるまでの長さ |
| [`strpbrk`](strpbrk.md) | 指定した文字のどれかが現れる位置 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: std::strspn](https://cpprefjp.github.io/reference/cstring/strspn.html)
- [cppreference: std::strspn](https://en.cppreference.com/w/cpp/string/byte/strspn)
