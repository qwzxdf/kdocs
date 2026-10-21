---
title: std::make_pair
summary: "型を推論して pair を作る。"
order: 52
tags:
  - ユーティリティ
---

# std::make_pair

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <utility>`
</div>

`std::make_pair` は、**値から型を推論して `std::pair` を作る**関数です。C++17 以降は、クラステンプレートの型推論（CTAD）が使えるので、`std::pair(a, b)` や `{a, b}` と書けば足ります。古いコードや、他人のコードを読むときのために知っておく関数です。

!!! tip "ポイント"
    - C++17 以降は `std::pair(a, b)` / `{a, b}` で足りる。
    - 参照を保持したいときは `std::make_pair(std::ref(x), 2)` のように `std::ref` を使う。
    - 文字列リテラルは `const char*` として保存される（`std::string` にしたいなら明示する）。

## 関数の詳しい説明

### std::make_pair {#make_pair}

```cpp
template <class T1, class T2>
constexpr std::pair<V1, V2> make_pair(T1&& t, T2&& u);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | T1 | 1 つ目の値 |
| `u` | T2 | 2 つ目の値 |

- 戻り値: `std::pair<V1, V2>`（`V` は `std::decay` した型。`reference_wrapper` は参照になる）
- 計算量: O(1)

```cpp
#include <print>
#include <utility>

int main() {
  auto p = std::make_pair(3, 4.5);           // pair<int, double>
  auto q = std::pair(3, 4.5);                // C++17: 型を推論してくれる
  std::println("{} {} {}", p.first, p.second, p == q);
}
```

```text title="実行結果"
3 4.5 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| map に要素を追加する（古い書き方） | `m.insert(std::make_pair(key, value));` |

## よくあるミス

??? failure "文字列リテラルが std::string にならない"
    `std::make_pair("a", 1)` の 1 つ目は `const char*` です。`std::string` が欲しいなら、`std::pair<std::string, int>{"a", 1}` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::pair`](pair.md) | 本体 |
| [`std::make_tuple`](make_tuple.md) | tuple 版 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型を推論して pair を作る
    - [x] C++17 以降は `{a, b}` で足りる
    - [x] 古いコードで見かける

## 関連ページ

- [cpprefjp: std::make_pair](https://cpprefjp.github.io/reference/utility/make_pair.html)
- [cppreference: std::make_pair](https://en.cppreference.com/w/cpp/utility/pair/make_pair)
