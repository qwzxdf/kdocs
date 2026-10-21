---
title: std::make_from_tuple
summary: "tuple の要素を引数にして、クラスのオブジェクトを作る。"
order: 55
tags:
  - ユーティリティ
---

# std::make_from_tuple

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <tuple>`
</div>

`std::make_from_tuple` は、**tuple の要素をコンストラクタの引数にして、指定したクラスのオブジェクトを作る**関数です。[`std::apply`](apply.md) の「オブジェクトを作る版」です。

!!! tip "ポイント"
    - `std::make_from_tuple<Vec>(std::make_tuple(3, 4))` は `Vec(3, 4)` と同じ。
    - 設定データ（tuple）から、オブジェクトを組み立てるときに使える。

## 関数の詳しい説明

### std::make_from_tuple {#make_from_tuple}

```cpp
template <class T, class Tuple>
constexpr T make_from_tuple(Tuple&& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 作りたい型 |
| `t` | tuple | コンストラクタの引数をまとめた tuple |

- 戻り値: `T` のオブジェクト
- 計算量: コンストラクタによる

```cpp
#include <print>
#include <tuple>

struct Vec {
  Vec(int x, int y) : x(x), y(y) {}
  int x;
  int y;
};

int main() {
  auto args = std::make_tuple(3, 4);
  Vec v = std::make_from_tuple<Vec>(args);
  std::println("{} {}", v.x, v.y);
}
```

```text title="実行結果"
3 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 保存しておいた引数から、オブジェクトを作る | `std::make_from_tuple<Enemy>(args)` |

## よくあるミス

??? failure "型を書き忘れる"
    テンプレート引数で、作りたい型を明示します（`make_from_tuple<T>(t)`）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::apply`](apply.md) | 関数を呼ぶ |
| [`std::make_unique`](make_unique.md) | ヒープに作って `unique_ptr` にする |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tuple の要素でオブジェクトを作る
    - [x] 作る型を明示する
    - [x] C++17

## 関連ページ

- [cpprefjp: std::make_from_tuple](https://cpprefjp.github.io/reference/tuple/make_from_tuple.html)
- [cppreference: std::make_from_tuple](https://en.cppreference.com/w/cpp/utility/make_from_tuple)
