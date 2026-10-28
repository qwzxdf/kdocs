---
title: std::atomic_thread_fence
summary: "スレッド間のメモリ順序を、変数なしで強制する柵（フェンス）。"
order: 900
tags:
  - 並行処理
---

# std::atomic_thread_fence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`atomic` 変数の読み書きに順序を付ける代わりに、独立した「柵」を置いて、その前後のメモリ操作の順序を固定します。`release` の柵の前の書き込みは、`acquire` の柵の後の読み込みから見えるようになります。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_thread_fence {#atomic_thread_fence}

```cpp
void atomic_thread_fence(std::memory_order order) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `order` | memory_order | 柵の強さ |

- 戻り値: なし
- 計算量: 定数（アトミック命令）


## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  int data = 0;
  std::atomic<bool> ready{false};
  std::thread producer([&] {
    data = 42;
    std::atomic_thread_fence(std::memory_order_release);
    ready.store(true, std::memory_order_relaxed);
  });
  std::thread consumer([&] {
    while (!ready.load(std::memory_order_relaxed)) {
    }
    std::atomic_thread_fence(std::memory_order_acquire);
    std::println("{}", data);
  });
  producer.join();
  consumer.join();
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 細かい同期の最適化 |

## よくあるミス

??? failure "柵の置き場所を間違える"
    柵は、フラグの書き込み・読み込みを挟む位置に置かないと、順序が守られません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memory_order`](memory_order.md) | 順序の種類 |
| [`atomic_signal_fence`](atomic_signal_fence.md) | シグナルハンドラとの間 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スレッド間のメモリ順序を変数なしで強制する柵（フェンス）
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_thread_fence](https://cpprefjp.github.io/reference/atomic/atomic_thread_fence.html)
- [cppreference: std::atomic_thread_fence](https://en.cppreference.com/w/cpp/atomic/atomic_thread_fence)
