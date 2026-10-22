---
title: std::chrono::tzdb
summary: "タイムゾーンのデータベース（IANA）を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::tzdb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

タイムゾーンの規則は、各国の政策で変わります。それを持つデータベースが `tzdb` で、バージョン・ゾーン一覧・うるう秒の一覧などをもっています。

!!! tip "ポイント"
    - `get_tzdb()` で現在のものを取る。
    - `zones`・`links`・`leap_seconds`・`version` のメンバをもつ。
    - `reload_tzdb()` で更新を読み直せる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::tzdb {#tzdb}

```cpp
struct tzdb {
  string version;
  vector<time_zone> zones;
  vector<time_zone_link> links;
  vector<leap_second> leap_seconds;
  const time_zone* locate_zone(string_view) const;
  const time_zone* current_zone() const;
};
```

- 戻り値: データベースの内容
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", !db.zones.empty());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 対応しているゾーン一覧を調べる | `std::chrono::get_tzdb().zones` |

## よくあるミス

??? failure "コピーして持ち歩く"
    大きなオブジェクトです。参照で扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_tzdb`](get_tzdb.md) | 取得する関数 |
| [`tzdb_list`](tzdb_list.md) | 複数世代の管理 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] タイムゾーンの DB
    - [x] get_tzdb() で取る
    - [x] zones / links / leap_seconds

## 関連ページ

- [cpprefjp: std::chrono::tzdb](https://cpprefjp.github.io/reference/chrono/tzdb.html)
- [cppreference: std::chrono::tzdb](https://en.cppreference.com/w/cpp/chrono/tzdb)
