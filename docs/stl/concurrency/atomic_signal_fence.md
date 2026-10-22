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

`atomic_thread_fence` はスレッド間の順序ですが、`atomic_signal_fence` は同じスレッドの中で、通常の処理とシグナルハンドラの間の順序を固定します。CPU 命令は出さず、コンパイラの並べ替えだけを防ぎます。

!!! tip "ポイント"
    - `std::atomic` のメンバ関数と同じ働きの、自由関数版。
    - ふつうはメンバ関数のほうが読みやすい。
    - C 言語との互換のためにある。

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_signal_fence {#atomic_signal_fence}

```cpp
void atomic_signal_fence(std::memory_order order) noexcept;
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

int main() {
  // 例: シグナルハンドラと本体の間で、書き込みの順序を保つ
  std::atomic_signal_fence(std::memory_order_seq_cst);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | シグナルハンドラとの順序を保つ |

## よくあるミス

??? failure "スレッド間の同期に使う"
    スレッド間には効きません。`atomic_thread_fence` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_thread_fence`](atomic_thread_fence.md) | スレッド間の柵 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じスレッドの中の、シグナルハンドラとの間の順序を強制する柵
    - [x] `std::atomic` のメンバ関数と同じ働きの、自由関数版
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atomic_signal_fence](https://cpprefjp.github.io/reference/atomic/atomic_signal_fence.html)
- [cppreference: std::atomic_signal_fence](https://en.cppreference.com/w/cpp/atomic/atomic_signal_fence)
