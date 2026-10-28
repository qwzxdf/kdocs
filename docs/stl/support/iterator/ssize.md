---
title: std::ssize
summary: "要素数を符号つきの整数で返す。"
order: 6
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::ssize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

コンテナの要素数は `size()` が返しますが、型が符号なし（`size_t`）です。`i < v.size() - 1` のような式は、空のコンテナで巨大な値になり、バグの元です。`std::ssize` は、<strong>符号つきの要素数</strong>を返します。

!!! tip "ポイント"
    - `std::ssize(c)` は符号つき整数で返す要素数
    - 空のコンテナでも、`ssize(c) - 1` が `-1` になる
    - `for (int i = 0; i < std::ssize(v); ++i)` が安全に書ける
    - 配列にも使える

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ssize {#ssize}

<span class="ver ver-20">C++20</span>

```cpp
template <class C>
constexpr auto ssize(const C& c) -> std::common_type_t<std::ptrdiff_t, std::make_signed_t<decltype(c.size())>>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナまたは配列 | 対象 |

戻り値は符号つき整数（通常 `std::ptrdiff_t`）です。`size()` を `int` に変換する手間も、符号の異なる比較の警告もなくなります。

`v.size() - 1` は、`v` が空のとき、符号なしの 0 − 1 で巨大な値になります。`std::ssize(v) - 1` なら `-1` です。逆順のループを書くときに特に有効です。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  const std::vector<int> empty;
  std::println("size()  - 1 = {}", empty.size() - 1);          // 符号なしで折り返す
  std::println("ssize() - 1 = {}", std::ssize(empty) - 1);     // -1
}
```

```text title="実行結果"
size()  - 1 = 18446744073709551615
ssize() - 1 = -1
```

## ゲームでの使いどころ

添字ループを安全に書きます。

```cpp
for (int i = std::ssize(items) - 1; i >= 0; --i) { /* 逆順に処理 */ }
```

## よくあるミス

??? failure "`size()` の符号なしを引き算に使って折り返す"
    `std::ssize` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`begin`](begin.md) | 先頭のイテレーター |
| [`empty`](empty.md) | 空か |

## コンパイラ対応

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ssize(c)` は符号つきの要素数
    - [x] 空のコンテナでも引き算が安全
    - [x] 配列にも使える

## 関連ページ

- [cpprefjp: std::ssize](https://cpprefjp.github.io/reference/iterator/ssize.html)
- [cppreference: std::ssize](https://en.cppreference.com/w/cpp/iterator/ssize)
