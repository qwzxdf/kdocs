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

`unique_lock` は、作った時点でミューテックスをロックします。あとでまとめて（デッドロックを避けて）ロックしたいときは、`std::defer_lock` を渡して「ロックは後で」と伝えます。

!!! tip "ポイント"
    - `std::defer_lock_t` 型の定数。
    - `lock_guard`・`unique_lock`・`scoped_lock` のコンストラクタの第 2 引数に渡す。
    - デッドロックを避ける `std::lock` と組み合わせて使う。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::defer_lock {#defer_lock}

```cpp
struct defer_lock_t { explicit defer_lock_t() = default; };
inline constexpr defer_lock_t defer_lock{};
```

- 戻り値: なし（目印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>

int main() {
  std::mutex m;
  std::unique_lock lk(m, std::defer_lock);
  std::println("{}", lk.owns_lock());
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 複数のミューテックスを同時にロック | `std::lock(m1, m2);` のあと `std::lock_guard g1(m1, std::adopt_lock);` |

## よくあるミス

??? failure "目印とロックの状態が食い違う"
    `owns_lock()` で、実際にロックを持っているかを確かめてから使います。

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
    - [x] unique_lock に「まだロックしない」と伝える目印
    - [x] ロックの方法を指定する目印
    - [x] std::lock と組み合わせる

## 関連ページ

- [cpprefjp: std::defer_lock](https://cpprefjp.github.io/reference/mutex/defer_lock.html)
- [cppreference: std::defer_lock](https://en.cppreference.com/w/cpp/thread/lock_tag)
