---
title: std::contracts::contract_violation
summary: "契約（事前条件・事後条件）の違反の情報を表す型。"
order: 900
tags:
  - 型・言語サポート
---

# std::contracts::contract_violation

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <contracts>`
</div>

C++26 の契約（`pre`・`post`・`contract_assert`）は、関数の前提条件や事後条件を、コードの中に書く仕組みです。条件が破られたとき、プログラムは「違反ハンドラー」を呼びます。ハンドラーに「どの条件が、どこで破られたか」を伝える入れ物が `std::contracts::contract_violation` です。ログに出したり、救済の処理を切り替えたりするのに使います。

!!! tip "ポイント"
    - 違反ハンドラー `handle_contract_violation` の引数として渡される
    - `comment()` で条件の式の文字列、`location()` で場所、`kind()` で `pre`・`post`・`assert` の別を取る
    - 自分で作る型ではない（実装が作って渡す）
    - C++26 の機能。実装の対応は、まだ限られている

!!! info "このページを読む前に"
    [`std::source_location`](source_location.md)（呼び出し位置を表す型）を先に読んでおくと、行番号やファイル名の話が分かりやすくなります。

## 関数の詳しい説明

### std::contracts::contract_violation {#contract_violation}

<span class="ver ver-26">C++26</span>

```cpp
namespace std::contracts {
class contract_violation {
 public:
  const char* comment() const noexcept;
  std::source_location location() const noexcept;
  assertion_kind kind() const noexcept;
  evaluation_semantic semantic() const noexcept;
  detection_mode detection_mode() const noexcept;
  bool is_terminating() const noexcept;
  std::exception_ptr evaluation_exception() const noexcept;
};
}
```

#### comment

`comment()` は、破られた条件の式を文字列で返します。`pre(x > 0)` が破られたなら、`"x > 0"` のような文字列です。ログに出すと、どの条件かが分かります。形式は実装に依存します。

#### location

`location()` は、違反を検出した場所を [`std::source_location`](source_location.md) で返します。ファイル名、行番号、関数名が取れます。

#### kind

`kind()` は、`pre`（事前条件）・`post`（事後条件）・`assert`（`contract_assert`）のどれが破られたかを返します。事前条件の違反は、呼び出し側のバグ、事後条件の違反は、その関数自身のバグ、という見分けに使えます。

#### semantic

`semantic()` は、そのとき適用された「評価の意味」を返します。違反を無視する（`ignore`）、ハンドラーを呼んで続行する（`observe`）、ハンドラーのあとに終了する（`enforce`）、ハンドラーなしで即終了する（`quick_enforce`）の 4 つがあります。どれを使うかは、ビルドの設定で決まります。

#### detection_mode と evaluation_exception

`detection_mode()` は、違反の見つかり方を返します。条件が偽になった場合（`predicate_false`）と、条件を評価している途中で例外が飛んだ場合（`evaluation_exception`）です。後者のときは、`evaluation_exception()` でその例外を取れます。

#### is_terminating

`is_terminating()` は、ハンドラーから戻ったあとに、プログラムが終了するかを返します。

## 使い方の形

```cpp
#include <contracts>
#include <print>

// 契約が破られたときに呼ばれる違反ハンドラー
void handle_contract_violation(const std::contracts::contract_violation& v) {
  std::println("契約違反: {}", v.comment());
  std::println("  場所: {}:{}", v.location().file_name(), v.location().line());
}

int Divide(int a, int b)
  pre(b != 0)   // 事前条件: 0 で割らない
{
  return a / b;
}
```


## ゲームでの使いどころ

ライブラリや関数の呼び出し側と呼ばれる側の約束を、コードに書いて、破られたときにログを残す仕組みの一部です。テストや開発中のビルドで有効にし、製品では無視する、という使い分けを想定しています。

## よくあるミス

??? failure "自分でインスタンスを作る"
    実装が作って渡す型です。コンストラクターは公開されていません。

??? failure "ハンドラーの中で例外を投げて続行しようとする"
    `noexcept` の関数なら終了します。ハンドラーでできることは、ログの出力などに絞ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`source_location`](source_location.md) | 場所を表す型 |
| [`stacktrace`](stacktrace.md) | 違反の時点の呼び出し履歴を残す |
| [`terminate`](exceptions/terminate.md) | プログラムの終了 |

## コンパイラ対応

C++26 です。手元の MSVC（Visual Studio 2026）では、まだ `<contracts>` が使えないため、このページのサンプルは動かして確かめていません。また、ハンドラーを差し替える方法は、実装ごとに定まります。

## 関連ページ

- [cpprefjp: std::contracts::contract_violation](https://cpprefjp.github.io/reference/contracts/contract_violation.html)
- [cppreference: std::contracts::contract_violation](https://en.cppreference.com/w/cpp/utility/contract_violation)
