---
title: std::reference_constructs_from_temporary
summary: "参照が、一時オブジェクトを作って束縛されるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::reference_constructs_from_temporary

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <type_traits>`
</div>

`const int&` を `int` から作ると、一時オブジェクトに束縛されます。その一時オブジェクトが、参照より先に消えてしまう危険を、コンパイル時に検出するために使います。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::reference_constructs_from_temporary {#reference_constructs_from_temporary}

```cpp
template <class T, class U>
struct reference_constructs_from_temporary;
template <class T, class U>
inline constexpr bool reference_constructs_from_temporary_v = reference_constructs_from_temporary<T, U>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `U` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::reference_constructs_from_temporary_v<const int&, int>);
  std::println("{}", std::reference_constructs_from_temporary_v<const int&, int&>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型の性質に応じて処理を切り替える |

## よくあるミス

??? failure "値と型を取り違える"
    `reference_constructs_from_temporary` は型を調べます。変数を渡すときは `decltype(x)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 参照が、一時オブジェクトを作って束縛されるかを調べる
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::reference_constructs_from_temporary](https://cpprefjp.github.io/reference/type_traits/reference_constructs_from_temporary.html)
- [cppreference: std::reference_constructs_from_temporary](https://en.cppreference.com/w/cpp/types/reference_constructs_from_temporary)
