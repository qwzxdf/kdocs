---
title: std::kill_dependency
summary: "メモリ順序の依存関係をここで断ち切る。"
order: 900
tags:
  - 並行処理
---

# std::kill_dependency

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`memory_order_consume` は、「この読み込みの値に依存する操作」だけを順序付ける、弱い順序です。依存の連鎖を、途中で切りたいときに使うのが `std::kill_dependency` です。ただし、`consume` は、コンパイラが実装しきれていないため、実際には `acquire` として扱われます。

!!! tip "ポイント"
    - `consume` の依存の連鎖を、この値で打ち切る
    - 引数の値を、そのまま返す
    - 現在は `consume` が `acquire` 扱いなので、実質的な効果はない
    - C++26 で `consume` の仕様自体が見直される予定

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::kill_dependency {#kill_dependency}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
T kill_dependency(T y) noexcept;
```

`memory_order_consume` で読んだ値から、別の操作へ依存が伝わる範囲を、コンパイラは追跡して、最適化に使います。`kill_dependency` で包むと、その値から先の依存は、追跡されなくなります。

`consume` は、ポインターを読んでから、その指す先を読むような、データ依存のある場面で、`acquire` より軽い順序を実現するためのものでした。しかし、主要なコンパイラは、依存を追跡する実装をあきらめ、`consume` を `acquire` に格上げしています。

そのため、新しいコードで `consume` や `kill_dependency` を使う理由はありません。`acquire` を使います。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>

int main() {
  std::atomic<int> a{5};

  const int v = a.load(std::memory_order_consume);
  // v からの依存を切る
  const int w = std::kill_dependency(v);

  std::println("{} {}", v, w);
}
```

```text title="実行結果"
5 5
```

## ゲームでの使いどころ

古い資料やライブラリのコードで見かけます。新しく書くことはありません。

## よくあるミス

??? failure "consume を使う"
    実質 `acquire` です。最初から `acquire` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memory_order`](memory_order.md) | 順序の一覧 |
| [`atomic_load_explicit`](atomic_load_explicit.md) | 読み込み |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::kill_dependency](https://cpprefjp.github.io/reference/atomic/kill_dependency.html)
- [cppreference: std::kill_dependency](https://en.cppreference.com/w/cpp/atomic/kill_dependency)
