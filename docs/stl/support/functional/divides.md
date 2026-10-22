---
title: std::divides
summary: "`a / b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::divides

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

割り算を `transform` や `fold` に渡したいとき、`std::divides<>{}` が使えます。整数なら小数点以下は切り捨てです。

!!! tip "ポイント"
    - `std::divides<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数に、ラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::divides {#divides}

```cpp
template <class T = void>
struct divides {
  constexpr auto operator()(const T& a, const T& b) const;  // a / b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a / b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::divides<>{}(10, 3));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 全要素を同じ値で割る | `std::transform(a.begin(), a.end(), b.begin(), out.begin(), std::divides<>{});` |

## よくあるミス

??? failure "0 で割る"
    整数を 0 で割ると未定義動作です。割る側の列に 0 がないことを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`multiplies`](multiplies.md) | かけ算 |
| [`modulus`](modulus.md) | 余り |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a / b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::divides<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::divides](https://cpprefjp.github.io/reference/functional/divides.html)
- [cppreference: std::divides](https://en.cppreference.com/w/cpp/utility/functional/divides)
