---
title: std::mktime
summary: "tm（年月日時分秒）を time_t に変換する（ローカル時刻として）。"
order: 900
tags:
  - 入出力・文字列
---

# std::mktime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

年月日を自分で組み立てた日時を `time_t` に変換したいことがあります。`std::mktime` は、`tm` をローカル時刻として解釈し、`time_t` を返します。同時に、範囲外の値（1 月 32 日など）を正しい日時に**正規化**します。

!!! tip "ポイント"
    - `tm` の `tm_year` は 1900 からの差、`tm_mon` は 0〜11。
    - 引数の `tm` は書き換わる（正規化される）。
    - `tm_isdst` は -1 にすると、夏時間を自動判定する。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::mktime {#mktime}

```cpp
std::time_t mktime(std::tm* time);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time` | tm* | 変換する日時（正規化されて書き換わる） |

- 戻り値: `time_t`（変換できないと `-1`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::tm t{};
  t.tm_year = 124;  // 2024 年
  t.tm_mon = 0;     // 1 月
  t.tm_mday = 32;   // 1 月 32 日 → 2 月 1 日に正規化される
  t.tm_isdst = -1;
  std::mktime(&t);
  std::println("{} {}", t.tm_mon, t.tm_mday);
}
```

```text title="実行結果"
1 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 月日を足して日付を進める | `t.tm_mday += 30; std::mktime(&t);` |

## よくあるミス

??? failure "月を 1 から数える"
    `tm_mon` は 0 始まりです。`tm_year` も `年 - 1900` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`localtime`](localtime.md) | time_t を tm に |
| [`gmtime`](gmtime.md) | UTC の tm に |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tm を time_t に変換
    - [x] tm を正規化する
    - [x] tm_mon は 0 始まり

## 関連ページ

- [cpprefjp: std::mktime](https://cpprefjp.github.io/reference/ctime/mktime.html)
- [cppreference: std::mktime](https://en.cppreference.com/w/cpp/chrono/c/mktime)
