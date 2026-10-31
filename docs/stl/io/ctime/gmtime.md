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

`time(nullptr)` が返す 1767225600 のような秒数は、人間には読めません。年月日に直すのが `gmtime` です。名前の gm は Greenwich Mean（グリニッジ標準時）で、結果は<strong>協定世界時（UTC）</strong>の日時になります。タイムゾーンの影響を受けないので、サーバーとクライアントで同じ結果になり、ログやデータ交換の時刻に向いています。

画面に出すときの、利用者のローカル時刻は `localtime` が担当します。

!!! tip "ポイント"
    - 結果は UTC。タイムゾーンや夏時間の影響を受けない
    - 戻り値は静的な領域を指す。次に `gmtime` か `localtime` を呼ぶと上書きされる
    - スレッドから使うなら、MSVC の `gmtime_s`、POSIX の `gmtime_r`
    - 失敗すると `nullptr`。範囲外の `time_t` を渡したときなど

!!! info "このページを読む前に"
    [`std::time`](time.md) と [`std::tm`](tm.md) を先に読んでください。

## 関数の詳しい説明

### std::gmtime {#gmtime}

```cpp
std::tm* gmtime(const std::time_t* timer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `timer` | `const std::time_t*` | 変換する時刻。ポインタで渡す |

引数がポインタなのは C 由来の書き方で、`&now` のように変数のアドレスを渡します。値を直接渡す形ではないので、`gmtime(std::time(nullptr))` とは書けません。

戻り値は、変換した結果の `tm` へのポインタです。このポインタは、ライブラリ内部の静的な領域を指しています。次に `gmtime` や `localtime` を呼ぶと、中身が上書きされます。結果を残したいときは、自分の変数にコピーします。

```cpp
std::tm utc = *std::gmtime(&now);   // 静的領域から、自分の変数へコピー
```

変換できない値を渡すと、`nullptr` を返します。そのまま `*` で参照するとクラッシュするので、時刻が外から来る値のときは、検査します。

静的な領域を使うので、複数のスレッドから同時に呼ぶとデータ競合になります。MSVC では `gmtime_s(&tm, &t)` が、POSIX では `gmtime_r(&t, &tm)` が、呼び出し側が用意した `tm` に書き込む安全な版です。引数の順番が環境で逆なので、注意します。

C++20 の `std::chrono` なら、静的な領域も、ポインタも要りません。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  // 2026 年 1 月 1 日 0 時 0 分 0 秒（UTC）
  const std::time_t t = 1767225600;
  const std::tm utc = *std::gmtime(&t);  // コピーして持つ

  std::println("{}-{:02}-{:02} {:02}:{:02}:{:02}",
               utc.tm_year + 1900, utc.tm_mon + 1, utc.tm_mday,
               utc.tm_hour, utc.tm_min, utc.tm_sec);
  std::println("曜日 {} (0 が日曜)", utc.tm_wday);
  std::println("1 月 1 日から {} 日目", utc.tm_yday);
}
```

```text title="実行結果"
2026-01-01 00:00:00
曜日 4 (0 が日曜)
1 月 1 日から 0 日目
```

`tm_year` に 1900、`tm_mon` に 1 を足して、人間向けの表示にしています。2026 年 1 月 1 日は木曜日です。

## ゲームでの使いどころ

サーバーに送る時刻や、ログに書く時刻は UTC にそろえておくと、遊ぶ人のタイムゾーンによる食い違いが起きません。表示するときだけ `localtime` に変えます。

毎日 0 時にリセットするイベントのように、「どこの 0 時か」が問題になる場面では、UTC の `gmtime` で判定して、サーバーとクライアントを同じ基準にします。

## よくあるミス

??? failure "戻り値のポインタを保存しておく"
    `std::tm* p = std::gmtime(&a); std::tm* q = std::gmtime(&b);` の `p` と `q` は同じ領域を指します。`p` の中身が `b` の結果に変わっています。`*std::gmtime(&a)` で、コピーして持ちます。

??? failure "複数スレッドから呼ぶ"
    静的な領域を共有するので、結果が混ざります。`gmtime_s` / `gmtime_r` を使うか、`chrono` に移ります。

??? failure "ローカル時刻のつもりで gmtime を使う"
    日本の時刻（UTC+9）を出したいのに、9 時間ずれた値が出ます。ローカル時刻には `localtime` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`localtime`](localtime.md) | ローカル時刻に分解する |
| [`mktime`](mktime.md) | `tm` を `time_t` に戻す（ローカル時刻として） |
| [`std::chrono::sys_days`](../../utilities/chrono/sys_days.md) | C++20 の日付。UTC を前提にした型 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `gmtime(&t)` は、UTC の年月日時分秒に分解する
    - [x] 戻り値は静的な領域を指す。自分の変数にコピーする
    - [x] スレッドからは `gmtime_s` / `gmtime_r`

## 関連ページ

- [cpprefjp: std::gmtime](https://cpprefjp.github.io/reference/ctime/gmtime.html)
- [cppreference: std::gmtime](https://en.cppreference.com/w/cpp/chrono/c/gmtime)
