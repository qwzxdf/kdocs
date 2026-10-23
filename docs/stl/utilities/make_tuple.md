---
title: std::make_tuple
summary: "型を推論して tuple を作る。"
order: 53
tags:
  - ユーティリティ
---

# std::make_tuple

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`std::make_tuple` は、**値から型を推論して `std::tuple` を作る**関数です。C++17 以降は、`std::tuple(a, b, c)` や `{a, b, c}` で足ります。

!!! tip "ポイント"
    - C++17 以降は `std::tuple(a, b, c)` で足りる。
    - 参照のまま持たせるなら [`std::tie`](tie.md) か `std::ref`。
    - 中身は**コピー**（またはムーブ）される。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::make_tuple {#make_tuple}

```cpp
template <class... Types>
constexpr std::tuple<VTypes...> make_tuple(Types&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args...` | 可変個 | まとめる値 |

- 戻り値: `std::tuple<VTypes...>`
- 計算量: O(n)

```cpp
#include <print>
#include <tuple>

int main() {
  auto t = std::make_tuple(1, 'a', 2.5);  // tuple<int, char, double>
  std::println("{}", t);
}
```

```text title="実行結果"
(1, 'a', 2.5)
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートの中で、受け取った値をまとめる | `std::make_tuple(args...)` |

## よくあるミス

??? failure "参照を保持したつもりが、コピーになる"
    `std::make_tuple(x)` は `x` のコピーを持ちます。参照を持たせるなら `std::tie(x)` か `std::make_tuple(std::ref(x))`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tuple`](tuple.md) | 本体 |
| [`std::tie`](tie.md) | 参照のtuple |
| [`std::make_pair`](make_pair.md) | pair 版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型を推論して tuple を作る
    - [x] C++17 以降は `std::tuple(a, b)` で足りる
    - [x] 中身はコピー

## 関連ページ

- [cpprefjp: std::make_tuple](https://cpprefjp.github.io/reference/tuple/make_tuple.html)
- [cppreference: std::make_tuple](https://en.cppreference.com/w/cpp/utility/tuple/make_tuple)
