---
title: std::chrono::tzdb_list
summary: "tzdb の更新履歴（世代ごとの一覧）を管理する型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::tzdb_list

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

実行中にタイムゾーンのデータベースを更新すると、古い版を参照している箇所も残ります。`tzdb_list` は、新しい順に `tzdb` の世代を持ち、`front()` で最新のものを取ります。

!!! tip "ポイント"
    - `get_tzdb_list()` で取得する。
    - `front()` が最新の `tzdb`。
    - `begin()` / `end()` で世代を順に調べられる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::tzdb_list {#tzdb_list}

```cpp
class tzdb_list {
 public:
  const tzdb& front() const noexcept;
  const_iterator begin() const noexcept;
  const_iterator end() const noexcept;
};
```

- 戻り値: 世代の一覧
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto& db = std::chrono::get_tzdb_list().front();
  std::println("{}", !db.zones.empty());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| データベースの更新を確かめる | `std::chrono::reload_tzdb()` |

## よくあるミス

??? failure "古い世代の参照を持ち続ける"
    更新後も古い世代が残るため、メモリが増えます。必要なら参照を持たず、その都度取り直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tzdb`](tzdb.md) | データベース本体 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tzdb の世代管理
    - [x] front() が最新
    - [x] 更新は reload_tzdb

## 関連ページ

- [cpprefjp: std::chrono::tzdb_list](https://cpprefjp.github.io/reference/chrono/tzdb_list.html)
- [cppreference: std::chrono::tzdb_list](https://en.cppreference.com/w/cpp/chrono/tzdb_list)
