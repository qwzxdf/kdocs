---
title: std::is_copy_constructible
summary: "コピーして作れる型かを調べる。"
order: 11
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_copy_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::is_copy_constructible_v<T>` は、**型 T のオブジェクトをコピーして作れるか**を調べます。`unique_ptr` のようなムーブだけできる型は `false` です。`std::function` に入れられる型かの確認にも使えます。

!!! tip "ポイント"
    - `unique_ptr` は `false`。
    - `std::function` に入れるには `true` が必要。
    - コンセプト版は `std::copy_constructible`。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_copy_constructible_v {#is_copy_constructible}

- コピーできるか。`std::unique_ptr` は false

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_copy_constructible_v<int>, std::is_copy_constructible_v<std::unique_ptr<int>>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コピー可能な型だけをキューに入れる | `static_assert(std::is_copy_constructible_v<Job>)` |

## よくあるミス

??? failure "ムーブだけの型を function に入れる"
    コンパイルエラーです。`move_only_function` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_nothrow_move_constructible`](is_nothrow_move_constructible.md) | ムーブが例外を投げないか |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コピーして作れるか
    - [x] unique_ptr は false
    - [x] function に入れる条件

## 関連ページ

- [cpprefjp: std::is_copy_constructible](https://cpprefjp.github.io/reference/type_traits/is_copy_constructible.html)
- [cppreference: std::is_copy_constructible](https://en.cppreference.com/w/cpp/types/is_copy_constructible)
