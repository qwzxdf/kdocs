---
title: std::sprintf
summary: "書式を指定して、文字配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::sprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

文字列を組み立てたいとき、`sprintf` で配列に書式つきで書き込めます。ただし、配列の大きさを確かめないので、あふれる危険があります。`snprintf` を使うほうが安全です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::sprintf {#sprintf}

```cpp
int sprintf(char* buffer, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | char* | 書き込み先（十分な大きさが必要） |
| `format` | const char* | 書式文字列 |
| `...` | 可変引数 | 書式に対応する値 |

- 戻り値: 書き込んだ文字数（終端を除く）
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  char buf[16];
  std::sprintf(buf, "%03d", 7);
  std::println("{}", buf);
}
```

```text title="実行結果"
007
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （古い C のコードの保守） |

## よくあるミス

??? failure "バッファがあふれる"
    長さの確認がありません。`snprintf` か `std::format` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`snprintf`](snprintf.md) | 大きさを指定する |
| [`std::format`](../../utilities/format.md) | 型安全な書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式を指定して、文字配列に書き込む
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sprintf](https://cpprefjp.github.io/reference/cstdio/sprintf.html)
- [cppreference: std::sprintf](https://en.cppreference.com/w/cpp/io/c/sprintf)
