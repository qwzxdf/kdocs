---
title: std::this_thread::yield
summary: "他のスレッドに、実行の順番を譲る。"
order: 77
group: this_thread
tags:
  - 並行処理
---

# std::this_thread::yield

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <thread>`
</div>

`std::this_thread::yield` は、**今のスレッドが「少し他のスレッドに順番を譲ります」と OS に伝える**関数です。待ちのループ（スピン）で CPU を無駄に使い続けないための、軽い工夫に使います。実際に眠るわけではないので、長く待つなら `sleep_for` や条件変数を使います。

!!! tip "ポイント"
    - 待つ時間が短い（数マイクロ秒）スピン待ちのループで使う。
    - 長く待つなら条件変数。
    - 効果は OS しだいで、必ず順番が譲られるわけではない。

!!! info "このページを読む前に"
    [並行処理の基本](../../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::this_thread::yield {#yield}

```cpp
void yield() noexcept;
```

- 他のスレッドに順番を譲ります。待ちのループで CPU を使い切らないようにするのに使いますが、普通は条件変数などで待ちます

```cpp
#include <print>
#include <thread>

int main() {
  auto main_id = std::this_thread::get_id();
  std::jthread t([main_id] {
    std::this_thread::yield();
    std::println("メインスレッド？ {}", std::this_thread::get_id() == main_id);
  });
  t.join();
  std::println("コア数は 1 以上？ {}", std::thread::hardware_concurrency() >= 1);
}
```

```text title="実行結果"
メインスレッド？ false
コア数は 1 以上？ true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 他のスレッドの結果を短時間だけ待つ | `while (!ready) std::this_thread::yield();` |

## よくあるミス

??? failure "yield で長く待つ"
    CPU を使い続けます。長い待ちは条件変数か `sleep_for` に任せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::this_thread::sleep_for`](sleep_for.md) | 眠る |
| [`std::condition_variable`](../condition_variable.md) | 条件を待つ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 他のスレッドに順番を譲る
    - [x] 短いスピン待ち向け
    - [x] 長い待ちは別の方法

## 関連ページ

- [cpprefjp: std::this_thread::yield](https://cpprefjp.github.io/reference/thread/this_thread/yield.html)
- [cppreference: std::this_thread::yield](https://en.cppreference.com/w/cpp/thread/yield)
