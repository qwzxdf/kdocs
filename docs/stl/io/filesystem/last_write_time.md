---
title: std::filesystem::last_write_time
summary: "ファイルの最終更新日時を取得する。"
order: 17
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::last_write_time

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

アセットのファイルが更新されたら、ゲームを再起動せずに読み直したい（ホットリロード）。そのためには、ファイルの最終更新日時が要ります。`std::filesystem::last_write_time` は、ファイルの最終更新日時を返す関数です。前回の値と比べるだけなら、変換は不要です。

!!! tip "ポイント"
    - 戻り値は `file_time_type`（[`file_clock`](../../utilities/chrono/file_clock.md) の時点）。
    - 前回の値と比べるだけなら、変換不要。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### last_write_time {#last_write_time}

```cpp
file_time_type last_write_time(const path& p);
```

- 最終更新日時。前回と比べて変わっていたら読み込み直す（ホットリロード）のに使えます

```cpp
#include <chrono>
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("shader.txt") << "v1";
  auto before = fs::last_write_time("shader.txt");
  fs::last_write_time("shader.txt", before + std::chrono::seconds(5));  // 書き換えたとする
  std::println("更新された？ {}", fs::last_write_time("shader.txt") != before);
}
```

```text title="実行結果"
更新された？ true
```

## ゲームでの使いどころ

ホットリロードの実装に使います。アセットを読み込んだ時点の更新日時を覚えておき、毎秒1回程度 `last_write_time` を取って、変わっていれば読み直します。毎フレーム調べると、ファイルシステムへの問い合わせが多くなるので、間隔をあけます。

セーブデータの新しさの比較にも使えます。2 つのセーブデータの更新日時を比べて、新しいほうを選ぶ、という処理です。

戻り値は `file_time_type`（`file_clock` の時点）です。日時として表示するには、`system_clock` の時点に変換します。C++20 では `clock_cast` を使います。

## よくあるミス

??? failure "system_clock と直接比べる"
    型が違います。`clock_cast` で変換します。

??? failure "毎フレーム呼んで重くなる"
    ファイルシステムへの問い合わせは、フレームごとに行うと負担になります。1 秒に 1 回程度に間引きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_clock`](../../utilities/chrono/file_clock.md) | 時計の型 |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最終更新日時
    - [x] 前回と比べて更新を検出
    - [x] 日時にするなら clock_cast

## 関連ページ

- [cpprefjp: std::filesystem::last_write_time](https://cpprefjp.github.io/reference/filesystem/last_write_time.html)
- [cppreference: std::filesystem::last_write_time](https://en.cppreference.com/w/cpp/filesystem/last_write_time)
