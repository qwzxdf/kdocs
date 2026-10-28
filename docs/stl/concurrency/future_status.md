---
title: std::future_status
summary: "future の待機の結果（準備完了・時間切れ・遅延）を表す列挙型。"
order: 900
tags:
  - 並行処理
---

# std::future_status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`future::wait_for(時間)` は、結果が準備できた、時間切れ、まだ始まっていない（遅延）のどれかを `future_status` で返します。結果が出たかをポーリングしたいときに使います。

!!! tip "ポイント"
    - `ready`: 結果が出た。
    - `timeout`: 時間切れ。
    - `deferred`: `launch::deferred` で、まだ実行されていない。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::future_status {#future_status}

```cpp
enum class future_status { ready, timeout, deferred };
```

- 戻り値: なし（列挙型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <chrono>
#include <future>
#include <print>

int main() {
  using namespace std::chrono_literals;
  auto f = std::async(std::launch::deferred, [] { return 1; });
  std::println("{}", f.wait_for(0s) == std::future_status::deferred);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ロード中を別の画面表示でつなぐ | `if (f.wait_for(0s) == std::future_status::ready) { ... }` |

## よくあるミス

??? failure "`deferred` を忘れる"
    `launch::deferred` の `future` は、`wait_for` が常に `deferred` を返します。`get()` するまで動きません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future`](future.md) | 結果を受け取る |
| [`launch`](launch.md) | 実行方法 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] future の待機の結果
    - [x] ready / timeout / deferred
    - [x] 0 秒で wait_for するとポーリング

## 関連ページ

- [cpprefjp: std::future_status](https://cpprefjp.github.io/reference/future/future_status.html)
- [cppreference: std::future_status](https://en.cppreference.com/w/cpp/thread/future_status)
