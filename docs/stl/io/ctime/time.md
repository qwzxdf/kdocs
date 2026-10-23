---
title: std::time
summary: "現在時刻を、1970 年からの秒数で取得する（C 由来）。"
order: 1
group: 時刻（<ctime>）
tags:
  - 入出力・文字列
---

# std::time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ctime>`
</div>

`std::time(nullptr)` は、**現在の時刻を、1970-01-01 00:00:00 UTC からの秒数で返す**C 由来の関数です。乱数の種や、ファイル名に使う時刻の取得に使われます。C++ では [`std::chrono::system_clock`](../../utilities/chrono/system_clock.md) が型安全です。

!!! tip "ポイント"
    - 戻り値は `time_t`（秒）。
    - 秒の精度しかない。
    - 新しいコードでは `chrono`。

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::time {#time}

```cpp
std::time_t time(std::time_t* t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | `time_t*` | 結果の書き込み先（`nullptr` 可） |

- 戻り値: 現在時刻（秒）
- 計算量: O(1)

```cpp
#include <ctime>
#include <print>

int main() {
  std::time_t now = std::time(nullptr);
  std::println("{}", now > 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードの読解 | `system_clock::now()` に置き換える |

## よくあるミス

??? failure "乱数の種に使う"
    1 秒以内に 2 回起動すると同じ種になります。`random_device` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::chrono::system_clock`](../../utilities/chrono/system_clock.md) | C++ の時計 |
| [`gmtime`](gmtime.md) | 年月日に分解 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在時刻を秒で取る
    - [x] 秒の精度
    - [x] 新しいコードは chrono

## 関連ページ

- [cpprefjp: std::time](https://cpprefjp.github.io/reference/ctime/time.html)
- [cppreference: std::time](https://en.cppreference.com/w/cpp/chrono/c/time)
