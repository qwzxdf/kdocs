---
title: std::chrono::current_zone
summary: "今の環境のタイムゾーンを取得する。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::current_zone

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

プレイヤーのパソコンが設定している地域の時刻を扱いたいときは、名前を知らなくても `current_zone()` で取り出せます。

!!! tip "ポイント"
    - OS の設定から取得される。
    - 戻り値はデータベースが持つ `time_zone` へのポインタ。
    - `zoned_time(current_zone(), now)` でローカル時刻にする。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::current_zone {#current_zone}

```cpp
const time_zone* current_zone();
```

- 戻り値: 今のゾーンへのポインタ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  const auto* tz = std::chrono::current_zone();
  std::println("{}", tz != nullptr);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| プレイヤーの現地時刻を表示 | `zoned_time{current_zone(), system_clock::now()}` |

## よくあるミス

??? failure "サーバーでクライアントの地域と取り違える"
    動いているマシンの設定です。遠隔のプレイヤーの地域は、別に受け取ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`locate_zone`](locate_zone.md) | 名前から取得 |

## コンパイラ対応

C++20 の機能です。GCC 14 以降、MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 今の環境のゾーン
    - [x] OS の設定に従う
    - [x] 戻りはポインタ

## 関連ページ

- [cpprefjp: std::chrono::current_zone](https://cpprefjp.github.io/reference/chrono/current_zone.html)
- [cppreference: std::chrono::current_zone](https://en.cppreference.com/w/cpp/chrono/tzdb/current_zone)
