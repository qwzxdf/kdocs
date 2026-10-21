---
title: std::predicate
summary: "`bool` として使える結果を返す関数であることを要求するコンセプト。"
order: 7
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::predicate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::predicate<F, Args...>` は、**関数 `F` を `Args...` で呼ぶと、結果が `bool` として使えること**を要求するコンセプトです。`filter` や `find_if` の条件関数の制約です。

!!! tip "ポイント"
    - `find_if` や `remove_if` の条件に当たる。
    - `std::invocable` に「戻り値が bool」を足したもの。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::predicate {#predicate}

```cpp
template <class T>
concept predicate = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

int main() {
  auto is_even = [](int x) { return x % 2 == 0; };
  auto twice = [](int x) { return x * 2; };
  std::println("{} {}", std::predicate<decltype(is_even), int>, std::predicate<decltype(twice), int>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 条件関数を受け取る自作のアルゴリズム | `template <std::predicate<const Enemy&> P>` |

## よくあるミス

??? failure "戻り値が整数でも true になる"
    `bool` に変換できれば条件を満たします（`int` 0/1 など）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invocable`](invocable.md) | 呼べればよい |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] bool を返す関数
    - [x] 条件関数の制約
    - [x] invocable に bool を足したもの

## 関連ページ

- [cpprefjp: std::predicate](https://cpprefjp.github.io/reference/concepts/predicate.html)
- [cppreference: std::predicate](https://en.cppreference.com/w/cpp/concepts/predicate)
