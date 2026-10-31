---
title: std::is_trivially_copy_assignable
summary: "コピー代入が自明（メモリのコピーだけ）な型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_copy_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

代入がビットの複製だけで済む型かを知りたい。`std::is_trivially_copy_assignable` は、<strong>型が自明なコピー代入を持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_copy_assignable_v<T>` は、`T` が自明なコピー代入を持つか
    - ビットを写すだけで済む代入が対象
    - `std::is_trivially_copy_assignable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 仮想関数を持つ型は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_copy_assignable_v {#is_trivially_copy_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivially_copy_assignable_v = is_trivially_copy_assignable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

代入するとき、ビットをそのまま写すだけでよい型なら `true` です。`int` や数値だけの構造体がそうです。`std::string` のように、代入で古いメモリを解放して新しく確保する型や、仮想関数を持つ型は `false` です。

配列全体を `memcpy` で更新できる型かの判断に使います。

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
  std::println("Player                             -> {}", std::is_trivially_copy_assignable_v<Player>);
  std::println("int                                -> {}", std::is_trivially_copy_assignable_v<int>);
  std::println("std::string                        -> {}", std::is_trivially_copy_assignable_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

配列を別の配列へコピーするとき、自明な型なら `memcpy` を使います。

```cpp
template <class T>
void Assign(T* dst, const T* src, std::size_t n) {
  if constexpr (std::is_trivially_copy_assignable_v<T>) {
    std::memcpy(dst, src, sizeof(T) * n);
  } else {
    std::copy_n(src, n, dst);   // 代入を 1 つずつ呼ぶ
  }
}
```

## よくあるミス

??? failure "仮想関数を持つ型で true を期待する"
    仮想関数を持つ型は、コピー代入が自明ではありません。`false` です。

??? failure "ポインターのコピーが安全だと思う"
    ポインターを持つ構造体は `true` になります。ただし、指す先は共有されるだけで、所有権の管理は別の話です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_copy_assignable`](is_copy_assignable.md) | 自明さを考えずに、コピー代入できるか |
| [`is_trivially_copy_constructible`](is_trivially_copy_constructible.md) | コピー構築の自明さ |
| [`is_trivially_copyable`](is_trivially_copyable.md) | コピー全体の自明さ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_copy_assignable_v<T>` は、`T` が自明なコピー代入を持つか
    - [x] コピー代入の自明さを調べる
    - [x] memcpy の近道を選ぶ条件になる

## 関連ページ

- [cpprefjp: std::is_trivially_copy_assignable](https://cpprefjp.github.io/reference/type_traits/is_trivially_copy_assignable.html)
- [cppreference: std::is_trivially_copy_assignable](https://en.cppreference.com/w/cpp/types/is_trivially_copy_assignable)
