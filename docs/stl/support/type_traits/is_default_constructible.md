---
title: std::is_default_constructible
summary: "引数なしで作れる型かを調べる。"
order: 10
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_default_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::is_default_constructible_v<T>` は、**型 T を引数なしで作れる（既定コンストラクターがある）か**を調べます。配列を `resize` で作る、既定値で初期化する、といったテンプレートの制約に使います。

!!! tip "ポイント"
    - `vector::resize(n)` は、この条件が必要。
    - コンセプト版は `std::default_initializable`。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_default_constructible_v {#is_default_constructible}

- `T()` で作れるか

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct NeedsArg {
  explicit NeedsArg(int) {}
};

int main() {
  std::println("{} {}", std::is_default_constructible_v<int>, std::is_default_constructible_v<NeedsArg>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| resize できる型だけを受け取る | `static_assert(std::is_default_constructible_v<T>)` |

## よくあるミス

??? failure "参照メンバを持つ型"
    既定構築できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_copy_constructible`](is_copy_constructible.md) | コピーできるか |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数なしで作れるか
    - [x] resize の条件
    - [x] コンセプト版もある

## 関連ページ

- [cpprefjp: std::is_default_constructible](https://cpprefjp.github.io/reference/type_traits/is_default_constructible.html)
- [cppreference: std::is_default_constructible](https://en.cppreference.com/w/cpp/types/is_default_constructible)
