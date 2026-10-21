---
title: std::equal_to
summary: "「等しいか」を比べる関数オブジェクト（`==` の代わり）。"
order: 3
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::equal_to

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`std::equal_to<T>` は、**`a == b` を関数オブジェクトとして使えるようにしたもの**です。`unordered_map` の既定の等しさの判定として使われています。自作のハッシュ表で、`Hash` と組みで渡します。

!!! tip "ポイント"
    - `unordered_map<K, V, Hash, std::equal_to<>>` の 4 番目の引数。
    - 自作の等しさ判定は、構造体に `operator()` を持たせるか、ラムダ式。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::equal_to {#equal_to}

```cpp
template <class T = void>
struct equal_to;  // a == b
```

- `a == b`。unordered_map のデフォルトのキー比較です

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{} {}", std::equal_to<>{}(3, 3), std::equal_to<>{}(3, 4));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| unordered_map のキーの等しさを明示する | `std::equal_to<>` |

## よくあるミス

??? failure "ハッシュと等しさの組を間違える"
    等しいキーは、同じハッシュ値でなければなりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::hash`](../../utilities/hash.md) | ハッシュ値を作る側 |
| [`less`](less.md) | 大小 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `==` を関数オブジェクトにしたもの
    - [x] unordered_map の既定
    - [x] Hash と組

## 関連ページ

- [cpprefjp: std::equal_to](https://cpprefjp.github.io/reference/functional/equal_to.html)
- [cppreference: std::equal_to](https://en.cppreference.com/w/cpp/utility/functional/equal_to)
