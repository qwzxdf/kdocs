"""バッチ 15: <cstdio> / <cwchar> の未登録分。"""
from mk import *  # noqa: F401,F403

SIO = "io/cstdio/"
SIOI = "[`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。"
TMP = "std::FILE* f = std::tmpfile();\n"


def F(name, summary, intro, sig, args, ret, body, out, use, miss, sim, ver=None, pre="", inc=("cstdio", "print"), rank="rare", tips=None, cr=None):
    Q(SIO + name.lower() + ".md", name if name.isupper() or name in ("FILE",) else "std::" + name, summary, rank, [*inc], intro,
      tips or ["C 由来の入出力関数。", "戻り値で失敗を調べる。", "新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx="入出力の量に比例", ver=ver, info=SIOI, pre=pre, rj=f"cstdio/{name.lower()}.html", cr=f"io/c/{cr or name}")


F("fprintf", "書式を指定して、ファイルに出力する。", "`printf` は標準出力に出しますが、`fprintf` は出力先の `FILE*` を指定できます。ファイルにも `stdout` にも `stderr` にも、同じ書式で書けます。", "int fprintf(std::FILE* stream, const char* format, ...);",
  [("stream", "FILE*", "出力先"), ("format", "const char*", "書式文字列（`%d` `%s` など）"), ("...", "可変引数", "書式に対応する値")], "書き込んだ文字数。失敗したら負の値", 'std::fprintf(stdout, "%d-%s\\n", 1, "a");', "1-a",
  "ログファイルに書式つきで書く", ("書式と型が合わない", "`%d` に `double` を渡すなど、型が合わないと未定義動作です。新しいコードでは型安全な `std::print` を使います。"), [("[`printf`](printf.md)", "標準出力へ"), ("[`sprintf`](sprintf.md)", "バッファへ")], inc=("cstdio",))
F("sprintf", "書式を指定して、文字配列に書き込む。", "文字列を組み立てたいとき、`sprintf` で配列に書式つきで書き込めます。ただし、配列の大きさを確かめないので、あふれる危険があります。`snprintf` を使うほうが安全です。", "int sprintf(char* buffer, const char* format, ...);",
  [("buffer", "char*", "書き込み先（十分な大きさが必要）"), ("format", "const char*", "書式文字列"), ("...", "可変引数", "書式に対応する値")], "書き込んだ文字数（終端を除く）", 'char buf[16];\nstd::sprintf(buf, "%03d", 7);\nstd::println("{}", buf);', "007",
  "（古い C のコードの保守）", ("バッファがあふれる", "長さの確認がありません。`snprintf` か `std::format` を使います。"), [("[`snprintf`](../../memory/cstring/snprintf.md)", "大きさを指定する"), ("[`std::format`](../../utilities/format.md)", "型安全な書き方")])
F("vprintf", "可変引数のリスト（va_list）を使って、標準出力に出力する。", "`printf` を包んだ自作のログ関数を書くとき、受け取った `...` をそのまま `printf` には渡せません。`va_list` にして `vprintf` に渡します。", "int vprintf(const char* format, std::va_list vlist);",
  [("format", "const char*", "書式文字列"), ("vlist", "va_list", "`va_start` で作った引数のリスト")], "書き込んだ文字数。失敗したら負の値", 'Log("%d-%s\\n", 1, "a");', "1-a",
  "自作のログ関数", ("`va_end` を忘れる", "`va_start` したら、必ず `va_end` で閉じます。"), [("[`printf`](printf.md)", "直接書く"), ("[`va_start`](../va_start.md)", "可変引数")], inc=("cstdarg", "cstdio"),
  pre="void Log(const char* fmt, ...) {\n  va_list ap;\n  va_start(ap, fmt);\n  std::vprintf(fmt, ap);\n  va_end(ap);\n}")
F("vfprintf", "可変引数のリスト（va_list）を使って、ファイルに出力する。", "`fprintf` を包んだ自作のログ関数用です。出力先の `FILE*` を指定できます。", "int vfprintf(std::FILE* stream, const char* format, std::va_list vlist);",
  [("stream", "FILE*", "出力先"), ("format", "const char*", "書式文字列"), ("vlist", "va_list", "引数のリスト")], "書き込んだ文字数。失敗したら負の値", 'Log("%d-%s\\n", 1, "a");', "1-a",
  "自作のログ関数（出力先を選べる）", ("`va_end` を忘れる", "`va_start` したら、必ず `va_end` で閉じます。"), [("[`vprintf`](vprintf.md)", "標準出力"), ("[`fprintf`](fprintf.md)", "直接書く")], inc=("cstdarg", "cstdio"),
  pre="void Log(const char* fmt, ...) {\n  va_list ap;\n  va_start(ap, fmt);\n  std::vfprintf(stdout, fmt, ap);\n  va_end(ap);\n}")
F("vsprintf", "可変引数のリスト（va_list）を使って、文字配列に書き込む。", "`sprintf` を包んだ自作の書式化関数用です。配列の大きさを確かめないため、`vsnprintf` のほうが安全です。", "int vsprintf(char* buffer, const char* format, std::va_list vlist);",
  [("buffer", "char*", "書き込み先"), ("format", "const char*", "書式文字列"), ("vlist", "va_list", "引数のリスト")], "書き込んだ文字数", 'std::println("{}", Format("%d-%s", 1, "a"));', "1-a",
  "（古い C のコードの保守）", ("バッファがあふれる", "長さの確認がありません。`vsnprintf` を使います。"), [("[`vsnprintf`](vsnprintf.md)", "大きさを指定する")], inc=("cstdarg", "cstdio", "print", "string"),
  pre="std::string Format(const char* fmt, ...) {\n  char buf[32];\n  va_list ap;\n  va_start(ap, fmt);\n  std::vsprintf(buf, fmt, ap);\n  va_end(ap);\n  return buf;\n}")
F("vsnprintf", "可変引数のリスト（va_list）を使って、大きさを指定して文字配列に書き込む。", "自作の書式化関数で、必要な大きさを先に調べてから、ちょうどの大きさで確保する、という使い方ができます。`nullptr` と 0 を渡すと、必要な長さだけが返ります。", "int vsnprintf(char* buffer, std::size_t buf_size, const char* format, std::va_list vlist);",
  [("buffer", "char*", "書き込み先（`nullptr` も可）"), ("buf_size", "size_t", "書き込める最大のバイト数（終端を含む）"), ("format", "const char*", "書式文字列"), ("vlist", "va_list", "引数のリスト")], "書き込めたはずの文字数（終端を除く）", 'std::println("{}", Format("%d-%s", 1, "a"));', "1-a",
  "自作の書式化関数を、安全に書く", ("`va_list` を 2 回使う", "`va_list` は 1 回使うと進んでしまいます。2 回使うなら `va_copy` で複製します。"), [("[`vsprintf`](vsprintf.md)", "大きさを指定しない"), ("[`va_copy`](../va_copy.md)", "リストを複製する")], inc=("cstdarg", "cstdio", "print", "string"),
  pre="std::string Format(const char* fmt, ...) {\n  va_list ap;\n  va_start(ap, fmt);\n  va_list ap2;\n  va_copy(ap2, ap);\n  int n = std::vsnprintf(nullptr, 0, fmt, ap);\n  std::string s(n, '\\0');\n  std::vsnprintf(s.data(), n + 1, fmt, ap2);\n  va_end(ap2);\n  va_end(ap);\n  return s;\n}")
F("scanf", "標準入力から、書式を指定して読み込む。", "`scanf(\"%d\", &n)` のように、書式に合わせて標準入力から値を読みます。読み込めた個数が戻ります。入力の失敗の扱いが難しく、新しいコードでは `std::cin` が安全です。", "int scanf(const char* format, ...);",
  [("format", "const char*", "書式文字列"), ("...", "ポインタ", "読み込んだ値を入れる場所")], "読み込めた個数。入力が終わったら `EOF`", 'int n = 0;\nint count = std::scanf("%d", &n);\nstd::println("{} {}", count, n);', None,
  "（競技プログラミングや、古い C のコード）", ("`&` を忘れる", "変数のアドレス（`&n`）を渡さないと、未定義動作です。"), [("[`std::cin`](../cin.md)", "C++ の入力"), ("[`sscanf`](sscanf.md)", "文字列から読む")])
F("fscanf", "ファイルから、書式を指定して読み込む。", "`scanf` の、読み込み元の `FILE*` を指定できる版です。", "int fscanf(std::FILE* stream, const char* format, ...);",
  [("stream", "FILE*", "読み込み元"), ("format", "const char*", "書式文字列"), ("...", "ポインタ", "読み込んだ値を入れる場所")], "読み込めた個数。入力が終わったら `EOF`",
  TMP + 'std::fputs("42 7", f);\nstd::rewind(f);\nint a = 0;\nint b = 0;\nstd::fscanf(f, "%d %d", &a, &b);\nstd::println("{} {}", a, b);\nstd::fclose(f);', "42 7", "テキストの設定ファイルの数値を読む", ("戻り値を確かめない", "戻り値が期待した個数でなければ、読み込みに失敗しています。"), [("[`scanf`](scanf.md)", "標準入力"), ("[`fgets`](fgets.md)", "1 行を読む")])
F("sscanf", "文字列から、書式を指定して読み込む。", "文字列を解析して、数値などを取り出したいとき、`sscanf` が使えます。1 行を `fgets` で読んでから、`sscanf` で分解する、という使い方が定番です。", "int sscanf(const char* buffer, const char* format, ...);",
  [("buffer", "const char*", "読み込み元の文字列"), ("format", "const char*", "書式文字列"), ("...", "ポインタ", "読み込んだ値を入れる場所")], "読み込めた個数。入力が終わったら `EOF`", 'int a = 0;\nint b = 0;\nstd::sscanf("42 7", "%d %d", &a, &b);\nstd::println("{} {}", a, b);', "42 7",
  "コマンド文字列の解析", ("戻り値を確かめない", "戻り値が期待した個数でなければ、解析に失敗しています。新しいコードでは `std::from_chars` が安全です。"), [("[`from_chars`](../from_chars.md)", "新しい書き方"), ("[`fgets`](fgets.md)", "1 行を読む")])
F("freopen", "開いているファイル（stdout など）を、別のファイルに付け替える。", "`stdout` の出力先を、ファイルに切り替えたいことがあります（ログ出力の保存など）。`freopen(\"log.txt\", \"w\", stdout)` で、以降の `printf` の出力がファイルへ向かいます。元に戻すのは難しいので、必要な場面は限られます。", "std::FILE* freopen(const char* filename, const char* mode, std::FILE* stream);",
  [("filename", "const char*", "新しいファイル名"), ("mode", "const char*", "開くモード（`\"w\"` など）"), ("stream", "FILE*", "付け替えるストリーム（`stdout` など）")], "成功なら `stream`、失敗なら `nullptr`", 'if (std::freopen("out.txt", "w", stdout) != nullptr) {\n  std::printf("このメッセージはファイルへ\\n");\n}', None,
  "標準出力をファイルに保存する", ("元に戻せない", "付け替えると、元の出力先には戻せません。一時的な切り替えには `rdbuf` を使います。"), [("[`fopen`](fopen.md)", "ファイルを開く")])
F("fclose", "ファイルを閉じる。", "`fopen` で開いたファイルは、使い終わったら必ず閉じます。閉じないと、バッファの内容が書き出されなかったり、ファイル記述子がリークしたりします。", "int fclose(std::FILE* stream);",
  [("stream", "FILE*", "閉じるファイル")], "成功なら 0、失敗なら `EOF`", TMP + 'std::println("{}", std::fclose(f));', "0",
  "ファイルを閉じる（RAII で包むのが安全）", ("閉じたあとに使う", "閉じたあとの `FILE*` を使うと未定義動作です。`unique_ptr` と `fclose` を組み合わせると、閉じ忘れを防げます。"), [("[`fopen`](fopen.md)", "開く"), ("[`std::ifstream`](../ifstream.md)", "デストラクタで自動で閉じる")])
F("fflush", "出力バッファの内容を、いまファイルに書き出す。", "出力はバッファに貯められて、まとめて書き出されます。`fflush` を呼ぶと、貯まっているぶんを、いまこの時点で書き出します。クラッシュ前にログを確実に残したいときに使います。", "int fflush(std::FILE* stream);",
  [("stream", "FILE*", "書き出すファイル。`nullptr` なら開いている出力ファイル全部")], "成功なら 0、失敗なら `EOF`", 'std::fputs("hello\\n", stdout);\nstd::println("{}", std::fflush(stdout));', "hello\n0",
  "クラッシュしても残したいログを書き出す", ("入力ストリームに使う", "入力ストリームへの `fflush` は未定義動作です（入力を捨てる用途には使えません）。"), [("[`std::flush`](../flush.md)", "C++ のフラッシュ")])
F("setbuf", "ファイルのバッファを、自分で指定した配列にする（または無効にする）。", "標準では、出力にバッファが付いています。`setbuf(stdout, nullptr)` でバッファを無効にすると、出力がすぐに書き出されます。デバッグ出力の順序を保つときなどに使います。", "void setbuf(std::FILE* stream, char* buffer);",
  [("stream", "FILE*", "対象のファイル"), ("buffer", "char*", "`BUFSIZ` バイト以上の配列。`nullptr` ならバッファなし")], "なし", 'std::setbuf(stdout, nullptr);  // バッファを無効にする\nstd::fputs("unbuffered\\n", stdout);', "unbuffered",
  "出力の順序をデバッグで確実にする", ("入出力を始めたあとに呼ぶ", "最初の入出力の前に呼ぶ必要があります。"), [("[`setvbuf`](setvbuf.md)", "モードと大きさを選べる")])
F("setvbuf", "ファイルのバッファの方式（全部・行・なし）と大きさを設定する。", "`setbuf` より細かく、バッファの方式（`_IOFBF` 全バッファ、`_IOLBF` 行バッファ、`_IONBF` なし）と大きさを指定します。", "int setvbuf(std::FILE* stream, char* buffer, int mode, std::size_t size);",
  [("stream", "FILE*", "対象のファイル"), ("buffer", "char*", "バッファ（`nullptr` なら自動）"), ("mode", "int", "`_IOFBF`・`_IOLBF`・`_IONBF`"), ("size", "size_t", "バッファの大きさ")], "成功なら 0", 'static char buf[1024];\nstd::println("{}", std::setvbuf(stdout, buf, _IOFBF, sizeof buf));', "0",
  "大量出力の前にバッファを大きくする", ("ローカル配列を渡す", "バッファは、ファイルが閉じられるまで生きている必要があります。`static` にします。"), [("[`setbuf`](setbuf.md)", "簡易版")])
F("fgetc", "ファイルから 1 文字を読む。", "ファイルから、1 バイトを `int` として読みます。終端やエラーのときは `EOF` が返るため、戻り値は `char` ではなく `int` で受けます。", "int fgetc(std::FILE* stream);",
  [("stream", "FILE*", "読み込み元")], "読んだ文字（`unsigned char` を `int` にした値）。終端やエラーなら `EOF`", TMP + 'std::fputs("A", f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "A",
  "1 文字ずつ読む処理", ("戻り値を `char` で受ける", "`char` で受けると、`EOF` と文字 `0xFF` が区別できなくなります。`int` で受けます。"), [("[`getc`](getc.md)", "マクロの場合がある"), ("[`fgets`](fgets.md)", "1 行を読む")])
F("getc", "ファイルから 1 文字を読む（`fgetc` と同じ）。", "`fgetc` と同じ働きです。C 言語ではマクロとして実装されることがあり、引数が何度も評価される点が違いました。C++ では関数として扱われるので、`fgetc` との違いはありません。", "int getc(std::FILE* stream);",
  [("stream", "FILE*", "読み込み元")], "読んだ文字。終端やエラーなら `EOF`", TMP + 'std::fputs("A", f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::getc(f)));\nstd::fclose(f);', "A",
  "1 文字ずつ読む処理", ("戻り値を `char` で受ける", "`int` で受けます。"), [("[`fgetc`](fgetc.md)", "同じ働き")])
F("getchar", "標準入力から 1 文字を読む。", "`getc(stdin)` と同じです。ゲームでは使わず、コンソールの簡単な入力待ちで使われます。", "int getchar();",
  [], "読んだ文字。終端やエラーなら `EOF`", 'int c = std::getchar();\nstd::println("{}", c != EOF);', None,
  "コンソールで Enter 待ち", ("改行が残る", "`scanf` の後の改行が残ることがあります。`getchar` で捨てます。"), [("[`fgetc`](fgetc.md)", "ファイルから")])
F("fputc", "ファイルに 1 文字を書く。", "ファイルに、1 バイトを書き込みます。成功すると書いた文字が返ります。", "int fputc(int ch, std::FILE* stream);",
  [("ch", "int", "書く文字"), ("stream", "FILE*", "書き込み先")], "書いた文字。失敗したら `EOF`", TMP + 'std::fputc(\'B\', f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "B",
  "1 文字ずつ書く処理", ("戻り値を確かめない", "ディスクがいっぱいの場合などは `EOF` が返ります。"), [("[`putc`](putc.md)", "同じ働き"), ("[`fputs`](fputs.md)", "文字列を書く")])
F("putc", "ファイルに 1 文字を書く（`fputc` と同じ）。", "`fputc` と同じ働きです。C 言語ではマクロとして実装されることがあります。", "int putc(int ch, std::FILE* stream);",
  [("ch", "int", "書く文字"), ("stream", "FILE*", "書き込み先")], "書いた文字。失敗したら `EOF`", TMP + 'std::putc(\'B\', f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "B",
  "1 文字ずつ書く処理", ("戻り値を確かめない", "失敗したら `EOF` が返ります。"), [("[`fputc`](fputc.md)", "同じ働き")])
F("putchar", "標準出力に 1 文字を書く。", "`putc(ch, stdout)` と同じです。", "int putchar(int ch);",
  [("ch", "int", "書く文字")], "書いた文字。失敗したら `EOF`", "std::putchar('X');\nstd::putchar('\\n');", "X",
  "コンソールに 1 文字を出す", ("戻り値を無視する", "ふつうは無視してかまいませんが、エラー検出が必要なら確かめます。"), [("[`fputc`](fputc.md)", "ファイルへ")], inc=("cstdio",))
F("fputs", "ファイルに文字列を書く（改行は付かない）。", "文字列を、そのままファイルに書き込みます。`puts` と違い、末尾に改行を自動で付けません。", "int fputs(const char* str, std::FILE* stream);",
  [("str", "const char*", "書く文字列（終端文字は書かれない）"), ("stream", "FILE*", "書き込み先")], "成功なら負でない値、失敗なら `EOF`", 'std::fputs("hi\\n", stdout);', "hi",
  "ログ 1 行を書く", ("改行が付くと思う", "`fputs` は改行を付けません。自分で `\\n` を書きます。"), [("[`puts`](puts.md)", "標準出力に改行つき"), ("[`fprintf`](fprintf.md)", "書式つき")], inc=("cstdio",))
F("puts", "標準出力に文字列と改行を書く。", "文字列を標準出力に書き、最後に改行を付けます。書式を使わない単純な出力に便利です。", "int puts(const char* str);",
  [("str", "const char*", "書く文字列")], "成功なら負でない値、失敗なら `EOF`", 'std::puts("hello");', "hello",
  "デバッグメッセージを 1 行出す", ("`fputs` と取り違える", "`puts` は改行を付け、`fputs` は付けません。"), [("[`fputs`](fputs.md)", "改行なし"), ("[`printf`](printf.md)", "書式つき")], inc=("cstdio",))
F("ungetc", "読んだ文字を 1 文字、ファイルに戻す。", "次の文字を見て、読むかどうかを決めたいときに、読んでから戻すことができます。戻せるのは、最低 1 文字までです。", "int ungetc(int ch, std::FILE* stream);",
  [("ch", "int", "戻す文字"), ("stream", "FILE*", "戻す先")], "戻した文字。失敗したら `EOF`", TMP + 'std::fputs("AB", f);\nstd::rewind(f);\nint c = std::fgetc(f);\nstd::ungetc(c, f);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "A",
  "字句解析で、先読みした文字を戻す", ("2 文字以上戻す", "保証されるのは 1 文字までです。"), [("[`fgetc`](fgetc.md)", "1 文字読む")])
F("ftell", "ファイルの現在位置を返す。", "いま、ファイルのどこを読み書きしているかを、先頭からのバイト数で返します。`fseek` で戻る位置を覚えておくときに使います。", "long ftell(std::FILE* stream);",
  [("stream", "FILE*", "対象のファイル")], "現在位置（失敗したら `-1L`）", TMP + 'std::fputs("abc", f);\nstd::println("{}", std::ftell(f));\nstd::fclose(f);', "3",
  "ファイルの大きさを調べる（末尾に移動して `ftell`）", ("2GB を超えるファイル", "`long` が 32 ビットの環境では、大きなファイルで使えません。`std::filesystem::file_size` を使います。"), [("[`fseek`](fseek.md)", "位置を動かす"), ("[`fgetpos`](fgetpos.md)", "位置を保存する")])
F("fgetpos", "ファイルの現在位置を、保存する。", "`ftell` と違い、大きなファイルでも使え、特殊な状態も保存できます。保存した位置は、`fsetpos` で復元します。", "int fgetpos(std::FILE* stream, std::fpos_t* pos);",
  [("stream", "FILE*", "対象のファイル"), ("pos", "fpos_t*", "位置の保存先")], "成功なら 0", TMP + 'std::fputs("abc", f);\nstd::rewind(f);\nstd::fpos_t pos;\nstd::fgetpos(f, &pos);\nstd::fgetc(f);\nstd::fsetpos(f, &pos);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "a",
  "あとで戻るために位置を覚える", ("保存した値を数値として扱う", "`fpos_t` の中身は実装依存です。計算には使えません。"), [("[`fsetpos`](fsetpos.md)", "位置を復元する"), ("[`ftell`](ftell.md)", "数値で位置を取る")])
F("fseek", "ファイルの読み書き位置を動かす。", "ファイルの途中に飛んで、読み書きを続けたいときに使います。基準は `SEEK_SET`（先頭）・`SEEK_CUR`（現在位置）・`SEEK_END`（末尾）です。", "int fseek(std::FILE* stream, long offset, int origin);",
  [("stream", "FILE*", "対象のファイル"), ("offset", "long", "動かすバイト数"), ("origin", "int", "基準（`SEEK_SET`・`SEEK_CUR`・`SEEK_END`）")], "成功なら 0", TMP + 'std::fputs("abc", f);\nstd::fseek(f, 1, SEEK_SET);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "b",
  "ファイルの途中から読む", ("読みから書きに切り替えるときに呼ばない", "読み書きを切り替えるときは、間に `fseek` か `fflush` が必要です。"), [("[`ftell`](ftell.md)", "位置を取る"), ("[`rewind`](rewind.md)", "先頭に戻る")])
F("fsetpos", "`fgetpos` で保存した位置に、読み書き位置を戻す。", "`fgetpos` で保存した位置を、そのまま復元します。", "int fsetpos(std::FILE* stream, const std::fpos_t* pos);",
  [("stream", "FILE*", "対象のファイル"), ("pos", "const fpos_t*", "`fgetpos` で得た位置")], "成功なら 0", TMP + 'std::fputs("abc", f);\nstd::rewind(f);\nstd::fpos_t pos;\nstd::fgetpos(f, &pos);\nstd::fgetc(f);\nstd::fgetc(f);\nstd::fsetpos(f, &pos);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "a",
  "あとで戻る位置を復元する", ("別のファイルの位置を使う", "位置は、同じファイルのものを使います。"), [("[`fgetpos`](fgetpos.md)", "位置を保存する")])
F("rewind", "ファイルの読み書き位置を、先頭に戻す。", "`fseek(f, 0, SEEK_SET)` と同じですが、エラー状態もクリアします。書いたあとにすぐ読み返すときに使います。", "void rewind(std::FILE* stream);",
  [("stream", "FILE*", "対象のファイル")], "なし", TMP + 'std::fputs("a", f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "a",
  "書いたデータを読み返す", ("エラーを見落とす", "`rewind` は成否を返しません。確かめたいなら `fseek` を使います。"), [("[`fseek`](fseek.md)", "位置を動かす")])
F("clearerr", "ファイルのエラー状態と終端状態をクリアする。", "ファイルを最後まで読むと終端の状態（`feof`）が立ち、それ以降は読めません。`clearerr` で状態を戻すと、読み込みを再開できます（ファイルが後から伸びる場合など）。", "void clearerr(std::FILE* stream);",
  [("stream", "FILE*", "対象のファイル")], "なし", TMP + 'std::fputs("a", f);\nstd::rewind(f);\nstd::fgetc(f);\nstd::fgetc(f);  // 終端に達する\nstd::clearerr(f);\nstd::println("{}", std::feof(f) != 0);\nstd::fclose(f);', "false",
  "追記されるログファイルを読み続ける", ("クリアしたのに読めると思う", "状態をクリアしても、読む位置が末尾なら、読み込みは終端のままです。"), [("[`feof`](feof.md)", "終端かを調べる")])
F("feof", "ファイルの終端に達したかを調べる。", "`fgetc` などで、終端を**越えて読もうとした**とき、終端の状態が立ちます。ループ条件に `feof` だけを使うと、最後に 1 回余分に読むことになるので、読み込みの戻り値で判定します。", "int feof(std::FILE* stream);",
  [("stream", "FILE*", "対象のファイル")], "終端なら 0 以外", TMP + 'std::fputs("a", f);\nstd::rewind(f);\nstd::fgetc(f);\nstd::fgetc(f);  // 終端を越えて読む\nstd::println("{}", std::feof(f) != 0);\nstd::fclose(f);', "true",
  "読み込みが終端で終わったか、エラーで終わったかを区別する", ("`while (!feof(f))` でループする", "最後の読み込みの直後は、まだ終端の状態が立たないので、1 回余分にループします。`while (fgets(...))` のように、戻り値で判定します。"), [("[`ferror`](ferror.md)", "エラーかを調べる"), ("[`clearerr`](clearerr.md)", "状態をクリアする")])
F("ferror", "ファイルの読み書きでエラーが起きたかを調べる。", "読み込みが終わった理由が、終端なのか、エラーなのかを区別するために使います。", "int ferror(std::FILE* stream);",
  [("stream", "FILE*", "対象のファイル")], "エラーがあれば 0 以外", TMP + 'std::fputs("a", f);\nstd::println("{}", std::ferror(f) != 0);\nstd::fclose(f);', "false",
  "読み込みの失敗の原因を調べる", ("終端とエラーを混同する", "終端は `feof`、エラーは `ferror` です。"), [("[`feof`](feof.md)", "終端かを調べる"), ("[`perror`](perror.md)", "エラーの内容を出す")])
F("perror", "`errno` の内容を、説明つきで標準エラー出力に出す。", "ファイル操作の失敗の原因を、人が読める文字列で出したいとき、`perror(\"ファイル名\")` と書くと、`ファイル名: No such file or directory` のように標準エラー出力に出ます。", "void perror(const char* s);",
  [("s", "const char*", "先頭に付ける説明（`nullptr` や空文字列なら付けない）")], "なし", 'std::FILE* f = std::fopen("not_exist.txt", "r");\nif (f == nullptr) {\n  std::perror("open failed");\n}', None,
  "ファイルを開けなかった理由をログに出す", ("成功時の `errno` を見る", "`errno` は成功しても 0 に戻されません。失敗を確かめた直後に呼びます。"), [("[`strerror`](../../memory/cstring/strerror.md)", "文字列として取り出す")])
F("tmpfile", "自動で消える一時ファイルを作る。", "プログラムが終了するか、`fclose` で閉じると自動で消える、一時ファイルを作ります。名前は不要で、`\"wb+\"` で開かれます。中間データの一時保存に使います。", "std::FILE* tmpfile();",
  [], "成功なら `FILE*`、失敗なら `nullptr`", TMP + 'std::fputs("x", f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "x",
  "大きな中間データを一時的に置く", ("閉じ忘れる", "閉じるまでファイルが残ります。`fclose` を忘れないようにします。"), [("[`tmpnam`](tmpnam.md)", "名前だけを作る（非推奨）"), ("[`fopen`](fopen.md)", "名前つきで開く")])
F("tmpnam", "一時ファイルに使える名前を作る（非推奨）。", "一時ファイルの名前を作りますが、名前を作ってから開くまでの間に、他のプロセスが同じ名前を使う危険があります（競合）。`tmpfile` を使うほうが安全です。", "char* tmpnam(char* filename);",
  [("filename", "char*", "名前を入れる配列（`L_tmpnam` 以上の大きさ）。`nullptr` なら内部の静的領域")], "名前（失敗したら `nullptr`）", 'char name[L_tmpnam];\nstd::println("{}", std::tmpnam(name) != nullptr);', "true",
  "（古い C のコードの保守）", ("名前だけ作って後で開く", "競合の危険があります。`tmpfile` を使います。"), [("[`tmpfile`](tmpfile.md)", "安全な一時ファイル")])
F("FILE", "ファイルを表す型。", "`fopen` が返す `FILE*` の、`FILE` 型です。ファイルの位置、バッファ、エラー状態などをまとめて持ちますが、中身は実装依存なので、触れません。ポインタで受け渡して、`fclose` で閉じます。", "using FILE = /* 実装定義 */;",
  [], "なし（型）", TMP + 'std::println("{}", f != nullptr);\nstd::fclose(f);', "true", "C のファイル API を使うとき", ("`FILE` をコピーする", "`FILE` はコピーできません。必ず `FILE*` で扱います。"), [("[`fopen`](fopen.md)", "開く"), ("[`fclose`](fclose.md)", "閉じる")])
F("stdin", "標準入力を表す FILE*。", "プログラムが起動した時点で開いている、標準入力です。`fgets(buf, n, stdin)` のように使います。", "extern std::FILE* stdin;",
  [], "標準入力の `FILE*`", 'std::println("{}", stdin != nullptr);', "true", "コンソールからの入力", ("閉じる", "`stdin` を `fclose` で閉じないようにします。"), [("[`stdout`](stdout.md)", "標準出力"), ("[`std::cin`](../cin.md)", "C++ の標準入力")])
F("stdout", "標準出力を表す FILE*。", "プログラムが起動した時点で開いている、標準出力です。`fprintf(stdout, ...)` は `printf(...)` と同じです。", "extern std::FILE* stdout;",
  [], "標準出力の `FILE*`", 'std::fputs("out\\n", stdout);', "out", "コンソールへの出力", ("閉じる", "`stdout` を `fclose` で閉じないようにします。"), [("[`stdin`](stdin.md)", "標準入力"), ("[`stderr`](stderr.md)", "標準エラー出力")], inc=("cstdio",))
F("stderr", "標準エラー出力を表す FILE*。", "エラーメッセージ用の出力です。バッファなしで、すぐに書き出されます。普通の出力（`stdout`）と分けられるので、リダイレクトしても画面に出せます。", "extern std::FILE* stderr;",
  [], "標準エラー出力の `FILE*`", 'std::fputs("error\\n", stderr);', None, "エラーメッセージの出力", ("`stdout` と順序が混ざる", "`stdout` はバッファされるため、`stderr` と出力順が前後することがあります。"), [("[`stdout`](stdout.md)", "標準出力"), ("[`std::cerr`](../cerr.md)", "C++ の標準エラー出力")], inc=("cstdio",))
F("EOF", "ファイルの終端またはエラーを表す定数（負の整数）。", "`fgetc` などが、終端やエラーを知らせるときに返す値です。負の整数（ふつう `-1`）で、通常の文字（0〜255）と区別できます。", "#define EOF (-1)  // 値は実装定義（負の整数）",
  [], "負の整数の定数", 'std::println("{}", EOF < 0);', "true", "`fgetc` の結果の判定", ("`char` に入れる", "`char` に入れると、`0xFF` の文字と `EOF` が区別できません。`int` で受けます。"), [("[`fgetc`](fgetc.md)", "1 文字を読む")])
F("BUFSIZ", "標準のバッファの大きさ（バイト）。", "`setbuf` に渡す配列の、必要な大きさです。実装ごとに違いますが、最低 256 です。", "#define BUFSIZ /* 実装定義（256 以上） */",
  [], "バッファの大きさ", 'std::println("{}", BUFSIZ >= 256);', "true", "`setbuf` のバッファを用意する", ("固定値を決め打ちする", "実装ごとに値が違います。`BUFSIZ` を使います。"), [("[`setbuf`](setbuf.md)", "バッファを設定する")])
F("SEEK_SET", "`fseek` の基準：ファイルの先頭。", "`fseek(f, offset, SEEK_SET)` は、ファイルの**先頭**から `offset` バイトの位置に動かします。", "#define SEEK_SET /* 実装定義 */",
  [], "基準を表す整数", TMP + 'std::fputs("abc", f);\nstd::fseek(f, 2, SEEK_SET);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "c", "先頭から数えた位置に飛ぶ", ("負のオフセットを指定する", "`SEEK_SET` では負の値は使えません。"), [("[`SEEK_CUR`](seek_cur.md)", "現在位置"), ("[`SEEK_END`](seek_end.md)", "末尾")])
F("SEEK_CUR", "`fseek` の基準：現在位置。", "`fseek(f, offset, SEEK_CUR)` は、**現在の位置**から `offset` バイト動かします。負の値で戻れます。", "#define SEEK_CUR /* 実装定義 */",
  [], "基準を表す整数", TMP + 'std::fputs("abc", f);\nstd::rewind(f);\nstd::fgetc(f);\nstd::fseek(f, 1, SEEK_CUR);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "c", "いまの位置から読み飛ばす", ("テキストモードで使う", "テキストモードでは、0 以外のオフセットが使えない環境があります。"), [("[`SEEK_SET`](seek_set.md)", "先頭"), ("[`SEEK_END`](seek_end.md)", "末尾")])
F("SEEK_END", "`fseek` の基準：ファイルの末尾。", "`fseek(f, offset, SEEK_END)` は、ファイルの**末尾**から `offset` バイトの位置に動かします。`fseek(f, 0, SEEK_END)` のあと `ftell` を呼ぶと、ファイルの大きさが分かります。", "#define SEEK_END /* 実装定義 */",
  [], "基準を表す整数", TMP + 'std::fputs("abc", f);\nstd::fseek(f, -1, SEEK_END);\nstd::println("{}", static_cast<char>(std::fgetc(f)));\nstd::fclose(f);', "c", "ファイルの末尾から数えて読む", ("テキストモードで使う", "テキストモードでは、`SEEK_END` が使えない環境があります。バイナリモードで開きます。"), [("[`SEEK_SET`](seek_set.md)", "先頭"), ("[`SEEK_CUR`](seek_cur.md)", "現在位置")])
# snprintf は既存か確認が必要なので別に

# ================= cwchar =================
WC = "io/cwchar/"
WCI = "[`<cwchar>`](../cwchar.md) の概要が分かると読みやすいです。" if False else "[文字コード](@/encoding/index.md) の考え方を先に読んでください。"


def W(name, summary, intro, sig, args, ret, body, out, use, miss, sim, ver=None, pre="", inc=("cwchar", "print"), tips=None, cr=None):
    Q(WC + name.lower() + ".md", name if name.isupper() else "std::" + name, summary, "rare", [*inc], intro,
      tips or ["`wchar_t`（ワイド文字）版の C の関数。", "`char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。", "Windows の API でよく使われる。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx="文字数に比例", ver=ver, info=WCI, pre=pre, rj=f"cwchar/{name.lower()}.html", cr=f"string/wide/{cr or name}")


W("wprintf", "書式を指定して、ワイド文字で標準出力に出す。", "`printf` の `wchar_t` 版です。書式文字列も `L\"...\"` のワイド文字列を使います。1 つのストリームに、ふつうの `printf` とワイドの `wprintf` を混ぜて使うと、向き（orientation）が食い違って、動作しなくなります。", "int wprintf(const wchar_t* format, ...);",
  [("format", "const wchar_t*", "書式文字列"), ("...", "可変引数", "書式に対応する値")], "書き込んだ文字数。失敗したら負の値", 'std::wprintf(L"%d\\n", 42);', "42", "Windows のワイド文字列の出力", ("`printf` と混ぜる", "向きが食い違い、出力が壊れます。どちらかに統一します。"), [("[`printf`](../cstdio/printf.md)", "char 版")], inc=("cwchar",))
W("fwprintf", "書式を指定して、ワイド文字でファイルに出力する。", "`fprintf` の `wchar_t` 版です。出力先の `FILE*` を指定できます。", "int fwprintf(std::FILE* stream, const wchar_t* format, ...);",
  [("stream", "FILE*", "出力先"), ("format", "const wchar_t*", "書式文字列"), ("...", "可変引数", "書式に対応する値")], "書き込んだ文字数。失敗したら負の値", 'std::fwprintf(stdout, L"%d\\n", 42);', "42", "ワイド文字列をファイルに書く", ("`fprintf` と混ぜる", "ストリームの向きが食い違います。"), [("[`fprintf`](../cstdio/fprintf.md)", "char 版")], inc=("cwchar", "cstdio"))
W("swprintf", "書式を指定して、ワイド文字の配列に書き込む。", "`snprintf` の `wchar_t` 版です。大きさを指定するので、あふれにくくなっています。", "int swprintf(wchar_t* buffer, std::size_t bufsz, const wchar_t* format, ...);",
  [("buffer", "wchar_t*", "書き込み先"), ("bufsz", "size_t", "書き込める最大の文字数（終端を含む）"), ("format", "const wchar_t*", "書式文字列")], "書き込んだ文字数。入りきらなければ負の値", 'wchar_t buf[16];\nint n = std::swprintf(buf, 16, L"%d", 42);\nstd::println("{}", n);', "2", "Windows API 用のワイド文字列を組み立てる", ("入りきらなくても成功と思う", "あふれたときは、負の値が返ります。"), [("[`snprintf`](../../memory/cstring/snprintf.md)", "char 版")])
W("wscanf", "ワイド文字で、標準入力から書式を指定して読み込む。", "`scanf` の `wchar_t` 版です。", "int wscanf(const wchar_t* format, ...);",
  [("format", "const wchar_t*", "書式文字列"), ("...", "ポインタ", "読み込んだ値を入れる場所")], "読み込めた個数。入力が終わったら `WEOF`", 'int n = 0;\nstd::wscanf(L"%d", &n);\nstd::println("{}", n);', None, "ワイド文字の入力", ("`&` を忘れる", "変数のアドレスを渡さないと、未定義動作です。"), [("[`scanf`](../cstdio/scanf.md)", "char 版")])
W("fgetwc", "ファイルからワイド文字を 1 文字読む。", "`fgetc` の `wchar_t` 版です。終端やエラーのときは `WEOF` が返ります。", "std::wint_t fgetwc(std::FILE* stream);",
  [("stream", "FILE*", "読み込み元")], "読んだ文字。終端やエラーなら `WEOF`", TMP + 'std::fputwc(L\'A\', f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::fgetwc(f)));\nstd::fclose(f);', "A", "ワイド文字を 1 文字ずつ読む", ("`wchar_t` で受ける", "`WEOF` との区別のため、`wint_t` で受けます。"), [("[`fgetc`](../cstdio/fgetc.md)", "char 版")], inc=("cwchar", "cstdio", "print"))
W("fputwc", "ファイルにワイド文字を 1 文字書く。", "`fputc` の `wchar_t` 版です。", "std::wint_t fputwc(wchar_t ch, std::FILE* stream);",
  [("ch", "wchar_t", "書く文字"), ("stream", "FILE*", "書き込み先")], "書いた文字。失敗したら `WEOF`", TMP + 'std::fputwc(L\'A\', f);\nstd::rewind(f);\nstd::println("{}", static_cast<char>(std::fgetwc(f)));\nstd::fclose(f);', "A", "ワイド文字を 1 文字ずつ書く", ("戻り値を確かめない", "失敗したら `WEOF` が返ります。"), [("[`fputc`](../cstdio/fputc.md)", "char 版")], inc=("cwchar", "cstdio", "print"))
W("fgetws", "ファイルからワイド文字列を 1 行読む。", "`fgets` の `wchar_t` 版です。", "wchar_t* fgetws(wchar_t* str, int count, std::FILE* stream);",
  [("str", "wchar_t*", "読み込み先"), ("count", "int", "読む最大の文字数（終端を含む）"), ("stream", "FILE*", "読み込み元")], "成功なら `str`、失敗なら `nullptr`", TMP + 'std::fputws(L"abc\\n", f);\nstd::rewind(f);\nwchar_t buf[8];\nstd::fgetws(buf, 8, f);\nstd::println("{}", std::wcslen(buf));\nstd::fclose(f);', "4", "ワイド文字列を 1 行読む", ("改行が含まれることを忘れる", "改行も読み込まれます。長さに 1 含まれます。"), [("[`fgets`](../cstdio/fgets.md)", "char 版")], inc=("cwchar", "cstdio", "print"))
W("fputws", "ファイルにワイド文字列を書く。", "`fputs` の `wchar_t` 版です。", "int fputws(const wchar_t* str, std::FILE* stream);",
  [("str", "const wchar_t*", "書く文字列"), ("stream", "FILE*", "書き込み先")], "成功なら負でない値、失敗なら `EOF`", TMP + 'std::fputws(L"abc", f);\nstd::rewind(f);\nwchar_t buf[8] = {};\nstd::fgetws(buf, 8, f);\nstd::println("{}", std::wcslen(buf));\nstd::fclose(f);', "3", "ワイド文字列をファイルに書く", ("改行が付くと思う", "`fputws` は改行を付けません。"), [("[`fputs`](../cstdio/fputs.md)", "char 版")], inc=("cwchar", "cstdio", "print"))
W("wcscpy", "ワイド文字列をコピーする。", "`strcpy` の `wchar_t` 版です。コピー先の大きさを確かめないので、あふれる危険があります。", "wchar_t* wcscpy(wchar_t* dest, const wchar_t* src);",
  [("dest", "wchar_t*", "コピー先（十分な大きさ）"), ("src", "const wchar_t*", "コピー元")], "`dest`", 'wchar_t dst[8];\nstd::wcscpy(dst, L"abc");\nstd::println("{}", std::wcslen(dst));', "3", "（古い C のコードの保守）", ("コピー先が小さい", "あふれると未定義動作です。`std::wstring` を使います。"), [("[`strcpy`](../../memory/cstring/strcpy.md)", "char 版")])
W("wcscmp", "2 つのワイド文字列を比べる。", "`strcmp` の `wchar_t` 版です。辞書順ではなく、文字コードの順で比べます。", "int wcscmp(const wchar_t* lhs, const wchar_t* rhs);",
  [("lhs, rhs", "const wchar_t*", "比べる 2 つの文字列")], "`lhs < rhs` なら負、等しければ 0、大きければ正", 'std::println("{}", std::wcscmp(L"a", L"b") < 0);', "true", "ワイド文字列の比較", ("戻り値を `-1` / `1` と思う", "負・0・正のどれかです。値は決まっていません。"), [("[`strcmp`](../../memory/cstring/strcmp.md)", "char 版")])
W("wmemcpy", "ワイド文字の配列を、指定した個数だけコピーする。", "`memcpy` の `wchar_t` 版です。バイト数ではなく、**文字数**で指定します。", "wchar_t* wmemcpy(wchar_t* dest, const wchar_t* src, std::size_t count);",
  [("dest", "wchar_t*", "コピー先"), ("src", "const wchar_t*", "コピー元"), ("count", "size_t", "コピーする文字数")], "`dest`", 'wchar_t dst[4] = {};\nstd::wmemcpy(dst, L"abc", 3);\nstd::println("{}", std::wcslen(dst));', "3", "ワイド文字の配列のコピー", ("バイト数で指定する", "`wmemcpy` は文字数です。`sizeof` で渡すと大きすぎます。"), [("[`memcpy`](../../memory/cstring/memcpy.md)", "バイト単位")])
W("wcstol", "ワイド文字列を long に変換する。", "`strtol` の `wchar_t` 版です。", "long wcstol(const wchar_t* str, wchar_t** str_end, int base);",
  [("str", "const wchar_t*", "変換する文字列"), ("str_end", "wchar_t**", "読み終えた位置を受け取る（不要なら `nullptr`）"), ("base", "int", "進数")], "変換した値", 'std::println("{}", std::wcstol(L"42", nullptr, 10));', "42", "Windows API から来た文字列を数値にする", ("範囲外を確かめない", "範囲外のとき、`errno` が `ERANGE` になります。"), [("[`strtol`](../../numeric/cstdlib/strtol.md)", "char 版")])
W("btowc", "1 バイトの文字を、ワイド文字に変換する。", "`char` の 1 文字を、`wchar_t` に変換します。変換できなければ `WEOF` が返ります。", "std::wint_t btowc(int c);",
  [("c", "int", "変換する文字（`unsigned char` の値か `EOF`）")], "変換したワイド文字。できなければ `WEOF`", 'std::println("{}", static_cast<int>(std::btowc(\'A\')));', "65", "ASCII 文字をワイド文字に直す", ("マルチバイト文字に使う", "1 バイトで表せる文字だけが対象です。"), [("[`wctob`](wctob.md)", "逆の変換")])
W("wctob", "ワイド文字を、1 バイトの文字に変換する。", "`wchar_t` の 1 文字を、`char` に変換します。1 バイトで表せなければ `EOF` が返ります。", "int wctob(std::wint_t c);",
  [("c", "wint_t", "変換するワイド文字")], "変換した 1 バイト。できなければ `EOF`", 'std::println("{}", std::wctob(L\'A\'));', "65", "ワイド文字を ASCII に戻す", ("日本語の文字に使う", "1 バイトで表せない文字は、`EOF` になります。"), [("[`btowc`](btowc.md)", "逆の変換")])
W("mbrlen", "マルチバイト文字 1 文字のバイト数を返す（途中状態つき）。", "`mblen` の再入可能版です。変換の途中状態（`mbstate_t`）を引数で受け取るので、スレッドで安全です。", "std::size_t mbrlen(const char* s, std::size_t n, std::mbstate_t* ps);",
  [("s", "const char*", "調べるバイト列"), ("n", "size_t", "調べる最大のバイト数"), ("ps", "mbstate_t*", "変換の途中状態")], "1 文字のバイト数。不正なら `(size_t)-1`", 'std::mbstate_t st{};\nstd::println("{}", std::mbrlen("A", 1, &st));', "1", "可変長の文字列の文字数を数える", ("`mbstate_t` を初期化しない", "最初に `std::mbstate_t st{};` で 0 に初期化します。"), [("[`mblen`](../../numeric/cstdlib/mblen.md)", "途中状態なし")])
W("mbrtowc", "マルチバイト文字を、ワイド文字に変換する（途中状態つき）。", "`mbtowc` の再入可能版です。途中で区切られた文字も、続きから変換できます。", "std::size_t mbrtowc(wchar_t* pwc, const char* s, std::size_t n, std::mbstate_t* ps);",
  [("pwc", "wchar_t*", "変換結果の書き込み先"), ("s", "const char*", "変換元"), ("n", "size_t", "調べる最大のバイト数"), ("ps", "mbstate_t*", "変換の途中状態")], "使ったバイト数。不正なら `(size_t)-1`", 'std::mbstate_t st{};\nwchar_t w = 0;\nstd::size_t n = std::mbrtowc(&w, "A", 1, &st);\nstd::println("{} {}", n, static_cast<int>(w));', "1 65", "UTF-8 の文字列を 1 文字ずつワイド文字にする", ("ロケールを設定しない", "既定の `\"C\"` ロケールでは ASCII のみです。"), [("[`mbtowc`](../../numeric/cstdlib/mbtowc.md)", "途中状態なし")])
W("wcrtomb", "ワイド文字を、マルチバイト文字に変換する（途中状態つき）。", "`wctomb` の再入可能版です。", "std::size_t wcrtomb(char* s, wchar_t wc, std::mbstate_t* ps);",
  [("s", "char*", "変換結果の書き込み先（`MB_CUR_MAX` バイト以上）"), ("wc", "wchar_t", "変換するワイド文字"), ("ps", "mbstate_t*", "変換の途中状態")], "書き込んだバイト数。変換できなければ `(size_t)-1`", 'char buf[MB_LEN_MAX];\nstd::mbstate_t st{};\nstd::println("{}", std::wcrtomb(buf, L\'A\', &st));', "1", "ワイド文字を UTF-8 などに戻す", ("バッファが小さい", "`MB_CUR_MAX`（最大のバイト数）以上の大きさが必要です。"), [("[`wctomb`](../../numeric/cstdlib/wctomb.md)", "途中状態なし")], inc=("cwchar", "climits", "print"))
W("mbsrtowcs", "マルチバイト文字列を、ワイド文字列に変換する（途中状態つき）。", "`mbstowcs` の再入可能版です。変換した位置を、次の呼び出しに引き継げます。", "std::size_t mbsrtowcs(wchar_t* dst, const char** src, std::size_t len, std::mbstate_t* ps);",
  [("dst", "wchar_t*", "変換結果の書き込み先"), ("src", "const char**", "変換元（変換した位置まで進む）"), ("len", "size_t", "書き込む最大の文字数"), ("ps", "mbstate_t*", "変換の途中状態")], "変換した文字数。不正なら `(size_t)-1`", 'const char* s = "abc";\nwchar_t buf[8];\nstd::mbstate_t st{};\nstd::println("{}", std::mbsrtowcs(buf, &s, 8, &st));', "3", "UTF-8 をワイド文字列に変換する", ("元の文字列を失う", "`src` が変換した位置まで進みます。元のポインタを別に持っておきます。"), [("[`mbstowcs`](../../numeric/cstdlib/mbstowcs.md)", "途中状態なし")])
W("wcsrtombs", "ワイド文字列を、マルチバイト文字列に変換する（途中状態つき）。", "`wcstombs` の再入可能版です。", "std::size_t wcsrtombs(char* dst, const wchar_t** src, std::size_t len, std::mbstate_t* ps);",
  [("dst", "char*", "変換結果の書き込み先"), ("src", "const wchar_t**", "変換元（変換した位置まで進む）"), ("len", "size_t", "書き込む最大のバイト数"), ("ps", "mbstate_t*", "変換の途中状態")], "書き込んだバイト数。不正なら `(size_t)-1`", 'const wchar_t* s = L"abc";\nchar buf[8];\nstd::mbstate_t st{};\nstd::println("{}", std::wcsrtombs(buf, &s, 8, &st));', "3", "ワイド文字列を UTF-8 などに戻す", ("元の文字列を失う", "`src` が進みます。元のポインタを別に持っておきます。"), [("[`wcstombs`](../../numeric/cstdlib/wcstombs.md)", "途中状態なし")])
W("mbstate_t", "マルチバイト文字の変換の途中状態を入れる型。", "UTF-8 のように、1 文字が複数バイトの文字列を変換するとき、途中で区切られた文字の続きを覚えておく必要があります。その状態を入れる型が `mbstate_t` で、`mbrtowc` などの関数が受け取ります。", "using mbstate_t = /* 実装定義 */;",
  [], "なし（型）", 'std::mbstate_t st{};\nstd::println("{}", std::mbrlen("A", 1, &st));', "1", "文字コードの変換を、1 文字ずつ行う", ("初期化しない", "変換を始める前に、`std::mbstate_t st{};` で 0 に初期化します。"), [("[`mbrtowc`](mbrtowc.md)", "この型を使う関数")])
W("wint_t", "ワイド文字と WEOF を入れられる整数型。", "`wchar_t` の値に加えて、終端を表す `WEOF` を入れられる整数型です。`fgetwc` などの戻り値で、`wchar_t` ではなく `wint_t` を使うのは、この `WEOF` を区別するためです。", "using wint_t = /* 整数型 */;",
  [], "なし（型）", 'std::wint_t c = L\'A\';\nstd::println("{}", static_cast<int>(c));', "65", "ワイド文字の読み込みの戻り値を受ける", ("`wchar_t` で受ける", "`WEOF` と文字を区別できなくなります。"), [("[`WEOF`](weof.md)", "終端を表す定数")])
W("WEOF", "ワイド文字の終端またはエラーを表す定数。", "`fgetwc` などが、終端やエラーを知らせるときに返す値です。`wchar_t` の文字とは区別できる値です。", "#define WEOF /* wint_t の値（実装定義） */",
  [], "終端を表す `wint_t` の値", TMP + 'std::println("{}", std::fgetwc(f) == WEOF);\nstd::fclose(f);', "true", "`fgetwc` の結果の判定", ("`wchar_t` と比べる", "`wint_t` で受けて比べます。"), [("[`wint_t`](wint_t.md)", "ワイド文字を受ける型")], inc=("cwchar", "cstdio", "print"))

add_secs("io/basic_ios.md", fn("std::ios", "using ios = basic_ios<char>;", None, "`char` 用の `basic_ios` の別名", "なし", None,
         notes="`basic_ios<char>` の別名で、すべての `char` ストリームの土台です。`std::ios::sync_with_stdio` のような static な関数や、`std::ios::in` のようなフラグも、`ios_base` から受け継いでいるため、`std::ios::` で書けます。", ids="ios"))

if __name__ == "__main__":
    flush_hubs()
