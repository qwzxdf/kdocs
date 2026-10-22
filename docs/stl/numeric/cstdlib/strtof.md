---
title: std::strtof
summary: "文字列を float に変換する（読み終えた位置が分かる）。"
order: 900
tags:
  - 数値
---

# std::strtof

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`atof` と違い、読み終えた位置を返し、範囲外のときは `errno` に `ERANGE` を設定します。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::strtof {#strtof}

```cpp
float strtof(const char* str, char** str_end);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 変換する文字列 |
| `str_end` | char** | 読み終えた位置を受け取る（不要なら `nullptr`） |

- 戻り値: 変換した `float`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", std::strtof("1.5", nullptr));
}
```

```text title="実行結果"
1.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 設定ファイルの数値の読み取り |

## よくあるミス

??? failure "読み終えた位置を確かめない"
    不正な文字列では 0 が返り、位置が進みません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atof`](atof.md) | 簡易版 |
| [`strtod`](strtod.md) | double 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を float に変換する（読み終えた位置が分かる）
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strtof](https://cpprefjp.github.io/reference/cstdlib/strtof.html)
- [cppreference: std::strtof](https://en.cppreference.com/w/cpp/c/strtof)
