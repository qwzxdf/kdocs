---
title: std::ostream
summary: "すべての出力ストリームの共通の親クラス。関数の引数にすると、画面にもファイルにも出せる。"
order: 90
tags:
  - 入出力・文字列
---

# std::ostream

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <ostream>`
</div>

`std::ostream` は、**出力ストリームの共通の親クラス**です。`std::cout`、`std::ofstream`、`std::ostringstream` はすべて `ostream` の仲間です。関数の引数を `std::ostream&` にしておくと、画面にもファイルにも文字列にも、同じ関数で出力できます。`operator<<` を自作するときの、第 1 引数の型でもあります。

!!! tip "ポイント"
    - 出力する関数は `void Dump(std::ostream& os)` と書く。画面もファイルも渡せる。
    - `operator<<(std::ostream&, const T&)` を自作すると、自作の型を `<<` で出せる。
    - ストリームは**参照で**受け取る（コピーできない）。

## 関数の詳しい説明

### std::ostream {#ostream}

```cpp
class ostream {
 public:
  ostream& operator<<(int value);   // 型ごとにある
  ostream& write(const char* s, std::streamsize n);
  ostream& flush();
};
```

- 戻り値: `*this`（`<<` を続けて書ける）
- 計算量: O(出力量)

```cpp
#include <iostream>
#include <print>
#include <sstream>

struct Vec2 {
  int x;
  int y;
};

// 自作の型を << で出せるようにする
std::ostream& operator<<(std::ostream& os, const Vec2& v) {
  return os << '(' << v.x << ", " << v.y << ')';
}

void Dump(std::ostream& os, const Vec2& v) {
  os << "pos=" << v;
}

int main() {
  std::ostringstream out;       // 画面の代わりに文字列へ出す
  Dump(out, Vec2{3, 4});
  std::println("{}", out.str());
}
```

```text title="実行結果"
pos=(3, 4)
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログ関数を、画面にもファイルにも出せるようにする | `void Log(std::ostream& os, ...)` |

## よくあるミス

??? failure "ストリームを値で受け取る"
    コピーできないのでコンパイルエラーです。参照で受け取ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cout`](cout.md) | 画面の ostream |
| [`std::ofstream`](ofstream.md) | ファイルの ostream |
| [`std::formatter`](../utilities/formatter.md) | `println` 用の自作型の対応 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力ストリームの親クラス
    - [x] 関数の引数にすると何にでも出せる
    - [x] 参照で受け取る

## 関連ページ

- [cpprefjp: std::ostream](https://cpprefjp.github.io/reference/ostream/basic_ostream.html)
- [cppreference: std::ostream](https://en.cppreference.com/w/cpp/io/basic_ostream)
