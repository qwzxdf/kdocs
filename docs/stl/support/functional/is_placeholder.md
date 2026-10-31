---
title: std::is_placeholder
summary: "型がプレースホルダー（_1 など）か、何番かを調べる型特性。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::is_placeholder

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

`std::bind` の内部は、引数の中から「これは `_1` だ」「これは `_2` だ」と印を見分けて、呼び出し時の引数を入れていきます。その見分けに使う型特性が `std::is_placeholder<T>` です。`T` が `_N` なら `N` を、そうでなければ `0` を返します。

!!! tip "ポイント"
    - `is_placeholder<T>::value` は、`_N` なら `N`、そうでなければ `0`
    - `std::is_placeholder_v<T>` が短縮形（C++17）
    - `bind` の実装が使う。普通のコードでは使わない
    - 自作のプレースホルダーを `bind` に認識させるときに特殊化する

!!! info "このページを読む前に"
    [`std::placeholders`](placeholders.md) を先に読んでください。

## 関数の詳しい説明

### std::is_placeholder {#is_placeholder}

```cpp
template <class T>
struct is_placeholder;

template <class T>
inline constexpr int is_placeholder_v = is_placeholder<T>::value;   // C++17
```

`is_placeholder<T>` は `std::integral_constant<int, N>` から派生します。`T` が `std::placeholders::_N` の型なら `N`、そうでなければ `0` です。

`std::placeholders::_1` の型は、実装が決める未規定の型なので、`decltype(_1)` で型を取ります。

自作のプレースホルダーの型を `bind` に使わせたいときは、`std::is_placeholder` を特殊化して、`N` を返します。この使い方は稀ですが、`bind` が「印」を認識する仕組みが、この型特性であることを知っておくと、`bind` の動きを理解しやすくなります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  using namespace std::placeholders;

  std::println("_1 の番号: {}", std::is_placeholder_v<decltype(_1)>);
  std::println("_2 の番号: {}", std::is_placeholder_v<decltype(_2)>);
  std::println("_3 の番号: {}", std::is_placeholder_v<decltype(_3)>);
  std::println("int の番号: {}", std::is_placeholder_v<int>);   // 印ではないので 0
}
```

```text title="実行結果"
_1 の番号: 1
_2 の番号: 2
_3 の番号: 3
int の番号: 0
```

## ゲームでの使いどころ

`bind` を自作するライブラリや、`bind` の式を解析するテンプレートを書くときに関わります。普通のゲーム コードでは、使いません。

## よくあるミス

??? failure "decltype を使わずに型を書こうとする"
    `_1` の型名は実装ごとに違います。`decltype(_1)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`placeholders`](placeholders.md) | 印そのもの |
| [`is_bind_expression`](is_bind_expression.md) | `bind` の式かどうかを調べる |
| [`bind`](bind.md) | 使う関数 |

## コンパイラ対応

C++11 から使えます。`is_placeholder_v` は C++17 からです。

## 関連ページ

- [cpprefjp: std::is_placeholder](https://cpprefjp.github.io/reference/functional/is_placeholder.html)
- [cppreference: std::is_placeholder](https://en.cppreference.com/w/cpp/utility/functional/is_placeholder)
