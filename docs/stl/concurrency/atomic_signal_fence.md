---
title: std::atomic_signal_fence
summary: "同じスレッドの中の、シグナルハンドラとの間の順序を強制する柵。"
order: 900
tags:
  - 並行処理
---

# std::atomic_signal_fence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`atomic_thread_fence` が、スレッド間の順序を作るのに対し、`atomic_signal_fence` は、同じスレッドの中で、シグナル ハンドラーとの順序を作ります。CPU 命令のフェンスは出さず、コンパイラの並べ替えだけを防ぎます。

!!! tip "ポイント"
    - 同じスレッドと、そのスレッドのシグナル ハンドラーの間の順序
    - コンパイラの並べ替えだけを制限する。CPU のフェンス命令は出さない
    - スレッド間には効かない
    - 使う場面はほとんどない

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_signal_fence {#atomic_signal_fence}

<span class="ver ver-11">C++11</span>

```cpp
void atomic_signal_fence(std::memory_order order) noexcept;
```

シグナル ハンドラーは、メイン処理を中断して割り込みます。同じスレッドなので、CPU の並べ替えは問題になりませんが、コンパイラの最適化で、書き込みの順序が変わると、ハンドラーが中途半端な状態を見ます。

このフェンスで、コンパイラが操作を超えて並べ替えるのを防ぎます。`volatile sig_atomic_t` や、ロックフリーの `atomic` と組み合わせます。

マルチスレッドの同期には、使えません。`atomic_thread_fence` を使います。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <csignal>
#include <print>

volatile std::sig_atomic_t g_flag = 0;

int main() {
  // 順序をコンパイラに守らせる
  g_flag = 1;
  std::atomic_signal_fence(std::memory_order_seq_cst);
  const int snapshot = g_flag;

  std::println("{}", snapshot);
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

シグナル ハンドラーと共有するフラグの扱いで出てくることがあります。ゲームではほとんど使いません。

## よくあるミス

??? failure "スレッド間の同期に使う"
    効果がありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_thread_fence`](atomic_thread_fence.md) | スレッド間のフェンス |
| `std::sig_atomic_t` | シグナル ハンドラーと共有できる整数型 |
| [`memory_order`](memory_order.md) | 順序の一覧 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_signal_fence](https://cpprefjp.github.io/reference/atomic/atomic_signal_fence.html)
- [cppreference: std::atomic_signal_fence](https://en.cppreference.com/w/cpp/atomic/atomic_signal_fence)
