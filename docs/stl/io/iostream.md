---
title: std::iostream
summary: "入力も出力もできるストリームのクラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::iostream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ostream>`
</div>

`std::iostream` は、`istream` と `ostream` の両方を継承した、読み書き両用のクラスです。`fstream` や `stringstream` の土台になります。関数の引数で、読み書き両用のストリームを受け取りたいときに使います。

!!! tip "ポイント"
    - `iostream` は `basic_istream と basic_ostream` から派生。
    - 関数の引数で受けるときは、必要なほう（`istream` か `ostream`）を使う。
    - 関数の引数には、参照で受ける。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::iostream {#iostream}

```cpp
using iostream = /* basic_istream と basic_ostream */;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_class_v<std::iostream>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ストリームを引数で受ける関数 | `void Save(std::ostream& os);` |

## よくあるミス

??? failure "値で受ける"
    ストリームはコピーできません。参照（`&`）で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`istream`](istream.md) | 入力ストリーム |
| [`ostream`](ostream.md) | 出力ストリーム |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力も出力もできるストリームのクラス
    - [x] コピーできないので参照で受ける
    - [x] ふつうは別名を使う

## 関連ページ

- [cpprefjp: std::iostream](https://cpprefjp.github.io/reference/ostream/iostream.html)
- [cppreference: std::iostream](https://en.cppreference.com/w/cpp/io/iostream)
