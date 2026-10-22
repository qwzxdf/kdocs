"""バッチ 7: <cstring> / <cstdlib> / <cctype> / <cwctype> / <cuchar> / <cfenv> の未登録分。"""
from mk import *  # noqa: F401,F403

# ================= cstring =================
CS = "memory/cstring/"
CSI = "[`<cstring>`](../cstring.md) の概要と [ポインタ](@/basics/pointer.md) を先に読んでください。"
CSH = "memory/cstring.md"


def S(name, summary, intro, sig, args, ret, body, out, use, miss, sim, tips=None, rank="rare", cr=None, inc=None):
    Q(CS + name + ".md", "std::" + name, summary, rank, inc or ["cstring", "print"], intro,
      tips or ["終端の `'\\0'` を前提にする C 由来の関数。", "バッファの大きさは自分で確かめる。", "新しいコードでは `std::string` / `std::string_view` のほうが安全。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, ver=None, info=CSI, rj=f"cstring/{name}.html", cr=f"string/byte/{cr or name}", hub=CSH, hubname="<cstring>")


S("strncat", "文字列の末尾に、最大 n 文字を連結する。", "`strcat` は連結する長さを指定できず、バッファをあふれさせる事故のもとです。`strncat` は連結する最大の文字数を指定でき、必ず終端の `'\\0'` を付けてくれます。ただし n は「連結する文字数」で、バッファ全体の大きさではありません。",
  "char* strncat(char* dest, const char* src, std::size_t count);", [("dest", "char*", "連結先（`\\0` で終わっていること）"), ("src", "const char*", "連結する文字列"), ("count", "size_t", "連結する最大の文字数")], "`dest`",
  'char buf[16] = "abc";\nstd::strncat(buf, "defgh", 2);\nstd::println("{}", buf);', "abcde", "固定長バッファへの安全な連結", ("count をバッファ全体の大きさにする", "`count` は連結する文字数です。`dest` の残りの大きさ（終端ぶんも含めて）以下にします。"),
  [("[`strcat`](strcat.md)", "長さの指定なし"), ("[`strncpy`](strncpy.md)", "コピーする")])
S("strrchr", "文字列の中から、指定した文字が最後に現れる位置を探す。", "ファイルパスから拡張子や最後のフォルダ区切りを探すとき、先頭から探す `strchr` では最初の位置しか分かりません。`strrchr` は**最後に現れる**位置を返します。",
  "const char* strrchr(const char* str, int ch);", [("str", "const char*", "探す文字列"), ("ch", "int", "探す文字（`'\\0'` も探せる）")], "見つかった位置のポインタ。なければ `nullptr`",
  'const char* path = "a/b/c.txt";\nconst char* name = std::strrchr(path, \'/\') + 1;\nstd::println("{}", name);', "c.txt", "パスからファイル名を取り出す", ("見つからないのに +1 する", "戻り値が `nullptr` のときに `+ 1` すると、不正なポインタになります。必ず `nullptr` を確かめます。"),
  [("[`strchr`](strchr.md)", "最初に現れる位置"), ("[`std::filesystem::path`](../../io/filesystem/path.md)", "パスの扱いはこちら")])
S("strspn", "先頭から、指定した文字だけが続く長さを返す。", "文字列の先頭が、「数字だけ」「英字だけ」など決まった文字の集まりで何文字続くか知りたいことがあります。`strspn` は、先頭から連続して `accept` の文字に含まれる長さを返します。",
  "std::size_t strspn(const char* str, const char* accept);", [("str", "const char*", "調べる文字列"), ("accept", "const char*", "許す文字の集まり")], "先頭から続く長さ",
  'std::println("{}", std::strspn("abc123", "abc"));', "3", "入力の先頭の英字の長さを調べる", ("文字列全体を調べた気になる", "最初に合わない文字が来た時点で止まります。途中の文字は見ません。"),
  [("[`strcspn`](strcspn.md)", "逆に、含まない文字が続く長さ")])
S("strcspn", "先頭から、指定した文字を含まない部分の長さを返す。", "「最初に区切り文字が現れるまで何文字か」を知りたいとき、`strcspn` を使います。`strspn` の逆で、`reject` の文字が最初に現れる位置までの長さを返します。",
  "std::size_t strcspn(const char* str, const char* reject);", [("str", "const char*", "調べる文字列"), ("reject", "const char*", "現れたら止まる文字の集まり")], "先頭から続く長さ",
  'std::println("{}", std::strcspn("abc123", "0123456789"));', "3", "最初の数字までの文字数を調べる", ("見つからないときの戻り値", "見つからなければ、文字列全体の長さ（終端の位置）が返ります。"),
  [("[`strspn`](strspn.md)", "含む文字が続く長さ"), ("[`strpbrk`](strpbrk.md)", "位置のポインタを返す")])
S("strpbrk", "文字列の中から、指定した文字のどれかが最初に現れる位置を探す。", "区切り文字が複数ある文字列（空白かカンマ）で、最初にどれかが現れる場所を見つけたいとき、`strpbrk` を使います。",
  "const char* strpbrk(const char* str, const char* breakset);", [("str", "const char*", "探す文字列"), ("breakset", "const char*", "探す文字の集まり")], "見つかった位置のポインタ。なければ `nullptr`",
  'const char* s = "hello world";\nstd::println("{}", std::strpbrk(s, " ,") - s);', "5", "最初の区切り文字の位置", ("見つからない場合を無視する", "`nullptr` が返るので、引き算や参照の前に確かめます。"),
  [("[`strcspn`](strcspn.md)", "長さで返す"), ("[`strchr`](strchr.md)", "1 文字だけ探す")])
S("strtok", "文字列を、区切り文字で分割して 1 つずつ取り出す。", "「a,b,c」のような文字列を分割して順番に取り出したいとき、`strtok` が使えます。ただし元の文字列を**書き換え**（区切りを `'\\0'` にする）、内部の状態を使うので、同時に複数の分割はできません。",
  "char* strtok(char* str, const char* delim);", [("str", "char*", "最初の呼び出しでは分割する文字列。続きでは `nullptr`"), ("delim", "const char*", "区切り文字の集まり")], "次のトークンのポインタ。なければ `nullptr`",
  'char s[] = "a,b,c";\nfor (char* t = std::strtok(s, ","); t != nullptr; t = std::strtok(nullptr, ",")) {\n  std::println("{}", t);\n}', "a\nb\nc", "古い C のコードの文字列の分割", ("文字列リテラルに使う", "リテラルは書き換えられません。`char s[] = ...` のコピーに使います。内部状態があるので、スレッドや入れ子では使えません。"),
  [("[`std::ranges::views::split`](../../algorithms/views/split.md)", "新しい書き方"), ("[`std::getline`](../../io/getline.md)", "区切り文字で読む")],
  tips=["元の文字列を書き換える。", "2 回目以降は第 1 引数に `nullptr` を渡す。", "新しいコードでは `views::split` のほうが安全。"])
S("strcoll", "ロケールの規則で、2 つの文字列を比べる。", "`strcmp` は文字コードの順で比べます。辞書の順番（五十音、アルファベットの大文字小文字の扱い）は、言語によって違います。`strcoll` は、現在のロケールの規則で比べます。",
  "int strcoll(const char* lhs, const char* rhs);", [("lhs, rhs", "const char*", "比べる 2 つの文字列")], "`lhs < rhs` なら負、等しければ 0、大きければ正",
  'std::println("{}", std::strcoll("a", "b") < 0);', "true", "言語ごとの順序で名前を並べる", ("ロケールを設定せずに使う", "既定の `\"C\"` ロケールでは `strcmp` と同じ結果です。`std::setlocale` で設定します。"),
  [("[`strcmp`](strcmp.md)", "文字コード順の比較"), ("[`strxfrm`](strxfrm.md)", "比較用に変換する")])
S("strxfrm", "ロケールの規則での比較用に、文字列を変換する。", "`strcoll` を何度も呼ぶより、先に比較用の文字列に変換して、あとは `strcmp` で比べるほうが速いことがあります。`strxfrm` は、その変換をします。",
  "std::size_t strxfrm(char* dest, const char* src, std::size_t count);", [("dest", "char*", "変換結果の書き込み先（`nullptr` も可）"), ("src", "const char*", "変換する文字列"), ("count", "size_t", "書き込む最大の長さ")], "変換後の文字列の長さ（終端を除く）",
  'std::println("{}", std::strxfrm(nullptr, "abc", 0));', "3", "大量の文字列を何度も比べる前の準備", ("バッファの大きさを決めずに呼ぶ", "まず `dest = nullptr, count = 0` で必要な長さを調べてから確保します。"),
  [("[`strcoll`](strcoll.md)", "直接比べる")])
S("strerror", "エラー番号（errno）を、説明の文字列にする。", "`errno` の数値だけでは原因が分かりません。`strerror(errno)` で、「No such file or directory」のような説明が得られます。文字列は処理系が決め、静的な領域にあるので、スレッドで使うときは `strerror_s` などを使います。",
  "char* strerror(int errnum);", [("errnum", "int", "エラー番号（`errno` の値）")], "説明の文字列（静的な領域。書き換え禁止）",
  'std::println("{}", std::strerror(ENOENT) != nullptr);', "true", "ファイルを開けなかった理由をログに出す", ("戻り値を保存して使い回す", "次の呼び出しで上書きされることがあります。すぐコピーします。"),
  [("[`errno`](../../io/cerrno.md)", "エラー番号"), ("[`std::error_code`](../../support/error_code.md)", "C++ のエラー表現")], inc=["cerrno", "cstring", "print"])

# ================= cstdlib =================
CL = "numeric/cstdlib/"
CLI = "[`<cstdlib>`](../cstdlib.md) の概要を先に読むと分かりやすいです。" if False else "[`std::atoi`](atoi.md) を先に読んでください。"


def L(name, summary, intro, sig, args, ret, body, out, use, miss, sim, tips=None, rank="rare", cr=None, inc=None, pre="", ver=None):
    Q(CL + name.lower() + ".md", name if name.isupper() else "std::" + name, summary, rank, inc or ["cstdlib", "print"], intro,
      tips or ["C 由来の関数。", "失敗の知らせ方は関数ごとに違う。", "新しいコードでは `std::from_chars` や `std::string` が安全。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, ver=ver, info=CLI, rj=f"cstdlib/{name}.html", cr=f"utility/program/{cr or name}" if False else f"c/{cr or name}", pre=pre)


L("labs", "long の絶対値を返す。", "`abs` は引数の型に合わせた版を選びます。`long` の絶対値を明示的に求めたいとき、`labs` が使えます。", "long labs(long n);", [("n", "long", "絶対値を求める値")], "`|n|`",
  'std::println("{}", std::labs(-5L));', "5", "長整数の差の大きさ", ("最小値の絶対値", "`LONG_MIN` の絶対値は表せず、未定義動作です。"), [("[`abs`](../cmath/abs.md)", "型を選ぶ版")])
L("llabs", "long long の絶対値を返す。", "64 ビット整数（`long long`）の絶対値を求める関数です。", "long long llabs(long long n);", [("n", "long long", "絶対値を求める値")], "`|n|`",
  'std::println("{}", std::llabs(-5LL));', "5", "64 ビット整数の差の大きさ", ("最小値の絶対値", "`LLONG_MIN` の絶対値は表せず、未定義動作です。"), [("[`abs`](../cmath/abs.md)", "型を選ぶ版")])
L("ldiv", "long の割り算で、商と余りをいっしょに返す。", "`/` と `%` を別々に書くと、割り算が 2 回行われることがあります。`ldiv` は 1 回で商と余りを構造体で返します。", "ldiv_t ldiv(long x, long y);", [("x, y", "long", "割られる数・割る数")], "`quot`（商）と `rem`（余り）をもつ構造体",
  'auto r = std::ldiv(7L, 2L);\nstd::println("{} {}", r.quot, r.rem);', "3 1", "商と余りを同時に使う", ("0 で割る", "y が 0 だと未定義動作です。"), [("[`div`](div.md)", "int の版")])
L("lldiv", "long long の割り算で、商と余りをいっしょに返す。", "`ldiv` の `long long` 版です。", "lldiv_t lldiv(long long x, long long y);", [("x, y", "long long", "割られる数・割る数")], "`quot`（商）と `rem`（余り）をもつ構造体",
  'auto r = std::lldiv(7LL, 2LL);\nstd::println("{} {}", r.quot, r.rem);', "3 1", "64 ビット整数の商と余り", ("0 で割る", "y が 0 だと未定義動作です。"), [("[`div`](div.md)", "int の版")])
L("srand", "rand() の乱数の並びを、シードで初期化する。", "`rand()` は、`srand` に与えたシードから決まる並びを返します。同じシードなら同じ並びなので、再現したいときに便利ですが、本格的な乱数には `<random>` を使います。",
  "void srand(unsigned seed);", [("seed", "unsigned", "初期値")], "なし", 'std::srand(42);\nint a = std::rand();\nstd::srand(42);\nint b = std::rand();\nstd::println("{}", a == b);', "true",
  "テストで同じ乱数を再現する", ("`time(nullptr)` を何度も呼ぶ", "1 秒に何度も `srand(time(nullptr))` すると同じ値が続きます。起動時に 1 回だけ呼びます。"), [("[`rand`](rand.md)", "乱数を取る"), ("[`std::mt19937`](../../utilities/random/mt19937.md)", "高品質な乱数")])
L("atol", "文字列を long に変換する。", "`atoi` の `long` 版です。失敗しても例外を出さず 0 を返すので、失敗が区別できません。", "long atol(const char* str);", [("str", "const char*", "変換する文字列")], "変換した値（失敗したら 0）",
  'std::println("{}", std::atol("123456"));', "123456", "古い C のコードの数値の読み取り", ("失敗を 0 と区別できない", "`\"abc\"` も `\"0\"` も 0 になります。エラーを知りたいなら `strtol` や `std::from_chars`。"), [("[`atoi`](atoi.md)", "int の版"), ("[`strtol`](strtol.md)", "エラーが分かる版")])
L("atoll", "文字列を long long に変換する。", "`atoi` の `long long` 版です。失敗しても 0 を返します。", "long long atoll(const char* str);", [("str", "const char*", "変換する文字列")], "変換した値（失敗したら 0）",
  'std::println("{}", std::atoll("9000000000"));', "9000000000", "大きな ID の読み取り", ("失敗を 0 と区別できない", "エラーを知りたいなら `strtoll` や `std::from_chars`。"), [("[`atoi`](atoi.md)", "int の版"), ("[`strtoll`](strtoll.md)", "エラーが分かる版")])
L("atof", "文字列を double に変換する。", "`atoi` の小数版です。失敗しても 0.0 を返します。", "double atof(const char* str);", [("str", "const char*", "変換する文字列")], "変換した値（失敗したら 0.0）",
  'std::println("{}", std::atof("3.5"));', "3.5", "設定ファイルの小数の読み取り", ("失敗を 0 と区別できない", "エラーを知りたいなら `strtod` や `std::from_chars`。"), [("[`atoi`](atoi.md)", "整数の版"), ("[`strtod`](strtod.md)", "エラーが分かる版")])
for nm, rt, base, call, res, what in [
    ("strtoll", "long long", True, 'std::strtoll("ff", nullptr, 16)', "255", "long long"),
    ("strtoul", "unsigned long", True, 'std::strtoul("42", nullptr, 10)', "42", "unsigned long"),
    ("strtoull", "unsigned long long", True, 'std::strtoull("18446744073709551615", nullptr, 10)', "18446744073709551615", "unsigned long long")]:
    L(nm, f"文字列を {what} に変換する（進数を指定でき、読み終えた位置が分かる）。", f"`atoi` 系は失敗を知らせてくれません。`{nm}` は、進数（2〜36）を指定でき、読み終えた位置を返し、範囲外なら `errno` に `ERANGE` を設定します。16 進数の文字列を読むときなどにも使います。",
      f"{rt} {nm}(const char* str, char** str_end, int base);", [("str", "const char*", "変換する文字列"), ("str_end", "char**", "読み終えた位置を受け取る（不要なら `nullptr`）"), ("base", "int", "進数（2〜36、0 なら接頭辞で判断）")], f"変換した値",
      f'std::println("{{}}", {call});', res, "16 進数の文字列を数値にする", ("`str_end` を確かめない", "数字が 1 文字もないとき、`str_end` は `str` のままです。先頭から消費できたか確かめます。"), [("[`atoi`](atoi.md)", "簡易版"), ("[`std::from_chars`](../../io/from_chars.md)", "例外も errno も使わない")])
L("strtof", "文字列を float に変換する（読み終えた位置が分かる）。", "`atof` と違い、読み終えた位置を返し、範囲外のときは `errno` に `ERANGE` を設定します。", "float strtof(const char* str, char** str_end);", [("str", "const char*", "変換する文字列"), ("str_end", "char**", "読み終えた位置を受け取る（不要なら `nullptr`）")], "変換した `float`",
  'std::println("{}", std::strtof("1.5", nullptr));', "1.5", "設定ファイルの数値の読み取り", ("読み終えた位置を確かめない", "不正な文字列では 0 が返り、位置が進みません。"), [("[`atof`](atof.md)", "簡易版"), ("[`strtod`](strtod.md)", "double 版")])
L("strtod", "文字列を double に変換する（読み終えた位置が分かる）。", "`atof` と違い、読み終えた位置を返し、範囲外のときは `errno` に `ERANGE` を設定します。`\"inf\"` や `\"nan\"` も読めます。", "double strtod(const char* str, char** str_end);", [("str", "const char*", "変換する文字列"), ("str_end", "char**", "読み終えた位置を受け取る（不要なら `nullptr`）")], "変換した `double`",
  'char* end = nullptr;\ndouble v = std::strtod("2.25abc", &end);\nstd::println("{} {}", v, end);', "2.25 abc", "数値の後ろの単位を取り出す", ("`end` が先頭のまま", "読めなかったとき、`end` は元の位置のままです。`end == str` で検出します。"), [("[`atof`](atof.md)", "簡易版"), ("[`std::from_chars`](../../io/from_chars.md)", "新しい書き方")])
L("strtold", "文字列を long double に変換する（読み終えた位置が分かる）。", "`strtod` の `long double` 版です。", "long double strtold(const char* str, char** str_end);", [("str", "const char*", "変換する文字列"), ("str_end", "char**", "読み終えた位置を受け取る（不要なら `nullptr`）")], "変換した `long double`",
  'std::println("{}", std::strtold("0.5", nullptr));', "0.5", "高い精度の数値の読み取り", ("範囲外を確かめない", "範囲外のとき `errno` が `ERANGE` になります。"), [("[`strtod`](strtod.md)", "double 版")])
L("atexit", "プログラム終了時に呼ぶ関数を登録する。", "後始末（ログのクローズなど）を、どこから終了しても確実に行いたいときに、`atexit` で関数を登録します。登録した順の**逆**に呼ばれます。", "int atexit(void (*func)());", [("func", "関数ポインタ", "終了時に呼ぶ関数")], "成功なら 0",
  'std::atexit([] { std::println("bye"); });\nstd::println("main");', "main\nbye", "終了時の後始末", ("後始末を静的デストラクタとの順序に頼る", "静的オブジェクトの破棄との順序は、登録の前後で決まります。重要な後始末は明示的に呼びます。"), [("[`exit`](exit.md)", "終了する"), ("[`quick_exit`](quick_exit.md)", "後始末を最小限に")], ver=None)
L("quick_exit", "後始末を最小限にして、プログラムを終了する。", "`exit` は、静的オブジェクトの破棄や `atexit` の関数をすべて実行するので、時間がかかり、デッドロックの危険もあります。`quick_exit` は、`at_quick_exit` で登録した関数だけを呼んで終了します。", "[[noreturn]] void quick_exit(int exit_code);", [("exit_code", "int", "終了コード")], "戻らない",
  '// 例: std::at_quick_exit(Cleanup);  std::quick_exit(0);', None, "異常時にすばやく終了する", ("通常の後始末を期待する", "デストラクタは実行されません。ファイルバッファなども書き出されない場合があります。"), [("[`exit`](exit.md)", "通常の終了"), ("[`abort`](abort.md)", "異常終了")], ver=("11", "C++11"))
L("at_quick_exit", "quick_exit() で終了するときに呼ぶ関数を登録する。", "`quick_exit` が呼ぶ後始末の関数を登録します。`atexit` の `quick_exit` 版です。", "int at_quick_exit(void (*func)());", [("func", "関数ポインタ", "終了時に呼ぶ関数")], "成功なら 0",
  '// 例: std::at_quick_exit(Cleanup);  std::quick_exit(0);', None, "すばやい終了時の後始末", ("`atexit` のつもりで登録する", "`atexit` の関数は `quick_exit` では呼ばれません。別に登録します。"), [("[`quick_exit`](quick_exit.md)", "終了する"), ("[`atexit`](atexit.md)", "通常の終了時")], ver=("11", "C++11"))
L("system", "OS のコマンドを実行する。", "外部のコマンド（`dir` や `ls` など）を実行して、終了コードを受け取ります。ゲームの本編では使いませんが、開発用ツールで使うことがあります。引数の文字列がそのままシェルに渡るので、外部から入力された値を使うと危険です。", "int system(const char* command);", [("command", "const char*", "実行するコマンド（`nullptr` でシェルの有無を確認）")], "コマンドの終了コード（処理系による）",
  '// 例: int code = std::system("echo hello");', None, "開発ツールからコマンドを呼ぶ", ("入力された文字列をそのまま渡す", "シェルのコマンドとして解釈されるため、コマンド注入の危険があります。ユーザー入力を直接渡さないでください。"), [("[`std::filesystem`](../../io/filesystem.md)", "ファイル操作は専用の API で")])
L("EXIT_SUCCESS", "成功を表す終了コードのマクロ。", "`main` の戻り値や `exit` の引数に、成功と失敗を表す名前付きの定数を使うと、読みやすくなります。`EXIT_SUCCESS` は成功（通常 0）です。", "#define EXIT_SUCCESS 0  // 値は実装定義", [], "成功を表す整数",
  'std::println("{}", EXIT_SUCCESS);', "0", "main の戻り値", ("0 と書く", "意味は同じですが、名前のほうが意図が伝わります。"), [("[`EXIT_FAILURE`](exit_failure.md)", "失敗を表す")])
L("EXIT_FAILURE", "失敗を表す終了コードのマクロ。", "`EXIT_FAILURE` は失敗を表す終了コードです（通常 1）。`main` の戻り値や `exit` の引数に使います。", "#define EXIT_FAILURE 1  // 値は実装定義", [], "失敗を表す整数",
  'std::println("{}", EXIT_FAILURE);', "1", "エラーで終了するとき", ("-1 を返す", "環境によって扱いが違います。`EXIT_FAILURE` を使います。"), [("[`EXIT_SUCCESS`](exit_success.md)", "成功を表す")])
L("RAND_MAX", "rand() が返す最大値のマクロ。", "`rand()` が返す値は 0 〜 `RAND_MAX` です。この値は処理系によって違います（GCC では約 21 億、Windows の MSVC では 32767）。範囲を狭めるときの割り算で使います。", "#define RAND_MAX /* 実装定義 */", [], "`rand()` の最大値",
  'std::println("{}", RAND_MAX >= 32767);', "true", "rand() の値を 0.0〜1.0 にする", ("`RAND_MAX` を 32767 だと決めつける", "環境で違います。必ずマクロを使います。"), [("[`rand`](rand.md)", "乱数を取る")])
for nm, sig, args, ret, body, out, summ, intro in [
    ("mblen", "int mblen(const char* s, std::size_t n);", [("s", "const char*", "調べるバイト列"), ("n", "size_t", "調べる最大のバイト数")], "1 文字のバイト数。終端文字なら 0。不正なら -1", 'std::println("{}", std::mblen("A", 1));', "1", "マルチバイト文字の 1 文字目のバイト数を返す。", "UTF-8 や Shift_JIS のような可変長の文字列で、「先頭の 1 文字が何バイトか」を知りたいことがあります。`mblen` はそれを返します。ロケールによって結果が変わります。"),
    ("mbtowc", "int mbtowc(wchar_t* pwc, const char* s, std::size_t n);", [("pwc", "wchar_t*", "変換結果の書き込み先"), ("s", "const char*", "変換元のバイト列"), ("n", "size_t", "調べる最大のバイト数")], "使ったバイト数。不正なら -1", 'wchar_t w = 0;\nint n = std::mbtowc(&w, "A", 1);\nstd::println("{} {}", n, static_cast<int>(w));', "1 65", "マルチバイト文字 1 文字を wchar_t に変換する。", "ロケールのマルチバイト文字を、ワイド文字（`wchar_t`）1 文字に変換します。内部の状態を使うので、スレッドセーフではありません。"),
    ("wctomb", "int wctomb(char* s, wchar_t wc);", [("s", "char*", "変換結果の書き込み先（`MB_CUR_MAX` バイト以上）"), ("wc", "wchar_t", "変換するワイド文字")], "書き込んだバイト数。変換できなければ -1", 'char buf[MB_LEN_MAX];\nint n = std::wctomb(buf, L\'A\');\nstd::println("{}", n);', "1", "wchar_t 1 文字をマルチバイト文字に変換する。", "ワイド文字（`wchar_t`）1 文字を、ロケールのマルチバイト文字に変換します。バッファは `MB_CUR_MAX` バイト以上必要です。"),
    ("mbstowcs", "std::size_t mbstowcs(wchar_t* dst, const char* src, std::size_t len);", [("dst", "wchar_t*", "変換結果の書き込み先（`nullptr` で長さだけ調べる）"), ("src", "const char*", "変換元の文字列"), ("len", "size_t", "書き込む最大の `wchar_t` の数")], "変換した `wchar_t` の数。不正なら `(size_t)-1`", 'wchar_t buf[8];\nstd::size_t n = std::mbstowcs(buf, "abc", 8);\nstd::println("{}", n);', "3", "マルチバイト文字列を wchar_t の文字列に変換する。", "ロケールのマルチバイト文字列を、`wchar_t` の文字列にまとめて変換します。Windows の API に渡す文字列を作るときに使います。"),
    ("wcstombs", "std::size_t wcstombs(char* dst, const wchar_t* src, std::size_t len);", [("dst", "char*", "変換結果の書き込み先（`nullptr` で長さだけ調べる）"), ("src", "const wchar_t*", "変換元の文字列"), ("len", "size_t", "書き込む最大のバイト数")], "書き込んだバイト数。不正なら `(size_t)-1`", 'char buf[8];\nstd::size_t n = std::wcstombs(buf, L"abc", 8);\nstd::println("{}", n);', "3", "wchar_t の文字列をマルチバイト文字列に変換する。", "`wchar_t` の文字列を、ロケールのマルチバイト文字列にまとめて変換します。")]:
    L(nm, summ, intro, sig, args, ret, body, out, "文字コードの変換（ただし新しいコードは UTF-8 に統一する）", ("ロケールを設定せずに使う", "既定は `\"C\"` ロケールで、ASCII しか変換できません。`std::setlocale` で設定します。"),
      [("[文字コード](@/encoding/index.md)", "変換の考え方")], inc=["cstdlib", "climits", "print"] if nm == "wctomb" else ["cstdlib", "print"])

# ================= cctype =================
CC = "numeric/cctype/"
CCI = "[`std::isalpha`](isalpha.md) を先に読んでください。"
for nm, what, ex_t, ex_f, intro in [
    ("isalnum", "英字か数字かを調べる。", "'a'", "'!'", "識別子や入力の検査で、「英数字か」を判定します。`isalpha` と `isdigit` の両方を調べるのと同じです。"),
    ("islower", "英小文字かを調べる。", "'a'", "'A'", "文字が英字の小文字（a〜z）かを判定します。"),
    ("isupper", "英大文字かを調べる。", "'A'", "'a'", "文字が英字の大文字（A〜Z）かを判定します。"),
    ("isxdigit", "16 進数の数字（0〜9, a〜f, A〜F）かを調べる。", "'f'", "'g'", "16 進数の文字列を読むときに、1 文字ずつ有効な桁かを調べます。"),
    ("iscntrl", "制御文字かを調べる。", "'\\n'", "'a'", "改行やタブのような、画面に表示されない制御文字かを判定します。"),
    ("isgraph", "空白以外の表示できる文字かを調べる。", "'a'", "' '", "画面に表示できて、空白ではない文字かを判定します。"),
    ("isblank", "空白かタブかを調べる。", "' '", "'\\n'", "行の中の区切りになる空白（スペースとタブ）かを判定します。改行は含みません。"),
    ("isprint", "表示できる文字（空白を含む）かを調べる。", "' '", "'\\n'", "空白を含めて、画面に表示できる文字かを判定します。"),
    ("ispunct", "句読点・記号かを調べる。", "'!'", "'a'", "英数字でも空白でもない、記号の文字かを判定します。")]:
    Q(CC + nm + ".md", "std::" + nm, what, "rare", ["cctype", "print"], f"`<cctype>` の判定関数のひとつです。{intro}戻り値は真偽ではなく `int` で、真なら 0 以外が返ります。",
      ["戻り値は `int`（真なら 0 以外）。", "引数は `unsigned char` の範囲か `EOF`。`char` が負のときは `unsigned char` に直して渡す。", "ASCII 以外の文字（日本語）には使えない。"],
      f"int {nm}(int ch);", [("ch", "int", "調べる文字（`unsigned char` の値か `EOF`）")], "条件に合えば 0 以外、合わなければ 0",
      f'std::println("{{}} {{}}", std::{nm}({ex_t}) != 0, std::{nm}({ex_f}) != 0);', "true false", use="入力文字の検査", miss=("負の `char` をそのまま渡す", "`char` が符号付きの環境で、非 ASCII の文字は負の値になります。`static_cast<unsigned char>(c)` に直して渡さないと、未定義動作です。"),
      sim=[("[`isalpha`](isalpha.md)", "英字か"), ("[`isdigit`](isdigit.md)", "数字か")], cx="定数", info=CCI, rj=f"cctype/{nm}.html", cr=f"string/byte/{nm}")

# ================= cwctype =================
CW = "numeric/cwctype/"
CWI = "[`std::isalpha`](../cctype/isalpha.md) を先に読んでください。"
for nm, what, ex in [
    ("iswalnum", "ワイド文字が英数字かを調べる。", "L'a'"), ("iswalpha", "ワイド文字が英字かを調べる。", "L'a'"), ("iswlower", "ワイド文字が小文字かを調べる。", "L'a'"),
    ("iswupper", "ワイド文字が大文字かを調べる。", "L'A'"), ("iswdigit", "ワイド文字が数字かを調べる。", "L'5'"), ("iswxdigit", "ワイド文字が 16 進数の数字かを調べる。", "L'f'"),
    ("iswcntrl", "ワイド文字が制御文字かを調べる。", "L'\\n'"), ("iswgraph", "ワイド文字が空白以外の表示できる文字かを調べる。", "L'a'"), ("iswspace", "ワイド文字が空白類かを調べる。", "L' '"),
    ("iswblank", "ワイド文字が空白かタブかを調べる。", "L' '"), ("iswprint", "ワイド文字が表示できる文字かを調べる。", "L'a'"), ("iswpunct", "ワイド文字が記号かを調べる。", "L'!'")]:
    Q(CW + nm + ".md", "std::" + nm, what, "rare", ["cwctype", "print"], f"`<cctype>` の `{nm[:2] + nm[3:]}` の、`wchar_t`（ワイド文字）版です。Windows の API の `wchar_t` 文字列を扱うときに使います。ロケールによって、ASCII 以外の文字の扱いが変わります。",
      ["`wint_t` を受け取り、真なら 0 以外を返す。", "ロケールの設定で、日本語などの判定が変わる。", "`char` 版は `<cctype>`。"],
      f"int {nm}(std::wint_t wc);", [("wc", "wint_t", "調べるワイド文字")], "条件に合えば 0 以外、合わなければ 0",
      f'std::println("{{}}", std::{nm}({ex}) != 0);', "true", use="wchar_t 文字列の検査", miss=("ロケールを設定せずに日本語を渡す", "既定の `\"C\"` ロケールでは ASCII 以外の判定が使えません。`std::setlocale` を呼びます。"),
      sim=[(f"[`{nm[:2] + nm[3:]}`](../cctype/isalpha.md)", "char 版")], cx="定数", info=CWI, rj=f"cwctype/{nm}.html", cr=f"string/wide/{nm}",
      group="<cwctype> のワイド文字の判定・変換")
for nm, what, ex, out in [("towlower", "ワイド文字を小文字にする。", "std::towlower(L'A')", "a"), ("towupper", "ワイド文字を大文字にする。", "std::towupper(L'a')", "A")]:
    Q(CW + nm + ".md", "std::" + nm, what, "rare", ["cwctype", "print"], f"`<cctype>` の `{nm[:2] + nm[3:]}` の、`wchar_t`（ワイド文字）版です。",
      ["`wint_t` を受け取って `wint_t` を返す。", "ロケールで対象の文字が変わる。", "`char` 版は `<cctype>`。"], f"std::wint_t {nm}(std::wint_t wc);", [("wc", "wint_t", "変換するワイド文字")], "変換した文字（変換できなければそのまま）",
      f'std::println("{{}}", static_cast<char>({ex}));', out, use="wchar_t の文字列の大文字小文字をそろえる", miss=("文字の数が変わる言語を考えない", "ドイツ語の `ß` のように 1 文字が 2 文字になる変換はできません。"),
      sim=[(f"[`{nm[:2] + nm[3:]}`](../cctype/tolower.md)", "char 版")], cx="定数", info=CWI, rj=f"cwctype/{nm}.html", cr=f"string/wide/{nm}", group="<cwctype> のワイド文字の判定・変換")

# ================= cuchar =================
CU = "numeric/cuchar/"
CUI = "[文字コード](@/encoding/index.md) の考え方と、[ロケール](@/stl/io/locale.md) を先に読んでください。"
for nm, ch, kind, ver, intro in [
    ("mbrtoc8", "char8_t", "mb → c8", ("20", "C++20"), "ロケールのマルチバイト文字列 1 文字を UTF-8 のコード単位（`char8_t`）に変換します。"),
    ("c8rtomb", "char8_t", "c8 → mb", ("20", "C++20"), "UTF-8 のコード単位（`char8_t`）を、ロケールのマルチバイト文字列に変換します。"),
    ("mbrtoc16", "char16_t", "mb → c16", ("11", "C++11"), "ロケールのマルチバイト文字列 1 文字を UTF-16 のコード単位（`char16_t`）に変換します。サロゲートペアのときは 2 回に分けて返します。"),
    ("c16rtomb", "char16_t", "c16 → mb", ("11", "C++11"), "UTF-16 のコード単位（`char16_t`）を、ロケールのマルチバイト文字列に変換します。"),
    ("mbrtoc32", "char32_t", "mb → c32", ("11", "C++11"), "ロケールのマルチバイト文字列 1 文字を UTF-32（コードポイント、`char32_t`）に変換します。"),
    ("c32rtomb", "char32_t", "c32 → mb", ("11", "C++11"), "UTF-32（コードポイント、`char32_t`）を、ロケールのマルチバイト文字列に変換します。")]:
    to = kind.startswith("mb")
    sig = (f"std::size_t {nm}({ch}* pc, const char* s, std::size_t n, std::mbstate_t* ps);" if to else f"std::size_t {nm}(char* s, {ch} c, std::mbstate_t* ps);")
    args = ([("pc", f"{ch}*", "変換結果の書き込み先"), ("s", "const char*", "変換元のバイト列"), ("n", "size_t", "調べる最大のバイト数"), ("ps", "mbstate_t*", "変換の途中状態")] if to else
            [("s", "char*", "変換結果の書き込み先（`MB_LEN_MAX` バイト以上）"), ("c", ch, "変換する文字"), ("ps", "mbstate_t*", "変換の途中状態")])
    Q(CU + nm + ".md", "std::" + nm, f"{kind}：" + intro.split("。")[0] + "。", "rare", ["cuchar"], intro + "状態（`mbstate_t`）を引数で受け取るので、1 つの文字が複数回に分かれる場合も扱えます。",
      ["途中状態 `mbstate_t` を呼び出しの間で保つ。", "ロケールの設定で動作が変わる。", "新しいコードでは UTF-8 に統一し、変換は最小限にする。"],
      sig, args, "書き込んだ・読んだバイト数など（エラー時は `(size_t)-1`）",
      "// 例（ロケールを UTF-8 に設定して使う）\n// std::setlocale(LC_ALL, \"C.UTF-8\");\n// std::mbstate_t st{};", None,
      use="古い API とのやり取りで文字コードを変換する", miss=("`mbstate_t` を初期化しない", "最初の呼び出しの前に、`std::mbstate_t st{};` で 0 に初期化します。"), sim=[("[文字コード](@/encoding/index.md)", "変換の考え方")], cx="定数", ver=ver, info=CUI, rj=f"cuchar/{nm}.html", cr=f"string/multibyte/{nm}")

# ================= cfenv =================
FE = "numeric/"
FEI = "[`std::fesetround`](fesetround.md) を先に読んでください。"
for nm, summ, intro, sig, args, ret, body, out, use, miss in [
    ("feclearexcept", "浮動小数点例外のフラグをクリアする。", "ゼロ除算やオーバーフローが起きると、CPU の浮動小数点例外フラグが立ちます。計算の前にいったんクリアしておくと、その計算で起きた例外だけを調べられます。", "int feclearexcept(int excepts);", [("excepts", "int", "クリアする例外のビットのマスク（`FE_ALL_EXCEPT` など）")], "成功なら 0",
     'std::feraiseexcept(FE_DIVBYZERO);\nstd::feclearexcept(FE_ALL_EXCEPT);\nstd::println("{}", std::fetestexcept(FE_DIVBYZERO) != 0);', "false", "計算の前にフラグを初期化する", ("クリアし忘れる", "前の計算のフラグが残ったまま調べると、別の計算の例外を拾ってしまいます。")),
    ("fetestexcept", "浮動小数点例外のフラグを調べる。", "計算のあとで、ゼロ除算やオーバーフローなど、どんな例外が起きたかを調べます。例外を投げるのではなく、フラグが立つだけなので、自分で確認します。", "int fetestexcept(int excepts);", [("excepts", "int", "調べる例外のビットのマスク")], "立っていたビットの組み合わせ（`0` なら立っていない）",
     'std::feclearexcept(FE_ALL_EXCEPT);\nstd::feraiseexcept(FE_DIVBYZERO);\nstd::println("{}", std::fetestexcept(FE_DIVBYZERO) != 0);', "true", "計算の異常を後からまとめて検知する", ("最適化で計算が消える", "結果を使わない計算は、最適化で削除されることがあります。結果を使うか、`volatile` を使います。")),
    ("feraiseexcept", "浮動小数点例外を、意図して発生させる。", "テストなどで、例外が起きた状態を作りたいときに、指定した例外のフラグを立てます。ハードウェアの例外の設定によっては、トラップ（割り込み）になります。", "int feraiseexcept(int excepts);", [("excepts", "int", "発生させる例外のビットのマスク")], "成功なら 0",
     'std::feclearexcept(FE_ALL_EXCEPT);\nstd::feraiseexcept(FE_OVERFLOW);\nstd::println("{}", std::fetestexcept(FE_OVERFLOW) != 0);', "true", "例外処理のテスト", ("トラップが有効な環境で呼ぶ", "環境によってはプログラムが止まります。")),
    ("fegetexceptflag", "浮動小数点例外のフラグの状態を保存する。", "いまのフラグの状態を、あとで戻すために保存します。`fesetexceptflag` で復元します。", "int fegetexceptflag(std::fexcept_t* flagp, int excepts);", [("flagp", "fexcept_t*", "保存先"), ("excepts", "int", "保存する例外のビットのマスク")], "成功なら 0",
     'std::fexcept_t saved;\nstd::feraiseexcept(FE_INEXACT);\nstd::fegetexceptflag(&saved, FE_ALL_EXCEPT);\nstd::feclearexcept(FE_ALL_EXCEPT);\nstd::fesetexceptflag(&saved, FE_ALL_EXCEPT);\nstd::println("{}", std::fetestexcept(FE_INEXACT) != 0);', "true", "ライブラリを呼ぶ前後でフラグを保つ", ("保存せずにクリアする", "呼び出し元が気にしているフラグまで消してしまいます。")),
    ("fesetexceptflag", "保存しておいた浮動小数点例外のフラグを復元する。", "`fegetexceptflag` で保存した状態を元に戻します。例外そのものは発生させず、フラグだけ設定します。", "int fesetexceptflag(const std::fexcept_t* flagp, int excepts);", [("flagp", "const fexcept_t*", "復元する状態"), ("excepts", "int", "復元する例外のビットのマスク")], "成功なら 0",
     'std::fexcept_t saved;\nstd::feclearexcept(FE_ALL_EXCEPT);\nstd::fegetexceptflag(&saved, FE_ALL_EXCEPT);\nstd::feraiseexcept(FE_OVERFLOW);\nstd::fesetexceptflag(&saved, FE_ALL_EXCEPT);\nstd::println("{}", std::fetestexcept(FE_OVERFLOW) != 0);', "false", "計算の途中で起きたフラグを取り消す", ("`excepts` の指定が足りない", "指定したビットだけが復元されます。")),
    ("fegetround", "現在の浮動小数点の丸めモードを調べる。", "丸めの規則（最も近い値、切り上げ、切り捨てなど）は切り替えられます。いまの設定を調べるのが `fegetround` で、変えるのは `fesetround` です。", "int fegetround();", [], "`FE_TONEAREST`・`FE_UPWARD`・`FE_DOWNWARD`・`FE_TOWARDZERO` のどれか",
     'std::println("{}", std::fegetround() == FE_TONEAREST);', "true", "丸めモードを変えた後に元へ戻す", ("設定を覚えずに変える", "先に `fegetround` で保存してから `fesetround` します。")),
    ("fegetenv", "浮動小数点環境（フラグと丸めモード）を丸ごと保存する。", "例外フラグと丸めモードなどを、1 つにまとめて保存します。`fesetenv` で復元します。", "int fegetenv(std::fenv_t* envp);", [("envp", "fenv_t*", "保存先")], "成功なら 0",
     'std::fenv_t env;\nstd::fegetenv(&env);\nstd::fesetround(FE_UPWARD);\nstd::fesetenv(&env);\nstd::println("{}", std::fegetround() == FE_TONEAREST);', "true", "計算の前後で環境を元に戻す", ("保存した環境を、別のスレッドに持ち込む", "環境はスレッドごとです。")),
    ("fesetenv", "保存しておいた浮動小数点環境を復元する。", "`fegetenv` で保存した環境（フラグと丸めモード）を元に戻します。", "int fesetenv(const std::fenv_t* envp);", [("envp", "const fenv_t*", "復元する環境（`FE_DFL_ENV` も指定可）")], "成功なら 0",
     'std::fenv_t env;\nstd::fegetenv(&env);\nstd::fesetround(FE_DOWNWARD);\nstd::fesetenv(&env);\nstd::println("{}", std::fegetround() == FE_TONEAREST);', "true", "丸めモードを一時的に変える処理の後始末", ("例外フラグも元に戻ると気づかない", "保存時点のフラグに戻ります。その後に起きたフラグは消えます。")),
    ("feholdexcept", "環境を保存し、例外フラグをクリアして、例外を止めるモードに入る。", "計算中に起きる例外を気にせず、まとめて後で処理したいときに使います。環境を保存してフラグを消し、以降の例外ではトラップしない状態にします。", "int feholdexcept(std::fenv_t* envp);", [("envp", "fenv_t*", "保存先")], "成功なら 0",
     'std::fenv_t env;\nstd::println("{}", std::feholdexcept(&env) == 0);\nstd::feupdateenv(&env);', "true", "計算の例外をまとめて処理する", ("`feupdateenv` で戻し忘れる", "必ず `feupdateenv` か `fesetenv` で元の環境に戻します。")),
    ("feupdateenv", "保存した環境を復元し、保留中の例外を再び発生させる。", "`feholdexcept` で止めていた間に起きた例外を、環境を戻すときにまとめて発生させます。", "int feupdateenv(const std::fenv_t* envp);", [("envp", "const fenv_t*", "復元する環境")], "成功なら 0",
     'std::fenv_t env;\nstd::feholdexcept(&env);\nstd::feraiseexcept(FE_INEXACT);\nstd::feupdateenv(&env);\nstd::println("{}", std::fetestexcept(FE_INEXACT) != 0);', "true", "例外を一時的に止めた後で、起きたものを引き継ぐ", ("`fesetenv` と取り違える", "`fesetenv` は保留中の例外を捨て、`feupdateenv` は再発生させます。"))]:
    Q(FE + nm + ".md", "std::" + nm, summ, "rare", ["cfenv", "print"], intro, ["`<cfenv>` の関数（浮動小数点環境の操作）。", "例外を投げず、フラグで知らせる。", "ほとんどのゲームでは使わない。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=[("[`fesetround`](fesetround.md)", "丸めモードを変える")], cx="定数", ver=("11", "C++11"), info=FEI, rj=f"cfenv/{nm}.html", cr=f"numeric/fenv/{nm}",
      group="浮動小数点環境（<cfenv>）")

if __name__ == "__main__":
    flush_hubs()
