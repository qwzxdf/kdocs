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

設定の読み込み関数を作るとき、ファイルから読むのか、文字列から読むのかで、関数を 2 つ作るのは無駄です。`std::istream` は、入力ストリームの共通の親クラスで、`std::cin`、`std::ifstream`、`std::istringstream` はすべてこの仲間です。読み込む関数の引数を `std::istream&` にしておけば、キーボード、ファイル、文字列のどれからでも読めます。

!!! tip "ポイント"
    - 読み込み関数は `bool Load(std::istream& in)` と書く。テストでは `istringstream` を渡せる。
    - `operator>>(std::istream&, T&)` を自作すると、自作の型を `>>` で読める。
    - 失敗は `failbit`。`if (in)` で確認する。

!!! info "このページを読む前に"
    [`std::ifstream`](ifstream.md) や [`std::cout`](cout.md) など、ストリームの基本を先に読んでください。

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

### std::istream::peek {#peek}

```cpp
int_type peek();
```

- 戻り値: 次の 1 文字（読み進めない）。終端なら `EOF`
- 計算量: 定数

次に読む文字を、消費せずにのぞきます。次の文字によって読み方を切り替えたいときに使います。

### std::istream::unget {#unget}

```cpp
istream& unget();
```

- 戻り値: ストリームへの参照
- 計算量: 定数

直前に読んだ 1 文字を戻して、もう一度読めるようにします。戻せないときは `badbit` が立ちます。

### std::istream::putback {#putback}

```cpp
istream& putback(char_type ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | char | 戻す文字 |

- 戻り値: ストリームへの参照
- 計算量: 定数

直前に読んだ文字として、指定した文字を戻します。`unget` と違い、戻す文字を指定できます。

### std::istream::readsome {#readsome}

```cpp
streamsize readsome(char_type* s, streamsize n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | char* | 読み込み先 |
| `n` | streamsize | 読む最大の文字数 |

- 戻り値: 読んだ文字数
- 計算量: O(n)

バッファに**すでにある**文字だけを、待たずに読みます。ブロックしたくないときに使います。

### std::istream::sync {#sync}

```cpp
int sync();
```

- 戻り値: 成功なら 0、失敗なら -1
- 計算量: 実装による

入力バッファを、ソース（ファイルや端末）と同期します。標準入力の読み残しを捨てる用途は、実装によって動作が違うので、`ignore` を使います。

### operator>> {#op_shr}

```cpp
istream& operator>>(int& value);
istream& operator>>(std::string& str);
```

- 計算量: O(読んだ文字数)

書式つきで読み込みます。空白を区切りとして読み飛ばします。失敗すると `failbit` が立ちます。

### get {#get}

```cpp
int get();
istream& get(char& ch);
istream& get(char* s, streamsize n, char delim = '\n');
```

- 計算量: O(読んだ文字数)

空白や改行も含めて、1 文字（または複数文字）を、書式なしで読みます。

### getline {#getline}

```cpp
istream& getline(char* s, streamsize n, char delim = '\n');
```

- 計算量: O(読んだ文字数)

区切り文字（既定は改行）まで、1 行を読みます。区切り文字は読み捨てます。`std::string` に読むなら、自由関数の `std::getline` を使います。

### read {#read}

```cpp
istream& read(char* s, streamsize n);
```

- 計算量: O(n)

ちょうど `n` バイトを、書式なしで読みます（バイナリ用）。足りなければ `failbit` と `eofbit` が立ちます。

### ignore {#ignore}

```cpp
istream& ignore(streamsize count = 1, int_type delim = EOF);
```

- 計算量: O(count)

最大 `count` 文字を読み飛ばします。`delim` に当たったら、それも読んで止まります。

### gcount {#gcount}

```cpp
streamsize gcount() const;
```

- 計算量: 定数

直前の書式なしの読み込み（`get`・`getline`・`read`・`ignore`）で、読んだ文字数。

### tellg {#tellg}

```cpp
pos_type tellg();
```

- 計算量: 定数

入力側の現在位置を返します。`seekg` で戻るときの目印になります。

### seekg {#seekg}

```cpp
istream& seekg(pos_type pos);
istream& seekg(off_type off, ios_base::seekdir dir);
```

- 計算量: 定数

入力側の位置を動かします。ファイルの途中から読み直したいときに使います。

## ゲームでの使いどころ

読み込み関数の引数に使います。`bool Load(std::istream& in)` と書けば、実際のファイルからも、テスト用の文字列からも、同じ関数で読めます。テストでは `std::istringstream` を渡すだけです。

自作の型を `>>` で読めるようにするには、`std::istream& operator>>(std::istream& in, Vec3& v)` を定義します。

ストリームはコピーできないので、参照で受け取ります。読み込みの失敗は `failbit` で示されるので、`if (in)` で確かめます。

## よくあるミス

??? failure "失敗を確認しない"
    `if (in >> x)` で確認します。

??? failure "ストリームをコピーしようとする"
    ストリームはコピーできません。引数は `std::istream&` と参照で受けます。

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
