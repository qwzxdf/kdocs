---
title: std::default_accessor
summary: "mdspan の要素への標準のアクセス方法（ふつうのポインタ）。"
order: 900
tags:
  - コンテナ
---

# std::default_accessor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

`mdspan` は、要素にアクセスする方法（アクセサ）を差し替えられます。何も指定しなければ、ふつうのポインタで読み書きする `default_accessor` が使われます。

!!! tip "ポイント"
    - `mdspan` の第 4 テンプレート引数の既定。
    - `access(p, i)` が `p[i]` を返す。
    - 差し替えるとアトミックなアクセスなどにできる。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::default_accessor {#default_accessor}

```cpp
template <class ElementType>
struct default_accessor {
  using reference = ElementType&;
  constexpr reference access(data_handle_type p, size_t i) const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ElementType` | 型 | 要素の型 |

- 戻り値: 要素への参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <mdspan>
#include <print>

int main() {
  int arr[] = {1, 2, 3};
  std::default_accessor<int> a;
  std::println("{}", a.access(arr, 1));
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 要素へのアクセスを自作する | 自作のアクセサを `mdspan` の第 4 引数に渡す |

## よくあるミス

??? failure "自分で指定する"
    ふつうの用途では指定しません。省略すれば `default_accessor` が使われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`aligned_accessor`](aligned_accessor.md) | 境界を保証するアクセサ |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] mdspan の標準のアクセサ
    - [x] p[i] を返す
    - [x] ふつうは意識しない

## 関連ページ

- [cpprefjp: std::default_accessor](https://cpprefjp.github.io/reference/mdspan/default_accessor.html)
- [cppreference: std::default_accessor](https://en.cppreference.com/w/cpp/container/mdspan/default_accessor)
