---
title: std::iscntrl
summary: "制御文字かを調べる。"
order: 900
tags:
  - 数値
---

# std::iscntrl

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cctype>`
</div>

`<cctype>` の判定関数のひとつです。改行やタブのような、画面に表示されない制御文字かを判定します。戻り値は真偽ではなく `int` で、真なら 0 以外が返ります。

!!! tip "ポイント"
    - 戻り値は `int`（真なら 0 以外）。
    - 引数は `unsigned char` の範囲か `EOF`。`char` が負のときは `unsigned char` に直して渡す。
    - ASCII 以外の文字（日本語）には使えない。

!!! info "このページを読む前に"
    [`std::isalpha`](isalpha.md) を先に読んでください。

## 関数の詳しい説明

### std::iscntrl {#iscntrl}

```cpp
int iscntrl(int ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | int | 調べる文字（`unsigned char` の値か `EOF`） |

- 戻り値: 条件に合えば 0 以外、合わなければ 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cctype>
#include <print>

int main() {
  std::println("{} {}", std::iscntrl('\n') != 0, std::iscntrl('a') != 0);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 入力文字の検査 |

## よくあるミス

??? failure "負の `char` をそのまま渡す"
    `char` が符号付きの環境で、非 ASCII の文字は負の値になります。`static_cast<unsigned char>(c)` に直して渡さないと、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isalpha`](isalpha.md) | 英字か |
| [`isdigit`](isdigit.md) | 数字か |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 制御文字かを調べる
    - [x] 戻り値は `int`（真なら 0 以外）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::iscntrl](https://cpprefjp.github.io/reference/cctype/iscntrl.html)
- [cppreference: std::iscntrl](https://en.cppreference.com/w/cpp/string/byte/iscntrl)
