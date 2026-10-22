---
title: std::destroy_n
summary: "先頭から n 個のオブジェクトのデストラクタを呼ぶ。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::destroy_n

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

壊す範囲を「先頭と個数」で持っているとき、`destroy` のようにペアでなく、個数で渡せる版が `destroy_n` です。最後に壊した位置の次を返します。

!!! tip "ポイント"
    - デストラクタを呼ぶだけで、メモリは返さない。
    - 戻り値は壊した最後の次の位置。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::destroy_n {#destroy_n}

```cpp
template <class ForwardIt, class Size>
constexpr ForwardIt destroy_n(ForwardIt first, Size n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | イテレータ | 壊す先頭 |
| `n` | 整数 | 壊す個数 |

- 戻り値: 壊した最後の次の位置
- 計算量: 線形


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
  alignas(Tracer) unsigned char buf[sizeof(Tracer) * 3];
  auto* p = reinterpret_cast<Tracer*>(buf);
  for (int i = 0; i < 3; ++i) std::construct_at(p + i);
  auto* end = std::destroy_n(p, 3);
  std::println("{} {}", Tracer::alive, end - p);
}
```

```text title="実行結果"
0 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 先頭と個数で持っている配列を壊す | `std::destroy_n(p, count);` |

## よくあるミス

??? failure "個数を実際より多く指定する"
    作っていない領域のデストラクタを呼ぶと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`destroy`](destroy.md) | 範囲で指定 |
| [`destroy_at`](destroy_at.md) | 1 つだけ |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭と個数で壊す
    - [x] メモリは返さない
    - [x] 戻り値は最後の次

## 関連ページ

- [cpprefjp: std::destroy_n](https://cpprefjp.github.io/reference/memory/destroy_n.html)
- [cppreference: std::destroy_n](https://en.cppreference.com/w/cpp/memory/destroy_n)
