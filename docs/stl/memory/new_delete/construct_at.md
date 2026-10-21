---
title: std::construct_at
summary: "確保済みのメモリの上に、オブジェクトを作る（配置 new の安全版）。"
order: 6
group: new / delete まわり
tags:
  - メモリ
---

# std::construct_at

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

`std::construct_at` は、**確保済みのメモリの上にオブジェクトを作る**関数で、配置 new の C++20 版です。`constexpr` 関数の中でも使えます。

!!! tip "ポイント"
    - `std::construct_at(ptr, args...)` で作る。
    - 壊すのは [`destroy_at`](destroy_at.md)。
    - アロケーターの `construct` の実体として使われる。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::construct_at <span class="ver ver-20">C++20</span> {#construct_at data-toc-label="std::construct_at"}

```cpp
template <class T, class... Args>
constexpr T* construct_at(T* p, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `T*` | 作る場所 |
| `args...` | `Args&&...` | コンストラクタの引数 |

- 戻り値: `p`
- 配置 new を、`::new` と間違えにくく書ける関数です。`constexpr` の中でも使えます。**配置 new が必要なら、こちらを優先**します

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  alignas(int) unsigned char buffer[sizeof(int)];
  int* p = std::construct_at(reinterpret_cast<int*>(buffer), 5);
  std::println("{}", *p);
  std::destroy_at(p);
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| メモリプールの上にオブジェクトを作る | `std::construct_at(slot, args...)` |

## よくあるミス

??? failure "メモリが足りない"
    十分な大きさ・アラインメントを自分で用意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`placement_new`](placement_new.md) | 配置 new |
| [`destroy_at`](destroy_at.md) | 壊す |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 配置 new の安全な版
    - [x] C++20
    - [x] `destroy_at` と対

## 関連ページ

- [cpprefjp: std::construct_at](https://cpprefjp.github.io/reference/new/construct_at.html)
- [cppreference: std::construct_at](https://en.cppreference.com/w/cpp/memory/new/construct_at)
