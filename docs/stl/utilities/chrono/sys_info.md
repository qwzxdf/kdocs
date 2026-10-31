---
title: std::chrono::sys_info
summary: "ある UTC の時点での、時差・夏時間・略称の情報。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::sys_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

ある瞬間の東京の時差は何時間か、夏時間は効いているか、略称は `JST` か `EDT` か。`time_zone::get_info(sys_time)` が返す `std::chrono::sys_info` は、そのゾーンの、ある UTC の時点での設定をまとめた構造体です。

!!! tip "ポイント"
    - `offset` は UTC からの時差、`save` は夏時間の補正（夏時間でなければ 0）
    - `abbrev` は略称（`JST`、`EDT` など）
    - `begin` と `end` は、この設定が有効な期間
    - 夏時間の切り替えで `end` を過ぎると、次の設定になる

!!! info "このページを読む前に"
    [`time_zone`](time_zone.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::sys_info {#sys_info}

<span class="ver ver-20">C++20</span>

```cpp
struct sys_info {
  sys_seconds begin;
  sys_seconds end;
  seconds offset;
  minutes save;
  std::string abbrev;
};
```

`offset` は、その時点の UTC との差です。夏時間の補正を含みます。日本の `JST` は `+9h` です。ニューヨークの夏は `EDT` で `-4h`、冬は `EST` で `-5h` です。

`save` は、`offset` のうち、夏時間のために足された分です。夏時間の期間は `1h`、そうでなければ `0` です。標準時間の時差は `offset - save` で求まります。

`begin` から `end` までの期間は、同じ設定が続きます。夏時間の切り替え日に、`end` で次の設定に変わります。1 つのゾーンが、一生変わらない設定なら、`begin` は `sys_seconds::min()`、`end` は `sys_seconds::max()` です。

`abbrev` は、時刻の表示に添える略称です。ただし、略称は一意ではありません。`IST` は、インド、アイルランド、イスラエルのどれにも使われます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const sys_seconds jan = sys_days{2026y / January / 1};
  const sys_seconds jul = sys_days{2026y / July / 1};

  const time_zone* ny = locate_zone("America/New_York");
  for (const sys_seconds t : {jan, jul}) {
    const sys_info info = ny->get_info(t);
    std::println("{:%F}: 時差 {} 時間 夏時間 {} 分", t,
                 duration_cast<hours>(info.offset).count(), info.save.count());
  }

  const sys_info tokyo = locate_zone("Asia/Tokyo")->get_info(jan);
  std::println("東京: {} 時差 {} 時間", tokyo.abbrev, duration_cast<hours>(tokyo.offset).count());
}
```

```text title="実行結果"
2026-01-01: 時差 -5 時間 夏時間 0 分
2026-07-01: 時差 -4 時間 夏時間 60 分
東京: JST 時差 9 時間
```

ニューヨークの冬は -5 時間、夏は夏時間の 60 分が足されて -4 時間です。略称は、標準の実装では冬が `EST`、夏が `EDT` ですが、MSVC（ICU を使う実装）では `GMT-5` や `GMT-4` と出ることがあるため、ここでは表示していません。

## ゲームでの使いどころ

ログに「JST」のような略称を添えたり、プレイヤーに「現在 UTC+9」と表示したりするときに使います。

## よくあるミス

??? failure "略称で地域を判定する"
    `IST` のように、略称は一意ではありません。地域の判定には、ゾーン名を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_info`](local_info.md) | ローカル時刻から調べる版。曖昧さも表す |
| [`time_zone`](time_zone.md) | この情報を返す |
| [`zoned_time`](zoned_time.md) | ゾーンつきの時点 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: sys_info](https://cpprefjp.github.io/reference/chrono/sys_info.html)
- [cppreference: std::chrono::sys_info](https://en.cppreference.com/w/cpp/chrono/sys_info)
