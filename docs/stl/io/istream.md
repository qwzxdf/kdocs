---
title: std::istream
summary: "すべての入力ストリームの共通の親クラス。関数の引数にすると、キーボードにもファイルにも対応できる。"
order: 91
tags:
  - 入出力・文字列
---

# std::istream

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <istream>`
</div>

`std::istream` は、**入力ストリームの共通の親クラス**です。`std::cin`、`std::ifstream`、`std::istringstream` はすべて `istream` の仲間です。読み込む関数の引数を `std::istream&` にしておくと、キーボード・ファイル・文字列のどれからでも読めて、テストも簡単になります。

!!! tip "ポイント"
    - 読み込み関数は `bool Load(std::istream& in)` と書く。テストでは `istringstream` を渡せる。
    - `operator>>(std::istream&, T&)` を自作すると、自作の型を `>>` で読める。
    - 失敗は `failbit`。`if (in)` で確認する。

## 関数の詳しい説明

### std::istream {#istream}

```cpp
class istream {
 public:
  istream& operator>>(int& value);   // 型ごとにある
  istream& read(char* s, std::streamsize n);
  istream& ignore(std::streamsize n = 1, int delim = EOF);
};
```

- 戻り値: `*this`（`>>` を続けて書ける）
- 計算量: O(読み込み量)

```cpp
#include <iostream>
#include <print>
#include <sstream>

struct Vec2 {
  int x = 0;
  int y = 0;
};

std::istream& operator>>(std::istream& is, Vec2& v) {
  return is >> v.x >> v.y;
}

bool Load(std::istream& in, Vec2& out) {
  return static_cast<bool>(in >> out);
}

int main() {
  std::istringstream in("3 4");   // ファイルの代わりに文字列から読む（テストが簡単）
  Vec2 v;
  if (Load(in, v)) {
    std::println("{} {}", v.x, v.y);
  }
}
```

```text title="実行結果"
3 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの読み込みを、ファイルなしでテストする | `Load(std::istringstream{"..."})` |

## よくあるミス

??? failure "失敗を確認しない"
    `if (in >> x)` で確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cin`](cin.md) | 標準入力の istream |
| [`std::ifstream`](ifstream.md) | ファイルの istream |
| [`std::ostream`](ostream.md) | 出力側 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力ストリームの親クラス
    - [x] 関数の引数にするとテストしやすい
    - [x] 失敗は `if (in)` で確認

## 関連ページ

- [cpprefjp: std::istream](https://cpprefjp.github.io/reference/istream/basic_istream.html)
- [cppreference: std::istream](https://en.cppreference.com/w/cpp/io/basic_istream)
