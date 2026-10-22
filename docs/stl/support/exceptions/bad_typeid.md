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

`typeid(*p)` で、仮想関数を持つクラスの実際の型を調べるとき、`p` が `nullptr` だと、`bad_typeid` が投げられます。ふつうの `nullptr` の参照は未定義動作ですが、この場合に限って例外になる、と決められています。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [例外](../../../basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。

## 関数の詳しい説明

### std::bad_typeid {#bad_typeid}

```cpp
class bad_typeid : public exception {
 public:
  const char* what() const noexcept override;
};
```

- 戻り値: `what()` はエラーを表す文字列
- 計算量: 定数


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
    std::println("{}", typeid(*p).name() != nullptr);
  } catch (const std::bad_typeid&) {
    std::println("bad_typeid");
  }
}
```

```text title="実行結果"
bad_typeid
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 実行時の型を調べる処理の安全確認 |

## よくあるミス

??? failure "非多態型で期待する"
    仮想関数を持たない型では、`typeid` は静的な型を返し、例外になりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`typeid`](../typeid.md) | 実行時の型 |
| [`bad_cast`](bad_cast.md) | `dynamic_cast` の失敗 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヌルの多態型ポインタに typeid を使ったときの例外
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::bad_typeid](https://cpprefjp.github.io/reference/typeinfo/bad_typeid.html)
- [cppreference: std::bad_typeid](https://en.cppreference.com/w/cpp/error/bad_typeid)
