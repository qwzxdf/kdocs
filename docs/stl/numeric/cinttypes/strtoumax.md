---
title: std::strtoumax
summary: "文字列を `uintmax_t` に変換する。"
order: 900
tags:
  - 数値
---

# std::strtoumax

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cinttypes>`
</div>

`strtoull` の `uintmax_t` 版です。

!!! tip "ポイント"
    - `<cinttypes>` の関数。
    - `intmax_t` / `uintmax_t` を扱う。
    - 新しいコードでは `std::from_chars` が安全。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::strtoumax {#strtoumax}

```cpp
std::uintmax_t strtoumax(const char* str, char** str_end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 変換する文字列 |
| `str_end` | char** | 読み終えた位置を受け取る（不要なら `nullptr`） |
| `base` | int | 進数 |

- 戻り値: 変換した値
- 計算量: O(文字数)


## 実際に動かしてみる

```cpp
#include <cinttypes>
#include <print>

int main() {
  std::println("{}", std::strtoumax("42", nullptr, 10));
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 最大幅の整数の扱い |

## よくあるミス

??? failure "範囲外を確かめない"
    変換が範囲外だと `errno` が `ERANGE` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cstdint`](../cstdint.md) | 固定幅の整数型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を `uintmax_t` に変換する
    - [x] `<cinttypes>` の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strtoumax](https://cpprefjp.github.io/reference/cinttypes/strtoumax.html)
- [cppreference: std::strtoumax](https://en.cppreference.com/w/cpp/c/strtoumax)
