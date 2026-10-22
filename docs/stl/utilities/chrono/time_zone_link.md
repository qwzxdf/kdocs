---
title: std::chrono::time_zone_link
summary: "別名のタイムゾーン（古い名前から新しい名前への対応）を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::time_zone_link

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

ゾーン名は、地名の変更などで変わります。古い名前でも使えるように、データベースは別名を持ちます。`time_zone_link` は、その「古い名前 → 実際の名前」の対応を表します。

!!! tip "ポイント"
    - `name()` が別名、`target()` が実際の名前。
    - `tzdb.links` に入っている。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::time_zone_link {#time_zone_link}

```cpp
class time_zone_link {
 public:
  string_view name() const noexcept;
  string_view target() const noexcept;
};
```

- 戻り値: 別名と、その向き先の名前
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto& db = std::chrono::get_tzdb();
  std::println("{}", !db.links.empty());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いゾーン名を新しい名前に直す | `link.target()` |

## よくあるミス

??? failure "別名を実体と取り違える"
    別名は `time_zone` ではありません。`target()` の名前で `locate_zone` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tzdb`](tzdb.md) | データベース |
| [`time_zone`](time_zone.md) | ゾーン本体 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ゾーン名の別名
    - [x] name() と target()
    - [x] links に入っている

## 関連ページ

- [cpprefjp: std::chrono::time_zone_link](https://cpprefjp.github.io/reference/chrono/time_zone_link.html)
- [cppreference: std::chrono::time_zone_link](https://en.cppreference.com/w/cpp/chrono/time_zone_link)
