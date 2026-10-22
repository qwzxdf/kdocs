---
title: std::chrono::time_zone
summary: "1 つのタイムゾーン（例: Asia/Tokyo）を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::time_zone

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

世界の時刻は、地域ごとに時差や夏時間が違います。`std::chrono::time_zone` は、1 つの地域の規則（Asia/Tokyo など）を持つ型で、UTC の時点とその地域のローカル時刻を変換できます。

!!! tip "ポイント"
    - `locate_zone("Asia/Tokyo")` で取得する（所有はせず、ポインタで受け取る）。
    - `name()` で名前、`get_info(...)` でその時点の時差などを取れる。
    - `zoned_time` と組み合わせて使うことが多い。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::time_zone {#time_zone}

```cpp
class time_zone {
 public:
  string_view name() const noexcept;
  template <class D> sys_info get_info(const sys_time<D>& st) const;
  template <class D> local_info get_info(const local_time<D>& tp) const;
  template <class D> local_time<common_type_t<D, seconds>> to_local(const sys_time<D>& tp) const;
  template <class D> sys_time<common_type_t<D, seconds>> to_sys(const local_time<D>& tp) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `st / tp` | sys_time / local_time | 調べたい時点 |

- 戻り値: 名前や、その時点の時差などの情報
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
| プレイヤーの地域の時刻で日替わりを判定 | `zoned_time(tz, now)` |

## よくあるミス

??? failure "tzdata がない環境"
    タイムゾーンのデータベースが無い環境（一部の組み込みや古い OS）では、`locate_zone` が例外を投げます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`zoned_time`](zoned_time.md) | ゾーンつきの時刻 |
| [`locate_zone`](locate_zone.md) | 名前から取得する |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] タイムゾーンを表す型
    - [x] locate_zone で取る
    - [x] データベースが必要

## 関連ページ

- [cpprefjp: std::chrono::time_zone](https://cpprefjp.github.io/reference/chrono/time_zone.html)
- [cppreference: std::chrono::time_zone](https://en.cppreference.com/w/cpp/chrono/time_zone)
