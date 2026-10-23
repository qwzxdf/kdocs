---
title: std::chrono::gps_seconds
summary: "gps_clock の時点（秒単位）を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::gps_seconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`time_point<gps_time, ...>` のように毎回書くのは長いので、標準が別名を用意しています。`gps_seconds` は、gps_clock の時点（秒単位）です。

!!! tip "ポイント"
    - 中身は `gps_time<seconds>`。
    - `time_since_epoch().count()` で経過を取れる。
    - 時計の違いを型で区別できる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::gps_seconds {#gps_seconds}

```cpp
using gps_seconds = gps_time<seconds>;
```

- 戻り値: `gps_seconds` の値
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::chrono::gps_seconds, std::chrono::time_point<std::chrono::gps_clock, std::chrono::seconds>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 時計ごとに時点の型を区別する | `std::chrono::gps_seconds` |

## よくあるミス

??? failure "時計が違う時点を混ぜる"
    別の時計の時点どうしは、引き算できません。`clock_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`clock_cast`](clock_cast.md) | 時計どうしを変換する |
| [`gps_clock`](gps_clock.md) | 時計 |

## コンパイラ対応

C++20 の機能です。GCC 13 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] gps_clock の時点（秒単位）の別名
    - [x] time_since_epoch() で経過を取る
    - [x] clock_cast で他の時計に変換

## 関連ページ

- [cpprefjp: std::chrono::gps_seconds](https://cpprefjp.github.io/reference/chrono/time_point.html)
- [cppreference: std::chrono::gps_seconds](https://en.cppreference.com/w/cpp/chrono/time_point)
