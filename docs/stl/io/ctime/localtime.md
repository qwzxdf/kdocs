---
title: std::localtime
summary: "time_t を、ローカル時刻の tm に変換する。"
order: 900
tags:
  - 入出力・文字列
---

# std::localtime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`time_t`（秒数）を、年月日時分秒に分けたいときに使います。`std::localtime` はローカル時刻（OS のタイムゾーン）で、UTC なら [`gmtime`](gmtime.md) です。

!!! tip "ポイント"
    - 戻り値は**静的な領域**を指すので、次に呼ぶと上書きされる。
    - スレッドをまたぐなら `localtime_s`（Windows）/ `localtime_r`（POSIX）。
    - 新しいコードでは `std::chrono` のほうが安全。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::localtime {#localtime}

```cpp
std::tm* localtime(const std::time_t* timer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `timer` | const time_t* | 変換する時刻 |

- 戻り値: `tm` へのポインタ（失敗すると `nullptr`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::time_t t = 86400LL * 365 * 30;  // 1999 年の終わりごろ
  std::tm* local = std::localtime(&t);
  std::println("{}", local->tm_year);
}
```

```text title="実行結果"
99
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブの日付を表示 | `std::localtime(&t)` |

## よくあるミス

??? failure "戻り値を保存する"
    戻り値のポインタは、次の呼び出しで上書きされます。必要なら `tm` を値でコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gmtime`](gmtime.md) | UTC の版 |
| [`mktime`](mktime.md) | 逆の変換 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] time_t をローカル時刻の tm に
    - [x] 戻りは静的領域
    - [x] スレッドでは _s / _r 版

## 関連ページ

- [cpprefjp: std::localtime](https://cpprefjp.github.io/reference/ctime/localtime.html)
- [cppreference: std::localtime](https://en.cppreference.com/w/cpp/chrono/c/localtime)
