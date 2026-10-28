---
title: std::regular_invocable
summary: "同じ引数で何度呼んでも、同じ結果になる呼び出し可能な型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::regular_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::invocable` に、「同じ入力なら同じ結果を返し、呼び出しで引数や状態を変えない」という意味上の約束を足したものが `std::regular_invocable` です。ただし、この約束はコンパイラには確かめられません。

!!! tip "ポイント"
    - `std::regular_invocable<F, Args...>`: `F` を `Args...` で呼べる、副作用のない関数か
    - 構文上の条件は `invocable` と同じ
    - 意味上の約束（同じ入力は同じ結果）は、コンパイラが検査しない
    - 標準のアルゴリズムの引数の説明に登場する

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::regular_invocable {#regular_invocable}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
concept regular_invocable = invocable<F, Args...>;   // 意味上の要求を加えたもの
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `F` | 型 | 呼び出す対象の型 |
| `Args...` | 型の並び | 渡す引数の型 |

構文上の判定は `invocable` と完全に同じで、`regular_invocable` と `invocable` を区別して満たす／満たさないが分かれることはありません。違いは、標準ライブラリの設計上の意図を表す点だけです。「この関数は、何度呼んでも同じ入力に同じ結果を返すはず」という約束を読み手に伝えます。

乱数を返すラムダや、呼ぶたびに状態が変わる関数を渡しても、コンパイルは通ります。約束を破ると、アルゴリズムの結果が不定になります。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

int main() {
  auto twice = [](int x) { return x * 2; };
  std::println("regular_invocable: {}", std::regular_invocable<decltype(twice), int>);
  std::println("invocable        : {}", std::invocable<decltype(twice), int>);
}
```

```text title="実行結果"
regular_invocable: true
invocable        : true
```

## ゲームでの使いどころ

自作のアルゴリズムの引数に副作用のない関数であることを示す目的で書きます。

```cpp
template <std::regular_invocable<int> F>
int SumOf(const std::vector<int>& v, F f) { /* f は何度呼んでもよい */ }
```

## よくあるミス

??? failure "副作用のある関数を渡しても、コンパイルが通ってしまう"
    約束はコンパイラに検査されません。自分で守ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invocable`](invocable.md) | 構文上の条件は同じ |
| [`predicate`](predicate.md) | `bool` を返す |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `regular_invocable` は `invocable` に意味上の約束を足したもの
    - [x] 構文上の判定は `invocable` と同じ
    - [x] 約束はコンパイラに検査されない

## 関連ページ

- [cpprefjp: std::regular_invocable](https://cpprefjp.github.io/reference/concepts/regular_invocable.html)
- [cppreference: std::regular_invocable](https://en.cppreference.com/w/cpp/concepts/regular_invocable)
