---
title: std::to_address
summary: "ポインターやイテレータ（スマートポインターなど）から、生のポインターを取る。"
order: 22
tags:
  - メモリ
---

# std::to_address

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

`std::to_address(p)` は、**ポインターのようなもの（スマートポインター、`vector` のイテレータ）から、生のポインターを取る**関数です。イテレータ `it` を `&*it` と書くと、`end()` では未定義動作になりますが、`to_address` なら安全です。

!!! tip "ポイント"
    - `&*it` は、`end()` で未定義動作。`to_address` はOK。
    - 連続したメモリのイテレータ（`vector`、`string`、`array`）に使える。
    - スマートポインターの `.get()` と同じ目的。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [所有権（誰が消すのか）](../../basics/ownership.md)（所有権の考え方）

## 関数の詳しい説明

### std::to_address {#to_address}

```cpp
template <class Ptr>
constexpr auto to_address(const Ptr& p) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | ポインター風のもの | 生のポインターに直したいもの |

- 戻り値: 生のポインター
- 計算量: O(1)

```cpp
#include <memory>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  int* first = std::to_address(v.begin());
  int* last = std::to_address(v.end());   // &*v.end() は未定義動作だが、これは安全
  std::println("{} {}", first == v.data(), last - first);
}
```

```text title="実行結果"
true 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のAPI に、イテレータが指す連続領域を渡す | `Fill(std::to_address(v.begin()), v.size())` |

## よくあるミス

??? failure "連続しないメモリのイテレータ"
    `list` のイテレータには使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`addressof`](../utilities/addressof.md) | オブジェクトのアドレス |
| [`std::data`](../support/iterator/data.md) | 配列・コンテナの先頭 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ポインター風のものから生ポインターを取る
    - [x] `&*it` より安全
    - [x] 連続メモリのイテレータに

## 関連ページ

- [cpprefjp: std::to_address](https://cpprefjp.github.io/reference/memory/to_address.html)
- [cppreference: std::to_address](https://en.cppreference.com/w/cpp/memory/to_address)
