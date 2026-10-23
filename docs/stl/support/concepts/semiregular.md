---
title: std::semiregular
summary: "コピーでき、既定構築できる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::semiregular

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::vector` の要素など、標準ライブラリが要求する基本的な性質を持つ型を受け付けたい。`std::semiregular` は、<strong>T がコピーでき、既定の初期化もできるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::semiregular<T>` は、`T` がコピーでき、既定の初期化もできるか
    - `template <std::semiregular T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::semiregular {#semiregular}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept semiregular = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`copyable` と `default_initializable` の両方を満たす型が満たします。比較演算子は要求しません（比較も要求するのは `regular`）。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

struct Player {
  int hp;
  float x;
};
struct NoDefault {
  explicit NoDefault(int) {}
};

int main() {
  std::println("Player                             -> {}", std::semiregular<Player>);
  std::println("int                                -> {}", std::semiregular<int>);
  std::println("NoDefault                          -> {}", std::semiregular<NoDefault>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
NoDefault                          -> false
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::semiregular T>
void Process(T value) {
  // T は semiregular を満たす型だけ
}
```

## よくあるミス

??? failure "参照や `const` が付いた型で、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`same_as`](same_as.md) | 2 つの型が同じ |
| [`integral`](integral.md) | 整数型 |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::semiregular<T>` は、`T` がコピーでき、既定の初期化もできるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::semiregular](https://cpprefjp.github.io/reference/concepts/semiregular.html)
- [cppreference: std::semiregular](https://en.cppreference.com/w/cpp/concepts/semiregular)
