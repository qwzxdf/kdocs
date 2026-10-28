"""cstdio の書き直し（バッチ 4: 書式つきの入出力、バッファー、位置の保存、定数）。"""
from rw import rewrite

C = 'stl/io/cstdio/'

rewrite(C + 'fprintf.md',
  intro="""ログ ファイルに「HP: 100 / 120」のような、数値を含む行を書き出したい。文字列を `+` でつなぐのは面倒なので、書式の中に値をはめ込んで、ファイルへ出す関数が `std::fprintf` です。`printf` の出力先を選べる版です。""",
  tips=["`fprintf(ファイル, 書式, 値...)`。書式の `%d`、`%f`、`%s` などに、値がはまる",
        "戻り値は、書いた文字数。失敗は負の値",
        "書式と値の型が合っていないと、未定義動作になる。コンパイラの警告を有効にする",
        "ユーザー入力を書式にそのまま渡してはいけない。`\"%s\"` を使う"],
  details="""### std::fprintf {#fprintf}

```cpp
int fprintf(std::FILE* stream, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 出力先。`stdout` や `stderr` も渡せる |
| `format` | `const char*` | 書式文字列。`%` から始まる指定に、値がはまる |
| `...` | 可変個引数 | 書式に対応する値 |

よく使う指定は、`%d`（`int`）、`%u`（`unsigned`）、`%f`（`double`）、`%s`（文字列）、`%c`（文字）、`%x`（16 進数）、`%%`（`%` そのもの）です。`long long` には `%lld`、`size_t` には `%zu` を使います。

<strong>書式と値の型が食い違うと、未定義動作</strong>です。`%d` に `double` を渡すと、でたらめな値が出たり、クラッシュしたりします。`float` は可変個引数に渡す時点で `double` になるので `%f` で受けられます。GCC や Clang は `-Wformat`、MSVC は `/W4` で、食い違いを警告します。

書式文字列が、プログラムに埋め込んだ定数ではなく、ユーザー入力やファイルの内容から来ていると、`%s` や `%n` を仕込まれる危険があります（書式文字列攻撃）。外から来た文字列は、`fprintf(f, \"%s\", text)` のように、値として渡します。

C++23 の `std::print(FILE*, ...)` なら、型が合っていないとコンパイル エラーになるので、新しいコードではそちらが安全です。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("status.log", "w");
  int n = std::fprintf(f, "HP: %d / %d (%.1f%%)\\n", 85, 120, 85 * 100.0 / 120);
  std::fclose(f);
  std::println("書いた文字数: {}", n);

  std::FILE* in = std::fopen("status.log", "r");
  char buf[64];
  std::fgets(buf, sizeof(buf), in);
  std::print("{}", buf);
  std::fclose(in);
}""",
  out="""書いた文字数: 21
HP: 85 / 120 (70.8%)""",
  uses="""ログ ファイルへの出力や、`stderr` へのエラー表示に使います。`fprintf(stderr, ...)` は、標準エラー出力にメッセージを出す、C の定番の書き方です。

新しい C++ のコードでは、`std::print` / `std::println`（C++23）や `std::format` が、型安全で書きやすいので、`fprintf` は、C のコードを読むときと、C のライブラリに合わせるときに使います。""",
  mistakes=[("書式と値の型が食い違って、でたらめな値が出る", "`%d` に `double`、`%s` に `int` などを渡さないようにします。警告を有効にします。"),
            ("ユーザー入力を書式に渡して、脆弱性になる", "`fprintf(f, input)` ではなく、`fprintf(f, \"%s\", input)` にします。"),
            ("`size_t` を `%d` で出して、大きな値で壊れる", "`%zu` を使います。")],
  similar=[("[`printf`](printf.md)", "標準出力に書く"),
           ("[`sprintf`](sprintf.md)", "文字配列に書く"),
           ("`std::print`", "C++23 の型安全な出力")],
  memo=["書式つきでファイルに書く", "書式と値の型を合わせる", "外から来た文字列は `\"%s\"` で渡す"])

rewrite(C + 'sprintf.md',
  intro="""書式を使って作った文字列を、ファイルではなく、メモリ上の配列に入れたい。たとえば、「Player_01.png」のようなファイル名を作る。それをやるのが `std::sprintf` ですが、<strong>書き込む先の大きさを確かめない</strong>ため、バッファーを溢れさせる危険があります。""",
  tips=["`sprintf(バッファー, 書式, 値...)`。戻り値は、書いた文字数（終端の `\\0` を除く）",
        "バッファーの大きさを指定できない。溢れると、メモリを破壊する",
        "代わりに `snprintf`（大きさを指定する版）を使う",
        "C++ では `std::format`（C++20）や `std::to_string` のほうが安全で楽"],
  details="""### std::sprintf {#sprintf}

```cpp
int sprintf(char* buffer, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 結果を入れる配列 |
| `format` | `const char*` | 書式文字列 |
| `...` | 可変個引数 | 書式に対応する値 |

結果の文字数に、終端の `\\0` を足した分の領域が `buffer` に必要です。`%d` で出る数字の桁数や、`%s` に渡す文字列の長さは、実行時に決まるので、固定の大きさの配列では、足りなくなることがあります。溢れると、周りのメモリを書き潰して、クラッシュや脆弱性の原因になります。

そのため、`sprintf` は避け、<strong>`snprintf(buffer, size, format, ...)` を使う</strong>のが原則です。`snprintf` は、書き込みを `size - 1` 文字までで止めて、必ず `\\0` を付けます。

MSVC は、`sprintf` を使うと、警告（C4996）を出します。警告を黙らせるのではなく、`snprintf` に置き換えるのが正しい対処です。""",
  code="""#include <cstdio>
#include <print>

int main() {
  char name[32];
  int n = std::sprintf(name, "Player_%02d.png", 7);   // 余裕のある大きさの配列に
  std::println("{} ({} 文字)", name, n);

  // 安全な版: 大きさを渡す
  char small[8];
  int m = std::snprintf(small, sizeof(small), "Player_%02d.png", 7);
  std::println("切り詰め: {}", small);
  std::println("本来の長さ: {}", m);
}""",
  out="""Player_07.png (13 文字)
切り詰め: Player_
本来の長さ: 13""",
  uses="""既存の C のコードで見かけます。新しく書くなら、`snprintf` か、C++20 の `std::format`、`std::format_to_n` を使います。ファイル名の組み立てのような、文字列が短い場面でも、後で書式や元の文字列が変わって溢れることがあるので、大きさを指定できる版にしておきます。""",
  mistakes=[("バッファーが足りず、メモリを壊す", "桁数や文字列の長さが読めないものは、`snprintf` にします。"),
            ("`snprintf` の戻り値が、書いた文字数だと思う", "戻り値は、切り詰めがなければ書けたはずの長さです。`size` 以上なら切れています。")],
  similar=[("[`vsnprintf`](vsnprintf.md)", "可変個引数を `va_list` で受ける版"),
           ("[`fprintf`](fprintf.md)", "ファイルに書く"),
           ("`std::format`", "C++20 の型安全な文字列組み立て")],
  memo=["書式つきで文字配列に書く", "大きさを指定できず危険", "`snprintf` を使う"])

rewrite(C + 'sscanf.md',
  intro="""設定ファイルから読んだ 1 行 `"pos=10,20"` を、2 つの数値に分けたい。文字列を自分で切り分けるのは面倒です。`std::sscanf` は、<strong>文字列の中から、書式に沿って値を取り出す</strong>関数です。""",
  tips=["`sscanf(文字列, 書式, &変数...)`。戻り値は、取り出せた項目の数",
        "値を入れる変数には、アドレス（`&x`）を渡す。忘れると、未定義動作",
        "`%s` は幅の指定がないと、バッファーを溢れさせる。`%31s` のように幅を付ける",
        "戻り値が期待した数より少なければ、書式に合わなかったということ"],
  details="""### std::sscanf {#sscanf}

```cpp
int sscanf(const char* buffer, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `const char*` | 読み取る元の文字列 |
| `format` | `const char*` | 書式文字列 |
| `...` | ポインター | 取り出した値を入れる変数のアドレス |

書式の中の `%d`、`%f`、`%s` などに対応する値を、文字列から順に取り出して、渡された変数に入れます。書式の中の空白は、文字列の側の空白（なくてもよい）に一致します。それ以外の文字（`=` や `,`）は、そのとおりに一致する必要があります。

戻り値は、<strong>取り出せた項目の数</strong>です。2 つ取り出すつもりで、1 が返れば、2 つ目の前で書式が合わなくなりました。値を使う前に、戻り値を確かめます。全く取り出せなかったときは 0 で、入力が最初から空など、取り出す前に終わったときは `EOF` です。

`%d` は、`int` へのポインターが要ります。`%f` は `float`、`%lf` は `double` です。`double` に `%f` を使うと、値が壊れます。

`%s` は、空白までを読み、<strong>幅の指定がないと、入力の長さの分だけ書き込みます</strong>。`char name[32]` なら `%31s` のように、大きさ - 1 を指定します。""",
  code="""#include <cstdio>
#include <print>

int main() {
  const char* line = "pos=10,20";
  int x = 0, y = 0;
  int n = std::sscanf(line, "pos=%d,%d", &x, &y);
  std::println("取り出せた数: {}  x={} y={}", n, x, y);

  // 書式に合わない文字列
  int a = 0;
  int m = std::sscanf("abc", "%d", &a);
  std::println("合わない場合: {}", m);

  // 文字列は幅を付ける
  char name[8];
  std::sscanf("hero 100", "%7s", name);
  std::println("名前: {}", name);
}""",
  out="""取り出せた数: 2  x=10 y=20
合わない場合: 0
名前: hero""",
  uses="""短い文字列から値を取り出す場面で使います。設定の行、コマンドライン引数、簡単なコマンド（`move 10 20`）のパースなどです。

C++ では、`std::from_chars`（C++17）が、数値の変換に高速で安全です。複数の値を取り出すなら `std::istringstream` や、自前の分割も選べます。`sscanf` は、書式がそのまま読める手軽さが利点です。""",
  mistakes=[("戻り値を確かめずに、失敗した変数を使う", "取り出せなかった変数は、書き換わりません。初期値のままか、不定です。"),
            ("`%s` に幅を付けず、バッファーを溢れさせる", "`%31s` のように、大きさ - 1 の幅を付けます。"),
            ("`double` に `%f` を使って、値が壊れる", "`double` には `%lf` です。")],
  similar=[("[`scanf`](scanf.md)", "標準入力から取り出す"),
           ("[`fscanf`](fscanf.md)", "ファイルから取り出す"),
           ("`std::from_chars`", "C++17 の高速で安全な数値変換")],
  memo=["文字列から書式で値を取り出す", "戻り値は取り出せた数", "`%s` には幅を付ける"])

rewrite(C + 'scanf.md',
  intro="""コンソールで、プレイヤーの名前や数値を入力してもらいたい。標準入力から、書式に沿って値を読み取るのが `std::scanf` です。ゲームの本編より、ツールや練習用のプログラムで使う場面が多い関数です。""",
  tips=["`scanf(書式, &変数...)`。戻り値は、読み取れた項目の数",
        "値を入れる変数には、アドレス（`&x`）を渡す。忘れると、クラッシュする",
        "`%s` は幅の指定がないと、バッファーを溢れさせる",
        "入力が書式に合わなかったとき、残った文字が入力に残る。次の読み込みに影響する"],
  details="""### std::scanf {#scanf}

```cpp
int scanf(const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `const char*` | 書式文字列 |
| `...` | ポインター | 取り出した値を入れる変数のアドレス |

動作は [`sscanf`](sscanf.md) と同じで、読み取る元が標準入力です。戻り値は、読み取れた項目の数で、入力が終わったら `EOF` です。

`scanf` の扱いにくい点は、<strong>書式に合わなかった文字が、入力に残る</strong>ことです。たとえば、`%d` で数値を読もうとして、`abc` と入力されると、0 が返り、`abc` はそのまま残ります。ループの中で同じ `scanf` を繰り返すと、同じ `abc` を何度も読もうとして、無限ループになります。入力を一行ずつ `fgets` で読み、`sscanf` で解釈するほうが、失敗の扱いが楽です。

`%s` の幅の指定や、`double` に `%lf` を使う決まりは、`sscanf` と同じです。MSVC は `scanf` を安全でないと警告し、`scanf_s` を勧めますが、標準ではないので、移植性を考えるなら、`fgets` と `sscanf` の組み合わせにします。""",
  code="""#include <cstdio>
#include <print>

int main() {
  int hp = -1;
  // 標準入力が空のとき、読み取りは失敗して EOF が返る
  int n = std::scanf("%d", &hp);
  std::println("読み取り結果: {}", n == EOF ? "EOF" : "読めた");
  std::println("hp は変わらない: {}", hp == -1);
}""",
  out="""読み取り結果: EOF
hp は変わらない: true""",
  uses="""コンソールの簡単なツールや、アルゴリズムの練習で使います。ゲームの製品では、入力はウィンドウ メッセージやゲームパッドから受けるので、`scanf` を使う場面はほとんどありません。

コンソールで入力を受けるなら、`fgets` で 1 行読んでから、`sscanf` や `std::from_chars` で解釈する形が、失敗に強い書き方です。""",
  mistakes=[("書式に合わない入力で、無限ループになる", "合わなかった文字が残ります。`fgets` で行ごとに読んで、解釈に失敗したら、その行を捨てます。"),
            ("変数のアドレスを渡し忘れて、クラッシュする", "`scanf(\"%d\", x)` ではなく、`&x` です。"),
            ("`%s` に幅を付けず、溢れる", "`%31s` のように幅を付けます。")],
  similar=[("[`sscanf`](sscanf.md)", "文字列から取り出す"),
           ("[`fscanf`](fscanf.md)", "ファイルから取り出す"),
           ("[`fgets`](fgets.md)", "1 行を読む。解釈は別にする")],
  memo=["標準入力から書式で読む", "戻り値は読み取れた数", "行ごとに `fgets` で読む方が安全"])

rewrite(C + 'fscanf.md',
  intro="""テキスト形式のデータ ファイルから、数値や単語を、書式に沿って順に読み取りたい。ファイルに対する `sscanf` が、`std::fscanf` です。""",
  tips=["`fscanf(ファイル, 書式, &変数...)`。戻り値は、読み取れた項目の数",
        "終わりに達して 1 つも読めなかったときは `EOF`",
        "`%s` には幅を付ける。`%d` などには `&` を付けたアドレスを渡す",
        "書式に合わない文字が残ると、次の呼び出しも失敗し続ける"],
  details="""### std::fscanf {#fscanf}

```cpp
int fscanf(std::FILE* stream, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 読み取るファイル |
| `format` | `const char*` | 書式文字列 |
| `...` | ポインター | 取り出した値を入れる変数のアドレス |

読み取る元がファイルであること以外は、[`sscanf`](sscanf.md) と同じです。空白は読み飛ばされるので、スペース区切りや改行区切りの数値の列を、続けて読むのに向いています。

戻り値は、読み取れた項目の数です。ループで `while (fscanf(f, \"%d\", &v) == 1)` と書くと、数値が読める限り続けて、書式に合わない文字か、ファイルの終わりで止まります。止まったあとで、`feof` と `ferror` を調べると、終わりなのか、不正な文字なのかが分かります。

行ごとに形式が決まっているデータは、`fgets` で 1 行読んでから `sscanf` で解釈するほうが、壊れた行に引きずられません。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("nums.txt", "w");
  std::fputs("10 20 30\\n40 50\\n", out);
  std::fclose(out);

  std::FILE* f = std::fopen("nums.txt", "r");
  int sum = 0, v = 0, count = 0;
  while (std::fscanf(f, "%d", &v) == 1) {   // 数値が読める限り続ける
    sum += v;
    ++count;
  }
  std::println("{} 個の合計: {}", count, sum);
  std::println("終わりまで読んだ: {}", std::feof(f) != 0);
  std::fclose(f);
}""",
  out="""5 個の合計: 150
終わりまで読んだ: true""",
  uses="""数値の列を並べただけの、簡単なデータ ファイル（座標のリスト、スコア表）を読むときに使います。形式が少しでも複雑になるなら、1 行ずつ `fgets` で読み、自分で分割するほうが、壊れたデータに強くなります。

JSON のような構造のあるデータには、専用のライブラリを使います。""",
  mistakes=[("書式に合わない文字で止まって、無限ループになる", "合わない文字は読まれずに残るので、同じ呼び出しが失敗し続けます。戻り値を見てループを抜けます。"),
            ("`%s` に幅を付けず、溢れる", "幅を付けます。")],
  similar=[("[`sscanf`](sscanf.md)", "文字列から取り出す"),
           ("[`fgets`](fgets.md)", "1 行を読む"),
           ("`std::ifstream` の `>>`", "C++ のストリームでの同等の読み取り")],
  memo=["ファイルから書式で読む", "戻り値は読み取れた数", "壊れたデータには行単位が強い"])

rewrite(C + 'setvbuf.md',
  intro="""ログ ファイルを書き込むとき、行ごとにすぐディスクへ出したい場合と、まとめて効率よく出したい場合があります。標準ライブラリは、ファイルごとに「バッファリング」の方式を持っていて、それを選べるのが `std::setvbuf` です。

<strong>バッファーの方式と大きさを指定する</strong>関数で、ファイルを開いた直後、読み書きの前に呼びます。""",
  tips=["方式は 3 つ。`_IOFBF`（全体をバッファー）、`_IOLBF`（行ごとに出す）、`_IONBF`（バッファーなし）",
        "ファイルを開いた直後、読み書きを始める前に呼ぶ",
        "戻り値は、成功なら 0",
        "渡したバッファーは、ファイルを閉じるまで生きていなければならない"],
  details="""### std::setvbuf {#setvbuf}

```cpp
int setvbuf(std::FILE* stream, char* buffer, int mode, std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 設定するファイル |
| `buffer` | `char*` | 使うバッファー。`nullptr` なら、ライブラリが用意する |
| `mode` | `int` | `_IOFBF`、`_IOLBF`、`_IONBF` のどれか |
| `size` | `size_t` | バッファーの大きさ（バイト） |

`_IOFBF` は、バッファーが一杯になるまで溜めてから書き出します（フル バッファリング）。ディスクへのファイルの標準的な方式で、速さが出ます。`_IOLBF` は、改行が出るたびに書き出します（行バッファリング）。端末への出力の標準です。`_IONBF` は、バッファーを使わず、書くたびに出します。

`_IONBF` にすると、クラッシュしても、書いた分が残るので、デバッグ ログに向きます。そのぶん、書き込みの回数が増えて遅くなります。`stderr` が既定でバッファーなしなのは、この理由です。

`buffer` に自分の配列を渡す場合、その配列は、ファイルを閉じるまで有効でなければなりません。関数のローカル配列を渡して、関数を抜けたあとにファイルを使うと、壊れます。`nullptr` を渡して、ライブラリに任せるほうが安全です。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("debug.log", "w");

  // バッファーなし: 書いた分がすぐ OS に渡される
  int r = std::setvbuf(f, nullptr, _IONBF, 0);
  std::println("設定できた: {}", r == 0);

  std::fputs("start\\n", f);

  // 閉じる前に別のハンドルで読んでも、書いた内容が見える
  std::FILE* peek = std::fopen("debug.log", "r");
  char buf[16] = {};
  std::fgets(buf, sizeof(buf), peek);
  std::print("読めた: {}", buf);
  std::fclose(peek);
  std::fclose(f);
}""",
  out="""設定できた: true
読めた: start""",
  uses="""クラッシュの原因を調べるデバッグ ログで、`_IONBF` にします。クラッシュ直前の行まで、確実にファイルに残るので、原因の特定に役立ちます。製品では、速さを優先して、通常のフル バッファリングに戻します。

コンソールへの出力で、改行なしの進捗表示を即座に出したいときも、`setvbuf(stdout, nullptr, _IONBF, 0)` が使えます。""",
  mistakes=[("読み書きを始めた後に呼んで、効かない", "最初の入出力の前に呼びます。"),
            ("ローカル配列を渡して、関数を抜けたあとに壊れる", "ファイルを閉じるまで生きている配列を渡すか、`nullptr` にします。")],
  similar=[("[`setbuf`](setbuf.md)", "バッファーを指定するだけの簡易版"),
           ("[`fflush`](fflush.md)", "その場で書き出す")],
  memo=["バッファリングの方式と大きさを決める", "最初の入出力の前に呼ぶ", "デバッグ ログは `_IONBF`"])

rewrite(C + 'setbuf.md',
  intro="""`setvbuf` の簡易版です。自分で用意したバッファーを、ファイルに使わせたい、または、バッファーを無効にしたい、という単純な場面のために残されています。""",
  tips=["`setbuf(ファイル, バッファー)`。`BUFSIZ` 以上の大きさの配列を渡す",
        "`nullptr` を渡すと、バッファーなしになる",
        "戻り値はなく、成否は分からない",
        "新しいコードでは、方式と大きさを指定できる `setvbuf` を使う"],
  details="""### std::setbuf {#setbuf}

```cpp
void setbuf(std::FILE* stream, char* buffer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 設定するファイル |
| `buffer` | `char*` | 使うバッファー。大きさは `BUFSIZ` 以上。`nullptr` ならバッファーなし |

`buffer` が `nullptr` でないときは `setvbuf(stream, buffer, _IOFBF, BUFSIZ)` と同じ、`nullptr` のときは `setvbuf(stream, nullptr, _IONBF, 0)` と同じです。

戻り値がないので、設定が成功したか分かりません。大きさも [`BUFSIZ`](bufsiz.md) 固定です。方式や大きさを選びたい、失敗を確かめたい、という場合は `setvbuf` を使います。

C++ では、`setbuf` は、C の古いコードを移植するとき以外に、使う場面がありません。C++23 でも非推奨にはなっていませんが、`setvbuf` で十分です。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("unbuf.log", "w");
  std::setbuf(f, nullptr);          // バッファーなし
  std::fputs("A", f);

  std::FILE* peek = std::fopen("unbuf.log", "r");
  int c = std::fgetc(peek);
  std::println("すぐ読める: {}", c == 'A');
  std::fclose(peek);
  std::fclose(f);
}""",
  out="すぐ読める: true",
  uses="""古い C のコードの移植で、「`setbuf(stdout, NULL)` で標準出力のバッファーを切る」書き方に出会います。同じことは `setvbuf(stdout, nullptr, _IONBF, 0)` で書けます。""",
  mistakes=[("`BUFSIZ` より小さい配列を渡して、メモリを壊す", "`BUFSIZ` 以上の大きさが要ります。"),
            ("読み書きを始めた後に呼んで、効かない", "最初の入出力の前に呼びます。")],
  similar=[("[`setvbuf`](setvbuf.md)", "方式と大きさを選べる。戻り値で成否も分かる"),
           ("[`BUFSIZ`](bufsiz.md)", "既定のバッファーの大きさ")],
  memo=["バッファーを指定するだけの簡易版", "`nullptr` でバッファーなし", "新しくは `setvbuf`"])

rewrite(C + 'fgetpos.md',
  intro="""ファイルの途中で、あとで戻ってきたい位置を記録しておきたい。`ftell` は `long` で位置を返すので、巨大なファイルや、テキスト モードの特殊な状態では、足りないことがあります。`std::fgetpos` は、<strong>位置の情報を、ライブラリが決めた型（`fpos_t`）にそのまま保存する</strong>関数です。""",
  tips=["`fgetpos(ファイル, &pos)` で、今の位置を `fpos_t` に保存する",
        "保存した位置に戻るのは `fsetpos`",
        "`fpos_t` の中身は不透明。数値として表示したり、計算したりしない",
        "戻り値は、成功なら 0、失敗なら 0 以外"],
  details="""### std::fgetpos {#fgetpos}

```cpp
int fgetpos(std::FILE* stream, std::fpos_t* pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を調べるファイル |
| `pos` | `fpos_t*` | 位置の保存先 |

`fpos_t` には、位置だけでなく、マルチバイト文字の解析途中の状態など、ファイルを同じ状態で再開するための情報が入ります。そのため、`ftell` の `long` より、確実に元の状態へ戻れます。

型の中身は規格が決めていないので、整数のように表示したり、足し算したりできません。保存して、`fsetpos` に渡すためだけの値です。

Windows の MSVC では `fpos_t` が 64 ビットなので、2 GB を超えるファイルでも使えます。`long` が 32 ビットの環境で、大きなファイルの位置を保存する、簡単な方法の 1 つです。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("ab.txt", "w");
  std::fputs("0123456789", out);
  std::fclose(out);

  std::FILE* f = std::fopen("ab.txt", "r");
  std::fgetc(f);
  std::fgetc(f);                       // 2 文字進める

  std::fpos_t mark;
  std::fgetpos(f, &mark);              // ここ（3 文字目の手前）を記録する
  std::println("記録した位置から: {}", static_cast<char>(std::fgetc(f)));

  std::fsetpos(f, &mark);              // 記録した位置に戻る
  std::println("戻って読み直し: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}""",
  out="""記録した位置から: 2
戻って読み直し: 2""",
  uses="""パーサーが、先の内容を見て、うまくいかなければ元の位置からやり直す（バックトラック）ときに使います。`fgetpos` で位置を保存し、試して失敗したら `fsetpos` で戻ります。

位置が数値で扱えて足りるなら、`ftell` と `fseek` のほうが簡単です。""",
  mistakes=[("`fpos_t` を整数として表示・計算しようとする", "中身は不透明です。保存して `fsetpos` に渡すだけにします。"),
            ("別のファイルの `fpos_t` を使い回す", "その `fpos_t` は、取得したファイルでのみ有効です。")],
  similar=[("[`fsetpos`](fsetpos.md)", "保存した位置に戻る"),
           ("[`ftell`](ftell.md)", "位置を `long` で返す"),
           ("[`fseek`](fseek.md)", "数値で位置を動かす")],
  memo=["位置を `fpos_t` に保存する", "戻るのは `fsetpos`", "中身は数値として扱わない"])

rewrite(C + 'fsetpos.md',
  intro="""`fgetpos` で保存しておいた位置に、ファイルの読み書きの位置を戻します。数値として扱えない `fpos_t` を、そのまま受け取って、同じ状態から再開できる関数が `std::fsetpos` です。""",
  tips=["`fsetpos(ファイル, &pos)`。`fgetpos` で得た `pos` を渡す",
        "戻り値は、成功なら 0、失敗なら 0 以外",
        "終わりとエラーの印も消える",
        "別のファイルで得た `pos` を渡してはいけない"],
  details="""### std::fsetpos {#fsetpos}

```cpp
int fsetpos(std::FILE* stream, const std::fpos_t* pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を戻すファイル |
| `pos` | `const fpos_t*` | `fgetpos` で保存した位置 |

保存した時点の位置と、ファイルの解析状態に戻ります。ファイルの終わりの印は消え、`ungetc` で戻した文字も捨てられます。

位置が `long` に収まるなら、`fseek(f, pos, SEEK_SET)` でも戻れます。`fsetpos` が必要なのは、`long` に収まらない巨大なファイルや、`fpos_t` でしか表せない状態を持つ、特殊な場合です。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("seq.txt", "w");
  std::fputs("ABCDE", out);
  std::fclose(out);

  std::FILE* f = std::fopen("seq.txt", "r");
  std::fpos_t start;
  std::fgetpos(f, &start);              // 先頭を記録する

  while (std::fgetc(f) != EOF) {}       // 最後まで読む
  std::println("読み終えた: {}", std::feof(f) != 0);

  int r = std::fsetpos(f, &start);      // 先頭に戻る。印も消える
  std::println("戻れた: {}  終わりの印: {}", r == 0, std::feof(f) != 0);
  std::println("先頭の文字: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}""",
  out="""読み終えた: true
戻れた: true  終わりの印: false
先頭の文字: A""",
  uses="""`fgetpos` と組み合わせて、バックトラックに使います。`rewind` との違いは、先頭以外の、記録した任意の位置へ戻れる点です。""",
  mistakes=[("別のファイルの `fpos_t` を渡す", "取得したファイルのものだけが有効です。"),
            ("戻り値を確かめない", "失敗すると、位置は変わりません。続きの処理が、意図と違う場所で動きます。")],
  similar=[("[`fgetpos`](fgetpos.md)", "位置を保存する"),
           ("[`fseek`](fseek.md)", "数値で位置を動かす"),
           ("[`rewind`](rewind.md)", "先頭へ戻る")],
  memo=["保存した位置に戻る", "終わりの印も消える", "戻り値で成否を確かめる"])

rewrite(C + 'freopen.md',
  intro="""ゲームの `stdout` や `stderr` に出ているメッセージを、画面ではなく、ログ ファイルに保存したい。プログラムのあちこちの `printf` を書き換えずに、出力先だけを差し替える関数が `std::freopen` です。

<strong>すでにある `FILE*` を閉じて、別のファイルに開き直します</strong>。`stdout` のような標準ストリームの向きを変えるときの、定番です。""",
  tips=["`freopen(パス, モード, ストリーム)`。戻り値は、成功ならそのストリーム、失敗は `nullptr`",
        "`stdout`、`stderr`、`stdin` の出力先・入力元を、ファイルに変えられる",
        "元に戻すのは難しい（環境依存）。リダイレクトは起動時に 1 回だけにする",
        "GUI アプリ（Windows のサブシステム `WINDOWS`）では、`stdout` が元々つながっていない"],
  details="""### std::freopen {#freopen}

```cpp
std::FILE* freopen(const char* filename, const char* mode, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` | 新しく開くファイルのパス。`nullptr` なら、同じファイルでモードだけ変える（環境による） |
| `mode` | `const char*` | 開き方。`fopen` と同じ |
| `stream` | `FILE*` | 開き直す対象。`stdout` などでもよい |

まず、`stream` で開いているファイルを閉じ、そのあと `filename` を `mode` で開いて、同じ `FILE*` に結び付けます。失敗すると、元のストリームは閉じられたままになるので、使い続けられません。戻り値の `nullptr` を確かめます。

`freopen("log.txt", "w", stdout)` を実行すると、その後の `printf` や `std::print`（`stdout` への出力）が、すべて `log.txt` に書かれます。個々の呼び出しを直さなくて済むのが利点です。

Windows の GUI アプリ（`WinMain` で始まるもの）では、コンソールが無いため、`stdout` が使えません。`AllocConsole` でコンソールを作り、`freopen(\"CONOUT$\", \"w\", stdout)` でつなぎ直す、というデバッグ用の定番があります。""",
  code="""#include <cstdio>
#include <print>

int main() {
  // 標準エラー出力をファイルに向け直す
  std::FILE* r = std::freopen("err.log", "w", stderr);
  if (!r) return 1;

  std::fprintf(stderr, "警告: テクスチャがありません\\n");   // 画面ではなくファイルに入る
  std::fflush(stderr);

  // ファイルに入ったか確かめる
  std::FILE* in = std::fopen("err.log", "r");
  char buf[64];
  std::fgets(buf, sizeof(buf), in);
  std::fclose(in);
  std::print("ログの中身: {}", buf);
}""",
  out="""ログの中身: 警告: テクスチャがありません""",
  uses="""ゲームの起動時に、`stdout` と `stderr` をログ ファイルに向けます。サードパーティのライブラリが `printf` で出すメッセージも、まとめてログに残せます。

Windows の GUI アプリでは、デバッグ用に、コンソールを開いて `freopen("CONOUT$", "w", stdout)` でつなぎます。製品版では外します。""",
  mistakes=[("失敗しても続けて、閉じられた `stdout` に書いて落ちる", "`nullptr` が返ったら、元のストリームは使えません。エラーを `stderr` 以外に伝える手段を用意します。"),
            ("途中で何度も向き先を変えようとして、混乱する", "起動時に 1 回だけにします。")],
  similar=[("[`fopen`](fopen.md)", "新しいファイルを開く"),
           ("[`fclose`](fclose.md)", "閉じる")],
  memo=["既存のストリームを別のファイルに開き直す", "`stdout` の向き先を変えられる", "失敗するとストリームは使えない"])

rewrite(C + 'tmpnam.md',
  intro="""一時ファイルの名前だけを、先に決めたい。`std::tmpnam` は、<strong>ほかのファイルとぶつからない名前</strong>を作る関数ですが、名前を作ってから実際にファイルを作るまでの間に、他のプロセスが同じ名前を作ってしまう危険があり、現在は使うことが勧められません。""",
  tips=["`tmpnam(バッファー)` で、使われていない名前を作る。失敗は `nullptr`",
        "名前の確認とファイルの作成が別なので、競合する（TOCTOU）",
        "MSVC や GCC は、警告を出す。新しいコードでは使わない",
        "代わりに `tmpfile`、または `temp_directory_path` に自分で名前を付ける"],
  details="""### std::tmpnam {#tmpnam}

```cpp
char* tmpnam(char* filename);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `char*` | 名前を入れるバッファー（`L_tmpnam` バイト以上）。`nullptr` なら、内部の静的な領域に入れる |

使われていない名前を返します。返された名前は、作成した時点では未使用ですが、そのファイルをこちらが作るまでに、別のプロセスが同じ名前で作成できます。この隙を突くと、他者に自分の一時ファイルを乗っ取られる脆弱性になります。

`filename` に `nullptr` を渡すと、内部の領域に名前を入れ、その場所を返します。2 回目の呼び出しで上書きされ、複数のスレッドから呼ぶと壊れます。

GCC は、リンク時に「`tmpnam` は危険」と警告し、MSVC は警告 C4996 を出します。代わりに、[`tmpfile`](tmpfile.md)（名前を出さず、競合なしで開く）や、`std::filesystem::temp_directory_path()` の下に、プロセス番号や乱数で自分の名前を作る方法を使います。""",
  code="""#include <cstdio>
#include <print>

int main() {
  char name[L_tmpnam];
  char* r = std::tmpnam(name);
  std::println("名前が作れた: {}", r != nullptr);
  std::println("空ではない: {}", name[0] != '\\0');
}""",
  out="""名前が作れた: true
空ではない: true""",
  uses="""新しいコードでは使いません。古い C のコードに出てきたときは、`tmpfile` か、`mkstemp`（POSIX）、`std::filesystem` を使った書き方に置き換えます。""",
  mistakes=[("名前を作ってから、あとでファイルを作って、競合する", "確認と作成の間に隙があります。`tmpfile` のように、作成と同時に開く方法を使います。"),
            ("`nullptr` を渡して、複数のスレッドから呼ぶ", "内部の領域が共有され、壊れます。")],
  similar=[("[`tmpfile`](tmpfile.md)", "競合のない一時ファイルを開く"),
           ("[`temp_directory_path`](../filesystem/temp_directory_path.md)", "一時フォルダーの場所")],
  memo=["使われていない名前を作る", "競合に弱く、非推奨", "代わりに `tmpfile`"])
print('cs4 ok')
