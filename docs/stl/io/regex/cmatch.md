---
title: std::cmatch
summary: "C 文字列用の match_results。"
order: 900
tags:
  - 入出力・文字列
---

# std::cmatch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::smatch` は `std::string` を検索したときの結果を入れる型でした。`const char*` の C 文字列を検索するときは、対応する `std::cmatch` を使います。`match_results<const char*>` の別名で、`m[n]` の型は `std::csub_match` です。

!!! tip "ポイント"
    - `match_results<const char*>` の別名
    - C 文字列やリテラルを検索するときに使う
    - `std::string` を検索するなら `std::smatch`
    - 一時オブジェクトの制限（削除されたオーバーロード）は、`const char*` にはない

!!! info "このページを読む前に"
    [`std::match_results`](match_results.md) を先に読んでください。

## 関数の詳しい説明

### std::cmatch {#cmatch}

```cpp
using cmatch = match_results<const char*>;
```

機能は `match_results` と同じです。`m[n]`、`m.size()`、`m.prefix()`、`m.suffix()`、`m.position(n)` などが使えます。`m[n]` が返すのは `csub_match` で、`first` と `second` は `const char*` です。

`regex_search(const char*, cmatch&, const regex&)` の形で使います。`std::string` を渡すなら、`smatch` を使い、`c_str()` を渡して `cmatch` で受けることもできますが、`std::string` のまま検索したほうが、分かりやすくなります。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  const char* s = "x=5";
  std::cmatch m;
  const std::regex re(R"((\w)=(\d))");

  if (std::regex_search(s, m, re)) {
    std::println("size={}", m.size());
    std::println("名前: {}  値: {}", m[1].str(), m[2].str());
  }
}
```

```text title="実行結果"
size=3
名前: x  値: 5
```

## ゲームでの使いどころ

コマンドライン引数の `argv[i]` のように、もともと C 文字列で来る入力を検査するときに使います。

## よくあるミス

??? failure "smatch と cmatch を取り違える"
    `std::string` を検索するのに `cmatch` を渡す、またはその逆は、型が合わずコンパイル エラーです。検索対象に合わせます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::smatch`](../smatch.md) | `std::string` 用 |
| [`std::wcmatch`](wcmatch.md) | `const wchar_t*` 用 |
| [`match_results`](match_results.md) | 元のテンプレート |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cmatch` は、`const char*` を検索した結果を入れる型
    - [x] `m[n]` は `csub_match`
    - [x] `std::string` なら `smatch`

## 関連ページ

- [cpprefjp: cmatch](https://cpprefjp.github.io/reference/regex/cmatch.html)
- [cppreference: std::cmatch](https://en.cppreference.com/w/cpp/regex/match_results)
