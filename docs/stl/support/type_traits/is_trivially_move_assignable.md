---
title: std::is_trivially_move_assignable
summary: "ムーブ代入が自明（メモリのコピーだけ）な型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_move_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

ムーブ代入がビットの複製だけで済む型かを知りたい。`std::is_trivially_move_assignable` は、<strong>型が自明なムーブ代入を持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_move_assignable_v<T>` は、`T` が自明なムーブ代入を持つか
    - リソースを管理する型は `false`
    - `std::is_trivially_move_assignable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `memmove` で済ませてよい型の目印

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_move_assignable_v {#is_trivially_move_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivially_move_assignable_v = is_trivially_move_assignable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

ムーブ代入が、ビットを写すだけで済む型なら `true` です。`int` や数値だけの構造体がそうです。`std::unique_ptr` や `std::string` のような、リソースを管理する型は、元のオブジェクトを空にする処理が必要なので `false` です。

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
  std::println("Player                             -> {}", std::is_trivially_move_assignable_v<Player>);
  std::println("int                                -> {}", std::is_trivially_move_assignable_v<int>);
  std::println("std::string                        -> {}", std::is_trivially_move_assignable_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

配列の要素を、前へ詰める処理で、自明な型なら `memmove` を使います。

```cpp
template <class T>
void ShiftLeft(T* data, std::size_t n) {
  if constexpr (std::is_trivially_move_assignable_v<T>) {
    std::memmove(data, data + 1, sizeof(T) * (n - 1));   // ビットを移動する
  } else {
    std::move(data + 1, data + n, data);                 // ムーブ代入を 1 つずつ呼ぶ
  }
}
```

## よくあるミス

??? failure "unique_ptr を memmove で詰める"
    元のオブジェクトの中身を空にする処理が飛ぶので、壊れます。`false` を返す型には、使いません。

??? failure "コピーが自明ならムーブも自明だと思う"
    コピー代入とムーブ代入は別に定義できます。別々に調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_move_assignable`](is_move_assignable.md) | 自明さを考えずに、ムーブ代入できるか |
| [`is_trivially_copy_assignable`](is_trivially_copy_assignable.md) | コピー代入の自明さ |
| [`is_trivially_move_constructible`](is_trivially_move_constructible.md) | ムーブ構築の自明さ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_move_assignable_v<T>` は、`T` が自明なムーブ代入を持つか
    - [x] ムーブ代入の自明さを調べる
    - [x] memmove の近道を選ぶ条件になる

## 関連ページ

- [cpprefjp: std::is_trivially_move_assignable](https://cpprefjp.github.io/reference/type_traits/is_trivially_move_assignable.html)
- [cppreference: std::is_trivially_move_assignable](https://en.cppreference.com/w/cpp/types/is_trivially_move_assignable)
