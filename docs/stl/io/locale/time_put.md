---
title: std::time_put
summary: "日時を、書式に従って文字列に書き出すファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::time_put

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`std::put_time` という操作子で `os << std::put_time(&t, "%Y-%m-%d")` と書くと、日時が文字になって出力されます。その裏で整形をしているのが、ロケールの部品の `std::time_put` です。`strftime` と同じ書式の指定が使え、曜日や月の名前は、ロケールの言語で出力されます。

!!! tip "ポイント"
    - 書式は `strftime` と同じ（`%Y-%m-%d` など）
    - 曜日や月の名前は、ロケールの言語で決まる。`"C"` ロケールは英語
    - 書式の範囲を、ポインタの組で渡す
    - 普段は `std::put_time` の操作子から使う

!!! info "このページを読む前に"
    [`std::strftime`](../ctime/strftime.md) と [`std::put_time`](../put_time.md) を先に読んでください。

## 関数の詳しい説明

### std::time_put {#time_put}

```cpp
template <class CharT, class OutIt = std::ostreambuf_iterator<CharT>>
class time_put {
 public:
  OutIt put(OutIt out, std::ios_base& str, CharT fill, const std::tm* t,
            const CharT* fmt_first, const CharT* fmt_last) const;
  OutIt put(OutIt out, std::ios_base& str, CharT fill, const std::tm* t,
            char format, char modifier = 0) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | `OutIt` | 書き出し先の出力イテレータ |
| `str` | `std::ios_base&` | ロケールの取得元のストリーム |
| `fill` | `CharT` | 埋める文字 |
| `t` | `const std::tm*` | 書く日時 |
| `fmt_first`, `fmt_last` | `const CharT*` | 書式の範囲 |

書式の範囲を渡す版は、`%Y-%m-%d` のような書式の文字列全体を処理します。`char format` を渡す版は、`'Y'` のように 1 つの変換指定だけを処理します。

書式の意味は `strftime` と同じです。ただし、曜日と月の名前など、言語に依存する部分は、`str` に設定されたロケール（`str.getloc()`）に従って出力されます。

`t` の各フィールドは、正しい範囲でなければなりません。範囲外は未定義動作です。曜日（`%A`）を出すには、`tm_wday` が正しく設定されている必要があるので、`mktime` などで補っておきます。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::tm t{};
  t.tm_year = 124;  // 2024 年
  t.tm_mon = 0;     // 1 月
  t.tm_mday = 1;

  std::ostringstream os;
  const std::string fmt = "%Y-%m-%d";
  std::use_facet<std::time_put<char>>(std::locale::classic())
      .put(std::ostreambuf_iterator<char>(os), os, ' ', &t,
           fmt.data(), fmt.data() + fmt.size());
  std::println("{}", os.str());
}
```

```text title="実行結果"
2024-01-01
```

書式の範囲を、`data()` と `data() + size()` で渡しています。`tm_year` は 1900 を引いた値なので、124 が 2024 年になります。

## ゲームでの使いどころ

ログの時刻やセーブデータの日付を出力するときに、`put_time` の裏で使われています。自分で直接呼ぶより、`std::put_time` や `std::format("{:%F}")` のほうが分かりやすいです。

## よくあるミス

??? failure "tm_wday を設定せずに %A を使う"
    曜日が、意図しないものになります。`mktime` を通して、`tm_wday` を計算してから渡します。

??? failure "書式の範囲の終わりを間違える"
    `fmt.data() + fmt.size()` が終端の次です。`size() + 1` にすると、終端の `\0` も書式として読まれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time_get`](time_get.md) | 逆方向。文字列から日時を読む |
| [`std::put_time`](../put_time.md) | ストリームに流す操作子。普段はこちら |
| [`std::strftime`](../ctime/strftime.md) | C の関数。同じ書式 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `time_put` は、`strftime` と同じ書式で、日時を文字にする部品
    - [x] 曜日や月の名前は、ロケールの言語に従う
    - [x] 普段は `put_time` の操作子

## 関連ページ

- [cpprefjp: time_put](https://cpprefjp.github.io/reference/locale/time_put.html)
- [cppreference: std::time_put](https://en.cppreference.com/w/cpp/locale/time_put)
