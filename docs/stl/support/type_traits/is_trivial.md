---
title: std::is_trivial
summary: "型がトリビアル（自明な構築・コピー・破棄ができる）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivial

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`memset` で初期化してよいか、`memcpy` でコピーしてよいかを知りたい。`std::is_trivial` は、<strong>型がトリビアルか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivial_v<T>` は、`T` がトリビアル（コンストラクター・コピー・ムーブ・デストラクターが自明）か
    - メンバーの既定値で `false` になる
    - `std::is_trivial<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `memset` などで直接書いてよい型の目印

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivial_v {#is_trivial}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivial_v = is_trivial<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

自分で定義したコンストラクター、コピー、デストラクターを持たず、仮想関数も持たない、単純な型が `true` です。`int` や、数値だけの構造体がそうです。`std::string` のように、動的メモリを管理する型は `false` です。メンバーに既定値（`int hp = 100;`）を書くと、既定のコンストラクターが自明でなくなり、`false` になります。

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
  std::println("int                        -> {}", std::is_trivial_v<int>);
  std::println("Player                     -> {}", std::is_trivial_v<Player>);
  std::println("std::string                -> {}", std::is_trivial_v<std::string>);
}
```

```text title="実行結果"
int                        -> true
Player                     -> true
std::string                -> false
```

## ゲームでの使いどころ

自明な型の配列は、`memset` で一気にゼロ埋めでき、自明でない型は、1 つずつ初期化する、という使い分けに使います。

```cpp
template <class T>
void Clear(T* data, std::size_t n) {
  if constexpr (std::is_trivial_v<T>) {
    std::memset(data, 0, sizeof(T) * n);   // ビットを直接書いてよい
  } else {
    std::fill_n(data, n, T{});
  }
}
```

## よくあるミス

??? failure "メンバーに既定値を書いて trivial でなくなる"
    `struct Vec { float x = 0; };` は、既定のコンストラクターが自明ではないので `false` です。初期値が要るときは、構築時に決めます。

??? failure "trivial なら memcpy で安全だと思う"
    コピーの自明さは `is_trivially_copyable` で調べます。`is_trivial` は、構築とコピーの両方の自明さを調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_trivially_copyable`](is_trivially_copyable.md) | コピーが自明か |
| [`is_standard_layout`](is_standard_layout.md) | C と同じメモリ配置か |
| [`is_aggregate`](is_aggregate.md) | 波括弧で初期化できるか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivial_v<T>` は、`T` がトリビアル（コンストラクター・コピー・ムーブ・デストラクターが自明）か
    - [x] 構築とコピーが自明な型が `true`
    - [x] 既定値つきのメンバーに注意

## 関連ページ

- [cpprefjp: std::is_trivial](https://cpprefjp.github.io/reference/type_traits/is_trivial.html)
- [cppreference: std::is_trivial](https://en.cppreference.com/w/cpp/types/is_trivial)
