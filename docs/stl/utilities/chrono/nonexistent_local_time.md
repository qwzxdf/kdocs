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

夏時間の開始では、時計が 2:00 から 3:00 に飛びます。2:30 は、その日にはありません。この「存在しない時刻」を、`choose` なしで UTC に変換しようとすると、`std::chrono::nonexistent_local_time` が投げられます。

!!! tip "ポイント"
    - `time_zone::to_sys(local)` や `zoned_time` の構築で投げられる
    - 夏時間のある地域の、春の切り替え日にだけ起きる
    - `std::runtime_error` の派生クラス
    - 避けるには、`choose` を渡すか、`get_info` で事前に調べる

!!! info "このページを読む前に"
    [`ambiguous_local_time`](ambiguous_local_time.md) と [`choose`](choose.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::nonexistent_local_time {#nonexistent_local_time}

<span class="ver ver-20">C++20</span>

```cpp
class nonexistent_local_time : public std::runtime_error {
 public:
  template <class Duration>
  nonexistent_local_time(const local_time<Duration>& tp, const local_info& i);
};
```

`ambiguous_local_time` と対になる例外です。どちらも、1 通りの UTC に決まらない時刻を、そのまま変換しようとしたときの例外ですが、原因が逆です。曖昧は「2 通りある」、存在しないは「0 通り」です。

`choose` を渡せば、例外ではなく、値が返ります。存在しない時刻に対しては、`earliest` でも `latest` でも、<strong>切り替えの瞬間</strong>（飛ばされる区間の始まり）が返ります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const time_zone* ny = locate_zone("America/New_York");

  // 2026-03-08 は春の夏時間の開始日: 2:30 は存在しない
  const local_seconds skipped = local_days{2026y / March / 8} + 2h + 30min;

  try {
    ny->to_sys(skipped);
  } catch (const nonexistent_local_time&) {
    std::println("存在しない時刻の例外");
  }

  // choose を渡せば、切り替えの瞬間になる
  std::println("earliest: {:%F %T} UTC", ny->to_sys(skipped, choose::earliest));
  std::println("latest:   {:%F %T} UTC", ny->to_sys(skipped, choose::latest));
}
```

```text title="実行結果"
存在しない時刻の例外
earliest: 2026-03-08 07:00:00 UTC
latest:   2026-03-08 07:00:00 UTC
```

存在しない 2:30 は、`earliest` でも `latest` でも、切り替えの瞬間の `07:00 UTC`（東部標準時の 2:00、東部夏時間の 3:00）という、同じ結果になっています。

## ゲームでの使いどころ

地域の時刻で決めたイベントの開始時刻が、春の切り替え日に存在しないとき、落ちないように `choose` を渡します。

## よくあるミス

??? failure "日本でだけテストして、春の切り替えで落ちる"
    日本には夏時間がありません。夏時間のある地域の人が遊ぶとき、初めて起きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ambiguous_local_time`](ambiguous_local_time.md) | 曖昧な時刻の例外 |
| [`choose`](choose.md) | 例外を避ける指定 |
| [`local_info`](local_info.md) | 事前に調べる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: nonexistent_local_time](https://cpprefjp.github.io/reference/chrono/nonexistent_local_time.html)
- [cppreference: std::chrono::nonexistent_local_time](https://en.cppreference.com/w/cpp/chrono/nonexistent_local_time)
