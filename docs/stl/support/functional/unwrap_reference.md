---
title: std::unwrap_reference
summary: "reference_wrapper を、ふつうの参照の型に戻す型変換。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::unwrap_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <functional>`
</div>

`std::reference_wrapper<T>` は、参照をコピーできる値として持ち運ぶための型です。ところが、それを受け取ったテンプレートは、「中身の参照 `T&` として扱いたい」ことがあります。`std::unwrap_reference<T>` は、`T` が `reference_wrapper<U>` なら `U&`、そうでなければ `T` そのものを返す型変換です。

!!! tip "ポイント"
    - `unwrap_reference_t<reference_wrapper<int>>` は `int&`
    - `reference_wrapper` でない型は、そのまま（`int` は `int`）
    - `decay` はしない。`unwrap_ref_decay` は `decay` もする
    - C++20 で追加された

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::unwrap_reference {#unwrap_reference}

<span class="ver ver-20">C++20</span>

```cpp
template <class T> struct unwrap_reference;
template <class T> using unwrap_reference_t = typename unwrap_reference<T>::type;
```

`T` が `std::reference_wrapper<U>` の特殊化なら `type` は `U&`、そうでなければ `T` です。`std::ref(x)` で包んだものを、`x` への参照として扱いたいときに使います。

`const` や参照は、そのまま保たれます。`int&` を渡すと `int&`、`const int` を渡すと `const int` です。`decay`（配列や関数のポインターへの変換、`const` の除去）はしないのが、[`unwrap_ref_decay`](unwrap_ref_decay.md) との違いです。

`std::make_tuple` や `std::thread` のように、引数をコピーして保存する関数が、`std::ref` で包まれたものだけは参照として保存する、という仕組みの部品に使われます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <type_traits>

// reference_wrapper なら中身の参照、そうでなければそのまま受け取る
template <class T>
std::unwrap_reference_t<T>& Unwrap(T& v) {
  return v;
}

int main() {
  static_assert(std::is_same_v<std::unwrap_reference_t<std::reference_wrapper<int>>, int&>);
  static_assert(std::is_same_v<std::unwrap_reference_t<int>, int>);
  static_assert(std::is_same_v<std::unwrap_reference_t<const int>, const int>);

  int hp = 10;
  auto wrapped = std::ref(hp);   // reference_wrapper<int>
  Unwrap(wrapped) += 5;          // hp への参照として扱える
  std::println("hp = {}", hp);

  int mp = 3;
  Unwrap(mp) += 1;               // 普通の int もそのまま
  std::println("mp = {}", mp);
}
```

```text title="実行結果"
hp = 15
mp = 4
```

## ゲームでの使いどころ

`std::ref` で包まれた引数を、参照として受け取る汎用のテンプレートを書くときに使います。

## よくあるミス

??? failure "配列や const を除きたいのに使う"
    `decay` はしません。除きたいなら `unwrap_ref_decay` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unwrap_ref_decay`](unwrap_ref_decay.md) | `decay` も行う版 |
| [`reference_wrapper`](reference_wrapper.md) | 参照を持ち運ぶ型 |
| [`ref`](ref.md) | `reference_wrapper` を作る |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::unwrap_reference](https://cpprefjp.github.io/reference/functional/unwrap_reference.html)
- [cppreference: std::unwrap_reference](https://en.cppreference.com/w/cpp/utility/functional/unwrap_reference)
