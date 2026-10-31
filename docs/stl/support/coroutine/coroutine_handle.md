---
title: std::coroutine_handle
summary: "コルーチンの再開・破棄を操作する「取っ手」。"
order: 1
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# std::coroutine_handle

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

一時停止中のコルーチンを、外から再開したり、終わったか調べたり、後片づけをしたい。そのための「取っ手」が `std::coroutine_handle<Promise>` です。実体はポインターで、コルーチンのフレーム（ローカル変数や再開位置を入れたメモリ）を指します。

!!! tip "ポイント"
    - `resume()` で再開、`done()` で終了の確認、`destroy()` で後片づけ
    - `std::coroutine_handle<>` は型を消した版で、任意のコルーチンを指せる
    - `promise()` で `promise_type` の中身に触れる（型つきのハンドルのみ）
    - コピーしてもフレームは増えない。`destroy()` は 1 度だけ呼ぶ

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページに、コルーチンの簡単な例があります。

## 関数の詳しい説明

### resume {#resume}

```cpp
void resume() const;
void operator()() const;   // resume と同じ
```

止まっているコルーチンを、再開します。`done()` が `true` のコルーチンに呼ぶと未定義動作です。終わったコルーチンを再開してしまうミスが多いので、`done()` を確認してから呼びます。

### done {#done}

```cpp
bool done() const;
```

`final_suspend()` で止まっているときだけ `true` になります。`initial_suspend` で止まっているときや、`co_await` で止まっているときは `false` です。止まっていない（実行中の）コルーチンに呼ぶと未定義動作です。

### destroy {#destroy}

```cpp
void destroy() const;
```

コルーチンのフレームを解放します。ローカル変数のデストラクターも、止まっている位置までのものが呼ばれます。`destroy()` を呼ばずに放置するとメモリ リークです。2 回呼ぶと二重解放です。ハンドルを持つ型のデストラクターで 1 回だけ呼ぶ、という形にします。

### from_promise {#from_promise}

```cpp
static coroutine_handle from_promise(Promise& p);
```

`promise_type` の参照から、そのコルーチンのハンドルを作ります。`get_return_object()` の中で、戻り値の型にハンドルを持たせるときに使います。

### promise {#promise}

```cpp
Promise& promise() const;
```

ハンドルから `promise_type` の実体を取り出します。`co_yield` の値や `co_return` の結果を、呼び出し側が読むのに使います。`std::coroutine_handle<>`（型を消した版）には、ありません。

### address と from_address {#address}

```cpp
void* address() const noexcept;
static coroutine_handle from_address(void* addr);
```

ハンドルを `void*` にして、C の API のユーザーデータなどに預けられます。受け取った側で、`from_address` で元のハンドルに戻します。

### operator bool {#operator-bool}

```cpp
explicit operator bool() const noexcept;
```

ハンドルがコルーチンを指しているか（空でないか）を返します。`done()` とは別で、「終わった」ではなく「ハンドルが有効」の意味です。

## 実際に動かしてみる

```cpp
#include <coroutine>
#include <exception>
#include <print>
#include <utility>
#include <vector>

struct Task {
  struct promise_type {
    Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_always initial_suspend() noexcept { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }
    void return_void() {}
    void unhandled_exception() { std::terminate(); }
  };

  std::coroutine_handle<promise_type> handle;
  explicit Task(std::coroutine_handle<promise_type> h) : handle(h) {}
  Task(Task&& other) noexcept : handle(std::exchange(other.handle, {})) {}
  ~Task() {
    if (handle) handle.destroy();
  }
};

Task Steps() {
  std::println("1 歩目");
  co_await std::suspend_always{};
  std::println("2 歩目");
}

int main() {
  Task t = Steps();
  std::coroutine_handle<Task::promise_type> h = t.handle;

  std::println("開始前の done: {}", h.done());   // initial_suspend で止まっている
  h.resume();
  std::println("1 回目の後の done: {}", h.done());
  h.resume();
  std::println("2 回目の後の done: {}", h.done());   // final_suspend で止まっている

  // void* に預けて、元に戻せる
  void* addr = h.address();
  auto h2 = std::coroutine_handle<Task::promise_type>::from_address(addr);
  std::println("同じハンドル: {}", h2 == h);
}
```

```text title="実行結果"
開始前の done: false
1 歩目
1 回目の後の done: false
2 歩目
2 回目の後の done: true
同じハンドル: true
```

## ゲームでの使いどころ

演出やイベントのコルーチンを、フレームごとに `resume()` して進めるとき、終わったものを `done()` で見つけて片づけるときに使います。

## よくあるミス

??? failure "done() が true のハンドルを resume する"
    未定義動作です。`done()` を確認してから呼びます。

??? failure "destroy() を忘れる、または 2 回呼ぶ"
    忘れるとリーク、2 回呼ぶと二重解放です。ハンドルを持つ型のデストラクターで 1 回だけ呼びます。

??? failure "ハンドルをコピーして、両方で destroy する"
    ハンドルはコピーしてもフレームは 1 つのままです。持ち主を 1 人に決め、ムーブだけを許します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`co_await`](co_await.md) | 止まる位置を作る |
| [`noop_coroutine`](noop_coroutine.md) | 何もしないハンドル |
| [`coroutine_traits`](coroutine_traits.md) | `promise_type` の決め方 |

## コンパイラ対応

C++20 の機能です。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::coroutine_handle](https://cpprefjp.github.io/reference/coroutine/coroutine_handle.html)
- [cppreference: std::coroutine_handle](https://en.cppreference.com/w/cpp/coroutine/coroutine_handle)
