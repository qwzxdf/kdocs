---
title: std::defer_lock
summary: "unique_lock に「まだロックしない」と伝える目印。"
order: 900
tags:
  - 並行処理
---

# std::defer_lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::unique_lock` は、構築のときにロックするのが普通ですが、「ロックの準備だけして、今はロックしない」ことができます。`std::defer_lock` は、そのための印です。あとで `lock()` を呼ぶか、`std::lock` に複数まとめて渡します。

!!! tip "ポイント"
    - `unique_lock(m, std::defer_lock)` は、ロックしないで作る
    - あとで `lk.lock()`、または `std::lock(lk1, lk2)` でロックする
    - `std::lock` と組み合わせると、デッドロックを避けて複数をロックできる
    - `lk.owns_lock()` で、ロック中かを調べられる

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::defer_lock {#defer_lock}

<span class="ver ver-11">C++11</span>

```cpp
struct defer_lock_t { explicit defer_lock_t() = default; };
inline constexpr std::defer_lock_t defer_lock{};
```

2 つのミューテックスを、別々のスレッドが逆の順でロックすると、お互いに待ち合って止まる（デッドロック）ことがあります。`std::lock(a, b)` は、デッドロックしない順序でロックします。その `std::lock` に渡すものとして、ロックを遅らせた `unique_lock` が使えます。

```cpp
std::unique_lock lk1(a, std::defer_lock);
std::unique_lock lk2(b, std::defer_lock);
std::lock(lk1, lk2);
```

スコープを抜けると、2 つとも自動で解放されます。

C++17 以降は、`std::scoped_lock` が同じことを 1 行でできます。ロックを途中で外したり、条件変数と組み合わせたりするときは、`unique_lock` と `defer_lock` が必要です。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::mutex a;
  std::mutex b;

  std::unique_lock<std::mutex> lk1(a, std::defer_lock);
  std::unique_lock<std::mutex> lk2(b, std::defer_lock);
  std::println("構築直後: {} {}", lk1.owns_lock(), lk2.owns_lock());

  std::lock(lk1, lk2);  // 2 つを、デッドロックせずにロック
  std::println("ロック後: {} {}", lk1.owns_lock(), lk2.owns_lock());
}
```

```text title="実行結果"
構築直後: false false
ロック後: true true
```

## ゲームでの使いどころ

2 つのオブジェクトの間で、データを移すときに、両方のミューテックスをロックするのに使います。

## よくあるミス

??? failure "ロックしたつもりで共有データを触る"
    `defer_lock` で作っただけでは、ロックされていません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`adopt_lock`](adopt_lock.md) | ロック済みを引き継ぐ |
| [`try_to_lock`](try_to_lock.md) | ロックを試す |
| [`lock`](lock.md) | 複数を同時にロック |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::defer_lock](https://cpprefjp.github.io/reference/mutex/defer_lock.html)
- [cppreference: std::defer_lock](https://en.cppreference.com/w/cpp/thread/lock_tag)
