---
title: co_await
summary: "コルーチンを一時停止して、あとで結果を受け取って再開する演算子。"
order: 4
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# co_await

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

「ロードが終わるまで待つ」「3 フレーム待つ」のような待ちを、スレッドを立てずに、上から下へ読める普通の順番の文章で書きたい。それをかなえるのが `co_await` です。コルーチンの実行をいったん止めて、準備ができたら続きから再開します。待つ相手は「待ち受け体（awaitable）」と呼ばれる型で、止めるかどうかや、再開のときに何を返すかは、その型の 3 つの関数が決めます。

!!! tip "ポイント"
    - `co_await 式;` の形。式の型が、止め方と再開の仕方を決める
    - 待ち受け体は `await_ready`・`await_suspend`・`await_resume` の 3 関数を持つ
    - `await_ready` が `true` を返すと、止まらずにそのまま進む
    - 標準で用意されている待ち受け体は [`suspend_always`](suspend_always.md) と [`suspend_never`](suspend_never.md) だけ。「N フレーム待つ」などは自作する

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページに、コルーチンの簡単な例があります。

## 関数の詳しい説明

### co_await {#co_await}

```cpp
co_await expression;
```

`co_await` はコルーチンの中でだけ書けるキーワードです。式の結果が待ち受け体になり、次の 3 つの関数が、この順に呼ばれます。

| 関数 | 呼ばれる時 | 役割 |
| --- | --- | --- |
| `bool await_ready()` | 止まる前 | `true` なら止まらずに、すぐ `await_resume` へ進む |
| `await_suspend(handle)` | 止まった直後 | 呼び出した側へ制御を戻す前の処理。自分の `handle` をどこかに保存しておく |
| `T await_resume()` | 再開された時 | `co_await` 式全体の値になる |

#### await_ready

`await_ready` は、「待つ必要があるか」を決めます。すでに結果がそろっているなら `true` を返します。止まらないので、コルーチンの切り替えのコストがかかりません。たとえば、キャッシュに入っている画像を `co_await` で読むなら、ここで `true` を返します。

#### await_suspend

`await_suspend` は、コルーチンが止まったあとに呼ばれ、引数に自分の `std::coroutine_handle` を受け取ります。このハンドルをどこかへ保存しておき、あとで `resume()` を呼ぶと、`co_await` の次の行から再開します。保存し忘れると、誰も再開できず、コルーチンは永久に止まったままです。

戻り値の型で動きが変わります。`void` なら、そのまま呼び出し側へ戻ります。`bool` なら、`false` を返したときは止まらずに再開します。`std::coroutine_handle<>` なら、そのハンドルのコルーチンへ直接切り替わります（[`noop_coroutine`](noop_coroutine.md) のページで扱います）。

#### await_resume

`await_resume` の戻り値が、`co_await` 式の値になります。`int` を返すなら `int x = co_await ...;` と書けます。何も返さないなら `void` です。例外を投げると、`co_await` の位置で例外が飛びます。

## 実際に動かしてみる

```cpp
#include <coroutine>
#include <exception>
#include <print>
#include <utility>
#include <vector>

// 待っているコルーチンの一覧。Tick() が 1 フレームごとに呼ばれる
struct Waiter {
  std::coroutine_handle<> handle;
  int left;
};
std::vector<Waiter> g_waiters;

// N フレーム待つ待ち受け体
struct WaitFrames {
  int frames;
  bool await_ready() const noexcept { return frames <= 0; }  // 0 以下なら止まらない
  void await_suspend(std::coroutine_handle<> h) { g_waiters.push_back({h, frames}); }
  void await_resume() const noexcept {}
};

// 1 フレーム進める。待ち終わったコルーチンを再開する
void Tick() {
  std::vector<Waiter> current = std::move(g_waiters);
  g_waiters.clear();
  for (Waiter& w : current) {
    if (--w.left <= 0) {
      w.handle.resume();
    } else {
      g_waiters.push_back(w);
    }
  }
}

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

Task Fade() {
  std::println("フェード開始");
  co_await WaitFrames{2};   // 2 フレーム待つ
  std::println("フェード終了");
}

int main() {
  Task t = Fade();
  t.handle.resume();   // 最初の co_await まで進む
  for (int frame = 1; frame <= 3; ++frame) {
    std::println("フレーム {}", frame);
    Tick();
  }
}
```

```text title="実行結果"
フェード開始
フレーム 1
フレーム 2
フェード終了
フレーム 3
```

## ゲームでの使いどころ

「3 秒待ってから次の演出」「ロードが終わったら開始」を、スレッドを使わずに、上から下へ読める順番で書くときに使います。待ち受け体を自作して、フレーム数や時間を数える仕組みを用意します。

## よくあるミス

??? failure "コルーチンの外で使う"
    `co_await` は、`co_await` / `co_yield` / `co_return` のどれかを含む関数（コルーチン）の中でだけ書けます。普通の関数に書くとコンパイル エラーです。

??? failure "await_suspend でハンドルを保存し忘れる"
    誰も再開できないので、コルーチンは永久に止まります。ハンドルは、待ち行列などへ入れてください。

??? failure "止まっている間に参照先が消える"
    止まっている間、ローカル変数はコルーチンのフレームに残りますが、参照で受け取った引数の指す先が先に消えると、再開後に壊れます。コルーチンの引数は値で受け取るのが安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`coroutine_handle`](coroutine_handle.md) | 再開や破棄の操作 |
| [`suspend_always`](suspend_always.md) | 必ず止まる待ち受け体 |
| [`suspend_never`](suspend_never.md) | 止まらない待ち受け体 |
| [`std::async`](../../concurrency/async.md) | スレッドで非同期にする別の方法 |

## コンパイラ対応

C++20 の機能です。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: co_await](https://cpprefjp.github.io/reference/coroutine/co_await.html)
- [cppreference: co_await](https://en.cppreference.com/w/cpp/language/coroutines)
