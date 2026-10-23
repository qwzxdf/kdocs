---
title: std::cbegin
summary: "コンテナや配列の先頭を指す、const のイテレータを返す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::cbegin

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-14">C++14</span>
`#include <iterator>`
</div>

読むだけの走査では、書き換えられない `const_iterator` を使うほうが安全です。`std::cbegin(c)` は、コンテナなら `c.cbegin()`、配列なら先頭へのポインタを返します。

!!! tip "ポイント"
    - コンテナでも C の配列でも同じ書き方で使える。
    - `c.cbegin()` と同じ働き。
    - ジェネリックなコードで使う。

!!! info "このページを読む前に"
    [`std::begin`](begin.md) を先に読んでください。

## 関数の詳しい説明

### std::cbegin {#cbegin}

```cpp
template <class C>
constexpr auto cbegin(const C& c) -> decltype(std::begin(c));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ / 配列 | 対象 |

- 戻り値: コンテナや配列の先頭を指す、const のイテレータを返す
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", *std::cbegin(v));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックな走査を書く |

## よくあるミス

??? failure "空のコンテナの先頭を読む"
    空のコンテナで `*cbegin(c)` を読むと未定義動作です。`empty()` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cend`](cend.md) | 対になる関数 |
| [`std::begin`](begin.md) | 先頭 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンテナや配列の先頭を指す、const のイテレータを返す
    - [x] コンテナでも C の配列でも同じ書き方で使える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::cbegin](https://cpprefjp.github.io/reference/iterator/cbegin.html)
- [cppreference: std::cbegin](https://en.cppreference.com/w/cpp/iterator/cbegin)
