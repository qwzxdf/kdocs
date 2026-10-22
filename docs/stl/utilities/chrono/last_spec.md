---
title: std::chrono::last_spec
summary: "「最後」を表す定数 `std::chrono::last` の型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::last_spec

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`February / last` や `Friday[last]` に出てくる `last` は、「最後」を表す特別な定数です。`last_spec` はその型で、直接使うことはほとんどありません。

!!! tip "ポイント"
    - `std::chrono::last` が唯一の値。
    - `month / last`、`weekday[last]` の中で使う。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::last_spec {#last_spec}

```cpp
struct last_spec { explicit last_spec() = default; };
inline constexpr last_spec last{};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto ymdl = 2024y / February / last;
  std::println("{}", unsigned(ymdl.day()));
}
```

```text title="実行結果"
29
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 月末の指定 | `std::chrono::last` |

## よくあるミス

??? failure "`last` を数値と思う"
    `last` は数値ではなく目印の型の値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_day_last`](month_day_last.md) | 月末 |
| [`weekday_last`](weekday_last.md) | 最後の曜日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「最後」を表す目印
    - [x] month / last など
    - [x] 型自体は意識しない

## 関連ページ

- [cpprefjp: std::chrono::last_spec](https://cpprefjp.github.io/reference/chrono/last_spec.html)
- [cppreference: std::chrono::last_spec](https://en.cppreference.com/w/cpp/chrono/last_spec)
