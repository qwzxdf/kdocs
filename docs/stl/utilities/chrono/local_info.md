---
title: std::chrono::local_info
summary: "あるローカル時刻の時差情報（曖昧・存在しない場合も表す）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::local_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

夏時間のある地域では、壁掛け時計の時刻が、1 通りの UTC に決まらないことがあります。春は、時計が 2:00 から 3:00 に飛ぶので、2:30 は存在しません。秋は、時計が 2:00 から 1:00 に戻るので、1:30 は 2 回あります。`time_zone::get_info(local_time)` が返す `std::chrono::local_info` は、ローカル時刻がどのような状態かと、前後の `sys_info` を持ちます。

!!! tip "ポイント"
    - `result` が `unique`（1 通り）、`nonexistent`（存在しない）、`ambiguous`（2 通り）のどれか
    - `first` は前のゾーン情報、`second` は後のゾーン情報（`unique` では `second` は未使用）
    - `unique` なら、`first` を使えば足りる
    - 夏時間のない地域では、常に `unique`

!!! info "このページを読む前に"
    [`sys_info`](sys_info.md) と [`local_time`](local_time.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_info {#local_info}

<span class="ver ver-20">C++20</span>

```cpp
struct local_info {
  static constexpr int unique = 0;
  static constexpr int nonexistent = 1;
  static constexpr int ambiguous = 2;
  int result;
  sys_info first;
  sys_info second;
};
```

`result` の意味は、次のとおりです。

| 値 | 状態 | `first` / `second` |
| --- | --- | --- |
| `unique` | 1 通りに決まる | `first` だけが有効 |
| `nonexistent` | 夏時間の開始で飛ばされた時刻 | `first` は切り替え前、`second` は切り替え後 |
| `ambiguous` | 夏時間の終了で 2 回現れる時刻 | `first` は切り替え前（夏時間）、`second` は切り替え後 |

`to_sys` を呼ぶ前に、`get_info(local_time)` で状態を調べておけば、例外に頼らず、分岐して処理できます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const time_zone* ny = locate_zone("America/New_York");
  const time_zone* tokyo = locate_zone("Asia/Tokyo");

  // 2026-03-08 は春の夏時間の開始日: 2:30 は存在しない
  const local_seconds skipped = local_days{2026y / March / 8} + 2h + 30min;
  std::println("存在しない時刻: {}", ny->get_info(skipped).result == local_info::nonexistent);

  // 2026-11-01 は秋の夏時間の終了日: 1:30 は 2 回ある
  const local_seconds twice = local_days{2026y / November / 1} + 1h + 30min;
  std::println("曖昧な時刻: {}", ny->get_info(twice).result == local_info::ambiguous);

  // 東京は夏時間がないので、常に 1 通り
  std::println("東京は unique: {}", tokyo->get_info(twice).result == local_info::unique);
}
```

```text title="実行結果"
存在しない時刻: true
曖昧な時刻: true
東京は unique: true
```

## ゲームでの使いどころ

「毎日 2:30 にイベント」のような、地域の時刻で決めた設計値が、夏時間の境目でどう扱われるかを、事前に調べられます。

## よくあるミス

??? failure "unique でないときに first だけを使う"
    `nonexistent` や `ambiguous` では、`second` も意味を持ちます。両方を見て判断します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sys_info`](sys_info.md) | UTC の時点から調べる版 |
| [`choose`](choose.md) | 曖昧さの解決方法 |
| [`ambiguous_local_time`](ambiguous_local_time.md) | 曖昧なときに `to_sys` が投げる例外 |
| [`nonexistent_local_time`](nonexistent_local_time.md) | 存在しないときに投げる例外 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: local_info](https://cpprefjp.github.io/reference/chrono/local_info.html)
- [cppreference: std::chrono::local_info](https://en.cppreference.com/w/cpp/chrono/local_info)
