---
title: std::make_obj_using_allocator
summary: "アロケータを渡しながら、オブジェクトを作る。"
order: 900
tags:
  - メモリ
---

# std::make_obj_using_allocator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

アロケータを受けられる型を作るとき、「コンストラクタにアロケータを渡す形」は型によってまちまちです（先頭に `allocator_arg`、末尾に渡すなど）。`make_obj_using_allocator` は、型に合った形を自動で選んで作ります。

!!! tip "ポイント"
    - 型がアロケータ対応かどうかで、渡し方を自動で選ぶ。
    - 結果は値で返る（ヒープ確保はしない）。
    - `scoped_allocator_adaptor` や pmr のコンテナの中身を作るのに使われる。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::make_obj_using_allocator {#make_obj_using_allocator}

```cpp
template <class T, class Alloc, class... Args>
constexpr T make_obj_using_allocator(const Alloc& alloc, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 作りたい型 |
| `alloc` | アロケータ | 渡すアロケータ |
| `args...` | 引数 | `T` のコンストラクタに渡す引数 |

- 戻り値: 作った `T`
- 計算量: `T` のコンストラクタに依存


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <vector>

int main() {
  auto v = std::make_obj_using_allocator<std::vector<int>>(std::allocator<int>{}, 3, 7);
  std::println("{}", v);
}
```

```text title="実行結果"
[7, 7, 7]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アロケータ付きの `vector` を作る | `std::make_obj_using_allocator<std::vector<int>>(alloc, 3, 7);` |

## よくあるミス

??? failure "アロケータ非対応の型に渡す"
    `uses_allocator` が `false` の型では、アロケータは無視され、普通に構築されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uses_allocator`](uses_allocator.md) | 対応型の判定 |
| [`construct_at`](new_delete/construct_at.md) | 場所を指定して作る |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケータ対応の作り方を自動で選ぶ
    - [x] 値で返る
    - [x] pmr で活躍

## 関連ページ

- [cpprefjp: std::make_obj_using_allocator](https://cpprefjp.github.io/reference/memory/make_obj_using_allocator.html)
- [cppreference: std::make_obj_using_allocator](https://en.cppreference.com/w/cpp/memory/make_obj_using_allocator)
