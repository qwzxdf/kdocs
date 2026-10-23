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

`std::apply` は、**tuple の要素を 1 つずつばらして、関数の引数として呼び出す**関数です。`std::apply(f, std::tuple{1, 2, 3})` は `f(1, 2, 3)` と同じです。可変引数テンプレートで保存しておいた引数を、あとで関数に渡すときに使います。

!!! tip "ポイント"
    - 引数を `std::tuple` に保存しておき、あとで実行する「遅延呼び出し」に使う。
    - ラムダ式にも渡せる。
    - 逆に、値から tuple を作る関数は [`std::make_tuple`](make_tuple.md)、クラスを作るのは [`std::make_from_tuple`](make_from_tuple.md)。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::apply {#apply}

```cpp
template <class F, class Tuple>
constexpr decltype(auto) apply(F&& f, Tuple&& t);
```

- tuple の中身をばらして、関数の引数として渡します

```cpp
#include <print>
#include <tuple>

int Add(int a, int b, int c) { return a + b + c; }

int main() {
  std::tuple args = {1, 2, 3};
  std::println("{} {}", std::apply(Add, args), std::tuple_size_v<decltype(args)>);
  auto t = std::make_tuple(1, 'a');
  std::println("{}", t);
}
```

```text title="実行結果"
6 3
(1, 'a')
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ジョブ（関数と引数）を保存して、あとでスレッドで実行する | `std::apply(job, saved_args)` |
| イベントの引数をまとめて渡す | `std::apply(callback, args)` |

## よくあるミス

??? failure "tuple の要素数と引数の数が違う"
    要素数と関数の引数の数が合わないと、コンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::invoke`](../support/functional/invoke.md) | 関数を呼び出す。引数はばらしたもの |
| [`std::make_from_tuple`](make_from_tuple.md) | tuple からクラスを作る |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tuple をばらして関数に渡す
    - [x] 引数の保存と遅延実行に使う
    - [x] C++17

## 関連ページ

- [cpprefjp: std::apply](https://cpprefjp.github.io/reference/tuple/apply.html)
- [cppreference: std::apply](https://en.cppreference.com/w/cpp/utility/apply)
