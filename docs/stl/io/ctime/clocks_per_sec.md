---
title: CLOCKS_PER_SEC
summary: "clock() の値を、秒に直すための 1 秒あたりのカウント数。"
order: 900
tags:
  - 入出力・文字列
---

# CLOCKS_PER_SEC

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`clock()` が返すカウントは、処理系ごとに単位が違います（Linux では 100 万、Windows では 1000 など）。秒に直すには、この `CLOCKS_PER_SEC` で割ります。

!!! tip "ポイント"
    - マクロ（式）で、値は処理系ごとに違う。
    - `double(end - start) / CLOCKS_PER_SEC` で秒にする。
    - 精度の良い計測には `steady_clock`。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### CLOCKS_PER_SEC {#clocks_per_sec}

```cpp
#define CLOCKS_PER_SEC /* 実装定義 */
```

- 戻り値: 1 秒あたりのカウント数
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::clock_t start = std::clock();
  // ... 計測したい処理 ...
  std::clock_t end = std::clock();
  double sec = static_cast<double>(end - start) / CLOCKS_PER_SEC;
  std::println("{}", sec >= 0.0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| CPU 時間を秒に直す | `double(c) / CLOCKS_PER_SEC` |

## よくあるミス

??? failure "値を決め打ちする"
    `1000` などと決め打ちすると、環境が変わったときにずれます。必ず `CLOCKS_PER_SEC` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`clock`](clock.md) | CPU 時間を取る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] clock() の単位を秒に直すマクロ
    - [x] 値は処理系ごと
    - [x] 決め打ちしない

## 関連ページ

- [cpprefjp: CLOCKS_PER_SEC](https://cpprefjp.github.io/reference/ctime/clock.html)
- [cppreference: CLOCKS_PER_SEC](https://en.cppreference.com/w/cpp/chrono/c/CLOCKS_PER_SEC)
