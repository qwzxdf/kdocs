---
title: strcmp
summary: "C 文字列どうしを比べる。"
order: 6
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strcmp

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

2 つの C 文字列が同じか、どちらが先に並ぶかを調べたい。`==` で比べると、文字列の中身ではなく、アドレスの比較になります。`std::strcmp(a, b)` は、先頭から 1 文字ずつ比べ、結果を整数で返します。

!!! tip "ポイント"
    - 戻り値は、`a` が小さければ負、等しければ 0、大きければ正
    - 戻り値の大きさには意味がない。`< 0`、`== 0`、`> 0` と比べる
    - `unsigned char` として比べる。UTF-8 のバイト順になる
    - 一致の判定は `strcmp(a, b) == 0`

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strcmp {#strcmp}

```cpp
int strcmp(const char* lhs, const char* rhs);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lhs` | `const char*` | 比べる 1 つ目 |
| `rhs` | `const char*` | 比べる 2 つ目 |

先頭から比べ、違う文字が見つかった所で結果が決まります。片方が先に終端に達したら、短いほうが小さいとされます。

戻り値を `-1`、`1` と比べてはいけません。`-32` や `98` を返す実装があります。

言語ごとの辞書順で比べたいときは `strcoll` です。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("同じ: {}", std::strcmp("abc", "abc") == 0);
  std::println("abc < abd: {}", std::strcmp("abc", "abd") < 0);
  std::println("b > a: {}", std::strcmp("b", "a") > 0);
  std::println("短いほうが小さい: {}", std::strcmp("ab", "abc") < 0);
}
```

```text title="実行結果"
同じ: true
abc < abd: true
b > a: true
短いほうが小さい: true
```

## ゲームでの使いどころ

C の API から受け取った文字列が、特定の名前かを調べるときに使います。自分のコードでは `std::string` の `==` です。

## よくあるミス

??? failure "== で比べる"
    アドレスの比較です。中身を比べるには `strcmp` です。

??? failure "戻り値を -1 と比べる"
    符号だけを見ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strncmp`](strncmp.md) | 先頭の n 文字だけ比べる |
| [`strcoll`](strcoll.md) | ロケールの辞書順で比べる |
| `std::string::operator==` | 普段はこちら |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strcmp](https://cpprefjp.github.io/reference/cstring/strcmp.html)
- [cppreference: strcmp](https://en.cppreference.com/w/cpp/string/byte/strcmp)
