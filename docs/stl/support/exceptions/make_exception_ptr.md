---
title: std::make_exception_ptr
summary: "例外オブジェクトから、exception_ptr を作る。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::make_exception_ptr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <exception>`
</div>

`throw` せずに、例外オブジェクトを `exception_ptr` に包みたいことがあります（`promise::set_exception` に渡すときなど）。`make_exception_ptr(e)` が、`throw` と `catch` を省いて作ってくれます。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::make_exception_ptr {#make_exception_ptr}

```cpp
template <class E>
std::exception_ptr make_exception_ptr(E e) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | 例外 | 包む例外オブジェクト |

- 戻り値: 包んだ `exception_ptr`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>
#include <stdexcept>

int main() {
  std::exception_ptr p = std::make_exception_ptr(std::runtime_error("boom"));
  try {
    std::rethrow_exception(p);
  } catch (const std::exception& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
boom
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `promise` にエラーを入れる |

## よくあるミス

??? failure "例外の型が切り落とされる"
    値渡しで受けるので、派生クラスを渡すなら、そのままの型で渡します。基底型の変数に入れると切り落とされます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rethrow_exception`](rethrow_exception.md) | 投げ直す |
| [`current_exception`](current_exception.md) | 処理中の例外を取る |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 例外オブジェクトから、exception_ptr を作る
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_exception_ptr](https://cpprefjp.github.io/reference/exception/make_exception_ptr.html)
- [cppreference: std::make_exception_ptr](https://en.cppreference.com/w/cpp/error/make_exception_ptr)
