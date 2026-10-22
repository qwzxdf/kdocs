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

タイムゾーンを使うには、まず `"Asia/Tokyo"` のような名前からゾーンを取り出します。`locate_zone(name)` が、その `time_zone` へのポインタを返します。

!!! tip "ポイント"
    - 名前は IANA のゾーン名（`Asia/Tokyo`、`America/New_York`）。
    - 戻り値はデータベースが持つオブジェクトへのポインタ（解放不要）。
    - 見つからないと例外。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::locate_zone {#locate_zone}

```cpp
const time_zone* locate_zone(string_view tz_name);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tz_name` | string_view | ゾーン名 |

- 戻り値: `time_zone` へのポインタ（見つからなければ例外）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto* tz = std::chrono::locate_zone("Asia/Tokyo");
  std::println("{}", tz->name());
}
```

```text title="実行結果"
Asia/Tokyo
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ユーザー設定のゾーンを読み込む | `std::chrono::locate_zone(setting)` |

## よくあるミス

??? failure "名前を間違える"
    存在しない名前は `std::runtime_error` を投げます。外から入力された名前は `try` で囲みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`current_zone`](current_zone.md) | 今のゾーン |
| [`time_zone`](time_zone.md) | ゾーンの型 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 名前からゾーンを取る
    - [x] 戻りはポインタ
    - [x] 見つからなければ例外

## 関連ページ

- [cpprefjp: std::chrono::locate_zone](https://cpprefjp.github.io/reference/chrono/locate_zone.html)
- [cppreference: std::chrono::locate_zone](https://en.cppreference.com/w/cpp/chrono/tzdb/locate_zone)
