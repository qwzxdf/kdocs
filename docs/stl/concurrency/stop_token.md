---
title: std::stop_token
summary: "「止まって」の合図を受け取る側。"
order: 72
tags:
  - 並行処理
---

# std::stop_token

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <stop_token>`
</div>

裏で動くスレッドを、ゲームの終了時に安全に止めたい。`atomic<bool>` のフラグを自分で作って回す方法もありますが、毎回同じ仕組みを書くことになります。`std::stop_token` は、スレッドが「止まって」という合図を受け取るための道具です。`jthread` が関数に渡してくれるほか、`stop_source` から取り出すこともできます。ループの中で `stop_requested()` を確かめ、`true` なら後始末して終わります。

!!! tip "ポイント"
    - ループは `while (!st.stop_requested()) { ... }` と書く。
    - 合図は一度出したら取り消せない。
    - 合図が来たときに処理を実行する [`stop_callback`](stop_callback.md) もある。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::stop_token {#stop_token}

<span class="ver ver-20">C++20</span>

```cpp
class stop_token {
 public:
  bool stop_requested() const noexcept;
};
```

- `stop_requested()` が `true` になったら、スレッドの処理を終わらせます。jthread の関数の最初の引数にすると自動で渡されます

### request_stop {#request_stop}

<span class="ver ver-20">C++20</span>

```cpp
bool request_stop() noexcept;
```

- 「止まって」と伝えます。スレッドが止まるかどうかは、stop_token を見ているかどうか次第です

### stop_requested {#stop_requested}

```cpp
[[nodiscard]] bool stop_requested() const noexcept;
```

- 計算量: 定数

停止が要求されていれば `true`。ワーカースレッドのループ条件で確かめます。

### stop_possible {#stop_possible}

```cpp
[[nodiscard]] bool stop_possible() const noexcept;
```

- 計算量: 定数

停止が要求されうる状態なら `true`。

### swap {#swap}

```cpp
void swap(stop_token& other) noexcept;
```

- 計算量: 定数

2 つの `stop_token` を入れ替えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <stop_token>

int main() {
  std::stop_source source;
  std::stop_token token = source.get_token();
  std::println("{}", token.stop_possible());   // 止める合図を出せる相手がいるか
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

ワーカースレッドのループで、`while (!st.stop_requested()) { ... }` と書きます。ゲームの終了時に、`jthread` のデストラクターが合図を出し、ループが抜けます。

待ち状態のスレッドを起こしたいときは、`stop_callback` を使います。条件変数で待っているスレッドに、停止の合図が来たら通知する、といった処理です。

合図は一度出したら取り消せません。再び動かすなら、新しい `stop_source` を作ります。

## よくあるミス

??? failure "stop_requested を確認しない"
    ループの先頭や、時間のかかる処理の合間で確認します。確認しない処理は止まりません。

??? failure "合図を出したあとで取り消そうとする"
    `request_stop()` は一度きりです。止めたスレッドは、新しく作り直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stop_source`](stop_source.md) | 合図を出す側 |
| [`std::stop_callback`](stop_callback.md) | 合図が来たら実行する |
| [`std::jthread`](jthread.md) | stop_token を自動で渡す |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「止まって」の合図を受け取る
    - [x] `stop_requested()` で確認
    - [x] 合図は取り消せない

## 関連ページ

- [cpprefjp: std::stop_token](https://cpprefjp.github.io/reference/stop_token/stop_token.html)
- [cppreference: std::stop_token](https://en.cppreference.com/w/cpp/thread/stop_token)
