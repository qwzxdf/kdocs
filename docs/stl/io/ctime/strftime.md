---
title: std::strftime
summary: "日時を、書式に従った文字列にする（C 由来）。"
order: 3
group: 時刻（<ctime>）
tags:
  - 入出力・文字列
---

# std::strftime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ctime>`
</div>

セーブデータのファイル名を `save_20261031_1800.dat` にしたい。ログの行頭に `[2026-10-31 18:00:05]` を付けたい。`tm` のフィールドを 1 つずつ取り出して整形するのは面倒で、年に 1900 を足し忘れる間違いも起きます。`strftime` は、`%Y-%m-%d` のような書式の文字列を渡すと、その形に整えた文字列を、指定したバッファに書き込んでくれます。

C++20 以降は、`std::format("{:%Y-%m-%d}", ...)` で `chrono` の時刻を書式化できます。新しく書くなら、そちらのほうが安全です。

!!! tip "ポイント"
    - 書式の中の `%Y` や `%m` が、年や月に置き換わる。それ以外の文字はそのまま出る
    - バッファの大きさを渡す。収まらないと、`0` を返し、バッファの中身は不定
    - 年は `%Y`（4 桁）、月日は `%m` `%d`（ゼロ詰め 2 桁）。`tm_year` に 1900 を足す必要はない
    - 曜日や月の名前は、ロケールで言語が変わる。既定の `"C"` ロケールでは英語

!!! info "このページを読む前に"
    [`std::tm`](tm.md) と [`std::localtime`](localtime.md) を先に読んでください。

## 関数の詳しい説明

### std::strftime {#strftime}

```cpp
std::size_t strftime(char* buffer, std::size_t size,
                     const char* format, const std::tm* t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 書き込み先 |
| `size` | `std::size_t` | バッファの大きさ（バイト数）。終端の `\0` を含める |
| `format` | `const char*` | 書式。`%Y-%m-%d` など |
| `t` | `const std::tm*` | 整形する日時 |

戻り値は、書き込んだ文字数です。終端の `\0` は数えません。書式に従って整形した結果が、`size` に収まらないと、`0` を返します。そのとき `buffer` の中身は不定なので、使ってはいけません。ただし、書式の結果が空の文字列になる場合も `0` を返すため、`0` は「収まらなかった」か「空だった」のどちらかです。

`size` には、`sizeof(buffer)` を渡すのが定番です。配列でなくポインタを渡している関数の中では、`sizeof` がポインタの大きさになるので、バッファの大きさを別の引数で受けます。

`t` の各フィールドは、範囲内でなければなりません。`tm_mon` が 12 のような値だと、未定義動作です。`mktime` で正規化してから渡すと安全です。

### よく使う書式 {#specifiers}

| 書式 | 意味 | 例 |
| --- | --- | --- |
| `%Y` | 西暦（4 桁） | `2026` |
| `%m` | 月（01〜12） | `01` |
| `%d` | 日（01〜31） | `05` |
| `%H` | 時（00〜23） | `18` |
| `%M` | 分（00〜59） | `07` |
| `%S` | 秒（00〜60） | `09` |
| `%F` | `%Y-%m-%d` と同じ | `2026-01-05` |
| `%T` | `%H:%M:%S` と同じ | `18:07:09` |
| `%A` | 曜日の名前 | `Thursday` |
| `%a` | 曜日の略称 | `Thu` |
| `%B` | 月の名前 | `January` |
| `%j` | 年の通算日（001〜366） | `001` |
| `%%` | `%` 自身 | `%` |

`%F` と `%T` は C++11 / C99 から使えます。古い MSVC では対応していなかったので、移植するコードでは気にします。

月や曜日の名前（`%B`、`%A`）は、`setlocale` で設定したロケールに従います。何も設定しなければ `"C"` ロケールで、英語です。日本語にしたいときは、ロケールの設定か、自分で配列を作る方法があります。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::time_t t = 1767225600;  // 2026-01-01 00:00:00 UTC
  const std::tm utc = *std::gmtime(&t);

  char buffer[64];
  std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &utc);
  std::println("{}", buffer);

  std::strftime(buffer, sizeof(buffer), "%A, %B %d", &utc);
  std::println("{}", buffer);

  // バッファが小さすぎると 0 が返る
  char small[8];
  const std::size_t n = std::strftime(small, sizeof(small), "%Y-%m-%d %H:%M:%S", &utc);
  std::println("収まらないとき: {}", n);
}
```

```text title="実行結果"
2026-01-01 00:00:00
Thursday, January 01
収まらないとき: 0
```

3 つ目は、`"2026-01-01 00:00:00"` が 19 文字なのに、バッファが 8 バイトしかないため、`0` が返っています。このあと `small` を読むのは危険です。

## ゲームでの使いどころ

セーブ データのファイル名に、保存した日時を入れます。

```cpp
char name[64];
const std::tm local = *std::localtime(&now);
std::strftime(name, sizeof(name), "save_%Y%m%d_%H%M%S.dat", &local);
```

ログの行頭の時刻も、同じように作ります。バッファは余裕を持たせます。64 バイトあれば、普通の書式は収まります。

## よくあるミス

??? failure "バッファが足りず、0 が返ったのに中身を使う"
    戻り値が 0 のとき、バッファの中身は不定です。0 を検査して、エラー処理をします。

??? failure "tm_year に 1900 を足してから渡す"
    `strftime` は `tm_year` が 1900 からの年数だと知っています。`2026` を入れた `tm` を渡すと、3926 年と表示されます。`tm` はそのまま渡します。

??? failure "%B や %A が英語で出る"
    ロケールを変えていないと `"C"` ロケールです。日本語にしたいなら `setlocale` を呼ぶ手もありますが、環境依存が強いので、ゲームでは自前の名前の表を使うことが多いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](../../utilities/format.md) | C++20 で `{:%F}` のように、`chrono` の時刻を書式化できる |
| [`asctime`](asctime.md) | 書式が固定の文字列にする |
| [`std::put_time`](../put_time.md) | ストリームに書式つきで日時を出す |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `strftime` は、書式に従って日時を文字列にする
    - [x] 戻り値が 0 のとき、バッファの中身は使えない
    - [x] `%Y-%m-%d %H:%M:%S` だけ覚えればほとんど足りる

## 関連ページ

- [cpprefjp: std::strftime](https://cpprefjp.github.io/reference/ctime/strftime.html)
- [cppreference: std::strftime](https://en.cppreference.com/w/cpp/chrono/c/strftime)
