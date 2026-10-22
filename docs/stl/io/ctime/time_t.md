---
title: std::time_t
summary: "時刻（エポックからの秒数）を表す型。"
order: 900
tags:
  - 入出力・文字列
---

# std::time_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`std::time` が返す型で、基準時刻（普通は 1970-01-01 00:00:00 UTC）からの経過秒数を表します。実際の型（32 / 64 ビット）は処理系次第です。

!!! tip "ポイント"
    - 算術型（多くは 64 ビット整数）。
    - 差は `difftime` で求める。
    - 年月日に分けるには `gmtime` / `localtime`。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::time_t {#time_t}

```cpp
using time_t = /* 算術型（実装定義） */;
```

- 戻り値: なし（型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_arithmetic_v<std::time_t>);
  std::println("{}", std::time(nullptr) > 0);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータのタイムスタンプ | `std::time(nullptr)` |

## よくあるミス

??? failure "32 ビットの time_t"
    古い環境の 32 ビットは、2038 年に桁あふれします。64 ビットの環境を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time`](time.md) | 現在時刻を取る |
| [`difftime`](difftime.md) | 差を求める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エポックからの秒数の型
    - [x] 処理系ごとに違う
    - [x] difftime で差を取る

## 関連ページ

- [cpprefjp: std::time_t](https://cpprefjp.github.io/reference/ctime/time_t.html)
- [cppreference: std::time_t](https://en.cppreference.com/w/cpp/chrono/c/time_t)
