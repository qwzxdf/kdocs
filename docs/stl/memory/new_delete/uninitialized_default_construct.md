---
title: std::uninitialized_default_construct
summary: "未初期化のメモリに、デフォルト初期化でオブジェクトを作る。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_default_construct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

未初期化の領域にオブジェクトを並べたいが、値は何でもよいとき（あとで上書きする）、`uninitialized_default_construct` が使えます。`int` のような型は**初期化されないまま**（ゴミの値）ですが、クラスは既定コンストラクタが呼ばれます。

!!! tip "ポイント"
    - 未初期化のメモリに、オブジェクトを作る。
    - 途中で例外が出たら、すでに作ったぶんを壊してから投げる。
    - 個数で指定する版は `uninitialized_default_construct_n`（同じページの下）。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::uninitialized_default_construct {#uninitialized_default_construct}

```cpp
template <class ForwardIt>
void uninitialized_default_construct(ForwardIt first, ForwardIt last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 未初期化の領域 |

- 戻り値: 最後に作った位置の次のイテレータ
- 計算量: 線形

### std::uninitialized_default_construct_n {#uninitialized_default_construct_n}

```cpp
template <class ForwardIt, class Size>
ForwardIt uninitialized_default_construct_n(ForwardIt first, Size n);
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
#include <string>

int main() {
  alignas(std::string) unsigned char buf[sizeof(std::string) * 2];
  auto* p = reinterpret_cast<std::string*>(buf);
  std::uninitialized_default_construct(p, p + 2);
  std::println("[{}] [{}]", p[0], p[1]);
  std::destroy(p, p + 2);
}
```

```text title="実行結果"
[] []
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| あとで全部上書きする配列を高速に用意する | `std::uninitialized_default_construct(p, p + n);` |

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

- [cpprefjp: std::uninitialized_default_construct](https://cpprefjp.github.io/reference/memory/uninitialized_default_construct.html)
- [cppreference: std::uninitialized_default_construct](https://en.cppreference.com/w/cpp/memory/uninitialized_default_construct)
