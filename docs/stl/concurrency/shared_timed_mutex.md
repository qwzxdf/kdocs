---
title: std::shared_timed_mutex
summary: "読み取りは同時に、書き込みは 1 つだけで、時間切れも指定できるミューテックス。"
order: 900
tags:
  - 並行処理
---

# std::shared_timed_mutex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <shared_mutex>`
</div>

`shared_mutex`（複数のスレッドが同時に読めるロック）にロックの待ち時間を指定する機能を足したものです。C++14 で登場しましたが、C++17 の `shared_mutex` のほうが軽いので、時間指定が必要なときだけ使います。

!!! tip "ポイント"
    - `lock_shared()` で読み取りロック、`lock()` で書き込みロック。
    - `try_lock_for` / `try_lock_shared_for` で待ち時間を指定する。
    - 時間指定が不要なら [`shared_mutex`](shared_mutex.md)。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::shared_timed_mutex {#shared_timed_mutex}

```cpp
class shared_timed_mutex {
 public:
  void lock();
  void lock_shared();
  template <class Rep, class Period> bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& d);
  void unlock();
  void unlock_shared();
};
```

- 戻り値: `try_lock_*_for` はロックできたら `true`
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <shared_mutex>

int main() {
  using namespace std::chrono_literals;
  std::shared_timed_mutex m;
  m.lock_shared();
  std::println("{}", m.try_lock_shared_for(10ms));  // 読み取りは同時にできる
  m.unlock_shared();
  m.unlock_shared();
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み取りが多く、時間切れも必要な設定データ | `std::shared_lock lk(m, 10ms);` |

## よくあるミス

??? failure "読み取りロックで書き込む"
    `lock_shared()` で取ったロックの間は、データを書き換えてはいけません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`shared_mutex`](shared_mutex.md) | 時間指定なし |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読み書きロック + 時間切れ
    - [x] shared が読み取り
    - [x] 時間指定が不要なら shared_mutex

## 関連ページ

- [cpprefjp: std::shared_timed_mutex](https://cpprefjp.github.io/reference/shared_mutex/shared_timed_mutex.html)
- [cppreference: std::shared_timed_mutex](https://en.cppreference.com/w/cpp/thread/shared_timed_mutex)
