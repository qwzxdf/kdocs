---
title: std::is_class
summary: "型がクラス（struct を含む）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_class

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

構造体やクラスだけを受け取るテンプレートを書きたい。`std::is_class` は、<strong>型が `struct` または `class` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_class_v<T>` は、`T` が `struct` か `class`（共用体を除く）か
    - `class` と `struct` はどちらも `true`。`union` と `enum` は `false`
    - `std::is_class<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - ラムダ式の型も `true`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_class_v {#is_class}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_class_v = is_class<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`class` または `struct` で定義した型が `true` です。`union` と列挙型は `false` です。`std::string` やラムダ式の型（クロージャー型）、`std::array` もクラスなので `true` になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
enum class Color { kRed, kBlue };
union Number {
  int i;
  float f;
};

int main() {
  std::println("Player                     -> {}", std::is_class_v<Player>);
  std::println("Color                      -> {}", std::is_class_v<Color>);
  std::println("Number                     -> {}", std::is_class_v<Number>);
  std::println("int                        -> {}", std::is_class_v<int>);
}
```

```text title="実行結果"
Player                     -> true
Color                      -> false
Number                     -> false
int                        -> false
```

## ゲームでの使いどころ

クラス型のときだけメンバーを順に処理し、基本型はそのまま書く、シリアライズの入り口に使えます。

```cpp
template <class T>
void Write(std::ostream& os, const T& value) {
  if constexpr (std::is_class_v<T>) {
    value.Serialize(os);   // クラスは自分で書き出す
  } else {
    os.write(reinterpret_cast<const char*>(&value), sizeof(T));
  }
}
```

## よくあるミス

??? failure "union をクラスだと思う"
    `union` は `false` です。`std::is_union_v` で調べます。

??? failure "class か struct かの区別を期待する"
    `class` と `struct` はどちらも `true` です。区別はできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_union`](is_union.md) | `union` か |
| [`is_enum`](is_enum.md) | 列挙型か |
| [`is_object`](is_object.md) | 関数・参照・`void` 以外のすべてか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_class_v<T>` は、`T` が `struct` か `class`（共用体を除く）か
    - [x] `class` / `struct` が `true`、`union` と `enum` は `false`
    - [x] ラムダ式の型や `std::string` も `true`

## 関連ページ

- [cpprefjp: std::is_class](https://cpprefjp.github.io/reference/type_traits/is_class.html)
- [cppreference: std::is_class](https://en.cppreference.com/w/cpp/types/is_class)
