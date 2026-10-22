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

`cout << 42` が内部で呼んでいるのが、`num_put` です。ロケールの規則（小数点・桁区切り）に従って、数値を文字にして出力先に流します。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::num_put {#num_put}

```cpp
template <class CharT, class OutIt = ostreambuf_iterator<CharT>>
class num_put {
 public:
  OutIt put(OutIt out, std::ios_base& str, CharT fill, long v) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `out` | 出力イテレータ | 書き出し先 |
| `str` | ios_base& | 書式の設定の元になるストリーム |
| `fill` | 文字 | 幅を埋める文字 |
| `v` | 数値 | 書く値 |

- 戻り値: 書き終えた後の出力イテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  std::ostringstream os;
  const auto& np = std::use_facet<std::num_put<char>>(std::locale::classic());
  np.put(std::ostreambuf_iterator<char>(os), os, ' ', 42L);
  std::println("{}", os.str());
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の出力関数で、ロケール付きの数値を書く |

## よくあるミス

??? failure "直接使う"
    ふつうは `<<` を使います。`num_put` は、自作の書式に拡張するときに登場します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`num_get`](num_get.md) | 読み込み側 |
| [`numpunct`](numpunct.md) | 書式の記号 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数値を文字列に書き出す処理を担当するファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::num_put](https://cpprefjp.github.io/reference/locale/num_put.html)
- [cppreference: std::num_put](https://en.cppreference.com/w/cpp/locale/num_put)
