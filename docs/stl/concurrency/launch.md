---
title: std::launch
summary: "async の実行方法（別スレッドか、遅延か）を選ぶ列挙型。"
order: 900
tags:
  - 並行処理
---

# std::launch

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::async` で関数を実行するとき、別スレッドで動かすのか、`get()` を呼ぶまで遅らせるのかを選べます。それを指定するのが `std::launch::async`（別スレッド）と `std::launch::deferred`（遅延）です。省略すると、どちらかを実装が選びます。

!!! tip "ポイント"
    - `std::launch::async`: すぐ別スレッドで始める。
    - `std::launch::deferred`: `get()` / `wait()` のときに、呼んだスレッドで実行する。
    - 省略すると実装が選ぶので、意図を持つなら明示する。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::launch {#launch}

```cpp
enum class launch : /* 実装定義 */ { async = 1, deferred = 2 };
```

- 戻り値: なし（列挙型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <future>
#include <print>
#include <thread>

int main() {
  auto f = std::async(std::launch::deferred, [] { return std::this_thread::get_id(); });
  std::println("{}", f.get() == std::this_thread::get_id());  // 呼んだスレッドで実行される
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 重い処理を確実に別スレッドで動かす | `std::async(std::launch::async, f);` |

## よくあるミス

??? failure "省略して別スレッドだと思う"
    省略すると `deferred` になる可能性があります。並列にしたいなら `launch::async` を明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`async`](async.md) | 非同期実行 |
| [`future`](future.md) | 結果を受け取る |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] async の実行方法を選ぶ
    - [x] async は別スレッド、deferred は遅延
    - [x] 省略は実装任せ

## 関連ページ

- [cpprefjp: std::launch](https://cpprefjp.github.io/reference/future/launch.html)
- [cppreference: std::launch](https://en.cppreference.com/w/cpp/thread/launch)
