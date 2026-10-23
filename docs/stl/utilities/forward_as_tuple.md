---
title: std::forward_as_tuple
summary: "引数を完全転送のまま、参照の tuple にまとめる。"
order: 57
tags:
  - ユーティリティ
---

# std::forward_as_tuple

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`std::forward_as_tuple` は、**引数を、左辺値・右辺値の区別を保ったまま、参照の tuple にまとめる**関数です。他の関数へ引数の束をそのまま転送するときに使います。[`std::piecewise_construct`](piecewise_construct.md) と組み合わせて、`map::emplace` に使うのが典型です。

!!! tip "ポイント"
    - 作った tuple は**参照**を持つだけ。コピーはしない。
    - 長く保存してはいけない（元の値が消えるとぶら下がる）。
    - `std::apply` や `piecewise_construct` へ渡すために使う。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::forward_as_tuple {#forward_as_tuple}

```cpp
template <class... Types>
constexpr std::tuple<Types&&...> forward_as_tuple(Types&&... args) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args...` | 可変個 | 転送する引数 |

- 戻り値: 各引数への参照を持つ tuple
- 計算量: O(1)

```cpp
#include <print>
#include <tuple>

int Add3(int a, int b, int c) { return a + b + c; }

int main() {
  // 引数を参照の tuple にまとめて、apply で展開して呼ぶ
  std::println("{}", std::apply(Add3, std::forward_as_tuple(1, 2, 3)));
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `map::emplace` で、キーと値のコンストラクタ引数を別々に渡す | `emplace(piecewise_construct, forward_as_tuple(...), forward_as_tuple(...))` |

## よくあるミス

??? failure "保存して後で使う"
    参照の tuple を、元の値が消えたあとで使うと未定義動作です。保存するなら `std::make_tuple` でコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tie`](tie.md) | 左辺値の参照だけ |
| [`std::make_tuple`](make_tuple.md) | コピーを持つ |
| [`std::piecewise_construct`](piecewise_construct.md) | pair の構築に使う |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数を転送用の参照 tuple にする
    - [x] 保存しない
    - [x] `piecewise_construct` と使う

## 関連ページ

- [cpprefjp: std::forward_as_tuple](https://cpprefjp.github.io/reference/tuple/forward_as_tuple.html)
- [cppreference: std::forward_as_tuple](https://en.cppreference.com/w/cpp/utility/tuple/forward_as_tuple)
