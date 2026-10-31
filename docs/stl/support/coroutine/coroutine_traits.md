---
title: std::coroutine_traits
summary: "コルーチンの戻り値の型から、promise_type を取り出す特性。"
order: 900
group: コルーチン（<coroutine>）
tags:
  - 型・言語サポート
---

# std::coroutine_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <coroutine>`
</div>

コルーチンを書くと、コンパイラは「この関数の戻り値の型から、`promise_type` を見つける」仕事をします。その見つけ方を表すのが `std::coroutine_traits<R, Args...>` です。普通は `R::promise_type` を探すだけなので、意識しません。しかし、戻り値の型に手を入れられない（`promise_type` を足せない）ときは、これを特殊化して、外から `promise_type` を決められます。

!!! tip "ポイント"
    - `coroutine_traits<R, Args...>::promise_type` が、コルーチンの `promise_type` になる
    - 既定では `R::promise_type`（戻り値の型の中の入れ子の型）
    - 自分で書けない型（標準や外部ライブラリの型）をコルーチンの戻り値にしたいときに特殊化する
    - 引数の型の組ごとに、違う `promise_type` を選べる

!!! info "このページを読む前に"
    [`coroutine_handle`](coroutine_handle.md) を先に読んでください。

## 関数の詳しい説明

### std::coroutine_traits {#coroutine_traits}

```cpp
template <class R, class... Args>
struct coroutine_traits;   // 既定: using promise_type = typename R::promise_type;
```

| 引数 | 意味 |
| --- | --- |
| `R` | コルーチン関数の戻り値の型 |
| `Args...` | コルーチン関数の引数の型（メンバー関数なら、先頭に `*this` の型が入る） |

コンパイラは、コルーチンを見つけるたびに `coroutine_traits<R, Args...>::promise_type` を探します。既定の実装は `R::promise_type` を返すだけなので、`Task` のように、戻り値の型が自分で `promise_type` を持っていれば、特殊化は要りません。

特殊化が要るのは、戻り値の型を変えられないときです。たとえば `Job` という型が、ほかのライブラリで定義されていて、`promise_type` を足せないなら、`std::coroutine_traits<Job, Args...>` を特殊化して、外から `promise_type` を与えます。特殊化は、名前空間 `std` に書くことが許されている、数少ないものの 1 つです。

## 実際に動かしてみる

```cpp
#include <coroutine>
#include <exception>
#include <print>
#include <utility>
#include <vector>
#include <type_traits>

// promise_type を持たない型。自分では変更できないものとする
struct Job {
  std::coroutine_handle<> handle;
};

// Job 用の promise_type は、外に別の型として書く
struct JobPromise {
  Job get_return_object() { return Job{std::coroutine_handle<JobPromise>::from_promise(*this)}; }
  std::suspend_always initial_suspend() noexcept { return {}; }
  std::suspend_always final_suspend() noexcept { return {}; }
  void return_void() {}
  void unhandled_exception() { std::terminate(); }
};

// Job を戻り値にするコルーチンは、どんな引数でも JobPromise を使う
template <class... Args>
struct std::coroutine_traits<Job, Args...> {
  using promise_type = JobPromise;
};

Job Run(int n) {
  std::println("ジョブ {} を実行", n);
  co_return;
}

int main() {
  Job j = Run(5);
  j.handle.resume();
  j.handle.destroy();

  // 既定の動作: 戻り値の型の入れ子の promise_type を使う
  struct WithNested {
    struct promise_type {};
  };
  static_assert(std::is_same_v<std::coroutine_traits<WithNested>::promise_type, WithNested::promise_type>);
}
```

```text title="実行結果"
ジョブ 5 を実行
```

## ゲームでの使いどころ

標準や外部ライブラリの型を、コルーチンの戻り値に使いたいときに特殊化します。多くのゲーム コードでは、自作の `Task` に `promise_type` を入れるだけで足ります。

## よくあるミス

??? failure "std 以外の名前空間で特殊化する"
    `std::coroutine_traits` の特殊化は、`std` の中に書く必要があります（`template <> struct std::coroutine_traits<...>` の形）。

??? failure "R::promise_type も特殊化も両方書く"
    特殊化が優先されますが、混乱のもとです。どちらか片方にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`coroutine_handle`](coroutine_handle.md) | `from_promise` でハンドルを作る |
| [`co_return`](co_return.md) | `promise_type` が受ける終わりの処理 |
| [`std::generator`](../generator.md) | 標準が用意した戻り値の型 |

## コンパイラ対応

C++20 の機能です。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::coroutine_traits](https://cpprefjp.github.io/reference/coroutine/coroutine_traits.html)
- [cppreference: std::coroutine_traits](https://en.cppreference.com/w/cpp/coroutine/coroutine_traits)
