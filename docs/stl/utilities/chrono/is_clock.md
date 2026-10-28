---
title: std::chrono::is_clock
summary: "型が chrono の「時計」の条件を満たすかを調べる型特性。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::is_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

ジェネリックな関数で、`system_clock` や `steady_clock` のような時計の型だけを受け付けたいことがあります。`is_clock_v<C>` は、`C` が時計として必要な型名（`rep`・`period`・`duration`・`time_point`）と `now()`・`is_steady` を持つなら `true` です。

!!! tip "ポイント"
    - `_v` 版で `bool` が取れる。
    - 自作の時計が条件を満たしているかの確認に使える。
    - C++20 の機能。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::is_clock {#is_clock}

```cpp
template <class T>
struct is_clock;
template <class T>
inline constexpr bool is_clock_v = is_clock<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 時計なら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::println("{}", std::chrono::is_clock_v<std::chrono::steady_clock>);
  std::println("{}", std::chrono::is_clock_v<int>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 時計の型だけを受け付けるテンプレート | `static_assert(std::chrono::is_clock_v<Clock>);` |

## よくあるミス

??? failure "時刻の型（`time_point`）を渡す"
    `time_point` は時計ではありません。時計の型は `system_clock` などです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | 時計の例 |
| [`steady_clock`](steady_clock.md) | 時計の例 |

## コンパイラ対応

C++20 の機能です。GCC 13 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時計の条件を調べる型特性
    - [x] _v 版で bool
    - [x] 自作の時計の検査に

## 関連ページ

- [cpprefjp: std::chrono::is_clock](https://cpprefjp.github.io/reference/chrono/is_clock.html)
- [cppreference: std::chrono::is_clock](https://en.cppreference.com/w/cpp/chrono/is_clock)
