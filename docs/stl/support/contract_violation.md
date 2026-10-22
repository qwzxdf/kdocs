---
title: std::contracts::contract_violation
summary: "契約（事前条件・事後条件）の違反の情報を表す型。"
order: 900
tags:
  - 型・言語サポート
---

# std::contracts::contract_violation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <contracts>`
</div>

C++26 の契約（`pre`・`post`・`contract_assert`）が破られたとき、違反の内容（どの条件か、どこか）を知らせるのが `contract_violation` です。違反ハンドラ（`handle_contract_violation`）の引数として渡されます。

!!! tip "ポイント"
    - 違反ハンドラの引数として受け取る。
    - `comment()` で条件の文字列、`location()` で場所を取る。
    - C++26 の機能。

!!! info "このページを読む前に"
    [`std::source_location`](source_location.md) を先に読んでください。

## 関数の詳しい説明

### std::contracts::contract_violation {#contract_violation}

```cpp
namespace std::contracts {
class contract_violation {
 public:
  const char* comment() const noexcept;
  std::source_location location() const noexcept;
  // ...
};
}
```

- 戻り値: 違反の条件の文字列・場所など
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <contracts>
#include <print>

// 契約違反のハンドラ（実装がリンク時に探す）
void handle_contract_violation(const std::contracts::contract_violation& v) {
  std::println("契約違反: {}", v.comment());
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 違反をログに出すハンドラ | `void handle_contract_violation(const std::contracts::contract_violation& v);` |

## よくあるミス

??? failure "自分で作る"
    ライブラリが作って渡す型です。自分でインスタンスを作ることはありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`source_location`](source_location.md) | 場所を表す型 |

## コンパイラ対応

C++26 の機能です。対応は新しいコンパイラに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 契約違反の情報
    - [x] ハンドラの引数
    - [x] C++26

## 関連ページ

- [cpprefjp: std::contracts::contract_violation](https://cpprefjp.github.io/reference/contracts/contract_violation.html)
- [cppreference: std::contracts::contract_violation](https://en.cppreference.com/w/cpp/utility/contract_violation)
