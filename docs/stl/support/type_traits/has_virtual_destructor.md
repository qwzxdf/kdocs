---
title: std::has_virtual_destructor
summary: "型が仮想デストラクタを持つかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::has_virtual_destructor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

基底クラスのポインターで派生クラスを `delete` するには、基底クラスのデストラクターが仮想でなければなりません。`std::has_virtual_destructor` は、<strong>型が仮想デストラクターを持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::has_virtual_destructor_v<T>` は、`T` が仮想デストラクターを持つか
    - 基底クラスから受け継いだ仮想デストラクターも `true`
    - `std::has_virtual_destructor<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 仮想関数があっても、デストラクターが非仮想なら `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::has_virtual_destructor_v {#has_virtual_destructor}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool has_virtual_destructor_v = has_virtual_destructor<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

基底クラスのデストラクターが `virtual` なら `true` です。派生クラスでは、基底から受け継いだ場合も `true` です。仮想デストラクターを持たない基底クラスのポインターから `delete` すると、派生クラスのデストラクターが呼ばれず、未定義動作になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Animal {
  virtual ~Animal() = default;
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Animal                             -> {}", std::has_virtual_destructor_v<Animal>);
  std::println("Player                             -> {}", std::has_virtual_destructor_v<Player>);
  std::println("int                                -> {}", std::has_virtual_destructor_v<int>);
}
```

```text title="実行結果"
Animal                             -> true
Player                             -> false
int                                -> false
```

## ゲームでの使いどころ

基底クラスとして使うテンプレートに、破棄の安全性の確認を足します。

```cpp
template <class Base>
class Handle {
  static_assert(std::has_virtual_destructor_v<Base>, "基底クラスには仮想デストラクターが必要です");
  std::unique_ptr<Base> ptr_;
};
```

## よくあるミス

??? failure "仮想関数があれば安心だと思う"
    仮想関数があっても、デストラクターが `virtual` でなければ `false` です。基底クラスのポインターで消すと未定義動作です。

??? failure "派生クラスだけに virtual を付ける"
    基底クラスのデストラクターが非仮想なら、派生クラスのデストラクターが `virtual` でも、基底クラス経由の `delete` は安全になりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_polymorphic`](is_polymorphic.md) | 仮想関数を持つか |
| [`is_abstract`](is_abstract.md) | 純粋仮想関数を持つか |
| [`is_destructible`](is_destructible.md) | 破棄できるか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::has_virtual_destructor_v<T>` は、`T` が仮想デストラクターを持つか
    - [x] 仮想デストラクターを持つ型が `true`
    - [x] 基底クラスのポインターから消すなら必須

## 関連ページ

- [cpprefjp: std::has_virtual_destructor](https://cpprefjp.github.io/reference/type_traits/has_virtual_destructor.html)
- [cppreference: std::has_virtual_destructor](https://en.cppreference.com/w/cpp/types/has_virtual_destructor)
