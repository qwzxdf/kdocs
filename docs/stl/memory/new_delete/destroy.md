---
title: std::destroy
summary: "範囲のオブジェクトのデストラクタを呼ぶ（メモリは返さない）。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::destroy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`vector` の中のように、自分で確保した領域に `construct_at` などで作ったオブジェクトをまとめて壊したいときがあります。`std::destroy(first, last)` は範囲の全オブジェクトのデストラクタを呼びます。メモリは返さないので、そのあと自分で解放します。

!!! tip "ポイント"
    - デストラクタを呼ぶだけで、メモリは返さない。
    - `int` のようなトリビアルな型では何もしない。
    - 個数を数で渡す版は [`destroy_n`](destroy_n.md)。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::destroy {#destroy}

```cpp
template <class ForwardIt>
constexpr void destroy(ForwardIt first, ForwardIt last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 壊す範囲 |

- 戻り値: なし
- 計算量: 線形（トリビアルな型なら何もしない）


## 実際に動かしてみる

```cpp
#include <memory>
#include <new>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  ~Tracer() { --alive; }
};

int main() {
  alignas(Tracer) unsigned char buf[sizeof(Tracer) * 2];
  auto* p = reinterpret_cast<Tracer*>(buf);
  std::construct_at(p);
  std::construct_at(p + 1);
  std::println("{}", Tracer::alive);
  std::destroy(p, p + 2);
  std::println("{}", Tracer::alive);
}
```

```text title="実行結果"
2
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自前のプールの中身を壊す | `std::destroy(pool.begin(), pool.begin() + count);` |

## よくあるミス

??? failure "デストラクタを二重に呼ぶ"
    壊したあとのオブジェクトにもう一度 `destroy` を呼ぶと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`destroy_at`](destroy_at.md) | 1 つだけ壊す |
| [`destroy_n`](destroy_n.md) | 個数で指定 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲のデストラクタを呼ぶ
    - [x] メモリは返さない
    - [x] 二重に呼ばない

## 関連ページ

- [cpprefjp: std::destroy](https://cpprefjp.github.io/reference/memory/destroy.html)
- [cppreference: std::destroy](https://en.cppreference.com/w/cpp/memory/destroy)
