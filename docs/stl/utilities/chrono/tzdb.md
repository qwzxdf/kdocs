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

世界のタイムゾーンの規則は、国の都合で何度も変わります。夏時間の開始日が変わる、国が時差を変える。そうした履歴は、IANA（インターネット番号割り当て機関）が管理するタイムゾーンデータベースにまとまっています。`std::chrono::tzdb` は、そのデータベースの 1 つの版を表す型で、ゾーンの一覧、別名の一覧、うるう秒の一覧、版の文字列を持ちます。

!!! tip "ポイント"
    - `zones`（ゾーンの一覧）、`links`（別名）、`leap_seconds`（うるう秒）、`version`（版）の 4 つを持つ
    - `get_tzdb()` で、現在の版を取得する
    - `locate_zone` / `current_zone` は、このデータベースへの検索のショートカット
    - コピーできない。参照で扱う

!!! info "このページを読む前に"
    [`time_zone`](time_zone.md) と [`get_tzdb`](get_tzdb.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::tzdb {#tzdb}

<span class="ver ver-20">C++20</span>

```cpp
struct tzdb {
  std::string version;
  std::vector<time_zone> zones;
  std::vector<time_zone_link> links;
  std::vector<leap_second> leap_seconds;

  const time_zone* locate_zone(std::string_view tz_name) const;
  const time_zone* current_zone() const;
};
```

`zones` は、ゾーンの名前の昇順に並んでいます。数百件あります。`links` は、古い名前から新しい名前への対応で、`locate_zone` は、これも辿って、最終のゾーンを返します。

`version` は、データベースの版を示す文字列で、`2025b` のような形です。ゾーンの規則が更新されると、版が上がります。OS やランタイムが更新を配布する方式なので、古い OS では古い規則のままのことがあります。

`locate_zone` の名前がデータベースにない場合は、`std::runtime_error` を投げます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const tzdb& db = get_tzdb();

  std::println("版がある: {}", !db.version.empty());
  std::println("ゾーン数が 100 以上: {}", db.zones.size() >= 100);
  std::println("うるう秒 27 回: {}", db.leap_seconds.size() == 27);

  const time_zone* tokyo = db.locate_zone("Asia/Tokyo");
  std::println("{}", tokyo->name());
}
```

```text title="実行結果"
版がある: true
ゾーン数が 100 以上: true
うるう秒 27 回: true
Asia/Tokyo
```

## ゲームでの使いどころ

プレイヤーが選べるタイムゾーンの一覧を、設定画面に出すときに、`zones` を回して名前を並べます。

## よくあるミス

??? failure "tzdb をコピーする"
    コピーできません。`const tzdb&` で受けます。

??? failure "古い OS で、新しい規則が反映されていない"
    OS が持つデータベースの版に依存します。重要な日付の計算は、サーバー側で行うことを検討します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_tzdb`](get_tzdb.md) | 現在の版を取る |
| [`tzdb_list`](tzdb_list.md) | 版の履歴を持つ |
| [`time_zone`](time_zone.md) | ゾーン 1 つ |
| [`time_zone_link`](time_zone_link.md) | 別名 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: tzdb](https://cpprefjp.github.io/reference/chrono/tzdb.html)
- [cppreference: std::chrono::tzdb](https://en.cppreference.com/w/cpp/chrono/tzdb)
