---
title: std::chrono_literals
summary: "16ms、2s のように、単位つきの時間を書けるリテラル。"
order: 8
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono_literals

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-14">C++14</span>
`#include <chrono>`
</div>

`std::chrono_literals` は、**`16ms`、`2s`、`1.5min` のように、数値の後ろに単位を付けて `duration` を書ける**リテラルです。`using namespace std::chrono_literals;` と書くと使えます。コードが読みやすくなり、単位の取り違えもなくなります。

!!! tip "ポイント"
    - `ns`（ナノ秒）、`us`（マイクロ秒）、`ms`（ミリ秒）、`s`（秒）、`min`（分）、`h`（時）が使える。
    - 整数リテラルは整数の `duration`（`2s` は `seconds`）、小数は `double` の `duration`（`1.5s`）。
    - 日付用に `y`（年）、`d`（日）もある（C++20）。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### ms, s, min, h など {#literals}

```cpp
namespace std::chrono_literals {
constexpr chrono::milliseconds operator""ms(unsigned long long);
constexpr chrono::duration<double, milli> operator""ms(long double);
// ns, us, ms, s, min, h も同じ形
}
```

- 戻り値: 対応する `duration`
- 計算量: コンパイル時

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono_literals;

  auto frame = 16ms;     // milliseconds
  auto timeout = 2s;     // seconds
  auto fine = 1.5s;      // duration<double>（小数の秒）

  std::println("{} {}", frame + timeout, fine);
}
```

```text title="実行結果"
2016ms 1.5s
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| クールダウン・待ち時間の指定 | `std::this_thread::sleep_for(100ms);` |
| フレーム予算（16ms） | `constexpr auto kFrameBudget = 16ms;` |

## よくあるミス

??? failure "using namespace を書き忘れる"
    `using namespace std::chrono_literals;` がないと、`16ms` が使えません。ヘッダーでなく、`.cpp` の関数の中などの狭い範囲に書きます。

??? failure "`min` が min 関数とぶつかる"
    `<algorithm>` の `std::min` は関数で、リテラルの `min` は数値の直後に付くので、ぶつかりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 本体 |
| [`std::string_literals`](../string_view.md) | 文字列のリテラル |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `16ms`、`2s` のように単位つきで書ける
    - [x] `using namespace std::chrono_literals;` が必要
    - [x] ヘッダーには書かない

## 関連ページ

- [cpprefjp: std::chrono_literals](https://cpprefjp.github.io/reference/chrono/duration/op_ms.html)
- [cppreference: std::literals::chrono_literals](https://en.cppreference.com/w/cpp/chrono/duration/operator%22%22ms)
