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

プレイヤーの画面に「最後に遊んだのは 2026/10/31 18:00」と表示したい。UTC の時刻をそのまま出すと、日本のプレイヤーには 9 時間ずれて見えます。`localtime` は、`time_t` を、OS に設定されているタイムゾーンの年月日時分秒に分解します。夏時間のある地域では、その調整も含まれます。

UTC のままで分解する場合は [`gmtime`](gmtime.md) です。その点以外は、使い方も落とし穴も同じです。

!!! tip "ポイント"
    - 結果は、OS のタイムゾーンによるローカル時刻。環境で結果が変わる
    - 戻り値は静的な領域を指す。次の呼び出しで上書きされるので、コピーして持つ
    - スレッドからは、MSVC の `localtime_s`、POSIX の `localtime_r`
    - 保存やサーバーとの通信は UTC。`localtime` は表示のときだけ

!!! info "このページを読む前に"
    [`std::time`](time.md) と [`std::gmtime`](gmtime.md) を先に読んでください。

## 関数の詳しい説明

### std::localtime {#localtime}

```cpp
std::tm* localtime(const std::time_t* timer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `timer` | `const std::time_t*` | 変換する時刻。ポインタで渡す |

戻り値は `tm` へのポインタで、失敗すると `nullptr` です。`gmtime` と同じく、ライブラリ内部の静的な領域を指します。さらに、`gmtime` と `localtime` は、同じ領域を共有している環境が多く、片方を呼ぶともう片方の結果が壊れます。

```cpp
const std::tm local = *std::localtime(&t);   // すぐコピーする
```

返される日時は、`TZ` 環境変数や OS の設定によるタイムゾーンで決まります。日本なら UTC+9 で、夏時間はありません。そのため、サーバー（UTC のことが多い）で実行した結果と、手元の PC で実行した結果は、違います。テストで時刻の文字列を比べるときは、ローカルタイムを避けます。

夏時間のある地域では、`tm_isdst` が正になります。夏時間の切り替えの前後で、`tm_hour` が飛んだり、同じ値が 2 回現れたりします。

C++20 の `std::chrono::zoned_time` は、タイムゾーンを明示して変換でき、静的な領域も使いません。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::time_t t = 1767225600;  // 2026-01-01 00:00:00 UTC

  const std::tm utc = *std::gmtime(&t);
  const std::tm local = *std::localtime(&t);

  // UTC とローカルの時差（時間）。環境で変わるので、範囲だけ確かめる
  const int diff_hours = (local.tm_hour - utc.tm_hour + 24) % 24;
  std::println("時差は 0〜23 時間: {}", diff_hours >= 0 && diff_hours < 24);
  std::println("UTC の年は 2026: {}", utc.tm_year + 1900 == 2026);
}
```

```text title="実行結果"
時差は 0〜23 時間: true
UTC の年は 2026: true
```

`local.tm_hour` は、実行する環境のタイムゾーンで変わります。日本の環境なら 9 になり、UTC の環境なら 0 になります。結果が環境で変わるコードは、自動のテストに向きません。

## ゲームでの使いどころ

セーブ データの一覧の「最終更新」や、ログ画面の時刻の表示に使います。保存する値は `time_t`（UTC）のままにして、表示のときだけ `localtime` を通します。

```cpp
char text[32];
const std::tm local = *std::localtime(&saved);
std::strftime(text, sizeof(text), "%Y/%m/%d %H:%M", &local);
```

## よくあるミス

??? failure "戻り値のポインタを保存しておく"
    次の `localtime` や `gmtime` の呼び出しで、中身が変わります。必ず `*` でコピーします。

??? failure "ローカル時刻を保存しておく"
    保存した人と読み込む人でタイムゾーンが違うと、ずれます。保存は UTC（`time_t`）で行い、表示のときに変換します。

??? failure "複数スレッドから呼ぶ"
    静的な領域を共有するので、データ競合になります。`localtime_s`（MSVC）/ `localtime_r`（POSIX）か、`chrono` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gmtime`](gmtime.md) | UTC に分解する |
| [`mktime`](mktime.md) | ローカル時刻の `tm` を `time_t` に戻す |
| [`std::chrono::zoned_time`](../../utilities/chrono/zoned_time.md) | C++20 のタイムゾーンつきの時刻 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。MSVC は、`localtime` を使うと警告（C4996）を出すことがあります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `localtime(&t)` は、OS のタイムゾーンで年月日時分秒に分解する
    - [x] 戻り値は静的な領域を指す。コピーして持つ
    - [x] 保存は UTC で、`localtime` は表示のときだけ

## 関連ページ

- [cpprefjp: std::localtime](https://cpprefjp.github.io/reference/ctime/localtime.html)
- [cppreference: std::localtime](https://en.cppreference.com/w/cpp/chrono/c/localtime)
