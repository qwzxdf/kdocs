---
title: std::call_once
summary: "何回呼ばれても、初期化を 1 回だけ実行する。"
order: 84
tags:
  - 並行処理
---

# std::call_once

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11</span>
`#include <mutex>`
</div>

`std::call_once` は、**複数のスレッドから何度呼ばれても、渡した関数を 1 回だけ実行する**関数です。`std::once_flag` という「実行済みの印」とセットで使います。シングルトンの初期化のような、一度だけ行う処理に使います。ローカル `static` 変数でも同じ保証があるので、そちらで足りることも多いです。

!!! tip "ポイント"
    - `std::once_flag flag;` と `std::call_once(flag, 関数);` のセット。
    - 同時に呼ばれても、1 つのスレッドだけが実行し、ほかは終わるまで待つ。
    - 関数内の `static` 変数の初期化は、C++11 以降スレッドセーフ。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::call_once {#call_once}

```cpp
template <class Callable, class... Args>
void call_once(std::once_flag& flag, Callable&& f, Args&&... args);
```

- 何個のスレッドから呼ばれても、`f` を 1 回だけ実行します（初期化に使う）

```cpp
#include <mutex>
#include <print>
#include <thread>
#include <vector>

int main() {
  std::once_flag init_flag;
  int init_count = 0;
  {
    std::vector<std::jthread> threads;
    for (int i = 0; i < 4; ++i) {
      threads.emplace_back([&] { std::call_once(init_flag, [&] { ++init_count; }); });
    }
  }
  std::println("初期化 {} 回", init_count);
}
```

```text title="実行結果"
初期化 1 回
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイルの遅延読み込み（最初の 1 回だけ） | `std::call_once(flag, LoadConfig);` |

## よくあるミス

??? failure "関数が例外を投げた"
    例外を投げると「実行済み」にならず、次の呼び出しがもう一度実行します。

## 類似

| 名前 | 違い |
| --- | --- |
| 関数内の `static` 変数 | 同じ保証があり、より簡単 |
| [`std::mutex`](mutex.md) | 自分でロックする |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 回だけ実行する
    - [x] `once_flag` とセット
    - [x] 関数内の `static` で足りることも多い

## 関連ページ

- [cpprefjp: std::call_once](https://cpprefjp.github.io/reference/mutex/call_once.html)
- [cppreference: std::call_once](https://en.cppreference.com/w/cpp/thread/call_once)
