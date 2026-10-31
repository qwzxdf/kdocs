---
title: co_yield
summary: "コルーチンから値を 1 つ返して一時停止し、次に呼ばれたら続きから再開する。"
order: 5
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# co_yield

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

1 から順に値を出していく、敵の出現位置を 1 つずつ返す、のような「少しずつ値を渡していく処理」を、状態を持つクラスにせずに、普通のループで書きたい。`co_yield 値;` は、値を呼び出し側へ渡して、コルーチンをいったん止めます。次に再開されると、`co_yield` の次の行から続きます。

!!! tip "ポイント"
    - `co_yield v;` は `co_await promise.yield_value(v);` と同じ意味
    - 値の置き場は、`promise_type` の中に自分で用意する
    - 標準で用意された型は [`std::generator`](../generator.md)（C++23）
    - ループの途中で止まれるので、無限の列も書ける

!!! info "このページを読む前に"
    [`std::generator`](../generator.md) のページに、コルーチンの簡単な例があります。

## 関数の詳しい説明

### co_yield {#co_yield}

```cpp
co_yield expression;
```

`co_yield` は、書き換えると `co_await promise.yield_value(expression);` です。つまり、`promise_type` に `yield_value` という関数を用意しておく必要があります。普通は、`yield_value` の中で受け取った値を `promise_type` のメンバーへ保存し、`std::suspend_always` を返して止まります。

呼び出し側は、`handle.resume()` で次の値まで進め、`handle.promise()` の中の値を読みます。`handle.done()` が `true` になったら、値はもう出ません。

標準ライブラリで同じことをしたいなら、C++23 の [`std::generator`](../generator.md) があります。自分で書くのは、`generator` が使えない環境や、動きを理解したいときです。

## 実際に動かしてみる

```cpp
#include <coroutine>
#include <exception>
#include <print>
#include <utility>
#include <vector>

struct Generator {
  struct promise_type {
    int value = 0;
    Generator get_return_object() { return Generator{std::coroutine_handle<promise_type>::from_promise(*this)}; }
    std::suspend_always initial_suspend() noexcept { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }
    std::suspend_always yield_value(int v) noexcept {   // co_yield v; で呼ばれる
      value = v;
      return {};
    }
    void return_void() {}
    void unhandled_exception() { std::terminate(); }
  };

  std::coroutine_handle<promise_type> handle;
  explicit Generator(std::coroutine_handle<promise_type> h) : handle(h) {}
  Generator(Generator&& other) noexcept : handle(std::exchange(other.handle, {})) {}
  ~Generator() {
    if (handle) handle.destroy();
  }

  // 次の値まで進める。値が尽きたら false
  bool Next() {
    handle.resume();
    return !handle.done();
  }
  int Value() const { return handle.promise().value; }
};

// 敵の出現位置を 10 ずつずらして返す
Generator SpawnPositions(int count) {
  for (int i = 1; i <= count; ++i) {
    co_yield i * 10;
  }
}

int main() {
  Generator g = SpawnPositions(3);
  while (g.Next()) {
    std::println("出現位置: {}", g.Value());
  }
}
```

```text title="実行結果"
出現位置: 10
出現位置: 20
出現位置: 30
```

## ゲームでの使いどころ

敵の出現位置、タイルの座標、フレームごとの補間値など、少しずつ値を出す処理を、ループのまま書けます。無限に続く列（連番、乱数）も、必要な分だけ取り出せます。

## よくあるミス

??? failure "yield_value を用意しない"
    `promise_type` に `yield_value` がないと、`co_yield` がコンパイル エラーになります。

??? failure "Next() の前に Value() を読む"
    最初の `resume()` の前は、値がまだ入っていません。`Next()` が `true` を返してから読みます。

??? failure "値を参照で返して、次の resume で上書きされる"
    `value` はコルーチンが次に進むと変わります。長く持つなら、コピーしておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::generator`](../generator.md) | 標準の生成器（C++23） |
| [`co_await`](co_await.md) | `co_yield` は `co_await` の一種 |
| [`co_return`](co_return.md) | 最後の値を返して終わる |
| [`coroutine_handle`](coroutine_handle.md) | 再開と状態の確認 |

## コンパイラ対応

C++20 の機能です。標準の `std::generator` は C++23 で、MSVC・GCC 14 以降が対応しています。

## 関連ページ

- [cpprefjp: コルーチン](https://cpprefjp.github.io/reference/coroutine.html)
- [cppreference: Coroutines](https://en.cppreference.com/w/cpp/language/coroutines)
