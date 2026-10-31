---
title: std::atomic_notify_all
summary: "atomic_wait で待っているスレッドを全部起こす。"
order: 900
tags:
  - 並行処理
---

# std::atomic_notify_all

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <atomic>`
</div>

`atomic_wait` で眠っている全てのスレッドを、まとめて起こすのが `atomic_notify_all(&a)` です。「開始の合図」「終了の通知」のように、全員が反応するべき変化に使います。

!!! tip "ポイント"
    - `atomic_wait` で眠っている全スレッドを起こす
    - 値を変えてから呼ぶ
    - 起きたスレッドは、各自で値を確かめる
    - 1 つだけ起こすなら `atomic_notify_one`

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_notify_all {#atomic_notify_all}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
void atomic_notify_all(std::atomic<T>* obj) noexcept;
```

全員を起こすので、起きたあとの競争（全員が同じ資源を取りに行く）で性能が落ちることがあります。仕事を 1 つ渡すだけなら、`notify_one` のほうが適切です。

「止まれ」の合図のように、全員が同じ反応をする場面では、`notify_all` を使います。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::atomic<int> go{0};
  std::atomic<int> started{0};

  std::vector<std::thread> workers;
  for (int i = 0; i < 3; ++i) {
    workers.emplace_back([&] {
      std::atomic_wait(&go, 0);  // 開始の合図を待つ
      started.fetch_add(1);
    });
  }

  go.store(1);
  std::atomic_notify_all(&go);  // 全員を起こす
  for (auto& w : workers) w.join();
  std::println("開始したスレッド: {}", started.load());
}
```

```text title="実行結果"
開始したスレッド: 3
```

## ゲームでの使いどころ

全ワーカーに、「開始」や「終了」の合図を送るときに使います。

## よくあるミス

??? failure "notify_one で全員を起こそうとする"
    1 つしか起きず、他は眠ったままです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_notify_one`](atomic_notify_one.md) | 1 つだけ起こす |
| [`atomic_wait`](atomic_wait.md) | 待つ側 |
| [`latch`](latch.md) | 使い捨ての合図 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_notify_all](https://cpprefjp.github.io/reference/atomic/atomic_notify_all.html)
- [cppreference: std::atomic_notify_all](https://en.cppreference.com/w/cpp/atomic/atomic_notify_all)
