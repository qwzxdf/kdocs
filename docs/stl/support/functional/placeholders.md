---
title: std::placeholders
summary: "bind の引数の位置を表す _1, _2, … の名前空間。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::placeholders

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`std::bind` で、関数の引数のうち「あとから渡す分」だけを空けておきたい。その空きの場所を表す印が `std::placeholders::_1`、`_2` … です。`_1` は、できあがった関数オブジェクトを呼ぶときの 1 番目の引数、`_2` は 2 番目の引数、という意味になります。

!!! tip "ポイント"
    - `_1`、`_2` … は、呼び出し時の引数の位置を表す
    - 同じ印を何度使ってもよい（`_1` を 2 回書くと、同じ値が 2 か所に入る）
    - 引数の順番を入れ替えるのにも使える
    - 新しいコードでは、ラムダか [`bind_front`](bind_front.md) のほうが読みやすい

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::placeholders {#placeholders}

```cpp
namespace std::placeholders {
  inline constexpr /* 実装定義 */ _1, _2, _3 /* ... */;
}
```

`_1` から先は、実装が決める数まで用意されています（少なくとも `_10` ぐらいまで）。名前空間が長いので、関数の中で `using namespace std::placeholders;` と書くのが一般的です。

#### 位置の指定

`bind(f, _2, _1)` は、「できあがった関数を `g(a, b)` と呼んだら、`f(b, a)` を呼ぶ」という意味です。引数の順番を入れ替えられます。

#### 同じ印を複数回使う

`bind(Mul, _1, _1)` は、「`g(a)` と呼ぶと `Mul(a, a)`」です。1 つの値を複数の場所に使えます。

#### 渡さなかった引数

呼び出し側が渡した引数のうち、どの印にも使われなかったものは、捨てられます。たとえば `bind(f, _1)` を `g(1, 2)` と呼ぶと、2 は使われません。

#### ラムダとの比較

ラムダなら `[](int a, int b) { return Sub(b, a); }` と書けて、型も引数の名前も見えます。`bind` は「どの印がどの位置か」を頭の中で数える必要があり、読みにくくなりがちです。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int Sub(int a, int b) { return a - b; }
int Mul(int a, int b) { return a * b; }

int main() {
  using namespace std::placeholders;

  // 引数の順番を入れ替える: g(a, b) -> Sub(b, a)
  auto swapped = std::bind(Sub, _2, _1);
  std::println("Sub(10, 3) = {}", Sub(10, 3));
  std::println("入れ替え後 g(10, 3) = {}", swapped(10, 3));

  // 同じ印を 2 回: g(a) -> Mul(a, a)
  auto square = std::bind(Mul, _1, _1);
  std::println("square(5) = {}", square(5));

  // 一部を固定して、残りをあとで渡す
  auto times_ten = std::bind(Mul, _1, 10);
  std::println("times_ten(7) = {}", times_ten(7));
}
```

```text title="実行結果"
Sub(10, 3) = 7
入れ替え後 g(10, 3) = -7
square(5) = 25
times_ten(7) = 70
```

## ゲームでの使いどころ

古いコードや、`bind` を前提にしたライブラリに出会ったときに、読めるようにしておく知識です。新しく書くときは、ラムダのほうが分かりやすくなります。

## よくあるミス

??? failure "位置の数え間違い"
    `_1` は「関数の 1 番目の引数」ではなく、「呼び出し時の 1 番目の引数」です。`bind(f, _2, _1)` で意味が逆になるのを間違えやすいです。

??? failure "名前空間を忘れる"
    `_1` は `std::placeholders` の中にあります。`std::_1` ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind`](bind.md) | 使う関数 |
| [`bind_front`](bind_front.md) | 先頭の引数を固定する、読みやすい版 |
| [`is_placeholder`](is_placeholder.md) | 印かどうかを調べる |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::placeholders](https://cpprefjp.github.io/reference/functional/placeholders.html)
- [cppreference: std::placeholders](https://en.cppreference.com/w/cpp/utility/functional/placeholders)
