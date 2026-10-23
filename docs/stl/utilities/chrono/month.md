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

### std::chrono::January <span class="ver ver-20">C++20</span> {#January data-toc-label="std::chrono::January"}

```cpp
inline constexpr std::chrono::month January{1};
```

- 戻り値: 1 月を表す定数
- 計算量: 定数

`std::chrono::January` は、1 月（`month{1}`）を表す定数です。`2024y / January / 1` のように、日付を組み立てるときに使います。

### std::chrono::February <span class="ver ver-20">C++20</span> {#February data-toc-label="std::chrono::February"}

```cpp
inline constexpr std::chrono::month February{2};
```

- 戻り値: 2 月を表す定数
- 計算量: 定数

`std::chrono::February` は、2 月（`month{2}`）を表す定数です。`2024y / February / 1` のように、日付を組み立てるときに使います。

### std::chrono::March <span class="ver ver-20">C++20</span> {#March data-toc-label="std::chrono::March"}

```cpp
inline constexpr std::chrono::month March{3};
```

- 戻り値: 3 月を表す定数
- 計算量: 定数

`std::chrono::March` は、3 月（`month{3}`）を表す定数です。`2024y / March / 1` のように、日付を組み立てるときに使います。

### std::chrono::April <span class="ver ver-20">C++20</span> {#April data-toc-label="std::chrono::April"}

```cpp
inline constexpr std::chrono::month April{4};
```

- 戻り値: 4 月を表す定数
- 計算量: 定数

`std::chrono::April` は、4 月（`month{4}`）を表す定数です。`2024y / April / 1` のように、日付を組み立てるときに使います。

### std::chrono::May <span class="ver ver-20">C++20</span> {#May data-toc-label="std::chrono::May"}

```cpp
inline constexpr std::chrono::month May{5};
```

- 戻り値: 5 月を表す定数
- 計算量: 定数

`std::chrono::May` は、5 月（`month{5}`）を表す定数です。`2024y / May / 1` のように、日付を組み立てるときに使います。

### std::chrono::June <span class="ver ver-20">C++20</span> {#June data-toc-label="std::chrono::June"}

```cpp
inline constexpr std::chrono::month June{6};
```

- 戻り値: 6 月を表す定数
- 計算量: 定数

`std::chrono::June` は、6 月（`month{6}`）を表す定数です。`2024y / June / 1` のように、日付を組み立てるときに使います。

### std::chrono::July <span class="ver ver-20">C++20</span> {#July data-toc-label="std::chrono::July"}

```cpp
inline constexpr std::chrono::month July{7};
```

- 戻り値: 7 月を表す定数
- 計算量: 定数

`std::chrono::July` は、7 月（`month{7}`）を表す定数です。`2024y / July / 1` のように、日付を組み立てるときに使います。

### std::chrono::August <span class="ver ver-20">C++20</span> {#August data-toc-label="std::chrono::August"}

```cpp
inline constexpr std::chrono::month August{8};
```

- 戻り値: 8 月を表す定数
- 計算量: 定数

`std::chrono::August` は、8 月（`month{8}`）を表す定数です。`2024y / August / 1` のように、日付を組み立てるときに使います。

### std::chrono::September <span class="ver ver-20">C++20</span> {#September data-toc-label="std::chrono::September"}

```cpp
inline constexpr std::chrono::month September{9};
```

- 戻り値: 9 月を表す定数
- 計算量: 定数

`std::chrono::September` は、9 月（`month{9}`）を表す定数です。`2024y / September / 1` のように、日付を組み立てるときに使います。

### std::chrono::October <span class="ver ver-20">C++20</span> {#October data-toc-label="std::chrono::October"}

```cpp
inline constexpr std::chrono::month October{10};
```

- 戻り値: 10 月を表す定数
- 計算量: 定数

`std::chrono::October` は、10 月（`month{10}`）を表す定数です。`2024y / October / 1` のように、日付を組み立てるときに使います。

### std::chrono::November <span class="ver ver-20">C++20</span> {#November data-toc-label="std::chrono::November"}

```cpp
inline constexpr std::chrono::month November{11};
```

- 戻り値: 11 月を表す定数
- 計算量: 定数

`std::chrono::November` は、11 月（`month{11}`）を表す定数です。`2024y / November / 1` のように、日付を組み立てるときに使います。

### std::chrono::December <span class="ver ver-20">C++20</span> {#December data-toc-label="std::chrono::December"}

```cpp
inline constexpr std::chrono::month December{12};
```

- 戻り値: 12 月を表す定数
- 計算量: 定数

`std::chrono::December` は、12 月（`month{12}`）を表す定数です。`2024y / December / 1` のように、日付を組み立てるときに使います。

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
