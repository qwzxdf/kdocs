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

「2026 年 10 月 31 日の 18 時」のような、人間が読む形の日時を持つ構造体が `std::tm` です。1970 年からの秒数（`time_t`）は計算しやすい反面、年や月が読めません。`gmtime` と `localtime` が、秒数を `tm` に分解し、`mktime` と `strftime` が、`tm` を秒数や文字列に変換します。

使うときにいちばん間違えやすいのが、各フィールドの基準です。年は 1900 年からの差、月は 0 から始まります。

!!! tip "ポイント"
    - `tm_year` は 1900 年からの年数（2026 年なら 126）
    - `tm_mon` は 0〜11（10 月なら 9）。`tm_mday` だけは 1 から始まる
    - `tm_wday` は日曜が 0。`tm_yday` は 1 月 1 日が 0
    - `tm_isdst` は夏時間。`mktime` に渡すときは `-1`（自動判定）にする

!!! info "このページを読む前に"
    [`std::time`](time.md) と [`std::time_t`](time_t.md) を先に読んでください。

## 関数の詳しい説明

### std::tm {#tm}

```cpp
struct tm {
  int tm_sec;    // 秒 [0, 60]
  int tm_min;    // 分 [0, 59]
  int tm_hour;   // 時 [0, 23]
  int tm_mday;   // 日 [1, 31]
  int tm_mon;    // 月 [0, 11]
  int tm_year;   // 1900 からの年数
  int tm_wday;   // 曜日 [0, 6]（日曜 = 0）
  int tm_yday;   // 1 月 1 日からの日数 [0, 365]
  int tm_isdst;  // 夏時間（正: 有効、0: 無効、負: 不明）
};
```

### 各フィールドの意味 {#fields}

`tm_sec` は 0〜60 です。60 は、うるう秒のためにあります。普通の環境では、59 までしか出ません。

`tm_year` は、西暦から 1900 を引いた数です。2026 年は 126 になります。西暦にするには 1900 を足します。2000 年問題のとき、年を 2 桁で持っていた古い設計から、この形が残りました。

`tm_mon` は、1 月が 0、12 月が 11 です。人間向けの表示では、1 を足します。同じ構造体の中で、`tm_mday` だけが 1 から始まるので、うっかり揃えてしまう間違いが起きやすいところです。

`tm_wday` は、日曜が 0、土曜が 6 です。`gmtime`、`localtime`、`mktime` が計算して書き込むので、自分で設定する必要はありません。`tm_yday` も同じです。

`tm_isdst` は、夏時間が有効なら正、無効なら 0、不明なら負です。日本には夏時間がないので、どの値でも結果は変わりませんが、`mktime` に渡す前には、`-1` にして自動判定させるのが決まりです。

規格が決めているのはここまでです。環境によっては、`tm_gmtoff`（UTC との差）や `tm_zone` のような、独自のフィールドが追加されています。

### 初期化 {#init}

`std::tm t{};` と書いて、全部を 0 にしてから必要なフィールドだけを設定します。初期化しないまま `mktime` に渡すと、ゴミの値が日時になります。0 で初期化すると、`tm_mday` が 0 になり、「前の月の末日」と解釈されるので、日も必ず設定します。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::time_t t = 0;  // エポック
  const std::tm* p = std::gmtime(&t);
  std::println("年={} 月={} 日={}", p->tm_year, p->tm_mon, p->tm_mday);
  std::println("西暦 {} 年 {} 月 {} 日", p->tm_year + 1900, p->tm_mon + 1, p->tm_mday);
  std::println("曜日={} (0 が日曜)", p->tm_wday);
}
```

```text title="実行結果"
年=70 月=0 日=1
西暦 1970 年 1 月 1 日
曜日=4 (0 が日曜)
```

エポックの 1970 年 1 月 1 日は木曜日なので、`tm_wday` は 4 です。`tm_year` は 70、`tm_mon` は 0 で、そのまま表示すると人間向けの値と 1 ずつ、または 1900 ずれます。

## ゲームでの使いどころ

セーブデータの一覧に「2026/10/31 18:00」と表示するとき、`localtime` で分解した `tm` の各フィールドを組み立てます。書式つきの文字列にするなら、自分で 1900 を足すより、`strftime` に任せるほうが間違えません。

```cpp
std::tm local = *std::localtime(&saved);  // 静的領域から、自分の変数にコピー
std::println("{}/{:02}/{:02}", local.tm_year + 1900, local.tm_mon + 1, local.tm_mday);
```

## よくあるミス

??? failure "tm_year に西暦を入れる"
    `t.tm_year = 2026;` と書くと、3926 年になります。`2026 - 1900` を入れます。

??? failure "tm_mon を 1 始まりだと思う"
    10 月は 9 です。表示するときに 1 を足し、設定するときに 1 を引きます。

??? failure "初期化しないで mktime に渡す"
    `std::tm t;` のままだと、ゴミの値が入っています。`std::tm t{};` で 0 にしてから、年月日を設定します。`tm_mday` は 0 のままだと前の月の末日になるので、必ず設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::time_t`](time_t.md) | 秒数の形。計算しやすい |
| [`gmtime`](gmtime.md) | `time_t` を UTC の `tm` に分解する |
| [`localtime`](localtime.md) | `time_t` をローカル時刻の `tm` に分解する |
| [`mktime`](mktime.md) | `tm` を `time_t` に戻す |
| [`std::chrono::year_month_day`](../../utilities/chrono/year_month_day.md) | C++20 の日付。基準の違いで間違えにくい |

## コンパイラ対応

C 由来の構造体です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `tm` は、年月日時分秒を分けて持つ構造体
    - [x] `tm_year` は 1900 から、`tm_mon` は 0 から。`tm_mday` だけ 1 から
    - [x] `std::tm t{};` で初期化してから使う

## 関連ページ

- [cpprefjp: std::tm](https://cpprefjp.github.io/reference/ctime/tm.html)
- [cppreference: std::tm](https://en.cppreference.com/w/cpp/chrono/c/tm)
