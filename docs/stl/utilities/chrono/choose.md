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

夏時間の終わりには、同じ壁掛け時計の時刻が 2 回現れます。1:30 が 2 回あるとき、UTC のどちらの瞬間にするかを、呼ぶ側が決めます。`std::chrono::choose` は、その選択を表す列挙型で、`earliest`（先のほう）か `latest`（後のほう）を指定します。

!!! tip "ポイント"
    - `choose::earliest` は、先に現れる側（夏時間の側）
    - `choose::latest` は、後に現れる側（標準時間の側）
    - `time_zone::to_sys(local, choose)` に渡す
    - 存在しない時刻（春の飛ばされた時刻）にも、この指定で解決できる

!!! info "このページを読む前に"
    [`local_info`](local_info.md) と [`time_zone`](time_zone.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::choose {#choose}

<span class="ver ver-20">C++20</span>

```cpp
enum class choose { earliest, latest };
```

`to_sys(local_time)` は、曖昧な時刻や存在しない時刻を渡すと例外を投げます。`to_sys(local_time, choose)` は、例外を投げずに、指定に従った値を返します。

曖昧な時刻（秋の 1:30）では、`earliest` が夏時間側、`latest` が標準時間側の瞬間で、2 つの差は夏時間の補正分（普通は 1 時間）です。

存在しない時刻（春の 2:30）に対しては、`earliest` でも `latest` でも、切り替えの瞬間が返ります。

`zoned_time` のコンストラクターにも、`choose` を渡せます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const time_zone* ny = locate_zone("America/New_York");

  // 秋の夏時間の終了日: 1:30 が 2 回ある
  const local_seconds twice = local_days{2026y / November / 1} + 1h + 30min;
  const sys_seconds first = ny->to_sys(twice, choose::earliest);
  const sys_seconds second = ny->to_sys(twice, choose::latest);

  std::println("earliest: {:%F %T} UTC", first);
  std::println("latest:   {:%F %T} UTC", second);
  std::println("差: {} 分", duration_cast<minutes>(second - first).count());
}
```

```text title="実行結果"
earliest: 2026-11-01 05:30:00 UTC
latest:   2026-11-01 06:30:00 UTC
差: 60 分
```

ニューヨークの 1:30 に当たる UTC の瞬間が、`05:30`（夏時間、EDT）と `06:30`（標準時間、EST）の 2 つあります。

## ゲームでの使いどころ

「毎日 1:30 にリセット」のような設定が、秋の切り替え日に 2 回起きないよう、`earliest` を選んで 1 回に決めます。

## よくあるミス

??? failure "choose を渡さず、例外で落ちる"
    曖昧な時刻に `to_sys` を choose なしで呼ぶと例外です。設計値の時刻なら、`choose` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ambiguous_local_time`](ambiguous_local_time.md) | choose を渡さなかったときの例外 |
| [`local_info`](local_info.md) | 状態を事前に調べる |
| [`time_zone`](time_zone.md) | `to_sys` を持つ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: choose](https://cpprefjp.github.io/reference/chrono/choose.html)
- [cppreference: std::chrono::choose](https://en.cppreference.com/w/cpp/chrono/choose)
