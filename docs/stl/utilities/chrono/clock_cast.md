---
title: std::chrono::clock_cast
summary: "時計どうしの時点を、別の時計の時点に変換する。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::clock_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`system_clock` の時点を、`utc_clock` や `tai_clock` の時点に直したい。ファイルの更新日時（`file_clock`）を、日付として表示したい。時計ごとに起点や、うるう秒の扱いが違うので、時点の数値をそのまま移すことはできません。`std::chrono::clock_cast<DestClock>(tp)` は、時計の違いを吸収して、別の時計の時点に変換する関数です。

!!! tip "ポイント"
    - `clock_cast<utc_clock>(sys_tp)` のように、変換先の時計を指定する
    - `system_clock` を中継点にして、必要なら複数の変換をつなぐ
    - 同じ瞬間を表す時点に変換される。値は時計ごとに違う
    - 変換できない組み合わせは、コンパイル エラー

!!! info "このページを読む前に"
    [`system_clock`](system_clock.md)、[`utc_clock`](utc_clock.md)、[`file_clock`](file_clock.md) のいずれかを先に読んでください。

## 関数の詳しい説明

### std::chrono::clock_cast {#clock_cast}

<span class="ver ver-20">C++20</span>

```cpp
template <class DestClock, class SourceClock, class Duration>
auto clock_cast(const time_point<SourceClock, Duration>& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `DestClock` | テンプレート引数 | 変換先の時計 |
| `t` | `time_point<SourceClock, Duration>` | 変換する時点 |

`SourceClock` から `DestClock` へ、`to_sys` / `from_sys`、`to_utc` / `from_utc` の関数があれば、それらをつないで変換します。`system_clock`、`utc_clock`、`tai_clock`、`gps_clock`、`file_clock` の間は、すべて相互に変換できます。

戻り値の `Duration` は、元の `Duration` と秒の共通の型です。たとえば `sys_days` を `utc_clock` に変換すると、秒の単位の `utc_time` になります。

変換の関数を持たない時計や、`local_t`（タイムゾーンのない時刻）との変換は、コンパイル エラーです。`local_time` を `sys_time` にするには、`time_zone` が要ります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const sys_seconds s = sys_days{2026y / January / 1};

  // 時計をまたいで変換する
  const utc_seconds u = clock_cast<utc_clock>(s);
  const tai_seconds t = clock_cast<tai_clock>(s);
  const gps_seconds g = clock_cast<gps_clock>(s);

  // 元に戻すと、同じ時点になる
  std::println("UTC 経由で往復: {}", clock_cast<system_clock>(u) == s);
  std::println("TAI 経由で往復: {}", clock_cast<system_clock>(t) == s);
  std::println("GPS 経由で往復: {}", clock_cast<system_clock>(g) == s);
}
```

```text title="実行結果"
UTC 経由で往復: true
TAI 経由で往復: true
GPS 経由で往復: true
```

時計ごとに数値は違いますが、元の時計に戻すと同じ時点になります。

## ゲームでの使いどころ

ファイルの更新日時を表示する（`file_clock` → `system_clock`）ときが、ほとんど唯一の場面です。

## よくあるミス

??? failure "時点の数値をそのままコピーする"
    時計ごとに起点が違います。`clock_cast` で変換します。

??? failure "local_time を clock_cast しようとする"
    タイムゾーンが分からないので、変換できません。`time_zone::to_sys` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time_point_cast`](time_point_cast.md) | 同じ時計の中で、単位を変える |
| [`zoned_time`](zoned_time.md) | タイムゾーンつきで変換する |
| [`is_clock`](is_clock.md) | 型が時計かを調べる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: clock_cast](https://cpprefjp.github.io/reference/chrono/clock_cast.html)
- [cppreference: std::chrono::clock_cast](https://en.cppreference.com/w/cpp/chrono/clock_cast)
