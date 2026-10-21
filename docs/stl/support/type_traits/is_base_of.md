---
title: std::is_base_of
summary: "ある型が、別の型の基底クラスかを調べる。"
order: 8
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_base_of

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

`std::is_base_of_v<Base, Derived>` は、**`Base` が `Derived` の基底クラス（または同じ型）か**を調べます。テンプレートで、「このクラスの派生クラスだけ受け取る」という制約に使います。コンセプト版は `std::derived_from` です。

!!! tip "ポイント"
    - **基底が先、派生が後**。
    - 同じ型どうしも `true`（クラスの場合）。
    - private 継承でも `true`。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_base_of_v {#is_base_of}

```cpp
template <class Base, class Derived>
inline constexpr bool is_base_of_v;
```

- Derived が Base を継承していれば true。「Component を継承した型だけ AddComponent できる」のチェックに使えます

```cpp
#include <print>
#include <type_traits>

struct Component {};
struct Transform : Component {};
struct NotComponent {};

template <class T>
void AddComponent() {
  static_assert(std::is_base_of_v<Component, T>, "Component を継承していない");
  std::println("追加した");
}

int main() {
  AddComponent<Transform>();
  // AddComponent<NotComponent>();  // コンパイルエラー
  std::println("{} {}", std::is_pointer_v<int*>, std::is_enum_v<int>);
}
```

```text title="実行結果"
追加した
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| Component の派生だけを受け取るテンプレート | `static_assert(std::is_base_of_v<Component, T>)` |

## よくあるミス

??? failure "引数の順番を逆にする"
    `is_base_of_v<Derived, Base>` は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::derived_from` | コンセプト版（C++20） |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基底クラスかを調べる
    - [x] 基底が先、派生が後
    - [x] コンセプト版もある

## 関連ページ

- [cpprefjp: std::is_base_of](https://cpprefjp.github.io/reference/type_traits/is_base_of.html)
- [cppreference: std::is_base_of](https://en.cppreference.com/w/cpp/types/is_base_of)
