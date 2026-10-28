---
title: std::tmpfile
summary: "自動で消える一時ファイルを作る。"
order: 900
tags:
  - 入出力・文字列
---

# std::tmpfile

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ちょっとした作業用に、一時ファイルが欲しい。名前を考えるのも、後で消すのも、面倒です。`std::tmpfile` は、<strong>一時ファイルを作って、開いた状態の `FILE*` を返し、閉じたら自動で消えます</strong>。

!!! tip "ポイント"
    - 戻り値は、読み書き兼用（`"wb+"`）で開かれた `FILE*`。失敗は `nullptr`
    - 名前は分からない。閉じるか、プログラムが終わると、自動で消える
    - 名前を付けて保存したいときには向かない
    - Windows では、ルート直下に作ろうとして権限エラーになる環境がある

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::tmpfile {#tmpfile}

```cpp
std::FILE* tmpfile();
```

引数はありません。システムが決めた、重複しない名前で、一時ファイルを作り、バイナリの読み書き兼用で開いて返します。作れなかったときは `nullptr` です。

戻り値の `FILE*` を `fclose` すると、ファイルは自動で削除されます。プログラムが正常に終了したときも、削除されます。異常終了すると、削除されずに残る環境があります。

ファイルの名前を取得する方法は、標準にはありません。別のプログラムに渡したい、あとで名前で開き直したい、という用途には向きません。その場合は、名前を自分で決めて、`std::filesystem::temp_directory_path` に作ります。

Windows の古い MSVC では、`tmpfile` が、ドライブのルート（`C:\`）に作ろうとして、管理者権限がないと失敗することがありました。新しい処理系は改善されていますが、`nullptr` の確認は欠かせません。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* tmp = std::tmpfile();
  if (!tmp) {
    std::println("作れなかった");
    return 1;
  }
  std::fputs("work data", tmp);

  std::rewind(tmp);                        // 書いたあと、先頭に戻って読む
  char buf[32];
  std::fgets(buf, sizeof(buf), tmp);
  std::println("読み戻した: {}", buf);

  std::fclose(tmp);                        // 閉じると自動で消える
}
```

```text title="実行結果"
読み戻した: work data
```

## ゲームでの使いどころ

計算の途中結果を、メモリに入りきらないときの逃がし場所として使います。たとえば、大きなデータを並べ替えるときの、外部ソートの作業ファイルです。

名前を付けて残したいデータには使いません。ダウンロード中のファイルの一時保存のように、あとで別のプログラムに渡す用途には、`temp_directory_path` に名前を決めて作ります。

## よくあるミス

??? failure "`nullptr` を確かめずに使う"
    権限やディスクの空きで失敗します。必ず確かめます。

??? failure "名前を知りたくなって、困る"
    標準では取得できません。名前が要るなら、`std::filesystem::temp_directory_path()` に自分で名前を決めて作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tmpnam`](tmpnam.md) | 一時ファイルの名前だけを作る。競合に弱く、非推奨に近い |
| [`temp_directory_path`](../filesystem/temp_directory_path.md) | OS の一時フォルダーの場所 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自動で消える一時ファイルを開く
    - [x] 名前は分からない
    - [x] `nullptr` を確かめる

## 関連ページ

- [cpprefjp: std::tmpfile](https://cpprefjp.github.io/reference/cstdio/tmpfile.html)
- [cppreference: std::tmpfile](https://en.cppreference.com/w/cpp/io/c/tmpfile)
