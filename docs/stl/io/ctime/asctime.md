---
title: std::asctime
summary: "tm を、決まった形の文字列にする。"
order: 900
tags:
  - 入出力・文字列
---

# std::asctime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`tm` を、`Thu Jan  1 00:00:00 2026` のような英語の決まった形に整える関数です。末尾に改行が付いてきます。書式を選べないうえ、結果を静的な領域に置くため、現在では `strftime` や `std::format` に置き換えるのが普通です。C23 では非推奨になっています。古いコードを読むときのために、挙動だけ知っておきます。

!!! tip "ポイント"
    - 形は固定: `曜日 月 日 時:分:秒 年` と、末尾の改行（全体で 25 文字）
    - 日の前は、1 桁のとき空白で埋まる（`Jan  1`）
    - 結果は静的な領域を指す。次の呼び出しで上書きされる
    - 書式を変えたいときや安全に使いたいときは `strftime`

!!! info "このページを読む前に"
    [`std::tm`](tm.md) と [`std::strftime`](strftime.md) を先に読んでください。

## 関数の詳しい説明

### std::asctime {#asctime}

```cpp
char* asctime(const std::tm* time_ptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time_ptr` | `const std::tm*` | 文字列にする日時 |

戻り値は、静的な領域にある文字列へのポインタです。内容は、`Thu Jan  1 00:00:00 2026\n` のように、曜日の略称、月の略称、日（2 桁、1 桁のときは前が空白）、時刻、年（4 桁）と、末尾の改行です。曜日と月は、ロケールにかかわらず常に英語です。

`tm_year` が 9999 年を超えるなど、年が 4 桁に収まらないときは、未定義動作です。`tm` のフィールドが範囲外のときも同じです。

静的な領域を共有するため、`ctime` と同じバッファを使っている環境があり、片方を呼ぶと、もう片方の結果が上書きされます。スレッドからの呼び出しにも向きません。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <ctime>
#include <print>

int main() {
  const std::time_t t = 1767225600;  // 2026-01-01 00:00:00 UTC
  const std::tm utc = *std::gmtime(&t);

  const char* text = std::asctime(&utc);
  std::println("{:?}", text);
  std::println("文字数: {}", std::strlen(text));
}
```

```text title="実行結果"
"Thu Jan  1 00:00:00 2026\n"
文字数: 25
```

`{:?}` で表示すると、末尾の `\n` が見えます。日の前に空白が 2 つ並んでいるのは、1 桁の日を右に揃えるためです。

## ゲームでの使いどころ

使う場面はありません。古い C のコードで、ログに日時を出すために、`printf("%s", asctime(...))` と書かれているのを見かけます。末尾の改行が付くので、その後ろで改行しなくても、行が変わります。

置き換えるなら、`strftime` で自分の書式を決めます。

## よくあるミス

??? failure "末尾の改行を知らずに、二重に改行する"
    戻り値の文字列に `\n` が含まれます。`printf("%s\n", asctime(...))` と書くと、空行が入ります。

??? failure "戻り値のポインタを保存する"
    静的な領域なので、次の呼び出しで上書きされます。文字列は `std::string` にコピーして持ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ctime`](ctime.md) | `time_t` から直接、ローカル時刻の同じ形の文字列にする |
| [`strftime`](strftime.md) | 書式を自分で決められる。普段はこちら |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。MSVC は、`asctime` を使うと警告（C4996）を出すことがあります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `asctime` は、固定の形（25 文字、末尾に改行）の文字列にする
    - [x] 静的な領域を使うので、スレッドに向かない
    - [x] 新しいコードは `strftime`

## 関連ページ

- [cpprefjp: std::asctime](https://cpprefjp.github.io/reference/ctime/asctime.html)
- [cppreference: std::asctime](https://en.cppreference.com/w/cpp/chrono/c/asctime)
