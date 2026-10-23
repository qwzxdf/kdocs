---
title: std::bad_typeid
summary: "ヌルの多態型ポインタに typeid を使ったときの例外。"
order: 900
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_typeid

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <typeinfo>`
</div>

標準ライブラリの機能は、前提が満たされないとき、例外を投げて失敗を伝えます。`std::bad_typeid` は、<strong>ヌルポインターを `typeid` したことを表す例外</strong>。

!!! tip "ポイント"
    - 多態的な型の `typeid(*p)` で `p` が `nullptr` のときに投げられる
    - `<typeinfo>` で宣言される
    - ヌルでない確認があれば、起こらない
    - ゲームでの出番はほとんどない

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_typeid {#bad_typeid}

```cpp
class bad_typeid : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

多態的な型（仮想関数を持つクラス）のポインターを `typeid(*p)` と参照するとき、`p` が `nullptr` だと投げられます。

`typeid` の引数にヌルのポインターを渡す間違いに、例外で気づける、という意味です。ゲームでは、ほとんど出会いません。

## 実際に動かしてみる

```cpp
#include <print>
#include <typeinfo>

struct Base {
  virtual ~Base() = default;
};

int main() {
  Base* p = nullptr;
  try {
    const auto& t = typeid(*p);       // ヌルを参照して typeid
    (void)t;
  } catch (const std::bad_typeid&) {
    std::println("bad_typeid を捕まえた");
  }
}
```

```text title="実行結果"
bad_typeid を捕まえた
```

## ゲームでの使いどころ

ヌルの確認を忘れたバグの検出に使えますが、実際には、ヌルの確認を先に書くほうが確実です。

## よくあるミス

??? failure "捕まえずに放置して、プログラムが終了する"
    例外を投げうる機能を使うときは、`try` / `catch` で受けるか、事前に条件を確かめます。

??? failure "`catch (std::exception)` と値で捕まえる"
    `const` 参照で捕まえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exception`](exception.md) | すべての標準例外の基底 |

## コンパイラ対応

C++98 から使えます。`<typeinfo>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 多態的な型の `typeid(*p)` で `p` が `nullptr` のときに投げられる
    - [x] `what()` でメッセージを取れる（内容は実装で違う）
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::bad_typeid](https://cpprefjp.github.io/reference/typeinfo/bad_typeid.html)
- [cppreference: std::bad_typeid](https://en.cppreference.com/w/cpp/error/bad_typeid)
