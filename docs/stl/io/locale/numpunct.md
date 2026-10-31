---
title: std::numpunct
summary: "数値の書式（小数点・桁区切り）を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::numpunct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

1234567.89 を、日本では `1,234,567.89` と書き、ドイツでは `1.234.567,89` と書きます。小数点の文字、桁区切りの文字、何桁ごとに区切るか、`true` をどう書くか。こうした<strong>数値の見た目の規則</strong>を持つ部品が `std::numpunct` です。ストリームが数値を出し入れするとき（`num_put` と `num_get`）に、この部品を参照します。

!!! tip "ポイント"
    - `decimal_point`、`thousands_sep`、`grouping` が、小数点と桁区切りの規則
    - `"C"` ロケールは、小数点が `.`、桁区切りが `,`、グループ分けなし（区切りは出ない）
    - 桁区切りを入れたいときは、`numpunct` を継承したファセットを `imbue` する
    - `truename` / `falsename` は、`boolalpha` で出す `true` / `false` の文字列

!!! info "このページを読む前に"
    [`std::locale::facet`](facet.md) と [`std::use_facet`](use_facet.md) を先に読んでください。

## 関数の詳しい説明

### std::numpunct {#numpunct}

```cpp
template <class CharT>
class numpunct {
 public:
  CharT decimal_point() const;
  CharT thousands_sep() const;
  std::string grouping() const;
  std::basic_string<CharT> truename() const;
  std::basic_string<CharT> falsename() const;
};
```

### decimal_point {#decimal_point}

小数点の文字を返します。`"C"` ロケールでは `'.'` です。ドイツ語やフランス語のロケールでは `','` です。ストリームが小数を出力するときと、読み込むときの両方で使われます。

### thousands_sep {#thousands_sep}

桁区切りの文字を返します。`"C"` ロケールでは `','` ですが、`grouping` が空なので、実際には区切りが出力されません。日本語のロケールも `','` です。

### grouping {#grouping}

何桁ごとに桁区切りを入れるかを、数値の並びを入れた `std::string` で返します。文字ではなく数の値で、`"\3"` なら「下から 3 桁ごと」です。空文字列は「区切りなし」です。`"C"` ロケールは空なので、`1234567` は `1234567` のまま出力されます。

### truename と falsename {#truename}

`std::boolalpha` を使ったときに、`bool` を文字列にするための値です。`"C"` ロケールでは `"true"` と `"false"` で、これを継承して日本語にすれば、`真` と `偽` と出力できます。

## 実際に動かしてみる

```cpp
#include <locale>
#include <print>
#include <sstream>

// 桁区切りを 3 桁ごとの , にする
struct Comma3 : std::numpunct<char> {
  std::string do_grouping() const override { return "\3"; }
};

int main() {
  const auto& np = std::use_facet<std::numpunct<char>>(std::locale::classic());
  std::println("小数点: {}", np.decimal_point());
  std::println("桁区切り: {}", np.thousands_sep());
  std::println("区切りなし: {}", np.grouping().empty());
  std::println("{} / {}", np.truename(), np.falsename());

  // 3 桁区切りのファセットを差し込んだストリーム
  std::ostringstream os;
  os.imbue(std::locale(std::locale::classic(), new Comma3));
  os << 1234567;
  std::println("{}", os.str());
}
```

```text title="実行結果"
小数点: .
桁区切り: ,
区切りなし: true
true / false
1,234,567
```

`Comma3` は `do_grouping` だけを上書きしています。区切りの文字は、継承元の `','` がそのまま使われます。

## ゲームでの使いどころ

スコアやコインの数に桁区切りを入れたいときに使えます。ただし、ゲーム内の表示は、`std::format("{:L}", ...)` や自作の整形関数のほうが、分かりやすいことが多いです。

## よくあるミス

??? failure "grouping に文字の '3' を書く"
    `"3"` は文字 `'3'`（値 51）なので、51 桁ごとの区切りになります。数の値は `"\3"` と書きます。

??? failure "ファセットを imbue するだけで、既存の出力も変わると思う"
    `imbue` したあとに出力する数値から変わります。それ以前の出力は変わりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`num_put`](num_put.md) | 数値を書き出す。この規則を使う |
| [`num_get`](num_get.md) | 数値を読み込む。この規則を使う |
| [`moneypunct`](moneypunct.md) | 通貨の書式 |
| [`lconv`](lconv.md) | C のロケールの同じ情報 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `numpunct` は、小数点と桁区切りと、`true` / `false` の文字列を持つ
    - [x] `"C"` ロケールは、区切りなし。`grouping` の値は `"\3"` のように数で書く
    - [x] 継承して `imbue` すると、ストリームの数値の見た目が変わる

## 関連ページ

- [cpprefjp: numpunct](https://cpprefjp.github.io/reference/locale/numpunct.html)
- [cppreference: std::numpunct](https://en.cppreference.com/w/cpp/locale/numpunct)
