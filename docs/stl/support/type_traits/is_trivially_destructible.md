---
title: std::is_trivially_destructible
summary: "破棄が自明（何もしなくてよい）な型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_destructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

メモリを解放するだけで、デストラクターを呼ぶ必要がない型かを知りたい。`std::is_trivially_destructible` は、<strong>型が自明なデストラクターを持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_destructible_v<T>` は、`T` が自明なデストラクターを持つか
    - 仮想デストラクターを持つ型は `false`
    - `std::is_trivially_destructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 自明な型は、破棄の処理を省ける

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_destructible_v {#is_trivially_destructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivially_destructible_v = is_trivially_destructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

破棄するとき、何もしなくてよい型なら `true` です。`int` や、数値だけの構造体がそうです。仮想デストラクターを持つ型や、`std::string` のように資源を持つ型は `false` です。自明なデストラクターの型は、`std::vector` などが破棄のループを省けます。

オブジェクト プールなどで、メモリを再利用するときに、デストラクターの呼び出しを省けるかの判断に使います。

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
  std::println("Player                             -> {}", std::is_trivially_destructible_v<Player>);
  std::println("int                                -> {}", std::is_trivially_destructible_v<int>);
  std::println("std::string                        -> {}", std::is_trivially_destructible_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

メモリ プールで、要素を破棄するとき、自明な型ならデストラクターを呼ぶ手間を省きます。

```cpp
template <class T>
void DestroyArray(T* p, std::size_t n) {
  if constexpr (!std::is_trivially_destructible_v<T>) {
    for (std::size_t i = 0; i < n; ++i) p[i].~T();   // 自明でない型だけ、破棄する
  }
}
```

## よくあるミス

??? failure "仮想デストラクターを持つ型で true を期待する"
    仮想デストラクターは、自明ではありません。基底クラスのポインターから消せるようにするための印が、自明さを失わせます。

??? failure "デストラクターを書かなければ何でも true だと思う"
    メンバーのどれかが自明でなければ、全体も `false` です。`std::string` を持つ構造体は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_destructible`](is_destructible.md) | 自明さを考えずに、破棄できるか |
| [`is_nothrow_destructible`](is_nothrow_destructible.md) | 破棄が例外を投げないか |
| [`is_trivial`](is_trivial.md) | 構築とコピーの自明さ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_destructible_v<T>` は、`T` が自明なデストラクターを持つか
    - [x] 破棄が何もしない型が `true`
    - [x] プールの破棄ループを省く条件になる

## 関連ページ

- [cpprefjp: std::is_trivially_destructible](https://cpprefjp.github.io/reference/type_traits/is_trivially_destructible.html)
- [cppreference: std::is_trivially_destructible](https://en.cppreference.com/w/cpp/types/is_trivially_destructible)
