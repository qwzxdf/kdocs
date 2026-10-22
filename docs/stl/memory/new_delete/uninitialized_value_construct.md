---
title: std::uninitialized_value_construct
summary: "未初期化のメモリに、値初期化でオブジェクトを作る。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_value_construct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`int` のような型を 0 で初期化した状態で並べたいとき、`uninitialized_value_construct` を使います。`default_construct` と違い、`int` は **0 になります**。

!!! tip "ポイント"
    - 未初期化のメモリに、オブジェクトを作る。
    - 途中で例外が出たら、すでに作ったぶんを壊してから投げる。
    - 個数で指定する版は `uninitialized_value_construct_n`（同じページの下）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::uninitialized_value_construct {#uninitialized_value_construct}

```cpp
template <class ForwardIt>
void uninitialized_value_construct(ForwardIt first, ForwardIt last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 未初期化の領域 |

- 戻り値: 最後に作った位置の次のイテレータ
- 計算量: 線形

### std::uninitialized_value_construct_n {#uninitialized_value_construct_n}

```cpp
template <class ForwardIt, class Size>
ForwardIt uninitialized_value_construct_n(ForwardIt first, Size n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | イテレータ | 未初期化の領域の先頭 |
| `n` | 整数 | 作る個数 |

- 戻り値: 最後に作った位置の次のイテレータ
- 計算量: 線形


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  alignas(int) unsigned char buf[sizeof(int) * 3];
  auto* p = reinterpret_cast<int*>(buf);
  std::uninitialized_value_construct(p, p + 3);
  std::println("{} {} {}", p[0], p[1], p[2]);
}
```

```text title="実行結果"
0 0 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 0 初期化された配列を用意する | `std::uninitialized_value_construct(p, p + n);` |

## よくあるミス

??? failure "すでにオブジェクトがある場所に使う"
    この関数は**未初期化の領域**専用です。作ってあるオブジェクトの上に使うと、デストラクタが呼ばれずに壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`construct_at`](construct_at.md) | 1 つだけ作る |
| [`destroy`](destroy.md) | 壊す |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 未初期化のメモリにオブジェクトを作る
    - [x] 例外が出たら作ったぶんを壊す
    - [x] `_n` は個数で指定

## 関連ページ

- [cpprefjp: std::uninitialized_value_construct](https://cpprefjp.github.io/reference/memory/uninitialized_value_construct.html)
- [cppreference: std::uninitialized_value_construct](https://en.cppreference.com/w/cpp/memory/uninitialized_value_construct)
