---
title: std::adopt_lock
summary: "「すでにロック済みのミューテックスを引き取る」と伝える目印。"
order: 900
tags:
  - 並行処理
---

# std::adopt_lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

すでに自分でロックしたミューテックスを `lock_guard` や `unique_lock` に引き取らせて、スコープを抜けるときに解除させたいときに、`std::adopt_lock` を渡します。`std::lock` で複数を同時にロックしたあとに使います。

!!! tip "ポイント"
    - `std::adopt_lock_t` 型の定数。
    - `lock_guard`・`unique_lock`・`scoped_lock` のコンストラクタの第 2 引数に渡す。
    - デッドロックを避ける `std::lock` と組み合わせて使う。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::adopt_lock {#adopt_lock}

```cpp
struct adopt_lock_t { explicit adopt_lock_t() = default; };
inline constexpr adopt_lock_t adopt_lock{};
```

- 戻り値: なし（目印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::mutex m;
  m.lock();
  {
    std::lock_guard g(m, std::adopt_lock);
    std::println("adopted");
  }
}
```

```text title="実行結果"
adopted
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 複数のミューテックスを同時にロック | `std::lock(m1, m2);` のあと `std::lock_guard g1(m1, std::adopt_lock);` |

## よくあるミス

??? failure "目印とロックの状態が食い違う"
    `adopt_lock` は、すでにロックしていることが前提です。ロックしていないと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unique_lock`](unique_lock.md) | 柔軟なロック |
| [`lock_guard`](lock_guard.md) | 単純なロック |
| [`std::lock`](lock.md) | 複数を同時にロック |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「すでにロック済みのミューテックスを引き取る」と伝える目印
    - [x] ロックの方法を指定する目印
    - [x] std::lock と組み合わせる

## 関連ページ

- [cpprefjp: std::adopt_lock](https://cpprefjp.github.io/reference/mutex/defer_lock.html)
- [cppreference: std::adopt_lock](https://en.cppreference.com/w/cpp/thread/lock_tag)
