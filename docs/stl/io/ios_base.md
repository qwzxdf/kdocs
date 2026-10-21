---
title: std::ios_base
summary: "ストリームの状態と、開き方・書式のフラグをまとめた土台のクラス。"
order: 68
tags:
  - 入出力・文字列
---

# std::ios_base

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

`std::ios_base` は、**すべての入出力ストリームの土台**となるクラスです。ファイルの開き方（`openmode`）、位置の基準（`seekdir`）、書式のフラグ（`fmtflags`）、状態（`iostate`）の定数を持っています。`std::ios::in` や `std::ios::binary` と書くのは、この中の定数です。

!!! tip "ポイント"
    - ファイルを開くときのフラグ: `std::ios::in` `out` `binary` `app` `trunc` `ate`。
    - 状態の確認: `good()` `eof()` `fail()` `bad()`。`if (stream)` は `!fail()` と同じ。
    - 位置の基準: `std::ios::beg` `cur` `end`。

## 開き方（openmode）

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `std::ios::in` | <span class="rank rank-must">必須</span> | 読み込み（ifstream のデフォルト） |
| `std::ios::out` | <span class="rank rank-must">必須</span> | 書き込み（ofstream のデフォルト。中身は消える） |
| `std::ios::binary` | <span class="rank rank-must">必須</span> | バイナリ。改行コードを変換しない |
| `std::ios::app` | <span class="rank rank-often">よく使う</span> | 必ず末尾に追記する |
| `std::ios::trunc` | <span class="rank rank-sometimes">たまに</span> | 開くときに中身を消す |
| `std::ios::ate` | <span class="rank rank-rare">知ってるだけ</span> | 開いた直後に末尾へ移動（その後は好きな場所に書ける） |
| `std::ios::noreplace` | <span class="rank rank-rare">知ってるだけ</span> | すでにファイルがあれば開くのに失敗する <span class="ver ver-23">C++23</span> |

## 位置の基準（seekdir）

| 値 | 意味 |
| --- | --- |
| `std::ios::beg` | 先頭から |
| `std::ios::cur` | 今の位置から |
| `std::ios::end` | 末尾から |

## 状態（iostate）

| 値 | 意味 | 調べる関数 |
| --- | --- | --- |
| `goodbit` | 問題なし | `good()` |
| `eofbit` | 終わりまで読んだ | `eof()` |
| `failbit` | 読み取り・変換に失敗した（数字の所に文字があった、など） | `fail()` |
| `badbit` | 読み書きそのものができない深刻なエラー | `bad()` |

## 関数の詳しい説明

### 状態の確認と復帰 {#state}

```cpp
bool good() const;   // 問題なし
bool eof() const;    // 終わりまで読んだ
bool fail() const;   // 失敗した（failbit か badbit）
bool bad() const;    // 深刻なエラー
void clear();        // エラー状態を消す
```

```cpp
#include <print>
#include <sstream>

int main() {
  std::istringstream in("12 abc");
  int a = 0;
  int b = 0;

  in >> a;                         // 12 を読む
  std::println("a={} fail={}", a, in.fail());

  in >> b;                         // "abc" は数字でない
  std::println("fail={}", in.fail());

  in.clear();                      // エラー状態を消す（読み取れなかった文字は残っている）
  std::println("fail={}", in.fail());
}
```

```text title="実行結果"
a=12 fail=false
fail=true
fail=false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| バイナリで書き出す | `std::ofstream out(path, std::ios::binary);` |
| 読み込みの失敗を調べる | `if (in.fail()) ...` |

## よくあるミス

??? failure "eof で終わりを判断する"
    `eof()` は「読もうとして終わりだった」ときに初めて真になります。読む前に `while (!in.eof())` と書くと、最後に余分に回ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ifstream`](ifstream.md) / [`std::ofstream`](ofstream.md) | フラグを渡して使う |
| [`std::cout`](cout.md) | 書式フラグを使う |

## コンパイラ対応

C++98 から使えます。`std::ios::noreplace` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームの定数と状態の土台
    - [x] 開き方は `in` `out` `binary` `app`
    - [x] 状態は `good` `eof` `fail` `bad`

## 関連ページ

- [cpprefjp: std::ios_base](https://cpprefjp.github.io/reference/ios/ios_base.html)
- [cppreference: std::ios_base](https://en.cppreference.com/w/cpp/io/ios_base)
