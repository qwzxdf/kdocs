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

「イベントの終了は 2026 年 11 月 30 日の 23 時」を `time_t` にして、いまの時刻と比べたい。あるいは、日付に 30 日を足して、「30 日後」を求めたい。`mktime` は、`tm` の年月日時分秒を `time_t` に戻す関数で、`gmtime` や `localtime` の逆の働きをします。

もう 1 つ、便利な働きがあります。範囲外の値を<strong>正規化</strong>してくれるのです。`tm_mday` に 32 を入れて渡すと、翌月 1 日になります。日付の足し算を、`tm` のフィールドに直接足してから `mktime` を通すだけで済みます。

!!! tip "ポイント"
    - 渡す `tm` はローカル時刻として解釈される。UTC の `tm` を戻すなら `timegm`（POSIX）/ `_mkgmtime`（MSVC）
    - 範囲外の値は正規化されて、引数の `tm` が書き換わる。`tm_wday` と `tm_yday` も計算される
    - `tm_isdst` は `-1`（自動判定）にして渡す
    - 変換できないときは `-1` を返す

!!! info "このページを読む前に"
    [`std::tm`](tm.md) と [`std::localtime`](localtime.md) を先に読んでください。

## 関数の詳しい説明

### std::mktime {#mktime}

```cpp
std::time_t mktime(std::tm* time);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time` | `std::tm*` | 変換する日時。正規化されて書き換わる |

引数の `tm` からは、`tm_year`、`tm_mon`、`tm_mday`、`tm_hour`、`tm_min`、`tm_sec`、`tm_isdst` が読まれます。`tm_wday` と `tm_yday` は無視され、`mktime` が計算した値で上書きされます。

引数が非 `const` なのは、書き換わるからです。たとえば `tm_mday` が 32 なら、月が 1 つ進んで 1 日になり、`tm_mon` と `tm_mday` が正しい値になります。`tm_hour` が 25 なら、翌日の 1 時です。この性質で、「30 日後」は、`t.tm_mday += 30;` のあとで `mktime(&t)` を呼ぶだけで求まります。

`tm_isdst` は、夏時間を使う地域では重要です。`-1` を渡すと、`mktime` が自動で判定します。0 や 1 を渡すと、その指定で計算されて、夏時間の境目で 1 時間ずれることがあります。

変換できないほど範囲外のときは、`(time_t)(-1)` を返します。1969 年 12 月 31 日 23 時 59 分 59 秒もこの値と同じ `-1` なので、`-1` が返ったとき、失敗か正しい値かを区別するには、`tm_wday` が `-1` に書き換わっていないかを見ます。

`mktime` は常にローカル時刻として解釈します。UTC の `tm` を戻したい場合は、POSIX の `timegm` か、MSVC の `_mkgmtime` を使います。標準には、UTC 版がありません。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::tm t{};
  t.tm_year = 126;  // 2026 年
  t.tm_mon = 0;     // 1 月
  t.tm_mday = 32;   // 1 月 32 日 → 2 月 1 日に正規化される
  t.tm_isdst = -1;  // 夏時間は自動判定
  std::mktime(&t);

  std::println("{} 年 {} 月 {} 日", t.tm_year + 1900, t.tm_mon + 1, t.tm_mday);
  std::println("曜日 {} (0 が日曜)", t.tm_wday);
}
```

```text title="実行結果"
2026 年 2 月 1 日
曜日 0 (0 が日曜)
```

`tm_mday = 32` が 2 月 1 日になり、`tm_wday` も計算されました。2026 年 2 月 1 日は日曜日です。

## ゲームでの使いどころ

「今日から 7 日後の 4 時」のような日付の計算に使います。

```cpp
std::tm t = *std::localtime(&now);
t.tm_mday += 7;     // 7 日進める
t.tm_hour = 4;
t.tm_min = 0;
t.tm_sec = 0;
t.tm_isdst = -1;
const std::time_t deadline = std::mktime(&t);
```

秒を足して日数を出す方法（`now + 7 * 86400`）と違い、夏時間の切り替えをまたいでも、ちょうど 7 日後の同じ時刻になります。

## よくあるミス

??? failure "tm_isdst を設定しない"
    初期化しないと、ゴミの値が夏時間の指定になり、1 時間ずれます。`t.tm_isdst = -1;` を忘れずに書きます。

??? failure "UTC の tm を mktime に渡す"
    ローカル時刻として解釈されるので、時差の分だけずれます。UTC なら `timegm` / `_mkgmtime` を使います。

??? failure "返り値の -1 を、失敗と決めつける"
    1969 年 12 月 31 日 23 時 59 分 59 秒（UTC）も `-1` です。通常のゲームでは起きませんが、昔の日付を扱うときは、気をつけます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`localtime`](localtime.md) | 逆向きの変換。`time_t` から `tm` へ |
| [`gmtime`](gmtime.md) | UTC に分解する |
| [`std::chrono::sys_days`](../../utilities/chrono/sys_days.md) | C++20 の日付。足し算が型で安全にできる |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mktime` は、`tm`（ローカル時刻）を `time_t` に戻す
    - [x] 範囲外の値を正規化する。日付の足し算に使える
    - [x] `tm_isdst` は `-1`。UTC には使えない

## 関連ページ

- [cpprefjp: std::mktime](https://cpprefjp.github.io/reference/ctime/mktime.html)
- [cppreference: std::mktime](https://en.cppreference.com/w/cpp/chrono/c/mktime)
