---
title: std::chrono::nonexistent_local_time
summary: "夏時間の切り替えで存在しないローカル時刻を変換したときの例外。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::nonexistent_local_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

夏時間が始まる日は、時計が 2:00 から 3:00 に飛びます。「2:30」は存在しない時刻で、これを UTC に変換しようとすると `nonexistent_local_time` が投げられます。

!!! tip "ポイント"
    - `std::runtime_error` から派生。
    - `to_sys(local_time)` が存在しない時刻で投げる。
    - `choose::earliest` / `choose::latest` を渡すと、投げずに選べる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::nonexistent_local_time {#nonexistent_local_time}

```cpp
class nonexistent_local_time : public runtime_error {
 public:
  template <class D> nonexistent_local_time(const local_time<D>&, const local_info&);
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
    tz->to_sys(local_days{2024y / March / 10} + 2h + 30min);
  } catch (const nonexistent_local_time&) {
    std::println("存在しない時刻");
  }
}
```

```text title="実行結果"
存在しない時刻
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 夏時間の切り替え日のスケジュール | `to_sys(t, choose::earliest)` |

## よくあるミス

??? failure "切り替え日を考えない"
    ゾーンによっては、年に 1 度、存在しない時刻があります。例外が出る箇所を `try` で囲みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ambiguous_local_time`](ambiguous_local_time.md) | 曖昧な時刻の例外 |
| [`local_info`](local_info.md) | 事前に確かめる |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 存在しないローカル時刻の例外
    - [x] 夏時間の切り替えで起こる
    - [x] choose で回避

## 関連ページ

- [cpprefjp: std::chrono::nonexistent_local_time](https://cpprefjp.github.io/reference/chrono/nonexistent_local_time.html)
- [cppreference: std::chrono::nonexistent_local_time](https://en.cppreference.com/w/cpp/chrono/nonexistent_local_time)
