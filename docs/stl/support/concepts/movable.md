---
title: std::movable
summary: "ムーブできる型であることを要求するコンセプト。"
order: 10
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::movable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::movable<T>` は、**T がムーブでき、ムーブ代入でき、`swap` できる型であること**を要求するコンセプトです。コピーできなくてもよいので、`unique_ptr` も満たします。

!!! tip "ポイント"
    - `const T` は代入できないので `false`。
    - コピーも要求するなら `std::copyable`。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::movable {#movable}

```cpp
template <class T>
concept movable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <memory>
#include <print>

int main() {
  std::println("{} {}", std::movable<std::unique_ptr<int>>, std::movable<const int>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ムーブだけできる型を受け取るジョブキュー | `template <std::movable T>` |

## よくあるミス

??? failure "const の型を渡す"
    代入できないので条件を満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copyable`](copyable.md) | コピーも必要 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ムーブできる型
    - [x] `unique_ptr` も満たす
    - [x] const は false

## 関連ページ

- [cpprefjp: std::movable](https://cpprefjp.github.io/reference/concepts/movable.html)
- [cppreference: std::movable](https://en.cppreference.com/w/cpp/concepts/movable)
