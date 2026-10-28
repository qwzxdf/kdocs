---
title: std::strftime
summary: "日時を、書式に従った文字列にする（C 由来）。"
order: 3
group: 時刻（<ctime>）
tags:
  - 入出力・文字列
---

# std::strftime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ctime>`
</div>

`std::strftime` は、**日時（`tm` 構造体）を `%Y-%m-%d` のような書式に従った文字列にする**C 由来の関数です。ログのタイムスタンプ、ファイル名に日付を入れる、といった用途に使います。C++20 以降は `std::format("{:%F}", ...)` が簡単です。

!!! tip "ポイント"
    - `%Y` 年、`%m` 月、`%d` 日、`%H` 時、`%M` 分、`%S` 秒。
    - 書き込み先のバッファの大きさを渡す。足りないと 0 を返す。
    - C++20 では `std::format` で日時を書式化できる。

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::strftime {#strftime}

```cpp
std::size_t strftime(char* buffer, std::size_t size, const char* format, const std::tm* t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 書き込み先 |
| `size` | `size_t` | バッファの大きさ |
| `format` | `const char*` | 書式（`%Y-%m-%d` など） |
| `t` | `const tm*` | 日時 |

- 戻り値: 書き込んだ文字数（足りなければ 0）
- 計算量: O(1)

```cpp
#include <ctime>
#include <print>

int main() {
  std::tm t{};
  t.tm_year = 126;   // 1900 年からの年数: 2026
  t.tm_mon = 9;      // 月は 0 始まり: 10 月
  t.tm_mday = 21;

  char buffer[32];
  std::strftime(buffer, sizeof(buffer), "%Y-%m-%d", &t);
  std::println("{}", buffer);
}
```

```text title="実行結果"
2026-10-21
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータのファイル名に日付を入れる | `std::strftime(name, sizeof(name), "save_%Y%m%d", &t)` |

## よくあるミス

??? failure "tm_year と tm_mon の基準を間違える"
    `tm_year` は 1900 年からの年数、`tm_mon` は 0〜11 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::chrono::year_month_day`](../../utilities/chrono/year_month_day.md) | C++20 の日付 |
| [`std::format`](../../utilities/format.md) | `{:%F}` で日時を書式化 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日時を書式の文字列にする
    - [x] `tm_year` は 1900 年から
    - [x] バッファの大きさを守る

## 関連ページ

- [cpprefjp: std::strftime](https://cpprefjp.github.io/reference/ctime/strftime.html)
- [cppreference: std::strftime](https://en.cppreference.com/w/cpp/chrono/c/strftime)
