---
title: std::this_thread::yield
summary: "他のスレッドに、実行の順番を譲る。"
order: 77
group: this_thread
tags:
  - 並行処理
---

# std::this_thread::yield

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <thread>`
</div>

ほかのスレッドの結果を待つために、フラグを調べ続けるループ（スピン）を書くと、そのスレッドが CPU を独占して、待たれている側の実行が遅れます。`std::this_thread::yield()` は、「いまの CPU の割り当てを、他のスレッドに譲ってよい」とスケジューラーに伝えます。

!!! tip "ポイント"
    - 現在のスレッドが、実行の順番を譲る
    - 待ち合わせのスピン ループの中で、CPU の無駄遣いを和らげる
    - 効果は OS 次第。何も起きないこともある
    - 長く待つなら、`mutex` や条件変数で眠らせる

!!! info "このページを読む前に"
    [`std::thread`](../thread.md) を先に読んでください。

## 関数の詳しい説明

### std::this_thread::yield {#yield}

<span class="ver ver-11">C++11</span>

```cpp
void yield() noexcept;
```

あくまでヒントで、実際にスレッドが切り替わるかは、OS が決めます。ほかに実行できるスレッドがなければ、すぐ戻ります。

`yield` を挟んだスピン ループは、純粋に回し続けるよりは CPU に優しくなりますが、それでも CPU を使い続けます。待ち時間が分からない、または長いなら、`std::condition_variable` や `atomic::wait` で眠らせるほうが適切です。

ごく短い待ち（数マイクロ秒）で、眠らせる切り替えのコストが見合わないときに、`yield` つきのスピンが選ばれます。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  std::atomic<bool> ready{false};

  std::thread worker([&] {
    ready.store(true);
  });

  // 準備ができるまで、CPU を譲りながら待つ
  while (!ready.load()) {
    std::this_thread::yield();
  }
  std::println("準備完了");
  worker.join();
}
```

```text title="実行結果"
準備完了
```

## ゲームでの使いどころ

ごく短い待ち合わせで使います。長く待つなら、眠らせる仕組みに替えます。

## よくあるミス

??? failure "yield のスピンで長く待つ"
    CPU を使い続けます。`atomic::wait` や条件変数にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sleep_for`](sleep_for.md) | 一定時間眠る |
| [`get_id`](get_id.md) | スレッド ID |
| [`atomic_wait`](../atomic_wait.md) | 眠って待つ |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::this_thread::yield](https://cpprefjp.github.io/reference/thread/this_thread/yield.html)
- [cppreference: std::this_thread::yield](https://en.cppreference.com/w/cpp/thread/yield)
