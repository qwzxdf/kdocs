---
title: std::data
summary: "先頭の要素へのポインターを返す（配列にも使える）。"
order: 8
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::data

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::data(c)` は、**連続したメモリの先頭へのポインター**を返す関数です。`c.data()` と同じですが、生の配列にも使えます。C のAPI にバッファを渡すときなどに使います。

!!! tip "ポイント"
    - `std::vector` や `std::string` の `data()` と同じ。
    - 生の配列では、配列そのものの先頭。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::data {#data}

```cpp
template <class C>
constexpr auto data(C& c) -> decltype(c.data());
```

- 先頭のポインタ。C の配列にも使えます

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  const int* p = std::data(v);
  std::println("{} {}", p == v.data(), p[1]);
}
```

```text title="実行結果"
true 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のAPI に配列を渡す | `Fill(std::data(buf), std::size(buf))` |

## よくあるミス

??? failure "空のコンテナの data を読む"
    ポインターは有効でも、読める要素がありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`size`](size.md) | 要素数 |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭のポインター
    - [x] 配列にも使える
    - [x] C の API 連携に

## 関連ページ

- [cpprefjp: std::data](https://cpprefjp.github.io/reference/iterator/data.html)
- [cppreference: std::data](https://en.cppreference.com/w/cpp/iterator/data)
