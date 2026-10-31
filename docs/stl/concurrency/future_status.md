---
title: std::future_status
summary: "future の待機の結果（準備完了・時間切れ・遅延）を表す列挙型。"
order: 900
tags:
  - 並行処理
---

# std::future_status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <future>`
</div>

`std::future::wait_for` は、結果が出るまで一定時間だけ待ちます。時間内に結果が出たのか、まだなのか、そもそも別スレッドで動いていないのか。その状態を返す列挙型が `std::future_status` で、`ready`、`timeout`、`deferred` の 3 つがあります。

!!! tip "ポイント"
    - `ready`: 結果が出ている（`get()` が待たない）
    - `timeout`: 時間切れ。まだ終わっていない
    - `deferred`: `launch::deferred` で、`get()` や `wait()` を呼ぶまで実行されない
    - `deferred` のとき、`wait_for` は待たずに、すぐ戻る

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::future_status {#future_status}

<span class="ver ver-11">C++11</span>

```cpp
enum class future_status { ready, timeout, deferred };
```

`wait_for` / `wait_until` の戻り値です。

遅延実行（`std::launch::deferred`）の `future` は、`get()` を呼ぶまで、仕事が始まりません。`wait_for` で待っても、何も進まないので、待たずに `deferred` を返します。`while (f.wait_for(10ms) != future_status::ready) {}` と書くと、`deferred` のときに、永久に回ります。

そのため、ループで待つときは、`timeout` かどうかを見て、`deferred` なら、先に `get()` で実行させる、といった分岐が要ります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <future>
#include <print>

int main() {
  using namespace std::chrono_literals;

  // 時間切れ: promise がまだ値を入れていない
  std::promise<int> p;
  std::future<int> f = p.get_future();
  std::println("時間切れ: {}", f.wait_for(1ms) == std::future_status::timeout);

  // 準備完了
  p.set_value(7);
  std::println("準備完了: {}", f.wait_for(1ms) == std::future_status::ready);

  // 遅延実行
  auto d = std::async(std::launch::deferred, [] { return 1; });
  std::println("遅延: {}", d.wait_for(1ms) == std::future_status::deferred);
}
```

```text title="実行結果"
時間切れ: true
準備完了: true
遅延: true
```

## ゲームでの使いどころ

ロード画面で、非同期の読み込みの完了を、毎フレーム `wait_for(0ms)` で確かめるのに使います。

## よくあるミス

??? failure "deferred を考えずにループで待つ"
    永久に回ります。

??? failure "ready を確かめずに get する"
    待たされます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`future`](future.md) | `wait_for` を持つ |
| [`launch`](launch.md) | 実行方針 |
| [`cv_status`](cv_status.md) | 条件変数の同様の列挙型 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::future_status](https://cpprefjp.github.io/reference/future/future_status.html)
- [cppreference: std::future_status](https://en.cppreference.com/w/cpp/thread/future_status)
