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

アセットを最後に更新した時刻を調べて、ビルドの必要があるかを判断したい。セーブ データの一覧を、新しい順に並べたい。ファイルの「最後に書き込まれた時刻」を取得する関数が `std::filesystem::last_write_time` で、同じ名前で時刻の設定もできます。

!!! tip "ポイント"
    - 引数を 1 つ渡すと取得、時刻も渡すと設定
    - 時刻の型は [`file_time_type`](file_time_type.md)。`system_clock` とは別の時計
    - 新しさの比較（`<`、`>`）や、時間差の計算は、そのまま行える
    - 人が読む日時に直すには、`clock_cast`（C++20）で `system_clock` に変換する

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### last_write_time {#last_write_time}

<span class="ver ver-17">C++17</span>

```cpp
file_time_type last_write_time(const path& p);
file_time_type last_write_time(const path& p, std::error_code& ec) noexcept;
void last_write_time(const path& p, file_time_type new_time);
void last_write_time(const path& p, file_time_type new_time, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 対象のファイルまたはフォルダー |
| `new_time` | `file_time_type` | 設定する時刻 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

取得する版は、`file_time_type` を返します。ファイルが存在しない、権限がない、といったときは、例外（または `ec`）です。

設定する版は、ファイルの内容を変えずに、更新時刻だけを書き換えます。ビルド システムが、「この出力は、この入力より新しい」と見せかけたいときや、テストで古いファイルを用意したいときに使います。

返ってくる時刻の精度は、ファイルシステムによって違います（NTFS は 100 ナノ秒、FAT は 2 秒など）。書き込んだ時刻と、すぐ読み取った時刻が、丸められて少し違うことがあります。<strong>等しいかどうかで比べず</strong>、大小や、ある幅の差で比べます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("shader.hlsl") << "x";
  std::ofstream("shader.cso") << "x";

  // ソース（hlsl）のほうを新しい時刻にして、「再コンパイルが必要」を作る
  auto now = fs::file_time_type::clock::now();
  fs::last_write_time("shader.cso", now - std::chrono::hours(2));
  fs::last_write_time("shader.hlsl", now);

  bool need_rebuild = fs::last_write_time("shader.hlsl") > fs::last_write_time("shader.cso");
  std::println("再コンパイルが必要: {}", need_rebuild);

  // 出力のほうを新しくすると、不要になる
  fs::last_write_time("shader.cso", now + std::chrono::minutes(1));
  need_rebuild = fs::last_write_time("shader.hlsl") > fs::last_write_time("shader.cso");
  std::println("更新後は不要: {}", !need_rebuild);
}
```

```text title="実行結果"
再コンパイルが必要: true
更新後は不要: true
```

## ゲームでの使いどころ

ビルド パイプラインやホット リロードで、「元のファイルが、生成物より新しいか」を判定します。シェーダー、テクスチャ、モデルを、変更されたものだけ再変換する仕組みの基本です。

ゲーム内のセーブ データ一覧では、各ファイルの更新時刻を取得して、新しい順に並べ、「最終プレイ日時」として表示します。表示するときは、`system_clock` に直してから書式化します。

## よくあるミス

??? failure "`==` で更新時刻の一致を判定して、環境によって外れる"
    精度や丸めの違いで、書いた値と読んだ値がぴったり一致するとは限りません。大小で比べます。

??? failure "`file_time_type` を `system_clock::time_point` と直接比べて、コンパイル エラー"
    時計が違うので、そのままでは比べられません。`clock_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_time_type`](file_time_type.md) | この関数が使う時刻の型 |
| [`directory_entry`](directory_entry.md) | 走査の途中で更新時刻を持っている |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最後に書き込まれた時刻の取得と設定
    - [x] 型は `file_time_type`
    - [x] `==` ではなく大小で比べる

## 関連ページ

- [cpprefjp: std::filesystem::last_write_time](https://cpprefjp.github.io/reference/filesystem/last_write_time.html)
- [cppreference: std::filesystem::last_write_time](https://en.cppreference.com/w/cpp/filesystem/last_write_time)
