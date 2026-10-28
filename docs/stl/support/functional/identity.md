---
title: std::identity
summary: "受け取った値をそのまま返す関数オブジェクト。"
order: 6
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::identity

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <functional>`
</div>

引数をそのまま返すだけの関数オブジェクトが、役に立つ場面があります。`std::ranges` のアルゴリズムは「どの部分を比べるか」を射影（projection）で指定でき、既定の射影が何もしないもの、つまり `std::identity` です。

!!! tip "ポイント"
    - `std::identity{}(x)` は `x` をそのまま返す
    - `std::ranges` のアルゴリズムの既定の射影
    - コピーせず、参照のまま転送する
    - C++20 で追加

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::identity {#identity}

<span class="ver ver-20">C++20</span>

```cpp
struct identity {
  template <class T>
  constexpr T&& operator()(T&& t) const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 値 | そのまま返す値 |

`operator()` は、受け取った引数を同じ値カテゴリーのまま返します。左辺値を渡せば左辺値参照、右辺値を渡せば右辺値参照が返り、コピーは起きません。

自分で使う場面は多くありません。射影を受け取る自作のアルゴリズムで、「射影なし」の既定値として書くのが主な用途です。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  int x = 5;
  std::println("identity(5) = {}", std::identity{}(x));
  std::println("参照のまま返す: {}", &std::identity{}(x) == &x);
}
```

```text title="実行結果"
identity(5) = 5
参照のまま返す: true
```

## ゲームでの使いどころ

射影を受け取る自作のアルゴリズムの既定値にします。

```cpp
template <class R, class Proj = std::identity>
auto MaxBy(R&& range, Proj proj = {});   // 何も指定しなければ要素そのもので比べる
```

## よくあるミス

??? failure "コピーが起きると思う"
    参照のまま返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<functional>`](../functional.md) | 関数オブジェクトの一覧 |
| [`plus`](plus.md) | 演算の関数オブジェクト |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::identity` は引数をそのまま返す
    - [x] `ranges` のアルゴリズムの既定の射影
    - [x] 参照のまま転送する

## 関連ページ

- [cpprefjp: std::identity](https://cpprefjp.github.io/reference/functional/identity.html)
- [cppreference: std::identity](https://en.cppreference.com/w/cpp/utility/functional/identity)
