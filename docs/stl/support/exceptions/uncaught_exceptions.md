---
title: std::uncaught_exceptions
summary: "いま処理中（スタックを巻き戻している最中）の例外の数を返す。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::uncaught_exceptions

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <exception>`
</div>

デストラクタの中で、「例外のせいで呼ばれたのか、普通に抜けたのか」を知りたいことがあります（スコープガードが、失敗したときだけ後始末をする場合など）。`uncaught_exceptions()` が、いま巻き戻している最中の例外の数を返します。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::uncaught_exceptions {#uncaught_exceptions}

```cpp
int uncaught_exceptions() noexcept;
```

- 戻り値: 処理中の例外の数
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <exception>
#include <print>

struct Guard {
  ~Guard() { std::println("{}", std::uncaught_exceptions()); }
};

int main() {
  {
    Guard g;
  }
  try {
    Guard g;
    throw 1;
  } catch (...) {
  }
}
```

```text title="実行結果"
0
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | スコープガードで、成功と失敗を区別する |

## よくあるミス

??? failure "`uncaught_exception()`（単数）を使う"
    古い `uncaught_exception()` は C++17 で削除されました。数を返す版を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception_ptr`](exception_ptr.md) | 例外を持ち歩く |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] いま処理中（スタックを巻き戻している最中）の例外の数を返す
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::uncaught_exceptions](https://cpprefjp.github.io/reference/exception/uncaught_exceptions.html)
- [cppreference: std::uncaught_exceptions](https://en.cppreference.com/w/cpp/error/uncaught_exceptions)
