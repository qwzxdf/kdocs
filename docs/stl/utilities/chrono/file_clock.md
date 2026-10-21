---
title: std::chrono::file_clock
summary: "ファイルの更新日時に使われる時計。"
order: 12
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::file_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::file_clock` は、**ファイルシステムの更新日時（`std::filesystem::last_write_time`）で使われる時計**です。`system_clock` とは基準時刻が違うことがあるので、日時として表示したり比べたりするときは、`std::chrono::clock_cast` で変換します。

!!! tip "ポイント"
    - `std::filesystem::file_time_type` は、`file_clock` の時点。
    - `system_clock` に変換するには `std::chrono::clock_cast<std::chrono::system_clock>(ft)`（C++20）。
    - ファイルの更新を検出するだけなら、変換せずに時点どうしを比べればよい。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::chrono::file_clock {#file_clock}

```cpp
struct file_clock {
  using time_point = std::chrono::time_point<file_clock>;
  static time_point now() noexcept;
};
```

- 戻り値: `now()` は今の時点
- 計算量: O(1)

```cpp
#include <chrono>
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  using namespace std::chrono;

  // ファイルの更新日時を、system_clock に変換して表示する例
  auto ft = fs::last_write_time("main.cpp");
  auto st = clock_cast<system_clock>(ft);
  std::println("{:%F %T}", floor<seconds>(st));
}
```

```text title="実行結果"
（ファイルの更新日時によって変わります）
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アセットの更新日時を比べる（ホットリロード） | `last_write_time(path)` を保存して、時点どうしを比べる |
| ファイルの更新日時をログに出す | `clock_cast` で `system_clock` へ |

## よくあるミス

??? failure "file_clock と system_clock を直接比べる"
    型が違うのでコンパイルエラーです。`clock_cast` で変換します。

??? failure "古い環境で clock_cast が無い"
    C++20 の機能です。使えないときは、`time_since_epoch()` の差を調べる、ファイル更新の比較だけに使う、などで代用します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | 現実の日時 |
| [`std::filesystem`](../../io/filesystem.md) | ファイル操作 |

## コンパイラ対応

C++20 の機能です。GCC 13 / MSVC 19.29 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの更新日時の時計
    - [x] 日時にしたいなら `clock_cast`
    - [x] 更新の比較だけなら変換不要

## 関連ページ

- [cpprefjp: std::chrono::file_clock](https://cpprefjp.github.io/reference/chrono/file_clock.html)
- [cppreference: std::chrono::file_clock](https://en.cppreference.com/w/cpp/chrono/file_clock)
