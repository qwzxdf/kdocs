---
title: std::is_trivially_move_constructible
summary: "ムーブして構築するのが自明（メモリのコピーだけ）な型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_move_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

ムーブがビットの複製だけで済む型かを知りたい。`std::is_trivially_move_constructible` は、<strong>型が自明なムーブコンストラクターを持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_move_constructible_v<T>` は、`T` が自明なムーブコンストラクターを持つか
    - リソースを管理する型は `false`
    - `std::is_trivially_move_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 数値だけの構造体は `true`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_move_constructible_v {#is_trivially_move_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivially_move_constructible_v = is_trivially_move_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

ムーブするとき、ビットを写すだけでよい型なら `true` です。`std::unique_ptr` や `std::string` は、元のオブジェクトを空にする処理があるので `false` です。数値だけの構造体は `true` です。

自明なムーブは、コピーと同じ扱いになります。

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
  std::println("Player                             -> {}", std::is_trivially_move_constructible_v<Player>);
  std::println("int                                -> {}", std::is_trivially_move_constructible_v<int>);
  std::println("std::string                        -> {}", std::is_trivially_move_constructible_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

要素を別の場所へ移す処理で、自明な型なら `memcpy` で移します。

```cpp
template <class T>
void Relocate(T* dst, T* src, std::size_t n) {
  if constexpr (std::is_trivially_move_constructible_v<T>) {
    std::memcpy(dst, src, sizeof(T) * n);
  } else {
    std::uninitialized_move_n(src, n, dst);
    std::destroy_n(src, n);   // 元のオブジェクトは破棄する
  }
}
```

## よくあるミス

??? failure "unique_ptr の配列を memcpy で移す"
    移した後に、元のポインターが残って、二重解放になります。`false` の型には、使いません。

??? failure "コピーが自明なら、ムーブも自明だと思う"
    別に定義できるので、別々に調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_move_constructible`](is_move_constructible.md) | 自明さを考えずに、ムーブ構築できるか |
| [`is_trivially_copy_constructible`](is_trivially_copy_constructible.md) | コピー構築の自明さ |
| [`is_trivially_move_assignable`](is_trivially_move_assignable.md) | ムーブ代入の自明さ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_move_constructible_v<T>` は、`T` が自明なムーブコンストラクターを持つか
    - [x] ムーブ構築の自明さを調べる
    - [x] memcpy で移してよい型の目印

## 関連ページ

- [cpprefjp: std::is_trivially_move_constructible](https://cpprefjp.github.io/reference/type_traits/is_trivially_move_constructible.html)
- [cppreference: std::is_trivially_move_constructible](https://en.cppreference.com/w/cpp/types/is_trivially_move_constructible)
