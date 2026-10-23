---
title: std::chrono::tai_time
summary: "tai_clock の時点（単位を選べる）を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::tai_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`time_point<tai_clock, ...>` のように毎回書くのは長いので、標準が別名を用意しています。`tai_time` は、tai_clock の時点（単位を選べる）です。

!!! tip "ポイント"
    - 中身は `time_point<tai_clock, Duration>`。
    - `time_since_epoch().count()` で経過を取れる。
    - 時計の違いを型で区別できる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::tai_time {#tai_time}

```cpp
template <class Duration>
using tai_time = time_point<tai_clock, Duration>;
```

- 戻り値: `tai_time` の値
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::chrono::tai_time<std::chrono::seconds>, std::chrono::time_point<std::chrono::tai_clock, std::chrono::seconds>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 時計ごとに時点の型を区別する | `std::chrono::tai_time` |

## よくあるミス

??? failure "時計が違う時点を混ぜる"
    別の時計の時点どうしは、引き算できません。`clock_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`clock_cast`](clock_cast.md) | 時計どうしを変換する |
| [`tai_clock`](tai_clock.md) | 時計 |

## コンパイラ対応

C++20 の機能です。GCC 13 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tai_clock の時点（単位を選べる）の別名
    - [x] time_since_epoch() で経過を取る
    - [x] clock_cast で他の時計に変換

## 関連ページ

- [cpprefjp: std::chrono::tai_time](https://cpprefjp.github.io/reference/chrono/time_point.html)
- [cppreference: std::chrono::tai_time](https://en.cppreference.com/w/cpp/chrono/time_point)
