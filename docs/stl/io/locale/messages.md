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

ゲームの多言語対応で、メッセージのカタログ（翻訳ファイル）から、言語ごとの文字列を取り出すための仕組みです。POSIX の `catgets` / gettext 風の機能で、Windows ではあまり使われません。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::messages {#messages}

```cpp
template <class CharT>
class messages {
 public:
  catalog open(const std::string& name, const std::locale& loc) const;
  std::basic_string<CharT> get(catalog c, int set, int msgid, const std::basic_string<CharT>& dfault) const;
  void close(catalog c) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `name` | string | カタログの名前 |
| `loc` | locale | ロケール |

- 戻り値: カタログの識別子
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <locale>
#include <print>

int main() {
  // 例: カタログを開いてメッセージを取り出す
  // auto cat = std::use_facet<std::messages<char>>(loc).open("game", loc);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | （POSIX の環境での翻訳） |

## よくあるミス

??? failure "Windows で使う"
    標準のカタログ機能は、環境によってほぼ使えません。多言語対応は別のライブラリ（gettext など）を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::locale`](../locale.md) | ロケール |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メッセージ（翻訳された文字列）をカタログから取り出すファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::messages](https://cpprefjp.github.io/reference/locale/messages.html)
- [cppreference: std::messages](https://en.cppreference.com/w/cpp/locale/messages)
