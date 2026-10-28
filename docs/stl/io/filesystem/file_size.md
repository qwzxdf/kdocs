---
title: std::filesystem::file_size
summary: "ファイルの大きさ（バイト数）を取得する。"
order: 13
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::file_size

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ファイルを丸ごと読み込むために、先に大きさを知って、その分のバッファーを確保したい。ダウンロードの進み具合を、保存されたファイルの大きさから計算したい。ファイルを開いて `seekg` するよりも、手軽に大きさを知る方法が `std::filesystem::file_size` です。

<strong>通常のファイルのバイト数</strong>を返します。

!!! tip "ポイント"
    - 戻り値は `std::uintmax_t`（符号なしの大きな整数）
    - 存在しないパスはエラー。フォルダーに使った結果は、実装によって違う（エラーになる環境も、値が返る環境もある）
    - リンクは先をたどった、実体のファイルの大きさ
    - ファイルを書いている途中は、書き込み済みの量とずれることがある（バッファーのため）

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### file_size {#file_size}

<span class="ver ver-17">C++17</span>

```cpp
std::uintmax_t file_size(const path& p);
std::uintmax_t file_size(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 大きさを調べるファイル |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値の型 `std::uintmax_t` は、最も大きな符号なし整数型なので、4 GB を超えるファイルでも扱えます。`int` に代入すると、2 GB を超えたところで壊れるので、`std::size_t` や `std::uintmax_t` で受けます。

存在しないパスに使うと、例外（または `ec` のエラー）になります。標準はフォルダーなど通常のファイルでないものもエラーとしていますが、手元の MSVC ではエラーにならず、値が返りました。フォルダーには使わないようにします。`error_code` を渡す版は、エラーのときに `static_cast<std::uintmax_t>(-1)` を返します。<strong>この値を、そのまま大きさとして使わない</strong>ようにします。

ファイルのバッファーに、まだ書き込まれていないデータがあると、実際に書いた量より小さい値になります。確実に調べたいときは、ストリームを `flush` するか閉じてから呼びます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  {
    std::ofstream out("data.bin", std::ios::binary);
    out << "0123456789";
  }
  std::println("data.bin: {} バイト", fs::file_size("data.bin"));

  // 存在しないパスは、エラーになる
  std::error_code ec;
  auto size = fs::file_size("missing.bin", ec);
  std::println("存在しない: エラー={} 戻り値は最大値={}", static_cast<bool>(ec),
               size == static_cast<std::uintmax_t>(-1));
}
```

```text title="実行結果"
data.bin: 10 バイト
存在しない: エラー=true 戻り値は最大値=true
```

## ゲームでの使いどころ

ファイルを丸ごと読み込むときの、バッファーの確保に使います。`std::vector<char> buf(fs::file_size(path))` で、ちょうどの大きさを用意して、`read` で一気に読み込みます。

ダウンロードの進行状況の表示や、セーブ データが空（0 バイト）でないかの確認、キャッシュ フォルダーの合計サイズの計算にも使います。合計サイズは、フォルダーを走査して、通常のファイルの `file_size` を足し上げます。

## よくあるミス

??? failure "フォルダーに使って、フォルダー全体の大きさだと思う"
    この関数は、フォルダーの中身の合計を返しません。環境によっては、エラーや、意味のない値になります。中のファイルを走査して足し合わせます。

??? failure "`int` で受けて、大きなファイルで負の値になる"
    `std::uintmax_t` で受けます。`size_t` に直すときも、範囲を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`space`](space.md) | ボリュームの空き容量 |
| [`resize_file`](resize_file.md) | ファイルの大きさを変更する |
| [`is_empty`](is_empty.md) | 空かどうかだけを調べる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 通常のファイルのバイト数を返す
    - [x] `uintmax_t` で受ける
    - [x] フォルダーにはエラー

## 関連ページ

- [cpprefjp: std::filesystem::file_size](https://cpprefjp.github.io/reference/filesystem/file_size.html)
- [cppreference: std::filesystem::file_size](https://en.cppreference.com/w/cpp/filesystem/file_size)
