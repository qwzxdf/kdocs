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

状態を表示する関数を作るとき、画面に出すのか、ファイルに出すのか、文字列に出すのかで、関数を何通りも作るのは無駄です。`std::ostream` は、出力ストリームの共通の親クラスで、`std::cout`、`std::ofstream`、`std::ostringstream` はすべてこの仲間です。関数の引数を `std::ostream&` にしておけば、画面、ファイル、文字列のどこにも同じ関数で出せます。

!!! tip "ポイント"
    - 出力する関数は `void Dump(std::ostream& os)` と書く。画面もファイルも渡せる。
    - `operator<<(std::ostream&, const T&)` を自作すると、自作の型を `<<` で出せる。
    - ストリームは**参照で**受け取る（コピーできない）。

!!! info "このページを読む前に"
    [`std::ifstream`](ifstream.md) や [`std::cout`](cout.md) など、ストリームの基本を先に読んでください。

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

### std::ostream::put {#put}

```cpp
ostream& put(char_type ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | char | 出力する文字 |

- 戻り値: ストリームへの参照
- 計算量: 定数

1 文字を、書式なしで出力します。`<<` と違い、`setw` などの影響を受けません。

### operator<< {#op_shl}

```cpp
ostream& operator<<(int value);
ostream& operator<<(const std::string& str);
```

- 計算量: O(出力の長さ)

書式つきで出力します。`<<` を続けて書けます（戻り値がストリーム自身のため）。

### write {#write}

```cpp
ostream& write(const char* s, streamsize n);
```

- 計算量: O(n)

`n` バイトを、書式なしで書き込みます（バイナリ用）。

### flush {#flush}

```cpp
ostream& flush();
```

- 計算量: 出力の量に比例

バッファの中身を、出力先に書き出します。

### tellp {#tellp}

```cpp
pos_type tellp();
```

- 計算量: 定数

出力側の現在位置を返します。

### seekp {#seekp}

```cpp
ostream& seekp(pos_type pos);
ostream& seekp(off_type off, ios_base::seekdir dir);
```

- 計算量: 定数

出力側の位置を動かします。書き込み位置を戻して、書き直したいときに使います。

## ゲームでの使いどころ

デバッグ出力の関数に使います。`void Dump(std::ostream& os)` と書けば、画面にもログファイルにも、同じ関数で出せます。

自作の型を `<<` で出せるようにするには、`std::ostream& operator<<(std::ostream& os, const Vec3& v)` を定義します。`std::println("{}", v)` で使うなら、`formatter` を用意します。

ストリームはコピーできないので、参照で受け取ります。戻り値にストリーム自身を返すと、`os << a << b` のようにつなげられます。

## よくあるミス

??? failure "ストリームを値で受け取る"
    コピーできないのでコンパイルエラーです。参照で受け取ります。

??? failure "ストリームをコピーしようとする"
    ストリームはコピーできません。引数は `std::ostream&` と参照で受けます。

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
