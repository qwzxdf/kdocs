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

`strcat` は連結する長さを指定できず、バッファをあふれさせる事故のもとです。`strncat` は連結する最大の文字数を指定でき、必ず終端の `'\0'` を付けてくれます。ただし n は「連結する文字数」で、バッファ全体の大きさではありません。

!!! tip "ポイント"
    - 終端の `'\0'` を前提にする C 由来の関数。
    - バッファの大きさは自分で確かめる。
    - 新しいコードでは `std::string` / `std::string_view` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strncat {#strncat}

```cpp
char* strncat(char* dest, const char* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | char* | 連結先（`\0` で終わっていること） |
| `src` | const char* | 連結する文字列 |
| `count` | size_t | 連結する最大の文字数 |

- 戻り値: `dest`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char buf[16] = "abc";
  std::strncat(buf, "defgh", 2);
  std::println("{}", buf);
}
```

```text title="実行結果"
abcde
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 固定長バッファへの安全な連結 |

## よくあるミス

??? failure "count をバッファ全体の大きさにする"
    `count` は連結する文字数です。`dest` の残りの大きさ（終端ぶんも含めて）以下にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strcat`](strcat.md) | 長さの指定なし |
| [`strncpy`](strncpy.md) | コピーする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列の末尾に、最大 n 文字を連結する
    - [x] 終端の `'\0'` を前提にする C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strncat](https://cpprefjp.github.io/reference/cstring/strncat.html)
- [cppreference: std::strncat](https://en.cppreference.com/w/cpp/string/byte/strncat)
