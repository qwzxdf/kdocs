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

`std::async(f)` は、仕事を別のスレッドで実行するのか、`get()` を呼ぶときに呼び出し元で実行するのか、実装に任されています。`std::launch` は、その実行方針を指定する列挙型で、`async`（別スレッドで必ず実行）と `deferred`（`get` / `wait` のときに実行）の 2 つがあります。

!!! tip "ポイント"
    - `launch::async`: 新しいスレッドで、すぐに実行
    - `launch::deferred`: `get()` / `wait()` を呼んだスレッドで、そのときに実行
    - 指定しないと、`async | deferred` で、実装が選ぶ
    - 確実に並列にしたいなら `launch::async` を指定する

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::launch {#launch}

<span class="ver ver-11">C++11</span>

```cpp
enum class launch : /* 未規定 */ {
  async = /* 未規定 */,
  deferred = /* 未規定 */
};
```

ビットマスク型で、`|` で組み合わせられます。方針を省略した `std::async(f)` は、`launch::async | launch::deferred` と同じで、実装が好きなほうを選びます。実装によっては、スレッドが足りないときに `deferred` を選び、並列にならないことがあります。

`deferred` の仕事は、`get()` を呼ばないと、いつまでも実行されません。結果を捨てる `async`（戻り値の `future` を受けない）は、`future` のデストラクターで完了を待つため、その場で止まります。

並列に実行したいなら、必ず `launch::async` を指定します。

## 実際に動かしてみる

```cpp
#include <future>
#include <print>
#include <thread>

int main() {
  const auto main_id = std::this_thread::get_id();

  // deferred: get() を呼んだスレッドで実行される
  auto d = std::async(std::launch::deferred, [] { return std::this_thread::get_id(); });
  std::println("deferred は呼び出し元: {}", d.get() == main_id);

  // async: 別のスレッドで実行される
  auto a = std::async(std::launch::async, [] { return std::this_thread::get_id(); });
  std::println("async は別スレッド: {}", a.get() != main_id);
}
```

```text title="実行結果"
deferred は呼び出し元: true
async は別スレッド: true
```

## ゲームでの使いどころ

アセットの読み込みのように、必ず裏で動かしたいものには `launch::async` を指定します。

## よくあるミス

??? failure "方針を省略して、並列になると思う"
    実装が `deferred` を選ぶことがあります。

??? failure "戻り値の future を受けない"
    デストラクターで完了を待つので、その場で止まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future`](future.md) | 結果を受け取る |
| [`future_status`](future_status.md) | 待ちの結果 |
| [`thread`](thread.md) | スレッドを直接作る |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::launch](https://cpprefjp.github.io/reference/future/launch.html)
- [cppreference: std::launch](https://en.cppreference.com/w/cpp/thread/launch)
