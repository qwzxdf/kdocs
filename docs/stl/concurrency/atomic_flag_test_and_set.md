---
title: std::atomic_flag_test_and_set
summary: "atomic_flag を立て、立てる前の状態を返す。"
order: 900
tags:
  - 並行処理
---

# std::atomic_flag_test_and_set

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`std::atomic_flag` は、真偽値を 1 つだけ持つ、最も単純な `atomic` です。`test_and_set` は、フラグを立てて、立てる前の値を返す操作で、スピンロック（ロックが取れるまで回し続ける）の土台になります。

!!! tip "ポイント"
    - フラグを立てて、立てる前の値を返す（不可分）
    - 前の値が `false` なら、自分が最初に立てた（ロックを取れた）
    - 解放は `clear`
    - `atomic_flag` は、必ずロックなしで動くことが保証される

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_flag_test_and_set {#atomic_flag_test_and_set}

<span class="ver ver-11">C++11</span>

```cpp
bool atomic_flag_test_and_set(std::atomic_flag* obj) noexcept;
bool atomic_flag_test_and_set_explicit(std::atomic_flag* obj, std::memory_order order) noexcept;
```

戻り値が `false` なら、その呼び出しがフラグを `false` から `true` にしたことを意味します。`true` なら、すでに誰かが立てていました。

スピンロックは、次の形です。

```cpp
while (flag.test_and_set(std::memory_order_acquire)) {
  // 取れるまで回る
}
// 臨界区間
flag.clear(std::memory_order_release);
```

スピンロックは、待ち時間が極めて短い場面でだけ有効です。待ちが長いと、CPU を無駄に使います。普通は `std::mutex` を使います。

C++20 から、`test()` というメンバー関数で、立てずに読むこともできます。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic_flag flag = ATOMIC_FLAG_INIT;

  std::println("1 回目: 前の値 {}", flag.test_and_set());  // false: 自分が立てた
  std::println("2 回目: 前の値 {}", flag.test_and_set());  // true: すでに立っている

  flag.clear();
  std::println("解除後: 前の値 {}", flag.test_and_set());
}
```

```text title="実行結果"
1 回目: 前の値 false
2 回目: 前の値 true
解除後: 前の値 false
```

## ゲームでの使いどころ

一度だけ実行したい初期化の判定や、短い排他区間のスピンロックに使います。

## よくあるミス

??? failure "長い処理をスピンロックで守る"
    CPU を使い続けます。`mutex` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_flag_clear`](atomic_flag_clear.md) | フラグを下ろす |
| [`atomic_flag`](atomic_flag.md) | 本体 |
| [`mutex`](mutex.md) | 普通のロック |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_flag_test_and_set](https://cpprefjp.github.io/reference/atomic/atomic_flag_test_and_set.html)
- [cppreference: std::atomic_flag_test_and_set](https://en.cppreference.com/w/cpp/atomic/atomic_flag_test_and_set)
