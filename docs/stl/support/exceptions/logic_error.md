---
title: std::logic_error
summary: "プログラムの論理の間違い（呼び出し側のミス）を表す例外。"
order: 5
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::logic_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <stdexcept>`
</div>

`std::logic_error` は、**プログラムの論理の間違い**（呼び出し方が悪い、前提条件を満たしていない）を表す例外の基底クラスです。`invalid_argument`、`out_of_range`、`length_error` などの親です。

!!! tip "ポイント"
    - 本来は「コードを直すべき」エラー。実行時エラーは `runtime_error`。
    - 派生クラスで細かく表す。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::logic_error {#logic_error}

```cpp
class logic_error : public exception;
```

- プログラムのミス（事前に確認すれば防げた失敗）を表す型の親です

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>

int main() {
  try {
    throw std::logic_error("初期化されていない");
  } catch (const std::logic_error& e) {
    std::println("{}", e.what());
  }
}
```

```text title="実行結果"
初期化されていない
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 前提条件が満たされていないことを伝える | `throw std::logic_error("not initialized");` |

## よくあるミス

??? failure "本来 assert で防ぐ間違いを例外にする"
    ゲームでは `assert` で十分なことが多いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`runtime_error`](runtime_error.md) | 実行時のエラー |
| [`exception`](exception.md) | 基底 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 論理の間違いの基底
    - [x] 派生クラスで細かく
    - [x] 実行時エラーは runtime_error

## 関連ページ

- [cpprefjp: std::logic_error](https://cpprefjp.github.io/reference/stdexcept/logic_error.html)
- [cppreference: std::logic_error](https://en.cppreference.com/w/cpp/error/logic_error)
