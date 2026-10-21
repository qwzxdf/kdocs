---
title: std::bind_back
summary: "関数の末尾の引数をあらかじめ決めた、新しい関数を作る。"
order: 10
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bind_back

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <functional>`
</div>

`std::bind_back(f, a)` は、**関数 `f` の最後の引数を `a` に決めた、新しい呼び出し可能オブジェクト**を作ります。[`bind_front`](bind_front.md) の後ろ版です。パイプ（`|`）の中で、`transform` に渡す関数を作るときなどに便利です。

!!! tip "ポイント"
    - `std::bind_back(std::plus{}, 10)` は、「10 を足す関数」。
    - C++23 の機能。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::bind_back {#bind_back}

<span class="ver ver-23">C++23</span>

```cpp
template <class F, class... Args>
constexpr auto bind_back(F&& f, Args&&... args);
```

- 後ろのほうの引数を固定します

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  auto minus3 = std::bind_back(std::minus{}, 3);  // 後ろの引数を 3 に固定
  std::println("{}", minus3(10));
}
```

```text title="実行結果"
7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パイプの中で使う「10 を足す関数」 | `std::views::transform(std::bind_back(std::plus{}, 10))` |

## よくあるミス

??? failure "古い環境で使えない"
    C++23 の機能です。ラムダ式で代用できます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind_front`](bind_front.md) | 先頭の引数を決める |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 末尾の引数を決めた関数を作る
    - [x] `bind_front` の後ろ版
    - [x] C++23

## 関連ページ

- [cpprefjp: std::bind_back](https://cpprefjp.github.io/reference/functional/bind_back.html)
- [cppreference: std::bind_back](https://en.cppreference.com/w/cpp/utility/functional/bind_back)
