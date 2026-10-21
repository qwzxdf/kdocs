---
title: std::fstream
summary: "同じファイルを、読んだり書いたりできる型。"
order: 67
tags:
  - 入出力・文字列
---

# std::fstream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <fstream>`
</div>

`std::fstream` は、**1 つのファイルを読むことも書くこともできる**型です。[`ifstream`](ifstream.md) と [`ofstream`](ofstream.md) の両方の機能を持ちます。ファイルの途中を書き換えるときなどに使いますが、普通は読むだけ・書くだけなので、専用の型で足ります。

!!! tip "ポイント"
    - 開くときに、`std::ios::in | std::ios::out` と、両方のモードを指定する。
    - 読む位置（`seekg`）と書く位置（`seekp`）は、実際には同じ位置を共有する。読み書きの切り替えには `seekg` / `seekp` を挟む。
    - 普通は `ifstream` / `ofstream` で十分。

!!! info "このページを読む前に"
    [ファイル入出力](../../basics/file-io.md) に入門があります。パスの扱いは [`std::filesystem`](filesystem.md) を見てください。

## 関数の詳しい説明

### std::fstream {#fstream}

```cpp
class fstream {
 public:
  explicit fstream(const std::filesystem::path& path,
                   std::ios::openmode mode = std::ios::in | std::ios::out);
};
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `path` | `path` | 開くファイル |  |
| `mode` | `openmode` | 開き方（読み書き両方を指定する） | `in | out` |

- 戻り値: （クラス）。`ifstream` と `ofstream` の操作がどちらも使える
- 計算量: ファイル操作による

```cpp
#include <fstream>
#include <print>
#include <string>

int main() {
  // 書いて、同じストリームで読み戻す（一時ファイルを作る）
  std::fstream io("fstream_demo.txt", std::ios::in | std::ios::out | std::ios::trunc);
  io << "hello";
  io.seekg(0);  // 書いた後に読むので、先頭に戻す

  std::string s;
  io >> s;
  std::println("{}", s);
}
```

```text title="実行結果"
hello
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの途中の数値だけを書き換える | `io.seekp(offset); io.write(...)` |

## よくあるミス

??? failure "読みと書きの切り替えで seek を忘れる"
    読みから書き、書きから読みに切り替えるときは、必ず `seekg` / `seekp`（または `flush`）を挟みます。標準で決まっています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ifstream`](ifstream.md) | 読むだけ |
| [`std::ofstream`](ofstream.md) | 書くだけ |
| [`std::ios_base`](ios_base.md) | 開き方のフラグ |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読み書き両方できる
    - [x] 切り替えには seek を挟む
    - [x] 普通は ifstream / ofstream

## 関連ページ

- [cpprefjp: std::fstream](https://cpprefjp.github.io/reference/fstream/basic_fstream.html)
- [cppreference: std::basic_fstream](https://en.cppreference.com/w/cpp/io/basic_fstream)
