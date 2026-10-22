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

「普通の値のように扱える」ための条件の前半です。コピーできて、引数なしでも作れる型を要求します。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::semiregular<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::semiregular {#semiregular}

```cpp
template <class T>
concept semiregular = /* copyable<T> かつ default_initializable<T> */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <memory>
#include <print>

int main() {
  std::println("{}", std::semiregular<int>);
  std::println("{}", std::semiregular<std::unique_ptr<int>>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数に条件をつけて、使える型を制限する |

## よくあるミス

??? failure "既定構築できない型"
    引数なしで作れない型は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regular`](regular.md) | さらに比較できる |
| [`copyable`](copyable.md) | 既定構築は不要 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コピーでき、既定構築できる型であることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::semiregular](https://cpprefjp.github.io/reference/concepts/semiregular.html)
- [cppreference: std::semiregular](https://en.cppreference.com/w/cpp/concepts/semiregular)
