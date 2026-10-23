---
title: std::cend
summary: "コンテナや配列の終端を指す、const のイテレータを返す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::cend

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <iterator>`
</div>

`cbegin` と組み合わせて、読むだけの走査の終わりを表します。

!!! tip "ポイント"
    - コンテナでも C の配列でも同じ書き方で使える。
    - `c.cend()` と同じ働き。
    - ジェネリックなコードで使う。

!!! info "このページを読む前に"
    [`std::begin`](begin.md) を先に読んでください。

## 関数の詳しい説明

### std::cend {#cend}

```cpp
template <class C>
constexpr auto cend(const C& c) -> decltype(std::end(c));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ / 配列 | 対象 |

- 戻り値: コンテナや配列の終端を指す、const のイテレータを返す
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", std::distance(std::cbegin(v), std::cend(v)));
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
    終端の位置は読めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cbegin`](cbegin.md) | 対になる関数 |
| [`std::begin`](begin.md) | 先頭 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンテナや配列の終端を指す、const のイテレータを返す
    - [x] コンテナでも C の配列でも同じ書き方で使える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::cend](https://cpprefjp.github.io/reference/iterator/cend.html)
- [cppreference: std::cend](https://en.cppreference.com/w/cpp/iterator/cend)
