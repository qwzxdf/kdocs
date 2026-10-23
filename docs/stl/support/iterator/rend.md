---
title: std::rend
summary: "コンテナや配列の逆順の終端（先頭の手前）を指すイテレータを返す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::rend

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <iterator>`
</div>

`rbegin` と組み合わせて、逆順の走査の終わりを表します。

!!! tip "ポイント"
    - コンテナでも C の配列でも同じ書き方で使える。
    - `c.rend()` と同じ働き。
    - ジェネリックなコードで使う。

!!! info "このページを読む前に"
    [`std::begin`](begin.md) を先に読んでください。

## 関数の詳しい説明

### std::rend {#rend}

```cpp
template <class C>
constexpr auto rend(C& c) -> decltype(c.rend());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ / 配列 | 対象 |

- 戻り値: コンテナや配列の逆順の終端（先頭の手前）を指すイテレータを返す
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", std::distance(std::rbegin(v), std::rend(v)));
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
| [`rbegin`](rbegin.md) | 対になる関数 |
| [`std::begin`](begin.md) | 先頭 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンテナや配列の逆順の終端（先頭の手前）を指すイテレータを返す
    - [x] コンテナでも C の配列でも同じ書き方で使える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::rend](https://cpprefjp.github.io/reference/iterator/rend.html)
- [cppreference: std::rend](https://en.cppreference.com/w/cpp/iterator/rend)
