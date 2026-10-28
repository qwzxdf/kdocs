---
title: std::advance
summary: "イテレータそのものを n 個進める（戻り値なし）。"
order: 3
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::advance

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::next` が新しいイテレーターを返すのに対して、`std::advance` は<strong>渡したイテレーターそのものを `n` 個進めます</strong>。戻り値はありません。

!!! tip "ポイント"
    - `std::advance(it, n)` は `it` 自身を `n` 個進める
    - 戻り値はない（`it` が変わる）
    - `n` が負なら戻る（双方向以上）
    - 新しいイテレーターが欲しいなら `std::next`

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::advance {#advance}

<span class="ver ver-98">C++98</span>

```cpp
template <class It, class Distance>
constexpr void advance(It& it, Distance n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | イテレーター | 進める対象（参照） |
| `n` | 整数 | 進める数 |

引数のイテレーターを書き換えます。ランダムアクセスのイテレーターは O(1)、そうでなければ O(n) です。

コードの意図が読み取りやすいのは `std::next` です。`advance` は、イテレーターを更新しながらループするような場面で使います。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <list>
#include <print>

int main() {
  std::list<int> l = {10, 20, 30, 40};
  auto it = l.begin();
  std::advance(it, 2);                  // it 自身が進む
  std::println("2 つ進めた先: {}", *it);
}
```

```text title="実行結果"
2 つ進めた先: 30
```

## ゲームでの使いどころ

イテレーターを読み進めながら処理します。新しい値が必要なときは `std::next` が読みやすいです。

## よくあるミス

??? failure "戻り値があると思って代入する"
    戻り値はありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`next`](next.md) | 新しいイテレーターを返す |
| [`distance`](distance.md) | 距離 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::advance(it, n)` は `it` 自身を進める
    - [x] 戻り値はない
    - [x] 新しい値が欲しいなら `next`

## 関連ページ

- [cpprefjp: std::advance](https://cpprefjp.github.io/reference/iterator/advance.html)
- [cppreference: std::advance](https://en.cppreference.com/w/cpp/iterator/advance)
