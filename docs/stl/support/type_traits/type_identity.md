---
title: std::type_identity
summary: "何もしない型変換（テンプレート引数の推論を止めるのに使う）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::type_identity

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

`Max2(1.5, 1)` のように、`double` と `int` を混ぜて呼ぶと、`template <class T> T Max2(T a, T b)` は T を 2 通りに推論して失敗します。片方を `type_identity_t<T>` で包むと、その引数からは T を推論しなくなり、`double` に統一できます。

!!! tip "ポイント"
    - `type_identity_t<T>` は `T` そのもの。
    - 推論に使われない文脈（non-deduced context）にするために使う。
    - 「ここは推論しない」と示す、目印として働く。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::type_identity {#type_identity}

```cpp
template <class T>
struct type_identity { using type = T; };
template <class T>
using type_identity_t = typename type_identity<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | そのまま返す型 |

- 戻り値: `T` そのもの
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

template <class T>
T Max2(T a, std::type_identity_t<T> b) {
  return a > b ? a : b;
}

int main() {
  std::println("{}", Max2(1.5, 1));
}
```

```text title="実行結果"
1.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 第 1 引数の型で、第 2 引数を決める |

## よくあるミス

??? failure "両方を包む"
    全部の引数を包むと、どこからも T を推論できなくなります。1 つは普通に書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`decay`](decay.md) | 型を値渡し用に変換 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何もしない型変換（テンプレート引数の推論を止めるのに使う）
    - [x] `type_identity_t<T>` は `T` そのもの
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::type_identity](https://cpprefjp.github.io/reference/type_traits/type_identity.html)
- [cppreference: std::type_identity](https://en.cppreference.com/w/cpp/types/type_identity)
