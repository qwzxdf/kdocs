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

タイムゾーンの名前は、時々付け替えられます。`Asia/Calcutta` は `Asia/Kolkata` に変わりましたが、古い名前を使っているデータも世の中にたくさんあります。`std::chrono::time_zone_link` は、古い名前（別名）から新しい名前への対応を表す型で、`tzdb` の `links` に並んでいます。

!!! tip "ポイント"
    - `name()` が別名、`target()` が元のゾーンの名前
    - `locate_zone` に別名を渡すと、元のゾーンが返る。意識する必要はない
    - 一覧は `get_tzdb().links`
    - ゾーンの名前を表示するときは、別名ではなく元の名前に直すと、そろえやすい

!!! info "このページを読む前に"
    [`tzdb`](tzdb.md) と [`locate_zone`](locate_zone.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::time_zone_link {#time_zone_link}

<span class="ver ver-20">C++20</span>

```cpp
class time_zone_link {
 public:
  std::string_view name() const noexcept;
  std::string_view target() const noexcept;
};
```

`name()` は別名（古い名前）、`target()` は指す先のゾーンの名前です。

`locate_zone("Asia/Calcutta")` は、`Asia/Kolkata` の `time_zone` を返します。そのため、別名で見つけたゾーンの `name()` は、別名ではなく、元の名前になります。

別名の一覧は、数百件あり、国や地域の名前の変更、複数の都市を同じ規則にまとめた場合などを含みます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const tzdb& db = get_tzdb();
  std::println("別名がある: {}", !db.links.empty());

  // 先頭の別名は、名前と対象が両方ある
  const time_zone_link& link = db.links.front();
  std::println("名前と対象がある: {}", !link.name().empty() && !link.target().empty());

  // 別名で検索しても、元のゾーンが得られる
  const time_zone* tz = db.locate_zone(link.name());
  std::println("元のゾーンの名前: {}", tz->name() == link.target());
}
```

```text title="実行結果"
別名がある: true
名前と対象がある: true
元のゾーンの名前: true
```

## ゲームでの使いどころ

プレイヤーのデータに古いゾーン名が入っているとき、`locate_zone` が自動で最新のゾーンに解決してくれます。自分で別名の表を作る必要はありません。

## よくあるミス

??? failure "別名の名前を、そのまま保存して表示する"
    別名を表示すると、古い名前が出ます。`locate_zone` で取ったゾーンの `name()` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time_zone`](time_zone.md) | ゾーンそのもの |
| [`tzdb`](tzdb.md) | `links` を持つ |
| [`locate_zone`](locate_zone.md) | 別名も辿って検索する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: time_zone_link](https://cpprefjp.github.io/reference/chrono/time_zone_link.html)
- [cppreference: std::chrono::time_zone_link](https://en.cppreference.com/w/cpp/chrono/time_zone_link)
