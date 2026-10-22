---
title: std::tm
summary: "年月日時分秒を分けて持つ構造体。"
order: 900
tags:
  - 入出力・文字列
---

# std::tm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`time_t` は秒数の 1 つの値です。年月日時分秒に分けて扱いたいときに使うのが `std::tm` で、`gmtime` / `localtime` が作り、`mktime` が `time_t` に戻します。

!!! tip "ポイント"
    - `tm_year` は 1900 からの経過年。
    - `tm_mon` は 0〜11（1 月が 0）。
    - `tm_wday` は日曜が 0、`tm_yday` は 1 月 1 日が 0。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::tm {#tm}

```cpp
struct tm {
  int tm_sec;    // 秒 [0, 60]
  int tm_min;    // 分 [0, 59]
  int tm_hour;   // 時 [0, 23]
  int tm_mday;   // 日 [1, 31]
  int tm_mon;    // 月 [0, 11]
  int tm_year;   // 1900 からの年
  int tm_wday;   // 曜日 [0, 6]（日曜 = 0）
  int tm_yday;   // 1 月 1 日からの日数 [0, 365]
  int tm_isdst;  // 夏時間（正: 有効、0: 無効、負: 不明）
};
```

- 戻り値: なし（構造体）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::time_t t = 0;
  std::tm* p = std::gmtime(&t);
  std::println("{} {} {}", p->tm_year, p->tm_mon, p->tm_mday);
}
```

```text title="実行結果"
70 0 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 日付の取り出し | `std::gmtime(&t)->tm_year + 1900` |

## よくあるミス

??? failure "月を 1 から数える"
    `tm_mon` は 0 始まり、`tm_year` は年 - 1900 です。足し忘れ・引き忘れでずれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gmtime`](gmtime.md) | UTC の tm に |
| [`mktime`](mktime.md) | time_t に戻す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 年月日時分秒の構造体
    - [x] 月は 0 始まり、年は -1900
    - [x] gmtime / mktime と組む

## 関連ページ

- [cpprefjp: std::tm](https://cpprefjp.github.io/reference/ctime/tm.html)
- [cppreference: std::tm](https://en.cppreference.com/w/cpp/chrono/c/tm)
