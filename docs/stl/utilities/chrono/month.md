---
title: std::chrono::month
summary: "月（1〜12）を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::month

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

月を `int` で持つと、`13` のような範囲外の値や、`0` から数えるのか `1` から数えるのかの混乱が起こります。`std::chrono::month` は、1〜12 の月を型で表し、`January` ... `December` の定数も用意されています。

!!! tip "ポイント"
    - `month{3}` または `std::chrono::March` で作る。
    - `month + months{n}` で、12 を超えると 1 に戻る（巡回する）。
    - `ok()` で 1〜12 の範囲か調べる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month {#month}

```cpp
class month {
 public:
  constexpr explicit month(unsigned m) noexcept;
  constexpr explicit operator unsigned() const noexcept;
  constexpr bool ok() const noexcept;
};
inline constexpr month January{1}, February{2} /* ... */, December{12};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `m` | unsigned | 月（1〜12 が有効） |

- 戻り値: `ok()` は 1〜12 なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  std::println("{}", unsigned(March));
  std::println("{}", unsigned(March + months{11}));
  std::println("{}", month{13}.ok());
}
```

```text title="実行結果"
3
2
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| シーズンイベントの月の判定 | `month == std::chrono::December` |

## よくあるミス

??? failure "0 始まりだと思う"
    `month` は 1 始まりです（`January` は 1）。配列の添字に使うときは `unsigned(m) - 1` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`day`](day.md) | 日 |
| [`year`](year.md) | 年 |
| [`year_month`](year_month.md) | 年と月 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 月（1〜12）の型
    - [x] 定数 January … December
    - [x] 足し算は巡回する

## 関連ページ

- [cpprefjp: std::chrono::month](https://cpprefjp.github.io/reference/chrono/month.html)
- [cppreference: std::chrono::month](https://en.cppreference.com/w/cpp/chrono/month)
