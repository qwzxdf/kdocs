---
title: std::hive
summary: "要素を挿入・削除しても、他の要素の位置が変わらない順序なしコンテナ。"
order: 900
tags:
  - コンテナ
---

# std::hive

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <hive>`
</div>

ゲームのエンティティのように、頻繁に追加・削除され、削除しても他の要素へのポインタが無効にならないでほしいコンテナがあります。`std::hive` は、要素を複数のブロックに分けて持ち、**削除された場所を再利用する**ことで、ポインタを安定させつつ、挿入・削除を速くします。順序は保証されません。

!!! tip "ポイント"
    - 要素へのポインタ・イテレータが、挿入・削除で無効にならない（削除した要素自身は除く）。
    - 順序は保証されない（隙間を再利用するため）。
    - C++26 の機能。`plf::colony` が元になった。

!!! info "このページを読む前に"
    [`std::vector`](vector.md) を先に読んでください。

## 関数の詳しい説明

### std::hive {#hive}

```cpp
template <class T, class Allocator = allocator<T>>
class hive;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 要素の型 |

- 戻り値: `insert`・`erase`・イテレータなどをもつ
- 計算量: 挿入・削除は 償却定数


## 実際に動かしてみる

```cpp
#include <hive>
#include <print>

int main() {
  std::hive<int> h = {1, 2, 3};
  h.insert(4);
  std::println("{}", h.size());
}
```

```text title="実行結果"
4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 敵やパーティクルの管理 | `std::hive<Enemy>` に追加し、倒したら `erase` |

## よくあるミス

??? failure "順序を期待する"
    挿入した順に並ぶとは限りません。順序が必要なら `vector` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vector`](vector.md) | 連続した順序つきの配列 |
| [`list`](list.md) | ポインタは安定だがキャッシュに弱い |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます（`plf::hive` が使える）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 位置が安定する順序なしコンテナ
    - [x] 削除した場所を再利用する
    - [x] C++26

## 関連ページ

- [cpprefjp: std::hive](https://cpprefjp.github.io/reference/hive/hive.html)
- [cppreference: std::hive](https://en.cppreference.com/w/cpp/container/hive)
