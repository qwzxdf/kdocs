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

`std::transform` に、メンバー関数を渡したい場面があります。`&Player::GetHp` はそのままでは、`f(x)` の形で呼べません。`std::mem_fn(&Player::GetHp)` は、<strong>メンバーへのポインターを、普通の関数のように呼べる関数オブジェクトに変えます</strong>。

!!! tip "ポイント"
    - `std::mem_fn(pm)` はメンバーへのポインターを関数オブジェクトにする
    - 呼ぶときは、最初の引数にオブジェクト（またはポインター）を渡す
    - メンバー変数にも使える
    - C++20 以降は、ラムダや `std::invoke`、射影でも代用できる

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::mem_fn {#mem_fn}

<span class="ver ver-11">C++11</span>

```cpp
template <class R, class T>
constexpr /* 関数オブジェクト */ mem_fn(R T::* pm) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pm` | メンバーへのポインター | メンバー関数またはメンバー変数へのポインター |

返る関数オブジェクトは、`obj` をオブジェクトまたはそのポインター、スマート ポインターとして受け取り、メンバーを呼びます。

`std::ranges` のアルゴリズムでは、射影に `&Player::hp` のようにメンバー ポインターを直接渡せるので、`mem_fn` の出番は減っています。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

struct Player {
  int hp;
  int GetHp() const { return hp; }
};

int main() {
  const std::vector<Player> players = {{30}, {80}, {50}};
  std::vector<int> hps(players.size());
  std::transform(players.begin(), players.end(), hps.begin(), std::mem_fn(&Player::GetHp));
  for (int h : hps) std::print("{} ", h);
  std::println("");
}
```

```text title="実行結果"
30 80 50 
```

## ゲームでの使いどころ

メンバー関数を、アルゴリズムの引数として渡します。

```cpp
auto total = std::transform_reduce(items.begin(), items.end(), 0, std::plus<>{}, std::mem_fn(&Item::Price));
```

## よくあるミス

??? failure "`const` でないメンバー関数を `const` オブジェクトに呼ぶ"
    `const` メンバー関数にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invoke`](invoke.md) | 直接呼び出す |
| [`bind_front`](bind_front.md) | オブジェクトを先に結びつける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mem_fn(pm)` はメンバーポインターを関数オブジェクトにする
    - [x] 最初の引数がオブジェクト
    - [x] `ranges` では射影で代用できる

## 関連ページ

- [cpprefjp: std::mem_fn](https://cpprefjp.github.io/reference/functional/mem_fn.html)
- [cppreference: std::mem_fn](https://en.cppreference.com/w/cpp/utility/functional/mem_fn)
