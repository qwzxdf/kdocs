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

`clock()` が返す数が「1 だけ増える」のは、何秒に当たるのでしょうか。これは処理系ごとに違います。Windows の MSVC では 1 秒あたり 1000（つまり 1 ミリ秒）、Linux の GCC では 100 万（1 マイクロ秒）です。`CLOCKS_PER_SEC` は、この「1 秒あたりのカウント数」を表すマクロで、`clock()` の差をこれで割ると、秒になります。

!!! tip "ポイント"
    - `clock()` の差を `CLOCKS_PER_SEC` で割ると、秒になる
    - 値は処理系ごとに違う。1000 などと決め打ちしない
    - 型は `clock_t` のことも、`long` のこともある。割るときは `double` に直す
    - 精度の高い計測には `steady_clock`

!!! info "このページを読む前に"
    [`std::clock`](clock.md) を先に読んでください。

## 関数の詳しい説明

### CLOCKS_PER_SEC {#clocks_per_sec}

```cpp
#define CLOCKS_PER_SEC /* 実装定義 */
```

`<ctime>` で定義されるマクロです。値は処理系が決めます。POSIX では 100 万と決まっていて、Linux や macOS はそうなっています。MSVC は 1000 です。

この値は、`clock()` が刻む細かさの単位であって、精度そのものではありません。`CLOCKS_PER_SEC` が 100 万でも、実際に更新される間隔が 1 ミリ秒より粗いこともあります。

使い方は 1 通りです。秒に直したいとき、`double` にキャストしてから割ります。

```cpp
const double sec = static_cast<double>(end - start) / CLOCKS_PER_SEC;
```

ミリ秒にしたいなら、`* 1000.0` を付けます。`CLOCKS_PER_SEC` 自体は式なので、値の型は環境で変わります。`1000` と決め打ちすると、別の環境で 1000 倍ずれます。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::clock_t start = std::clock();

  volatile long sum = 0;
  for (long i = 0; i < 5'000'000; ++i) {
    sum += i;
  }

  const std::clock_t end = std::clock();
  const double sec = static_cast<double>(end - start) / CLOCKS_PER_SEC;
  std::println("秒に直せた: {}", sec >= 0.0);
  std::println("単位は正の数: {}", CLOCKS_PER_SEC > 0);
}
```

```text title="実行結果"
秒に直せた: true
単位は正の数: true
```

## ゲームでの使いどころ

使うのは、古いコードで簡易に処理時間を測っている場所を読むときです。新しく計測を書くなら、`std::chrono::steady_clock` と `duration<double, std::milli>` で、単位の換算を型に任せます。

## よくあるミス

??? failure "値を決め打ちする"
    `/ 1000.0` と書くと、Linux では 1000 倍ずれます。必ず `CLOCKS_PER_SEC` を使います。

??? failure "整数のまま割る"
    `(end - start) / CLOCKS_PER_SEC` は整数の割り算で、1 秒未満が 0 になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`clock`](clock.md) | CPU 時間を取る関数 |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 単位を型で持つ。換算を間違えにくい |

## コンパイラ対応

C 由来のマクロです。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `clock()` の差を割って秒にするための、処理系ごとの定数
    - [x] 決め打ちしない
    - [x] `double` にキャストしてから割る

## 関連ページ

- [cpprefjp: CLOCKS_PER_SEC](https://cpprefjp.github.io/reference/ctime/clocks_per_sec.html)
- [cppreference: CLOCKS_PER_SEC](https://en.cppreference.com/w/cpp/chrono/c/CLOCKS_PER_SEC)
