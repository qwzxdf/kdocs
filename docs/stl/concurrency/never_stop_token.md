---
title: std::never_stop_token
summary: "停止が絶対に要求されない stop_token。"
order: 900
tags:
  - 並行処理
---

# std::never_stop_token

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <stop_token>`
</div>

停止の機能を持つ関数でも、停止させる必要がない呼び出し元もあります。そのとき、本物の `stop_source` を作る代わりに、`never_stop_token` を渡すと、停止の確認が常に `false` になり、コストもかかりません。

!!! tip "ポイント"
    - `stop_possible()` と `stop_requested()` が常に `false`。
    - ジェネリックな関数で、停止が不要な場合の型として使う。
    - C++26 の機能。

!!! info "このページを読む前に"
    [並行処理の基本](../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::never_stop_token {#never_stop_token}

```cpp
class never_stop_token {
 public:
  static constexpr bool stop_requested() noexcept { return false; }
  static constexpr bool stop_possible() noexcept { return false; }
};
```

- 戻り値: なし
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <stop_token>

int main() {
  std::never_stop_token t;
  std::println("{}", t.stop_possible());
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 停止不要の呼び出し | `Run(std::never_stop_token{})` |

## よくあるミス

??? failure "停止できると期待する"
    停止が要求されることはありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stop_token`](stop_token.md) | 実際の stop_token |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 絶対に止まらない stop_token
    - [x] 常に false
    - [x] C++26

## 関連ページ

- [cpprefjp: std::never_stop_token](https://cpprefjp.github.io/reference/stop_token/never_stop_token.html)
- [cppreference: std::never_stop_token](https://en.cppreference.com/w/cpp/thread/never_stop_token)
