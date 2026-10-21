---
title: std::is_pointer
summary: "ポインター型かを調べる。"
order: 7
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::is_pointer_v<T>` は、**型 T が生のポインター型か**を調べます。スマートポインターは `false` です。

!!! tip "ポイント"
    - `T*` は `true`。`unique_ptr<T>` は `false`。
    - メンバポインターは別（`is_member_pointer`）。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_pointer_v {#is_pointer}

- ポインタ型なら true（スマートポインタは false）

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <type_traits>

int main() {
  std::println("{} {} {}", std::is_pointer_v<int*>, std::is_pointer_v<int>, std::is_pointer_v<std::unique_ptr<int>>);
}
```

```text title="実行結果"
true false false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで、ポインターのときだけ別の処理 | `if constexpr (std::is_pointer_v<T>)` |

## よくあるミス

??? failure "スマートポインターを true と思う"
    `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | 修飾を外してから調べる |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 生のポインターか
    - [x] スマートポインターは false
    - [x] `T*` が true

## 関連ページ

- [cpprefjp: std::is_pointer](https://cpprefjp.github.io/reference/type_traits/is_pointer.html)
- [cppreference: std::is_pointer](https://en.cppreference.com/w/cpp/types/is_pointer)
