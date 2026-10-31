---
title: std::allocator_arg
summary: "「次の引数はアロケータ」と示す目印。"
order: 900
tags:
  - メモリ
---

# std::allocator_arg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

アロケーターを受け取れるクラス（`std::tuple` やコンテナ）のコンストラクターは、普通の引数と、アロケーターの引数を区別できる必要があります。`(int, std::allocator)` なのか、`(std::allocator, int)` なのか、曖昧になるからです。`std::allocator_arg` は、「次の引数はアロケーターです」と伝える目印です。

!!! tip "ポイント"
    - コンストラクターの第 1 引数に `std::allocator_arg`、第 2 引数にアロケーターを渡す
    - `std::tuple`、`std::function`（C++17 まで）などが使う
    - 値を持たない空の型 `allocator_arg_t` の定数
    - 自作のクラスを uses-allocator 構築に対応させるときに使う

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::allocator_arg {#allocator_arg}

<span class="ver ver-11">C++11</span>

```cpp
struct allocator_arg_t { explicit allocator_arg_t() = default; };
inline constexpr std::allocator_arg_t allocator_arg{};
```

`uses_allocator` が真の型は、アロケーターを受け取る2通りの構築を持つ決まりです。

1. `T(std::allocator_arg, alloc, args...)`（先頭に印とアロケーター）
2. `T(args..., alloc)`（末尾にアロケーター）

`allocator_arg` を先頭にする形は、`std::tuple` のように、引数が可変個で、末尾に足すと紛らわしい型で使われます。

`std::make_obj_using_allocator` などの標準の道具が、型に応じてどちらかの形を自動で選んでくれるので、自分で書く場面は、アロケーター対応のクラスを作るときだけです。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <tuple>

int main() {
  // tuple にアロケーターを渡して作る
  std::tuple<int, double> t(std::allocator_arg, std::allocator<int>(), 5, 2.5);
  std::println("{} {}", std::get<0>(t), std::get<1>(t));
}
```

```text title="実行結果"
5 2.5
```

## ゲームでの使いどころ

自作のコンテナを、`std::scoped_allocator_adaptor` に対応させるときに必要です。普段は触りません。

## よくあるミス

??? failure "印を付けずにアロケーターを渡す"
    普通の引数と区別できず、型が合いません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uses_allocator`](uses_allocator.md) | 型がアロケーターを受け取れるかの特性 |
| [`make_obj_using_allocator`](make_obj_using_allocator.md) | 自動で構築方法を選ぶ |
| [`scoped_allocator_adaptor`](scoped_allocator_adaptor.md) | 入れ子のコンテナに伝える |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::allocator_arg](https://cpprefjp.github.io/reference/memory/allocator_arg_t.html)
- [cppreference: std::allocator_arg](https://en.cppreference.com/w/cpp/memory/allocator_arg_t)
