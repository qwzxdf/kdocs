---
title: std::system_error
summary: "OS のエラー（error_code つき）を表す例外。"
order: 7
group: 標準の例外
tags:
  - 型・言語サポート
---

# std::system_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <system_error>`
</div>

`std::system_error` は、**OS やライブラリが返したエラー（`error_code`）を持つ例外**です。`std::thread` の作成失敗、`filesystem` の一部の関数などが投げます。`code()` で原因を調べられます。

!!! tip "ポイント"
    - `e.code()` が `std::error_code`。
    - `filesystem_error` はこの派生クラス。
    - 例外を使わない版では `error_code` を引数で受け取る。

!!! info "このページを読む前に"
    [標準の例外](../exceptions.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::system_error {#system_error}

```cpp
class system_error : public runtime_error {
 public:
  const std::error_code& code() const noexcept;
};
```

- OS が返したエラーコード付きの例外。filesystem の失敗（`filesystem_error`）はこれの子です

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  try {
    throw std::system_error(std::make_error_code(std::errc::permission_denied), "権限エラー");
  } catch (const std::system_error& e) {
    std::println("{}", e.code() == std::errc::permission_denied);
  }
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スレッドの作成失敗を調べる | `catch (const std::system_error& e)` |

## よくあるミス

??? failure "error_code の値を数値で比べる"
    OS ごとに値が違います。`std::errc` と比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`filesystem_error`](../../io/filesystem/filesystem_error.md) | 派生クラス |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] OS のエラーを持つ例外
    - [x] `code()` で原因
    - [x] 値は std::errc と比べる

## 関連ページ

- [cpprefjp: std::system_error](https://cpprefjp.github.io/reference/stdexcept/system_error.html)
- [cppreference: std::system_error](https://en.cppreference.com/w/cpp/error/system_error)
