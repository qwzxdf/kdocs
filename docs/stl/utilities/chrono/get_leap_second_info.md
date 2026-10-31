---
title: std::chrono::get_leap_second_info
summary: "ある UTC の時点が、うるう秒の中か、それまでに何秒入ったかを調べる。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::get_leap_second_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`utc_time` が、うるう秒の最中（23:59:60）なのか、そこまでに挿入された秒数はいくつか。それを調べるのが `std::chrono::get_leap_second_info` です。`utc_time` を `sys_time` に直すときに失われる情報を、別に取り出せます。

!!! tip "ポイント"
    - `utc_time` を渡すと、`is_leap_second` と `elapsed` を持つ構造体が返る
    - `is_leap_second` は、その時点がうるう秒の中なら真
    - `elapsed` は、その時点までに挿入されたうるう秒の累計
    - `sys_time` に直す前に呼ぶと、うるう秒の情報を残せる

!!! info "このページを読む前に"
    [`utc_clock`](utc_clock.md) と [`leap_second`](leap_second.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::get_leap_second_info {#get_leap_second_info}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
leap_second_info get_leap_second_info(const utc_time<Duration>& ut);

struct leap_second_info {
  bool is_leap_second;
  seconds elapsed;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ut` | `utc_time<Duration>` | 調べる UTC の時点 |

`is_leap_second` は、`ut` がうるう秒の 1 秒の中にあるときに真です。その 1 秒の間だけ、23:59:60 が現れます。

`elapsed` は、`ut` までに入ったうるう秒の合計です。2026 年の時点では 27 秒です。うるう秒の最中の場合は、その秒を含めた累計になります。

`utc_time` を `sys_time` に直すと、うるう秒の最中は、直前の秒にまとめられるので、情報が失われます。変換の前に呼んで、必要なら結果を別に保存します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 普通の時刻
  const utc_seconds normal = clock_cast<utc_clock>(sys_seconds{sys_days{2026y / January / 1}});
  const leap_second_info a = get_leap_second_info(normal);
  std::println("2026-01-01: うるう秒の中={} 累計={} 秒", a.is_leap_second, a.elapsed.count());

  // 2016-12-31 23:59:59 の 1 秒後は、うるう秒 23:59:60
  const sys_seconds last = sys_days{2016y / December / 31} + 23h + 59min + 59s;
  const utc_seconds leap = clock_cast<utc_clock>(last) + 1s;
  const leap_second_info b = get_leap_second_info(leap);
  std::println("23:59:60: うるう秒の中={} 累計={} 秒", b.is_leap_second, b.elapsed.count());
}
```

```text title="実行結果"
2026-01-01: うるう秒の中=false 累計=27 秒
23:59:60: うるう秒の中=true 累計=27 秒
```

2016 年末のうるう秒は 27 回目で、その最中の `elapsed` は 27 秒です。

## ゲームでの使いどころ

使いません。

## よくあるミス

??? failure "sys_time に直したあとで調べようとする"
    うるう秒の情報は失われています。`utc_time` のうちに調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`leap_second`](leap_second.md) | うるう秒 1 件の情報 |
| [`utc_clock`](utc_clock.md) | うるう秒を数える時計 |
| [`clock_cast`](clock_cast.md) | 時計どうしを変換する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: get_leap_second_info](https://cpprefjp.github.io/reference/chrono/get_leap_second_info.html)
- [cppreference: std::chrono::get_leap_second_info](https://en.cppreference.com/w/cpp/chrono/get_leap_second_info)
