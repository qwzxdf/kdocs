---
title: std::time_get
summary: "日時を、書式に従って文字列から読み込むファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::time_get

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

`get_time` が内部で使っているのが `time_get` です。ロケールの規則に従って、文字列から `tm` を作ります。

!!! tip "ポイント"
    - ロケール（言語・地域ごとの規則）の部品。
    - ふつうは `std::locale` 経由で使う。
    - ゲームのローカライズでは、書式（日付・数字）に関わる。

!!! info "このページを読む前に"
    [`std::locale`](../locale.md) を先に読んでください。

## 関数の詳しい説明

### std::time_get {#time_get}

```cpp
template <class CharT, class InIt = istreambuf_iterator<CharT>>
class time_get {
 public:
  InIt get_time(InIt in, InIt end, std::ios_base& str, std::ios_base::iostate& err, std::tm* t) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `in, end` | 入力イテレータ | 読み込み元の範囲 |
| `err` | iostate& | エラーの状態を受け取る |
| `t` | tm* | 結果を入れる変数 |

- 戻り値: 読み終えた位置の入力イテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <iterator>
#include <locale>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("12:30:45");
  std::istreambuf_iterator<char> b(in);
  std::istreambuf_iterator<char> e;
  std::tm t{};
  std::ios_base::iostate err = std::ios_base::goodbit;
  std::use_facet<std::time_get<char>>(std::locale::classic()).get_time(b, e, in, err, &t);
  std::println("{} {} {}", t.tm_hour, t.tm_min, t.tm_sec);
}
```

```text title="実行結果"
12 30 45
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ロケールに従った日時の入力 |

## よくあるミス

??? failure "直接使う"
    ふつうは `std::get_time` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`get_time`](../get_time.md) | ストリームから読む |
| [`time_put`](time_put.md) | 書き出し側 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日時を、書式に従って文字列から読み込むファセット
    - [x] ロケール（言語・地域ごとの規則）の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::time_get](https://cpprefjp.github.io/reference/locale/time_get.html)
- [cppreference: std::time_get](https://en.cppreference.com/w/cpp/locale/time_get)
