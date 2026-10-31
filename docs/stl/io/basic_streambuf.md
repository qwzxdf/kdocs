---
title: std::basic_streambuf
summary: "ストリームバッファの元になるテンプレート（`streambuf` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_streambuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <streambuf>`
</div>

`std::cout << "hello"` と書いたとき、文字が実際に画面へ出るまでには、いくつかの段階があります。`<<` で値を文字に直すのは `ostream` ですが、その文字を溜めて、画面やファイルに送るのは、ストリームの裏にいる別のオブジェクトです。それが<strong>ストリームバッファ</strong>、つまり `basic_streambuf` の仲間です。

役割を分けてあるので、ストリームはそのままで、バッファだけ差し替えられます。`cout` の出力先を文字列に変える、ログをファイルとコンソールの両方に出す、ネットワークに送る。こうした「出力先を作る」ときに、`basic_streambuf` を継承します。`std::streambuf` は `basic_streambuf<char>` の別名です。

!!! tip "ポイント"
    - `ostream` や `istream` は、文字を整形する担当。実際に読み書きする担当が `streambuf`
    - `rdbuf()` で取り出し、別のバッファに付け替えられる。付け替えたら、必ず元に戻す
    - 自作するときは、出力なら `overflow`（と `xsputn`）、入力なら `underflow` を書く
    - 普段は `stringbuf` と `filebuf` を使うだけで、自作することは少ない

!!! info "このページを読む前に"
    [`std::ostream`](ostream.md) と [`std::istream`](istream.md) を先に読んでください。ストリームの側から、`rdbuf` で触る方法を書いています。

## 関数の詳しい説明

### std::basic_streambuf {#basic_streambuf}

```cpp
template <class CharT, class Traits = std::char_traits<CharT>>
class basic_streambuf;
```

内部は、3 つの領域（入力の読み出し用、出力の書き込み用、ロケール）を持つ構造です。書き込みの領域（put area）が満杯になるか、バッファがない場合、`overflow` という仮想関数が呼ばれます。読み出しの領域（get area）が空になると、`underflow` が呼ばれます。この 2 つに「文字を実際の入出力先へ送る」「入出力先から文字を補充する」処理を書くのが、自作の基本です。

外から使う関数（`sputc`、`sgetc`、`sbumpc`、`pubsync` など）は `s` や `pub` で始まり、公開されています。これらは、バッファに余裕があればそのまま処理し、なければ仮想関数を呼びます。派生クラスが上書きするのは、`s` なしの保護された仮想関数（`overflow`、`underflow`、`sync`、`xsputn` など）です。公開側と保護側で名前が対になっています。

個々の関数は、[`std::streambuf`](streambuf.md) のページに書いています。

### 出力先を自作する {#custom}

`overflow` だけを上書きすると、最小の出力先が作れます。バッファを持たないので、1 文字書くたびに `overflow` が呼ばれます。

```cpp
class LineCounter : public std::streambuf {
 public:
  int lines() const { return lines_; }

 protected:
  // 1 文字書くたびに呼ばれる。改行を数えるだけで、実際の出力はしない
  int_type overflow(int_type ch) override {
    if (!traits_type::eq_int_type(ch, traits_type::eof()) && ch == '\n') {
      ++lines_;
    }
    return traits_type::not_eof(ch);  // 成功を知らせる
  }

 private:
  int lines_ = 0;
};
```

戻り値の `traits_type::not_eof(ch)` は、「成功した」ことを知らせる決まった書き方です。`eof()` を返すと、ストリームは失敗状態になります。

```cpp
#include <ostream>
#include <print>
#include <streambuf>

class LineCounter : public std::streambuf {
 public:
  int lines() const { return lines_; }

 protected:
  int_type overflow(int_type ch) override {
    if (!traits_type::eq_int_type(ch, traits_type::eof()) && ch == '\n') {
      ++lines_;
    }
    return traits_type::not_eof(ch);
  }

 private:
  int lines_ = 0;
};

int main() {
  LineCounter counter;
  std::ostream os(&counter);  // counter を出力先にしたストリーム
  os << "HP 30\n"
     << "MP 12\n"
     << "LV 5\n";
  std::println("{} 行", counter.lines());
}
```

```text title="実行結果"
3 行
```

`std::ostream os(&counter)` で、自作のバッファを持つストリームが作れます。`<<` が整形した文字は、すべて `overflow` を通って、改行だけが数えられました。

## ゲームでの使いどころ

ログを画面（Visual Studio の出力）とファイルの両方に流す、`cout` への出力をゲーム内コンソールに表示する、といった用途で自作します。ただし、ゲームのログは専用の仕組みに集めることが多く、`streambuf` を直接作る機会は多くありません。

`cout` の出力を一時的に文字列に取り込むだけなら、自作は不要です。`std::ostringstream` の `rdbuf()` を、`cout.rdbuf()` に渡します。

## よくあるミス

??? failure "付け替えたまま戻さない"
    `cout.rdbuf(別のバッファ)` で付け替えたら、スコープを抜ける前に必ず元に戻します。戻さずに別のバッファが破棄されると、`cout` が壊れたバッファを指したままになり、プログラムの終了時にクラッシュします。

??? failure "overflow が eof を返して、ストリームが壊れる"
    成功したのに `eof()` を返すと、ストリームが失敗状態になり、以降の出力が全部無視されます。成功時は `not_eof(ch)` を返します。

??? failure "デストラクターで出力が残る"
    バッファを持つ自作の `streambuf` は、デストラクターで残りを `sync` します。呼び忘れると、最後の数文字が出ません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::streambuf`](streambuf.md) | `basic_streambuf<char>` の別名。関数の説明はこちら |
| [`std::stringbuf`](stringbuf.md) | メモリ上の文字列を入出力先にする |
| [`std::filebuf`](filebuf.md) | ファイルを入出力先にする |
| [`std::syncbuf`](syncbuf.md) | スレッドから書いても混ざらない |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ストリームの裏で、実際に読み書きするのが `streambuf`
    - [x] `rdbuf()` で付け替えられる。付け替えたら必ず元に戻す
    - [x] 自作は、出力なら `overflow`、入力なら `underflow` を上書きする

## 関連ページ

- [cpprefjp: std::basic_streambuf](https://cpprefjp.github.io/reference/streambuf/basic_streambuf.html)
- [cppreference: std::basic_streambuf](https://en.cppreference.com/w/cpp/io/basic_streambuf)
