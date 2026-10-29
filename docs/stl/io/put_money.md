---
title: std::put_money
summary: "金額を、ロケールの形式で出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::put_money

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <iomanip>`
</div>

所持金やショップの値段を `12,345` のように、桁区切り付きで表示したい。国や言語ごとに、区切りの文字も、通貨記号の位置も違います。`std::put_money` は、その違いをストリームのロケールに任せて、金額を書式付きで出力します。

!!! tip "ポイント"
    - 渡す金額は、通貨の最小単位の整数（ドルならセント、円なら円）
    - 既定の `"C"` ロケールでは、数字がそのまま出る。桁区切りは、ロケールを設定したときだけ
    - 通貨記号は、`showbase` を付けたときだけ出る
    - ゲームの所持金の表示には、`std::format` の `{:L}` のほうが手軽なことが多い

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::put_money {#put_money}

```cpp
template <class MoneyT>
/* 未規定 */ put_money(const MoneyT& mon, bool intl = false);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mon` | `long double` または `std::basic_string` | 金額。最小単位の数。文字列なら、数字の並び |
| `intl` | `bool` | `true` で国際表記（通貨記号が `JPY` のような 3 文字の符号）にする |

ストリームのロケールの `money_put` ファセットに、金額と `intl` を渡して書き出させます。小数点以下の桁数は、ロケールの `frac_digits` で決まります。たとえば米国のロケールなら `frac_digits` が 2 なので、`12345` は `123.45` と出ます。日本のロケールは 0 なので、`12345` は `12,345` です。

通貨記号は、ストリームの `showbase` が立っているときだけ付きます。ロケールが用意する記号は、環境によって違うので、決まった文字列を期待するコードは書けません。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>
#include <locale>
#include <print>
#include <sstream>

int main() {
  // 既定の "C" ロケールでは、数字がそのまま出る
  std::cout << std::put_money(12345.0L) << '\n';

  // 桁区切りのあるロケール（通貨記号は showbase を付けたときだけ出る）
  std::ostringstream os;
  os.imbue(std::locale("ja-JP"));
  os << std::put_money(12345.0L);
  std::println("{}", os.str());

  // 区切り付きの文字列を、整数の金額として読み戻す
  std::istringstream in("12,345");
  in.imbue(std::locale("ja-JP"));
  long double v = 0;
  in >> std::get_money(v);
  std::println("ok={} {}", static_cast<bool>(in), static_cast<long long>(v));
}
```

```text title="実行結果"
12345
12,345
ok=true 12345
```

1 行目は、`"C"` ロケールで区切りが出ない例です。2 行目は、`ja-JP` ロケールを設定した `ostringstream` で、桁区切りが付いています。3 行目は、同じロケールで `get_money` を使い、区切り付きの文字から `12345` を読み戻しています。`std::locale("ja-JP")` の名前は MSVC の書き方で、POSIX では `"ja_JP.UTF-8"` のように書きます。指定したロケールが無い環境では、`std::runtime_error` が飛びます。

## ゲームでの使いどころ

アイテムの値段や、所持金の表示です。国際版を作るとき、通貨の書式をロケールに任せると、地域ごとの規則に合わせられます。

ただし、ゲーム内の通貨（ゴールド、コイン）は、実在の通貨と書式の規則が違うことがほとんどです。桁区切りだけで足りるなら、`std::format("{:L}", gold)` のように、ロケールを使った整数の書式化のほうが、短く書けます。`put_money` は、実在の通貨の金額を、地域の規則で表示するときに使います。

## よくあるミス

??? failure "桁区切りが出ない"
    ストリームのロケールが、既定の `"C"` のままです。`imbue` でロケールを設定します。グローバルのロケールを変えても、すでに作ったストリームには反映されません。

??? failure "`12345` を渡したのに、`123.45` と出た"
    ロケールの `frac_digits` が 2 です。渡す値は、最小単位（セント）の数なので、`12345` セントは `123.45` ドルです。

??? failure "指定したロケールで例外が飛ぶ"
    その名前のロケールが、環境にありません。`try` で囲んで、無いときの扱いを決めておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_money`](get_money.md) | 逆に、書式付きの金額を読み込む |
| [`quoted`](quoted.md) | 文字列を引用符で囲んで出力する |
| [`locale`](locale.md) | ロケール。書式のよりどころ |

## コンパイラ対応

C++11 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。ロケール名の書き方は、処理系で違います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `put_money` は、最小単位の金額を、ストリームのロケールの書式で出力する
    - [x] 桁区切りや通貨記号は、ロケールを設定しないと出ない。記号は `showbase` で付く
    - [x] ゲーム内の通貨の表示は、`std::format` の `{:L}` のほうが手軽なことが多い

## 関連ページ

- [cpprefjp: std::put_money](https://cpprefjp.github.io/reference/ios/put_money.html)
- [cppreference: std::put_money](https://en.cppreference.com/w/cpp/io/manip/put_money)
