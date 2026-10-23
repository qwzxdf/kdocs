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

`zoned_time` は、`"Asia/Tokyo"` のような文字列から `time_zone` を探します。この「ゾーンの型」と「既定のゾーン」「文字列からゾーンを探す方法」を決めているのが `zoned_traits` です。自作のゾーンの型を `zoned_time` で使うときに、特殊化します。

!!! tip "ポイント"
    - `default_zone()` と `locate_zone(name)` を持つ。
    - 標準では `const time_zone*` に対して用意されている。
    - ふつうは意識しない。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::chrono::zoned_traits {#zoned_traits}

```cpp
template <class TimeZonePtr>
struct zoned_traits;  // const time_zone* に対して特殊化済み
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `TimeZonePtr` | 型 | ゾーンを指す型 |

- 戻り値: `default_zone()` と `locate_zone()`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto* tz = std::chrono::zoned_traits<const std::chrono::time_zone*>::locate_zone("Asia/Tokyo");
  std::println("{}", tz->name());
}
```

```text title="実行結果"
Asia/Tokyo
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作のゾーン型を zoned_time で使う | `zoned_traits<MyZone>` を特殊化する |

## よくあるミス

??? failure "特殊化せずに自作型を渡す"
    特殊化がないと、`zoned_time` が文字列からゾーンを探せません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`zoned_time`](zoned_time.md) | ゾーンつきの時刻 |
| [`time_zone`](time_zone.md) | ゾーン |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] zoned_time のゾーン解釈の特性
    - [x] default_zone / locate_zone
    - [x] ふつうは触らない

## 関連ページ

- [cpprefjp: std::chrono::zoned_traits](https://cpprefjp.github.io/reference/chrono/zoned_traits.html)
- [cppreference: std::chrono::zoned_traits](https://en.cppreference.com/w/cpp/chrono/zoned_traits)
