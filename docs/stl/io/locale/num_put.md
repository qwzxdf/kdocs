---
title: std::num_put
summary: "数値を文字列に書き出す処理を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::num_put

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`std::cout << 42` と書いたとき、数値の 42 を `"42"` という文字に直しているのは、ストリームではなく、ロケールの部品である `std::num_put` です。進数（`hex`）、幅（`setw`）、桁数（`setprecision`）、桁区切りなどの設定を読み取って、文字を作ります。

普段は `<<` を通して間接的に使っているので、直接呼ぶことはほとんどありません。自作の `num_put` を差し込んで、出力のしかたを変えたい場面で意味があります。

!!! tip "ポイント"
    - `operator<<` は、内部で `num_put::put` を呼んでいる
    - 書式はストリーム（`ios_base`）の設定から読む。第 2 引数に渡す
    - 出力先は、出力イテレータ（`ostreambuf_iterator` など）
    - `bool`、整数、浮動小数点数、ポインタごとに `put` のオーバーロードがある

!!! info "このページを読む前に"
    [`std::numpunct`](numpunct.md) と [`std::use_facet`](use_facet.md) を先に読んでください。

## 関数の詳しい説明

### std::num_put {#num_put}

```cpp
template <class CharT, class OutIt = std::ostreambuf_iterator<CharT>>
class num_put {
 public:
  OutIt put(OutIt out, std::ios_base& str, CharT fill, long v) const;
  // bool, unsigned long, long long, double, long double, const void* にも
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | `OutIt` | 書き出し先の出力イテレータ |
| `str` | `std::ios_base&` | 書式の設定（進数、幅、桁数）を持つストリーム |
| `fill` | `CharT` | 幅を埋める文字 |
| `v` | 数値 | 書く値 |

`str` に設定されたフラグを見て、数値を整形します。`std::hex` が設定されていれば 16 進、`std::showpos` なら `+` を付ける、といった具合です。ストリームの設定を読むだけで、書き換えません。

戻り値は、書き終えたあとの出力イテレータです。続けて書くときに、これを次の `out` として渡します。

出力は、`numpunct` の規則（小数点、桁区切り）に従います。幅が設定されていれば、`fill` で埋めて揃えます。`setw` の指定は、`put` が 1 回呼ばれるたびに、0 に戻ります。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  const auto& np = std::use_facet<std::num_put<char>>(std::locale::classic());

  std::ostringstream os;
  np.put(std::ostreambuf_iterator<char>(os), os, ' ', 42L);
  std::println("10 進: {}", os.str());

  std::ostringstream hex_out;
  hex_out << std::hex;  // 書式の設定を 16 進にする
  np.put(std::ostreambuf_iterator<char>(hex_out), hex_out, ' ', 255L);
  std::println("16 進: {}", hex_out.str());
}
```

```text title="実行結果"
10 進: 42
16 進: ff
```

`put` は、ストリームのフラグ（`hex`）を読むだけです。ストリームを通さずに、`put` を直接呼んでも、同じ書式で整形できます。

## ゲームでの使いどころ

自作の出力ストリーム用に、数値を特定の書式で書くファセットを差し込む用途が考えられます。ゲーム開発では、`std::format` で書式を指定するほうが簡単なので、`num_put` を直接扱うことは多くありません。

## よくあるミス

??? failure "出力イテレータを使い回さない"
    `put` の戻り値は、続きの書き込み位置です。連続して書くなら、戻り値を次の `out` に渡します。同じイテレータに繰り返し渡すと、上書きになることがあります。

??? failure "ストリームの設定が、前の出力のまま残っている"
    `hex` や `setprecision` は残ります。`put` に渡す `str` の設定が、意図したものかを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`num_get`](num_get.md) | 逆方向。文字列から数値を読む |
| [`numpunct`](numpunct.md) | 小数点や桁区切りの規則 |
| `std::to_chars` | ロケールに依存せず、数値を文字にする。速い |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `num_put` は、`<<` の裏で数値を文字にする部品
    - [x] 書式はストリームの設定から読み、`numpunct` の規則に従う
    - [x] 直接使うことは少ない。数値の変換だけなら `std::to_chars`

## 関連ページ

- [cpprefjp: num_put](https://cpprefjp.github.io/reference/locale/num_put.html)
- [cppreference: std::num_put](https://en.cppreference.com/w/cpp/locale/num_put)
