---
title: std::make_move_iterator
summary: "参照外しするとムーブされるイテレータ。"
order: 13
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::make_move_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::copy` でコンテナを別のコンテナに移すと、要素がコピーされます。`std::string` や `std::vector` のような重い要素は、コピーでなくムーブしたい。`std::move_iterator` は、<strong>参照すると、右辺値参照として要素を返す</strong>アダプターです。

!!! tip "ポイント"
    - `std::make_move_iterator(it)` で作る
    - 参照すると、要素を右辺値参照で返す（ムーブされる）
    - `std::copy` に渡すと、コピーでなくムーブになる
    - 元の要素は、ムーブ後の有効だが未規定の状態

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::move_iterator {#move_iterator}

<span class="ver ver-11">C++11</span>

```cpp
template <class It>
class move_iterator {
 public:
  explicit move_iterator(It it);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | イテレーター | 包む元のイテレーター |

`*it` が `std::move(*base)` と同じ右辺値を返します。そのため、`std::copy` や `vector` のコンストラクターで要素を代入するとき、ムーブ代入・ムーブ構築が選ばれます。

ムーブしたあとの要素は、有効だが中身が未規定です。使わずに、破棄するか、新しい値を代入します。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> src = {std::string(40, 'a'), std::string(40, 'b')};
  std::vector<std::string> dst(std::make_move_iterator(src.begin()), std::make_move_iterator(src.end()));
  std::println("dst[0] の長さ = {}", dst[0].size());
  std::println("src[0] は移された: {}", src[0].empty());
}
```

```text title="実行結果"
dst[0] の長さ = 40
src[0] は移された: true
```

## ゲームでの使いどころ

大きな要素のコンテナを、コピーなしで別のコンテナに移します。

```cpp
std::vector<Enemy> alive(std::make_move_iterator(all.begin()), std::make_move_iterator(all.end()));
```

## よくあるミス

??? failure "ムーブ後の要素を使う"
    中身は未規定です。使いません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`move`](../../algorithms/move.md) | 範囲をムーブするアルゴリズム |
| [`move_sentinel`](move_sentinel.md) | 終端を表す番兵 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `move_iterator` は要素を右辺値で返すアダプター
    - [x] `copy` がムーブになる
    - [x] ムーブ後の要素は未規定

## 関連ページ

- [cpprefjp: std::make_move_iterator](https://cpprefjp.github.io/reference/iterator/move_iterator.html)
- [cppreference: std::make_move_iterator](https://en.cppreference.com/w/cpp/iterator/move_iterator)
