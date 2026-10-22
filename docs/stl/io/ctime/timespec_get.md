---
title: std::timespec_get
summary: "現在の時刻を、秒とナノ秒の組（timespec）で取得する。"
order: 900
tags:
  - 入出力・文字列
---

# std::timespec_get

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <ctime>`
</div>

`time` は秒の精度しかありません。`timespec_get` は、ナノ秒の精度で現在時刻を取れる C の関数です。ゲームの計測には [`steady_clock`](../../utilities/chrono/steady_clock.md) のほうが向いています。

!!! tip "ポイント"
    - `TIME_UTC` を渡すと、UTC の現在時刻が取れる。
    - 戻り値は `base`（成功）か 0（失敗）。
    - 時計の巻き戻りがありうるので計測には不向き。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::timespec_get {#timespec_get}

```cpp
int timespec_get(std::timespec* ts, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ts` | timespec* | 結果を入れる変数 |
| `base` | int | `TIME_UTC` を指定 |

- 戻り値: 成功なら `base`、失敗なら 0
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::timespec ts;
  int r = std::timespec_get(&ts, TIME_UTC);
  std::println("{}", r == TIME_UTC);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ナノ秒単位のタイムスタンプ | `std::timespec_get(&ts, TIME_UTC)` |

## よくあるミス

??? failure "経過時間の計測に使う"
    壁時計なので巻き戻ることがあります。計測には `steady_clock` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time`](time.md) | 秒の精度 |
| [`steady_clock`](../../utilities/chrono/steady_clock.md) | 計測に向く |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 秒とナノ秒の現在時刻
    - [x] TIME_UTC を渡す
    - [x] 計測は steady_clock

## 関連ページ

- [cpprefjp: std::timespec_get](https://cpprefjp.github.io/reference/ctime/timespec_get.html)
- [cppreference: std::timespec_get](https://en.cppreference.com/w/cpp/chrono/c/timespec_get)
