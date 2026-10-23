---
title: std::clock
summary: "プログラムが使った CPU 時間を取得する（C 由来）。"
order: 2
group: 時刻（<ctime>）
tags:
  - 入出力・文字列
---

# std::clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ctime>`
</div>

`std::clock()` は、**プログラムが使った CPU 時間**を返すC 由来の関数です。単位は `CLOCKS_PER_SEC` で割ると秒になります。処理の簡易的な計測に使われますが、マルチスレッドや待ち時間は正確に反映されません。計測には [`steady_clock`](../../utilities/chrono/steady_clock.md) を使います。

!!! tip "ポイント"
    - `CLOCKS_PER_SEC` で割って秒にする。
    - スレッドを使うと合計の CPU 時間になる（壁時計の時間ではない）。
    - 計測は `steady_clock`。

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::clock {#clock}

```cpp
std::clock_t clock();
```

- 戻り値: CPU 時間（クロック数）
- 計算量: O(1)

```cpp
#include <ctime>
#include <print>

int main() {
  std::clock_t t = std::clock();
  std::println("{}", t >= 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `steady_clock` に置き換える |

## よくあるミス

??? failure "実際に経過した時間だと思う"
    CPU 時間です。待ち時間（`sleep`）は含まれません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::chrono::steady_clock`](../../utilities/chrono/steady_clock.md) | 壁時計の経過時間 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CPU 時間を取る
    - [x] 壁時計の時間ではない
    - [x] 計測は steady_clock

## 関連ページ

- [cpprefjp: std::clock](https://cpprefjp.github.io/reference/ctime/clock.html)
- [cppreference: std::clock](https://en.cppreference.com/w/cpp/chrono/c/clock)
