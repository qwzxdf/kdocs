---
title: std::uninitialized_fill
summary: "未初期化のメモリの範囲を、同じ値のコピーで埋める。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_fill

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

自分で確保した領域に、同じ値のコピーをまとめて作りたいことがあります。`uninitialized_fill` は、`fill`（代入）と違い、まだオブジェクトがない領域に**コピーコンストラクタで作ります**。

!!! tip "ポイント"
    - 未初期化のメモリに、オブジェクトを作る。
    - 途中で例外が出たら、すでに作ったぶんを壊してから投げる。
    - 個数で指定する版は `uninitialized_fill_n`（同じページの下）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::uninitialized_fill {#uninitialized_fill}

```cpp
template <class ForwardIt, class T>
void uninitialized_fill(ForwardIt first, ForwardIt last, const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 未初期化の領域 |
| `value` | T | コピー元の値 |

- 戻り値: 最後に作った位置の次のイテレータ
- 計算量: 線形

### std::uninitialized_fill_n {#uninitialized_fill_n}

```cpp
template <class ForwardIt, class Size, class T>
ForwardIt uninitialized_fill_n(ForwardIt first, Size n, const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | イテレータ | 未初期化の領域の先頭 |
| `n` | 整数 | 作る個数 |
| `value` | T | コピー元の値 |

- 戻り値: 最後に作った位置の次のイテレータ
- 計算量: 線形


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <string>

int main() {
  alignas(std::string) unsigned char buf[sizeof(std::string) * 2];
  auto* p = reinterpret_cast<std::string*>(buf);
  std::uninitialized_fill(p, p + 2, std::string("hi"));
  std::println("{} {}", p[0], p[1]);
  std::destroy(p, p + 2);
}
```

```text title="実行結果"
hi hi
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 確保した領域を 0 で埋めて使い始める | `std::uninitialized_fill(p, p + n, 0);` |

## よくあるミス

??? failure "すでにオブジェクトがある場所に使う"
    この関数は**未初期化の領域**専用です。作ってあるオブジェクトの上に使うと、デストラクタが呼ばれずに壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`construct_at`](construct_at.md) | 1 つだけ作る |
| [`destroy`](destroy.md) | 壊す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 未初期化のメモリにオブジェクトを作る
    - [x] 例外が出たら作ったぶんを壊す
    - [x] `_n` は個数で指定

## 関連ページ

- [cpprefjp: std::uninitialized_fill](https://cpprefjp.github.io/reference/memory/uninitialized_fill.html)
- [cppreference: std::uninitialized_fill](https://en.cppreference.com/w/cpp/memory/uninitialized_fill)
