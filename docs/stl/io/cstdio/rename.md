---
title: std::rename
summary: "ファイルの名前を変える（移動もできる）。"
order: 900
tags:
  - 入出力・文字列
---

# std::rename

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

セーブ データを書き込んでいる最中に、クラッシュすると、壊れたファイルが残ってしまいます。そこで、いったん別の名前の一時ファイルに書いて、最後に本物の名前へ付け替える、という方法があります。この付け替えに使うのが `std::rename` です。

<strong>ファイルの名前を変える</strong>（または場所を移す）関数です。

!!! tip "ポイント"
    - `rename("旧", "新")` で、名前を変える。成功は 0、失敗は 0 以外
    - 新しい名前のファイルがすでにあるときの動きは、環境による（Windows は失敗、POSIX は置き換え）
    - 同じボリューム内なら、ふつう一瞬で終わる。別ボリュームへは失敗することがある
    - 安全に書き換えたいときは、一時ファイルに書いてから `rename` する

!!! info "このページを読む前に"
    [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::rename {#rename}

```cpp
int rename(const char* old_filename, const char* new_filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `old_filename` | `const char*` | 今の名前（パス） |
| `new_filename` | `const char*` | 新しい名前（パス） |

成功すれば 0 を返します。失敗すると 0 以外を返し、`errno` に理由が入ります。ファイルが存在しない、権限がない、といった理由のほかに、<strong>新しい名前のファイルがすでにある</strong>場合の扱いが、環境で違うことに注意します。

規格は、この場合の動作を実装定義としています。Windows の MSVC では失敗しますが、Linux などでは、既存のファイルを置き換えます。どちらの環境でも同じ動きにしたいなら、`std::filesystem::rename`（ここも似た違いがある）や、先に新しい名前を `remove` しておく、という手順を取ります。

セーブ データの安全な書き換えは、「一時ファイルに全部書く」「閉じる」「元のファイルを消す」「一時ファイルを `rename` する」の順です。途中でクラッシュしても、元のファイルか、新しい完全なファイルのどちらかが残ります。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("tmp_save.dat", "w");
  std::fputs("SAVE", f);
  std::fclose(f);

  std::remove("save.dat");                          // 前のファイルがあれば消す
  int r = std::rename("tmp_save.dat", "save.dat");  // 完成したので付け替える
  std::println("付け替えた: {}", r == 0);

  std::FILE* in = std::fopen("save.dat", "r");
  char buf[16];
  std::fgets(buf, sizeof(buf), in);
  std::println("中身: {}", buf);
  std::fclose(in);
}
```

```text title="実行結果"
付け替えた: true
中身: SAVE
```

## ゲームでの使いどころ

セーブ データの安全な保存に使います。壊れたセーブ ファイルは、プレイヤーにとって最悪の不具合の 1 つなので、一時ファイルに書いて付け替える手順は、必ず取り入れたい方法です。

古いセーブを残したいなら、本物の名前を `.bak` に `rename` で退避させてから、新しいファイルを付け替えます。

## よくあるミス

??? failure "新しい名前がすでにあって、環境ごとに結果が違う"
    Windows は失敗し、Linux は置き換えます。先に `remove` しておくなど、そろえる手順を入れます。

??? failure "開いたままのファイルを `rename` して、失敗する"
    閉じてから付け替えます。

??? failure "別のドライブへ移そうとして失敗する"
    同じボリュームの中でしか動かないことがあります。別ドライブへは、コピーしてから消します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove`](remove.md) | ファイルを消す |
| [`std::filesystem::rename`](../filesystem/rename.md) | C++17 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 名前を変える（移す）
    - [x] 新しい名前が既存だと環境で違う
    - [x] 安全な保存の最後の手順に使う

## 関連ページ

- [cpprefjp: std::rename](https://cpprefjp.github.io/reference/cstdio/rename.html)
- [cppreference: std::rename](https://en.cppreference.com/w/cpp/io/c/rename)
