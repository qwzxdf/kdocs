---
title: std::chrono::file_time
summary: "file_clock の時点を表す別名（単位を選べる）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::file_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`time_point<system_clock, seconds>` のように毎回書くのは長いので、標準が別名を用意しています。`std::chrono::file_time` は、file_clock の時点を表す別名（単位を選べる）です。

!!! tip "ポイント"
    - 中身は `time_point<file_clock, Duration>`。
    - `time_since_epoch().count()` で基準時刻からの経過を数で取れる。
    - 時計の違いを型で区別できる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::file_time {#file_time}

```cpp
template <class Duration>
using file_time = time_point<file_clock, Duration>;
```

- 戻り値: `file_time` の値
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::chrono::file_time<std::chrono::seconds>, std::chrono::time_point<std::chrono::file_clock, std::chrono::seconds>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 時刻を型で区別する | `std::chrono::file_time` |

## よくあるミス

??? failure "時計が違う時点を混ぜる"
    `local_time` は地域の時刻、`sys_time` は UTC 基準の時刻で、型が別です。変換は `zoned_time` や `time_zone` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time_point`](time_point.md) | 時点の型 |
| [`zoned_time`](zoned_time.md) | タイムゾーンつきの時刻 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] file_clock の時点を表す別名（単位を選べる）
    - [x] time_since_epoch() で経過を取る
    - [x] 型で時計の種類を区別する

## 関連ページ

- [cpprefjp: std::chrono::file_time](https://cpprefjp.github.io/reference/chrono/time_point.html)
- [cppreference: std::chrono::file_time](https://en.cppreference.com/w/cpp/chrono/time_point)
