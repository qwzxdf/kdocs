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

ゾーンの一覧や、うるう秒の一覧を見たいとき、その元になるデータベースを取り出す関数が `std::chrono::get_tzdb` です。戻り値は `const tzdb&` で、`zones`、`links`、`leap_seconds`、`version` が入っています。

!!! tip "ポイント"
    - 現在使われている `tzdb` への参照を返す
    - 参照は、`reload_tzdb` で更新されても、有効なまま
    - 初回の呼び出しで、データの読み込みが起きて、時間がかかることがある
    - `locate_zone` や `current_zone` は、内部でこれを使っている

!!! info "このページを読む前に"
    [`tzdb`](tzdb.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::get_tzdb {#get_tzdb}

<span class="ver ver-20">C++20</span>

```cpp
const tzdb& get_tzdb();
```

引数はありません。現在の最新の `tzdb` への参照を返します。

`get_tzdb_list()` が持つ一覧の先頭が、これです。`reload_tzdb()` で新しい版が読み込まれると、一覧の先頭が新しい版に変わり、そのあとの `get_tzdb()` は新しい版を返します。以前の `get_tzdb()` が返した参照は、古い版を指したまま、生き続けます。

初めて呼ぶときに、OS のデータベースの読み込みが行われる実装があります。ゲームの起動直後など、遅延が困る場所では、読み込み画面の最中に一度呼んで、準備しておきます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const tzdb& db = get_tzdb();
  std::println("版が空でない: {}", !db.version.empty());

  // 2 回呼んでも、同じ版
  std::println("同じ版: {}", &db == &get_tzdb());

  // ゾーンの一覧から、名前を数える
  int asia = 0;
  for (const time_zone& z : db.zones) {
    if (z.name().starts_with("Asia/")) ++asia;
  }
  std::println("Asia/ のゾーンがある: {}", asia > 0);
}
```

```text title="実行結果"
版が空でない: true
同じ版: true
Asia/ のゾーンがある: true
```

## ゲームでの使いどころ

設定画面で、プレイヤーにタイムゾーンを選ばせるための一覧作りに使います。

## よくあるミス

??? failure "初回の呼び出しの遅延を考えない"
    読み込みに時間がかかる環境があります。ゲームの最初のフレームで呼ぶと、画面が止まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tzdb`](tzdb.md) | 戻り値の型 |
| [`tzdb_list`](tzdb_list.md) | 版の履歴 |
| [`reload_tzdb`](reload_tzdb.md) | 最新版を読み込み直す |
| [`locate_zone`](locate_zone.md) | ゾーンを名前で探す |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: get_tzdb](https://cpprefjp.github.io/reference/chrono/get_tzdb.html)
- [cppreference: std::chrono::get_tzdb](https://en.cppreference.com/w/cpp/chrono/get_tzdb)
