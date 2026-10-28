---
title: std::bit_not
summary: "`~a`（ビット反転）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_not

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

全ビットを反転したいとき、`~` を渡せます。マスクの反転（立っているビットと落ちているビットを入れ替える）に使います。

!!! tip "ポイント"
    - `std::bit_not<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数にラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_not {#bit_not}

```cpp
template <class T = void>
struct bit_not {
  constexpr auto operator()(const T& a) const;  // ~a
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |

- 戻り値: `~a` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::bit_not<>{}(0));
}
```

```text title="実行結果"
-1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| マスクを反転して「それ以外」を作る | `std::bit_not<>{}(mask)` |

## よくあるミス

??? failure "符号付きの型で反転する"
    符号付き整数のビット反転は `-x - 1` と同じ値になります。マスク計算は `unsigned` で行います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logical_not`](logical_not.md) | `!` |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ~a を関数オブジェクトにしたもの
    - [x] 型を省略した `std::bit_not<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::bit_not](https://cpprefjp.github.io/reference/functional/bit_not.html)
- [cppreference: std::bit_not](https://en.cppreference.com/w/cpp/utility/functional/bit_not)
