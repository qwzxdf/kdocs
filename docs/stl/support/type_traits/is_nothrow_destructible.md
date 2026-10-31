---
title: std::is_nothrow_destructible
summary: "デストラクタが例外を投げない型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_destructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

デストラクターから例外が出ないことを保証したい。`std::is_nothrow_destructible` は、<strong>型の破棄が例外を投げないか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_destructible_v<T>` は、`T` の破棄が例外を投げないか
    - デストラクターは、既定で `noexcept`
    - `std::is_nothrow_destructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 例外を投げる型は、コンテナの要素に向かない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_destructible_v {#is_nothrow_destructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_nothrow_destructible_v = is_nothrow_destructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

デストラクターが `noexcept` なら `true` です。C++11 以降、デストラクターは既定で `noexcept` なので、ほとんどの型は `true` です。`~T() noexcept(false)` と明示した型だけが `false` になります。標準ライブラリのコンテナは、要素のデストラクターが例外を投げないことを前提にしています。

デストラクターから例外を投げると、`std::terminate` になることが多いので、基本は `noexcept` のままにします。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Thrower {
  ~Thrower() noexcept(false) {}
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                             -> {}", std::is_nothrow_destructible_v<Player>);
  std::println("std::string                        -> {}", std::is_nothrow_destructible_v<std::string>);
  std::println("Thrower                            -> {}", std::is_nothrow_destructible_v<Thrower>);
}
```

```text title="実行結果"
Player                             -> true
std::string                        -> true
Thrower                            -> false
```

## ゲームでの使いどころ

リソースを持つ型が、例外を投げずに破棄できることを、コンパイル時に確かめます。

```cpp
class Texture {
 public:
  ~Texture() { /* GPU のリソースを解放する */ }
};

static_assert(std::is_nothrow_destructible_v<Texture>, "デストラクターから例外を出してはいけません");
```

## よくあるミス

??? failure "デストラクターから例外を投げる"
    ほかの例外で巻き戻している最中に重なると、`std::terminate` で終了します。コンテナの破棄も壊れます。

??? failure "noexcept(false) を付ける"
    付けた型は `false` になり、標準のコンテナの要素にできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_destructible`](is_destructible.md) | 例外を考えずに、破棄できるか |
| [`is_trivially_destructible`](is_trivially_destructible.md) | 破棄が何もしないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_destructible_v<T>` は、`T` の破棄が例外を投げないか
    - [x] デストラクターの `noexcept` を調べる
    - [x] 既定は `true`。`noexcept(false)` だけが `false`

## 関連ページ

- [cpprefjp: std::is_nothrow_destructible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_destructible.html)
- [cppreference: std::is_nothrow_destructible](https://en.cppreference.com/w/cpp/types/is_nothrow_destructible)
