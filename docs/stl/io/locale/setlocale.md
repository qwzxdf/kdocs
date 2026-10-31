---
title: std::setlocale
summary: "C のロケールを設定・取得する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setlocale

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <clocale>`
</div>

`printf("%f", 3.14)` が、ある国の PC では `3,14` と出る。`strftime` の曜日が、環境で日本語になったり英語になったりする。C の標準ライブラリの関数は、プログラム全体で 1 つの「いまのロケール」に従って動くので、それを切り替える関数が `setlocale` です。`localeconv`、`strftime`、`mbrtowc` などの動作が、この設定で変わります。

C++ のストリームが従う `std::locale` とは、別の仕組みです。両方を合わせたいときは、`std::locale::global` を呼ぶと、C のロケールも変わります。

!!! tip "ポイント"
    - プログラムの起動時は、`"C"` ロケール。何も設定しなければ、環境に依存しない動作になる
    - `setlocale(LC_ALL, "")` は、環境（OS の設定）のロケールにする。結果が環境で変わる
    - 引数の `locale` を `nullptr` にすると、設定は変えず、いまの名前を返す
    - ゲームでは、数値の入出力が変わらないよう、`"C"` のままにすることが多い

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。C++ のロケールとの違いが分かります。

## 関数の詳しい説明

### std::setlocale {#setlocale}

```cpp
char* setlocale(int category, const char* locale);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `category` | `int` | 対象の分類。`LC_ALL`、`LC_NUMERIC` など |
| `locale` | `const char*` | ロケール名。`""` は環境の設定、`nullptr` は取得だけ |

`category` で、どの種類の規則を変えるかを選びます。`LC_ALL` は全部です。

| 分類 | 変わるもの |
| --- | --- |
| `LC_ALL` | 以下のすべて |
| `LC_COLLATE` | 文字列の並び順（`strcoll`） |
| `LC_CTYPE` | 文字の分類と変換、マルチバイト文字（`isalpha`、`mbrtowc`） |
| `LC_MONETARY` | 通貨の書式（`localeconv` の通貨の項目） |
| `LC_NUMERIC` | 小数点、桁区切り（`printf` の `%f`、`localeconv`） |
| `LC_TIME` | 日時の書式、曜日と月の名前（`strftime`） |

`locale` に渡す名前は、環境で違います。Linux は `"ja_JP.UTF-8"`、Windows の MSVC は `"ja-JP"` や `"Japanese_Japan.932"`、UTF-8 にするなら `".UTF-8"` です。`""` を渡すと、環境の設定を使います。OS の設定が日本語なら、日本語のロケールになります。

戻り値は、設定後のロケール名です。設定に失敗する（その名前のロケールがインストールされていない）と、`nullptr` を返し、いまの設定は変わりません。戻り値のポインタは、次の `setlocale` の呼び出しで無効になることがあります。保存したいなら、コピーします。

マルチスレッドのプログラムでは、`setlocale` は全スレッドに影響します。ほかのスレッドが `printf` や `strtod` を呼んでいる間に変えると、小数点が突然変わる事故が起きます。プログラムの最初に、1 回だけ呼びます。

## 実際に動かしてみる

```cpp
#include <clocale>
#include <print>

int main() {
  // 取得だけ: nullptr を渡すと、設定は変わらない
  std::println("起動時: {}", std::setlocale(LC_ALL, nullptr));

  // "C" ロケールに設定する
  std::println("設定後: {}", std::setlocale(LC_ALL, "C"));

  // 存在しないロケールは nullptr が返る
  const char* r = std::setlocale(LC_ALL, "no_such_locale");
  std::println("存在しない名前: {}", r == nullptr);
}
```

```text title="実行結果"
起動時: C
設定後: C
存在しない名前: true
```

存在しない名前を渡しても、設定は変わらず、`"C"` のままです。

## ゲームでの使いどころ

ゲームの設定やセーブ データを数値の文字列で書き出すときに、ロケールの影響で小数点が `,` になると、読み込めなくなります。数値の入出力の部分だけは、`"C"` ロケールのままにします。環境のロケールにするのは、ユーザーに見せる日付の表示くらいです。

```cpp
std::setlocale(LC_NUMERIC, "C");   // 小数点を . に固定する
```

## よくあるミス

??? failure "C++ のストリームにも効くと思う"
    `std::cout` や `std::ofstream` が従うのは `std::locale` です。`setlocale` だけでは変わりません。両方に反映したいなら、`std::locale::global(std::locale(""))` を使います。

??? failure "setlocale(LC_ALL, "") のまま、数値をファイルに書く"
    ドイツ語などの環境では、`3.14` が `3,14` と書かれて、別の環境で読み込めなくなります。数値は `"C"` ロケール、または `std::to_chars` / `std::from_chars`（ロケールに依存しない）で書き読みします。

??? failure "戻り値のポインタを保存しておく"
    次の `setlocale` で、指す先の内容が変わることがあります。`std::string` にコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`localeconv`](localeconv.md) | いまのロケールの数値と通貨の書式を調べる |
| [`std::locale`](../locale.md) | C++ のロケール。ストリームが従う |
| `std::to_chars` / `std::from_chars` | ロケールに依存せず、数値と文字列を変換する |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。ロケール名の書き方は環境ごとに違います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `setlocale` は、C の関数が従うロケールを設定・取得する
    - [x] 起動時は `"C"`。`""` で環境の設定、`nullptr` で取得だけ
    - [x] 数値の読み書きは `"C"` のままにする。C++ のストリームは `std::locale`

## 関連ページ

- [cpprefjp: setlocale](https://cpprefjp.github.io/reference/clocale/setlocale.html)
- [cppreference: std::setlocale](https://en.cppreference.com/w/cpp/locale/setlocale)
