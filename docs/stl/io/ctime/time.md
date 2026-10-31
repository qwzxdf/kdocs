---
title: std::time
summary: "現在時刻を、1970 年からの秒数で取得する（C 由来）。"
order: 1
group: 時刻（<ctime>）
tags:
  - 入出力・文字列
---

# std::time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ctime>`
</div>

セーブデータに「最後に遊んだ時刻」を書きたい。ログのファイル名に日付を入れたい。そんなとき、いちばん手軽に「いま」を取れるのが `std::time(nullptr)` です。返ってくるのは、1970 年 1 月 1 日 0 時 0 分 0 秒（UTC）からの経過秒数で、これを UNIX 時間（エポック秒）と呼びます。

C から引き継いだ関数で、秒より細かい時間は取れません。人間が読める年月日に直すには、`gmtime` か `localtime` を通します。新しいコードで時刻を扱うなら、型が安全で精度も高い `std::chrono::system_clock` のほうが向いています。

!!! tip "ポイント"
    - 戻り値は `time_t`。1970 年 1 月 1 日 0 時（UTC）からの秒数
    - 秒の精度しかない。ミリ秒以下が要るなら `chrono`
    - 年月日にするには `gmtime`（UTC）か `localtime`（ローカル時刻）を通す
    - ゲームの経過時間の計測には使わない。時計が巻き戻りうるので、`steady_clock` を使う

!!! info "このページを読む前に"
    [`std::time_t`](time_t.md) と [`std::tm`](tm.md) を先に読むと、この関数の戻り値と、その分解先が分かります。

## 関数の詳しい説明

### std::time {#time}

```cpp
std::time_t time(std::time_t* t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | `std::time_t*` | 結果を書き込む先。`nullptr` を渡してもよい |

引数 `t` は、結果を戻り値とは別に書き込みたいときのためのもので、今は `nullptr` を渡す書き方がほとんどです。`nullptr` でなければ、戻り値と同じ値が `*t` にも入ります。`std::time(&now)` と書くのは古い書き方で、`now = std::time(nullptr)` と同じ意味です。

戻り値は現在時刻です。取得に失敗したときは `(time_t)(-1)` を返しますが、普通の環境で失敗することはまずありません。

この値は「いまの時計」の読み取りなので、ユーザーが OS の時刻を変えたり、ネットワークで時刻が補正されたりすると、巻き戻ることがあります。2 回の呼び出しの差を、経過時間として使ってはいけません。経過時間は `std::chrono::steady_clock` で測ります。

計算量は定数です。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::time_t now = std::time(nullptr);
  std::println("1970 年より後: {}", now > 0);

  // 秒数 → UTC の年月日
  const std::tm* utc = std::gmtime(&now);
  std::println("2020 年以降: {}", utc->tm_year + 1900 >= 2020);
}
```

```text title="実行結果"
1970 年より後: true
2020 年以降: true
```

`tm_year` は 1900 年からの年数なので、1900 を足して西暦にします。

## ゲームでの使いどころ

「前回のログインから何日たったか」のように、日をまたぐ判定には `time` が使えます。保存した `time_t` と、今の `time_t` の差を `difftime` で秒にして、86400 で割ります。ユーザーが時計を動かすと、ずるができる点は、ゲームの設計として許すかを決めておきます。

```cpp
const double elapsed = std::difftime(std::time(nullptr), saved);  // 秒
const int days = static_cast<int>(elapsed / 86400.0);
```

乱数の種に使うことも多いですが、1 秒以内に 2 回起動すると、同じ種になります。`std::random_device` のほうが適しています。

## よくあるミス

??? failure "乱数の種に使って、同じ結果が出る"
    `srand(time(nullptr))` は、1 秒単位の種です。複数のプロセスが同時に起動すると、同じ乱数列になります。`std::random_device` で種を作ります。

??? failure "time の差で、フレームの経過時間を測る"
    秒の精度なので、1 フレーム（16 ミリ秒）の長さは測れません。時計が巻き戻ることもあります。`steady_clock::now()` の差を使います。

??? failure "time_t を int に入れる"
    `time_t` は 64 ビットが普通です。`int` に入れると、2038 年問題の元になります。`time_t` のまま持ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::chrono::system_clock`](../../utilities/chrono/system_clock.md) | C++ の時計。ナノ秒まで取れ、型が安全 |
| [`std::chrono::steady_clock`](../../utilities/chrono/steady_clock.md) | 巻き戻らない時計。経過時間の計測用 |
| [`gmtime`](gmtime.md) | 秒数を UTC の年月日に分解する |
| [`localtime`](localtime.md) | 秒数をローカル時刻の年月日に分解する |
| [`timespec_get`](timespec_get.md) | 秒とナノ秒で現在時刻を取る（C++17） |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `time(nullptr)` は、1970 年からの経過秒数を返す
    - [x] 秒の精度で、巻き戻りうる。経過時間の計測には使わない
    - [x] 年月日にするには `gmtime` か `localtime` を通す

## 関連ページ

- [cpprefjp: std::time](https://cpprefjp.github.io/reference/ctime/time.html)
- [cppreference: std::time](https://en.cppreference.com/w/cpp/chrono/c/time)
