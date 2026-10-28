---
title: std::modulus
summary: "`a % b`（余り）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::modulus

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

余りを求める `%` も、関数オブジェクトとして渡せます。ループ再生のインデックスや、均等な振り分けに使う余りをアルゴリズムの中で計算したいときに便利です。

!!! tip "ポイント"
    - `std::modulus<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数にラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::modulus {#modulus}

```cpp
template <class T = void>
struct modulus {
  constexpr auto operator()(const T& a, const T& b) const;  // a % b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a % b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::modulus<>{}(10, 3));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| インデックスを範囲内に折り返す | `std::transform(a.begin(), a.end(), b.begin(), out.begin(), std::modulus<>{});` |

## よくあるミス

??? failure "浮動小数点に使う"
    `%` は整数専用です。小数の余りは [`std::fmod`](../../numeric/cmath/fmod.md) を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`divides`](divides.md) | 割り算 |
| [`fmod`](../../numeric/cmath/fmod.md) | 小数の余り |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a % b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::modulus<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::modulus](https://cpprefjp.github.io/reference/functional/modulus.html)
- [cppreference: std::modulus](https://en.cppreference.com/w/cpp/utility/functional/modulus)
