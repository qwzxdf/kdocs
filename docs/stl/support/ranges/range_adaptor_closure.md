---
title: std::ranges::range_adaptor_closure
summary: "自作のパイプ対応アダプタを作るための土台。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::range_adaptor_closure

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`v | views::reverse` のようなパイプは、標準の view だけが使えるのではありません。`range_adaptor_closure<T>` を継承した自作の関数オブジェクトにも使えます。`v | sum` のように、自作の関数をパイプでつなげられます。

!!! tip "ポイント"
    - `struct Sum : std::ranges::range_adaptor_closure<Sum> {...}` と継承する。
    - `operator()(Range&&)` を定義すると、`範囲 | Sum{}` が呼べる。
    - C++23 の機能（C++20 では実装定義の仕組みで自作しづらい）。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::range_adaptor_closure {#range_adaptor_closure}

```cpp
template <class D>
requires is_class_v<D> && same_as<D, remove_cv_t<D>>
class range_adaptor_closure;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `D` | 型 | 継承するクラス自身 |

- 戻り値: `range | D{}` を `D{}(range)` として呼べるようにする
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  struct Sum : std::ranges::range_adaptor_closure<Sum> {
    template <std::ranges::range R>
    int operator()(R&& r) const {
      int s = 0;
      for (int x : r) s += x;
      return s;
    }
  };

  std::vector<int> v = {1, 2, 3};
  std::println("{}", v | Sum{});
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の変換をパイプでつなぐ |

## よくあるミス

??? failure "引数を範囲にしない"
    `operator()` の引数は範囲 1 つです。ほかの引数はコンストラクタで受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::transform`](../../algorithms/views/transform.md) | 標準のアダプタ |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自作のパイプ対応アダプタを作るための土台
    - [x] `struct Sum : std::ranges::range_adaptor_closure<Sum> {...}` と継承する
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::range_adaptor_closure](https://cpprefjp.github.io/reference/ranges/range_adaptor_closure.html)
- [cppreference: std::ranges::range_adaptor_closure](https://en.cppreference.com/w/cpp/ranges/range_adaptor_closure)
