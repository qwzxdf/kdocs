---
title: std::move_if_noexcept
summary: "ムーブが例外を投げないときだけ、ムーブにする（そうでなければコピー）。"
order: 55
tags:
  - ユーティリティ
---

# std::move_if_noexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

`std::vector` が要素を増やして、内部の領域を引っ越すとき、要素をムーブすると速いですが、ムーブの途中で例外が飛ぶと、元の要素も壊れて、元に戻せなくなります。そこで、「ムーブが例外を投げない（`noexcept`）なら、ムーブ。投げるかもしれないなら、コピー」と使い分けたい。それを 1 つで書くのが `std::move_if_noexcept` です。

!!! tip "ポイント"
    - ムーブコンストラクターが `noexcept` なら、右辺値（ムーブ）にする
    - `noexcept` でなく、コピーできるなら、`const` の左辺値（コピー）にする
    - コピーできない型は、`noexcept` でなくても、ムーブにする
    - `std::vector` の再配置が、この考え方に従っている

!!! info "このページを読む前に"
    [`std::move`](../../basics/move.md) と `noexcept` を先に読んでください。

## 関数の詳しい説明

### std::move_if_noexcept {#move_if_noexcept}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
constexpr std::conditional_t<
    !std::is_nothrow_move_constructible_v<T> && std::is_copy_constructible_v<T>,
    const T&, T&&>
move_if_noexcept(T& x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `T&` | ムーブかコピーを選ぶ対象 |

戻り値の型は、次の条件で決まります。

| 条件 | 戻り値 |
| --- | --- |
| ムーブが `noexcept` | `T&&`（ムーブ） |
| ムーブが `noexcept` でなく、コピーできる | `const T&`（コピー） |
| ムーブが `noexcept` でなく、コピーもできない | `T&&`（ムーブ。他に手がない） |

「強い例外保証」を守るための道具です。コピー中に例外が飛んでも、元のオブジェクトは無傷なので、元に戻せます。ムーブ中に例外が飛ぶと、元のオブジェクトが壊れていて、戻せません。

自作の型には、ムーブコンストラクターに `noexcept` を付けておくと、`vector` の再配置が、コピーではなくムーブになり、速くなります。付け忘れは、気づきにくい性能の低下の原因です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <utility>

// ムーブが noexcept の型
struct Fast {
  Fast() = default;
  Fast(const Fast&) = default;
  Fast(Fast&&) noexcept = default;
};

// ムーブが noexcept でなく、コピーもできる型
struct Slow {
  Slow() = default;
  Slow(const Slow&) = default;
  Slow(Slow&&) {}  // noexcept がない
};

// ムーブしかできない型（コピー禁止）
struct MoveOnly {
  MoveOnly() = default;
  MoveOnly(MoveOnly&&) {}  // noexcept がない
};

int main() {
  Fast f;
  Slow s;
  MoveOnly m;

  static_assert(std::is_same_v<decltype(std::move_if_noexcept(f)), Fast&&>);
  static_assert(std::is_same_v<decltype(std::move_if_noexcept(s)), const Slow&>);
  static_assert(std::is_same_v<decltype(std::move_if_noexcept(m)), MoveOnly&&>);

  std::println("Fast はムーブ、Slow はコピー、MoveOnly はムーブ");
}
```

```text title="実行結果"
Fast はムーブ、Slow はコピー、MoveOnly はムーブ
```

## ゲームでの使いどころ

自作のコンテナを書くときの再配置で使います。それ以外では、自作の型のムーブコンストラクターに `noexcept` を付ける、という心がけが大切です。

## よくあるミス

??? failure "ムーブコンストラクターに noexcept を付け忘れる"
    `std::vector<MyType>` の再配置が、ムーブではなく、コピーになります。要素が多いと、大きな性能の差が出ます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::move` | 無条件に右辺値にする |
| [`std::forward`](forward.md) | 値カテゴリを保って転送する |
| `std::vector::reserve` | 再配置の回数を減らす |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::move_if_noexcept](https://cpprefjp.github.io/reference/utility/move_if_noexcept.html)
- [cppreference: std::move_if_noexcept](https://en.cppreference.com/w/cpp/utility/move_if_noexcept)
