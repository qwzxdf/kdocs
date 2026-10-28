---
title: std::jthread
summary: "スコープを抜けると自動で join する、止める合図つきのスレッド。"
order: 71
tags:
  - 並行処理
---

# std::jthread

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-20">C++20</span>
`#include <thread>`
</div>

`std::thread` は、`join` か `detach` を呼ばずにデストラクターに達すると、プログラムが落ちます。例外や早期 `return` があると、`join` を書き忘れがちです。`std::jthread` は、`std::thread` の改良版で、デストラクターで自動的に `join` します。さらに、「止まって」という合図（`stop_token`）を受け取って、安全に終わらせる仕組みを持っています。

!!! tip "ポイント"
    - **`std::thread` の代わりに `std::jthread` を使う。** デストラクターで自動 join。
    - 関数の第 1 引数に `std::stop_token` を取ると、停止の合図を受け取れる。
    - `request_stop()` で止める合図を出す。デストラクターも、合図を出してから join する。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::jthread {#jthread}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
explicit jthread(F&& f, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出せるもの | スレッドで動かす関数・ラムダ。最初の引数を `std::stop_token` にすると合図を受け取れる |
| `args` | 何個でも | `f` に渡す引数（**コピーされる**） |

- 作った瞬間に別のスレッドで動き始めます
- デストラクタで `request_stop()` してから `join()` します

### join {#join}

```cpp
void join();
```

- スレッドが終わるまで、呼んだスレッドを止めて待ちます。1 回しか呼べません

### detach {#detach}

```cpp
void detach();
```

- 計算量: 定数

スレッドを切り離して、独立に動かします。`join` も `request_stop` もできなくなるので、`jthread` では普通は使いません。

### joinable {#joinable}

```cpp
[[nodiscard]] bool joinable() const noexcept;
```

- 計算量: 定数

スレッドが実行中（まだ `join` されていない）なら `true`。

### get_id {#get_id}

```cpp
id get_id() const noexcept;
```

- 計算量: 定数

スレッドの ID。

### native_handle {#native_handle}

```cpp
native_handle_type native_handle();
```

- 計算量: 定数

OS 固有のハンドル（`pthread_t` や `HANDLE`）を返します。標準にない機能（優先度の設定など）を使うときの出口です。

### hardware_concurrency {#hardware_concurrency}

```cpp
static unsigned hardware_concurrency() noexcept;
```

- 計算量: 定数

同時に動かせるスレッド数の目安（CPU のコア数など）。分からなければ 0 を返します。

### swap {#swap}

```cpp
void swap(jthread& other) noexcept;
```

- 計算量: 定数

2 つの `jthread` を入れ替えます。

### request_stop {#request_stop}

```cpp
bool request_stop() noexcept;
```

- 計算量: 定数

スレッドに停止を要求します。スレッド関数が受け取った `stop_token` で確かめて、自分で終了します。デストラクタでも、自動で呼ばれます。

### get_stop_source {#get_stop_source}

```cpp
stop_source get_stop_source() noexcept;
```

- 計算量: 定数

このスレッドの停止要求を管理する `stop_source` を返します。

### get_stop_token {#get_stop_token}

```cpp
stop_token get_stop_token() const noexcept;
```

- 計算量: 定数

このスレッドの停止要求を確認する `stop_token` を返します。

### operator= {#op_assign}

```cpp
jthread& operator=(jthread&& other) noexcept;
```

- 計算量: スレッドの終了まで待つ

ムーブ代入。自分が実行中なら、先に停止を要求して、`join` します。

## 実際に動かしてみる

```cpp
#include <print>
#include <thread>

int main() {
  {
    std::jthread worker([] { std::println("worker"); });
  }  // ここで自動的に join される
  std::println("done");
}
```

```text title="実行結果"
worker
done
```

## ゲームでの使いどころ

`std::thread` の代わりに、いつも `std::jthread` を使います。ワーカースレッドの関数の第 1 引数に `std::stop_token` を受ける形にすると、`request_stop()` で終了を伝えられます。ゲームの終了時に裏のスレッド（ロード、サウンド、ネットワーク）を安全に止められます。

```cpp
std::jthread worker([](std::stop_token st) {
  while (!st.stop_requested()) {
    // 裏の処理
  }
});
```

デストラクターは、`request_stop()` を呼んでから `join` します。ループが `stop_requested()` を確かめていれば、スコープを抜けるだけで止まります。

## よくあるミス

??? failure "スレッドに渡した関数が stop_token を見ない"
    `request_stop` は合図を出すだけです。関数のループで `stop_requested()` を確認しないと止まりません。

??? failure "参照を渡したつもりがコピー"
    スレッドの引数はコピーされます。参照で渡すなら `std::ref(x)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::thread`](thread.md) | 従来のスレッド。join を忘れると落ちる |
| [`std::stop_token`](stop_token.md) | 止める合図 |
| [`std::async`](async.md) | 結果を受け取るなら |

## コンパイラ対応

C++20 の機能です。GCC 10 / Clang 18 / MSVC 19.28 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `thread` の代わりに `jthread`
    - [x] 自動で join
    - [x] `stop_token` で止める

## 関連ページ

- [cpprefjp: std::jthread](https://cpprefjp.github.io/reference/thread/jthread.html)
- [cppreference: std::jthread](https://en.cppreference.com/w/cpp/thread/jthread)
