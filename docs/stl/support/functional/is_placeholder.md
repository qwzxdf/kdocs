---
title: std::is_placeholder
summary: "型がプレースホルダー（_1 など）か、何番かを調べる型特性。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::is_placeholder

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

`bind` の中で `_1` や `_2` を見分ける仕組みが `is_placeholder` です。プレースホルダーなら番号（1, 2, …）、そうでなければ 0 になります。

!!! tip "ポイント"
    - `_1` の型なら 1、`_2` なら 2、それ以外は 0。
    - 自作のプレースホルダーを作るときに特殊化する。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_placeholder {#is_placeholder}

```cpp
template <class T> struct is_placeholder;
template <class T> inline constexpr int is_placeholder_v = is_placeholder<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: プレースホルダーなら番号、そうでなければ 0
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  using namespace std::placeholders;
  std::println("{}", std::is_placeholder_v<decltype(_1)>);
  std::println("{}", std::is_placeholder_v<decltype(_3)>);
  std::println("{}", std::is_placeholder_v<int>);
}
```

```text title="実行結果"
1
3
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで引数が `_N` かを判定 | `std::is_placeholder_v<decltype(_2)>` |

## よくあるミス

??? failure "値と型を取り違える"
    判定するのは型です。`decltype(_1)` のように型を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_bind_expression`](is_bind_expression.md) | bind 式かどうか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] プレースホルダーの番号を返す型特性
    - [x] プレースホルダーでなければ 0
    - [x] 普通は使わない

## 関連ページ

- [cpprefjp: std::is_placeholder](https://cpprefjp.github.io/reference/functional/is_placeholder.html)
- [cppreference: std::is_placeholder](https://en.cppreference.com/w/cpp/utility/functional/is_placeholder)
