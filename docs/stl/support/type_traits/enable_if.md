---
title: std::enable_if
summary: "条件が真のときだけ、型を存在させる（SFINAE のための道具）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::enable_if

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

テンプレート関数を特定の型にだけ使えるようにしたい。たとえば、整数にだけ使える関数を作り、小数には別の関数を使わせたい。`std::enable_if` は、<strong>条件が真のときだけ型が存在する</strong>ようにして、条件に合わない場合に関数を候補から外します（SFINAE）。

!!! tip "ポイント"
    - `std::enable_if_t<B, T>`: `B` が真なら `T`、偽なら型が存在しない
    - 偽のとき、その関数テンプレートは、オーバーロードの候補から外れる
    - C++20 以降は `requires` や `concept` のほうが読みやすい
    - 戻り値の型や、テンプレート引数の既定値に書く

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::enable_if_t {#enable_if}

<span class="ver ver-11">C++11</span>

```cpp
template <bool B, class T = void>
using enable_if_t = typename enable_if<B, T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B` | `bool` | 条件（コンパイル時の定数） |
| `T` | 型 | 条件が真のときの型。既定は `void` |

`enable_if_t<B, T>` は、`B` が真なら `T`、偽なら定義がなく、その式は不適格になります。関数テンプレートの宣言の中で不適格になると、エラーにならず、その関数が候補から静かに外れます。これが SFINAE（置換の失敗はエラーではない）です。

```cpp
template <class T>
std::enable_if_t<std::is_integral_v<T>, T> Half(T v) { return v / 2; }
```

C++20 の `concept` を使うと、同じことを `template <std::integral T> T Half(T v)` と短く書けます。新しいコードでは、そちらを使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

// 整数にだけ使える
template <class T>
std::enable_if_t<std::is_integral_v<T>, T> Half(T v) {
  return v / 2;
}

int main() {
  std::println("Half(10) = {}", Half(10));
  // Half(10.0);   // 整数ではないので候補から外れ、コンパイルエラー
}
```

```text title="実行結果"
Half(10) = 5
```

## ゲームでの使いどころ

古い C++ のコードで、型による制約をかけるために使われています。新しいコードでは `concept` を使います。

```cpp
template <std::integral T>
T Half(T v) { return v / 2; }   // enable_if より読みやすい
```

## よくあるミス

??? failure "複数のオーバーロードで条件が重なり、曖昧になる"
    条件が排他的になるよう書きます。

??? failure "エラーメッセージが読みにくい"
    `concept` に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`conditional`](conditional.md) | 条件で型を選ぶ |
| [`void_t`](void_t.md) | 型が有効かを検出する |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `enable_if_t<B, T>` は条件が偽のとき型が存在しない
    - [x] 関数が候補から外れる（SFINAE）
    - [x] 新しいコードは `concept` / `requires`

## 関連ページ

- [cpprefjp: std::enable_if](https://cpprefjp.github.io/reference/type_traits/enable_if.html)
- [cppreference: std::enable_if](https://en.cppreference.com/w/cpp/types/enable_if)
