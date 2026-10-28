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

条件を反転した関数が欲しいことがあります。`std::remove_if` に「偶数」の条件を渡す代わりに、「偶数でない」を渡したい。`std::not_fn(f)` は、<strong>`f` の結果を反転する関数オブジェクト</strong>を作ります。

!!! tip "ポイント"
    - `std::not_fn(f)` は `!f(args...)` を返す関数オブジェクト
    - 引数の数や型は、`f` に従う
    - `std::remove_if` や `std::find_if` の条件を反転するのに使う
    - 古い `std::not1` / `std::not2` の後継

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::not_fn {#not_fn}

<span class="ver ver-17">C++17</span>

```cpp
template <class F>
constexpr /* 関数オブジェクト */ not_fn(F&& f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | 呼び出し可能なもの | 条件の関数 |

返った関数オブジェクトを呼ぶと、`f` を同じ引数で呼び、結果を `!` で反転して返します。`f` は何個の引数でも受け取れます。

ラムダで `[](int x) { return !IsEven(x); }` と書くのと同じです。条件の関数が名前を持つ関数のとき、`std::not_fn(IsEven)` のほうが短くなります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

bool IsEven(int x) { return x % 2 == 0; }

int main() {
  const std::vector<int> v = {1, 2, 3, 4, 5};
  std::println("偶数の数 : {}", std::count_if(v.begin(), v.end(), IsEven));
  std::println("奇数の数 : {}", std::count_if(v.begin(), v.end(), std::not_fn(IsEven)));
}
```

```text title="実行結果"
偶数の数 : 2
奇数の数 : 3
```

## ゲームでの使いどころ

既存の条件関数を、反転して使い回します。

```cpp
items.erase(std::remove_if(items.begin(), items.end(), std::not_fn(IsAlive)), items.end());
```

## よくあるミス

??? failure "`std::not1` / `std::not2` を使う"
    削除されました。`not_fn` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logical_not`](logical_not.md) | `!` の関数オブジェクト |
| [`bind_front`](bind_front.md) | 引数を固定 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `not_fn(f)` は `f` の結果を反転した関数オブジェクト
    - [x] 任意の数の引数に対応する
    - [x] `not1` / `not2` の後継

## 関連ページ

- [cpprefjp: std::not_fn](https://cpprefjp.github.io/reference/functional/not_fn.html)
- [cppreference: std::not_fn](https://en.cppreference.com/w/cpp/utility/functional/not_fn)
