---
title: std::is_trivially_copy_constructible
summary: "コピーして構築するのが自明（メモリのコピーだけ）な型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_copy_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`memcpy` で複製してよい型かを知りたい。`std::is_trivially_copy_constructible` は、<strong>型が自明なコピーコンストラクターを持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_copy_constructible_v<T>` は、`T` が自明なコピーコンストラクターを持つか
    - ポインターを持つだけの型も `true`（所有権は別の話）
    - `std::is_trivially_copy_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 仮想関数を持つ型は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_copy_constructible_v {#is_trivially_copy_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivially_copy_constructible_v = is_trivially_copy_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

コピーするとき、メンバーのビットをそのまま写すだけの型なら `true` です。ポインターを持つ型も、ポインターの値を写すだけなら `true` になります（所有権の扱いは別の話です）。`std::string` のように、コピーで動的メモリを確保する型や、仮想関数を持つ型は `false` です。

`true` でも、ポインタが指す先を共有する点に注意します。

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
  std::println("Player                             -> {}", std::is_trivially_copy_constructible_v<Player>);
  std::println("int                                -> {}", std::is_trivially_copy_constructible_v<int>);
  std::println("std::string                        -> {}", std::is_trivially_copy_constructible_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

配列を別の場所へ複製するとき、自明な型なら `memcpy`、そうでなければコンストラクターを呼ぶ複製を選びます。

```cpp
template <class T>
T* Clone(const T* src, std::size_t n) {
  T* dst = static_cast<T*>(::operator new(sizeof(T) * n));
  if constexpr (std::is_trivially_copy_constructible_v<T>) {
    std::memcpy(dst, src, sizeof(T) * n);
  } else {
    std::uninitialized_copy_n(src, n, dst);
  }
  return dst;
}
```

## よくあるミス

??? failure "ポインターを持つ型を複製して二重解放する"
    ポインターを持つだけの型は自明に複製できますが、指す先の所有権まではコピーされません。両方で解放すると二重解放です。

??? failure "仮想関数を持つ型で memcpy する"
    仮想関数のテーブルのポインターを持つので、`false` です。`memcpy` で写すのは未定義動作の恐れがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_copy_constructible`](is_copy_constructible.md) | 自明さを考えずに、コピー構築できるか |
| [`is_trivially_copyable`](is_trivially_copyable.md) | コピー全体の自明さ |
| [`is_trivially_move_constructible`](is_trivially_move_constructible.md) | ムーブ構築の自明さ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_copy_constructible_v<T>` は、`T` が自明なコピーコンストラクターを持つか
    - [x] コピー構築が `memcpy` で済む型が `true`
    - [x] 所有権の扱いは別に考える

## 関連ページ

- [cpprefjp: std::is_trivially_copy_constructible](https://cpprefjp.github.io/reference/type_traits/is_trivially_copy_constructible.html)
- [cppreference: std::is_trivially_copy_constructible](https://en.cppreference.com/w/cpp/types/is_trivially_copy_constructible)
