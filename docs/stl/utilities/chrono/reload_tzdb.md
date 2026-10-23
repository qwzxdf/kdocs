---
title: std::chrono::reload_tzdb
summary: "タイムゾーンのデータベースを、最新のものに読み込み直す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::reload_tzdb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

夏時間の規則は、国の政策で変わります。OS のタイムゾーンのデータが更新されたとき、起動したままのプログラムは古い規則を使い続けます。`reload_tzdb()` は、データベースを読み込み直して、最新の規則を反映します。

!!! tip "ポイント"
    - 新しいデータがあれば、新しい `tzdb` を追加して、その参照を返す。
    - 古い `tzdb` への参照は、そのまま有効。
    - 常時動くサーバーなどで、定期的に呼ぶ。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::reload_tzdb {#reload_tzdb}

```cpp
const tzdb& reload_tzdb();
```

- 戻り値: 最新の `tzdb` への参照
- 計算量: データベースの大きさに比例


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto& db = std::chrono::reload_tzdb();
  std::println("{}", !db.version.empty());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 長時間動くサーバーが、規則の更新を取り込む | `std::chrono::reload_tzdb();` |

## よくあるミス

??? failure "更新できない環境で呼ぶ"
    データベースが更新できない環境では、現在のものがそのまま返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_tzdb`](get_tzdb.md) | 現在のデータベース |
| [`remote_version`](remote_version.md) | 新しい版があるか |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] タイムゾーン DB を読み直す
    - [x] 新しい版を追加する
    - [x] 常時動くプログラム向け

## 関連ページ

- [cpprefjp: std::chrono::reload_tzdb](https://cpprefjp.github.io/reference/chrono/reload_tzdb.html)
- [cppreference: std::chrono::reload_tzdb](https://en.cppreference.com/w/cpp/chrono/tzdb_functions)
