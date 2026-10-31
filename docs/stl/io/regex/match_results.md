---
title: std::match_results
summary: "一致の結果（全体とグループ）を保持するクラスの、元になるテンプレート。"
order: 900
tags:
  - 入出力・文字列
---

# std::match_results

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

正規表現の検索が成功すると、知りたいことは「どこが一致したか」だけではありません。グループごとの中身、一致の前に何があったか、後ろに何が残っているか。これらをまとめて持つのが `match_results` です。`m[0]` が全体、`m[1]` 以降が各グループ（`sub_match`）です。

`std::smatch` や `std::cmatch` は、検索対象の種類ごとに用意された、この型の別名です。

!!! tip "ポイント"
    - `m[0]` が一致の全体、`m[1]` 以降が 1 番目以降のグループ
    - `size()` は、グループ数 + 1。一致しなかったときは 0
    - `prefix()` が一致の前、`suffix()` が一致の後ろ
    - `position(n)` が位置、`str(n)` が文字列

!!! info "このページを読む前に"
    [`std::regex_search`](../regex_search.md) と [`std::smatch`](../smatch.md) を先に読んでください。

## 関数の詳しい説明

### std::match_results {#match_results}

```cpp
template <class BidirIt, class Alloc = std::allocator<std::sub_match<BidirIt>>>
class match_results;
```

別名は、検索対象の種類ごとにあります。

| 別名 | 検索対象 |
| --- | --- |
| `std::smatch` | `std::string` |
| `std::cmatch` | `const char*` |
| `std::wsmatch` | `std::wstring` |
| `std::wcmatch` | `const wchar_t*` |

### 状態を調べる {#state}

| 関数 | 意味 |
| --- | --- |
| `empty()` | 一致が見つかっていなければ真 |
| `ready()` | 検索が完了している（結果が入っている）か |
| `size()` | 要素数。成功なら `グループ数 + 1`、失敗なら 0 |

検索が失敗したときは、`size()` が 0 になり、`m[0]` を参照しても、範囲外ではなく空の `sub_match` が返ります。

### 要素を取り出す {#element}

`m[n]` は、n 番目のグループの `sub_match` を返します。`n` が範囲外のときは、一致しなかった空の `sub_match` です。`m.str(n)` は、`m[n].str()` と同じです。`m.length(n)` は長さです。`m.position(n)` は、検索対象の先頭からの位置です。

### 前後の文字列 {#prefix}

`m.prefix()` は、一致の前の部分、`m.suffix()` は、一致の後ろの部分を、`sub_match` で返します。`suffix()` を次の検索の開始位置にすれば、文字列の中の一致を、順に取り出せます。

### format {#format}

```cpp
std::string format(const std::string& fmt) const;
```

結果を使って、書式に従って文字列を作ります。`$1` で 1 番目のグループ、`$&` で全体、`$`` で一致の前、`$'` で一致の後ろを埋め込みます。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  const std::string s = "id=42; name=Hero";
  const std::regex re(R"((\w+)=(\w+))");

  std::smatch m;
  std::regex_search(s, m, re);

  std::println("size={} empty={}", m.size(), m.empty());
  std::println("全体: {}", m.str(0));
  std::println("グループ 1: {}  グループ 2: {}", m.str(1), m.str(2));
  std::println("位置: {}  長さ: {}", m.position(0), m.length(0));
  std::println("後ろ: {:?}", m.suffix().str());
  std::println("format: {}", m.format("$2=$1"));
}
```

```text title="実行結果"
size=3 empty=false
全体: id=42
グループ 1: id  グループ 2: 42
位置: 0  長さ: 5
後ろ: "; name=Hero"
format: 42=id
```

`suffix()` が、一致の後ろの `; name=Hero` を返しています。

## ゲームでの使いどころ

`key=value` の形の設定ファイルの 1 行や、`move 10 20` のようなコマンドを、グループに分けて取り出します。

## よくあるミス

??? failure "検索に失敗した m を使う"
    `size()` が 0 のときに `m[1]` を参照しても、エラーにはならず、空の `sub_match` が返ります。気づきにくいので、`regex_search` の戻り値を、先に確認します。

??? failure "一時オブジェクトの string を検索する"
    `std::regex_search(func_returning_string(), m, re)` は、削除されたオーバーロードに当たり、コンパイルできません。結果が、破棄された文字列を指してしまうからです。名前のある変数に入れます。

??? failure "m[0] を最初のグループと間違える"
    `m[0]` は全体で、1 番目のグループは `m[1]` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::sub_match`](sub_match.md) | 要素 1 つぶん |
| [`std::smatch`](../smatch.md) | `std::string` 用の別名 |
| [`std::regex_iterator`](regex_iterator.md) | 一致を順に取り出す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `match_results` は、一致の全体とグループを持つ。`m[0]` が全体
    - [x] `prefix()` と `suffix()` で、一致の前後を取れる
    - [x] 検索の戻り値を確認してから使う

## 関連ページ

- [cpprefjp: match_results](https://cpprefjp.github.io/reference/regex/match_results.html)
- [cppreference: std::match_results](https://en.cppreference.com/w/cpp/regex/match_results)
