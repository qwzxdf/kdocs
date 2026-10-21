---
title: std::copyable
summary: "コピーできる型であることを要求するコンセプト。"
order: 9
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::copyable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::copyable<T>` は、**T がコピーでき、代入でき、ムーブもできる型であること**を要求するコンセプトです。`std::function` に入れられる型、`std::vector` の要素として自由に扱える型の条件です。

!!! tip "ポイント"
    - `unique_ptr` はコピーできないので `false`。
    - `std::movable` より条件が厳しい。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::copyable {#copyable}

```cpp
template <class T>
concept copyable = /* 条件 */;
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
  std::println("{} {}", std::copyable<int>, std::copyable<std::unique_ptr<int>>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コピー可能な型だけをキューに入れるテンプレート | `template <std::copyable T>` |

## よくあるミス

??? failure "const メンバを持つ型"
    代入できないので `false` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`movable`](movable.md) | ムーブだけでよい |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コピーできる型
    - [x] `unique_ptr` は false
    - [x] movable より厳しい

## 関連ページ

- [cpprefjp: std::copyable](https://cpprefjp.github.io/reference/concepts/copyable.html)
- [cppreference: std::copyable](https://en.cppreference.com/w/cpp/concepts/copyable)
