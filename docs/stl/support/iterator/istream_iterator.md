---
title: std::istream_iterator
summary: "入力ストリームから、値を 1 つずつ読むイテレータ。"
order: 15
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::istream_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::cin` やファイルから、数値を次々に読み取って、`vector` に詰めたい。`while (cin >> x) v.push_back(x);` と書くところを、`std::istream_iterator` を使うと、アルゴリズムの入力として渡せます。

!!! tip "ポイント"
    - `std::istream_iterator<T>(stream)` は、ストリームから `T` を読み取る入力イテレーター
    - 引数なしで作ると、終端を表す
    - `std::vector` のコンストラクターなどに、範囲として渡せる
    - 空白区切りで読み取る

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::istream_iterator {#istream_iterator}

<span class="ver ver-98">C++98</span>

```cpp
template <class T>
class istream_iterator {
 public:
  istream_iterator();
  explicit istream_iterator(std::istream& stream);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | 入力ストリーム | 読み取り元 |

`*it` で現在の値を読み、`++it` で次の値を読み取ります。読み取りに失敗する（終端に達する）と、引数なしで作った終端のイテレーターと等しくなります。

入力イテレーターなので、1 回しか読めません。`vector` のコンストラクターに範囲として渡すと、全部読み取って詰められます。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <numeric>
#include <print>
#include <sstream>
#include <vector>

int main() {
  std::istringstream input("1 2 3 4");
  std::vector<int> v((std::istream_iterator<int>(input)), std::istream_iterator<int>());
  std::println("要素数 = {}", v.size());
  std::println("合計   = {}", std::accumulate(v.begin(), v.end(), 0));
}
```

```text title="実行結果"
要素数 = 4
合計   = 10
```

## ゲームでの使いどころ

数値の羅列を、まとめて読み込みます。

```cpp
std::vector<int> values((std::istream_iterator<int>(file)), std::istream_iterator<int>());
```

最初の引数を括弧で囲んでいるのは、関数宣言と解釈されるのを避けるためです。

## よくあるミス

??? failure "最初の引数を括弧で囲まず、関数宣言と解釈される"
    `std::vector<int> v((std::istream_iterator<int>(in)), {})` のように括弧を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ostream_iterator`](ostream_iterator.md) | 出力版 |
| [`istreambuf_iterator`](istreambuf_iterator.md) | 1 文字ずつ読む |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `istream_iterator<T>(s)` はストリームから `T` を読む入力イテレーター
    - [x] 引数なしは終端
    - [x] 空白区切りで読む

## 関連ページ

- [cpprefjp: std::istream_iterator](https://cpprefjp.github.io/reference/iterator/istream_iterator.html)
- [cppreference: std::istream_iterator](https://en.cppreference.com/w/cpp/iterator/istream_iterator)
