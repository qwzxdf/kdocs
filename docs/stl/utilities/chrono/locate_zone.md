---
title: std::chrono::locate_zone
summary: "名前から time_zone を取得する。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::locate_zone

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`"Asia/Tokyo"` や `"America/New_York"` のような、IANA のタイムゾーン名から、`time_zone` を取り出す関数が `std::chrono::locate_zone` です。名前が分からないものを渡すと、例外を投げます。

!!! tip "ポイント"
    - 名前は IANA のタイムゾーン名（`Area/City`）
    - 戻り値は `const time_zone*`。nullptr にはならない
    - 存在しない名前では `std::runtime_error`
    - 別名（`time_zone_link`）でも、元のゾーンが返る

!!! info "このページを読む前に"
    [`time_zone`](time_zone.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::locate_zone {#locate_zone}

<span class="ver ver-20">C++20</span>

```cpp
const time_zone* locate_zone(std::string_view tz_name);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tz_name` | `std::string_view` | タイムゾーンの名前 |

現在のタイムゾーンデータベース（`get_tzdb()`）から、名前が一致するゾーンを探します。名前は、大文字小文字を区別します。`"asia/tokyo"` は見つかりません。

別名（古い名前）を渡したときも、元のゾーンへのポインタが返ります。`"Asia/Calcutta"` と `"Asia/Kolkata"` は、同じゾーンを指します。

見つからないと `std::runtime_error` を投げます。プレイヤーの設定などの外部の入力から来る名前は、`try` で囲みます。

戻り値のポインタは、データベースが更新されても、有効なままです。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <stdexcept>

int main() {
  using namespace std::chrono;

  const time_zone* tokyo = locate_zone("Asia/Tokyo");
  std::println("{}", tokyo->name());

  // 同じ名前なら同じポインタ
  std::println("同じゾーン: {}", tokyo == locate_zone("Asia/Tokyo"));

  // 存在しない名前は例外
  try {
    locate_zone("Mars/Olympus");
  } catch (const std::runtime_error&) {
    std::println("見つからない名前は例外");
  }
}
```

```text title="実行結果"
Asia/Tokyo
同じゾーン: true
見つからない名前は例外
```

## ゲームでの使いどころ

プレイヤーが設定画面で選んだタイムゾーン名から、`time_zone` を取得します。

## よくあるミス

??? failure "名前の大文字小文字を間違える"
    `"asia/tokyo"` では見つかりません。

??? failure "例外を考えない"
    外から来る名前は、`try` で囲んで、見つからなければ既定のゾーンに戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`current_zone`](current_zone.md) | 今の環境のタイムゾーンを取る |
| [`time_zone`](time_zone.md) | 取得するもの |
| [`get_tzdb`](get_tzdb.md) | データベース全体 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: locate_zone](https://cpprefjp.github.io/reference/chrono/locate_zone.html)
- [cppreference: std::chrono::locate_zone](https://en.cppreference.com/w/cpp/chrono/locate_zone)
