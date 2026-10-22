---
title: std::chrono::weekday_indexed
summary: "「第 n の曜日」を表す型（第 2 月曜日など）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::weekday_indexed

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「毎月第 2 月曜日」のような予定を扱うとき、`weekday` に「何番目か」の情報を足したものが `weekday_indexed` です。`Monday[2]` と書いて作ります。

!!! tip "ポイント"
    - `weekday[n]` で作る（n は 1〜5）。
    - `weekday()` と `index()` で中身を取り出す。
    - `year/month/weekday[n]` で日付の指定になる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::weekday_indexed {#weekday_indexed}

```cpp
class weekday_indexed {
 public:
  constexpr std::chrono::weekday weekday() const noexcept;
  constexpr unsigned index() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | unsigned | 何番目か（1〜5） |

- 戻り値: `index()` は何番目か
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto wi = Monday[2];
  std::println("{} {}", wi.weekday().c_encoding(), wi.index());
}
```

```text title="実行結果"
1 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 毎月第 2 日曜日のセール日 | `std::chrono::Sunday[2]` |

## よくあるミス

??? failure "第 5 曜日が存在しない月"
    第 5 週の曜日が無い月もあります。`ok()` と、組み合わせた日付の `ok()` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weekday`](weekday.md) | 曜日 |
| [`weekday_last`](weekday_last.md) | 最後の曜日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 第 n 曜日
    - [x] weekday[n] で作る
    - [x] n は 1〜5

## 関連ページ

- [cpprefjp: std::chrono::weekday_indexed](https://cpprefjp.github.io/reference/chrono/weekday_indexed.html)
- [cppreference: std::chrono::weekday_indexed](https://en.cppreference.com/w/cpp/chrono/weekday_indexed)
