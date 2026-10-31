---
title: std::collate
summary: "文字列の照合（辞書順の比較）を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::collate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

英語なら、文字コードの順で並べれば、ほぼ辞書順になります。でも、フランス語の `é` や、ドイツ語の `ä` は、辞書では `e` や `a` の近くに並べたいはずです。言語ごとの辞書順に、文字列を比べる部品が `std::collate` です。`std::locale` を比較関数のように使って、`std::sort` に渡す方法でも利用されます。

!!! tip "ポイント"
    - `compare` は、`-1`（小さい）、`0`（等しい）、`1`（大きい）を返す
    - 文字コードの順ではなく、ロケールの辞書順で比べる
    - `"C"` ロケールでは、文字コードの順と同じ
    - `std::locale` 自身が `operator()` を持ち、並べ替えの比較関数として渡せる

!!! info "このページを読む前に"
    [`std::use_facet`](use_facet.md) を先に読んでください。

## 関数の詳しい説明

### std::collate {#collate}

```cpp
template <class CharT>
class collate {
 public:
  int compare(const CharT* lo1, const CharT* hi1,
              const CharT* lo2, const CharT* hi2) const;
  std::basic_string<CharT> transform(const CharT* lo, const CharT* hi) const;
  long hash(const CharT* lo, const CharT* hi) const;
};
```

### compare {#compare}

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `lo1, hi1` | `const CharT*` | 1 つ目の文字列の範囲 `[lo1, hi1)` |
| `lo2, hi2` | `const CharT*` | 2 つ目の文字列の範囲 `[lo2, hi2)` |

2 つの範囲を、ロケールの辞書順で比べます。1 つ目が先に来るなら `-1`、同じなら `0`、後なら `1` を返します。`strcmp` と違い、返す値は `-1`、`0`、`1` のどれかに決まっています。

文字列ではなく、ポインタの組を受け取るのは、終端のない文字列や、一部だけを比べるためです。`std::string` なら、`s.data()` と `s.data() + s.size()` を渡します。

### transform と hash {#transform}

`transform` は、文字列を「`strcmp` で比べるだけで辞書順になる」文字列に変換します。同じ文字列を何度も比べるとき、先に変換しておけば、毎回ロケールの規則を適用しなくて済みます。`hash` は、`compare` が 0 を返す文字列どうしで、同じ値になるハッシュ値を返します。

### 並べ替えに使う {#sort}

`std::locale` は、`operator()(const basic_string&, const basic_string&)` を持っています。内部で `collate` を使って、辞書順の比較を行います。

```cpp
std::sort(names.begin(), names.end(), std::locale("ja_JP.UTF-8"));
```

指定した名前のロケールがインストールされていないと、`std::locale` のコンストラクターが `std::runtime_error` を投げます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <locale>
#include <print>
#include <string>
#include <vector>

int main() {
  const char a[] = "a";
  const char b[] = "b";
  const auto& co = std::use_facet<std::collate<char>>(std::locale::classic());
  std::println("a と b: {}", co.compare(a, a + 1, b, b + 1));
  std::println("b と a: {}", co.compare(b, b + 1, a, a + 1));
  std::println("a と a: {}", co.compare(a, a + 1, a, a + 1));

  // classic ロケールを比較関数にして並べ替える
  std::vector<std::string> names = {"orc", "elf", "dwarf"};
  std::sort(names.begin(), names.end(), std::locale::classic());
  std::println("{} {} {}", names[0], names[1], names[2]);
}
```

```text title="実行結果"
a と b: -1
b と a: 1
a と a: 0
dwarf elf orc
```

## ゲームでの使いどころ

アイテム名やキャラクター名の並べ替えで、言語ごとの辞書順にしたいときに使います。日本語の五十音順は、ロケールが対応していても、環境ごとに結果が変わるので、ゲームでは、読み仮名のデータを別に持って並べることが多いです。

## よくあるミス

??? failure "C ロケールで辞書順を期待する"
    `"C"` ロケールの `collate` は文字コードの順です。大文字がすべて小文字より先に来ます。言語の辞書順にするには、そのロケールを使います。

??? failure "存在しないロケール名を渡して例外が飛ぶ"
    `std::locale("ja_JP.UTF-8")` は、環境にそのロケールがなければ `std::runtime_error` を投げます。try で囲むか、環境に依存しない方法を選びます。

## 類似

| 名前 | 違い |
| --- | --- |
| `strcoll` | C のロケールで比べる関数 |
| `strcmp` | 文字コードの順で比べる |
| [`use_facet`](use_facet.md) | ファセットを取り出す |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `collate::compare` は、ロケールの辞書順で文字列を比べる
    - [x] `-1`、`0`、`1` を返す。`"C"` ロケールは文字コードの順
    - [x] `std::locale` を比較関数として `std::sort` に渡せる

## 関連ページ

- [cpprefjp: collate](https://cpprefjp.github.io/reference/locale/collate.html)
- [cppreference: std::collate](https://en.cppreference.com/w/cpp/locale/collate)
