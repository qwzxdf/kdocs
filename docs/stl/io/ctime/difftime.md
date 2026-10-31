---
title: std::difftime
summary: "2 つの time_t の差を、秒（double）で返す。"
order: 900
tags:
  - 入出力・文字列
---

# std::difftime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

セーブデータの時刻と今の時刻の差から、「前回から何日たったか」を出したい。`time_t` は引き算できそうに見えますが、規格では整数とも浮動小数点数とも決められていません。単位も秒とは限りません。実際の環境のほとんどでは秒の整数ですが、規格の上で安全に差を取る方法が `std::difftime` で、結果は秒の `double` で返ります。

!!! tip "ポイント"
    - `difftime(end, beg)` は、`end - beg` を秒で返す。順番は「新しいほう、古いほう」
    - 戻り値は `double`。小数が付く環境もある
    - 年月日をまたぐ日数の計算には、`chrono` の `year_month_day` のほうが向く
    - 時計が巻き戻ると、負の値になる

!!! info "このページを読む前に"
    [`std::time`](time.md) と [`std::time_t`](time_t.md) を先に読んでください。

## 関数の詳しい説明

### std::difftime {#difftime}

```cpp
double difftime(std::time_t time_end, std::time_t time_beg);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time_end` | `std::time_t` | 新しいほうの時刻 |
| `time_beg` | `std::time_t` | 古いほうの時刻 |

戻り値は `time_end - time_beg` を秒にした `double` です。引数の順番を入れ替えると、符号が逆になるだけで、値は同じです。「新しいほうを先に」と覚えておくと、普通の使い方では正の数になります。

実装は、ほとんどの環境で、`time_t` の整数の引き算をして `double` に直すだけです。`time_t` を `int` に入れて自分で引き算するよりは、`difftime` のほうが、桁あふれと環境の違いに安全です。

落とし穴は、日付をまたいだ計算の単位です。秒を 86400 で割って日数にしても、夏時間の切り替えの日は、1 日が 23 時間や 25 時間になります。「暦の上で何日たったか」を厳密に出したいときは、`year_month_day` に変換して、日数を引き算します。

計算量は定数です。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::time_t saved = 100;  // 古い時刻
  const std::time_t now = 160;    // 新しい時刻
  std::println("{} 秒", std::difftime(now, saved));
  std::println("{} 秒", std::difftime(saved, now));  // 逆にすると負

  // 90000 秒 = 1 日と 1 時間
  const double days = std::difftime(90100, 100) / 86400.0;
  std::println("{} 日", static_cast<int>(days));
}
```

```text title="実行結果"
60 秒
-60 秒
1 日
```

`static_cast<int>` は小数部を切り捨てるので、1 日と 1 時間が `1 日` になります。

## ゲームでの使いどころ

毎日ログイン ボーナスなどの、「前回からの経過日数」に使います。保存してある `time_t` と `time(nullptr)` を渡します。

```cpp
const double sec = std::difftime(std::time(nullptr), lastLogin);
if (sec >= 24 * 60 * 60) {
  // 1 日以上たっている
}
```

## よくあるミス

??? failure "引数の順番を逆にして、負の値で判定が外れる"
    `difftime(saved, now)` は負になります。`>= 86400` の判定が、いつまでも成立しません。新しい時刻（`now`）を先に渡します。

??? failure "夏時間をまたいだ日数が、1 日ずれる"
    秒数で割った日数は、夏時間の切り替えの日に 1 時間ぶんずれます。暦の日付で比べるなら、`chrono` の日付型を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time`](time.md) | 今の時刻 |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間の長さを型で持つ。引き算に向く |
| [`std::chrono::steady_clock`](../../utilities/chrono/steady_clock.md) | 精度のよい計測 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `difftime(end, beg)` で、2 つの `time_t` の差を秒（`double`）で得る
    - [x] 新しいほうを先に渡す
    - [x] 暦の日数を厳密に出すなら、`chrono` の日付型

## 関連ページ

- [cpprefjp: std::difftime](https://cpprefjp.github.io/reference/ctime/difftime.html)
- [cppreference: std::difftime](https://en.cppreference.com/w/cpp/chrono/c/difftime)
