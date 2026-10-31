---
title: std::stop_callback
summary: "「止まって」の合図が来たときに、実行する処理を登録する。"
order: 74
tags:
  - 並行処理
---

# std::stop_callback

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <stop_token>`
</div>

`std::stop_token` で、中断の要求を受け取るスレッドは、要求が来たときに何かを片付けたい（待っている操作を中断する、ソケットを閉じる）ことがあります。`std::stop_callback` は、`stop_token` に紐づけて作ると、中断の要求が出たときに、登録した関数を呼びます。

!!! tip "ポイント"
    - `stop_callback cb(token, f);` で、`f` を登録する
    - `request_stop()` を呼んだスレッドで、`f` が実行される
    - `cb` を破棄すると、登録が解除される
    - 要求がすでに出ていたら、構築のその場で `f` が実行される

!!! info "このページを読む前に"
    [`std::future`](future.md) を先に読んでください。

## 関数の詳しい説明

### std::stop_callback {#stop_callback}

<span class="ver ver-20">C++20</span>

```cpp
template <class Callback>
class stop_callback {
 public:
  template <class C>
  explicit stop_callback(const std::stop_token& st, C&& cb);
  ~stop_callback();
};
```

登録した関数は、`request_stop()` を呼んだスレッドで、その呼び出しの中で実行されます。待っているスレッドの上ではありません。

コールバックの実行中に、同じ `stop_callback` を破棄すると、実行が終わるまで待たされます。コールバックの中で、自分自身のデストラクターを待つと、デッドロックします。

コールバックの中の処理は、短く、安全に保ちます。別のスレッドで、重い片付けをするなら、そこへ通知を送るだけにします。

## 実際に動かしてみる

```cpp
#include <print>
#include <stop_token>

int main() {
  std::stop_source source;
  int called = 0;

  {
    std::stop_callback cb(source.get_token(), [&called] { ++called; });
    std::println("要求前: {}", called);

    source.request_stop();  // ここで、コールバックが実行される
    std::println("要求後: {}", called);
  }

  // すでに要求が出ているトークンに登録すると、その場で実行される
  std::stop_callback late(source.get_token(), [&called] { ++called; });
  std::println("遅れて登録: {}", called);
}
```

```text title="実行結果"
要求前: 0
要求後: 1
遅れて登録: 2
```

## ゲームでの使いどころ

終了要求が来たとき、待ち状態のソケットや条件変数を起こす、といった片付けに使います。

## よくあるミス

??? failure "コールバックの中で重い処理をする"
    `request_stop` を呼んだスレッドが、その間止まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stop_token`](stop_token.md) | 要求を受け取る側 |
| [`stop_source`](stop_source.md) | 要求を出す側 |
| [`jthread`](jthread.md) | 終了要求つきのスレッド |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::stop_callback](https://cpprefjp.github.io/reference/stop_token/stop_callback.html)
- [cppreference: std::stop_callback](https://en.cppreference.com/w/cpp/thread/stop_callback)
