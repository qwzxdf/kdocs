---
title: std::equal_to
summary: "「等しいか」を比べる関数オブジェクト（`==` の代わり）。"
order: 3
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::equal_to

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a == b; }` を毎回書くのは冗長です。`std::equal_to` は、<strong>演算子 `==`（等しいか）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::equal_to<>{}(2 つの値)` は演算子 `==` と同じ結果
    - 型を省略した `std::equal_to<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::equal_to {#equal_to}

```cpp
template <class T = void>
struct equal_to {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::equal_to<>{}(a, b)` は `a == b` と同じ結果を返します。`std::unordered_map` や `std::unordered_set` の等しさの判定の既定値でもあります。注意したいのは、ポインターを比べると、指す先の値ではなくアドレスを比べる点です。C の文字列（`const char*`）どうしに使うと、文字の中身ではなく、ポインターの値が比べられます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::equal_to<>{{}}(2, 2) = {}", std::equal_to<>{}(2, 2));
}
```

```text title="実行結果"
std::equal_to<>{}(2, 2) = true
```

## ゲームでの使いどころ

2 つの配列が、同じ内容かを確かめます。

```cpp
std::vector<int> a = {1, 2, 3};
std::vector<int> b = {1, 2, 3};
bool same = std::equal(a.begin(), a.end(), b.begin(), std::equal_to<>{});   // true
```

## よくあるミス

??? failure "const char* どうしを比べる"
    アドレスを比べるので、同じ文字列でも `false` になります。`std::string` か `std::string_view` にして比べます。

??? failure "浮動小数点数の == を信じる"
    計算の誤差で、等しいはずの値が `false` になります。許容誤差つきの比較を自作します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`not_equal_to`](not_equal_to.md) | 等しくないかを返す |
| [`less`](less.md) | 大小の比較 |
| [`hash`](../../utilities/hash.md) | `unordered_map` が等しさとあわせて使う |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::equal_to<>` は演算子 `==`（等しいか）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::equal_to](https://cpprefjp.github.io/reference/functional/equal_to.html)
- [cppreference: std::equal_to](https://en.cppreference.com/w/cpp/utility/functional/equal_to)
