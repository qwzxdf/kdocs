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

`atomic` の操作に順序を付けるのではなく、操作とは独立に、メモリの順序の壁（フェンス）を置く関数が `atomic_thread_fence` です。フェンスの前後で、メモリ操作の並べ替えを制限します。

!!! tip "ポイント"
    - メモリ順序の壁を置く。操作を伴わない
    - `release` フェンスより前の書き込みは、あとの `atomic` 書き込みより先に見える
    - `acquire` フェンスより後の読み込みは、前の `atomic` 読み込みより先に移動しない
    - 通常は `atomic` の操作に順序を付けるほうが分かりやすい

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_thread_fence {#atomic_thread_fence}

<span class="ver ver-11">C++11</span>

```cpp
void atomic_thread_fence(std::memory_order order) noexcept;
```

| `order` | 効果 |
| --- | --- |
| `acquire` | このフェンス以降の読み書きが、前に移動しない |
| `release` | このフェンス以前の読み書きが、後ろに移動しない |
| `acq_rel` | 両方 |
| `seq_cst` | 全体で一貫した順序 |

`relaxed` の `atomic` 操作の前後にフェンスを置いて、同期を作る使い方があります。ロック フリーのデータ構造の実装で、複数の `atomic` に対して、フェンスを 1 回で済ませたいときです。

読み書きの順序は、CPU の種類で、保証の強さが違います。x86 は強く、ARM は弱いので、フェンスの必要性が違います。標準のモデルに従って書けば、どちらでも正しく動きます。

プログラムを書く前に、まず `mutex` や `atomic` の既定の順序で足りないか、考えます。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

int data = 0;
std::atomic<bool> ready{false};

int main() {
  std::thread producer([] {
    data = 42;
    std::atomic_thread_fence(std::memory_order_release);   // 以前の書き込みを確定させる
    ready.store(true, std::memory_order_relaxed);
  });

  while (!ready.load(std::memory_order_relaxed)) {
  }
  std::atomic_thread_fence(std::memory_order_acquire);     // 以降の読み込みを遅らせる
  std::println("{}", data);
  producer.join();
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

ロック フリーの自作データ構造で、フェンスを 1 回で済ませる最適化に使います。普通は不要です。

## よくあるミス

??? failure "フェンスだけで同期できると思う"
    `atomic` の操作と組み合わせて、初めて意味があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_signal_fence`](atomic_signal_fence.md) | 同じスレッド内の割り込み用 |
| [`memory_order`](memory_order.md) | 順序の一覧 |
| [`atomic_store_explicit`](atomic_store_explicit.md) | 操作に順序を付ける |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_thread_fence](https://cpprefjp.github.io/reference/atomic/atomic_thread_fence.html)
- [cppreference: std::atomic_thread_fence](https://en.cppreference.com/w/cpp/atomic/atomic_thread_fence)
