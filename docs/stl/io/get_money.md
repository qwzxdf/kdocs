---
title: std::get_money
summary: "金額を、ロケールの形式で入力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::get_money

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <iomanip>`
</div>

プレイヤーが入力した `12,345` という金額の文字から、数の `12345` を取り出したい。桁区切りの `,` を自分で取り除くのは簡単ですが、国によって区切りも小数点も違います。`std::get_money` は、その規則をストリームのロケールに任せて、書式付きの金額を読み込みます。

!!! tip "ポイント"
    - 読み込み先は、`long double` か `std::string`。値は最小単位の数になる
    - 桁区切りの文字や、小数点は、ストリームのロケールで決まる
    - 書式に合わない入力では、ストリームが失敗状態（`failbit`）になる
    - 通貨記号が付いた入力は、`showbase` を設定したストリームで読む

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::get_money {#get_money}

```cpp
template <class MoneyT>
/* 未規定 */ get_money(MoneyT& mon, bool intl = false);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `mon` | `long double&` または `std::basic_string&` | 読み込んだ金額を入れる変数 |
| `intl` | `bool` | `true` で、国際表記（`JPY` のような 3 文字の符号）の通貨記号を期待する |

ストリームのロケールの `money_get` ファセットが、入力から金額を読み、桁区切りを取り除いた数にします。`long double` に読む場合は、通貨の最小単位での数になります。`std::string` に読む場合は、符号と数字だけの文字列になります。

小数点以下の桁数は、ロケールの `frac_digits` に従うため、`123.45` と書いてある入力を米国のロケールで読むと、`12345`（セント）になります。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <locale>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream in("12,345");
  in.imbue(std::locale("ja-JP"));
  long double v = 0;
  in >> std::get_money(v);
  std::println("ok={} {}", static_cast<bool>(in), static_cast<long long>(v));

  // string に読むと、数字の並びになる
  std::string digits;
  std::istringstream in3("98765");
  in3 >> std::get_money(digits);
  std::println("string 版: {}", digits);
}
```

```text title="実行結果"
ok=true 12345
string 版: 98765
```

1 つ目は、`ja-JP` ロケールの桁区切り `,` を取り除いて、`12345` になっています。2 つ目は、`std::string` に読んだ例で、数字の並びがそのまま入ります。`std::locale("ja-JP")` の名前は MSVC の書き方で、POSIX では `"ja_JP.UTF-8"` のように書きます。

## ゲームでの使いどころ

ユーザーが入力する金額の欄を読み取るときです。ショップのオークションや、課金の確認画面の金額欄のように、地域ごとの書式で入力されうる場面で役に立ちます。

ゲーム内の通貨の数を読むだけなら、`std::from_chars` で整数を読む前に、桁区切りの `,` を取り除くほうが、速くて単純です。ロケールを介する `get_money` は、ファセットを探す分、重くなります。入力のたびに呼ぶ場所では、頻度を考えて選んでください。

## よくあるミス

??? failure "読み込んだ値が、思った値の 100 倍になった"
    米国のロケールのように `frac_digits` が 2 のロケールでは、読んだ値は最小単位（セント）の数です。`123.45` ドルを読むと `12345` になります。

??? failure "区切りの `,` が原因で、読み込みに失敗する"
    ストリームのロケールが `"C"` のままで、区切りの規則がありません。`imbue` で、期待する書式のロケールを設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`put_money`](put_money.md) | 逆に、金額を書式付きで書き出す |
| [`from_chars`](from_chars.md) | 区切りなしの整数や浮動小数点を、ロケールなしで読む |

## コンパイラ対応

C++11 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。ロケール名の書き方は、処理系で違います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `get_money` は、ロケールの書式の金額を、最小単位の数として読み込む
    - [x] 区切りや小数点の規則は、ストリームのロケールで決まる
    - [x] 区切りなしの整数を読むだけなら、`from_chars` のほうが速い

## 関連ページ

- [cpprefjp: std::get_money](https://cpprefjp.github.io/reference/ios/get_money.html)
- [cppreference: std::get_money](https://en.cppreference.com/w/cpp/io/manip/get_money)
