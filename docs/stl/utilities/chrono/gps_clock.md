---
title: std::chrono::gps_clock
summary: "GPS の時刻に合わせた時計。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::gps_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

GPS 衛星が配る時刻は、1980 年 1 月 6 日を基準にして、うるう秒を入れずに進みます。`gps_clock` は、この GPS 時刻を表す時計です。

!!! tip "ポイント"
    - TAI より 19 秒遅れている。
    - `now()` で今の時点を取る。
    - `is_steady` は `false`（時計の補正が入りうる）。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::gps_clock {#gps_clock}

```cpp
class gps_clock {
 public:
  using rep = /* 実装定義 */;
  using period = ratio<1>;
  using duration = chrono::duration<rep, period>;
  using time_point = chrono::time_point<gps_clock>;
  static constexpr bool is_steady = false;
  static time_point now();
};
```

- 戻り値: `now()` は今の `time_point`
- 計算量: `now()` は定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::gps_clock::is_steady);
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| うるう秒も含む厳密な経過時間 | `utc_clock` / `tai_clock` の時点を引き算する |

## よくあるミス

??? failure "`system_clock` と取り違える"
    1 日の長さの扱いが違います。普通のゲームのタイムスタンプには [`system_clock`](system_clock.md) で十分です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | うるう秒を無視する普通の時計 |
| [`clock_cast`](clock_cast.md) | 時計どうしを変換する |

## コンパイラ対応

C++20 の機能です。GCC 13 以降で使えます。MSVC は 19.29 以降。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPS の時刻に合わせた時計
    - [x] `is_steady` は false
    - [x] 普段は system_clock / steady_clock でよい

## 関連ページ

- [cpprefjp: std::chrono::gps_clock](https://cpprefjp.github.io/reference/chrono/gps_clock.html)
- [cppreference: std::chrono::gps_clock](https://en.cppreference.com/w/cpp/chrono/gps_clock)
