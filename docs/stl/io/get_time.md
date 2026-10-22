---
title: std::get_time
summary: "日時を、書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::get_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <sstream>`
</div>

`strptime` のような書式で、文字列から `tm` に読み込みます。

!!! tip "ポイント"
    - 書式は `strftime` と同じ。
    - 失敗するとストリームが `failbit` になる。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::get_time {#get_time}

```cpp
template <class CharT>
/* 実装定義 */ get_time(std::tm* tmb, const CharT* fmt);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tmb` | tm* | 結果を入れる変数 |
| `fmt` | 文字列 | 書式 |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <iomanip>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("12:30");
  std::tm t{};
  in >> std::get_time(&t, "%H:%M");
  std::println("{} {}", t.tm_hour, t.tm_min);
}
```

```text title="実行結果"
12 30
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "失敗を確かめない"
    書式に合わないと `failbit` が立ちます。`if (in)` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`put_time`](put_time.md) | 出力 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日時を、書式を指定して読み込む
    - [x] 書式は `strftime` と同じ
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::get_time](https://cpprefjp.github.io/reference/ios/get_time.html)
- [cppreference: std::get_time](https://en.cppreference.com/w/cpp/io/manip/get_time)
