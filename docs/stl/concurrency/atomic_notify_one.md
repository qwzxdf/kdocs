---
title: std::atomic_notify_one
summary: "atomic_wait で待っているスレッドを 1 つ起こす。"
order: 900
tags:
  - 並行処理
---

# std::atomic_notify_one

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <atomic>`
</div>

`atomic_wait` で眠っているスレッドを起こすのが、`atomic_notify_one(&a)` です。待っているスレッドのうち、1 つだけを起こします。値を変えたあとに呼びます。

!!! tip "ポイント"
    - `atomic_wait` で眠っているスレッドのうち、1 つを起こす
    - 値を変えてから呼ぶ。順序を逆にすると、起きたときに値がまだ古い
    - 誰も待っていなければ、何も起きない
    - 複数のスレッドを起こすなら `atomic_notify_all`

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_notify_one {#atomic_notify_one}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
void atomic_notify_one(std::atomic<T>* obj) noexcept;
```

どのスレッドが起きるかは、規定されていません。1 つのタスクを 1 つのワーカーに渡す設計に向きます。

通知を取りこぼさない手順は、(1) 値を変える、(2) 通知する、の順です。待つ側は、値が変わったかを見てから眠るため、この順なら、取りこぼしが起きません。

誰も待っていないときの呼び出しは、安価な実装になっています。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  std::atomic<int> tasks{0};

  std::thread worker([&] {
    std::atomic_wait(&tasks, 0);  // 仕事が来るまで眠る
    std::println("仕事 {} 件を受け取った", tasks.load());
  });

  tasks.store(3);                   // 先に値を変える
  std::atomic_notify_one(&tasks);   // 次に通知する
  worker.join();
}
```

```text title="実行結果"
仕事 3 件を受け取った
```

## ゲームでの使いどころ

ジョブ キューに仕事を足したとき、待っているワーカーを 1 つだけ起こします。

## よくあるミス

??? failure "通知を先にして、値を後で変える"
    起きたワーカーが、古い値を見て、また眠ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_notify_all`](atomic_notify_all.md) | 全員を起こす |
| [`atomic_wait`](atomic_wait.md) | 待つ側 |
| [`condition_variable`](condition_variable.md) | 条件変数 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_notify_one](https://cpprefjp.github.io/reference/atomic/atomic_notify_one.html)
- [cppreference: std::atomic_notify_one](https://en.cppreference.com/w/cpp/atomic/atomic_notify_one)
