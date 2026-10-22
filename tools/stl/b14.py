"""バッチ 14: 入出力ストリームの未登録分（マニピュレータ、iostate、クラス、streambuf、C の補助）。"""
from mk import *  # noqa: F401,F403

IO = "io/"
IOI = "[`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。"
IOG = None


def M(name, summary, intro, tips, body, out, miss, sim, inc=("iostream",), ver=None, pre="", rank="rare", sig=None, args=None, ret="ストリームへの参照"):
    Q(IO + name + ".md", "std::" + name, summary, rank, [*inc], intro, tips, sig or f"std::ios_base& {name}(std::ios_base& str);", args if args is not None else [("str", "ios_base&", "対象のストリーム")], ret, body, out,
      use="出力の書式を、ストリームに設定する", miss=miss, sim=sim, cx="定数", ver=ver, info=IOI, pre=pre, rj=f"ios/{name}.html", cr=f"io/manip/{name}")


M("showbase", "整数の出力に、進数の接頭辞（`0x` や `0`）を付ける。", "`std::hex` で 16 進数を出力しても、ふつうは `ff` のように接頭辞が付きません。`showbase` を設定すると、`0xff` のように、進数が分かる接頭辞が付きます。", ["`hex` で `0x`、`oct` で `0` が付く。", "`noshowbase` で解除する。", "大文字にするなら `uppercase`。"],
  'std::cout << std::showbase << std::hex << 255 << \'\\n\';', "0xff", ("設定が残り続ける", "ストリームの書式は設定したら残ります。必要なら `noshowbase` で戻します。"), [("[`hex`](hex.md)", "16 進数にする"), ("[`uppercase`](uppercase.md)", "大文字にする")])
M("showpoint", "小数の出力に、小数点と末尾の 0 を必ず付ける。", "`std::cout << 1.0` は、既定では `1` と出力されます。`showpoint` を設定すると、`1.00000` のように、小数点と桁数ぶんの 0 が付きます。", ["有効桁数（既定は 6）ぶんまで 0 が付く。", "`noshowpoint` で解除する。", "桁数は `setprecision` で変える。"],
  'std::cout << std::showpoint << 1.0 << \'\\n\';', "1.00000", ("`fixed` と取り違える", "`showpoint` は有効桁数ぶんの桁、`fixed` は小数点以下の桁数が基準です。"), [("[`fixed`](fixed.md)", "小数点以下の桁数で固定"), ("[`setprecision`](setprecision.md)", "桁数を設定")])
M("showpos", "正の数の出力に、`+` を付ける。", "ふつうは、正の数の前には何も付きません。`showpos` を設定すると、`+5` のように `+` が付きます。ダメージの増減表示（+10 / -3）などで便利です。", ["`noshowpos` で解除する。", "0 にも `+0` が付く。", "整数にも小数にも効く。"],
  'std::cout << std::showpos << 5 << \'\\n\';', "+5", ("設定が残り続ける", "他の出力にも `+` が付き続けます。必要なら `noshowpos` で戻します。"), [("[`setw`](setw.md)", "幅を設定")])
M("skipws", "入力で、先頭の空白を読み飛ばす（既定でオン）。", "`cin >> x` が、先頭の空白や改行を飛ばしてくれるのは、`skipws` が既定でオンだからです。`noskipws` で解除すると、空白も 1 文字として読めます。", ["既定でオン。", "`std::noskipws` で空白も読む。", "文字単位で読みたいときに `noskipws` を使う。"],
  'std::istringstream in(" x");\nin >> std::noskipws;\nchar c;\nin >> c;\nstd::println("{}", c == \' \');', "true", ("`noskipws` を戻し忘れる", "設定が残り、後続の整数の入力が失敗します。`skipws` で戻します。"), [("[`ws`](ws.md)", "空白を読み飛ばす")], inc=("sstream", "print"))
M("unitbuf", "出力のたびに、バッファをフラッシュする。", "出力はふつうバッファに貯められて、まとめて書き出されます。`unitbuf` を設定すると、`<<` のたびに書き出されます。`cerr` が既定でこの設定です。クラッシュ直前のログを確実に残したいときに使いますが、遅くなります。", ["`cerr` は既定でオン。", "`nounitbuf` で解除する。", "遅くなるので、必要な場面だけ。"],
  'std::cout << std::unitbuf << "x\\n";', "x", ("速度を気にしない", "毎回フラッシュするので、大量の出力が遅くなります。"), [("[`flush`](flush.md)", "手動でフラッシュ")])
M("uppercase", "16 進数や指数表記の英字を、大文字で出力する。", "`0xff` が `0XFF`、`1e5` が `1E5` になります。16 進数のダンプや、見やすさを優先した表示で使います。", ["`showbase` と組み合わせると `0XFF`。", "`nouppercase` で解除する。", "指数表記の `e` も大文字になる。"],
  'std::cout << std::uppercase << std::hex << std::showbase << 255 << \'\\n\';', "0XFF", ("`showbase` を忘れる", "`showbase` がないと、`FF` と出力されます。"), [("[`showbase`](showbase.md)", "接頭辞を付ける"), ("[`hex`](hex.md)", "16 進数にする")])
M("dec", "整数を 10 進数で出力・入力する（既定）。", "`std::hex` や `std::oct` に切り替えたあと、元の 10 進数に戻すときに使います。何も設定しなければ、すでに 10 進数です。", ["既定は 10 進数。", "`hex`・`oct` のあとに戻すときに使う。", "設定はストリームに残る。"],
  'std::cout << std::hex << 255 << \' \' << std::dec << 255 << \'\\n\';', "ff 255", ("戻し忘れる", "`hex` のまま後続の出力が続きます。`dec` で戻します。"), [("[`hex`](hex.md)", "16 進数"), ("[`oct`](oct.md)", "8 進数")])
M("oct", "整数を 8 進数で出力・入力する。", "ファイルの権限（`0755` など）の表示に使われる、8 進数で出力します。", ["`dec` で 10 進数に戻す。", "`showbase` を付けると先頭に `0` が付く。", "入力にも効く。"],
  'std::cout << std::oct << 8 << \'\\n\';', "10", ("戻し忘れる", "`dec` で戻さないと、後続の整数も 8 進数で出力されます。"), [("[`hex`](hex.md)", "16 進数"), ("[`dec`](dec.md)", "10 進数")])
M("hexfloat", "浮動小数点数を、16 進の指数表記で出力する。", "10 進数への変換で丸めが入らない、正確な表現です。浮動小数点の値を、一切の誤差なしでテキストに保存したいときに使います。", ["`0x1p+0`（1.0）のような形になる。", "読み込みは `std::hexfloat` を設定した入力。", "`defaultfloat` で戻す。"],
  'std::cout << std::hexfloat << 1.0 << \'\\n\';', "0x1p+0", ("人が読むために使う", "人には読みにくい表現です。正確さが必要なときだけ使います。"), [("[`fixed`](fixed.md)", "固定小数点"), ("[`defaultfloat`](defaultfloat.md)", "既定に戻す")])
M("defaultfloat", "浮動小数点数の出力を、既定の形式に戻す。", "`fixed` や `scientific` を設定したあと、既定の形式（値に応じて自動で選ぶ）に戻すときに使います。", ["`fixed`・`scientific`・`hexfloat` を解除する。", "桁数（`setprecision`）は変わらない。", "設定はストリームに残る。"],
  'std::cout << std::fixed << 1.5 << \' \' << std::defaultfloat << 1.5 << \'\\n\';', "1.500000 1.5", ("`setprecision` もリセットされると思う", "桁数は別の設定です。戻したいなら `setprecision(6)` も指定します。"), [("[`fixed`](fixed.md)", "固定小数点")])
M("internal", "符号や接頭辞を左に、数字を右に寄せる（間を埋める）。", "`setw` で幅を決めたとき、`-42` を `-00042` のように、符号と数字の間を埋めて表示できます。`left`・`right` は全体を寄せるのに対し、`internal` は符号と数字の間を埋めます。", ["`setfill('0')` と組み合わせて使う。", "`left`・`right`・`internal` から 1 つを選ぶ。", "幅は `setw` で決める。"],
  'std::cout << std::internal << std::setw(6) << std::setfill(\'0\') << -42 << \'\\n\';', "-00042", ("`setw` を忘れる", "幅を指定しないと、埋める場所がありません。"), [("[`left`](left.md)", "左寄せ"), ("[`right`](right.md)", "右寄せ")], inc=("iostream", "iomanip"))
M("left", "出力を、幅の中で左寄せにする。", "`setw` で幅を決めたとき、文字を左に寄せて、右側を埋めます。表の左揃えの列に使います。", ["`setw` は次の 1 回の出力にだけ効く。", "`left` の設定はストリームに残る。", "`right` で戻す。"],
  'std::cout << std::left << std::setw(5) << 42 << \'|\\n\';', "42   |", ("`setw` が次の出力でリセットされる", "`setw` は 1 回の出力ごとに必要です。`left` は残ります。"), [("[`right`](right.md)", "右寄せ"), ("[`setw`](setw.md)", "幅を設定")], inc=("iostream", "iomanip"))
M("right", "出力を、幅の中で右寄せにする（既定）。", "`setw` で幅を決めたとき、文字を右に寄せて、左側を埋めます。数値の列を揃えるのに使います。", ["既定は右寄せ。", "`left` のあとで戻すときに使う。", "`setw` は 1 回の出力ごとに必要。"],
  'std::cout << std::right << std::setw(5) << 42 << \'\\n\';', "   42", ("`left` のまま戻し忘れる", "表示が左寄せのままになります。"), [("[`left`](left.md)", "左寄せ"), ("[`setw`](setw.md)", "幅を設定")], inc=("iostream", "iomanip"))
M("setbase", "整数の基数（8・10・16）を設定する。", "`hex`・`dec`・`oct` を、数値で切り替えます。基数を変数で決めたいときに便利です。", ["8・10・16 のどれか（それ以外は 10 に戻る）。", "`hex`・`dec`・`oct` と同じ効果。", "`<iomanip>` が必要。"],
  'std::cout << std::setbase(16) << 255 << \'\\n\';', "ff", ("2 進数を指定する", "`setbase(2)` はできません（10 になります）。2 進数は `std::bitset` です。"), [("[`hex`](hex.md)", "16 進数"), ("[`std::bitset`](../containers/bitset.md)", "2 進数の表示")], inc=("iostream", "iomanip"),
  sig="/* 実装定義 */ setbase(int base);", args=[("base", "int", "8・10・16 のどれか")])
M("setiosflags", "書式フラグを、まとめて設定する。", "`showpos | uppercase` のように、複数のフラグを 1 回で設定できます。`resetiosflags` で解除します。", ["フラグは `|` でつなぐ。", "追加であり、他のフラグは変わらない。", "`<iomanip>` が必要。"],
  'std::cout << std::setiosflags(std::ios::showpos) << 5 << \'\\n\';', "+5", ("`basefield` のフラグを足す", "`ios::hex` を足しても `dec` が残って効かないことがあります。`std::hex` を使います。"), [("[`resetiosflags`](resetiosflags.md)", "フラグを解除")], inc=("iostream", "iomanip"),
  sig="/* 実装定義 */ setiosflags(std::ios_base::fmtflags mask);", args=[("mask", "fmtflags", "設定するフラグ")])
M("resetiosflags", "書式フラグを、まとめて解除する。", "`setiosflags` で設定したフラグを、指定して解除します。", ["フラグは `|` でつなぐ。", "指定したフラグだけが解除される。", "`<iomanip>` が必要。"],
  'std::cout << std::showpos << std::resetiosflags(std::ios::showpos) << 5 << \'\\n\';', "5", ("設定していないフラグを解除する", "何も起こりません。"), [("[`setiosflags`](setiosflags.md)", "フラグを設定")], inc=("iostream", "iomanip"),
  sig="/* 実装定義 */ resetiosflags(std::ios_base::fmtflags mask);", args=[("mask", "fmtflags", "解除するフラグ")])
M("ws", "入力で、空白（スペース・改行・タブ）を読み飛ばす。", "`getline` の前後などで、残っている空白や改行を捨てたいときに、`in >> std::ws` と書きます。", ["連続する空白をすべて飛ばす。", "`skipws` が有効でも、`getline` では飛ばされないので使う。", "文字は 1 つも消費しない（空白だけ）。"],
  'std::istringstream in("   x");\nin >> std::ws;\nchar c;\nin >> c;\nstd::println("{}", c);', "x", ("改行が残って `getline` が空を返す", "`cin >> n` のあとの改行が残ります。`cin >> std::ws` か `ignore` で捨てます。"), [("[`skipws`](skipws.md)", "既定の空白の読み飛ばし")], inc=("sstream", "print"),
  sig="template <class CharT, class Traits>\nstd::basic_istream<CharT, Traits>& ws(std::basic_istream<CharT, Traits>& is);", args=[("is", "istream&", "対象のストリーム")])
M("ends", "文字列の終端（`'\\0'`）を出力する。", "`ostringstream` に書いた内容を、C の文字列のように `'\\0'` で終わらせたいときに、`ends` を書き込みます。ふつうは `str()` で足ります。", ["`'\\0'` を 1 文字書き込む。", "`ostringstream` の `str()` には終端が含まれることになる。", "ふつうは不要。"],
  'std::ostringstream os;\nos << "ab" << std::ends;\nstd::println("{}", os.str().size());', "3", ("`str()` の長さがずれる", "終端も含まれるので、長さが 1 増えます。"), [("[`endl`](endl.md)", "改行してフラッシュ")], inc=("sstream", "print"),
  sig="template <class CharT, class Traits>\nstd::basic_ostream<CharT, Traits>& ends(std::basic_ostream<CharT, Traits>& os);", args=[("os", "ostream&", "対象のストリーム")])
M("emit_on_flush", "osyncstream で、フラッシュのたびに出力を確定する設定にする。", "`osyncstream` は、普通は破棄されるときにまとめて出力します。`emit_on_flush` を設定すると、`flush` のたびに出力が確定します。", ["`noemit_on_flush` で解除する。", "既定はオフ（破棄時にまとめて出力）。", "`flush_emit` は、1 回だけ確定してフラッシュする。"],
  'std::osyncstream out(std::cout);\nout << std::emit_on_flush << "x\\n" << std::flush;', "x", ("既定でオンだと思う", "既定はオフです。"), [("[`flush_emit`](flush_emit.md)", "1 回だけ確定する"), ("[`osyncstream`](osyncstream.md)", "同期出力")], inc=("iostream", "syncstream"), ver=("20", "C++20"),
  sig="template <class CharT, class Traits>\nstd::basic_ostream<CharT, Traits>& emit_on_flush(std::basic_ostream<CharT, Traits>& os);", args=[("os", "ostream&", "対象のストリーム")])
M("flush_emit", "osyncstream の出力を確定して、フラッシュする。", "`osyncstream` に溜めた出力を、いまこの時点で確定（`emit`）してフラッシュします。複数のスレッドが書いても、行が混ざらずに出力されます。", ["`out << \"...\" << std::flush_emit;` と書く。", "`emit()` と `flush()` を一度に行う。", "C++20 の同期出力の部品。"],
  'std::osyncstream out(std::cout);\nout << "hi\\n" << std::flush_emit;', "hi", ("`osyncstream` 以外に使う", "普通のストリームに使っても、フラッシュだけです。"), [("[`osyncstream`](osyncstream.md)", "同期出力"), ("[`emit_on_flush`](emit_on_flush.md)", "フラッシュのたびに確定")], inc=("iostream", "syncstream"), ver=("20", "C++20"),
  sig="template <class CharT, class Traits>\nstd::basic_ostream<CharT, Traits>& flush_emit(std::basic_ostream<CharT, Traits>& os);", args=[("os", "ostream&", "対象のストリーム")])
M("quoted", "文字列を、引用符で囲んで出力・入力する。", "空白を含む文字列を、`\"a b\"` のように引用符で囲んで書き出し、読み込むときは引用符を外して読み戻せます。設定ファイルの書き出しなどに便利です。", ["`\"` で囲み、中の `\"` は `\\` でエスケープする。", "入力でも引用符を処理して元に戻す。", "`<iomanip>` が必要。"],
  'std::cout << std::quoted("a b") << \'\\n\';', "\"a b\"", ("入力時に引用符を忘れる", "`quoted` で読むには、入力側にも引用符が必要です。"), [("[`getline`](getline.md)", "行を読む")], inc=("iostream", "iomanip"), ver=("14", "C++14"),
  sig="template <class CharT, class Traits, class Alloc>\n/* 実装定義 */ quoted(const std::basic_string<CharT, Traits, Alloc>& s, CharT delim = '\"', CharT escape = '\\\\');", args=[("s", "文字列", "囲む文字列"), ("delim", "文字", "省略可。囲む文字"), ("escape", "文字", "省略可。エスケープ文字")])
M("put_money", "金額を、ロケールの形式で出力する。", "金額（整数の最小単位）を、ロケールに応じた通貨の書式で出力します。クラシックロケールでは、単なる数字になります。", ["ロケールの `money_put` の書式に従う。", "`showbase` を付けると通貨記号も出る。", "`<iomanip>` が必要。"],
  'std::cout.imbue(std::locale::classic());\nstd::cout << std::put_money(12345L) << \'\\n\';', "12345", ("ロケールを設定しない", "既定の `\"C\"` ロケールでは、通貨の区切りや記号は出ません。"), [("[`get_money`](get_money.md)", "入力")], inc=("iostream", "iomanip", "locale"), ver=("11", "C++11"),
  sig="template <class MoneyT>\n/* 実装定義 */ put_money(const MoneyT& mon, bool intl = false);", args=[("mon", "long double / string", "金額"), ("intl", "bool", "省略可。国際表記にするか")])
M("get_money", "金額を、ロケールの形式で入力する。", "ロケールの通貨の書式で書かれた文字列を、金額の数値として読み込みます。", ["ロケールの `money_get` の書式に従う。", "戻りは最小単位の整数。", "`<iomanip>` が必要。"],
  'std::istringstream in("123");\nin.imbue(std::locale::classic());\nlong double v = 0;\nin >> std::get_money(v);\nstd::println("{}", static_cast<int>(v));', "123", ("ロケールの違いを考えない", "国によって区切りや記号が違います。"), [("[`put_money`](put_money.md)", "出力")], inc=("sstream", "iomanip", "locale", "print"), ver=("11", "C++11"),
  sig="template <class MoneyT>\n/* 実装定義 */ get_money(MoneyT& mon, bool intl = false);", args=[("mon", "long double / string", "結果を入れる変数"), ("intl", "bool", "省略可。国際表記にするか")])
M("put_time", "日時（`tm`）を、書式を指定して出力する。", "`strftime` のような書式（`%Y-%m-%d`）で、`tm` をストリームに出力します。バッファを用意せずに書けます。", ["書式は `strftime` と同じ（`%Y` `%m` `%d` `%H` `%M` `%S`）。", "`std::tm` を渡す。", "`<iomanip>` が必要。"],
  'std::tm t{};\nt.tm_year = 124;  // 2024 年\nt.tm_mon = 0;\nt.tm_mday = 1;\nstd::cout << std::put_time(&t, "%Y-%m-%d") << \'\\n\';', "2024-01-01", ("`tm_year` を西暦で入れる", "`tm_year` は 1900 からの経過年です。"), [("[`get_time`](get_time.md)", "入力"), ("[`strftime`](ctime/strftime.md)", "バッファに書き込む版")], inc=("iostream", "iomanip", "ctime"), ver=("11", "C++11"),
  sig="template <class CharT>\n/* 実装定義 */ put_time(const std::tm* tmb, const CharT* fmt);", args=[("tmb", "const tm*", "出力する日時"), ("fmt", "文字列", "書式")])
M("get_time", "日時を、書式を指定して読み込む。", "`strptime` のような書式で、文字列から `tm` に読み込みます。", ["書式は `strftime` と同じ。", "失敗するとストリームが `failbit` になる。", "`<iomanip>` が必要。"],
  'std::istringstream in("12:30");\nstd::tm t{};\nin >> std::get_time(&t, "%H:%M");\nstd::println("{} {}", t.tm_hour, t.tm_min);', "12 30", ("失敗を確かめない", "書式に合わないと `failbit` が立ちます。`if (in)` で確かめます。"), [("[`put_time`](put_time.md)", "出力")], inc=("sstream", "iomanip", "ctime", "print"), ver=("11", "C++11"),
  sig="template <class CharT>\n/* 実装定義 */ get_time(std::tm* tmb, const CharT* fmt);", args=[("tmb", "tm*", "結果を入れる変数"), ("fmt", "文字列", "書式")])

# ================= 型・状態 =================
add_secs(IO + "ios_base.md", fn("std::ios_base::fmtflags", "using fmtflags = /* ビットマスク型 */;", None, "書式フラグ（`showbase`・`hex`・`fixed` など）を表すビットマスク型", "定数", None,
         notes="`flags()` で取れる、書式の状態をまとめた型です。`ios::showpos | ios::uppercase` のように `|` でつなぎます。個別に設定するなら、マニピュレータ（`std::showpos` など）が読みやすいです。", ids="fmtflags"))
for nm, what in [("streamsize", "ストリームで読み書きする文字数を表す符号つき整数型"), ("streamoff", "ストリーム上の位置の差（オフセット）を表す符号つき整数型"), ("streampos", "ストリーム上の位置を表す型（`fpos<mbstate_t>` の別名）")]:
    add_secs(IO + "ios_base.md", fn("std::" + nm, f"using {nm} = /* 実装定義 */;", None, what, "定数", None,
             notes=f"{what}です。`read(buf, n)` の `n` や、`gcount()` の戻り値などに出てきます。", ids=nm))
add_secs(IO + "ios_base.md", fn("std::fpos", "template <class StateT>\nclass fpos;", None, "ストリームの位置を表すクラス（状態つき）", "定数", None,
         notes="マルチバイト文字のように、位置に状態が必要なストリームのための位置の型です。`tellg()` の戻り値（`streampos`）が、これにあたります。整数のように足し引きできますが、`tellg()` で得た値以外の演算は、移植性がありません。", ids="fpos"))
for nm, what in [("badbit", "ストリームが壊れた（回復できないエラー）"), ("eofbit", "入力が終端に達した"), ("failbit", "操作に失敗した（形式が合わないなど。回復できる）"), ("goodbit", "エラーがない状態（値は 0）")]:
    add_secs(IO + "ios_base.md", fn("std::ios_base::" + nm, f"static constexpr iostate {nm} = /* 実装定義 */;", None, f"状態フラグ：{what}", "定数", None,
             notes=f"`rdstate()` で調べる状態フラグのひとつで、{what}ことを表します。`good()`・`eof()`・`fail()`・`bad()` で調べるほうが読みやすいです。", ids=nm))
for nm, what in [("iword", "ストリームに、任意の整数を 1 つ持たせる（`xalloc` で取った添字で）"), ("pword", "ストリームに、任意のポインタを 1 つ持たせる（`xalloc` で取った添字で）")]:
    add_secs(IO + "ios_base.md", fn("std::ios_base::" + nm, f"{'long' if nm == 'iword' else 'void*'}& {nm}(int idx);", [("idx", "int", "`xalloc()` で取った添字")], "格納場所への参照", "定数", None,
             notes=f"{what}。自作のマニピュレータが、ストリームごとの設定を覚えておくために使います。", ids=nm))

P(IO + "basic_ios.md", "std::basic_ios", "すべてのストリームの土台。状態の確認（good / fail / bad）とロケールの設定を持つ。", "rare", "ios",
  "`cin` も `cout` もファイルも、状態（「いま正常か」「入力が終わったか」）とロケールを持っています。その共通の部分を持つ土台が `basic_ios` で、`std::ios` はその `char` 版の別名です。ストリームの失敗を調べるときに使う `good()`・`fail()`・`bad()`・`rdstate()` は、この土台のメンバです。",
  ["`good()`・`eof()`・`fail()`・`bad()` で状態を調べる。", "`setstate()` で状態を設定し、`clear()` で戻す。", "`std::ios` = `basic_ios<char>`。"],
  [("入力が失敗したかを調べる", "`if (!(std::cin >> n)) { ... }`（`fail()` が呼ばれる）")],
  ("`eof()` だけでループを書く", "最後の読み込みの後で `eof()` が真になるまでループすると、最後に 1 回余分に読みます。読み込みの成否で判定します。"), [("[`ios_base`](ios_base.md)", "書式フラグなど"), ("[`istream`](istream.md)", "入力ストリーム"), ("[`ostream`](ostream.md)", "出力ストリーム")],
  ["ストリームの土台", "状態の確認とロケール", "ios は char 版の別名"],
  secs=[fn("std::basic_ios", "template <class CharT, class Traits = char_traits<CharT>>\nclass basic_ios : public ios_base;\nusing ios = basic_ios<char>;", None, "ストリームの共通の土台", "", None, ids="basic_ios"),
        fn("good", "bool good() const;", None, "エラーがなければ `true`（`badbit`・`eofbit`・`failbit` が全部立っていない）", "定数", None, ids="good"),
        fn("fail", "bool fail() const;", None, "`failbit` か `badbit` が立っていれば `true`", "定数", None, notes="読み込みの失敗（`int` に変換できない文字など）で `true` になります。`operator!` と `explicit operator bool` は、これを使っています。", ids="fail"),
        fn("bad", "bool bad() const;", None, "`badbit` が立っていれば `true`（回復できない深刻なエラー）", "定数", None, ids="bad"),
        fn("rdstate", "iostate rdstate() const;", None, "状態フラグ（`badbit`・`eofbit`・`failbit`）のビットマスク", "定数", None, ids="rdstate"),
        fn("setstate", "void setstate(iostate state);", [("state", "iostate", "立てる状態フラグ")], "なし", "定数", None, notes="既存の状態に、フラグを**足し**ます（上書きはしません）。上書きは `clear(state)` です。", ids="setstate"),
        fn("imbue", "std::locale imbue(const std::locale& loc);", [("loc", "locale", "設定するロケール")], "それまでのロケール", "定数", None, notes="ストリームのロケールを設定します。数値の区切りや日付の書式が変わります。", ids="imbue"),
        fn("getloc", "std::locale getloc() const;", None, "ストリームのロケール", "定数", None, ids="getloc")],
  code="""#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("abc");
  int n = 0;
  in >> n;  // 数字ではないので失敗
  std::println("{} {}", in.good(), in.fail());
}""", out="false true", info=IOI, rj="ios/basic_ios.html", cr="io/basic_ios")
for nm, base, what, intro in [
    ("basic_istream", "basic_ios", "入力ストリームの元になるテンプレート（`istream` の元）。", "`std::istream` は、`basic_istream<char>` の別名です。文字の型（`char`・`wchar_t`）を選べるように、元になるクラステンプレートがあります。ふつうは別名の `istream` を使います。"),
    ("basic_ostream", "basic_ios", "出力ストリームの元になるテンプレート（`ostream` の元）。", "`std::ostream` は、`basic_ostream<char>` の別名です。文字の型を選べるように、元になるクラステンプレートがあります。ふつうは別名の `ostream` を使います。"),
    ("iostream", "basic_istream と basic_ostream", "入力も出力もできるストリームのクラス。", "`std::iostream` は、`istream` と `ostream` の両方を継承した、読み書き両用のクラスです。`fstream` や `stringstream` の土台になります。関数の引数で、読み書き両用のストリームを受け取りたいときに使います。"),
    ("basic_iostream", "basic_istream と basic_ostream", "読み書き両用のストリームの元になるテンプレート（`iostream` の元）。", "`std::iostream` は、`basic_iostream<char>` の別名です。文字の型を選べるように、元になるクラステンプレートがあります。"),
    ("wistream", "basic_istream<wchar_t>", "`wchar_t` の入力ストリーム。", "`std::wistream` は、`basic_istream<wchar_t>` の別名です。`wchar_t` の文字列を入力するときに使います（`std::wcin` の型）。"),
    ("wostream", "basic_ostream<wchar_t>", "`wchar_t` の出力ストリーム。", "`std::wostream` は、`basic_ostream<wchar_t>` の別名です。`wchar_t` の文字列を出力するときに使います（`std::wcout` の型）。")]:
    tmpl = nm.startswith("basic")
    P(IO + nm + ".md", "std::" + nm, what, "rare", "istream" if "istream" in nm else "ostream" if "ostream" in nm else "iostream", intro,
      [f"`{nm}` は `{base}` から派生。", "ふつうは別名（`istream`・`ostream`）を使う。" if tmpl or nm.startswith("w") else "関数の引数で受けるときは、必要なほう（`istream` か `ostream`）を使う。", "関数の引数には、参照で受ける。"],
      [("ストリームを引数で受ける関数", "`void Save(std::ostream& os);`" if "ostream" in nm else "`void Load(std::istream& is);`")],
      ("値で受ける", "ストリームはコピーできません。参照（`&`）で受けます。"), [("[`istream`](istream.md)", "入力ストリーム"), ("[`ostream`](ostream.md)", "出力ストリーム")],
      [what.rstrip("。"), "コピーできないので参照で受ける", "ふつうは別名を使う"],
      sig=f"template <class CharT, class Traits = char_traits<CharT>>\nclass {nm};" if tmpl else f"using {nm} = /* {base} */;", args=[], ret="ストリームとして使う", cx="操作による",
      code=f"""#include <iostream>
#include <print>
#include <type_traits>

int main() {{
  std::println("{{}}", std::is_class_v<std::{nm}>);
}}""", out="true", info=IOI, rj=f"istream/{nm}.html" if "istream" in nm else f"ostream/{nm}.html", cr=f"io/{nm}")
add_secs(IO + "istream.md", fn("std::istream::peek", "int_type peek();", None, "次の 1 文字（読み進めない）。終端なら `EOF`", "定数", None, notes="次に読む文字を、消費せずにのぞきます。次の文字によって読み方を切り替えたいときに使います。", ids="peek"))
add_secs(IO + "istream.md", fn("std::istream::unget", "istream& unget();", None, "ストリームへの参照", "定数", None, notes="直前に読んだ 1 文字を戻して、もう一度読めるようにします。戻せないときは `badbit` が立ちます。", ids="unget"))
add_secs(IO + "istream.md", fn("std::istream::putback", "istream& putback(char_type ch);", [("ch", "char", "戻す文字")], "ストリームへの参照", "定数", None, notes="直前に読んだ文字として、指定した文字を戻します。`unget` と違い、戻す文字を指定できます。", ids="putback"))
add_secs(IO + "istream.md", fn("std::istream::readsome", "streamsize readsome(char_type* s, streamsize n);", [("s", "char*", "読み込み先"), ("n", "streamsize", "読む最大の文字数")], "読んだ文字数", "O(n)", None, notes="バッファに**すでにある**文字だけを、待たずに読みます。ブロックしたくないときに使います。", ids="readsome"))
add_secs(IO + "istream.md", fn("std::istream::sync", "int sync();", None, "成功なら 0、失敗なら -1", "実装による", None, notes="入力バッファを、ソース（ファイルや端末）と同期します。標準入力の読み残しを捨てる用途は、実装によって動作が違うので、`ignore` を使います。", ids="sync"))
add_secs(IO + "ostream.md", fn("std::ostream::put", "ostream& put(char_type ch);", [("ch", "char", "出力する文字")], "ストリームへの参照", "定数", None, notes="1 文字を、書式なしで出力します。`<<` と違い、`setw` などの影響を受けません。", ids="put"))
for nm, t_ in [("wcin", "wistream"), ("wcout", "wostream"), ("wcerr", "wostream"), ("wclog", "wostream")]:
    page_ = {"wcin": "cin", "wcout": "cout", "wcerr": "cerr", "wclog": "cerr"}[nm]
    add_secs(IO + page_ + ".md", fn("std::" + nm, f"extern std::{t_} {nm};", None, f"`{t_}`（`wchar_t` の{'標準入力' if nm == 'wcin' else '標準出力' if nm == 'wcout' else '標準エラー出力' if nm == 'wcerr' else 'ログ出力（バッファあり）'}）", "操作による", None,
             notes=f"`{nm}` は、`{nm[1:]}` の `wchar_t` 版です。`wchar_t` の文字列（`L\"...\"`）を扱うときに使います。1 つのプログラムで `{nm[1:]}` と `{nm}` を混ぜて使うと、文字化けや動作不良の原因になることがあります。", ids=nm))
add_secs(IO + "osyncstream.md", fn("std::syncbuf", "template <class CharT, class Traits = char_traits<CharT>, class Allocator = allocator<CharT>>\nclass basic_syncbuf;\nusing syncbuf = basic_syncbuf<char>;", None, "出力を一時的に溜めて、`emit()` でまとめて書き出すストリームバッファ", "操作による", None,
         notes="`osyncstream` の内部で使われる、バッファの型です。`emit()` を呼ぶまで、書き込みを溜めておきます。複数のスレッドが同じ出力先に書いても、`emit()` の単位で行が混ざらないようにします。直接使うことは少なく、`osyncstream` を使います。", ver=("20", "C++20"), ids="syncbuf"))

# ================= streambuf 周辺 =================
for nm, sig_, what, notes in [
    ("sgetc", "int_type sgetc();", "次の 1 文字を、読み進めずに返す", "入力バッファから、次の文字をのぞきます。消費はしません。"),
    ("sputc", "int_type sputc(char_type ch);", "1 文字を書き込む", "出力バッファに 1 文字を書きます。失敗すると `EOF` を返します。"),
    ("in_avail", "streamsize in_avail();", "待たずに読める文字の数", "入力バッファに、**すでに**入っている文字の数を返します。ブロックせずに読める量を知りたいときに使います。"),
    ("pubsync", "int pubsync();", "成功なら 0、失敗なら -1", "バッファの内容を、ソースや出力先と同期します。`flush()` の中でも呼ばれます。"),
    ("pubseekoff", "pos_type pubseekoff(off_type off, ios_base::seekdir way, ios_base::openmode which = ios_base::in | ios_base::out);", "新しい位置（失敗したら `-1`）", "位置を相対的に移動します。`seekg`・`seekp` は、これを呼んでいます。"),
    ("pubsetbuf", "streambuf* pubsetbuf(char_type* s, streamsize n);", "バッファを設定できたら自身（できなければ `nullptr`）", "ストリームバッファが使う、メモリ領域を指定します。実装によっては無視されます。")]:
    add_secs(IO + "streambuf.md", fn("std::streambuf::" + nm, sig_, None, what, "定数", None, notes=notes, ids=nm))
for nm, base, what, intro, code_, out_ in [
    ("basic_streambuf", "", "ストリームバッファの元になるテンプレート（`streambuf` の元）。", "ストリームは、文字の入出力の窓口です。実際にファイルや文字列に読み書きするのは、その裏にある「ストリームバッファ」です。`std::streambuf` は `basic_streambuf<char>` の別名で、自作のバッファ（ネットワークやログ）を作るときの土台になります。",
     'std::stringbuf buf("ab");\nstd::basic_streambuf<char>* p = &buf;\nstd::println("{}", static_cast<char>(p->sgetc()));', "a"),
    ("filebuf", "basic_streambuf<char>", "ファイルへの読み書きを担当するストリームバッファ。", "`ifstream`・`ofstream`・`fstream` の裏にあるのが `filebuf` です。`rdbuf()` で取り出して、別のストリームに付け替えると、出力先を切り替えられます。",
     'std::filebuf fb;\nstd::println("{}", fb.is_open());', "false"),
    ("stringbuf", "basic_streambuf<char>", "メモリ上の文字列への読み書きを担当するストリームバッファ。", "`stringstream` の裏にあるのが `stringbuf` です。`cout` の出力先を一時的に `stringbuf` に付け替えると、出力を文字列として取り込めます（テストで便利）。",
     'std::stringbuf sb;\nstd::ostream os(&sb);\nos << "hello";\nstd::println("{}", sb.str());', "hello")]:
    P(IO + nm + ".md", "std::" + nm, what, "rare", "streambuf", intro,
      ["ストリームの裏で実際に読み書きを行う。", "`rdbuf()` で取り出し・付け替えができる。", "自作するときは、`underflow`・`overflow` などを書く。"],
      [("`cout` の出力を文字列として取り込む", "`auto* old = std::cout.rdbuf(sb.rdbuf());` のあと、`std::cout.rdbuf(old);` で戻す")], ("付け替えたまま戻さない", "`rdbuf` で付け替えたら、スコープを抜ける前に必ず元に戻します。"),
      [("[`streambuf`](streambuf.md)", "char 版の別名"), ("[`stringstream`](stringstream.md)", "文字列ストリーム")], [what.rstrip("。"), "rdbuf() で付け替えられる", "自作の土台にもなる"],
      sig=f"template <class CharT, class Traits = char_traits<CharT>>\nclass {nm};" if nm.startswith("basic") else f"using {nm} = basic_{nm}<char>;  // 実際は派生クラス", args=[], ret="ストリームバッファとして使う", cx="操作による",
      code="#include <ios>\n#include <print>\n#include <sstream>\n#include <streambuf>\n#include <fstream>\n\nint main() {\n" + "\n".join("  " + l for l in code_.split("\n")) + "\n}", out=out_, info=IOI, rj=f"streambuf/{nm}.html", cr=f"io/{nm}")

# ================= 文字列ストリーム・ファイルストリーム・spanstream =================
for nm, base, what, intro in [
    ("wstringstream", "stringstream", "`wchar_t` の文字列ストリーム。", "`std::wstringstream` は、`stringstream` の `wchar_t` 版です。`wchar_t` の文字列を、組み立てたり解析したりするときに使います。"),
    ("wfstream", "fstream", "`wchar_t` のファイルストリーム。", "`std::wfstream` は、`fstream` の `wchar_t` 版です。ファイルを `wchar_t` の単位で読み書きします。文字コードの変換が絡むので、新しいコードでは UTF-8 のバイト列を `ifstream`・`ofstream` で扱うほうが一般的です。")]:
    P(IO + nm + ".md", "std::" + nm, what, "rare", "sstream" if "string" in nm else "fstream", intro,
      [f"`{base}` の `wchar_t` 版。", "`wstring` を扱う。", "ゲームでは UTF-8 の `string` を使うことが多い。"],
      [("Windows API と文字列をやり取りする", f"`std::{nm}`")], ("文字コードを考えない", "`wchar_t` は Windows では UTF-16、Linux では UTF-32 です。環境で意味が違います。"), [(f"[`{base}`]({base}.md)", "char 版")],
      [what.rstrip("。"), f"{base} の wchar_t 版", "UTF-8 の string が主流"],
      sig=f"using {nm} = basic_{nm[1:]}<wchar_t>;", args=[], ret="ストリームとして使う", cx="操作による",
      code=("#include <print>\n#include <sstream>\n\nint main() {\n  std::wstringstream ss;\n  ss << L\"abc\" << 42;\n  std::println(\"{}\", ss.str().size());\n}" if "string" in nm else
            "#include <fstream>\n#include <print>\n\nint main() {\n  std::wfstream fs;\n  std::println(\"{}\", fs.is_open());\n}"), out="5" if "string" in nm else "false", info="[`std::stringstream`](stringstream.md) を先に読んでください。" if "string" in nm else "[`std::fstream`](fstream.md) を先に読んでください。", rj=f"{'sstream' if 'string' in nm else 'fstream'}/{nm}.html", cr=f"io/{nm}")
for nm, base, what, intro, code_, out_ in [
    ("ispanstream", "istream", "`span` の上にあるメモリから、読み込むストリーム。", "`istringstream` は、文字列の**コピー**を持ちます。`ispanstream` は、すでにあるバッファ（`span<const char>`）を**そのまま**読むので、コピーが起きません。固定のバッファを解析するときに使います。",
     'std::ispanstream in(std::span<const char>("42 7", 4));\nint a = 0;\nint b = 0;\nin >> a >> b;\nstd::println("{} {}", a, b);', "42 7"),
    ("ospanstream", "ostream", "`span` の上にあるメモリに、書き込むストリーム。", "`ostringstream` は内部でメモリを確保します。`ospanstream` は、あらかじめ用意したバッファ（`span<char>`）に**そのまま**書き込むので、確保が起きません。ヒープを使いたくない場面（ゲームの毎フレームのログ）に向きます。",
     'char buf[16] = {};\nstd::ospanstream out{std::span<char>(buf)};\nout << 42;\nstd::println("{}", buf);', "42"),
    ("spanbuf", "streambuf", "`span` の上にあるメモリを使うストリームバッファ。", "`ispanstream` と `ospanstream` の裏にある、ストリームバッファです。固定のバッファに対して、読み書きを行います。直接使うことは少なく、`ispanstream`・`ospanstream` を使います。",
     'char buf[8] = "abc";\nstd::spanbuf sb{std::span<char>(buf)};\nstd::println("{}", sb.span().size());', "8")]:
    P(IO + nm + ".md", "std::" + nm, what, "rare", "spanstream", intro,
      ["コピーやヒープ確保が起きない。", "バッファは自分で用意し、生きている間だけ使える。", "C++23 の機能。"],
      [("固定のバッファを解析・書き込みする", f"`std::{nm}`")], ("バッファが先に消える", "ストリームはバッファを借りるだけです。バッファより先にストリームを破棄します。"), [("[`spanstream`](spanstream.md)", "読み書き両用"), ("[`std::span`](../containers/span.md)", "メモリの範囲を表す型")],
      [what.rstrip("。"), "コピーしない", "C++23"],
      sig=f"template <class CharT, class Traits = char_traits<CharT>>\nclass basic_{nm};\nusing {nm} = basic_{nm}<char>;", args=[], ret="ストリームとして使う", cx="操作による",
      code="#include <print>\n#include <span>\n#include <spanstream>\n\nint main() {\n" + "\n".join("  " + l for l in code_.split("\n")) + "\n}", out=out_, ver=("23", "C++23"), info="[`std::spanstream`](spanstream.md) を先に読んでください。", rj=f"spanstream/{nm}.html", cr=f"io/{nm}")

# ================= C の補助（シグナル、可変引数、setjmp） =================
CS = IO
CSI = "[`<csignal>`](csignal.md) の概要を先に読んでください。"
Q(CS + "raise.md", "std::raise", "自分自身にシグナルを送る。", "rare", ["csignal", "print"], "シグナル処理をテストしたいとき、本当に `Ctrl+C` を押さなくても、`raise(SIGINT)` で自分自身にシグナルを送れます。`signal` で登録したハンドラが呼ばれます。",
  ["`signal` で登録したハンドラが呼ばれる。", "ハンドラの中では、限られた操作しかできない。", "`sig_atomic_t` の変数を書き換えるのが定番。"], "int raise(int sig);", [("sig", "int", "送るシグナル（`SIGINT` など）")], "成功なら 0",
  'std::signal(SIGINT, Handler);\nstd::raise(SIGINT);\nstd::println("{}", got);', "1", use="Ctrl+C のハンドラのテスト", miss=("ハンドラで色々な処理をする", "ハンドラの中でできる操作は限られます。フラグを立てて、メインループで処理します。"),
  sim=[("[`signal`](csignal.md)", "ハンドラを登録する"), ("[`sig_atomic_t`](sig_atomic_t.md)", "ハンドラで使える整数")], cx="定数", info=CSI, pre="volatile std::sig_atomic_t got = 0;\nvoid Handler(int) { got = 1; }", rj="csignal/raise.html", cr="utility/program/raise")
Q(CS + "sig_atomic_t.md", "std::sig_atomic_t", "シグナルハンドラの中で、安全に読み書きできる整数型。", "rare", ["csignal", "type_traits", "print"], "シグナルハンドラは、プログラムの途中に割り込んで呼ばれます。そのため、ふつうの変数の書き換えは、読み書きの途中で割り込まれて壊れるかもしれません。`sig_atomic_t` は、1 回の操作で読み書きが済むと保証された整数型で、ハンドラとメインの間のフラグに使います。",
  ["`volatile std::sig_atomic_t` として宣言する。", "ハンドラの中で書き換えてよい数少ない型。", "スレッド間の同期には使えない（`atomic` を使う）。"], "using sig_atomic_t = /* 整数型 */;", [], "なし（型）", 'std::println("{}", std::is_integral_v<std::sig_atomic_t>);', "true", use="Ctrl+C で終了フラグを立てる", miss=("スレッド間の通信に使う", "スレッド間には `std::atomic` を使います。`sig_atomic_t` は割り込み専用です。"),
  sim=[("[`raise`](raise.md)", "シグナルを送る")], cx="なし", info=CSI, rj="csignal/sig_atomic_t.html", cr="utility/program/sig_atomic_t")
CVA = "[`<cstdarg>`](cstdarg.md) の概要を先に読んでください。"
for nm, summ, intro, body in [
    ("va_start", "可変引数の読み取りを始める。", "`printf` のように、引数の数が決まっていない関数（`...`）で、引数を読む準備をします。最後の名前つきの引数を渡します。", "int Sum(int count, ...) {\n  va_list ap;\n  va_start(ap, count);\n  int sum = 0;\n  for (int i = 0; i < count; ++i) sum += va_arg(ap, int);\n  va_end(ap);\n  return sum;\n}"),
    ("va_arg", "可変引数から、次の引数を指定した型で取り出す。", "`va_start` のあとで、`va_arg(ap, 型)` と書くたびに、次の引数が取り出されます。型を間違えると未定義動作です。", "int Sum(int count, ...) {\n  va_list ap;\n  va_start(ap, count);\n  int sum = 0;\n  for (int i = 0; i < count; ++i) sum += va_arg(ap, int);\n  va_end(ap);\n  return sum;\n}"),
    ("va_end", "可変引数の読み取りを終える。", "`va_start` で始めた読み取りの後始末です。関数を抜ける前に、必ず対応する `va_end` を呼びます。", "int Sum(int count, ...) {\n  va_list ap;\n  va_start(ap, count);\n  int sum = 0;\n  for (int i = 0; i < count; ++i) sum += va_arg(ap, int);\n  va_end(ap);\n  return sum;\n}"),
    ("va_copy", "可変引数の読み取り状態をコピーする。", "`va_list` は、ふつうにコピーできません。同じ引数を 2 回読みたいとき、`va_copy(dst, src)` で複製します。複製した方にも、`va_end` が必要です。", "int SumTwice(int count, ...) {\n  va_list ap, ap2;\n  va_start(ap, count);\n  va_copy(ap2, ap);\n  int sum = 0;\n  for (int i = 0; i < count; ++i) sum += va_arg(ap, int);\n  for (int i = 0; i < count; ++i) sum += va_arg(ap2, int);\n  va_end(ap2);\n  va_end(ap);\n  return sum;\n}")]:
    call = "SumTwice(2, 1, 2)" if nm == "va_copy" else "Sum(3, 1, 2, 3)"
    res = "6" if nm == "va_copy" else "6"
    Q(CS + nm + ".md", nm, summ, "rare", ["cstdarg", "print"], intro, ["C の可変長引数の仕組み。", "型の安全性がない（型を間違えると未定義動作）。", "新しいコードでは、可変長テンプレート（`Args&&... args`）を使う。"],
      f"#define {nm}(/* ... */)", [], "（マクロ）", f'std::println("{{}}", {call});', res, use="C の API に合わせた可変引数の関数を書く", miss=("型を間違えて取り出す", "`va_arg(ap, double)` で `int` を渡されたものを取ると、未定義動作です。"),
      sim=[("可変長テンプレート", "型安全な書き方")], cx="定数", info=CVA, pre=body, rj=f"cstdarg/{nm}.html", cr=f"utility/variadic/{nm}")
Q(CS + "jmp_buf.md", "jmp_buf", "setjmp が保存した、実行位置の情報を入れる型。", "rare", ["csetjmp", "print"], "`setjmp` は、「ここに戻ってくる」という実行位置を保存します。その保存先が `jmp_buf` 型です。`longjmp(env, 値)` を呼ぶと、保存した位置まで一気にジャンプして戻れます。C++ では、デストラクタが呼ばれないため危険で、例外を使うのが一般的です。",
  ["`setjmp(env)` が保存し、`longjmp(env, 値)` で戻る。", "デストラクタは呼ばれない（C++ では危険）。", "新しいコードでは例外を使う。"], "using jmp_buf = /* 配列型 */;", [], "なし（型）",
  'std::jmp_buf env;\nif (setjmp(env) == 0) {\n  std::longjmp(env, 1);\n} else {\n  std::println("jumped");\n}', "jumped", use="（古い C のコードの保守）", miss=("デストラクタが飛ばされる", "`longjmp` で飛ぶと、途中のオブジェクトのデストラクタが呼ばれません。リソースがリークします。"),
  sim=[("[`setjmp` / `longjmp`](csetjmp.md)", "ジャンプ")], cx="定数", info="[`<csetjmp>`](csetjmp.md) の概要を先に読んでください。", rj="csetjmp/jmp_buf.html", cr="utility/program/jmp_buf")

if __name__ == "__main__":
    flush_hubs()
