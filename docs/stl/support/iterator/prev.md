---
title: std::prev
summary: "イテレータを n 個戻した位置を返す（元は変えない）。"
order: 2
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::prev

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <iterator>`
</div>

末尾の要素を取りたい。`v.end()` は最後の要素の「1 つ後ろ」なので、参照できません。`std::prev(v.end())` は、<strong>イテレーターを 1 つ（または n 個）戻したコピー</strong>を返します。

!!! tip "ポイント"
    - `std::prev(it, n)` は `it` を `n` 個戻したコピーを返す
    - `n` の既定は 1。元の `it` は変わらない
    - 双方向イテレーター以上で使える（前方向のみは不可）
    - 最後の要素は `*std::prev(c.end())`

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::prev {#prev}

<span class="ver ver-11">C++11</span>

```cpp
template <class It>
constexpr It prev(It it, typename std::iterator_traits<It>::difference_type n = 1);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | 双方向イテレーター | 出発点 |
| `n` | 整数 | 戻す数。既定は 1 |

元のイテレーターは変えず、`n` 個前のイテレーターを新しく返します。`std::forward_list` のように、後ろへ戻れないイテレーターには使えません。

範囲外に戻すと未定義動作です。空のコンテナで `prev(c.end())` を呼んではいけません。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {10, 20, 30};
  std::println("最後の要素: {}", *std::prev(v.end()));
  std::println("最後から 2 番目: {}", *std::prev(v.end(), 2));
}
```

```text title="実行結果"
最後の要素: 30
最後から 2 番目: 20
```

## ゲームでの使いどころ

末尾の要素を、イテレーターで取ります。

```cpp
if (!items.empty()) Use(*std::prev(items.end()));
```

`vector` なら `items.back()` のほうが簡単です。

## よくあるミス

??? failure "空のコンテナで呼んで未定義動作"
    `empty()` を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`next`](next.md) | 進める |
| [`advance`](advance.md) | 元のイテレーターを動かす |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::prev(it, n)` は `n` 個戻したコピー
    - [x] 双方向イテレーター以上
    - [x] 空のコンテナでは使わない

## 関連ページ

- [cpprefjp: std::prev](https://cpprefjp.github.io/reference/iterator/prev.html)
- [cppreference: std::prev](https://en.cppreference.com/w/cpp/iterator/prev)
