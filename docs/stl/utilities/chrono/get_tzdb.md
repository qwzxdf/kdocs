---
title: std::chrono::get_tzdb
summary: "現在のタイムゾーンデータベースを取得する。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::get_tzdb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

タイムゾーンの情報にアクセスする入り口です。`get_tzdb()` が、最新の `tzdb` への参照を返します。

!!! tip "ポイント"
    - 戻り値は参照（コピーしない）。
    - `locate_zone` と `current_zone` は内部でこれを使っている。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::get_tzdb {#get_tzdb}

```cpp
const tzdb& get_tzdb();
```

- 戻り値: 最新の `tzdb` の参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", !db.version.empty());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 対応ゾーンの確認 | `std::chrono::get_tzdb().zones.size()` |

## よくあるミス

??? failure "コピーを作る"
    `auto db = get_tzdb();` はコピーです。`const auto&` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tzdb`](tzdb.md) | データベースの型 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最新の tzdb を返す
    - [x] 参照で受ける
    - [x] locate_zone の元

## 関連ページ

- [cpprefjp: std::chrono::get_tzdb](https://cpprefjp.github.io/reference/chrono/get_tzdb.html)
- [cppreference: std::chrono::get_tzdb](https://en.cppreference.com/w/cpp/chrono/tzdb/get_tzdb)
