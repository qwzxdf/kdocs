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

デストラクターの中で、「いま例外が飛んでいる最中か」を知りたいことがあります。正常に破棄されたときだけコミットし、例外で巻き戻されているときはロールバックしたい、といった処理です。`std::uncaught_exceptions()` は、<strong>いま処理中（まだ捕まっていない）の例外の数</strong>を返します。

!!! tip "ポイント"
    - 処理中の例外の数を返す
    - デストラクターで「例外による巻き戻し中か」が分かる
    - 正常終了なら 0、例外中なら 1 以上
    - 古い `uncaught_exception()` の代わり

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::uncaught_exceptions {#uncaught_exceptions}

<span class="ver ver-17">C++17</span>

```cpp
int uncaught_exceptions() noexcept;
```

例外が投げられて、`catch` に着くまでの間（スタックの巻き戻し中）は、1 以上を返します。通常の実行中は 0 です。

デストラクターの先頭で呼んで、作成時の値と比べると、「このオブジェクトの寿命の間に、新しい例外が投げられたか」が分かります。これにより、スコープ ガード（正常終了ならコミット、例外ならロールバック）が書けます。

古い `std::uncaught_exception()`（bool を返す）は、C++17 で非推奨になり、C++20 で削除されました。

## 実際に動かしてみる

```cpp
#include <exception>
#include <print>

struct Guard {
  ~Guard() { std::println("破棄時の例外の数: {}", std::uncaught_exceptions()); }
};

int main() {
  { Guard g; }                       // 正常に破棄される
  try {
    Guard g;
    throw 1;                         // 例外で巻き戻される
  } catch (int) {}
}
```

```text title="実行結果"
破棄時の例外の数: 0
破棄時の例外の数: 1
```

## ゲームでの使いどころ

スコープ ガードで、正常終了と例外を見分けます。

```cpp
class Transaction {
  int exceptions_ = std::uncaught_exceptions();
 public:
  ~Transaction() {
    if (std::uncaught_exceptions() == exceptions_) Commit();   // 例外なし
    else Rollback();
  }
};
```

## よくあるミス

??? failure "デストラクターから例外を投げる"
    デストラクターは `noexcept` のままにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`current_exception`](current_exception.md) | 処理中の例外を取る |
| [`terminate`](terminate.md) | 異常終了 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `uncaught_exceptions()` は処理中の例外の数
    - [x] スコープ ガードで、正常と例外を見分けられる
    - [x] 古い `uncaught_exception()` の後継

## 関連ページ

- [cpprefjp: std::uncaught_exceptions](https://cpprefjp.github.io/reference/exception/uncaught_exceptions.html)
- [cppreference: std::uncaught_exceptions](https://en.cppreference.com/w/cpp/error/uncaught_exceptions)
