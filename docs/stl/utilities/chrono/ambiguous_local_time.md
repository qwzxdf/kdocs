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

夏時間の終わりには、同じ壁掛け時計の時刻が 2 回現れます。その時刻を、`choose` なしで UTC に変換しようとすると、どちらの瞬間か決まらないので、`std::chrono::ambiguous_local_time` が投げられます。

!!! tip "ポイント"
    - `time_zone::to_sys(local)` や `zoned_time` の構築で投げられる
    - 夏時間のない地域では起きない
    - `std::runtime_error` の派生クラス
    - 避けるには、`choose` を渡すか、`get_info` で事前に調べる

!!! info "このページを読む前に"
    [`choose`](choose.md) と [`local_info`](local_info.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::ambiguous_local_time {#ambiguous_local_time}

<span class="ver ver-20">C++20</span>

```cpp
class ambiguous_local_time : public std::runtime_error {
 public:
  template <class Duration>
  ambiguous_local_time(const local_time<Duration>& tp, const local_info& i);
};
```

`what()` のメッセージには、曖昧な時刻と、2 通りの解釈（切り替え前と後の `sys_info`）が入ります。表示や比較には使わず、例外の型で判断します。

この例外は、夏時間のある地域で、切り替え日の夜中の時刻を扱うときだけ起きます。普段の動作確認では出ないので、本番で初めて発生する、という事故が起きやすいです。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const time_zone* ny = locate_zone("America/New_York");
  const local_seconds twice = local_days{2026y / November / 1} + 1h + 30min;

  try {
    ny->to_sys(twice);  // choose なし: どちらか決まらない
  } catch (const ambiguous_local_time&) {
    std::println("曖昧な時刻の例外");
  }

  // choose を渡せば、例外にならない
  const sys_seconds s = ny->to_sys(twice, choose::earliest);
  std::println("解決: {:%F %T} UTC", s);
}
```

```text title="実行結果"
曖昧な時刻の例外
解決: 2026-11-01 05:30:00 UTC
```

## ゲームでの使いどころ

地域の時刻で決めたリセット時刻を扱うサーバーの処理で、夏時間の切り替え日に落ちないよう、`choose` を渡しておきます。

## よくあるミス

??? failure "夏時間のない地域でだけテストして、本番で落ちる"
    日本では起きません。夏時間のある地域のユーザーに対して、初めて起きます。`choose` を最初から渡しておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nonexistent_local_time`](nonexistent_local_time.md) | 存在しない時刻の例外 |
| [`choose`](choose.md) | 例外を避ける指定 |
| [`local_info`](local_info.md) | 事前に調べる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: ambiguous_local_time](https://cpprefjp.github.io/reference/chrono/ambiguous_local_time.html)
- [cppreference: std::chrono::ambiguous_local_time](https://en.cppreference.com/w/cpp/chrono/ambiguous_local_time)
