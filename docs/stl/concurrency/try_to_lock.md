---
title: std::try_to_lock
summary: "unique_lock に「ロックを試すだけ。取れなければ待たない」と伝える目印。"
order: 900
tags:
  - 並行処理
---

# std::try_to_lock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

ミューテックスがすでに他のスレッドにロックされているとき、`unique_lock` の構築で待たされたくない。`std::try_to_lock` を渡すと、ロックを試みて、取れなければ待たずに諦めます。取れたかは、`owns_lock()` で分かります。

!!! tip "ポイント"
    - `unique_lock(m, std::try_to_lock)` は、ロックを試みる。待たない
    - 取れたら `owns_lock()` が真
    - 取れなければ、他の仕事を先に進められる
    - `lk.try_lock()` を、あとから呼ぶのと同じ

!!! info "このページを読む前に"
    [`std::mutex`](mutex.md) を先に読んでください。

## 関数の詳しい説明

### std::try_to_lock {#try_to_lock}

<span class="ver ver-11">C++11</span>

```cpp
struct try_to_lock_t { explicit try_to_lock_t() = default; };
inline constexpr std::try_to_lock_t try_to_lock{};
```

構築の中で `m.try_lock()` が呼ばれ、結果が `owns_lock()` に反映されます。

```cpp
std::unique_lock lk(m, std::try_to_lock);
if (lk.owns_lock()) {
  // 取れた
} else {
  // 取れなかった。他の仕事をする
}
```

同じスレッドが、すでにロックしている `std::mutex` に `try_to_lock` を試みると、未定義動作です。再帰ロックが要るなら `recursive_mutex` です。

ゲームでは、描画スレッドが、共有データのロックが取れなかったら、前のフレームのデータで描く、という戦略に使えます。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <print>
#include <thread>

int main() {
  std::mutex m;
  m.lock();  // main がロックを持っている

  bool got = true;
  std::thread t([&] {
    std::unique_lock<std::mutex> lk(m, std::try_to_lock);
    got = lk.owns_lock();  // 取れない
  });
  t.join();
  std::println("別スレッドで取れた: {}", got);

  m.unlock();
  std::unique_lock<std::mutex> lk(m, std::try_to_lock);
  std::println("解放後は取れた: {}", lk.owns_lock());
}
```

```text title="実行結果"
別スレッドで取れた: false
解放後は取れた: true
```

## ゲームでの使いどころ

描画スレッドが、更新スレッドのロックを待たずに、前の状態で描く場面に使います。

## よくあるミス

??? failure "取れたか確かめずに共有データを触る"
    `owns_lock()` を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`defer_lock`](defer_lock.md) | ロックを遅らせる |
| [`adopt_lock`](adopt_lock.md) | ロック済みを引き継ぐ |
| [`try_lock`](try_lock.md) | 複数を試す |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::try_to_lock](https://cpprefjp.github.io/reference/mutex/defer_lock.html)
- [cppreference: std::try_to_lock](https://en.cppreference.com/w/cpp/thread/lock_tag)
