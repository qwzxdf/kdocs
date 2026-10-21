---
title: std::scoped_lock
summary: "複数の mutex を、デッドロックしないようにまとめてかける。"
order: 79
tags:
  - 並行処理
---

# std::scoped_lock

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-17">C++17</span>
`#include <mutex>`
</div>

`std::scoped_lock` は、**複数の mutex を、デッドロックしない順序でまとめてロックし、スコープを抜けるときに全部開ける**クラスです。2 つの mutex を別々の順序でロックすると、お互いに待ち合って止まる（デッドロック）ことがありますが、`scoped_lock` はそれを避けます。

!!! tip "ポイント"
    - mutex が 1 つでも `lock_guard` の代わりに使える（C++17 以降）。
    - 複数の mutex は、書く順序が違ってもデッドロックしない。
    - C++17 の機能。それ以前は `std::lock` + `lock_guard`。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::scoped_lock {#scoped_lock}

<span class="ver ver-17">C++17</span>

```cpp
template <class... Mutexes>
class scoped_lock {
 public:
  explicit scoped_lock(Mutexes&... m);
};
```

- 複数の mutex を、デッドロックしない順番でまとめてロックします。1 つでも使えるので、lock_guard の代わりに全部これでも構いません

```cpp
#include <mutex>
#include <print>

struct Account {
  int gold = 100;
  std::mutex mutex;
};

void Transfer(Account& from, Account& to, int amount) {
  std::scoped_lock lock(from.mutex, to.mutex);  // 2 つを同時に（順番を気にしなくていい）
  from.gold -= amount;
  to.gold += amount;
}

int main() {
  Account a;
  Account b;
  Transfer(a, b, 30);
  Transfer(b, a, 10);
  std::println("{} {}", a.gold, b.gold);
}
```

```text title="実行結果"
80 120
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つのオブジェクトの間でアイテムをやりとりする | `std::scoped_lock lock(a.mutex_, b.mutex_);` |

## よくあるミス

??? failure "古いコンパイラ"
    C++17 が必要です。使えないときは `std::lock(a, b)` のあとに `std::lock_guard(a, std::adopt_lock)` を並べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::lock_guard`](lock_guard.md) | 1 つの mutex |
| [`std::lock`](lock.md) | 複数の mutex を同時にかける関数 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の mutex をデッドロックなしでかける
    - [x] 1 つでも使える
    - [x] C++17

## 関連ページ

- [cpprefjp: std::scoped_lock](https://cpprefjp.github.io/reference/mutex/scoped_lock.html)
- [cppreference: std::scoped_lock](https://en.cppreference.com/w/cpp/thread/scoped_lock)
