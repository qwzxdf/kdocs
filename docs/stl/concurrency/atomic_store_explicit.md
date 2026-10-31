---
title: std::atomic_store_explicit
summary: "メモリ順序を指定して、アトミックに値を書く。"
order: 900
tags:
  - 並行処理
---

# std::atomic_store_explicit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <atomic>`
</div>

`atomic_load_explicit` の書き込み版が `atomic_store_explicit` です。メモリ順序を指定して、`atomic` に値を書き込みます。`release` で書くと、それ以前の書き込みが、`acquire` で読んだスレッドから見えるようになります。

!!! tip "ポイント"
    - `atomic` に、メモリ順序を指定して書く
    - メンバー関数 `a.store(v, order)` と同じ
    - 書き込みに使える順序は `relaxed`、`release`、`seq_cst`
    - `acquire` や `acq_rel` は書き込みには使えない

!!! info "このページを読む前に"
    [`std::atomic`](atomic.md) を先に読んでください。

## 関数の詳しい説明

### std::atomic_store_explicit {#atomic_store_explicit}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
void atomic_store_explicit(std::atomic<T>* obj, typename std::atomic<T>::value_type desired,
                           std::memory_order order) noexcept;
```

`memory_order_release` は、「この書き込み以前の、全ての書き込みが、この書き込みより後に見える」保証です。データを準備してから、フラグを `release` で立てると、フラグを `acquire` で読んだスレッドが、データを確実に見られます。

順序を間違えると、コンパイルが通るのに、特定の CPU（ARM など）でだけ壊れる、気づきにくい不具合になります。x86 は順序が強いので、間違っていても動いてしまいます。

自信がなければ、既定の `seq_cst` を使います。

## 実際に動かしてみる

```cpp
#include <atomic>
#include <print>
#include <thread>

int main() {
  int config = 0;
  std::atomic<int> state{0};

  std::thread writer([&] {
    config = 100;
    std::atomic_store_explicit(&state, 1, std::memory_order_release);
  });

  while (std::atomic_load_explicit(&state, std::memory_order_acquire) != 1) {
  }
  std::println("config = {}", config);
  writer.join();
}
```

```text title="実行結果"
config = 100
```

## ゲームでの使いどころ

ゲームの起動時に、読み込みスレッドが設定を準備して、完了を知らせるフラグを立てるのに使います。

## よくあるミス

??? failure "store に acquire を指定する"
    コンパイル エラーか未定義です。書き込みには `release` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atomic_load_explicit`](atomic_load_explicit.md) | 読む側 |
| [`memory_order`](memory_order.md) | 順序の一覧 |
| [`atomic`](atomic.md) | 本体 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::atomic_store_explicit](https://cpprefjp.github.io/reference/atomic/atomic_store_explicit.html)
- [cppreference: std::atomic_store_explicit](https://en.cppreference.com/w/cpp/atomic/atomic_store_explicit)
