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

`std::async` で関数を実行するとき、別のスレッドで動かすのか、結果が欲しくなるまで実行を遅らせるのかを選びたい。それを指定する列挙型が `std::launch` です。`std::launch::async` は別のスレッド、`std::launch::deferred` は `get()` を呼んだときに、呼んだスレッドで実行します。省略すると、どちらかを実装が選びます。

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

必ず裏で走らせたいロード処理などには、`std::launch::async` を明示します。省略すると、実装によっては `deferred` が選ばれ、`get()` を呼んだ瞬間に重い処理が走って、画面が固まります。

`deferred` は、遅延評価に使えます。結果が要らなかったら実行されずに済みます。ただし、`wait_for` で「終わったか」を調べても、実行が始まっていないので、いつまでも終わりません。

2 つを `|` で組み合わせて、どちらでもよいと指定することもできますが、意図が曖昧になるので、避けます。

## よくあるミス

??? failure "省略して別スレッドだと思う"
    省略すると `deferred` になる可能性があります。並列にしたいなら `launch::async` を明示します。

??? failure "省略して、裏で動くと思い込む"
    省略すると、実装が `async` と `deferred` の両方から選びます。必ず裏で走らせたいなら、`std::launch::async` を明示します。

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
