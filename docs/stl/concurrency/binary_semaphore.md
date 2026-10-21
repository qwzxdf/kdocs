---
title: std::binary_semaphore
summary: "最大 1 のセマフォ。「合図」に使う。"
order: 97
tags:
  - 並行処理
---

# std::binary_semaphore

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-20">C++20</span>
`#include <semaphore>`
</div>

`std::binary_semaphore` は、**最大が 1 枚のセマフォ**（`counting_semaphore<1>` の別名）です。「ある」「ない」の 2 状態しかなく、**スレッド間の合図**に使えます。`release()` で合図を出し、`acquire()` で合図を待ちます。

!!! tip "ポイント"
    - `std::binary_semaphore sem(0);` で、最初は合図なし。
    - 別のスレッドが `release()` するまで、`acquire()` で待つ。
    - mutex と違い、別のスレッドが開ける（ロックと解除が別スレッドでもよい）。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::binary_semaphore {#binary_semaphore}

```cpp
using binary_semaphore = std::counting_semaphore<1>;
```

- 入場券が最大 1 枚のセマフォ。「準備できた」の合図をスレッド間で送るのに使えます（mutex と違い、取ったスレッドと別のスレッドが返してもいい）

```cpp
#include <print>
#include <semaphore>
#include <thread>

int main() {
  std::binary_semaphore ready(0);  // 最初は 0（まだ準備できていない）
  std::jthread worker([&] {
    ready.acquire();  // 合図が来るまで待つ
    std::println("合図を受け取った");
  });
  ready.release();  // 合図を送る
}
```

```text title="実行結果"
合図を受け取った
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 描画スレッドが「次のフレームのデータができた」と合図を待つ | `frame_ready.acquire();` |

## よくあるミス

??? failure "mutex の代わりに使う"
    ロックを取ったスレッドが解除する前提なら、`mutex` のほうが意図が伝わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::counting_semaphore`](counting_semaphore.md) | 最大 N 枚 |
| [`std::condition_variable`](condition_variable.md) | 条件つきで待つ |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大 1 のセマフォ
    - [x] 合図に使う
    - [x] 別のスレッドから `release` できる

## 関連ページ

- [cpprefjp: std::binary_semaphore](https://cpprefjp.github.io/reference/semaphore/binary_semaphore.html)
- [cppreference: std::binary_semaphore](https://en.cppreference.com/w/cpp/thread/counting_semaphore)
