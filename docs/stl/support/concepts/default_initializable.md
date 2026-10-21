---
title: std::default_initializable
summary: "引数なしで作れる型であることを要求するコンセプト。"
order: 11
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::default_initializable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::default_initializable<T>` は、**T が引数なしで作れること**（既定コンストラクターがあること）を要求するコンセプトです。`resize` や配列の確保に使う型の条件です。

!!! tip "ポイント"
    - `T{}` と `T()` と `T t;` のすべてが書けることが条件。
    - 参照メンバを持つ型は満たさない。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::default_initializable {#default_initializable}

```cpp
template <class T>
concept default_initializable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

struct NeedsArg {
  explicit NeedsArg(int) {}
};

int main() {
  std::println("{} {}", std::default_initializable<int>, std::default_initializable<NeedsArg>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列を確保する自作コンテナの要素型の条件 | `template <std::default_initializable T>` |

## よくあるミス

??? failure "const の型で true と思う"
    `const int` は `int` と違い、既定初期化できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_default_constructible`](../type_traits/is_default_constructible.md) | 変数テンプレート版 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数なしで作れる
    - [x] resize できる型
    - [x] 参照メンバがあると false

## 関連ページ

- [cpprefjp: std::default_initializable](https://cpprefjp.github.io/reference/concepts/default_initializable.html)
- [cppreference: std::default_initializable](https://en.cppreference.com/w/cpp/concepts/default_initializable)
