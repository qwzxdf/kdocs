---
title: 標準の例外（<stdexcept>）
summary: "標準の例外の種類（`runtime_error`、`out_of_range` など）と使い分け。"
order: 86
tags:
  - 型・言語サポート
  - エラー処理
---

# 標準の例外（&lt;stdexcept&gt;）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <stdexcept>` / `#include <exception>`
</div>

C++ の標準ライブラリは、失敗したときに**例外**を投げることがあります（`vector::at` の範囲外、`std::stoi` の変換失敗、filesystem の操作失敗など）。それらの例外の型は、すべて `std::exception` を親とする**決まった階層**になっています。自分で例外を投げるときも、この型を使うか継承すると、受け取る側が `catch (const std::exception& e)` でまとめて扱えます。

!!! tip "ポイント"
    - 受け取るときは **`catch (const std::exception& e)`**（const 参照で）、`e.what()` で説明を取る。
    - 自分で投げるなら `std::runtime_error("説明")` か、それを継承した型。
    - ゲームでは例外を使わない方針も多い（[エラー処理の方針](../../design/foundations/error-handling.md)）。その場合でも、標準ライブラリの例外を投げる関数を知っておく。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 例外の階層

<svg class="fig flow" viewBox="0 0 639 1180" role="img" aria-label="標準の例外の継承関係"><defs><marker id="fl76004" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">標準の例外の継承関係</text><line x1="108.2" y1="605.0" x2="298.8" y2="273.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="154.4" y1="605.0" x2="252.6" y2="567.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="353.0" y1="227.0" x2="495.5" y2="147.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="370.5" y1="239.1" x2="459.0" y2="222.5" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="370.5" y1="260.9" x2="474.5" y2="280.4" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="353.0" y1="273.0" x2="495.5" y2="353.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="373.5" y1="521.0" x2="475.0" y2="483.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="378.0" y1="544.0" x2="474.5" y2="544.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="373.5" y1="567.0" x2="475.0" y2="605.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="154.4" y1="651.0" x2="261.5" y2="692.5" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><line x1="124.7" y1="651.0" x2="282.3" y2="773.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><path d="M95.0,606.0 Q203.5,554.0 312.0,858.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><path d="M95.0,606.0 Q203.5,554.0 312.0,942.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><path d="M95.0,606.0 Q203.5,554.0 312.0,1026.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><path d="M95.0,606.0 Q203.5,554.0 312.0,1110.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl76004)"/><rect x="28.0" y="608.0" width="134" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="95.0" y="628.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">std::exception</text><rect x="256.5" y="230.0" width="111" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="250.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">logic error</text><rect x="249.0" y="524.0" width="126" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="544.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">runtime error</text><rect x="477.5" y="104.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.5" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">out of range</text><rect x="462.0" y="188.0" width="149" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.5" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">invalid argument</text><rect x="477.5" y="272.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.5" y="292.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">length error</text><rect x="477.5" y="356.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.5" y="376.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">domain error</text><rect x="470.5" y="440.0" width="132" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.5" y="460.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">range error 等</text><rect x="477.5" y="524.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.5" y="544.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">system error</text><rect x="477.5" y="608.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.5" y="628.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">format error</text><rect x="264.5" y="692.0" width="95" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="712.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bad alloc</text><rect x="226.0" y="776.0" width="172" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="796.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bad optional access</text><rect x="229.5" y="860.0" width="165" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="880.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bad variant access</text><rect x="233.5" y="944.0" width="157" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="964.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bad function call</text><rect x="253.0" y="1028.0" width="118" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="1048.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bad any cast</text><rect x="226.0" y="1112.0" width="172" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="312.0" y="1132.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bad expected access</text></svg>

| 例外 | いつ出るか |
| --- | --- |
| `logic_error` | プログラムのミス（事前に防げるもの） |
| `out_of_range` | `vector::at`、`string::substr` の範囲外 |
| `invalid_argument` | `std::stoi` に数字でない文字列 |
| `length_error` | `vector::reserve` が大きすぎる |
| `runtime_error` | 実行してみないと分からないもの |
| `system_error` | OS のエラー（`filesystem_error` はこの子） |
| `format_error` | `vformat` の書式間違い |
| `bad_alloc` | メモリ不足 |
| `bad_optional_access` | `optional::value()` で値なし |
| `bad_variant_access` | `std::get` で型違い |
| `bad_function_call` | 空の `std::function` を呼んだ |
| `bad_any_cast` | `any_cast` で型違い |
| `bad_expected_access` | `expected::value()` でエラー |

## 型一覧

| 型 | 重要度 | 投げられる場面 |
| --- | --- | --- |
| [`std::exception`](exceptions/exception.md) | <span class="rank rank-sometimes">たまに</span> | すべての親。catch でまとめて受け取る |
| [`std::runtime_error`](exceptions/runtime_error.md) | <span class="rank rank-sometimes">たまに</span> | 自分で投げるときの定番 |
| [`std::out_of_range`](exceptions/out_of_range.md) | <span class="rank rank-sometimes">たまに</span> | `at()`、`substr`、`stoi` の範囲外 |
| [`std::invalid_argument`](exceptions/invalid_argument.md) | <span class="rank rank-sometimes">たまに</span> | `stoi` などに変換できない文字列 |
| [`std::logic_error`](exceptions/logic_error.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラムのミスを表す親 |
| [`std::bad_alloc`](exceptions/bad_alloc.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリ確保の失敗 |
| [`std::system_error`](exceptions/system_error.md) | <span class="rank rank-rare">知ってるだけ</span> | OS のエラー（エラーコード付き） |
| [`std::exception_ptr`](exceptions/exception_ptr.md) | <span class="rank rank-rare">知ってるだけ</span> | 例外を保存して、別の場所で投げ直す |

## よくある使い方

```cpp
#include <print>
#include <stdexcept>
#include <string>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  try {
    std::println("{}", v.at(10));
  } catch (const std::out_of_range& e) {  // 細かい型から先に書く
    std::println("範囲外");
  } catch (const std::exception& e) {     // その他全部
    std::println("その他: {}", e.what());
  }

  try {
    std::stoi("abc");
  } catch (const std::invalid_argument&) {
    std::println("数字ではない");
  }
}
```

```text title="実行結果"
範囲外
数字ではない
```

## フラグ・オプション

| 書き方 | 意味 |
| --- | --- |
| `catch (...)` | どんな例外でも受け取る（型は分からない） |
| `throw;` | 今受け取った例外をそのまま投げ直す |
| `noexcept` | この関数は例外を投げないと約束する（投げると `std::terminate`） |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 例外を使うプロジェクトの読み込み処理 | ファイル形式のエラーを runtime_error で投げ、ロード画面でまとめて受け取る |
| 例外を使わないプロジェクト | 例外を投げる標準関数（`at`、`stoi`、filesystem）を避ける |

## よくあるミス

??? failure "値で catch する"
    `catch (std::exception e)` は、派生クラスの部分が切り落とされて（スライシング）`what()` の説明が変わることがあります。必ず `const&` で受け取ります。

??? failure "catch の順番が逆"
    親の型（`std::exception`）を先に書くと、子の型（`std::out_of_range`）の catch には来ません。細かい型から順に書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] すべての親は std::exception。const& で受けて what()
    - [x] 自分で投げるなら runtime_error
    - [x] catch は細かい型から

## 関連ページ

- [エラー処理の方針](../../design/foundations/error-handling.md)
- [cppreference: Exceptions](https://en.cppreference.com/w/cpp/error/exception)
