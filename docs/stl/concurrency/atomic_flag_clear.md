---
title: std::atomic_flag_clear
summary: "atomic_flag を下ろす。"
order: 900
tags:
  - 並行処理
---

# std::atomic_flag_clear

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

スピンロックを取った側が、解放するときに呼ぶのが `atomic_flag_clear` です。フラグを `false` に戻して、他のスレッドが `test_and_set` で取れるようにします。

!!! tip "ポイント"
    - フラグを `false` にする
    - ロックの解放に使うときは `memory_order_release`
    - メンバー関数 `flag.clear(order)` と同じ
    - `acquire` や `acq_rel` は指定できない

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_flag_clear {#atomic_flag_clear}

<span class="ver ver-11">C++11</span>

```cpp
void atomic_flag_clear(std::atomic_flag* obj) noexcept;
void atomic_flag_clear_explicit(std::atomic_flag* obj, std::memory_order order) noexcept;
```

`release` で解放すると、臨界区間の中での書き込みが、次に `acquire` で取ったスレッドから見えるようになります。取る側は `test_and_set(acquire)`、解放する側は `clear(release)` と組にします。

C++20 から、`wait` / `notify_one` / `notify_all` もあります。ロックが取れるまで眠らせる実装に、拡張できます。

臨界区間の途中で例外が出ると、`clear` が呼ばれないまま抜けます。そのため、`lock_guard` のように、デストラクターで `clear` を呼ぶ、自作のラッパーにするのが普通です。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

class SpinLock {
 public:
  void lock() {
    while (flag_.test_and_set(std::memory_order_acquire)) {
    }
  }
  void unlock() { flag_.clear(std::memory_order_release); }

 private:
  std::atomic_flag flag_ = ATOMIC_FLAG_INIT;
};

int main() {
  SpinLock lock;
  int counter = 0;

  auto work = [&] {
    for (int i = 0; i < 10000; ++i) {
      lock.lock();
      ++counter;
      lock.unlock();
    }
  };
  std::thread a(work);
  std::thread b(work);
  a.join();
  b.join();
  std::println("{}", counter);
}
```

```text title="実行結果"
20000
```

## ゲームでの使いどころ

ごく短い排他区間を守る自作のスピンロックで使います。

## よくあるミス

??? failure "unlock を忘れる"
    他のスレッドが永久に回り続けます。ラッパーで自動化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_flag_test_and_set`](atomic_flag_test_and_set.md) | フラグを立てる |
| [`atomic_flag`](atomic_flag.md) | 本体 |
| [`lock_guard`](lock_guard.md) | ロックの自動解放 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_flag_clear](https://cpprefjp.github.io/reference/atomic/atomic_flag_clear.html)
- [cppreference: std::atomic_flag_clear](https://en.cppreference.com/w/cpp/atomic/atomic_flag_clear)
