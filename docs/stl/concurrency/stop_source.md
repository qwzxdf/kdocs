---
title: std::stop_source
summary: "「止まって」の合図を出す側。"
order: 73
tags:
  - 並行処理
---

# std::stop_source

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <stop_token>`
</div>

`std::stop_source` は、**「止まって」の合図を出す側**です。`request_stop()` で合図を出し、`get_token()` で、合図を受け取る側の [`stop_token`](stop_token.md) を取り出します。`jthread` を使わずに、自分で停止の仕組みを組むときに使います。

!!! tip "ポイント"
    - 1 つの `stop_source` から、いくつでも `stop_token` を取り出せる。
    - `request_stop()` は、何度呼んでも安全（2 回目以降は何もしない）。
    - `jthread` なら内部で持っているので、通常は使わない。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::stop_source {#stop_source}

```cpp
class stop_source {
 public:
  stop_token get_token() const noexcept;
  bool request_stop() noexcept;
  bool stop_requested() const noexcept;
};
```

- 戻り値: `request_stop()` は、初めて合図を出したなら `true`
- 計算量: O(1)

```cpp
#include <print>
#include <stop_token>

int main() {
  std::stop_source source;
  std::stop_token token = source.get_token();

  std::println("合図の前: {}", token.stop_requested());
  source.request_stop();
  std::println("合図の後: {}", token.stop_requested());
}
```

```text title="実行結果"
合図の前: false
合図の後: true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 複数のスレッドをまとめて止める | 同じ `stop_source` の token を全員に渡す |

## よくあるミス

??? failure "token を渡す前に request_stop する"
    渡す時点で合図は出ているので、受け取ったスレッドはすぐ止まります。順序に注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stop_token`](stop_token.md) | 受け取る側 |
| [`std::jthread`](jthread.md) | 内部で持っている |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 合図を出す側
    - [x] `get_token()` で受け取る側を作る
    - [x] `request_stop()` は何度呼んでもよい

## 関連ページ

- [cpprefjp: std::stop_source](https://cpprefjp.github.io/reference/stop_token/stop_source.html)
- [cppreference: std::stop_source](https://en.cppreference.com/w/cpp/thread/stop_source)
