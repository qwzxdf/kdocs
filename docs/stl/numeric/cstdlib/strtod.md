---
title: std::strtod
summary: "文字列を double に変換する（読み終えた位置が分かる）。"
order: 900
tags:
  - 数値
---

# std::strtod

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`atof` と違い、読み終えた位置を返し、範囲外のときは `errno` に `ERANGE` を設定します。`"inf"` や `"nan"` も読めます。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::strtod {#strtod}

```cpp
double strtod(const char* str, char** str_end);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 変換する文字列 |
| `str_end` | char** | 読み終えた位置を受け取る（不要なら `nullptr`） |

- 戻り値: 変換した `double`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  char* end = nullptr;
  double v = std::strtod("2.25abc", &end);
  std::println("{} {}", v, end);
}
```

```text title="実行結果"
2.25 abc
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 数値の後ろの単位を取り出す |

## よくあるミス

??? failure "`end` が先頭のまま"
    読めなかったとき、`end` は元の位置のままです。`end == str` で検出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atof`](atof.md) | 簡易版 |
| [`std::from_chars`](../../io/from_chars.md) | 新しい書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を double に変換する（読み終えた位置が分かる）
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strtod](https://cpprefjp.github.io/reference/cstdlib/strtod.html)
- [cppreference: std::strtod](https://en.cppreference.com/w/cpp/c/strtod)
