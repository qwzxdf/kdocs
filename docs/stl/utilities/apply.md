---
title: std::apply
summary: "tuple の中身をばらして、関数の引数として渡す。"
order: 54
tags:
  - ユーティリティ
---

# std::apply

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <tuple>`
</div>

`std::tuple` に引数を保存しておいて、あとで関数に渡したい。ところが、`f(t)` と書くと、`tuple` 全体が 1 つの引数になってしまいます。`std::apply(f, t)` は、`tuple` の要素を 1 つずつばらして、`f(get<0>(t), get<1>(t), ...)` の形で呼びます。

イベントのキューに、「あとで実行する関数と引数」を入れておく、遅延呼び出しの仕組みを作るときに使います。

!!! tip "ポイント"
    - `std::apply(f, t)` は `f(get<0>(t), get<1>(t), ...)` と同じ
    - 呼び出せるものなら何でもよい（関数、ラムダ、メンバー関数ポインタ）
    - 戻り値は `f` の戻り値
    - `pair` や `std::array` も渡せる

!!! info "このページを読む前に"
    [`std::make_tuple`](make_tuple.md) を先に読んでください。

## 関数の詳しい説明

### std::apply {#apply}

<span class="ver ver-17">C++17</span>

```cpp
template <class F, class Tuple>
constexpr decltype(auto) apply(F&& f, Tuple&& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出し可能なもの | 呼び出す関数 |
| `t` | `tuple` / `pair` / `array` | 引数として展開する値 |

`t` の要素を、順に引数にして `f` を呼び、その戻り値を返します。要素の数が `f` の引数の数に合わなければ、コンパイル エラーです。

`t` が右辺値なら、要素は右辺値として渡されます（ムーブされる）。左辺値なら、左辺値として渡されます。

メンバー関数ポインタを `f` にするなら、`t` の先頭の要素がオブジェクトで、それ以降が引数です。

```cpp
std::apply(&Player::Heal, std::make_tuple(&player, 10));   // player.Heal(10)
```

### 遅延呼び出し {#deferred}

引数を `tuple` に保存して、ラムダに入れておけば、あとで好きなときに実行できます。

```cpp
auto task = [f, args = std::make_tuple(1, 2, 3)] { return std::apply(f, args); };
```

## 実際に動かしてみる

```cpp
#include <print>
#include <tuple>
#include <utility>

int Add(int a, int b, int c) { return a + b + c; }

int main() {
  const auto args = std::make_tuple(1, 2, 3);
  std::println("{}", std::apply(Add, args));  // Add(1, 2, 3)

  // ラムダでも使える
  const int r = std::apply([](int a, int b) { return a * b; }, std::make_pair(6, 7));
  std::println("{}", r);

  // 遅延呼び出し: 引数を保存しておき、あとで実行する
  auto task = [args = std::make_tuple(10, 20, 30)] { return std::apply(Add, args); };
  std::println("{}", task());
}
```

```text title="実行結果"
6
42
60
```

## ゲームでの使いどころ

ジョブ システムで、「関数と引数」を 1 つのタスクにまとめてキューに入れ、ワーカー スレッドで実行するときに使います。

## よくあるミス

??? failure "要素数と引数の数が合わない"
    `tuple` の要素が 3 つで、関数の引数が 2 つだと、コンパイル エラーです。

??? failure "保存した参照が、実行時には無効"
    `tuple` に参照を入れて、あとで実行すると、参照先が消えているかもしれません。値で保存します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_from_tuple`](make_from_tuple.md) | 展開してコンストラクターを呼ぶ |
| [`std::invoke`](../support/functional/invoke.md) | 引数を並べて呼ぶ |
| [`std::tuple_cat`](tuple_cat.md) | `tuple` をつなげる |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::apply](https://cpprefjp.github.io/reference/tuple/apply.html)
- [cppreference: std::apply](https://en.cppreference.com/w/cpp/utility/apply)
