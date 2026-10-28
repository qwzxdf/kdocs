---
title: std::filesystem::file_time_type
summary: "ファイルの更新時刻を表す型。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::file_time_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ファイルの更新時刻を、前回のビルドと比べて「新しくなったか」を判定したい。ところが、`last_write_time` が返す時刻の型は、`std::chrono::system_clock` ではありません。`std::filesystem::file_time_type` という、ファイルシステム専用の時刻の型です。

この型は、`std::chrono::time_point` の別名です。<strong>ファイルシステムの時刻専用の時計</strong>（`std::filesystem::__file_clock`、C++20 以降は `std::chrono::file_clock`）を使います。

!!! tip "ポイント"
    - `last_write_time` が返す型。`std::chrono::time_point` の別名
    - 比較（`<`, `>`, `==`）と、差の計算（`-`）は、そのまま使える
    - `system_clock` とは別の時計。日時として表示するには変換が要る（C++20 は `clock_cast`）
    - 時計の起点（エポック）は実装しだい。数値として他の環境と比べない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### file_time_type {#file_time_type}

<span class="ver ver-17">C++17</span>

```cpp
using file_time_type = std::chrono::time_point<std::chrono::file_clock>;   // C++20 以降。C++17 では実装定義の時計
```

C++17 では、`file_time_type` が使う時計の名前は規定されていませんでした（`trivial-clock` として実装定義）。C++20 で、`std::chrono::file_clock` が標準になり、`system_clock` や `utc_clock` との変換（`clock_cast`）も、可能になりました。

比較と差の計算は、普通の `time_point` として行えます。2 つのファイルの更新時刻を比べて新しい方を選ぶ、現在時刻との差を求める、といった処理には、変換が要りません。

人が読む日時に直す場合は、`system_clock` に変換します。C++20 以降なら `std::chrono::clock_cast<std::chrono::system_clock>(ft)` です。C++17 までは、この変換に標準の方法がありませんでした。

時計のエポック（起点）は、実装ごとに違います。MSVC は Windows のファイル時刻にそろえて 1601 年 1 月 1 日が起点ですが、他の実装では違います。<strong>`time_since_epoch().count()` の数値を、環境をまたいで比べてはいけません</strong>。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("old.txt") << "x";
  std::ofstream("new.txt") << "x";

  // old.txt を、1 時間前の時刻にする
  fs::file_time_type now = fs::file_time_type::clock::now();
  fs::last_write_time("old.txt", now - std::chrono::hours(1));

  fs::file_time_type t_old = fs::last_write_time("old.txt");
  fs::file_time_type t_new = fs::last_write_time("new.txt");

  // 比較と差の計算は、そのまま使える
  std::println("new.txt のほうが新しい: {}", t_new > t_old);
  auto diff = std::chrono::duration_cast<std::chrono::minutes>(t_new - t_old);
  std::println("約 {} 分以上の差", diff.count() >= 59 ? 59 : diff.count());
}
```

```text title="実行結果"
new.txt のほうが新しい: true
約 59 分以上の差
```

## ゲームでの使いどころ

ホット リロードや、ビルド システムで、「ソースがアセットより新しいか」を判定するときに使います。`last_write_time(src) > last_write_time(asset)` と書けば、変換なしで比べられます。

更新時刻をログに出すときは、`clock_cast` で `system_clock` に直してから、`std::format("{}", ...)` に渡します。数値のまま出さないようにします。

## よくあるミス

??? failure "`file_time_type` と `system_clock::time_point` を直接比べて、コンパイル エラー"
    別の時計の `time_point` は、比べられません。`clock_cast` で時計をそろえます。

??? failure "`time_since_epoch().count()` の数値を、保存して別の環境で使う"
    エポックが実装ごとに違うので、数値に意味がありません。保存するなら、`system_clock` に直した UTC の時刻にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`last_write_time`](last_write_time.md) | この型の時刻を読み書きする関数 |
| `std::chrono::system_clock` | カレンダー時刻に使う時計。変換が要る |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルシステム専用の時刻の型
    - [x] 比較と差の計算はそのまま
    - [x] 数値のエポックは環境ごとに違う

## 関連ページ

- [cpprefjp: std::filesystem::file_time_type](https://cpprefjp.github.io/reference/filesystem/file_time_type.html)
- [cppreference: std::filesystem::file_time_type](https://en.cppreference.com/w/cpp/filesystem/file_time_type)
