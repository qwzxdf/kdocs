---
title: std::num_get
summary: "文字列から数値を読み込む処理を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::num_get

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`cin >> n` が内部で呼んでいるのが、`num_get` です。ロケールの規則（小数点・桁区切り）に従って、文字から数値を作ります。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::num_get {#num_get}

```cpp
template <class CharT, class InIt = istreambuf_iterator<CharT>>
class num_get {
 public:
  InIt get(InIt in, InIt end, std::ios_base& str, std::ios_base::iostate& err, long& v) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `in, end` | 入力イテレータ | 読み込み元の範囲 |
| `str` | ios_base& | 書式の設定の元になるストリーム |
| `err` | iostate& | エラーの状態を受け取る |
| `v` | 数値 | 結果を入れる変数 |

- 戻り値: 読み終えた位置の入力イテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("42");
  std::istreambuf_iterator<char> b(in);
  std::istreambuf_iterator<char> e;
  std::ios_base::iostate err = std::ios_base::goodbit;
  long v = 0;
  std::use_facet<std::num_get<char>>(std::locale::classic()).get(b, e, in, err, v);
  std::println("{}", v);
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の入力関数で、ロケール付きの数値を読む |

## よくあるミス

??? failure "`err` を確かめない"
    読み込みの失敗は `err` に入ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`num_put`](num_put.md) | 書き出し側 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列から数値を読み込む処理を担当するファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::num_get](https://cpprefjp.github.io/reference/locale/num_get.html)
- [cppreference: std::num_get](https://en.cppreference.com/w/cpp/locale/num_get)
