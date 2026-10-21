---
title: std::move_if_noexcept
summary: "ムーブが例外を投げないときだけ、ムーブにする（そうでなければコピー）。"
order: 55
tags:
  - ユーティリティ
---

# std::move_if_noexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

`std::move_if_noexcept` は、**ムーブが例外を投げない（`noexcept`）ときだけムーブにして、そうでなければコピーにする**関数です。`vector` が再確保するときに、要素を安全に移すために使われています。普段のコードでは使いません。

!!! tip "ポイント"
    - ムーブが途中で例外を投げると、元の要素が壊れて、元に戻せない。
    - そこで「例外を投げないムーブのときだけ」ムーブを選び、そうでなければコピーする。
    - `vector` の再確保が、この仕組みを使っている。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) の考え方を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::move_if_noexcept {#move_if_noexcept}

```cpp
template <class T>
constexpr auto move_if_noexcept(T& x) noexcept;
```

- ムーブコンストラクタが `noexcept` ならムーブ、そうでなければコピーとして扱わせます。vector の再確保の中で使われている仕組みで、自分で書くことはまずありません

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <utility>

int main() {
  std::string s = "abc";
  std::string t = std::move_if_noexcept(s);   // string のムーブは noexcept なので、ムーブされる
  std::println("{} {}", t, s.empty());
}
```

```text title="実行結果"
abc true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 強い例外保証が必要な自作コンテナ | `std::move_if_noexcept(x)` |

## よくあるミス

??? failure "ムーブコンストラクタに noexcept を付け忘れる"
    ムーブコンストラクタに `noexcept` を付けないと、`vector` の再確保のたびにコピーになり、遅くなります。ムーブを書いたら `noexcept` も付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::move`](move.md) | 常にムーブにする |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ムーブが `noexcept` のときだけムーブにする
    - [x] `vector` の再確保が使っている
    - [x] 自作のムーブには `noexcept` を付ける

## 関連ページ

- [cpprefjp: std::move_if_noexcept](https://cpprefjp.github.io/reference/utility/move_if_noexcept.html)
- [cppreference: std::move_if_noexcept](https://en.cppreference.com/w/cpp/utility/move_if_noexcept)
