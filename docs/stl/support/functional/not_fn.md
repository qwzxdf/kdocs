---
title: std::not_fn
summary: "条件を逆にした関数を作る。"
order: 11
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::not_fn

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

`std::not_fn(f)` は、**関数 `f` の結果を反転（`!`）した新しい関数**を作ります。`find_if` で「条件に合わないもの」を探したいとき、`copy_if` の条件を逆にしたいとき、などに使います。

!!! tip "ポイント"
    - `std::ranges::find_if(v, std::not_fn(IsDead))`。
    - `find_if_not` のほうが短いことも多い。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::not_fn {#not_fn}

<span class="ver ver-17">C++17</span>

```cpp
template <class F>
constexpr auto not_fn(F&& f);
```

- 結果を反転した関数を作ります（`IsDead` から「生きている」を作る）

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

bool IsDead(int hp) { return hp <= 0; }

int main() {
  std::vector<int> hp = {0, 20, -5, 40};
  auto alive = std::ranges::count_if(hp, std::not_fn(IsDead));
  auto half = std::bind_back(std::divides{}, 2);  // x / 2
  std::println("{} {} {}", alive, half(10), std::multiplies{}(3, 4));
}
```

```text title="実行結果"
2 5 12
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「生きていない」の条件を、既存の「生きている」関数から作る | `std::not_fn(IsAlive)` |

## よくあるミス

??? failure "古い std::not1 / not2 を使う"
    C++17 で削除されました。`not_fn` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find`](../../algorithms/find.md) | `find_if_not` もある |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件を逆にする
    - [x] `!f(x)` の関数を作る
    - [x] not1 / not2 は削除

## 関連ページ

- [cpprefjp: std::not_fn](https://cpprefjp.github.io/reference/functional/not_fn.html)
- [cppreference: std::not_fn](https://en.cppreference.com/w/cpp/utility/functional/not_fn)
