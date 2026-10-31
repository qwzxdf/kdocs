---
title: std::regex_error
summary: "正規表現のパターンが不正なときに投げられる例外。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_error

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

ユーザーが入力した文字列を、そのまま正規表現のパターンとして使うと、`(` を閉じ忘れたり、`[` が閉じていなかったりして、パターンが不正になることがあります。`std::regex` のコンストラクターは、そのとき `std::regex_error` を投げます。

プログラムの内部で固定のパターンを使うなら、エラーは開発中に気づきます。外から来るパターンを受け付ける場合は、必ず `catch` します。

!!! tip "ポイント"
    - `std::runtime_error` の派生クラス。`<regex>` で定義される
    - `code()` で、原因を表すエラー コードが得られる
    - `what()` のメッセージは、実装ごとに違う。表示や比較には使わず、`code()` で判断する
    - パターンの構文ミス以外では、投げられない（`regex_match` / `regex_search` は投げない）

!!! info "このページを読む前に"
    [`std::basic_regex`](basic_regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_error {#regex_error}

```cpp
class regex_error : public std::runtime_error {
 public:
  explicit regex_error(std::regex_constants::error_type ecode);
  std::regex_constants::error_type code() const;
};
```

### code {#code}

エラーの原因を、`std::regex_constants::error_type` で返します。主な値は次のとおりです。

| 値 | 原因 |
| --- | --- |
| `error_paren` | `(` と `)` の対応が合っていない |
| `error_brack` | `[` と `]` の対応が合っていない |
| `error_brace` | `{` と `}` の対応が合っていない |
| `error_badbrace` | `{}` の中の回数が不正 |
| `error_range` | `[z-a]` のように、範囲が逆 |
| `error_escape` | エスケープが不正 |
| `error_backref` | 存在しないグループへの後方参照 |
| `error_badrepeat` | 繰り返しの前に対象がない（`*a` など） |
| `error_complexity` | パターンが複雑すぎる |
| `error_stack` | 実行時に、メモリが足りなくなった |

`error_complexity` と `error_stack` は、パターンの構文は正しくても、一致の判定中に実装の限界に達したときに投げられます。この 2 つは、`regex_match` / `regex_search` から投げられる場合があります。長い入力に、入れ子の繰り返しを含むパターンを使うと起きやすいです。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  try {
    std::regex re("(");  // 括弧が閉じていない
  } catch (const std::regex_error& e) {
    std::println("括弧のエラー: {}",
                 e.code() == std::regex_constants::error_paren);
  }

  try {
    std::regex re("[a-");  // 角括弧が閉じていない
  } catch (const std::regex_error& e) {
    std::println("角括弧のエラー: {}",
                 e.code() == std::regex_constants::error_brack);
  }
}
```

```text title="実行結果"
括弧のエラー: true
角括弧のエラー: true
```

`what()` の文章は、実装ごとに違うので、表示しません。判定は `code()` で行います。

## ゲームでの使いどころ

デバッグ コンソールで、プレイヤー（開発者）が入力した正規表現でログを絞り込む機能などで使います。不正な入力でクラッシュさせないために、`catch` して「パターンが不正です」と表示します。

```cpp
try {
  std::regex re(input);
  // 検索
} catch (const std::regex_error&) {
  // パターンの誤りを知らせる
}
```

## よくあるミス

??? failure "外から来るパターンを catch しない"
    不正な入力でプログラムが落ちます。`std::regex_error` を `catch` します。

??? failure "what() の文章で判定する"
    メッセージは実装ごとに違います。`code()` で判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::basic_regex`](basic_regex.md) | これを投げるクラス |
| [`regex_constants`](regex_constants.md) | エラー コードの定義がある |
| `std::runtime_error` | 親クラス |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `regex_error` は、不正なパターンで `regex` のコンストラクターが投げる例外
    - [x] 原因は `code()` で判断する。`what()` は実装ごとに違う
    - [x] 外から来るパターンは `catch` する

## 関連ページ

- [cpprefjp: regex_error](https://cpprefjp.github.io/reference/regex/regex_error.html)
- [cppreference: std::regex_error](https://en.cppreference.com/w/cpp/regex/regex_error)
