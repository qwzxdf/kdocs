---
title: std::chrono::zoned_traits
summary: "zoned_time が、ゾーンの指定をどう解釈するかを決める特性。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::zoned_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`zoned_time` は、`"Asia/Tokyo"` のような名前の文字列から、ゾーンを解決します。その解決のしかたを決めるのが `std::chrono::zoned_traits` で、ゾーンの型ごとに、既定のゾーンを返す `default_zone` と、名前から取り出す `locate_zone` を持ちます。標準の `const time_zone*` 用の特殊化が用意されています。

!!! tip "ポイント"
    - `zoned_time` のゾーンの型ごとの特性。既定の型は `const time_zone*`
    - `default_zone()` は UTC を返す。`locate_zone(名前)` は名前からゾーンを取る
    - 自作のタイムゾーン型を `zoned_time` に使うときに、特殊化する
    - 普段は意識しない

!!! info "このページを読む前に"
    [`zoned_time`](zoned_time.md) と [`locate_zone`](locate_zone.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::zoned_traits {#zoned_traits}

<span class="ver ver-20">C++20</span>

```cpp
template <class TimeZonePtr> struct zoned_traits {};

template <>
struct zoned_traits<const time_zone*> {
  static const time_zone* default_zone();
  static const time_zone* locate_zone(std::string_view name);
};
```

`zoned_time` に名前の文字列を渡して作ると、内部で `locate_zone` が呼ばれます。ゾーンを指定せずに作ると、`default_zone()` が呼ばれて、UTC になります。

`default_zone()` は、`locate_zone("UTC")` と同じ UTC のゾーンを返します。名前は、実装により `UTC` や `Etc/UTC` です。OS の現在のゾーンではない点に注意します。ローカルのゾーンにしたければ、`current_zone()` を明示します。

自作のタイムゾーンの型（たとえば、ゲーム内の架空の時刻体系）を `zoned_time` に使うなら、`zoned_traits<MyZone*>` を特殊化します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using Traits = zoned_traits<const time_zone*>;

  const time_zone* def = Traits::default_zone();
  const sys_seconds t = sys_days{2026y / January / 1};
  std::println("既定のゾーンの時差は 0: {}", def->get_info(t).offset == 0s);
  std::println("名前から取る: {}", Traits::locate_zone("Asia/Tokyo")->name());

  // ゾーンを指定しない zoned_time は UTC
  const zoned_time zt{sys_days{2026y / January / 1}};
  std::println("{:%F %T}", zt.get_local_time());
}
```

```text title="実行結果"
既定のゾーンの時差は 0: true
名前から取る: Asia/Tokyo
2026-01-01 00:00:00
```

ゾーンを指定しなかった `zoned_time` は UTC として扱われるので、ローカル時刻が UTC と同じになっています。

## ゲームでの使いどころ

自作することはありません。`zoned_time` に名前を直接渡せる、という仕組みの裏で動いています。

## よくあるミス

??? failure "default_zone を、今の環境のゾーンだと思う"
    UTC です。環境のゾーンは `current_zone()` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`zoned_time`](zoned_time.md) | この特性を使う型 |
| [`locate_zone`](locate_zone.md) | 名前からゾーンを取る関数 |
| [`current_zone`](current_zone.md) | 環境のゾーンを取る関数 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: zoned_traits](https://cpprefjp.github.io/reference/chrono/zoned_traits.html)
- [cppreference: std::chrono::zoned_traits](https://en.cppreference.com/w/cpp/chrono/zoned_traits)
