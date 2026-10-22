---
title: std::uses_allocator
summary: "型が、指定したアロケータを受け取れるかを調べる型特性。"
order: 900
tags:
  - メモリ
---

# std::uses_allocator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

コンテナの中のコンテナのように、入れ物の中の要素にもアロケータを渡したいことがあります。そのために、要素の型が**そのアロケータを受け取れる型か**を調べるのが `uses_allocator` です。`vector` や `string` のように `allocator_type` を持つ型なら `true` になります。

!!! tip "ポイント"
    - `T::allocator_type` があり、`Alloc` に変換できれば `true`。
    - 標準コンテナは `std::allocator` に対して `true`。
    - `scoped_allocator_adaptor` や pmr が内部で使う。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::uses_allocator {#uses_allocator}

```cpp
template <class T, class Alloc> struct uses_allocator;
template <class T, class Alloc> inline constexpr bool uses_allocator_v = uses_allocator<T, Alloc>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `Alloc` | 型 | アロケータの型 |

- 戻り値: 受けられるなら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <vector>

int main() {
  std::println("{}", std::uses_allocator_v<std::vector<int>, std::allocator<int>>);
  std::println("{}", std::uses_allocator_v<int, std::allocator<int>>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 要素がアロケータ対応かをコンパイル時に分岐 | `if constexpr (std::uses_allocator_v<T, Alloc>)` |

## よくあるミス

??? failure "`int` などで `true` を期待する"
    `allocator_type` を持たない型は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`allocator_arg`](allocator_arg.md) | アロケータを渡す目印 |
| [`make_obj_using_allocator`](make_obj_using_allocator.md) | アロケータを渡して作る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケータを受けられる型かの特性
    - [x] `_v` 版で bool
    - [x] 標準コンテナは true

## 関連ページ

- [cpprefjp: std::uses_allocator](https://cpprefjp.github.io/reference/memory/uses_allocator.html)
- [cppreference: std::uses_allocator](https://en.cppreference.com/w/cpp/memory/uses_allocator)
