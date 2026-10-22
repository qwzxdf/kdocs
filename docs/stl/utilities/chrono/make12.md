---
title: std::chrono::make12
summary: "24 時間制の時を、12 時間制の時（1〜12）に直す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::make12

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「15 時」を「午後 3 時」と表示するには、12 時間制に直す必要があります。`make12(hours{15})` は `hours{3}` を返します。

!!! tip "ポイント"
    - 0 時は 12 になる（午前 12 時）。
    - 午前か午後かは [`is_am`](is_am.md) / [`is_pm`](is_pm.md) で別に調べる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::make12 {#make12}

```cpp
constexpr hours make12(const hours& h) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `h` | hours | 24 時間制の時（0〜23） |

- 戻り値: 12 時間制の時（1〜12）の `hours`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  std::println("{}", make12(hours{15}).count());
  std::println("{}", make12(hours{0}).count());
}
```

```text title="実行結果"
3
12
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 時計の表示 | `make12(hours{h}).count()` |

## よくあるミス

??? failure "0 時の結果を 0 だと思う"
    0 時は 12 になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make24`](make24.md) | 逆の変換 |
| [`hh_mm_ss`](hh_mm_ss.md) | 時分秒 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 24 → 12 時間制
    - [x] 0 時は 12
    - [x] 午前午後は別に調べる

## 関連ページ

- [cpprefjp: std::chrono::make12](https://cpprefjp.github.io/reference/chrono/make12.html)
- [cppreference: std::chrono::make12](https://en.cppreference.com/w/cpp/chrono/hour_of_day/make12)
