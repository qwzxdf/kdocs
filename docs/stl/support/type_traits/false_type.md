---
title: std::false_type
summary: "`false` を表すコンパイル時の定数の型。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::false_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型の性質が当てはまらないとき、トレイトは「偽」を表す型を返します。`std::false_type` は、その型で、`std::integral_constant<bool, false>` の別名です。自作のトレイトでは、既定（当てはまらない場合）の継承元として使います。

!!! tip "ポイント"
    - `std::false_type::value` は `false`
    - `std::integral_constant<bool, false>` の別名
    - `is_integral<float>` などは `false_type` を継承する
    - 自作のトレイトの既定の継承元にする

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::false_type {#false_type}

<span class="ver ver-11">C++11</span>

```cpp
using false_type = integral_constant<bool, false>;
```

`std::false_type` は、`value` が `false` の型です。自作のトレイトで、「既定は偽、特定の型のときだけ真」を書くとき、主テンプレートが `std::false_type` を継承し、特殊化で `std::true_type` を継承します。

`static_assert(std::false_type::value)` は常に失敗しますが、テンプレートの中では、依存した型に基づく `false` を書かないと、使われなくても失敗します（`static_assert(always_false<T>)`）。そのとき、この型が役立ちます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

template <class T> struct Always : std::false_type {};   // 型に依存した false

int main() {
  std::println("false_type::value = {}", std::false_type::value);
  std::println("Always<int>::value = {}", Always<int>::value);
  std::println("is_integral<float> は false_type: {}",
               std::is_base_of_v<std::false_type, std::is_integral<float>>);
}
```

```text title="実行結果"
false_type::value = false
Always<int>::value = false
is_integral<float> は false_type: true
```

## ゲームでの使いどころ

使ってはいけない型に対して、コンパイルエラーを出す仕組みに使います。

```cpp
template <class T>
void Unsupported() {
  static_assert(Always<T>::value, "この型は未対応です");   // 呼ばれたときだけ失敗する
}
```

## よくあるミス

??? failure "`static_assert(false)` を直接書いて、常に失敗する"
    型に依存した `false`（`Always<T>::value`）を書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`true_type`](true_type.md) | 真を表す型 |
| [`integral_constant`](integral_constant.md) | 定数を包む型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::false_type` は「偽」を表す型
    - [x] 自作のトレイトの既定の継承元にする
    - [x] 型に依存した `false` で、遅延する `static_assert` が書ける

## 関連ページ

- [cpprefjp: std::false_type](https://cpprefjp.github.io/reference/type_traits/false_type.html)
- [cppreference: std::false_type](https://en.cppreference.com/w/cpp/types/integral_constant)
