---
title: std::make_error_condition
summary: "errc などの列挙値から、error_condition を作る。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::make_error_condition

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`error_condition` は、OS に依存しない、移植性のあるエラーの条件です。`error_code`（OS 固有の値）と比べるときに使い、`ec == make_error_condition(errc::...)` の形で、エラーの種類を判定できます。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`std::error_code`](error_code.md) を先に読んでください。

## 関数の詳しい説明

### std::make_error_condition {#make_error_condition}

```cpp
std::error_condition make_error_condition(std::errc e) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | errc | 標準のエラーの列挙値 |

- 戻り値: 対応する `error_condition`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  std::error_code ec = std::make_error_code(std::errc::invalid_argument);
  std::error_condition c = std::make_error_condition(std::errc::invalid_argument);
  std::println("{}", ec == c);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | OS が違っても同じ書き方でエラーを判定する |

## よくあるミス

??? failure "`error_code` と `error_condition` を混同する"
    `error_code` は具体的な値、`error_condition` は移植性のある意味です。比較は条件に対して行います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_error_code`](make_error_code.md) | コードを作る |
| [`error_condition`](error_condition.md) | エラー条件 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] errc などの列挙値から、error_condition を作る
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_error_condition](https://cpprefjp.github.io/reference/exception/make_error_condition.html)
- [cppreference: std::make_error_condition](https://en.cppreference.com/w/cpp/error/make_error_condition)
