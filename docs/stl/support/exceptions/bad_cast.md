---
title: std::bad_cast
summary: "参照の `dynamic_cast` が失敗したときの例外。"
order: 15
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::bad_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <typeinfo>`
</div>

標準ライブラリの機能は、前提が満たされないとき、例外を投げて失敗を伝えます。`std::bad_cast` は、<strong>`dynamic_cast` で参照への変換に失敗したことを表す例外</strong>。

!!! tip "ポイント"
    - 参照への `dynamic_cast` が失敗したときに投げられる
    - ポインターへの `dynamic_cast` は `nullptr` を返す（例外にならない）
    - `<typeinfo>` で宣言される
    - `dynamic_cast` を多用するなら、設計を見直す

!!! info "このページを読む前に"
    [エラー処理の設計](../../../design/foundations/error-handling.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bad_cast {#bad_cast}

```cpp
class bad_cast : public std::exception {
 public:
  const char* what() const noexcept override;
};
```

`dynamic_cast<T&>(obj)` で、`obj` の実際の型が `T` でないとき、投げられます。ポインターへの `dynamic_cast` は、失敗しても例外を投げず、`nullptr` を返します。参照にはヌルがないので、例外で失敗を伝えます。

ゲームで多くの `dynamic_cast` が必要になる場合は、設計を見直すサインです。仮想関数で振る舞いを分けるか、型の ID を持つ設計（コンポーネント）に変えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <typeinfo>

struct Base {
  virtual ~Base() = default;
};
struct Derived : Base {};

int main() {
  Base base;
  try {
    Derived& d = dynamic_cast<Derived&>(base);   // 実際は Base なので失敗
    (void)d;
  } catch (const std::bad_cast&) {
    std::println("bad_cast を捕まえた");
  }
}
```

```text title="実行結果"
bad_cast を捕まえた
```

## ゲームでの使いどころ

実際の型が分からない参照を派生クラスとして扱う場面で、失敗を検出します。

```cpp
try {
  auto& enemy = dynamic_cast<Enemy&>(entity);
} catch (const std::bad_cast&) { /* Enemy ではなかった */ }
```

ポインターを使えば、例外なしで同じ判定ができます（`if (auto* e = dynamic_cast<Enemy*>(&entity))`）。

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
    - [x] 参照への `dynamic_cast` が失敗したときに投げられる
    - [x] `what()` でメッセージを取れる（内容は実装で違う）
    - [x] `const` 参照で捕まえる

## 関連ページ

- [cpprefjp: std::bad_cast](https://cpprefjp.github.io/reference/typeinfo/bad_cast.html)
- [cppreference: std::bad_cast](https://en.cppreference.com/w/cpp/types/bad_cast)
