---
title: std::allocator_arg
summary: "「次の引数はアロケータ」と示す目印。"
order: 900
tags:
  - メモリ
---

# std::allocator_arg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

コンストラクタの引数にアロケータを渡したいとき、引数の並びだけでは「普通の引数」と区別できません。そこで `std::allocator_arg` という目印を最初に置いて、「次がアロケータです」と伝えます。`tuple` や `function` などのコンストラクタが使います。

!!! tip "ポイント"
    - `std::allocator_arg_t` 型の定数。
    - `tuple(std::allocator_arg, alloc, 値...)` の形で使う。
    - 自作の型でアロケータを受けるときもこの形に合わせる。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::allocator_arg {#allocator_arg}

```cpp
struct allocator_arg_t { explicit allocator_arg_t() = default; };
inline constexpr allocator_arg_t allocator_arg{};
```

- 戻り値: なし（目印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <tuple>

int main() {
  std::tuple<int> t(std::allocator_arg, std::allocator<int>{}, 5);
  std::println("{}", std::get<0>(t));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アロケータを指定して `tuple` を作る | `std::tuple<int> t(std::allocator_arg, std::allocator<int>{}, 5);` |

## よくあるミス

??? failure "目印を忘れる"
    `allocator_arg` を置かないと、アロケータが普通の引数として扱われ、コンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uses_allocator`](uses_allocator.md) | アロケータを受けられる型か調べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケータを渡す目印
    - [x] 最初の引数に置く
    - [x] tuple などが使う

## 関連ページ

- [cpprefjp: std::allocator_arg](https://cpprefjp.github.io/reference/memory/allocator_arg_t.html)
- [cppreference: std::allocator_arg](https://en.cppreference.com/w/cpp/memory/allocator_arg_t)
