---
title: std::uninitialized_move
summary: "未初期化のメモリに、範囲の要素をムーブして作る。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_move

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`vector` の再確保のように、古い領域の中身を新しい未初期化の領域へ引っ越したいことがあります。`uninitialized_move` は、移動元をムーブして、移動先に新しいオブジェクトを作ります。

!!! tip "ポイント"
    - 未初期化のメモリにオブジェクトを作る。
    - 途中で例外が出たら、すでに作ったぶんを壊してから投げる。
    - 個数で指定する版は `uninitialized_move_n`（同じページの下）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::uninitialized_move {#uninitialized_move}

```cpp
template <class InputIt, class NoThrowForwardIt>
NoThrowForwardIt uninitialized_move(InputIt first, InputIt last, NoThrowForwardIt d_first);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 移動元の範囲 |
| `d_first` | イテレータ | 未初期化の移動先の先頭 |

- 戻り値: 最後に作った位置の次のイテレータ
- 計算量: 線形

### std::uninitialized_move_n {#uninitialized_move_n}

```cpp
template <class InputIt, class Size, class NoThrowForwardIt>
pair<InputIt, NoThrowForwardIt> uninitialized_move_n(InputIt first, Size n, NoThrowForwardIt d_first);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | イテレータ | 移動元の先頭 |
| `n` | 整数 | 移動する個数 |
| `d_first` | イテレータ | 未初期化の移動先の先頭 |

- 戻り値: 最後に作った位置の次のイテレータ
- 計算量: 線形


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <string>

int main() {
  std::string src[2] = {"a", "b"};
  alignas(std::string) unsigned char buf[sizeof(std::string) * 2];
  auto* p = reinterpret_cast<std::string*>(buf);
  std::uninitialized_move(src, src + 2, p);
  std::println("{} {}", p[0], p[1]);
  std::destroy(p, p + 2);
}
```

```text title="実行結果"
a b
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作コンテナの再確保で、要素を新領域へ引っ越す | `std::uninitialized_move(old_begin, old_end, new_begin);` |

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

- [cpprefjp: std::uninitialized_move](https://cpprefjp.github.io/reference/memory/uninitialized_move.html)
- [cppreference: std::uninitialized_move](https://en.cppreference.com/w/cpp/memory/uninitialized_move)
