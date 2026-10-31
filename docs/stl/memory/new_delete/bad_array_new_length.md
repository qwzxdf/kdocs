---
title: std::bad_array_new_length
summary: "配列の new で、要素数が不正だったときの例外。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::bad_array_new_length

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <new>`
</div>

`new int[n]` の `n` が負だったり、確保できないほど巨大だったりすると、`std::bad_alloc` より具体的な `std::bad_array_new_length` が投げられます。`bad_alloc` の派生クラスなので、`catch (const std::bad_alloc&)` でも捕まえられます。

!!! tip "ポイント"
    - 配列の長さが負、または大きすぎるときに、`new[]` が投げる
    - `std::bad_alloc` の派生クラス
    - 長さが妥当でも、メモリが足りなければ、普通の `bad_alloc`
    - `nothrow` 版では例外ではなく `nullptr`

!!! info "このページを読む前に"
    [`operator new`](operator_new.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_array_new_length {#bad_array_new_length}

```cpp
class bad_array_new_length : public std::bad_alloc {
 public:
  const char* what() const noexcept override;
};
```

C++11 で追加されました。投げられるのは、次の場合です。

- 長さが負（`int n = -1; new int[n];`）
- 長さに要素の大きさをかけると、`size_t` の範囲を超える
- 初期化子の数が、配列の長さを超える

長さの検査は、確保の前に行われます。そのため、メモリの空きとは関係なく、不正な長さなら、必ず投げられます。

負の数が入る原因は、符号つき整数の計算ミスが多いです。`std::vector<int> v(n)` も、`n` が不正なら `std::length_error` を投げます。

## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  volatile int n = -1;  // 実行時に決まる負の長さ
  try {
    int* p = new int[n];
    delete[] p;
  } catch (const std::bad_array_new_length&) {
    std::println("bad_array_new_length");
  }

  // bad_alloc でも捕まえられる
  try {
    int* p = new int[n];
    delete[] p;
  } catch (const std::bad_alloc&) {
    std::println("bad_alloc としても捕まえられる");
  }
}
```

```text title="実行結果"
bad_array_new_length
bad_alloc としても捕まえられる
```

## ゲームでの使いどころ

外から読んだ値で配列を確保する処理で、不正な長さを、例外として検出します。長さは先に検査するほうが確実です。

## よくあるミス

??? failure "符号つきの計算ミスで負にする"
    `size_t` の引き算で巻き戻る、`int` の差が負になる、といった原因が多いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nothrow`](nothrow.md) | 例外の代わりに `nullptr` |
| `std::length_error` | 標準コンテナが長さの不正で投げる |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::bad_array_new_length](https://cpprefjp.github.io/reference/new/bad_array_new_length.html)
- [cppreference: std::bad_array_new_length](https://en.cppreference.com/w/cpp/error/bad_array_new_length)
