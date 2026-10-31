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

ある処理にどれだけ時間がかかったかを、手軽に知りたい。C の時代から、そのために使われてきたのが `std::clock()` です。ただし返すのは「実際に経過した時間」ではなく、<strong>プログラムが CPU を使った時間</strong>です。値は `CLOCKS_PER_SEC` で割ると秒になります。

CPU 時間なので、`sleep` や入出力の待ち時間は含まれません。複数のスレッドで動かすと、各スレッドの CPU 時間が足し合わされ、壁の時計より大きな値になることもあります。そのため、速さの計測には `steady_clock` を使うのが、現在の標準的なやり方です。

!!! tip "ポイント"
    - 戻り値の単位は `CLOCKS_PER_SEC` 分の 1 秒。割って秒にする
    - CPU 時間であり、実際に経過した時間（壁時計の時間）ではない。待ち時間は入らない
    - マルチスレッドでは、全スレッドの合計になる
    - 計測は `steady_clock` を使う

!!! info "このページを読む前に"
    [`CLOCKS_PER_SEC`](clocks_per_sec.md) と [`std::clock_t`](clock_t.md) を先に読むと、戻り値の単位が分かります。

## 関数の詳しい説明

### std::clock {#clock}

```cpp
std::clock_t clock();
```

引数はありません。呼び出した時点までの、プログラムが使った CPU 時間を、`clock_t` で返します。起点はプログラムの起動時とは限らず、処理系が決めます。そのため、1 回の値には意味がなく、2 回呼んだ差を取って使います。

差を秒にするときは、`static_cast<double>(end - start) / CLOCKS_PER_SEC` と書きます。整数のまま割ると、1 秒未満が 0 に切り捨てられます。

使えない場合や、値が表せない場合は `(clock_t)(-1)` を返します。

落とし穴は、環境による意味の違いです。Windows の MSVC では `clock()` は壁時計の経過時間を返し（CPU 時間ではなく）、Linux では CPU 時間です。同じコードで、待ち時間を含むか含まないかが変わります。

計算量は定数です。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::clock_t start = std::clock();

  volatile long sum = 0;  // 最適化で消えないようにする
  for (long i = 0; i < 10'000'000; ++i) {
    sum += i;
  }

  const std::clock_t end = std::clock();
  const double sec = static_cast<double>(end - start) / CLOCKS_PER_SEC;
  std::println("0 秒以上: {}", sec >= 0.0);
}
```

```text title="実行結果"
0 秒以上: true
```

実際に何秒かかったかは、マシンによって変わるので表示していません。`end - start` を `CLOCKS_PER_SEC` で割って、秒にしています。

## ゲームでの使いどころ

古いコードや、ちょっとした処理の簡易計測で見かけます。ゲームのフレーム時間やプロファイルには、`std::chrono::steady_clock` を使います。

```cpp
const auto t0 = std::chrono::steady_clock::now();
Update();
const auto t1 = std::chrono::steady_clock::now();
const double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
```

## よくあるミス

??? failure "実際に経過した時間だと思う"
    環境によっては CPU 時間なので、`sleep` の時間が入りません。`Sleep(1000)` のあとでも、差がほぼ 0 になります。

??? failure "整数のまま割って、0 秒になる"
    `(end - start) / CLOCKS_PER_SEC` は整数の割り算で、1 秒未満が切り捨てられます。`double` にしてから割ります。

??? failure "マルチスレッドで、実時間より大きい値が出る"
    各スレッドの CPU 時間が合計されます。4 スレッドで 1 秒動くと、4 秒近くになることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::chrono::steady_clock`](../../utilities/chrono/steady_clock.md) | 壁時計の経過時間。計測にはこちら |
| [`CLOCKS_PER_SEC`](clocks_per_sec.md) | `clock()` の単位 |
| [`std::time`](time.md) | 現在時刻（秒） |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `clock()` は CPU 時間（環境によっては壁時計の時間）を返す
    - [x] 2 回の差を `CLOCKS_PER_SEC` で割って秒にする。`double` で割る
    - [x] 計測は `steady_clock`

## 関連ページ

- [cpprefjp: std::clock](https://cpprefjp.github.io/reference/ctime/clock.html)
- [cppreference: std::clock](https://en.cppreference.com/w/cpp/chrono/c/clock)
