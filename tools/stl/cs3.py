"""cstdio の書き直し（バッチ 3: 1 文字の入出力、書式、ファイル操作）。"""
from rw import rewrite

C = 'stl/io/cstdio/'

rewrite(C + 'fgetc.md',
  intro="""テキスト ファイルを 1 文字ずつ読んで、自作の字句解析（トークナイザー）に渡したい。行ごとでも、バイト数ごとでもなく、<strong>1 文字ずつ取り出す</strong>のが `std::fgetc` です。""",
  tips=["戻り値は `int`。文字は `unsigned char` の値として返り、終わりかエラーのときは `EOF`（負の値）",
        "戻り値を `char` に入れると、`EOF` と区別できなくなる。`int` で受ける",
        "1 回呼ぶごとに、読み込み位置が 1 つ進む",
        "`getc` は同じ働きのマクロでもよい版。使い分けは気にしなくてよい"],
  details="""### std::fgetc {#fgetc}

```cpp
int fgetc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 読み込むファイル |

次の 1 文字を、`unsigned char` として読み、それを `int` に変換して返します。終わりに達したか、エラーが起きたときは `EOF` を返します。`EOF` は、`char` では表せない負の値（ふつう -1）です。

ここで落とし穴になるのが、戻り値を `char` で受けることです。`char c = fgetc(f);` とすると、`EOF` の -1 と、バイト値 `0xFF` が、符号つきの `char` では同じ値になり、区別できなくなります。ファイルの途中の `0xFF` で、読み込みが止まったり、終わりが検出できずに無限ループになったりします。必ず `int c` で受けます。

位置は 1 文字ごとに進むので、先読みしたいときは、[`ungetc`](ungetc.md) で戻せます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("word.txt", "w");
  std::fputs("Hi!", out);
  std::fclose(out);

  std::FILE* f = std::fopen("word.txt", "r");
  int c;                                   // char ではなく int で受ける
  int count = 0;
  while ((c = std::fgetc(f)) != EOF) {
    std::println("{}: {}", count++, static_cast<char>(c));
  }
  std::println("EOF が返った: {}", c == EOF);
  std::fclose(f);
}""",
  out="""0: H
1: i
2: !
EOF が返った: true""",
  uses="""自作のパーサー（設定ファイルや、簡単なスクリプトの読み込み）で、1 文字ずつ先頭を見ながら、トークンに切り分けるときに使います。先読みが必要なら、`ungetc` と組み合わせます。

大量のデータを読むには遅いので、速さが要るときは、`fread` でまとめてメモリへ読み、メモリ上で 1 文字ずつ処理します。""",
  mistakes=[("戻り値を `char` で受けて、`0xFF` で止まる、または止まらない", "`int` で受けて、`EOF` と比べます。"),
            ("`EOF` の確認だけして、エラーを見落とす", "`EOF` はエラーでも返ります。ループの後で `ferror` も調べます。")],
  similar=[("[`getc`](getc.md)", "同じ働き"),
           ("[`getchar`](getchar.md)", "標準入力から 1 文字"),
           ("[`ungetc`](ungetc.md)", "読んだ 1 文字を戻す")],
  memo=["1 文字読む", "戻り値は `int`（`EOF` と区別するため）", "先読みは `ungetc`"])

rewrite(C + 'getc.md',
  intro="""`fgetc` と同じように、ファイルから 1 文字を読みます。違いは、C の規格が「`getc` はマクロとして実装してもよい」と許している点です。昔は、関数呼び出しの手間を省くために、マクロ版が速いことがありました。""",
  tips=["`getc(f)` は `fgetc(f)` と同じ結果を返す。戻り値は `int`",
        "マクロとして実装されうるので、引数を 2 回評価されても困らないようにする",
        "現在のコンパイラでは、`fgetc` との速さの差はほとんどない",
        "迷ったら `fgetc` を使う"],
  details="""### std::getc {#getc}

```cpp
int getc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 読み込むファイル |

動作は [`fgetc`](fgetc.md) と同じです。次の 1 文字を `unsigned char` として読み、`int` で返し、終わりかエラーなら `EOF` を返します。

規格上、`getc` はマクロでもよいことになっています。マクロの場合、引数の式が複数回評価されることがあります。`getc(*files++)` のように、副作用のある式を渡すと、位置が二重に進むかもしれません。副作用のない式（変数名）を渡します。

C++ の標準ライブラリ（`<cstdio>`）では、`std::getc` は関数として使えます。現代のコンパイラは、`fgetc` と同じ速さで動くので、違いを気にする必要はありません。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("ab.txt", "w");
  std::fputs("AB", out);
  std::fclose(out);

  std::FILE* f = std::fopen("ab.txt", "r");
  int a = std::getc(f);
  int b = std::getc(f);
  int c = std::getc(f);   // もう無い
  std::println("{} {}", static_cast<char>(a), static_cast<char>(b));
  std::println("3 回目は EOF: {}", c == EOF);
  std::fclose(f);
}""",
  out="""A B
3 回目は EOF: true""",
  uses="""`fgetc` と同じ場面で使えます。既存の C のコードを読むと `getc` がよく出てきますが、新しく書くなら、`fgetc` で足ります。""",
  mistakes=[("副作用のある式を引数に渡す", "マクロ展開で複数回評価されると、意図しない位置の文字を読みます。変数に入れてから渡します。"),
            ("戻り値を `char` で受ける", "`fgetc` と同じ落とし穴です。`int` で受けます。")],
  similar=[("[`fgetc`](fgetc.md)", "関数として必ず存在する版"),
           ("[`getchar`](getchar.md)", "標準入力専用")],
  memo=["`fgetc` と同じ", "マクロかもしれない", "迷ったら `fgetc`"])

rewrite(C + 'getchar.md',
  intro="""コンソール ゲームや、ツールの対話で、キー入力を 1 文字ずつ受け取りたい。`getchar` は、<strong>標準入力から 1 文字読む</strong>関数です。`fgetc(stdin)` と同じ意味です。""",
  tips=["`getchar()` は `fgetc(stdin)` と同じ。戻り値は `int`",
        "端末では、Enter を押すまで入力が確定しない（行バッファリング）",
        "リダイレクトした入力（`< file.txt`）や、パイプからも読める",
        "ファイルの終わり（Ctrl+Z / Ctrl+D）で `EOF`"],
  details="""### std::getchar {#getchar}

```cpp
int getchar();
```

標準入力から次の 1 文字を読んで、`int` で返します。終わりかエラーで `EOF` を返します。引数はありません。

端末から読むとき、多くの環境では<strong>行単位</strong>で入力が渡されます。1 文字打っただけでは `getchar` は戻らず、Enter を押して初めて、その行の文字が順に読めます。「キーを押した瞬間に反応する」ゲームの入力には、`getchar` は向きません。Windows なら `_getch`（`<conio.h>`）などの、コンソール専用の関数を使います。

入力を Enter まで読み捨てたいときの定番は、`while ((c = getchar()) != '\\n' && c != EOF) {}` です。`fflush(stdin)` は標準では未定義動作なので、使いません。""",
  code="""#include <cstdio>
#include <print>

int main() {
  // 標準入力から 1 文字読む。入力がなければ EOF
  int c = std::getchar();
  if (c == EOF) {
    std::println("入力なし");
  } else {
    std::println("読んだ文字: {}", static_cast<char>(c));
  }
}""",
  out="入力なし",
  uses="""入力を待つだけの「Press Enter to continue」のような処理に使います。`getchar()` を 1 回呼べば、Enter が押されるまで待ちます。

ツールの対話や、パイプで流し込まれたテキストを 1 文字ずつ処理するフィルターなどでも使います。ゲーム本体のキー入力には、別の仕組み（ウィンドウ メッセージ、Raw Input、ゲームパッド API）を使います。""",
  mistakes=[("リアルタイムのキー入力に使おうとして、Enter まで反応しない", "行バッファリングのためです。ゲームの入力は、ウィンドウ メッセージや Raw Input で受けます。"),
            ("戻り値を `char` で受ける", "`EOF` と区別できなくなります。`int` で受けます。")],
  similar=[("[`fgetc`](fgetc.md)", "任意のファイルから 1 文字"),
           ("[`scanf`](scanf.md)", "書式つきで読む")],
  memo=["標準入力から 1 文字", "`fgetc(stdin)` と同じ", "端末では Enter まで確定しない"])

rewrite(C + 'fputc.md',
  intro="""ファイルに 1 文字ずつ書き出したい。たとえば、自作のシリアライザーで、記号を 1 つずつ出力する。<strong>1 文字を書き出す</strong>のが `std::fputc` です。""",
  tips=["`fputc(文字, ファイル)` の形。戻り値は、書いた文字。失敗は `EOF`",
        "文字は `int` で受け取り、`unsigned char` に変換して書く",
        "1 文字ごとに呼ぶと、まとめて書くより遅い",
        "`putc` は同じ働きのマクロでもよい版"],
  details="""### std::fputc {#fputc}

```cpp
int fputc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | `int` | 書き出す文字。`unsigned char` に変換されて書かれる |
| `stream` | `FILE*` | 書き出す先のファイル |

成功すると、書いた文字を `unsigned char` から `int` に直して返します。失敗すると `EOF` を返し、エラーの印を立てます。

1 文字ごとに関数を呼ぶので、数が多いと遅くなります。文字列は `fputs`、バイト列は `fwrite` でまとめて書きます。ただし、バッファーのおかげで、実際のディスクへの書き込みは、まとめて行われます。

読み込み用に開いたファイルに書こうとすると、失敗します。`\"r\"` で開いたファイルへの `fputc` は `EOF` を返します。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("out.txt", "w");
  for (char ch = 'A'; ch <= 'E'; ++ch) {
    std::fputc(ch, f);          // 1 文字ずつ書く
  }
  std::fputc('\\n', f);
  std::fclose(f);

  std::FILE* in = std::fopen("out.txt", "r");
  char buf[16];
  std::fgets(buf, sizeof(buf), in);
  std::print("{}", buf);
  std::fclose(in);
}""",
  out="ABCDE",
  uses="""ごく単純な文字単位の出力に使います。まとまった量は `fputs` や `fwrite`、書式つきは `fprintf` を使うほうが自然です。

C のコードを読むときには、`putc` や `fputc` が出てきますが、新しく書く C++ では、`std::ofstream` の `put` や `<<` を使います。""",
  mistakes=[("1 文字ずつ大量に書いて、遅くなる", "`fwrite` でまとめて書きます。"),
            ("読み込み用に開いたファイルに書いて、失敗に気づかない", "戻り値が `EOF` です。開くときのモードを確かめます。")],
  similar=[("[`putc`](putc.md)", "同じ働き"),
           ("[`putchar`](putchar.md)", "標準出力に 1 文字"),
           ("[`fputs`](fputs.md)", "文字列を書き出す")],
  memo=["1 文字を書き出す", "失敗は `EOF`", "まとまった量は `fputs` や `fwrite`"])

rewrite(C + 'putc.md',
  intro="""`fputc` と同じように、ファイルに 1 文字を書き出します。`getc` と `fgetc` の関係と同じで、規格が「`putc` はマクロでもよい」と許している点が違います。""",
  tips=["`putc(文字, ファイル)` は `fputc` と同じ結果を返す",
        "マクロの場合、引数の式が複数回評価されることがある",
        "現代のコンパイラでは `fputc` との速さの差はほとんどない",
        "迷ったら `fputc` を使う"],
  details="""### std::putc {#putc}

```cpp
int putc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | `int` | 書き出す文字 |
| `stream` | `FILE*` | 書き出す先のファイル |

動作は [`fputc`](fputc.md) と同じです。成功すれば書いた文字を、失敗すれば `EOF` を返します。

マクロ実装の場合、`putc(c++, f)` のように副作用のある式を渡すと、位置が複数回進むなどの不具合が起きえます。`ch` は変数にして渡します。

最近の標準ライブラリは、関数として実装していることが多く、実際に問題が起きる場面は少ないのですが、規格上は許されています。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("x.txt", "w");
  int r = std::putc('X', f);
  std::println("書いた文字: {}", static_cast<char>(r));
  std::fclose(f);
}""",
  out="書いた文字: X",
  uses="""`fputc` と同じ場面で使えます。既存のコードに出てきたら、`fputc` と同じものとして読みます。""",
  mistakes=[("副作用のある式を渡す", "変数に入れてから渡します。")],
  similar=[("[`fputc`](fputc.md)", "関数として必ず存在する版"),
           ("[`putchar`](putchar.md)", "標準出力専用")],
  memo=["`fputc` と同じ", "マクロかもしれない", "迷ったら `fputc`"])

rewrite(C + 'putchar.md',
  intro="""画面（標準出力）に 1 文字だけ出したい。`putchar` は、`fputc(ch, stdout)` と同じです。""",
  tips=["`putchar(c)` は `fputc(c, stdout)` と同じ。戻り値は書いた文字、失敗は `EOF`",
        "出力は行単位でバッファーされることがある。すぐ出したいなら `fflush(stdout)`",
        "改行は自動では付かない",
        "C++23 では `std::print` が使えるので、新しいコードではそちらが楽"],
  details="""### std::putchar {#putchar}

```cpp
int putchar(int ch);
```

標準出力に 1 文字を書き出します。引数は `int` ですが、`unsigned char` に変換されて出力されます。

標準出力は、端末につながっているときは<strong>行単位でバッファーされる</strong>のがふつうで、改行が出るまで画面に出ないことがあります。進捗を `\\r` で上書きするような表示では、`fflush(stdout)` を呼んで、すぐ出します。

マルチバイト文字（日本語）を 1 文字ずつ `putchar` で出すと、バイトが分断されて、端末が正しく解釈できないことがあります。日本語は、文字列として、まとめて出します。""",
  code="""#include <cstdio>

int main() {
  const char* msg = "OK";
  for (const char* p = msg; *p; ++p) std::putchar(*p);
  std::putchar('\\n');
}""",
  out="OK",
  uses="""ごく単純なコンソール出力で使います。進捗バーのような、1 文字ずつ伸びていく表示（`#` を出す）では、`putchar` と `fflush(stdout)` の組み合わせが手軽です。通常のログは `std::println` を使います。""",
  mistakes=[("画面にすぐ出ないと思って悩む", "行バッファリングのためです。`fflush(stdout)` を呼びます。"),
            ("日本語を 1 バイトずつ出して、文字化けする", "文字列としてまとめて出します。")],
  similar=[("[`fputc`](fputc.md)", "任意のファイルに 1 文字"),
           ("[`puts`](puts.md)", "文字列と改行を出す")],
  memo=["標準出力に 1 文字", "改行は付かない", "すぐ出すなら `fflush(stdout)`"])

rewrite(C + 'puts.md',
  intro="""デバッグ用に、メッセージを 1 行だけ画面に出したい。`puts` は、<strong>文字列に改行を足して、標準出力に出す</strong>関数です。`printf` のように書式を解釈しないので、`%` が混ざっていても安全です。""",
  tips=["`puts(文字列)` は、文字列を出したあと、改行も出す",
        "`fputs(文字列, stdout)` との違いは、改行が自動で付くこと",
        "書式を解釈しない。`%` はそのまま出る",
        "戻り値は、成功なら非負の値、失敗なら `EOF`"],
  details="""### std::puts {#puts}

```cpp
int puts(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 出力する文字列。`\\0` で終わっている必要がある |

`str` を標準出力に書き、続けて改行 `\\n` を 1 つ書きます。名前が似た [`fputs`](fputs.md) は、改行を足さないので、混同しないようにします。

`printf(str)` と違い、書式の解釈がありません。ユーザーの入力を含む文字列を `printf(input)` で出すと、`%s` や `%n` が解釈されて危険ですが、`puts(input)` は安全です。

C++23 の `std::println("{}", str)` が使える環境では、型安全で書式つきの `std::println` を使うほうが、一貫して書けます。""",
  code="""#include <cstdio>

int main() {
  std::puts("HP: 100%");    // % が含まれても、そのまま出る。改行も付く
  std::puts("MP: 50");
}""",
  out="""HP: 100%
MP: 50""",
  uses="""簡単なデバッグ出力に使います。ユーザー名やファイル名のような、`%` を含みうる文字列を、そのまま画面に出す場面で安心です。

ログの出力は、`std::println` やロギング ライブラリに任せ、`puts` は、C のコードや、短いスクリプトのようなプログラムで見かける、と考えておきます。""",
  mistakes=[("改行を自分で付けて、空行が増える", "`puts` は改行を足します。文字列に `\\n` を入れると、2 つ出ます。"),
            ("`fputs` と同じだと思って、改行が出ないと悩む", "`fputs` は改行を足さず、`puts` は足します。")],
  similar=[("[`fputs`](fputs.md)", "改行を足さない。出力先を選べる"),
           ("[`putchar`](putchar.md)", "1 文字だけ"),
           ("`std::println`", "C++23 の書式つき出力")],
  memo=["文字列と改行を標準出力に出す", "書式を解釈しない", "`fputs` は改行を足さない"])

rewrite(C + 'ungetc.md',
  intro="""トークナイザーで、数字が続く限り読みたい。でも、数字でない文字を 1 つ読んでしまってから、「これは次のトークンの先頭だった」と気づく。読んでしまった 1 文字を、読まなかったことにしたいときに使うのが `std::ungetc` です。

<strong>読んだ 1 文字を、入力に押し戻します</strong>。次の読み込みで、同じ文字がもう一度読めます。""",
  tips=["押し戻せることが保証されるのは 1 文字だけ。連続して押し戻す数は、環境による",
        "戻り値は、押し戻した文字。失敗は `EOF`",
        "ファイルの中身は書き換わらない。読み込み用のバッファーに戻すだけ",
        "`EOF` は押し戻せない"],
  details="""### std::ungetc {#ungetc}

```cpp
int ungetc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | `int` | 押し戻す文字 |
| `stream` | `FILE*` | 押し戻す先のファイル |

押し戻した文字は、次の `fgetc` などで最初に読まれます。ファイルそのものは変わらず、内部のバッファーに 1 文字置かれるだけです。

規格が保証するのは、<strong>1 文字</strong>だけです。読み込みを挟まず 2 回続けて押し戻すと、失敗する環境があります。先読みが 1 文字で足りる字句解析に向いた道具です。

直前に読んだ文字と、同じ文字を押し戻す必要はありません。ただし、`fseek` や `rewind` を呼ぶと、押し戻した文字は捨てられます。`EOF` を押し戻そうとすると、何も起きず、`EOF` が返ります。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("tok.txt", "w");
  std::fputs("123+45", out);
  std::fclose(out);

  std::FILE* f = std::fopen("tok.txt", "r");
  int value = 0;
  int c;
  while ((c = std::fgetc(f)) != EOF) {
    if (c < '0' || c > '9') {
      std::ungetc(c, f);               // 数字でない文字は、次のトークンのために戻す
      break;
    }
    value = value * 10 + (c - '0');
  }
  std::println("数: {}", value);
  std::println("次の文字: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}""",
  out="""数: 123
次の文字: +""",
  uses="""自作のパーサーや電卓のような、字句解析で使います。数字や識別子は「どこまで続くか」が、1 文字先を見ないと分からないので、読みすぎた 1 文字を戻して、次のトークンの先頭として使います。

C++ のストリームでは、`std::istream::peek()` が、読まずに先を見る手段として使えます。`ungetc` は、`FILE*` を扱うコードで使います。""",
  mistakes=[("2 文字以上続けて押し戻して、失敗する", "保証されるのは 1 文字です。複数文字の先読みが要るなら、自分でバッファーを持ちます。"),
            ("押し戻したあとに `fseek` して、文字が消える", "位置を動かすと、押し戻した文字は捨てられます。")],
  similar=[("[`fgetc`](fgetc.md)", "1 文字読む"),
           ("`std::istream::peek`", "C++ のストリームで、読まずに次の文字を見る")],
  memo=["読んだ 1 文字を押し戻す", "保証されるのは 1 文字", "ファイルは変わらない"])

rewrite(C + 'clearerr.md',
  intro="""読み込みでファイルの終わりに達したあと、そのファイルに別のプログラムが追記した。続きを読もうとしても、`feof` の印が残っているので、読み込みが止まったままになる。

`std::clearerr` は、<strong>終わりの印とエラーの印を、消す</strong>関数です。ログを追いかけて読み続ける `tail -f` のような処理で使います。""",
  tips=["`feof` と `ferror` が示す印を、両方消す",
        "ファイルの位置は変わらない。続きから読む",
        "エラーの原因が解消していないと、また同じエラーになる",
        "戻り値はない"],
  details="""### std::clearerr {#clearerr}

```cpp
void clearerr(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 印を消すファイル |

終わりの印とエラーの印は、読み書きのたびに更新されますが、自動では消えません。一度終わりに達したファイルは、あとからデータが増えても、`clearerr` で印を消さない限り、読み込みが失敗し続けることがあります。

似た関数の [`rewind`](rewind.md) は、位置を先頭に戻したうえで、印も消します。`clearerr` は位置を動かさず、印だけを消すので、「今の位置から続きを読む」場合に使います。

エラーの印を消しても、原因が解決するわけではありません。ディスクの故障のようなエラーは、消してもまた起きます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* w = std::fopen("grow.log", "w");
  std::fputs("line1\\n", w);
  std::fflush(w);

  std::FILE* r = std::fopen("grow.log", "r");
  char buf[32];
  while (std::fgets(buf, sizeof(buf), r)) {}
  std::println("1 回目の終わり: {}", std::feof(r) != 0);

  std::fputs("line2\\n", w);              // 別のところで追記された
  std::fflush(w);

  std::clearerr(r);                        // 印を消して、続きを読む
  std::println("clearerr の後: {}", std::feof(r) != 0);
  if (std::fgets(buf, sizeof(buf), r)) std::print("続き: {}", buf);

  std::fclose(r);
  std::fclose(w);
}""",
  out="""1 回目の終わり: true
clearerr の後: false
続き: line2""",
  uses="""ログ ビューアーのように、ファイルが伸びるのを追いかけて読むツールで使います。ゲームのログ ファイルを、別のウィンドウで監視する、デバッグ補助ツールの実装などです。

エラーが起きたあと、リトライする処理でも使います。印を消してから、同じ操作をやり直します。""",
  mistakes=[("印を消さずに読み続けて、いつまでも読めない", "終わりの印が残っていると、続きのデータがあっても、読み込みが止まることがあります。`clearerr` で消します。"),
            ("エラーの原因が残ったまま、`clearerr` だけして無限ループになる", "原因が解消されていなければ、同じエラーが続きます。リトライの回数に上限を付けます。")],
  similar=[("[`rewind`](rewind.md)", "位置を先頭に戻して、印も消す"),
           ("[`feof`](feof.md)", "終わりの印を調べる"),
           ("[`ferror`](ferror.md)", "エラーの印を調べる")],
  memo=["終わりとエラーの印を消す", "位置は動かさない", "ログの追いかけ読みに使う"])

rewrite(C + 'perror.md',
  intro="""ファイルが開けなかったとき、「失敗しました」だけでは、原因が分かりません。ファイルがないのか、権限がないのか、ディスクが一杯なのか。C の関数は、失敗の理由を `errno` という変数に入れていますが、数字のままでは読めません。

`std::perror` は、<strong>`errno` の意味を、人が読める文章で標準エラー出力に出す</strong>関数です。""",
  tips=["`perror(\"接頭辞\")` は、「接頭辞: エラーの説明」の形で、標準エラー出力に出す",
        "直前に失敗した関数の `errno` を使うので、失敗の直後に呼ぶ",
        "説明の文面は、環境（OS、ロケール）によって違う",
        "成功したときに `errno` が 0 になるとは限らない。失敗が確実なときだけ呼ぶ"],
  details="""### std::perror {#perror}

```cpp
void perror(const char* s);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const char*` | エラーの説明の前に付ける文字列。`nullptr` や空文字列なら付けない |

`s` が空でなければ、「`s: `」を出してから、`errno` に対応する説明と改行を出します。出力先は標準エラー出力（`stderr`）です。

`errno` は、関数が失敗したときに値が設定される変数ですが、成功したときに 0 に戻るとは限りません。`perror` を呼ぶのは、`fopen` が `nullptr` を返した、といった失敗が確かめられた直後に限ります。その間に別の関数（`printf` など）を呼ぶと、`errno` が上書きされることがあります。

説明の文面は、環境ごとに違います。プログラムの中で文面を比較して分岐してはいけません。分岐は `errno` の値（`ENOENT` など）で行います。""",
  code="""#include <cerrno>
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("not_found.txt", "r");
  if (!f) {
    // perror は stderr に出す。実行結果には現れないので、errno を確かめる
    std::println("存在しない: {}", errno == ENOENT);
    std::perror("not_found.txt を開けません");   // 標準エラー出力に説明が出る
  }
}""",
  out="存在しない: true",
  uses="""ファイルが開けない、読めない、といった失敗の原因を、簡単に知りたいときに使います。デバッグ中の確認や、小さなツールのエラー表示に便利です。

ゲームの製品では、`std::filesystem` の `error_code`（`ec.message()`）や、自前のログに残すほうが、文面を整えられます。`perror` は標準エラー出力にしか出せないので、ログ ファイルには使えません。""",
  mistakes=[("失敗の確認なしに呼んで、意味のない説明が出る", "成功した直後でも、前の失敗の `errno` が残っていることがあります。失敗を確かめてから呼びます。"),
            ("文面で分岐して、環境が変わると動かない", "分岐は `errno` の値で行います。")],
  similar=[("`std::strerror`", "`errno` の説明を、文字列として受け取る"),
           ("[`fopen`](fopen.md)", "失敗で `errno` を設定する代表的な関数")],
  memo=["`errno` の意味を標準エラーに出す", "失敗の直後に呼ぶ", "文面は環境による"])

rewrite(C + 'remove.md',
  intro="""一時ファイルを使い終わったので、消したい。C には、ファイル名を渡すだけで、そのファイルを消す関数があります。それが `std::remove` です。

<strong>ファイルを 1 つ消す</strong>関数で、`<cstdio>` に入っています。名前が `<algorithm>` の `std::remove` と同じなので、混同に注意が要ります。""",
  tips=["`remove(\"パス\")` で、ファイルを消す。戻り値は、成功なら 0、失敗なら 0 以外",
        "`<algorithm>` の `std::remove` とは、別の関数。引数の型で区別される",
        "フォルダーは、環境によって消せたり消せなかったりする。フォルダーは `std::filesystem::remove`",
        "開いているファイルを消そうとすると、Windows では失敗する"],
  details="""### std::remove {#remove}

```cpp
int remove(const char* filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` | 消すファイルのパス |

成功すれば 0 を返し、失敗すれば 0 以外を返して、`errno` に理由を入れます。典型的な失敗は、ファイルが存在しない（`ENOENT`）、権限がない、他で開かれている、などです。

注意したいのは、同じ名前の関数が 2 つあることです。`<cstdio>` の `std::remove(const char*)` はファイルを消し、`<algorithm>` の `std::remove(first, last, value)` は、コンテナーの要素を後ろへ詰める関数です。引数の数と型が違うので、オーバーロードとして区別されますが、`std::remove(vec.begin(), vec.end(), 3)` を書くつもりで、`cstdio` 側を呼んでしまう、といった混乱は起きえます。

C++17 以降のコードでは、[`std::filesystem::remove`](../filesystem/remove.md) のほうが、`path` を使えて、例外やエラー コードで失敗を調べられます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("temp.dat", "w");
  std::fclose(f);                         // 閉じてから消す

  std::println("消せた: {}", std::remove("temp.dat") == 0);
  std::println("もう一度: {}", std::remove("temp.dat") == 0);   // もう無いので失敗
}""",
  out="""消せた: true
もう一度: false""",
  uses="""一時ファイルの後片付けに使います。ただし、C++17 が使えるなら、`std::filesystem::remove` のほうが、存在しなくてもエラーにならない（`false` が返る）ので、後片付けに向いています。

C の古いコードや、`FILE*` を中心に書かれたコードを読むと、この `std::remove` が出てきます。""",
  mistakes=[("開いたまま消そうとして、Windows で失敗する", "`fclose` で閉じてから消します。"),
            ("`<algorithm>` の `std::remove` と取り違える", "コンテナーの要素を消すつもりで呼ぶと、意図と違う関数が選ばれます。引数を確かめます。")],
  similar=[("[`std::filesystem::remove`](../filesystem/remove.md)", "C++17 版。`path` を使い、失敗の扱いも柔軟"),
           ("[`rename`](rename.md)", "名前を変える")],
  memo=["ファイルを消す", "成功は 0", "C++17 以降は `std::filesystem::remove`"])

rewrite(C + 'rename.md',
  intro="""セーブ データを書き込んでいる最中に、クラッシュすると、壊れたファイルが残ってしまいます。そこで、いったん別の名前の一時ファイルに書いて、最後に本物の名前へ付け替える、という方法があります。この付け替えに使うのが `std::rename` です。

<strong>ファイルの名前を変える</strong>（または場所を移す）関数です。""",
  tips=["`rename(\"旧\", \"新\")` で、名前を変える。成功は 0、失敗は 0 以外",
        "新しい名前のファイルがすでにあるときの動きは、環境による（Windows は失敗、POSIX は置き換え）",
        "同じボリューム内なら、ふつう一瞬で終わる。別ボリュームへは失敗することがある",
        "安全に書き換えたいときは、一時ファイルに書いてから `rename` する"],
  details="""### std::rename {#rename}

```cpp
int rename(const char* old_filename, const char* new_filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `old_filename` | `const char*` | 今の名前（パス） |
| `new_filename` | `const char*` | 新しい名前（パス） |

成功すれば 0 を返します。失敗すると 0 以外を返し、`errno` に理由が入ります。ファイルが存在しない、権限がない、といった理由のほかに、<strong>新しい名前のファイルがすでにある</strong>場合の扱いが、環境で違うことに注意します。

規格は、この場合の動作を実装定義としています。Windows の MSVC では失敗しますが、Linux などでは、既存のファイルを置き換えます。どちらの環境でも同じ動きにしたいなら、`std::filesystem::rename`（ここも似た違いがある）や、先に新しい名前を `remove` しておく、という手順を取ります。

セーブ データの安全な書き換えは、「一時ファイルに全部書く」「閉じる」「元のファイルを消す」「一時ファイルを `rename` する」の順です。途中でクラッシュしても、元のファイルか、新しい完全なファイルのどちらかが残ります。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("tmp_save.dat", "w");
  std::fputs("SAVE", f);
  std::fclose(f);

  std::remove("save.dat");                          // 前のファイルがあれば消す
  int r = std::rename("tmp_save.dat", "save.dat");  // 完成したので付け替える
  std::println("付け替えた: {}", r == 0);

  std::FILE* in = std::fopen("save.dat", "r");
  char buf[16];
  std::fgets(buf, sizeof(buf), in);
  std::println("中身: {}", buf);
  std::fclose(in);
}""",
  out="""付け替えた: true
中身: SAVE""",
  uses="""セーブ データの安全な保存に使います。壊れたセーブ ファイルは、プレイヤーにとって最悪の不具合の 1 つなので、一時ファイルに書いて付け替える手順は、必ず取り入れたい方法です。

古いセーブを残したいなら、本物の名前を `.bak` に `rename` で退避させてから、新しいファイルを付け替えます。""",
  mistakes=[("新しい名前がすでにあって、環境ごとに結果が違う", "Windows は失敗し、Linux は置き換えます。先に `remove` しておくなど、そろえる手順を入れます。"),
            ("開いたままのファイルを `rename` して、失敗する", "閉じてから付け替えます。"),
            ("別のドライブへ移そうとして失敗する", "同じボリュームの中でしか動かないことがあります。別ドライブへは、コピーしてから消します。")],
  similar=[("[`remove`](remove.md)", "ファイルを消す"),
           ("[`std::filesystem::rename`](../filesystem/rename.md)", "C++17 版")],
  memo=["名前を変える（移す）", "新しい名前が既存だと環境で違う", "安全な保存の最後の手順に使う"])

rewrite(C + 'tmpfile.md',
  intro="""ちょっとした作業用に、一時ファイルが欲しい。名前を考えるのも、後で消すのも、面倒です。`std::tmpfile` は、<strong>一時ファイルを作って、開いた状態の `FILE*` を返し、閉じたら自動で消えます</strong>。""",
  tips=["戻り値は、読み書き兼用（`\"wb+\"`）で開かれた `FILE*`。失敗は `nullptr`",
        "名前は分からない。閉じるか、プログラムが終わると、自動で消える",
        "名前を付けて保存したいときには向かない",
        "Windows では、ルート直下に作ろうとして権限エラーになる環境がある"],
  details="""### std::tmpfile {#tmpfile}

```cpp
std::FILE* tmpfile();
```

引数はありません。システムが決めた、重複しない名前で、一時ファイルを作り、バイナリの読み書き兼用で開いて返します。作れなかったときは `nullptr` です。

戻り値の `FILE*` を `fclose` すると、ファイルは自動で削除されます。プログラムが正常に終了したときも、削除されます。異常終了すると、削除されずに残る環境があります。

ファイルの名前を取得する方法は、標準にはありません。別のプログラムに渡したい、あとで名前で開き直したい、という用途には向きません。その場合は、名前を自分で決めて、`std::filesystem::temp_directory_path` に作ります。

Windows の古い MSVC では、`tmpfile` が、ドライブのルート（`C:\\`）に作ろうとして、管理者権限がないと失敗することがありました。新しい処理系は改善されていますが、`nullptr` の確認は欠かせません。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* tmp = std::tmpfile();
  if (!tmp) {
    std::println("作れなかった");
    return 1;
  }
  std::fputs("work data", tmp);

  std::rewind(tmp);                        // 書いたあと、先頭に戻って読む
  char buf[32];
  std::fgets(buf, sizeof(buf), tmp);
  std::println("読み戻した: {}", buf);

  std::fclose(tmp);                        // 閉じると自動で消える
}""",
  out="読み戻した: work data",
  uses="""計算の途中結果を、メモリに入りきらないときの逃がし場所として使います。たとえば、大きなデータを並べ替えるときの、外部ソートの作業ファイルです。

名前を付けて残したいデータには使いません。ダウンロード中のファイルの一時保存のように、あとで別のプログラムに渡す用途には、`temp_directory_path` に名前を決めて作ります。""",
  mistakes=[("`nullptr` を確かめずに使う", "権限やディスクの空きで失敗します。必ず確かめます。"),
            ("名前を知りたくなって、困る", "標準では取得できません。名前が要るなら、`std::filesystem::temp_directory_path()` に自分で名前を決めて作ります。")],
  similar=[("[`tmpnam`](tmpnam.md)", "一時ファイルの名前だけを作る。競合に弱く、非推奨に近い"),
           ("[`temp_directory_path`](../filesystem/temp_directory_path.md)", "OS の一時フォルダーの場所")],
  memo=["自動で消える一時ファイルを開く", "名前は分からない", "`nullptr` を確かめる"])
print('cs3 ok')
