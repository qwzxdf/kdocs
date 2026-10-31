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

`std::stop_source` は、構築すると、中断の状態を共有する仕組みを確保します。状態を確保せず、空の `stop_source` が欲しいとき、`std::nostopstate` を渡します。空の `stop_source` は、停止の要求を出すことも、受けることもできません。

!!! tip "ポイント"
    - `std::stop_source s(std::nostopstate);` で、状態を持たない `stop_source` を作る
    - `stop_possible()` が `false`、`request_stop()` は何もしない
    - 確保のコストを避けたいときに使う
    - C++20

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::nostopstate {#nostopstate}

<span class="ver ver-20">C++20</span>

```cpp
struct nostopstate_t { explicit nostopstate_t() = default; };
inline constexpr std::nostopstate_t nostopstate{};
```

普通の `std::stop_source` は、構築のときに共有状態を確保します。`nostopstate` つきで作ると、確保しないので、軽く作れます。あとから、代入で本物の `stop_source` を入れれば使えます。

```cpp
std::stop_source s(std::nostopstate);
s = std::stop_source{};   // 本物に置き換える
```

`stop_token` の既定の構築も、空のトークンになります。

## 実際に動かしてみる

```cpp
#include <print>
#include <stop_token>

int main() {
  std::stop_source empty(std::nostopstate);
  std::println("空: stop_possible = {}", empty.stop_possible());
  std::println("要求は受け付けない: {}", !empty.request_stop());

  std::stop_source real;
  std::println("通常: stop_possible = {}", real.stop_possible());

  // 本物に置き換えられる
  empty = real;
  std::println("置き換え後: {}", empty.stop_possible());
}
```

```text title="実行結果"
空: stop_possible = false
要求は受け付けない: true
通常: stop_possible = true
置き換え後: true
```

## ゲームでの使いどころ

`stop_source` をメンバーに持つクラスで、まだ使わない間は確保を避けたいときに使います。

## よくあるミス

??? failure "空の stop_source に request_stop する"
    何も起きません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stop_source`](stop_source.md) | 要求を出す側 |
| [`stop_token`](stop_token.md) | 要求を受ける側 |
| [`never_stop_token`](never_stop_token.md) | 停止しないトークン |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::nostopstate](https://cpprefjp.github.io/reference/stop_token/nostopstate.html)
- [cppreference: std::nostopstate](https://en.cppreference.com/w/cpp/thread/nostopstate)
