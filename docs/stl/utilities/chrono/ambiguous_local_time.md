---
title: std::chrono::ambiguous_local_time
summary: "夏時間の終わりで 2 回ある（曖昧な）ローカル時刻を変換したときの例外。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::ambiguous_local_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

夏時間が終わる日は、時計が 2:00 から 1:00 に戻り、「1:30」が 2 回あります。どちらの 1:30 か決められないので、UTC に変換しようとすると `ambiguous_local_time` が投げられます。

!!! tip "ポイント"
    - `std::runtime_error` から派生。
    - `to_sys(local_time)` が曖昧な時刻で投げる。
    - `choose::earliest` / `choose::latest` で、どちらかを選べる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::ambiguous_local_time {#ambiguous_local_time}

```cpp
class ambiguous_local_time : public runtime_error {
 public:
  template <class D> ambiguous_local_time(const local_time<D>&, const local_info&);
};
```

- 戻り値: `what()` に説明が入る
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("America/New_York");
  try {
    tz->to_sys(local_days{2024y / November / 3} + 1h + 30min);
  } catch (const ambiguous_local_time&) {
    std::println("曖昧な時刻");
  }
}
```

```text title="実行結果"
曖昧な時刻
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 夏時間の終わりの日のログ | `to_sys(t, choose::earliest)` |

## よくあるミス

??? failure "日本だけで動かして見逃す"
    Asia/Tokyo には夏時間がないため、この例外は出ません。海外ゾーンで初めて出ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nonexistent_local_time`](nonexistent_local_time.md) | 存在しない時刻の例外 |
| [`local_info`](local_info.md) | 事前に確かめる |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 曖昧なローカル時刻の例外
    - [x] 夏時間の終わりで起こる
    - [x] choose で回避

## 関連ページ

- [cpprefjp: std::chrono::ambiguous_local_time](https://cpprefjp.github.io/reference/chrono/ambiguous_local_time.html)
- [cppreference: std::chrono::ambiguous_local_time](https://en.cppreference.com/w/cpp/chrono/ambiguous_local_time)
