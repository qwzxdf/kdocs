---
title: std::strtoll
summary: "文字列を long long に変換する（進数を指定でき、読み終えた位置が分かる）。"
order: 900
tags:
  - 数値
---

# std::strtoll

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`atoi` 系は失敗を知らせてくれません。`strtoll` は、進数（2〜36）を指定でき、読み終えた位置を返し、範囲外なら `errno` に `ERANGE` を設定します。16 進数の文字列を読むときなどにも使います。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::strtoll {#strtoll}

```cpp
long long strtoll(const char* str, char** str_end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 変換する文字列 |
| `str_end` | char** | 読み終えた位置を受け取る（不要なら `nullptr`） |
| `base` | int | 進数（2〜36、0 なら接頭辞で判断） |

- 戻り値: 変換した値
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", std::strtoll("ff", nullptr, 16));
}
```

```text title="実行結果"
255
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 16 進数の文字列を数値にする |

## よくあるミス

??? failure "`str_end` を確かめない"
    数字が 1 文字もないとき、`str_end` は `str` のままです。先頭から消費できたか確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atoi`](atoi.md) | 簡易版 |
| [`std::from_chars`](../../io/from_chars.md) | 例外も errno も使わない |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を long long に変換する（進数を指定でき、読み終えた位置が分かる）
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strtoll](https://cpprefjp.github.io/reference/cstdlib/strtoll.html)
- [cppreference: std::strtoll](https://en.cppreference.com/w/cpp/c/strtoll)
