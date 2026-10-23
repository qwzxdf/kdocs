---
title: std::rbegin
summary: "コンテナや配列の逆順の先頭（最後の要素）を指すイテレータを返す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::rbegin

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-14">C++14</span>
`#include <iterator>`
</div>

後ろから前へ走査したいとき、`std::rbegin(c)` が、最後の要素を指すイテレータを返します。コンテナなら `c.rbegin()`、配列なら `reverse_iterator` を作って返します。

!!! tip "ポイント"
    - コンテナでも C の配列でも同じ書き方で使える。
    - `c.rbegin()` と同じ働き。
    - ジェネリックなコードで使う。

!!! info "このページを読む前に"
    [`std::begin`](begin.md) を先に読んでください。

## 関数の詳しい説明

### std::rbegin {#rbegin}

```cpp
template <class C>
constexpr auto rbegin(C& c) -> decltype(c.rbegin());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ / 配列 | 対象 |

- 戻り値: コンテナや配列の逆順の先頭（最後の要素）を指すイテレータを返す
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", *std::rbegin(v));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックな走査を書く |

## よくあるミス

??? failure "空のコンテナの先頭を読む"
    空のコンテナで `*rbegin(c)` を読むと未定義動作です。`empty()` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rend`](rend.md) | 対になる関数 |
| [`std::begin`](begin.md) | 先頭 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンテナや配列の逆順の先頭（最後の要素）を指すイテレータを返す
    - [x] コンテナでも C の配列でも同じ書き方で使える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::rbegin](https://cpprefjp.github.io/reference/iterator/rbegin.html)
- [cppreference: std::rbegin](https://en.cppreference.com/w/cpp/iterator/rbegin)
