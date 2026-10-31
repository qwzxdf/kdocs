---
title: std::timespec_get
summary: "現在の時刻を、秒とナノ秒の組（timespec）で取得する。"
order: 900
tags:
  - 入出力・文字列
---

# std::timespec_get

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <ctime>`
</div>

`time(nullptr)` は秒の精度です。もっと細かい現在時刻（UTC）が欲しいが、`chrono` を使うほどでもない、という場面のために、C11 で追加され、C++17 で取り込まれたのが `timespec_get` です。結果を `timespec`（秒とナノ秒）に書き込みます。

実際の精度は環境しだいで、ナノ秒の単位で値が出ても、細かさは数百ナノ秒から、数マイクロ秒にとどまることがあります。

!!! tip "ポイント"
    - `timespec_get(&ts, TIME_UTC)` で、UTC の現在時刻が取れる
    - 戻り値は、成功なら第 2 引数の基準（`TIME_UTC`）、失敗なら 0
    - 現在時刻を取るだけで、経過時間の計測には向かない（巻き戻る）
    - C++ では `system_clock::now()` で、同じことがより簡単にできる

!!! info "このページを読む前に"
    [`std::timespec`](timespec.md) と [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::timespec_get {#timespec_get}

<span class="ver ver-17">C++17</span>

```cpp
int timespec_get(std::timespec* ts, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ts` | `std::timespec*` | 結果の書き込み先 |
| `base` | `int` | 時刻の基準。標準で決まっているのは `TIME_UTC` だけ |

`base` に `TIME_UTC` を渡すと、1970 年 1 月 1 日 0 時（UTC）からの経過時間を、秒とナノ秒で `ts` に書き込みます。`TIME_UTC` 以外の基準は、規格では決まっていません。環境によっては、独自の基準が追加されていることもあります。

戻り値は、成功すると `base`（つまり `TIME_UTC`、値は 1）、失敗すると 0 です。戻り値が `TIME_UTC` かどうかを確かめてから、`ts` を使います。

注意したいのは、時計の細かさが保証されないことです。`tv_nsec` が 1 ミリ秒ごとにしか変わらない環境もあります。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::timespec ts{};
  const int result = std::timespec_get(&ts, TIME_UTC);

  std::println("成功: {}", result == TIME_UTC);
  std::println("ナノ秒は範囲内: {}", ts.tv_nsec >= 0 && ts.tv_nsec < 1'000'000'000);
  std::println("1970 年より後: {}", ts.tv_sec > 0);
}
```

```text title="実行結果"
成功: true
ナノ秒は範囲内: true
1970 年より後: true
```

## ゲームでの使いどころ

ゲームのコードで使うことはほとんどありません。ミリ秒単位の現在時刻（ログのタイムスタンプ）が欲しいときは、`std::chrono::system_clock::now()` を使います。経過時間の計測は、`steady_clock` です。

## よくあるミス

??? failure "戻り値を確かめない"
    失敗すると 0 を返し、`ts` は書き換わりません。初期化していない `ts` を使うと、ゴミの値が時刻になります。

??? failure "計測に使って、巻き戻る"
    システム時計なので、NTP などの補正で戻ることがあります。経過時間は `steady_clock` で測ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::time`](time.md) | 秒の精度の現在時刻 |
| [`std::chrono::system_clock`](../../utilities/chrono/system_clock.md) | C++ の現在時刻。普段はこちら |
| [`std::chrono::steady_clock`](../../utilities/chrono/steady_clock.md) | 経過時間の計測用 |

## コンパイラ対応

C++17 から標準です。MSVC、GCC、Clang とも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `timespec_get(&ts, TIME_UTC)` で、秒とナノ秒の現在時刻が取れる
    - [x] 戻り値が `TIME_UTC` かを確かめる
    - [x] 普段は `system_clock::now()`、計測は `steady_clock`

## 関連ページ

- [cpprefjp: std::timespec_get](https://cpprefjp.github.io/reference/ctime/timespec_get.html)
- [cppreference: std::timespec_get](https://en.cppreference.com/w/cpp/chrono/c/timespec_get)
