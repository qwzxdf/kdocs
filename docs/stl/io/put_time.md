---
title: std::put_time
summary: "日時（`tm`）を、書式を指定して出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::put_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <iostream>`
</div>

`strftime` のような書式（`%Y-%m-%d`）で、`tm` をストリームに出力します。バッファを用意せずに書けます。

!!! tip "ポイント"
    - 書式は `strftime` と同じ（`%Y` `%m` `%d` `%H` `%M` `%S`）。
    - `std::tm` を渡す。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::put_time {#put_time}

```cpp
template <class CharT>
/* 実装定義 */ put_time(const std::tm* tmb, const CharT* fmt);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tmb` | const tm* | 出力する日時 |
| `fmt` | 文字列 | 書式 |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <iomanip>
#include <iostream>

int main() {
  std::tm t{};
  t.tm_year = 124;  // 2024 年
  t.tm_mon = 0;
  t.tm_mday = 1;
  std::cout << std::put_time(&t, "%Y-%m-%d") << '\n';
}
```

```text title="実行結果"
2024-01-01
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "`tm_year` を西暦で入れる"
    `tm_year` は 1900 からの経過年です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_time`](get_time.md) | 入力 |
| [`strftime`](ctime/strftime.md) | バッファに書き込む版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日時（`tm`）を、書式を指定して出力する
    - [x] 書式は `strftime` と同じ（`%Y` `%m` `%d` `%H` `%M` `%S`）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::put_time](https://cpprefjp.github.io/reference/ios/put_time.html)
- [cppreference: std::put_time](https://en.cppreference.com/w/cpp/io/manip/put_time)
