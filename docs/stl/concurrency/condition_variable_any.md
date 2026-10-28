---
title: std::condition_variable_any
summary: "どんな種類の鍵とも組み合わせられる条件変数。"
order: 100
tags:
  - 並行処理
---

# std::condition_variable_any

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <condition_variable>`
</div>

`std::condition_variable_any` は、[`std::condition_variable`](condition_variable.md) と同じ「条件が満たされるまで待つ」道具ですが、**`std::unique_lock<std::mutex>` 以外の鍵（`shared_lock`、自作の鍵）とも組み合わせられます**。そのぶん少し重いので、`std::mutex` と使うなら普通の `condition_variable` を使います。C++20 では、`stop_token` を渡して、停止の合図で待ちをやめることもできます。

!!! tip "ポイント"
    - 普通は `condition_variable` で足りる。
    - `shared_mutex` の `shared_lock` と組み合わせたいときなどに使う。
    - C++20 の `wait(lock, stop_token, 条件)` で、停止の合図に応じて待ちを抜けられる。

!!! info "このページを読む前に"
    [`std::condition_variable`](condition_variable.md) を先に読んでください。

## 関数の詳しい説明

### std::condition_variable_any {#condition_variable_any}

```cpp
class condition_variable_any;
```

- `std::unique_lock<std::mutex>` 以外のロックでも使える版。C++20 では `std::stop_token` を渡して「止める合図が来たら起きる」こともできます

## 実際に動かしてみる

```cpp
#include <condition_variable>
#include <mutex>
#include <print>
#include <shared_mutex>
#include <thread>

int main() {
  std::shared_mutex m;
  std::condition_variable_any cv;
  bool ready = false;

  std::thread t([&] {
    std::unique_lock lock(m);
    ready = true;
    cv.notify_one();
  });

  {
    std::unique_lock lock(m);
    cv.wait(lock, [&] { return ready; });  // shared_mutex の unique_lock でも待てる
  }
  t.join();
  std::println("ready");
}
```

```text title="実行結果"
ready
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `jthread` のワーカーを停止の合図で起こして終了させる | `cv.wait(lock, stop_token, 条件)` |

## よくあるミス

??? failure "condition_variable で足りるのに使う"
    `std::mutex` と使うなら、普通の `condition_variable` のほうが軽いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::condition_variable`](condition_variable.md) | `unique_lock<mutex>` 専用で軽い |
| [`std::stop_token`](stop_token.md) | 停止の合図 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] どんな鍵とも使える条件変数
    - [x] 少し重い
    - [x] C++20 で `stop_token` に対応

## 関連ページ

- [cpprefjp: std::condition_variable_any](https://cpprefjp.github.io/reference/condition_variable/condition_variable_any.html)
- [cppreference: std::condition_variable_any](https://en.cppreference.com/w/cpp/thread/condition_variable_any)
