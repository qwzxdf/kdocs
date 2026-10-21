---
title: std::bind
summary: "関数の引数の一部を固定した、新しい関数を作る（古い書き方）。"
order: 12
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bind

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`std::bind` は、**関数の引数の一部を固定して、新しい関数を作る**道具です。`_1`、`_2` のプレースホルダーで、残りの引数の位置を指定します。C++11 で入りましたが、**ラムダ式や `bind_front` のほうが読みやすい**ため、新しいコードでは使いません。

!!! tip "ポイント"
    - 新しいコードでは、ラムダ式か `bind_front`。
    - 古いコードを読むために知っておく。
    - 参照渡しには `std::ref` が必要。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::bind {#bind}

```cpp
template <class F, class... Args>
/* unspecified */ bind(F&& f, Args&&... args);
```

- 引数の固定や並べ替えをする古い関数（`std::placeholders::_1` を使う）。読みにくいので、ラムダか `bind_front` を使います

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  auto add5 = std::bind(std::plus<int>{}, std::placeholders::_1, 5);  // 第 2 引数を 5 に固定
  std::println("{}", add5(3));
}
```

```text title="実行結果"
8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `std::bind(&F::f, obj, _1)` → `[&](auto x) { obj.f(x); }` |

## よくあるミス

??? failure "オーバーロードされた関数を bind する"
    型が決まらずコンパイルエラーになります。ラムダ式なら問題ありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind_front`](bind_front.md) | 先頭の引数を固定 |
| [ラムダ式](../../../basics/lambda.md) | 読みやすい |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数を固定した関数を作る
    - [x] 新しいコードはラムダ式
    - [x] 古いコードの読解用

## 関連ページ

- [cpprefjp: std::bind](https://cpprefjp.github.io/reference/functional/bind.html)
- [cppreference: std::bind](https://en.cppreference.com/w/cpp/utility/functional/bind)
