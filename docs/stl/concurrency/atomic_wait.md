---
title: std::atomic_wait
summary: "値が変わるまで、アトミックに待つ。"
order: 900
tags:
  - 並行処理
---

# std::atomic_wait

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <atomic>`
</div>

スレッドが、`atomic` の値が変わるのを待つとき、`while (a.load() == old) {}` と回し続けると、CPU を無駄に使います。C++20 の `std::atomic_wait(&a, old)` は、`a` の値が `old` から変わるまで、スレッドを眠らせます。別のスレッドが `notify_one` / `notify_all` で起こします。

!!! tip "ポイント"
    - 値が `old` のあいだ、スレッドを眠らせる
    - `notify_one` / `notify_all` で起こされる
    - 起きたら、値がまだ `old` かを確かめ直す（偽の目覚め）
    - メンバー関数 `a.wait(old)` と同じ

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_wait {#atomic_wait}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
void atomic_wait(const std::atomic<T>* obj, typename std::atomic<T>::value_type old) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | `const std::atomic<T>*` | 見る対象 |
| `old` | 値 | この値のあいだは待つ |

`obj` の値が `old` と等しければ眠り、通知（`notify`）で起きたとき、値が `old` でなければ戻ります。通知がなくても、起きることがあるので、実装は内部で値を確かめ直します。

`condition_variable` と違い、ミューテックスが要りません。軽量な待ち合わせに向きます。

値が `old` から別の値になり、また `old` に戻ると、待ちが外れない場合があります（ABA）。変化の回数を数えるカウンターを、値に使うなど、設計で避けます。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  std::atomic<int> state{0};

  std::thread waiter([&] {
    std::atomic_wait(&state, 0);  // 0 のあいだ眠る
    std::println("起きた: state = {}", state.load());
  });

  state.store(1);
  std::atomic_notify_one(&state);  // 起こす
  waiter.join();
}
```

```text title="実行結果"
起きた: state = 1
```

## ゲームでの使いどころ

ワーカー スレッドが、仕事が来るのを待つ、軽い同期に使います。待つ条件が複雑なら `condition_variable` です。

## よくあるミス

??? failure "通知を送らない"
    眠ったままになります。値を変えたら `notify` を呼びます。

??? failure "起きた後に値を確かめない"
    偽の目覚めで、条件が成立していないことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_notify_one`](atomic_notify_one.md) | 1 つ起こす |
| [`atomic_notify_all`](atomic_notify_all.md) | 全部起こす |
| [`condition_variable`](condition_variable.md) | 複雑な条件の待ち合わせ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_wait](https://cpprefjp.github.io/reference/atomic/atomic_wait.html)
- [cppreference: std::atomic_wait](https://en.cppreference.com/w/cpp/atomic/atomic_wait)
