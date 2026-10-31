---
title: std::stoul
summary: "文字列を unsigned long に変換する（失敗すると例外）。"
order: 900
tags:
  - コンテナ
---

# std::stoul

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stoul(str)` は、文字列を `unsigned long` に変換します。`stol` の符号なし版です。注意したいのは、負の数の文字列（`"-1"`）を渡しても、エラーにならず、巨大な値に巻き戻って返ることです。

!!! tip "ポイント"
    - `unsigned long` に変換する
    - `"-1"` は、エラーにならず巻き戻った大きな値になる
    - 変換できなければ `invalid_argument`、範囲外は `out_of_range`
    - Windows の `unsigned long` は 32 ビット

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stoul {#stoul}

<span class="ver ver-11">C++11</span>

```cpp
unsigned long stoul(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

`strtoul` の仕様に従うため、先頭の `-` は、符号なしの値として巻き戻ります。`"-1"` は `ULONG_MAX` になります。ユーザーの入力を符号なしとして読むときは、先に `-` で始まっていないかを確かめます。

引数の意味は `stol` と同じです。64 ビットが必要なら `stoull` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::println("{}", std::stoul("123"));
  std::println("16 進: {}", std::stoul("ff", nullptr, 16));

  // 負の数の文字列は、エラーにならず巻き戻る
  const unsigned long wrapped = std::stoul("-1");
  std::println("-1 は ULONG_MAX: {}", wrapped == static_cast<unsigned long>(-1));
}
```

```text title="実行結果"
123
16 進: 255
-1 は ULONG_MAX: true
```

## ゲームでの使いどころ

要素数や ID など、負にならない値を読むときに使います。

## よくあるミス

??? failure "負の数を渡して、エラーになると思う"
    巻き戻った巨大な値になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stol`](stol.md) | 符号つき |
| [`stoull`](stoull.md) | `unsigned long long` |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::stoul](https://cpprefjp.github.io/reference/string/stoul.html)
- [cppreference: std::stoul](https://en.cppreference.com/w/cpp/string/basic_string/stol)
