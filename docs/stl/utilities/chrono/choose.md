---
title: std::chrono::choose
summary: "曖昧なローカル時刻の変換で、どちらを選ぶかを指定する列挙型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::choose

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

夏時間の終わりでは、同じローカル時刻が 2 回あります。`time_zone::to_sys(local_time, choose::earliest)` のように、`choose` を渡すと、例外を投げずに、早いほう（`earliest`）か遅いほう（`latest`）を選べます。

!!! tip "ポイント"
    - `earliest`: 2 回あるうちの早いほう。
    - `latest`: 遅いほう。
    - 存在しない時刻に対しては、切り替わりの時点が返る。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::choose {#choose}

```cpp
enum class choose {
  earliest,
  latest
};
```

- 戻り値: なし（列挙型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  const auto* tz = locate_zone("America/New_York");
  auto t = local_days{2024y / November / 3} + 1h + 30min;  // 2 回ある時刻
  auto a = tz->to_sys(t, choose::earliest);
  auto b = tz->to_sys(t, choose::latest);
  std::println("{}", (b - a).count());
}
```

```text title="実行結果"
3600
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 曖昧な時刻を、早いほうに決める | `tz->to_sys(t, std::chrono::choose::earliest)` |

## よくあるミス

??? failure "例外を投げると思う"
    `choose` を渡すと、例外は投げず、どちらかが選ばれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ambiguous_local_time`](ambiguous_local_time.md) | 曖昧な時刻の例外 |
| [`time_zone`](time_zone.md) | ゾーン |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 曖昧なローカル時刻の選び方
    - [x] earliest / latest
    - [x] 例外を避けられる

## 関連ページ

- [cpprefjp: std::chrono::choose](https://cpprefjp.github.io/reference/chrono/choose.html)
- [cppreference: std::chrono::choose](https://en.cppreference.com/w/cpp/chrono/choose)
