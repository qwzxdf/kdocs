---
title: std::ios_base::failure
summary: "ストリームのエラーで投げられる例外クラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::ios_base::failure

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ios>`
</div>

ストリームは、エラーが起きても、既定では例外を投げず、状態（`failbit` など）だけを立てます。`exceptions()` で例外を有効にすると、エラーのときに `std::ios_base::failure` が投げられます。`std::system_error` の派生クラスで、`code()` でエラーコードを取れます。

!!! tip "ポイント"
    - `exceptions(std::ios::failbit | std::ios::badbit)` で有効にする。
    - `std::system_error` から派生。
    - 既定では投げられない。

!!! info "このページを読む前に"
    [`std::basic_ios`](basic_ios.md) を先に読んでください。

## 関数の詳しい説明

### std::ios_base::failure {#ios_base_failure}

```cpp
class ios_base::failure : public system_error {
 public:
  explicit failure(const std::string& message, const std::error_code& ec = std::io_errc::stream);
};
```

- 戻り値: `what()` と `code()` を持つ
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <fstream>
#include <ios>
#include <print>

int main() {
  std::ifstream in;
  in.exceptions(std::ios::failbit);
  try {
    in.open("not_exist_kdocs.txt");
  } catch (const std::ios_base::failure&) {
    std::println("開けなかった");
  }
}
```

```text title="実行結果"
開けなかった
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルを開けなかったら例外にする | `file.exceptions(std::ios::failbit);` |

## よくあるミス

??? failure "既定で例外が出ると思う"
    既定では、状態を確かめる必要があります。例外にするには、`exceptions()` を設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_ios`](basic_ios.md) | 状態の確認 |
| [`system_error`](../support/exceptions/system_error.md) | 親のクラス |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームの例外
    - [x] exceptions() で有効にする
    - [x] system_error の派生

## 関連ページ

- [cpprefjp: std::ios_base::failure](https://cpprefjp.github.io/reference/ios/ios_base/failure.html)
- [cppreference: std::ios_base::failure](https://en.cppreference.com/w/cpp/io/ios_base/failure)
