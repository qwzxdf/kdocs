---
title: std::stol
summary: "文字列を long に変換する（失敗すると例外）。"
order: 900
tags:
  - コンテナ
---

# std::stol

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`stol` は、`stoi` の仲間で、文字列を `long` に変換します。大きな整数や高い精度の小数が必要なときに使います。

!!! tip "ポイント"
    - 失敗したときは例外を投げる。
    - 第 2 引数で、読み終えた位置を受け取れる。
    - 例外を避けたいなら [`from_chars`](../io/from_chars.md)。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stol {#stol}

```cpp
long stol(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | string | 変換する文字列 |
| `pos` | size_t* | 省略可。読み終えた位置を受け取る |
| `base` | int | 省略可。進数（既定は 10） |

- 戻り値: 変換した long
- 計算量: O(文字数)


## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::println("{}", std::stol("-42"));
}
```

```text title="実行結果"
-42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイルの数値を読む | `std::stol("-42")` |

## よくあるミス

??? failure "例外を捕まえない"
    `std::invalid_argument`（数字でない）と `std::out_of_range`（範囲外）を投げます。外から入った文字列は `try` で囲むか、`from_chars` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stoi`](stoi.md) | int の版 |
| [`from_chars`](../io/from_chars.md) | 例外を投げない版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を long に変換
    - [x] 失敗は例外
    - [x] 例外が嫌なら from_chars

## 関連ページ

- [cpprefjp: std::stol](https://cpprefjp.github.io/reference/string/stol.html)
- [cppreference: std::stol](https://en.cppreference.com/w/cpp/string/basic_string/stol)
