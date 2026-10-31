---
title: strcat
summary: "C 文字列の後ろに、別の C 文字列をつなげる（危険）。"
order: 13
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strcat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

文字列の後ろに別の文字列をつなげたい。`std::strcat(dst, src)` は、`dst` の終端の位置から `src` を書き込みます。`strcpy` と同じく、大きさを確かめないので、あふれる危険があります。

!!! tip "ポイント"
    - `dst` の終端を探して、そこから `src` をコピーする
    - `dst` に十分な空きが必要。`strlen(dst) + strlen(src) + 1` 要素
    - `dst` の長さを毎回数えるので、連続して呼ぶと遅い
    - 新しいコードは `std::string` の `+=`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strcat {#strcat}

```cpp
char* strcat(char* dest, const char* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | つなげられる側。終端のある文字列で、空きが十分にあること |
| `src` | `const char*` | つなげる文字列 |

戻り値は `dest` です。

`dest` の長さを先頭から数えるため、何度も `strcat` を重ねると、毎回その長さぶんの時間がかかり、全体で長さの 2 乗に近い時間になります。連結が多いなら、`std::string` の `+=`（内部で長さを持つ）が速くなります。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char buf[32] = "Hello";
  std::strcat(buf, ", ");
  std::strcat(buf, "world");
  std::println("{}", buf);
  std::println("長さ: {}", std::strlen(buf));
}
```

```text title="実行結果"
Hello, world
長さ: 12
```

## ゲームでの使いどころ

古いコードで見かけます。新しく書くなら `std::string` か `std::format` です。

## よくあるミス

??? failure "空きが足りない"
    `buf` が小さいと、領域の外を壊します。

??? failure "dst が未初期化"
    終端がないと、ゴミの位置から書き込みます。`char buf[32] = "";` で初期化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strncat`](strncat.md) | 追加する最大の文字数を指定する |
| `std::string::operator+=` | 普段はこちら |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strcat](https://cpprefjp.github.io/reference/cstring/strcat.html)
- [cppreference: strcat](https://en.cppreference.com/w/cpp/string/byte/strcat)
