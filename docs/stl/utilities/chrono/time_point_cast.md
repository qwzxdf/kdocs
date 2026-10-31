---
title: std::chrono::time_point_cast
summary: "time_point の単位を、別の単位に変換する（切り捨て）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::time_point_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`system_clock::now()` は、ナノ秒（や 100 ナノ秒）の細かさの時点を返します。ログに書くには秒の細かさで足りるので、時点の単位を粗くしたい。`std::chrono::time_point_cast<ToDuration>` は、`time_point` の単位を変える関数で、`duration_cast` の `time_point` 版です。

!!! tip "ポイント"
    - `time_point_cast<seconds>(tp)` で、秒単位の時点にする
    - 端数は 0 に向かって丸める（`duration_cast` と同じ）。エポックより前の時点では、`floor` と結果が違う
    - 時計の種類（`Clock`）は変わらず、単位だけが変わる
    - `floor`、`ceil`、`round` の `time_point` 版もある

!!! info "このページを読む前に"
    [`time_point`](time_point.md) と [`duration_cast`](duration_cast.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::time_point_cast {#time_point_cast}

```cpp
template <class ToDuration, class Clock, class Duration>
constexpr time_point<Clock, ToDuration>
time_point_cast(const time_point<Clock, Duration>& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換先の `duration` の型 |
| `t` | `time_point` | 変換する時点 |

`t.time_since_epoch()` を `duration_cast<ToDuration>` して、新しい `time_point` を作ります。戻り値の `Clock` は、元と同じです。

端数の丸めは、0 に向かう方向です。エポック（1970 年）より後の時点では切り捨てですが、エポックより前の時点（負の時間）では、切り上げの向きになります。常に切り捨てたいなら `floor<ToDuration>(t)` を使います。

日の単位にそろえると、時刻を捨てた日付が得られます。`time_point_cast<days>(system_clock::now())` は `sys_days` と同じ型です。ただし、エポックより前では、前述のとおり、丸めの向きに注意します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // ミリ秒単位の時点: エポックから 1999 ミリ秒
  const time_point<system_clock, milliseconds> tp{milliseconds{1999}};

  // 秒単位に直す（切り捨て）
  const auto sec = time_point_cast<seconds>(tp);
  std::println("{} 秒", sec.time_since_epoch().count());

  // 負の時点（エポックより前）では、0 に向かって丸められる
  const time_point<system_clock, milliseconds> before{milliseconds{-1999}};
  std::println("time_point_cast: {} 秒",
               time_point_cast<seconds>(before).time_since_epoch().count());
  std::println("floor:           {} 秒",
               floor<seconds>(before).time_since_epoch().count());
}
```

```text title="実行結果"
1 秒
time_point_cast: -1 秒
floor:           -2 秒
```

`-1999` ミリ秒は、`time_point_cast` では -1 秒、`floor` では -2 秒です。

## ゲームでの使いどころ

ログの時刻やセーブデータの更新日時を、秒の単位にそろえて記録するときに使います。細かさが違う時点どうしを比べる前にも、単位をそろえます。

## よくあるミス

??? failure "負の時点でも切り捨てだと思う"
    エポックより前では 0 に向かうので、切り捨てになりません。常に切り捨てるなら `floor` です。

??? failure "細かい単位へ変換するときに cast を使う"
    細かい単位への変換は、暗黙にできます。cast は、粗い単位に変えるときに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration_cast`](duration_cast.md) | `duration` の単位を変える |
| [`floor`](floor.md) | 常に切り捨てる |
| [`ceil`](ceil.md) | 切り上げる |
| [`round`](round.md) | 四捨五入する |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: time_point_cast](https://cpprefjp.github.io/reference/chrono/time_point_cast.html)
- [cppreference: std::chrono::time_point_cast](https://en.cppreference.com/w/cpp/chrono/time_point_cast)
