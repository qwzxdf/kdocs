---
title: std::less_equal
summary: "`a <= b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::less_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

「以下」を述語として渡したいときに使います。`less` は等しい値を含まないので、含めたいときはこちらです。

!!! tip "ポイント"
    - `std::less_equal<>{}` と書くと型を推論してくれる（透過版）。
    - アルゴリズムの引数に、ラムダを書かずに渡せる。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::less_equal {#less_equal}

```cpp
template <class T = void>
struct less_equal {
  constexpr auto operator()(const T& a, const T& b) const;  // a <= b
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | T | 左辺（1 つ目の値） |
| `b` | T | 右辺（2 つ目の値） |

- 戻り値: `a <= b` の結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("{}", std::less_equal<>{}(4, 3));
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 上限以下かを判定する述語 | `auto le = std::bind_front(std::less_equal<>{}, score);`（`le(100)` は `score <= 100`） |

## よくあるミス

??? failure "整列の比較に使う"
    `sort` の比較関数には使えません。同じ値で `true` を返すと未定義動作になります。`less` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`less`](less.md) | `<` |
| [`greater_equal`](greater_equal.md) | `>=` |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] a <= b を関数オブジェクトにしたもの
    - [x] 型を省略した `std::less_equal<>{}` が便利
    - [x] アルゴリズムにそのまま渡せる

## 関連ページ

- [cpprefjp: std::less_equal](https://cpprefjp.github.io/reference/functional/less_equal.html)
- [cppreference: std::less_equal](https://en.cppreference.com/w/cpp/utility/functional/less_equal)
