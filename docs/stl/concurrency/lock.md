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

`std::lock` は、**複数の mutex をデッドロックしない順序でまとめてロックする**関数です。C++17 以降は [`std::scoped_lock`](scoped_lock.md) で足ります。古いコードや、`unique_lock` の `defer_lock` と組み合わせるときに使います。

!!! tip "ポイント"
    - `unique_lock` を `std::defer_lock`（ロックしない）で作ってから、`std::lock(a, b)`。
    - ロックしたあとの開け閉めは、`unique_lock` に任せる。
    - C++17 以降は `scoped_lock` が簡単。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::lock {#lock_function}

```cpp
template <class L1, class L2, class... Ln>
void lock(L1& l1, L2& l2, Ln&... ln);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l1, l2, ...` | ロック可能なもの | mutex や `unique_lock` |

- 戻り値: なし。全部のロックを取り終えるまで戻らない
- 計算量: デッドロックしない

```cpp
#include <mutex>
#include <print>

int main() {
  std::mutex a;
  std::mutex b;

  std::unique_lock la(a, std::defer_lock);  // まだロックしない
  std::unique_lock lb(b, std::defer_lock);
  std::lock(la, lb);                        // 2 つを同時に、デッドロックしないようにかける
  std::println("2 つとも取れた: {} {}", la.owns_lock(), lb.owns_lock());
}
```

```text title="実行結果"
2 つとも取れた: true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つの mutex を同時にロックする（C++14 以前） | `std::lock(a, b);` |

## よくあるミス

??? failure "個別に lock() を呼んで、順序が食い違う"
    スレッド A が `a, b`、スレッド B が `b, a` の順に取ろうとすると、デッドロックします。`std::lock` か `scoped_lock` で同時に取ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::scoped_lock`](scoped_lock.md) | C++17 以降はこちら |
| [`std::unique_lock`](unique_lock.md) | `defer_lock` で作る |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の mutex を同時にかける
    - [x] デッドロックしない
    - [x] C++17 以降は `scoped_lock`

## 関連ページ

- [cpprefjp: std::lock](https://cpprefjp.github.io/reference/mutex/lock.html)
- [cppreference: std::lock](https://en.cppreference.com/w/cpp/thread/lock)
