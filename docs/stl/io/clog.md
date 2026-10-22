---
title: std::clog
summary: "標準のログ出力（cerr と同じ出力先で、バッファあり）。"
order: 900
tags:
  - 入出力・文字列
---

# std::clog

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::clog` は、`cerr` と同じ標準エラー出力に出しますが、**バッファにためてから**出します。1 回ごとにすぐ出す `cerr` よりも速いので、大量のログを出すときに向きます。代わりに、クラッシュの直前のログが出ずに失われることがあります。

!!! tip "ポイント"
    - `cerr` の仲間。
    - 出力先は `cerr` と同じ。
    - ゲームでは `std::println` やログライブラリを使うことが多い。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::clog {#clog}

```cpp
extern std::ostream clog;
```

- 戻り値: `ostream`
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::clog << "log: start\n";
}
```

```text title="実行結果"
log: start
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログ・エラーの出力 | `std::clog << ...;` |

## よくあるミス

??? failure "クラッシュ時のログを期待する"
    バッファにためるので、クラッシュ直前のログが失われることがあります。確実に残したいログは `cerr` か、`flush` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cerr`](cerr.md) | バッファなしの標準エラー出力 |
| [`std::println`](../utilities/print.md) | 新しい書き方 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準のログ出力（cerr と同じ出力先で、バッファあり）
    - [x] cerr の仲間
    - [x] バッファあり

## 関連ページ

- [cpprefjp: std::clog](https://cpprefjp.github.io/reference/iostream/clog.html)
- [cppreference: std::clog](https://en.cppreference.com/w/cpp/io/clog)
