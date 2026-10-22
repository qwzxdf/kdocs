---
title: std::ctime
summary: "time_t を、ローカル時刻の決まった形の文字列にする。"
order: 900
tags:
  - 入出力・文字列
---

# std::ctime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`localtime` して `asctime` するのを 1 回で済ませる関数です。`Mon Jan  1 09:00:00 2024\n` のような形になります。タイムゾーンによって結果が変わります。

!!! tip "ポイント"
    - `asctime(localtime(t))` と同じ。
    - 戻り値は静的な領域（スレッドセーフでない）。
    - 新しいコードは `std::chrono` と `std::format`。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::ctime {#ctime}

```cpp
char* ctime(const std::time_t* timer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `timer` | const time_t* | 文字列にする時刻 |

- 戻り値: 文字列へのポインタ（静的な領域）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::time_t t = 0;
  std::print("{}", std::ctime(&t));  // タイムゾーンにより結果が変わる
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 手軽なログの日時 | `std::ctime(&t)` |

## よくあるミス

??? failure "結果が環境で変わる"
    ローカル時刻なので、同じ `time_t` でも環境のタイムゾーンで文字列が変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`asctime`](asctime.md) | tm から |
| [`strftime`](strftime.md) | 形式を指定できる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] time_t を文字列にする
    - [x] ローカル時刻
    - [x] 末尾に改行

## 関連ページ

- [cpprefjp: std::ctime](https://cpprefjp.github.io/reference/ctime/ctime.html)
- [cppreference: std::ctime](https://en.cppreference.com/w/cpp/chrono/c/ctime)
