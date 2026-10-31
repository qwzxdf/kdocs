---
title: std::forward_like
summary: "別の式の値カテゴリ（左辺値 / 右辺値、const）を、メンバにも引き継いで転送する。"
order: 900
tags:
  - ユーティリティ
---

# std::forward_like

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <utility>`
</div>

オブジェクトのメンバーを、そのオブジェクトの「参照のしかた」に合わせて渡したい。たとえば、`obj` を右辺値で受けたなら、そのメンバーも右辺値として転送したい。`std::forward<T>(x)` は、`x` の型 `T` で値カテゴリを決めますが、`forward_like<T>(x)` は、別の型 `T` の値カテゴリ（`const` や、左辺値か右辺値か）を、`x` に写し取って転送します。

!!! tip "ポイント"
    - `std::forward_like<T>(x)` は、`T` の値カテゴリと `const` を、`x` に与える
    - 親のオブジェクトの参照のしかたに合わせて、メンバーを転送する
    - C++23。deducing this（明示的なオブジェクト引数）と組み合わせて使う
    - 普通の転送には、`std::forward`

!!! info "このページを読む前に"
    [`std::forward`](forward.md) を先に読んでください。

## 関数の詳しい説明

### std::forward_like {#forward_like}

<span class="ver ver-23">C++23</span>

```cpp
template <class T, class U>
constexpr auto&& forward_like(U&& x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 値カテゴリと `const` の元にする型 |
| `x` | `U&&` | 転送する値 |

戻り値の型は、`T` が左辺値参照か右辺値参照か、`const` かで決まります。

| `T` | 戻り値の型（`x` が `int` のとき） |
| --- | --- |
| `int&` | `int&` |
| `const int&` | `const int&` |
| `int&&` | `int&&` |
| `const int&&` | `const int&&` |

`T` の `const` が、`x` の `const` に足されます。`T` が非 const でも、`x` が `const` なら、`const` のままです。

用途は、オブジェクトのメンバーを返すメンバー関数で、`self` の種類に応じた参照を返すことです。

```cpp
template <class Self>
auto&& Name(this Self&& self) {
  return std::forward_like<Self>(self.name);
}
```

`self` が右辺値なら `name` も右辺値、`const` の左辺値なら `const` の左辺値で返ります。これを、`const` 用、非 const 用、右辺値用の 3 つに書き分ける必要が、なくなります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <utility>

struct Player {
  int level = 5;

  // self の種類に合わせて、level を返す
  template <class Self>
  auto&& Level(this Self&& self) {
    return std::forward_like<Self>(self.level);
  }
};

int main() {
  int x = 1;
  static_assert(std::is_same_v<decltype(std::forward_like<int&>(x)), int&>);
  static_assert(std::is_same_v<decltype(std::forward_like<const int&>(x)), const int&>);
  static_assert(std::is_same_v<decltype(std::forward_like<int&&>(x)), int&&>);

  Player p;
  const Player cp;
  static_assert(std::is_same_v<decltype(p.Level()), int&>);
  static_assert(std::is_same_v<decltype(cp.Level()), const int&>);
  static_assert(std::is_same_v<decltype(Player{}.Level()), int&&>);

  std::println("{}", p.Level());
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

自作のコンテナやラッパーで、中身を返す関数を、`const` の有無・右辺値の有無に対応させるときに使います。

## よくあるミス

??? failure "std::forward と取り違える"
    `forward<T>(x)` は、`x` の型 `T` の値カテゴリで転送します。`forward_like<T>(x)` は、別の型 `T` の値カテゴリを借ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::forward`](forward.md) | 自分の型の値カテゴリで転送する |
| `std::move` | 無条件に右辺値にする |
| [`std::move_if_noexcept`](move_if_noexcept.md) | 条件つきでムーブする |

## コンパイラ対応

C++23 から使えます。deducing this（`this Self&&`）に対応した処理系が要ります。

## 関連ページ

- [cpprefjp: std::forward_like](https://cpprefjp.github.io/reference/utility/forward_like.html)
- [cppreference: std::forward_like](https://en.cppreference.com/w/cpp/utility/forward_like)
