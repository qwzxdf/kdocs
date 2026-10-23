---
title: std::size_t
summary: "大きさや個数を表す、符号なしの整数型。"
order: 21
group: 基本の型（<cstddef>）
tags:
  - 型・言語サポート
---

# std::size_t

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstddef>`
</div>

`std::size_t` は、**メモリ上の大きさや、要素の個数を表す、符号なしの整数型**です。`sizeof` の結果、`vector::size()` の戻り値がこの型です。64 ビット環境では 8 バイト（64 ビット）です。符号なしなので、引き算で 0 を下回ると巨大な値になる事故に注意します。

!!! tip "ポイント"
    - `sizeof(型)` の結果、配列の添字、`size()` の戻り値は `size_t`。
    - 符号なし。`size() - 1` は 0 個のとき巨大な値になる。
    - 符号つきが欲しいときは [`std::ptrdiff_t`](ptrdiff_t.md)（や `ssize`）。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::size_t {#size_t}

```cpp
using size_t = /* 符号なし整数 */;
```

- 戻り値: （型）
- 計算量: O(1)

```cpp
#include <cstddef>
#include <print>
#include <vector>

int main() {
  std::vector<int> v;
  std::size_t n = v.size();
  std::println("{} {}", sizeof(std::size_t), n - 1 > 1000);  // 空の size() - 1 は巨大な値
}
```

```text title="実行結果"
8 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| メモリの大きさ・配列の添字 | `std::size_t index = 0;` |

## よくあるミス

??? failure "size() - 1 の事故"
    要素が 0 個のとき、`v.size() - 1` は巨大な値です。条件を足し算に直すか、`ssize` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ptrdiff_t`](ptrdiff_t.md) | 符号つき |
| [`std::ssize`](iterator/ssize.md) | 符号つきの要素数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きさ・個数を表す
    - [x] 符号なし
    - [x] 引き算の事故に注意

## 関連ページ

- [cpprefjp: std::size_t](https://cpprefjp.github.io/reference/cstddef/size_t.html)
- [cppreference: std::size_t](https://en.cppreference.com/w/cpp/types/size_t)
