---
title: std::less
summary: "「小さいか」を比べる関数オブジェクト（`<` の代わり）。"
order: 1
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::less

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a < b; }` を毎回書くのは冗長です。`std::less` は、<strong>演算子 `<`（小さいか）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::less<>{}(2 つの値)` は演算子 `<` と同じ結果
    - 型を省略した `std::less<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::less {#less}

```cpp
template <class T = void>
struct less {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::less<>{}(a, b)` は `a < b` と同じ結果を返します。`std::map`、`std::set`、`std::sort` の既定の順序です。ポインターに対して `<` を使うと、無関係な 2 つのオブジェクトの比較は未規定ですが、`std::less` は、全順序を保証します。ポインターをキーにした `std::map` が安全に動くのは、このためです。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::println("std::less<>{{}}(2, 3) = {}", std::less<>{}(2, 3));
  std::vector<int> v = {3, 1, 4, 2};
  std::sort(v.begin(), v.end(), std::less<>{});
  for (int x : v) std::print("{} ", x);
  std::println("");
}
```

```text title="実行結果"
std::less<>{}(2, 3) = true
1 2 3 4 
```

## ゲームでの使いどころ

文字列をキーにする `map` で、`std::string_view` のまま検索できるようにします。

```cpp
std::map<std::string, int, std::less<>> hp;   // less<> は透過的な比較
hp["hero"] = 100;

std::string_view key = "hero";
auto it = hp.find(key);   // std::string を作らずに検索できる
```

## よくあるミス

??? failure "透過的でない std::less<std::string> のままにする"
    `std::less<std::string>` だと、`find` に `string_view` を渡したとき、一時的な `std::string` が作られます。`std::less<>` と省略します。

??? failure "無関係なポインターを < で比べる"
    規格では未規定です。ポインターをキーにするなら、`std::less` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`greater`](greater.md) | 降順の比較 |
| [`less_equal`](less_equal.md) | 以下を返す |
| [`equal_to`](equal_to.md) | 等しいかを返す |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::less<>` は演算子 `<`（小さいか）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::less](https://cpprefjp.github.io/reference/functional/less.html)
- [cppreference: std::less](https://en.cppreference.com/w/cpp/utility/functional/less)
