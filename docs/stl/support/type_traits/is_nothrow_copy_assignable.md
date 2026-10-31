---
title: std::is_nothrow_copy_assignable
summary: "例外を投げずにコピー代入できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_copy_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

例外安全性の判断に使いたい。`std::is_nothrow_copy_assignable` は、<strong>型のコピー代入が例外を投げないか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_copy_assignable_v<T>` は、`T` のコピー代入が例外を投げないか
    - メモリを確保しない型は `true`、確保する型は `false`
    - `std::is_nothrow_copy_assignable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `= default` なら、メンバーの性質で決まる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_copy_assignable_v {#is_nothrow_copy_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_nothrow_copy_assignable_v = is_nothrow_copy_assignable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

コピー代入（`T& = const T&`）が `noexcept` と宣言されていれば `true` です。`int` や座標の構造体のように、メモリを確保しない型は `true`、`std::string` や `std::vector` のようにメモリを確保する型は `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                             -> {}", std::is_nothrow_copy_assignable_v<Player>);
  std::println("int                                -> {}", std::is_nothrow_copy_assignable_v<int>);
  std::println("std::string                        -> {}", std::is_nothrow_copy_assignable_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

代入の途中で例外が出ても、元の値が壊れないようにしたい処理で、安全な方法を選びます。

```cpp
template <class T>
void Store(T& dst, const T& src) {
  if constexpr (std::is_nothrow_copy_assignable_v<T>) {
    dst = src;                 // 例外が出ないので、直接代入してよい
  } else {
    T tmp = src;               // 先にコピーを作る（ここで例外が出ても dst は無事）
    dst = std::move(tmp);
  }
}
```

## よくあるミス

??? failure "noexcept を付け忘れて false になる"
    自作の代入演算子に `noexcept` を付けないと、中身が確保をしなくても `false` です。`= default` なら、メンバーの性質で決まります。

??? failure "ムーブ代入と取り違える"
    右辺値からの代入は `is_nothrow_move_assignable` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_nothrow_move_assignable`](is_nothrow_move_assignable.md) | ムーブ代入が例外を投げないか |
| [`is_copy_assignable`](is_copy_assignable.md) | 例外を考えずに、コピー代入できるか |
| [`is_nothrow_assignable`](is_nothrow_assignable.md) | 型の違う代入も含む |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_copy_assignable_v<T>` は、`T` のコピー代入が例外を投げないか
    - [x] コピー代入の `noexcept` を調べる
    - [x] 確保をする型は `false`

## 関連ページ

- [cpprefjp: std::is_nothrow_copy_assignable](https://cpprefjp.github.io/reference/type_traits/is_nothrow_copy_assignable.html)
- [cppreference: std::is_nothrow_copy_assignable](https://en.cppreference.com/w/cpp/types/is_nothrow_copy_assignable)
