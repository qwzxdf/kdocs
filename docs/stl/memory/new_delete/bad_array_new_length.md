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

`new int[n]` で、`n` が負だったり、確保できる上限を超えていたりすると、`bad_alloc` の派生の `bad_array_new_length` が投げられます。メモリ不足の `bad_alloc` と区別して、要素数のミスを知らせます。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`new[]` と `delete[]`](new_array.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_array_new_length {#bad_array_new_length}

```cpp
class bad_array_new_length : public bad_alloc {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: `what()` はエラーを表す文字列
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <new>
#include <print>

int main() {
  volatile int n = -1;
  try {
    int* p = new int[n];
    delete[] p;
  } catch (const std::bad_array_new_length&) {
    std::println("bad length");
  }
}
```

```text title="実行結果"
bad length
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 外から読み込んだ要素数で配列を確保する前の保険 |

## よくあるミス

??? failure "要素数を検査せずに使う"
    ファイルから読んだ数でそのまま `new[]` せず、範囲を確かめてから確保します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bad_alloc`](../../support/exceptions/bad_alloc.md) | メモリ不足 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 配列の new で、要素数が不正だったときの例外
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::bad_array_new_length](https://cpprefjp.github.io/reference/new/bad_array_new_length.html)
- [cppreference: std::bad_array_new_length](https://en.cppreference.com/w/cpp/error/bad_array_new_length)
