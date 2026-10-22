---
title: std::asctime
summary: "tm を、決まった形の文字列にする。"
order: 900
tags:
  - 入出力・文字列
---

# std::asctime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`tm` を `Mon Jan  1 00:00:00 2024` のような英語の決まった形にしたいときに使います。末尾に改行が付きます。形式が固定で、自由に変えられないので、新しいコードでは `strftime` や `std::format` のほうが便利です。

!!! tip "ポイント"
    - 形式は `曜日 月 日 時:分:秒 年\n`。
    - 戻り値は静的な領域を指す（スレッドセーフでない）。
    - 日本語や別の形式は `strftime`。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::asctime {#asctime}

```cpp
char* asctime(const std::tm* time_ptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time_ptr` | const tm* | 文字列にする日時 |

- 戻り値: 文字列へのポインタ（静的な領域）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::tm t{};
  t.tm_year = 124;
  t.tm_mon = 0;
  t.tm_mday = 1;
  t.tm_wday = 1;  // 月曜
  std::print("{}", std::asctime(&t));
}
```

```text title="実行結果"
Mon Jan  1 00:00:00 2024
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| デバッグログの日時 | `std::asctime(&tm)` |

## よくあるミス

??? failure "形式を変えたい"
    `asctime` の形式は変えられません。`std::strftime` や `std::format` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strftime`](strftime.md) | 形式を指定できる |
| [`ctime`](ctime.md) | time_t から直接 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tm を固定形式の文字列に
    - [x] 末尾に改行
    - [x] 形式を変えるなら strftime

## 関連ページ

- [cpprefjp: std::asctime](https://cpprefjp.github.io/reference/ctime/asctime.html)
- [cppreference: std::asctime](https://en.cppreference.com/w/cpp/chrono/c/asctime)
