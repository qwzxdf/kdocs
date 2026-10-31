---
title: std::messages
summary: "メッセージ（翻訳された文字列）をカタログから取り出すファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::messages

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

ゲームのメッセージを、日本語と英語で切り替えたい。C の世界には、メッセージのカタログ（翻訳の辞書ファイル）を開いて、番号で文字列を引く `catgets` という仕組みがあります。それを C++ のロケールの部品にしたのが `std::messages` です。ただし、カタログの形式と置き場所は処理系ごとに違い、実際のゲームで使われることは、ほとんどありません。

ゲームのローカライズは、JSON や CSV、専用の辞書ファイルを自作して読むのが普通です。

!!! tip "ポイント"
    - `open` でカタログを開き、`get` で番号から文字列を引き、`close` で閉じる
    - `get` の最後の引数は、見つからなかったときの既定の文字列
    - カタログの形式と場所は処理系しだい。移植性はない
    - ゲームのローカライズには、自前の辞書ファイルのほうが扱いやすい

!!! info "このページを読む前に"
    [`std::locale::facet`](facet.md) と [`std::use_facet`](use_facet.md) を先に読んでください。

## 関数の詳しい説明

### std::messages {#messages}

```cpp
template <class CharT>
class messages {
 public:
  using catalog = int;
  catalog open(const std::string& name, const std::locale& loc) const;
  std::basic_string<CharT> get(catalog c, int set, int msgid,
                               const std::basic_string<CharT>& dfault) const;
  void close(catalog c) const;
};
```

### open {#open}

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `name` | `const std::string&` | カタログの名前 |
| `loc` | `const std::locale&` | 使うロケール |

カタログを開き、その識別子（整数）を返します。開けなかったときは、負の値を返します。名前の意味（ファイル名か、登録名か）は、処理系が決めます。

### get {#get}

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `catalog` | `open` が返した識別子 |
| `set` | `int` | メッセージの集まりの番号 |
| `msgid` | `int` | メッセージの番号 |
| `dfault` | `const std::basic_string<CharT>&` | 見つからなかったときの文字列 |

`set` と `msgid` で指定したメッセージを返します。見つからなかったときは、`dfault` をそのまま返します。そのため、カタログを開けなかった環境でも、既定の文字列が出るので、プログラムは動き続けます。

### close {#close}

開いたカタログを閉じます。`open` で開いたものは、使い終えたら閉じます。

## 実際に動かしてみる

```cpp
#include <locale>
#include <print>
#include <string>

int main() {
  const std::locale loc = std::locale::classic();
  const auto& msg = std::use_facet<std::messages<char>>(loc);

  // 存在しないカタログ。開けなくても、既定の文字列が返る
  const auto cat = msg.open("no_such_catalog", loc);
  const std::string text = msg.get(cat, 0, 1, "Hello (default)");
  std::println("{}", text);
  if (cat >= 0) msg.close(cat);
}
```

```text title="実行結果"
Hello (default)
```

存在しないカタログを指定しているので、`get` は既定の文字列を返します。実際の翻訳を読める環境は、処理系ごとに特別な設定が必要です。

## ゲームでの使いどころ

標準の `messages` で翻訳を引くのは、移植性が低いので、ゲームでは使いません。言語ごとの辞書ファイルを自分で読み込み、キーから文字列を引く仕組みを作ります。

```cpp
// 言語ごとの辞書: キー → 表示する文字列
std::unordered_map<std::string, std::string> table;
```

## よくあるミス

??? failure "カタログが開けなかったのに get を呼ぶ"
    `open` が負の値を返したとき、`get` の動作は、環境によって違います。`dfault` を返すのが一般的ですが、保証はありません。開けたかを確認してから呼びます。

??? failure "close を呼ばない"
    開いたカタログは、閉じないと資源が残ります。`open` と `close` を組にします。

## 類似

| 名前 | 違い |
| --- | --- |
| `catgets` | C の POSIX のメッセージ カタログ |
| `gettext` | 広く使われる翻訳の仕組み。ライブラリが必要 |
| 自前の辞書ファイル | ゲームのローカライズで一般的 |

## コンパイラ対応

C++98 から使えます。カタログの形式と場所は、処理系ごとに違います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `messages` は、番号で翻訳文字列を引くカタログの部品
    - [x] `open`、`get`、`close` の順。見つからなければ既定の文字列
    - [x] ゲームのローカライズには、自前の辞書ファイルを使う

## 関連ページ

- [cpprefjp: messages](https://cpprefjp.github.io/reference/locale/messages.html)
- [cppreference: std::messages](https://en.cppreference.com/w/cpp/locale/messages)
