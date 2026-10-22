---
title: std::error_category
summary: "エラーコードの種類（分類）を表す基底クラス。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::error_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`error_code` の数値は、それだけでは意味が決まりません。`2` はファイルシステムでは「ファイルがない」、自作のゲームでは別の意味かもしれません。数値の意味を決めるのが `error_category` で、自分のエラーの種類を足したいときは、この基底クラスを継承して作ります。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`std::error_code`](error_code.md) を先に読んでください。

## 関数の詳しい説明

### std::error_category {#error_category}

```cpp
class error_category {
 public:
  virtual const char* name() const noexcept = 0;
  virtual std::string message(int condition) const = 0;
  virtual bool equivalent(const error_code& code, int condition) const noexcept;
  // ...
};
```

- 戻り値: `name()` は分類の名前、`message(c)` は説明
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <system_error>

struct GameCategory : std::error_category {
  const char* name() const noexcept override { return "game"; }
  std::string message(int c) const override { return c == 1 ? "out of mana" : "unknown"; }
};
const GameCategory& Game() {
  static GameCategory c;
  return c;
}

int main() {
  std::error_code ec(1, Game());
  std::println("{}: {}", ec.category().name(), ec.message());
}
```

```text title="実行結果"
game: out of mana
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ゲーム固有のエラーコードに名前をつける |

## よくあるミス

??? failure "カテゴリを関数ごとに作る"
    カテゴリは**1 つの実体**（グローバルに 1 つ）である必要があります。`static` の関数内変数で返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_code`](error_code.md) | エラーコード |
| [`generic_category`](generic_category.md) | 標準の分類 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エラーコードの種類（分類）を表す基底クラス
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::error_category](https://cpprefjp.github.io/reference/exception/error_category.html)
- [cppreference: std::error_category](https://en.cppreference.com/w/cpp/error/error_category)
