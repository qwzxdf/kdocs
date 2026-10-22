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

コルーチンの戻り値の型（`Task` など）には、コンパイラが探す `promise_type` が必要です。ふつうは `Task::promise_type` を定義すれば足りますが、自分で書けない型（`std::future` など）を戻り値にしたいときは、`coroutine_traits` を特殊化して `promise_type` を外から与えます。

!!! tip "ポイント"
    - 既定では、戻り値の型の `promise_type` を使う。
    - 他人の型にコルーチンの性質を足したいときに、特殊化する。
    - ふつうの自作コルーチンでは、意識しなくてよい。

!!! info "このページを読む前に"
    [`coroutine_handle`](coroutine_handle.md) を先に読んでください。

## 関数の詳しい説明

### std::coroutine_traits {#coroutine_traits}

```cpp
template <class R, class... Args>
struct coroutine_traits { using promise_type = typename R::promise_type; };
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | コルーチンの戻り値の型 |
| `Args...` | 型 | 引数の型 |

- 戻り値: `promise_type`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <coroutine>
#include <print>
#include <type_traits>

struct Task {
  struct promise_type {};
};

int main() {
  std::println("{}", std::is_same_v<std::coroutine_traits<Task>::promise_type, Task::promise_type>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `std::future` をコルーチンの戻り値にする | `std::coroutine_traits<std::future<int>, Args...>` を特殊化する |

## よくあるミス

??? failure "`promise_type` を定義し忘れる"
    戻り値の型にも特殊化にも `promise_type` がないと、コルーチンとしてコンパイルできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`coroutine_handle`](coroutine_handle.md) | コルーチンの操作 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 戻り値の型から promise_type を求める
    - [x] 既定は Task::promise_type
    - [x] 他人の型には特殊化で足す

## 関連ページ

- [cpprefjp: std::coroutine_traits](https://cpprefjp.github.io/reference/coroutine/coroutine_traits.html)
- [cppreference: std::coroutine_traits](https://en.cppreference.com/w/cpp/coroutine/coroutine_traits)
