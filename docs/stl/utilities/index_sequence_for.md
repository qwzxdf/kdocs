---
title: std::index_sequence_for
summary: "型のパックの個数ぶんの index_sequence を作る。"
order: 900
tags:
  - ユーティリティ
---

# std::index_sequence_for

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

テンプレートの引数が `template <class... Ts>` のように可変個のとき、その個数に合った添字の列 `0, 1, ..., sizeof...(Ts)-1` が欲しくなります。`std::index_sequence_for<Ts...>` は、`make_index_sequence<sizeof...(Ts)>` の短い書き方で、パラメーター パックの個数と同じ長さの添字の列を作ります。

!!! tip "ポイント"
    - `index_sequence_for<Ts...>` は `make_index_sequence<sizeof...(Ts)>`
    - 型のパラメーター パックを渡すと、その個数ぶんの添字の列ができる
    - `tuple<Ts...>` の全要素の処理で、よく使う
    - 値のパックではなく、型のパックを渡す

!!! info "このページを読む前に"
    [`std::make_index_sequence`](make_index_sequence.md) を先に読んでください。

## 関数の詳しい説明

### std::index_sequence_for {#index_sequence_for}

<span class="ver ver-14">C++14</span>

```cpp
template <class... T>
using index_sequence_for = std::make_index_sequence<sizeof...(T)>;
```

`index_sequence_for<int, float, char>` は `index_sequence<0, 1, 2>` です。

`tuple<Ts...>` を受け取る関数で、`Ts...` の個数ぶんの添字を作るのに使います。

```cpp
template <class... Ts>
void Print(const std::tuple<Ts...>& t) {
  PrintImpl(t, std::index_sequence_for<Ts...>{});
}
```

`tuple` の型から `tuple_size_v` で個数を求めて `make_index_sequence` に渡すのと同じ結果ですが、パックを直接渡せるので、短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <tuple>
#include <type_traits>
#include <utility>

// 型の個数と同じ長さの添字の列
template <class... Ts>
constexpr std::size_t Count() {
  return std::index_sequence_for<Ts...>::size();
}

int main() {
  static_assert(std::is_same_v<std::index_sequence_for<int, float, char>,
                               std::index_sequence<0, 1, 2>>);

  std::println("3 個: {}", Count<int, float, char>());
  std::println("0 個: {}", Count<>());
}
```

```text title="実行結果"
3 個: 3
0 個: 0
```

## ゲームでの使いどころ

`tuple` にコンポーネントをまとめたとき、全部に処理をかけるテンプレート関数の、土台に使います。

## よくあるミス

??? failure "値のパックを渡す"
    `index_sequence_for` に渡すのは、型のパックです。値のパックなら `sizeof...` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_index_sequence`](make_index_sequence.md) | 個数を数で指定する |
| [`std::index_sequence`](index_sequence.md) | 作られる列の型 |
| [`std::apply`](apply.md) | 添字の展開を内部で使う |

## コンパイラ対応

C++14 から使えます。

## 関連ページ

- [cpprefjp: std::index_sequence_for](https://cpprefjp.github.io/reference/utility/index_sequence_for.html)
- [cppreference: std::index_sequence_for](https://en.cppreference.com/w/cpp/utility/integer_sequence)
