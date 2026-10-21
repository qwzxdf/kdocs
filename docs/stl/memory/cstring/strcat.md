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

`strcat` は、**C 文字列の後ろに別の C 文字列をつなげる**関数ですが、`strcpy` と同じく**バッファの大きさを確認しません**。新しいコードでは使いません。

!!! tip "ポイント"
    - `std::string` の `+=` で足りる。
    - 先頭から終端を探すので、繰り返すと遅い。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strcat {#strcat}

```cpp
char* strcat(char* dest, const char* src);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `char*` | つなげる先（すでに C 文字列が入っている。十分な大きさが必要） |
| `src` | `const char*` | 後ろにつなげる C 文字列 |

- 戻り値: `dest`
- `strcpy` と同じで、**大きさのチェックがありません**。つなげるたびに先頭から終端を探すので、繰り返すと O(n²) です。`std::string` の `+=` を使います

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char dst[16] = "foo";
  std::strcat(dst, "bar");
  std::println("{}", dst);
}
```

```text title="実行結果"
foobar
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解用 | `std::string` の `+=` に置き換える |

## よくあるミス

??? failure "バッファがあふれる"
    範囲外に書き込みます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::string::operator+=` | 安全で速い |
| [`snprintf`](snprintf.md) | 書式つきで組み立てる |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 使わない
    - [x] 大きさを確認しない
    - [x] `std::string` を使う

## 関連ページ

- [cpprefjp: strcat](https://cpprefjp.github.io/reference/cstring/strcat.html)
- [cppreference: strcat](https://en.cppreference.com/w/cpp/string/byte/strcat)
