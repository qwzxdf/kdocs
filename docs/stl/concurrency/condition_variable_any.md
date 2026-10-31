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

`std::condition_variable` は、`std::unique_lock<std::mutex>` でしか待てません。`std::condition_variable_any` は、`lock()` と `unlock()` を持つものなら何でも使えます。共有ロック（`shared_lock`）や、自作のロック型でも待てます。C++20 では、`stop_token` による中断にも対応しています。

!!! tip "ポイント"
    - `lock` / `unlock` を持つ、任意のロック型で待てる
    - `std::condition_variable` より少し遅い
    - `stop_token` を渡して、待ちを中断できる（C++20）
    - 通常の `std::mutex` なら `condition_variable` を使う

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::condition_variable_any {#condition_variable_any}

<span class="ver ver-11">C++11</span>

```cpp
class condition_variable_any {
 public:
  void notify_one() noexcept;
  void notify_all() noexcept;
  template <class Lock> void wait(Lock& lock);
  template <class Lock, class Pred> void wait(Lock& lock, Pred pred);
  template <class Lock, class Pred>
  bool wait(Lock& lock, std::stop_token st, Pred pred);          // C++20
};
```

`wait` はロックを解放して眠り、起きたらロックを取り直します。この解放と取り直しを、渡された `Lock` の `unlock()` / `lock()` で行います。

C++20 の `stop_token` つきの `wait` は、`jthread` と組み合わせて、スレッドの終了要求で待ちを抜ける、という使い方に向いています。戻り値は、`pred` が真になって抜けたかです。

`std::condition_variable` は、`std::mutex` の `unique_lock` 専用に最適化されているため、`std::mutex` だけで足りるなら、そちらが速くなります。

## 実際に動かしてみる

```cpp
#include <condition_variable>
#include <mutex>
#include <print>
#include <thread>

int main() {
  std::mutex m;
  std::condition_variable_any cv;
  bool ready = false;

  std::thread waiter([&] {
    std::unique_lock<std::mutex> lock(m);
    cv.wait(lock, [&] { return ready; });  // 条件が成り立つまで待つ
    std::println("起きた");
  });

  {
    std::lock_guard<std::mutex> g(m);
    ready = true;
  }
  cv.notify_one();
  waiter.join();
}
```

```text title="実行結果"
起きた
```

## ゲームでの使いどころ

`stop_token` で終了要求を受けながら待つワーカー スレッドで使います。

## よくあるミス

??? failure "通知を先にして、条件を後で変える"
    起きたスレッドが条件を見て、また眠ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`condition_variable`](condition_variable.md) | `std::mutex` 専用の速い版 |
| [`jthread`](jthread.md) | `stop_token` と組み合わせる |
| [`shared_lock`](shared_lock.md) | 待てるロック型の例 |

## コンパイラ対応

C++11 から使えます。`stop_token` つきは C++20 から。

## 関連ページ

- [cpprefjp: std::condition_variable_any](https://cpprefjp.github.io/reference/condition_variable/condition_variable_any.html)
- [cppreference: std::condition_variable_any](https://en.cppreference.com/w/cpp/thread/condition_variable_any)
