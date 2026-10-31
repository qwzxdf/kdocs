---
title: std::lock
summary: "複数の mutex を、デッドロックしないように同時にかける関数。"
order: 86
tags:
  - 並行処理
---

# std::lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

2 つのミューテックスを、別々のスレッドが逆の順番でロックすると、お互いに相手を待って止まります（デッドロック）。`std::lock(m1, m2, ...)` は、デッドロックしないアルゴリズムで、全部のミューテックスを同時にロックします。

!!! tip "ポイント"
    - 複数のミューテックスを、デッドロックせずにロックする
    - 取れるまで待つ
    - 解放は呼び出し側の責任。`adopt_lock` で `lock_guard` に渡す
    - C++17 以降は `std::scoped_lock` が同じことをする

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::lock {#lock}

<span class="ver ver-11">C++11</span>

```cpp
template <class L1, class L2, class... Ln>
void lock(L1& l1, L2& l2, Ln&... ln);
```

実装は、1 つをロックし、残りを `try_lock` して、失敗したら全部を戻してやり直す、といった方法です。どのスレッドから、どの順序で渡しても、デッドロックしません。

途中で例外が出ると、取ったロックを解放してから例外を伝えます。

```cpp
std::lock(a, b);
std::lock_guard<std::mutex> ga(a, std::adopt_lock);
std::lock_guard<std::mutex> gb(b, std::adopt_lock);
```

C++17 の `std::scoped_lock lock(a, b);` が、これを 1 つにまとめた書き方です。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>
#include <thread>

int main() {
  std::mutex a;
  std::mutex b;
  int total = 0;

  // 逆の順番でロックしても、デッドロックしない
  auto work1 = [&] {
    for (int i = 0; i < 1000; ++i) {
      std::lock(a, b);
      std::lock_guard<std::mutex> ga(a, std::adopt_lock);
      std::lock_guard<std::mutex> gb(b, std::adopt_lock);
      ++total;
    }
  };
  auto work2 = [&] {
    for (int i = 0; i < 1000; ++i) {
      std::lock(b, a);
      std::lock_guard<std::mutex> gb(b, std::adopt_lock);
      std::lock_guard<std::mutex> ga(a, std::adopt_lock);
      ++total;
    }
  };

  std::thread t1(work1);
  std::thread t2(work2);
  t1.join();
  t2.join();
  std::println("{}", total);
}
```

```text title="実行結果"
2000
```

## ゲームでの使いどころ

2 つのオブジェクトを同時に更新するときに、両方のミューテックスをロックするのに使います。

## よくあるミス

??? failure "lock を使わず、別々に lock する"
    逆順のスレッドがあるとデッドロックします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`scoped_lock`](scoped_lock.md) | C++17 の簡単な書き方 |
| [`try_lock`](try_lock.md) | 待たない版 |
| [`adopt_lock`](adopt_lock.md) | 引き継ぐ印 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::lock](https://cpprefjp.github.io/reference/mutex/lock.html)
- [cppreference: std::lock](https://en.cppreference.com/w/cpp/thread/lock)
