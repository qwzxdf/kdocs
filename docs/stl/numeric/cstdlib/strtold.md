---
title: std::strtold
summary: "文字列を long double に変換する（読み終えた位置が分かる）。"
order: 900
tags:
  - 数値
---

# std::strtold

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`strtod` の `long double` 版です。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::strtold {#strtold}

```cpp
long double strtold(const char* str, char** str_end);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 変換する文字列 |
| `str_end` | char** | 読み終えた位置を受け取る（不要なら `nullptr`） |

- 戻り値: 変換した `long double`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", std::strtold("0.5", nullptr));
}
```

```text title="実行結果"
0.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 高い精度の数値の読み取り |

## よくあるミス

??? failure "範囲外を確かめない"
    範囲外のとき `errno` が `ERANGE` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strtod`](strtod.md) | double 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を long double に変換する（読み終えた位置が分かる）
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strtold](https://cpprefjp.github.io/reference/cstdlib/strtold.html)
- [cppreference: std::strtold](https://en.cppreference.com/w/cpp/c/strtold)
