---
title: std::is_same
summary: "2 つの型が同じかを、コンパイル時に調べる。"
order: 1
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_same

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <type_traits>`
</div>

テンプレートの中で、型が `float` のときだけ別の処理をしたい、2 つの型が同じかどうかを確かめたい。型を人の目で判断するのではなく、コンパイラーに聞くのが `std::is_same_v<A, B>` です。2 つの型がまったく同じ型なら `true` になります。`const` や参照の有無も区別されます。`if constexpr` と組み合わせて、型ごとの処理を書き分けます。

!!! tip "ポイント"
    - `std::is_same_v<int, int>` は `true`、`<int, const int>` は `false`。
    - `const` や参照を無視したいなら、先に `remove_cvref_t` を通す。
    - `if constexpr (std::is_same_v<T, float>)` で、型ごとの処理を書く。

!!! info "このページを読む前に"
    テンプレートの基本（型を引数にする関数やクラス）が分かると読みやすいです。

## 関数の詳しい説明

### std::is_same_v {#is_same}

```cpp
template <class T, class U>
inline constexpr bool is_same_v = /* T と U が同じなら true */;
```

- 2 つの型が完全に同じか（`int` と `const int` は違う）

## しくみ

`is_same_v<A, B>` は、A と B が同一の型のときだけ `true` です。`int` と `const int` は別の型、`int` と `int&` も別の型、`int` と `long` も別の型です。`using` で別名を付けただけの型は、元の型と同じものとして扱われます。

型を比べる前に `const` や参照を取り除きたいなら、`std::remove_cvref_t<T>` を通します。引数が `const int&` で来ても `int&&` で来ても、`remove_cvref_t` で `int` に直してから比べられます。

C++20 のコンセプト `std::same_as` は、同じ判定を `template <std::same_as<int> T>` の形で書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<int, int>, std::is_same_v<int, const int>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

型によって処理を切り替える場面で使います。

```cpp
template <class T>
void Save(const T& v) {
  if constexpr (std::is_same_v<T, std::string>) {
    // 文字列は長さを先に書く
  } else {
    // それ以外は、バイトをそのまま書く
  }
}
```

エンジンのコンポーネント管理（ECS）で、「このコンポーネントの型は、登録済みの型か」を調べる場面にも使います。可変長テンプレートで、型のリストの中に特定の型があるかを調べる再帰の部品として、`is_same_v` を使います。

`static_assert(std::is_same_v<decltype(x), float>)` のように、`decltype` と組み合わせて、型の推論結果が思った通りかを確かめられます。

## よくあるミス

??? failure "`const` や参照を無視して比べて `false` になる"
    テンプレートの引数 `T` が `const std::string&` で来ているのに、`is_same_v<T, std::string>` と比べると `false` です。`std::remove_cvref_t<T>` を通してから比べます。

??? failure "`int` と `long` が同じだと思う"
    サイズが同じでも、別の型です。Windows の `long` と `int` はどちらも 32 ビットですが、`is_same_v<int, long>` は `false` です。

??? failure "`if` の条件に使って、通らない枝がコンパイルエラーになる"
    型によって存在しないメンバーを使う枝は、普通の `if` ではコンパイルされてしまい、エラーになります。`if constexpr` を使うと、通らない枝は捨てられます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::same_as`](../concepts/same_as.md) | コンセプト版。関数の制約に使う |
| [`std::remove_cvref`](remove_cvref.md) | `const` と参照を外す。比べる前に通す |
| `std::is_convertible` | 変換できるかを調べる。同じ型でなくてよい |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの型が同じかをコンパイル時に調べる。
    - [x] `const` と参照は区別される。比べる前に `remove_cvref_t` を通す。
    - [x] 型ごとの処理は `if constexpr` で書き分ける。

## 関連ページ

- [cpprefjp: std::is_same](https://cpprefjp.github.io/reference/type_traits/is_same.html)
- [cppreference: std::is_same](https://en.cppreference.com/w/cpp/types/is_same)
