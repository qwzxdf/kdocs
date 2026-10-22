---
title: std::strtoimax
summary: "文字列を `intmax_t` に変換する。"
order: 900
tags:
  - 数値
---

# std::strtoimax

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cinttypes>`
</div>

`strtoll` の `intmax_t` 版です。進数を指定でき、読み終えた位置も受け取れます。

!!! tip "ポイント"
    - `<cinttypes>` の関数。
    - `intmax_t` / `uintmax_t` を扱う。
    - 新しいコードでは `std::from_chars` が安全。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::strtoimax {#strtoimax}

```cpp
std::intmax_t strtoimax(const char* str, char** str_end, int base);
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
  std::println("{}", std::strtoimax("-42", nullptr, 10));
}
```

```text title="実行結果"
-42
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
    - [x] 文字列を `intmax_t` に変換する
    - [x] `<cinttypes>` の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strtoimax](https://cpprefjp.github.io/reference/cinttypes/strtoimax.html)
- [cppreference: std::strtoimax](https://en.cppreference.com/w/cpp/c/strtoimax)
