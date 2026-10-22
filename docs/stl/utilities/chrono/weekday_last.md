---
title: std::chrono::weekday_last
summary: "「最後の曜日」を表す型（最終金曜日など）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::weekday_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「毎月最後の金曜日」のように、月ごとに日付が変わる指定には、`weekday_last` が使えます。`Friday[last]` と書いて作ります。

!!! tip "ポイント"
    - `weekday[std::chrono::last]` で作る。
    - `year/month/weekday[last]` で日付の指定になる。
    - 月ごとに 4 週か 5 週かを気にしなくてよい。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::weekday_last {#weekday_last}

```cpp
class weekday_last {
 public:
  constexpr std::chrono::weekday weekday() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `w` | weekday | 曜日 |

- 戻り値: `weekday()` は元の曜日
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto wl = Friday[last];
  std::println("{}", wl.weekday().c_encoding());
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 月末の金曜日にボーナスを配る | `2024y / March / Friday[last]` |

## よくあるミス

??? failure "last をつけ忘れる"
    `Friday[5]` と書くと「第 5 金曜」で、無い月もあります。「最後」は必ず `last` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weekday_indexed`](weekday_indexed.md) | 第 n 曜日 |
| [`last_spec`](last_spec.md) | `last` の型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最後の曜日
    - [x] weekday[last] で作る
    - [x] 月によって日付が変わる

## 関連ページ

- [cpprefjp: std::chrono::weekday_last](https://cpprefjp.github.io/reference/chrono/weekday_last.html)
- [cppreference: std::chrono::weekday_last](https://en.cppreference.com/w/cpp/chrono/weekday_last)
