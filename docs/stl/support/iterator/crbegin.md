---
title: std::crbegin
summary: "const の逆順イテレータで、末尾の要素を指す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::crbegin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <iterator>`
</div>

逆順に読むだけ（書き換えない）とき、`crbegin(c)` と書くと、const の逆順イテレータが得られます。`c.crbegin()` と同じです。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::crbegin {#crbegin}

```cpp
auto crbegin(/* ... */);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c / it` | コンテナ / イテレータ | 対象 |

- 戻り値: const の逆順イテレータで、末尾の要素を指す
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", *std::crbegin(v));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 逆順に走査する |

## よくあるミス

??? failure "`end()` の指す先を読む"
    空のコンテナで `*crbegin` を読むと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rbegin`](reverse_iterator.md) | const でない版 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] const の逆順イテレータで、末尾の要素を指す
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::crbegin](https://cpprefjp.github.io/reference/iterator/crbegin.html)
- [cppreference: std::crbegin](https://en.cppreference.com/w/cpp/iterator/crbegin)
