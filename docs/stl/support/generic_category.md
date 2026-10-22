---
title: std::generic_category
summary: "OS に依存しない標準のエラー（`errc`）の分類を表す error_category を返す。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::generic_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`error_code` を作るとき、数値がどの分類に属するかを指定します。`generic_category()` は、OS に依存しない標準のエラー（`errc`）の分類の唯一の実体を返します。`name()` は `"generic"` です。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`std::error_code`](error_code.md) を先に読んでください。

## 関数の詳しい説明

### std::generic_category {#generic_category}

```cpp
const std::error_category& generic_category() noexcept;
```

- 戻り値: OS に依存しない標準のエラー（`errc`）の分類の `error_category` への参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  std::println("{}", std::generic_category().name());
}
```

```text title="実行結果"
generic
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | OS のエラーと標準のエラーを区別する |

## よくあるミス

??? failure "カテゴリの違うコードを `==` で比べる"
    数値が同じでも、分類が違えば別のエラーです。比べるときは `error_condition` に直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_category`](error_category.md) | 基底クラス |
| [`error_code`](error_code.md) | エラーコード |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] OS に依存しない標準のエラー（`errc`）の分類を表す error_category を返す
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::generic_category](https://cpprefjp.github.io/reference/exception/generic_category.html)
- [cppreference: std::generic_category](https://en.cppreference.com/w/cpp/error/generic_category)
