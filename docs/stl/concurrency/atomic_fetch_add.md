---
title: std::atomic_fetch_add
summary: "アトミックに加算し、加算前の値を返す。"
order: 900
tags:
  - 並行処理
---

# std::atomic_fetch_add

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

複数のスレッドが同じカウンターを `++` すると、読み込み・加算・書き込みの途中で割り込まれて、更新が失われます。`std::atomic<int>` の `fetch_add(n)` は、この 3 つを分割できない 1 つの操作として行い、加算する前の値を返します。自由関数の `std::atomic_fetch_add(&a, n)` は、同じ働きのC 互換の書き方です。

!!! tip "ポイント"
    - 加算を不可分に行い、加算前の値を返す
    - メンバー関数 `a.fetch_add(n)` と同じ。普通はメンバー関数を使う
    - メモリ順序の指定版は `atomic_fetch_add_explicit`
    - 整数とポインターの `atomic` に使える

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_fetch_add {#atomic_fetch_add}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
T atomic_fetch_add(std::atomic<T>* obj, typename std::atomic<T>::difference_type arg) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `obj` | `std::atomic<T>*` | 対象 |
| `arg` | 加算する値 | 足す値 |

戻り値は、加算する前の値です。`++a` のように、加算後の値が欲しいときは、`a.fetch_add(1) + 1` と書くか、`a += 1` を使います。

ポインターの `atomic<T*>` では、`arg` は要素の個数で、アドレスは `sizeof(T) * arg` 進みます。

既定のメモリ順序は `memory_order_seq_cst`（最も強い順序）です。単なるカウンターで、他のデータの順序を気にしないなら、`memory_order_relaxed` の `explicit` 版を使うと、速くなります。

浮動小数点数の `atomic` にも、C++20 から `fetch_add` が使えます。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::atomic<int> counter{0};

  std::vector<std::thread> threads;
  for (int t = 0; t < 4; ++t) {
    threads.emplace_back([&counter] {
      for (int i = 0; i < 1000; ++i) std::atomic_fetch_add(&counter, 1);
    });
  }
  for (auto& th : threads) th.join();
  std::println("合計: {}", counter.load());

  // 戻り値は加算前の値
  std::atomic<int> a{10};
  const int before = std::atomic_fetch_add(&a, 5);
  std::println("加算前 {} 加算後 {}", before, a.load());
}
```

```text title="実行結果"
合計: 4000
加算前 10 加算後 15
```

## ゲームでの使いどころ

全スレッドが共有する、統計のカウンター（処理したジョブの数、確保した数）に使います。

## よくあるミス

??? failure "通常の int を ++ する"
    データ競合で、更新が失われます。

??? failure "戻り値を加算後の値だと思う"
    加算前の値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_fetch_sub`](atomic_fetch_sub.md) | 減算 |
| [`atomic`](atomic.md) | 本体 |
| [`atomic_load_explicit`](atomic_load_explicit.md) | メモリ順序を指定して読む |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_fetch_add](https://cpprefjp.github.io/reference/atomic/atomic_fetch_add.html)
- [cppreference: std::atomic_fetch_add](https://en.cppreference.com/w/cpp/atomic/atomic_fetch_add)
