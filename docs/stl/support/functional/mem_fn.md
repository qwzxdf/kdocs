---
title: std::mem_fn
summary: "メンバ関数ポインターを、普通の関数のように呼べるようにする。"
order: 13
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::mem_fn

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`std::mem_fn(&Class::member)` は、**メンバ関数（またはメンバ変数）へのポインターを、`f(obj)` の形で呼べる関数オブジェクトにする**道具です。`transform` や `for_each` に渡して、各オブジェクトのメンバ関数を呼ぶときに使います。

!!! tip "ポイント"
    - ranges のアルゴリズムは、メンバポインターをそのまま渡せる（`&Enemy::hp`）ので、`mem_fn` は不要なことが多い。
    - 古い `std::for_each` などで必要になる。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::mem_fn {#mem_fn}

```cpp
template <class M, class T>
/* unspecified */ mem_fn(M T::* pm) noexcept;
```

- メンバ関数のポインタを、`f(obj, 引数...)` の形で呼べる関数オブジェクトにします。今は `std::invoke` やプロジェクションで足ります

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

struct Player {
  int hp;
  int Doubled() const { return hp * 2; }
};

int main() {
  Player p{7};
  std::println("{} {}", std::mem_fn(&Player::Doubled)(p), std::mem_fn(&Player::hp)(p));
}
```

```text title="実行結果"
14 7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 各敵の Update を呼ぶ（古い書き方） | `std::for_each(v.begin(), v.end(), std::mem_fn(&Enemy::Update))` |

## よくあるミス

??? failure "ranges で不要なのに使う"
    `std::ranges::for_each(v, &Enemy::Update)` のように、メンバポインターを直接渡せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invoke`](invoke.md) | メンバポインターも呼べる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メンバポインターを呼べる関数にする
    - [x] ranges なら直接渡せる
    - [x] 古いコードで見かける

## 関連ページ

- [cpprefjp: std::mem_fn](https://cpprefjp.github.io/reference/functional/mem_fn.html)
- [cppreference: std::mem_fn](https://en.cppreference.com/w/cpp/utility/functional/mem_fn)
