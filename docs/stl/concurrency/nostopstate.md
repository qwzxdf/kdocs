---
title: std::nostopstate
summary: "stop_source を、停止の状態を持たない形で作る目印。"
order: 900
tags:
  - 並行処理
---

# std::nostopstate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <stop_token>`
</div>

`std::stop_source` は、作ると停止の状態（共有されるフラグ）を確保します。確保したくない（まだ使わない）ときは、`std::nostopstate` を渡して作ると、状態を持たない `stop_source` になります。

!!! tip "ポイント"
    - `stop_source(std::nostopstate)` の形で使う。
    - 状態を持たないので、`stop_possible()` は `false`。
    - あとで本物の `stop_source` を代入できる。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::nostopstate {#nostopstate}

```cpp
struct nostopstate_t { explicit nostopstate_t() = default; };
inline constexpr nostopstate_t nostopstate{};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <stop_token>

int main() {
  std::stop_source s(std::nostopstate);
  std::println("{}", s.stop_possible());
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 停止の機能を使わないときの初期値 | `std::stop_source s(std::nostopstate);` |

## よくあるミス

??? failure "状態がない `stop_source` に `request_stop` する"
    状態を持たないものに停止を要求しても、何も起こりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stop_source`](stop_source.md) | 停止を要求する側 |
| [`stop_token`](stop_token.md) | 停止を見る側 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 停止の状態を持たない目印
    - [x] stop_possible() が false
    - [x] あとで代入できる

## 関連ページ

- [cpprefjp: std::nostopstate](https://cpprefjp.github.io/reference/stop_token/nostopstate.html)
- [cppreference: std::nostopstate](https://en.cppreference.com/w/cpp/thread/nostopstate)
