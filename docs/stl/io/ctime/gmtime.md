---
title: std::gmtime
summary: "秒数を、UTC の年月日時分秒に分解する（C 由来）。"
order: 4
group: 時刻（<ctime>）
tags:
  - 入出力・文字列
---

# std::gmtime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ctime>`
</div>

`std::gmtime` は、**`time_t`（秒数）を UTC の年・月・日・時・分・秒に分解した `tm` 構造体にする**C 由来の関数です。`localtime` は現地時間、`gmtime` は世界標準時です。**返るポインターは内部の共有領域**なので、スレッドセーフではなく、すぐコピーして使います。

!!! tip "ポイント"
    - `tm_year` は 1900 年からの年数、`tm_mon` は 0〜11。
    - 戻り値のポインターは次の呼び出しで上書きされる。
    - スレッドセーフな `gmtime_r`（POSIX）/ `gmtime_s`（MSVC）もある。

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::gmtime {#gmtime}

```cpp
std::tm* gmtime(const std::time_t* time);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time` | `const time_t*` | 分解する時刻 |

- 戻り値: `tm` へのポインター（共有領域）
- 計算量: O(1)

```cpp
#include <ctime>
#include <print>

int main() {
  std::time_t t = 0;   // 1970-01-01 00:00:00 UTC
  std::tm* g = std::gmtime(&t);
  std::println("{}", g->tm_year + 1900);
}
```

```text title="実行結果"
1970
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `year_month_day` や `zoned_time` に置き換える |

## よくあるミス

??? failure "結果のポインターを保存する"
    次の `gmtime` / `localtime` の呼び出しで上書きされます。構造体ごとコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time`](time.md) | 現在の秒数 |
| [`std::chrono::zoned_time`](../../utilities/chrono/zoned_time.md) | C++20 のタイムゾーンつき日時 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 秒数 → UTC の日時
    - [x] ポインターは共有領域
    - [x] 現地時間は localtime

## 関連ページ

- [cpprefjp: std::gmtime](https://cpprefjp.github.io/reference/ctime/gmtime.html)
- [cppreference: std::gmtime](https://en.cppreference.com/w/cpp/chrono/c/gmtime)
