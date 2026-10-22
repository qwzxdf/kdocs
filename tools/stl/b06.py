"""バッチ 6: <cmath> の未登録分。"""
from mk import *  # noqa: F401,F403

D = "numeric/cmath/"
HUB = "numeric/cmath.md"
INC = ["cmath", "print"]
V17 = ("17", "C++17")
V11 = ("11", "C++11")
CRB = "numeric/math/"


def M(name, summary, intro, sig, args, ret, body, out, use, miss, sim, rank="rare", ver=V11, tips=None, cr=None, extra_inc=None, rjn=None):
    Q(D + name + ".md", "std::" + name, summary, rank, INC, intro,
      tips or ["`float` / `double` / `long double` の版がある。", "引数が整数なら `double` として計算される。", "角度はラジアン。" if name in ("asinh", "acosh", "atanh") else "エラーは `errno` か浮動小数点例外で知らされる。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, ver=ver, hub=HUB, hubname="<cmath>", rj=f"cmath/{rjn or name}.html", cr=f"{CRB}{cr or name}",
      extra_inc=extra_inc or [])


X = ("x", "浮動小数点", "引数")
M("fabs", "浮動小数点の絶対値を返す。", "`std::abs` は整数にも小数にも使えますが、小数だけを明示したいときは `fabs` が使えます。C 由来の名前で、C++ では `abs` と同じ働きです。",
  "double fabs(double x);  // float / long double 版もある", [("x", "浮動小数点", "絶対値を求める値")], "`|x|`", 'std::println("{}", std::fabs(-3.5));', "3.5",
  "2 点の座標の差の大きさを調べる", ("整数に使って精度を失う", "整数には `std::abs` を使います。`fabs` は `double` へ変換して計算します。"), [("[`abs`](abs.md)", "整数にも使える")], ver=None, rank="sometimes", cr="fabs")
M("remquo", "割り算の余りと、商の下位ビットをいっしょに返す。", "`fmod` は余りだけを返します。`remquo` は余りに加えて、商の下位の数ビットも受け取れます。周期的な関数（`sin` など）で、どの象限にいるかを知りたいときに使います。余りは `x - n·y`（n は商に最も近い整数）です。",
  "double remquo(double x, double y, int* quo);", [("x, y", "浮動小数点", "割られる数・割る数"), ("quo", "int*", "商の下位ビットを受け取る場所")], "余り（`x - n·y`）", 'int q = 0;\ndouble r = std::remquo(10.0, 3.0, &q);\nstd::println("{} {}", r, q);', "1 3",
  "周期関数の引数を象限ごとに分ける", ("`fmod` と同じ余りだと思う", "`remquo` の余りは**最も近い整数**への丸めで決まるので、負になることがあります。`fmod` は 0 以上です。"), [("[`fmod`](fmod.md)", "切り捨て基準の余り"), ("[`remainder`](remainder.md)", "余りだけ")], cr="remquo")
M("fdim", "x − y が正ならその値、そうでなければ 0 を返す。", "「差があれば差、なければ 0」を `max(x - y, 0)` と書く代わりに、`fdim` が使えます。残りの体力やゲージの不足分を求めるときなどです。",
  "double fdim(double x, double y);", [("x, y", "浮動小数点", "x から y を引く")], "`max(x - y, 0)`", 'std::println("{} {}", std::fdim(5.0, 3.0), std::fdim(3.0, 5.0));', "2 0",
  "ダメージ計算で、防御を差し引いた最低 0 のダメージ", ("符号付きの差を期待する", "`fdim(3, 5)` は -2 ではなく 0 です。負の差が欲しいときは普通に引き算します。"), [("[`fmax`](fmax.md)", "大きいほうを選ぶ")], cr="fdim")
M("nan", "指定した文字列に対応する NaN（非数）を返す。", "NaN（Not a Number）は、「値がない」を表すために使われる特別な小数の値です。`std::nan(\"\")` で作れます。「未設定の浮動小数点」を表したいときに使いますが、比較が全部 `false` になるので扱いに注意が必要です。",
  "double nan(const char* tagp);", [("tagp", "文字列", "NaN の種類を示す文字列（普通は空文字列）")], "NaN", 'double v = std::nan("");\nstd::println("{}", std::isnan(v));', "true",
  "「まだ計算されていない」値の目印", ("`==` で NaN を調べる", "NaN は自分自身とも等しくありません。`std::isnan` で調べます。"), [("[`isnan`](isnan.md)", "NaN かを調べる")], cr="nan")
M("asinh", "双曲線逆正弦（sinh の逆関数）を返す。", "`sinh(x)` の逆の計算です。ゲームではほとんど使いませんが、物理や信号処理の式に出てきます。",
  "double asinh(double x);", [X], "`asinh(x)`", 'std::println("{:.4f}", std::asinh(1.0));', "0.8814", "物理の式の計算", ("定義域を気にしない", "`asinh` は全ての実数で定義されます。"), [("[`sinh`](sinh.md)", "逆の関数")], cr="asinh")
M("acosh", "双曲線逆余弦（cosh の逆関数）を返す。", "`cosh(x)` の逆の計算です。定義域は `x >= 1` で、それより小さい値では NaN になります。",
  "double acosh(double x);", [("x", "浮動小数点", "1 以上の値")], "`acosh(x)`", 'std::println("{:.4f}", std::acosh(2.0));', "1.3170", "物理の式の計算", ("1 未満を渡す", "定義域外では NaN が返ります。"), [("[`cosh`](cosh.md)", "逆の関数")], cr="acosh")
M("atanh", "双曲線逆正接（tanh の逆関数）を返す。", "`tanh(x)` の逆の計算です。定義域は `-1 < x < 1`、±1 では無限大になります。",
  "double atanh(double x);", [("x", "浮動小数点", "-1 〜 1 の値")], "`atanh(x)`", 'std::println("{:.4f}", std::atanh(0.5));', "0.5493", "値を非線形に引き伸ばす", ("範囲外を渡す", "絶対値が 1 を超えると NaN が返ります。"), [("[`tanh`](tanh.md)", "逆の関数")], cr="atanh")
M("erf", "誤差関数（正規分布の積分に関係する関数）を返す。", "正規分布の累積確率を求めるときに出てくる関数です。`erf(x)` は 0 から x までの積分を使った値で、-1 〜 1 の範囲を取ります。",
  "double erf(double x);", [X], "`erf(x)`", 'std::println("{:.4f}", std::erf(1.0));', "0.8427", "ガチャの確率や正規分布の累積を求める", ("相補誤差関数と取り違える", "`1 - erf(x)` は `erfc(x)` と等しいですが、x が大きいと `erfc` のほうが精度が高くなります。"), [("[`erfc`](erfc.md)", "相補誤差関数")], cr="erf")
M("erfc", "相補誤差関数（1 − erf）を返す。", "`1 - erf(x)` を、桁落ちなしで計算します。x が大きいとき、`erf(x)` は 1 に近すぎて引き算で精度が落ちるので、`erfc` を使います。",
  "double erfc(double x);", [X], "`1 - erf(x)`", 'std::println("{:.4f}", std::erfc(1.0));', "0.1573", "正規分布の裾の確率を求める", ("`1 - erf` で計算する", "x が大きいと桁落ちします。`erfc` を直接使います。"), [("[`erf`](erf.md)", "誤差関数")], cr="erfc")
M("tgamma", "ガンマ関数（階乗の一般化）を返す。", "整数 n のとき `tgamma(n)` は `(n-1)!` です。階乗を小数にまで広げた関数で、確率分布や組み合わせの計算に登場します。",
  "double tgamma(double x);", [X], "`Γ(x)`", 'std::println("{}", std::tgamma(5.0));', "24", "階乗を小数まで広げた計算", ("`tgamma(n)` を n! と思う", "`tgamma(n)` は `(n-1)!` です。5! を求めるなら `tgamma(6)` です。"), [("[`lgamma`](lgamma.md)", "ガンマ関数の対数")], cr="tgamma")
M("lgamma", "ガンマ関数の自然対数を返す。", "`tgamma(x)` は x が少し大きいだけで桁あふれします。そこで、その対数を直接計算する `lgamma` が使えます。大きな組み合わせの計算（二項係数など）で、対数のまま足し引きして最後に `exp` で戻します。",
  "double lgamma(double x);", [X], "`log(|Γ(x)|)`", 'std::println("{:.4f}", std::lgamma(5.0));', "3.1781", "大きな組み合わせの数を桁あふれなしで扱う", ("`tgamma` を `log` する", "桁あふれするので `lgamma` を直接使います。"), [("[`tgamma`](tgamma.md)", "ガンマ関数")], cr="lgamma")
M("llround", "四捨五入して long long にする。", "`round` は小数で結果を返しますが、整数がほしいときは `llround` が便利です。`lround` の `long long` 版で、大きな値でも安全です。",
  "long long llround(double x);", [X], "四捨五入した `long long`", 'std::println("{} {}", std::llround(2.5), std::llround(-2.5));', "3 -3", "ダメージ計算の最後の整数化", ("0.5 を偶数に丸めると思う", "`llround` は 0.5 を**絶対値の大きいほう**へ丸めます（2.5 → 3）。偶数丸めは `llrint` です。"), [("[`lround`](lround.md)", "long 版"), ("[`round`](round.md)", "小数で返す")], cr="round")
M("rint", "現在の丸めモードで整数に丸める（結果は小数）。", "丸めの規則を `fesetround` で切り替えられる環境では、`rint` はその規則で丸めます。既定は「最も近い偶数への丸め」で、2.5 は 2、3.5 は 4 になります。",
  "double rint(double x);", [X], "丸めた値（小数型）", 'std::println("{} {}", std::rint(2.5), std::rint(3.5));', "2 4", "丸めの偏りを避ける統計処理", ("四捨五入と同じだと思う", "既定は偶数丸めです。2.5 が 2 になります。四捨五入は `round` です。"), [("[`round`](round.md)", "四捨五入"), ("[`nearbyint`](nearbyint.md)", "例外を出さない版")], cr="rint")
M("lrint", "現在の丸めモードで整数に丸める（long で返す）。", "`rint` の結果を `long` で受け取る版です。丸めの規則は `rint` と同じです。",
  "long lrint(double x);", [X], "丸めた `long`", 'std::println("{} {}", std::lrint(2.5), std::lrint(3.5));', "2 4", "丸めた値を整数で受け取る", ("範囲外の値を渡す", "`long` に収まらない値は未定義の結果になります。"), [("[`rint`](rint.md)", "小数で返す版"), ("[`llrint`](llrint.md)", "long long 版")], cr="rint")
M("llrint", "現在の丸めモードで整数に丸める（long long で返す）。", "`lrint` の `long long` 版です。Windows のように `long` が 32 ビットの環境でも、大きな値を安全に扱えます。",
  "long long llrint(double x);", [X], "丸めた `long long`", 'std::println("{} {}", std::llrint(2.5), std::llrint(3.5));', "2 4", "大きな値の整数化", ("`long` と取り違える", "Windows では `long` は 32 ビットです。大きな値は `llrint` を使います。"), [("[`lrint`](lrint.md)", "long 版")], cr="rint")
M("scalbn", "x × 2ⁿ を、乗算を使わずに計算する。", "2 のべき乗倍は、指数部だけを書き換えれば済むので、乗算より正確で速く計算できます。`ldexp` と同じ働きですが、基数が `FLT_RADIX` の環境でも正しく動きます。",
  "double scalbn(double x, int n);", [("x", "浮動小数点", "元の値"), ("n", "int", "2 の指数")], "`x × 2ⁿ`", 'std::println("{}", std::scalbn(1.5, 3));', "12", "2 のべき乗倍のスケール", ("`pow(2, n)` で乗算する", "桁あふれしやすく、誤差も出ます。`scalbn` を使います。"), [("[`ldexp`](ldexp.md)", "同じ働き"), ("[`scalbln`](scalbln.md)", "指数が long")], cr="scalbn")
M("scalbln", "x × 2ⁿ を計算する（指数が long）。", "`scalbn` の、指数部分が `long` の版です。",
  "double scalbln(double x, long n);", [("x", "浮動小数点", "元の値"), ("n", "long", "2 の指数")], "`x × 2ⁿ`", 'std::println("{}", std::scalbln(1.5, 3));', "12", "2 のべき乗倍のスケール", ("`int` 版との違いを気にしない", "`n` が `int` の範囲に収まるなら `scalbn` で十分です。"), [("[`scalbn`](scalbn.md)", "指数が int")], cr="scalbn")
M("ilogb", "x の指数部（2 を底とした対数の整数部分）を int で返す。", "浮動小数点数は `仮数 × 2^指数` の形で持たれます。`ilogb(x)` は、その指数を整数で返します。正の数 x に対して `floor(log2(x))` と同じです。",
  "int ilogb(double x);", [("x", "浮動小数点", "0 以外の有限の値")], "指数部（`int`）", 'std::println("{} {}", std::ilogb(8.0), std::ilogb(10.0));', "3 3", "必要なビット数やミップマップの段数を求める", ("0 や NaN を渡す", "特別な値（`FP_ILOGB0` など）が返ります。"), [("[`logb`](logb.md)", "小数で返す版"), ("[`log2`](log2.md)", "対数そのもの")], cr="ilogb")
M("logb", "x の指数部を、浮動小数点で返す。", "`ilogb` と同じ値を、小数型で返します。無限大や 0 のときも、数学的に自然な値（±∞）を返します。",
  "double logb(double x);", [("x", "浮動小数点", "0 以外の有限の値")], "指数部（小数型）", 'std::println("{}", std::logb(8.0));', "3", "2 のべき乗の桁の大きさを調べる", ("`log2` と取り違える", "`logb` は指数部（整数値）を返します。`log2(10)` は 3.32… ですが、`logb(10)` は 3 です。"), [("[`ilogb`](ilogb.md)", "int で返す版")], cr="logb")
M("nextafter", "x の次に表せる浮動小数点数を返す（y の方向へ）。", "浮動小数点数は連続ではなく、飛び飛びの値です。`nextafter(x, y)` は、x から y のほうへ 1 つ進んだ、隣の表せる値を返します。許容誤差をぎりぎりまで詰めたい場面で使います。",
  "double nextafter(double x, double y);", [("x", "浮動小数点", "出発点"), ("y", "浮動小数点", "向かう先")], "x の隣の値（y の方向）", '#include <limits>\n#include <print>\nstd::println("{}", std::nextafter(1.0, 2.0) - 1.0 == std::numeric_limits<double>::epsilon());'.split("\n", 2)[2], "true",
  "「1 より少しだけ大きい値」をつくる", ("`x + epsilon` と同じだと思う", "x が 1 から離れるほど、隣の値との差は変わります。`epsilon` は 1 付近の差です。"), [("[`nexttoward`](nexttoward.md)", "y が long double")], cr="nextafter", extra_inc=["limits"])
M("nexttoward", "x の次に表せる値を返す（向かう先が long double）。", "`nextafter` の、向かう先 `y` が `long double` の版です。`float` や `double` の隣を、高い精度の `y` に向かって探せます。",
  "float nexttoward(float x, long double y);", [("x", "浮動小数点", "出発点"), ("y", "long double", "向かう先")], "x の隣の値（y の方向）", 'std::println("{}", std::nexttoward(1.0f, 2.0L) - 1.0f == std::numeric_limits<float>::epsilon());', "true",
  "float の隣の値を調べる", ("`float` に `double` を入れて精度が違う", "戻りの型は x の型です。`y` だけが `long double` です。"), [("[`nextafter`](nextafter.md)", "y が同じ型")], cr="nexttoward", extra_inc=["limits"])
M("fpclassify", "浮動小数点数の種類（0・正規数・NaN など）を判定する。", "`isnan` や `isinf` など個別の関数でもできますが、`fpclassify` は 1 回で種類を分類します。結果は `FP_ZERO`・`FP_NORMAL`・`FP_SUBNORMAL`・`FP_INFINITE`・`FP_NAN` のどれかです。",
  "int fpclassify(double x);", [X], "`FP_NAN`・`FP_INFINITE`・`FP_ZERO`・`FP_SUBNORMAL`・`FP_NORMAL` のどれか", 'std::println("{}", std::fpclassify(0.0) == FP_ZERO);\nstd::println("{}", std::fpclassify(1.0) == FP_NORMAL);', "true\ntrue",
  "計算結果の異常値のデバッグ", ("`int` の比較を忘れる", "戻り値は列挙ではなく `int` です。`FP_xxx` のマクロと比べます。"), [("[`isnan`](isnan.md)", "NaN だけ"), ("[`isinf`](isinf.md)", "無限大だけ"), ("[`isnormal`](isnormal.md)", "正規数かどうか")], cr="fpclassify")
M("isnormal", "正規数（0・無限大・NaN・非正規数以外）かを判定する。", "計算が極端に小さい値（非正規数）になると、精度が落ちて遅くなります。`isnormal` は、通常の精度で扱える数かを調べます。",
  "bool isnormal(double x);", [X], "正規数なら `true`", 'std::println("{} {}", std::isnormal(1.0), std::isnormal(0.0));', "true false", "異常な値が計算に混ざっていないか検査する", ("0 を正規数と思う", "0 は正規数ではありません。`false` になります。"), [("[`fpclassify`](fpclassify.md)", "種類を分類する"), ("[`isfinite`](isfinite.md)", "有限かを判定する")], cr="isnormal")
for nm, op, expr, res, what in [
    ("isgreater", ">", "std::isgreater(2.0, 1.0)", "true", "x が y より大きいか"),
    ("isgreaterequal", ">=", "std::isgreaterequal(2.0, 2.0)", "true", "x が y 以上か"),
    ("isless", "<", "std::isless(1.0, 2.0)", "true", "x が y より小さいか"),
    ("islessequal", "<=", "std::islessequal(2.0, 2.0)", "true", "x が y 以下か"),
    ("islessgreater", "<  または  >", "std::islessgreater(1.0, 2.0)", "true", "x が y より小さいか大きいか（等しくも非順序でもない）"),
    ("isunordered", "順序なし", "std::isunordered(std::nan(\"\"), 1.0)", "true", "どちらかが NaN で、大小を比べられないか")]:
    M(nm, f"浮動小数点を比べる（{what}）。NaN でも例外を出さない。", f"NaN が混ざった比較は、普通の `{op.split()[0]}` では浮動小数点例外が起きる環境があります。`{nm}` は、NaN があっても例外を出さずに結果（`false`）を返す、安全な比較です。",
      f"bool {nm}(double x, double y);", [("x, y", "浮動小数点", "比べる 2 つの値")], f"{what}", f'std::println("{{}}", {expr});', res,
      "NaN が混ざりうる計算の比較", ("普通の比較で十分な場面で使う", "NaN の心配がなければ、`<` `>` のほうが読みやすいです。"), [("[`isnan`](isnan.md)", "NaN の判定")], cr=nm)

# ---- 特殊関数（C++17）
SP = dict(ver=V17, rank="rare")
M("assoc_laguerre", "ラゲール陪多項式を求める。", "量子力学や数値解析の式に登場する、特殊関数の 1 つです。ゲームではほとんど使いません。",
  "double assoc_laguerre(unsigned n, unsigned m, double x);", [("n, m", "unsigned", "次数"), ("x", "浮動小数点", "x ≥ 0")], "`L_n^m(x)`", 'std::println("{}", std::assoc_laguerre(1, 1, 0.5));', "1.5", "数値解析", ("負の x を渡す", "x は 0 以上です。"), [("[`laguerre`](laguerre.md)", "m = 0 の場合")], cr="assoc_laguerre", **SP)
M("assoc_legendre", "ルジャンドル陪関数を求める。", "球面調和関数などに登場する特殊関数です。`assoc_legendre(l, m, x)` は、条件 m ≤ l、−1 ≤ x ≤ 1 で定義されます。",
  "double assoc_legendre(unsigned l, unsigned m, double x);", [("l, m", "unsigned", "次数（m ≤ l）"), ("x", "浮動小数点", "-1 〜 1")], "`P_l^m(x)`", 'std::println("{:.4f}", std::assoc_legendre(1, 1, 0.6));', "0.8000", "球面上の計算", ("標準と他の定義の符号を取り違える", "C++ の定義は、数学で使う (−1)^m の符号（Condon–Shortley 位相）を**含みません**。"), [("[`legendre`](legendre.md)", "m = 0 の場合")], cr="assoc_legendre", **SP)
M("beta", "ベータ関数を求める。", "`B(x, y) = Γ(x)Γ(y) / Γ(x+y)`。確率分布（ベータ分布）の係数に登場します。",
  "double beta(double x, double y);", [("x, y", "浮動小数点", "正の値")], "`B(x, y)`", 'std::println("{:.4f}", std::beta(2.0, 3.0));', "0.0833", "確率分布の係数", ("0 以下を渡す", "引数は正の数です。"), [("[`tgamma`](tgamma.md)", "ガンマ関数")], cr="beta", **SP)
M("comp_ellint_1", "第 1 種完全楕円積分を求める。", "振り子の周期など、楕円の積分に登場する関数です。引数 k の範囲は −1 〜 1 です。",
  "double comp_ellint_1(double k);", [("k", "浮動小数点", "離心率 −1 〜 1")], "`K(k)`", 'std::println("{:.4f}", std::comp_ellint_1(0.0));', "1.5708", "振り子の周期の計算", ("範囲外を渡す", "|k| > 1 では定義されません。"), [("[`comp_ellint_2`](comp_ellint_2.md)", "第 2 種"), ("[`ellint_1`](ellint_1.md)", "不完全版")], cr="comp_ellint_1", **SP)
M("comp_ellint_2", "第 2 種完全楕円積分を求める。", "楕円の周の長さの計算に登場する関数です。",
  "double comp_ellint_2(double k);", [("k", "浮動小数点", "離心率 −1 〜 1")], "`E(k)`", 'std::println("{:.4f}", std::comp_ellint_2(0.0));', "1.5708", "楕円の周の長さ", ("範囲外を渡す", "|k| > 1 では定義されません。"), [("[`comp_ellint_1`](comp_ellint_1.md)", "第 1 種")], cr="comp_ellint_2", **SP)
M("comp_ellint_3", "第 3 種完全楕円積分を求める。", "楕円積分のうち、パラメータ `nu` をもつ 3 番目の種類です。物理の式に登場します。",
  "double comp_ellint_3(double k, double nu);", [("k", "浮動小数点", "離心率 −1 〜 1"), ("nu", "浮動小数点", "特性数")], "`Π(nu, k)`", 'std::println("{:.4f}", std::comp_ellint_3(0.0, 0.0));', "1.5708", "物理の計算", ("範囲外を渡す", "|k| > 1 では定義されません。"), [("[`comp_ellint_1`](comp_ellint_1.md)", "第 1 種")], cr="comp_ellint_3", **SP)
M("cyl_bessel_i", "第 1 種変形ベッセル関数を求める。", "円筒座標の波動方程式などの解に出てくる関数です。",
  "double cyl_bessel_i(double nu, double x);", [("nu", "浮動小数点", "次数（0 以上）"), ("x", "浮動小数点", "0 以上")], "`I_nu(x)`", 'std::println("{:.4f}", std::cyl_bessel_i(0.0, 1.0));', "1.2661", "波動の解析", ("負の x を渡す", "x は 0 以上です。"), [("[`cyl_bessel_j`](cyl_bessel_j.md)", "第 1 種ベッセル関数")], cr="cyl_bessel_i", **SP)
M("cyl_bessel_j", "第 1 種ベッセル関数を求める。", "円形の膜の振動や、波の回折などの解に出てくる関数です。",
  "double cyl_bessel_j(double nu, double x);", [("nu", "浮動小数点", "次数（0 以上）"), ("x", "浮動小数点", "0 以上")], "`J_nu(x)`", 'std::println("{:.4f}", std::cyl_bessel_j(0.0, 1.0));', "0.7652", "円形の振動の解析", ("負の x を渡す", "x は 0 以上です。"), [("[`cyl_neumann`](cyl_neumann.md)", "第 2 種ベッセル関数")], cr="cyl_bessel_j", **SP)
M("cyl_bessel_k", "第 2 種変形ベッセル関数を求める。", "遠くで減衰する波などの解に出てくる関数です。",
  "double cyl_bessel_k(double nu, double x);", [("nu", "浮動小数点", "次数（0 以上）"), ("x", "浮動小数点", "正の値")], "`K_nu(x)`", 'std::println("{:.4f}", std::cyl_bessel_k(0.0, 1.0));', "0.4210", "減衰する波の解析", ("0 を渡す", "x = 0 では発散します。"), [("[`cyl_bessel_i`](cyl_bessel_i.md)", "第 1 種変形ベッセル関数")], cr="cyl_bessel_k", **SP)
M("cyl_neumann", "ノイマン関数（第 2 種ベッセル関数）を求める。", "ベッセル関数の、もう 1 つの独立な解です。x = 0 で発散します。",
  "double cyl_neumann(double nu, double x);", [("nu", "浮動小数点", "次数（0 以上）"), ("x", "浮動小数点", "正の値")], "`N_nu(x)`（`Y_nu(x)`）", 'std::println("{:.4f}", std::cyl_neumann(0.0, 1.0));', "0.0883", "波動の解析", ("0 を渡す", "x = 0 では発散します。"), [("[`cyl_bessel_j`](cyl_bessel_j.md)", "第 1 種ベッセル関数")], cr="cyl_neumann", **SP)
M("ellint_1", "第 1 種不完全楕円積分を求める。", "完全版 `comp_ellint_1` の、積分範囲 `phi` を指定できる版です。",
  "double ellint_1(double k, double phi);", [("k", "浮動小数点", "離心率 −1 〜 1"), ("phi", "浮動小数点", "角度（ラジアン）")], "`F(k, phi)`", 'std::println("{:.4f}", std::ellint_1(0.0, 1.0));', "1.0000", "振り子の運動の解析", ("完全版と取り違える", "`phi = π/2` のとき、`comp_ellint_1(k)` と同じ値になります。"), [("[`comp_ellint_1`](comp_ellint_1.md)", "完全版")], cr="ellint_1", **SP)
M("ellint_2", "第 2 種不完全楕円積分を求める。", "完全版 `comp_ellint_2` の、積分範囲 `phi` を指定できる版です。",
  "double ellint_2(double k, double phi);", [("k", "浮動小数点", "離心率 −1 〜 1"), ("phi", "浮動小数点", "角度（ラジアン）")], "`E(k, phi)`", 'std::println("{:.4f}", std::ellint_2(0.0, 1.0));', "1.0000", "楕円弧の長さ", ("完全版と取り違える", "`phi = π/2` のとき、`comp_ellint_2(k)` と同じ値になります。"), [("[`comp_ellint_2`](comp_ellint_2.md)", "完全版")], cr="ellint_2", **SP)
M("ellint_3", "第 3 種不完全楕円積分を求める。", "完全版 `comp_ellint_3` の、積分範囲 `phi` を指定できる版です。",
  "double ellint_3(double k, double nu, double phi);", [("k", "浮動小数点", "離心率 −1 〜 1"), ("nu", "浮動小数点", "特性数"), ("phi", "浮動小数点", "角度（ラジアン）")], "`Π(nu, k, phi)`", 'std::println("{:.4f}", std::ellint_3(0.0, 0.0, 1.0));', "1.0000", "物理の計算", ("完全版と取り違える", "`phi = π/2` のとき、`comp_ellint_3(k, nu)` と同じ値になります。"), [("[`comp_ellint_3`](comp_ellint_3.md)", "完全版")], cr="ellint_3", **SP)
M("expint", "指数積分 Ei(x) を求める。", "指数と逆数が組み合わさった積分の関数です。放射や熱の計算に出てきます。",
  "double expint(double x);", [X], "`Ei(x)`", 'std::println("{:.4f}", std::expint(1.0));', "1.8951", "光の減衰の積分", ("x = 0 を渡す", "x = 0 では −∞ になります。"), [("[`exp`](exp.md)", "指数関数")], cr="expint", **SP)
M("hermite", "エルミート多項式を求める。", "量子力学の調和振動子の解などに登場する多項式です。",
  "double hermite(unsigned n, double x);", [("n", "unsigned", "次数"), ("x", "浮動小数点", "値")], "`H_n(x)`", 'std::println("{}", std::hermite(2, 1.0));', "2", "確率論の展開式", ("次数が大きすぎる", "n が大きいと計算が不安定になります。"), [("[`laguerre`](laguerre.md)", "ラゲール多項式")], cr="hermite", **SP)
M("laguerre", "ラゲール多項式を求める。", "量子力学の水素原子の解などに登場する多項式です。",
  "double laguerre(unsigned n, double x);", [("n", "unsigned", "次数"), ("x", "浮動小数点", "x ≥ 0")], "`L_n(x)`", 'std::println("{}", std::laguerre(2, 1.0));', "-0.5", "数値解析", ("負の x を渡す", "x は 0 以上です。"), [("[`assoc_laguerre`](assoc_laguerre.md)", "陪多項式")], cr="laguerre", **SP)
M("legendre", "ルジャンドル多項式を求める。", "球面上の計算や数値積分（ガウス求積）に登場する多項式です。",
  "double legendre(unsigned l, double x);", [("l", "unsigned", "次数"), ("x", "浮動小数点", "-1 〜 1")], "`P_l(x)`", 'std::println("{}", std::legendre(2, 0.5));', "-0.125", "球面調和関数による照明の近似", ("範囲外を渡す", "|x| > 1 では定義されません。"), [("[`assoc_legendre`](assoc_legendre.md)", "陪関数")], cr="legendre", **SP)
M("riemann_zeta", "リーマンのゼータ関数を求める。", "数論や統計物理に登場する関数です。`riemann_zeta(2)` は `π²/6` です。",
  "double riemann_zeta(double x);", [X], "`ζ(x)`", 'std::println("{:.4f}", std::riemann_zeta(2.0));', "1.6449", "数論の計算", ("x = 1 を渡す", "x = 1 で発散します。"), [("[`tgamma`](tgamma.md)", "ガンマ関数")], cr="riemann_zeta", **SP)
M("sph_bessel", "球ベッセル関数（第 1 種）を求める。", "球対称な波の解に出てくる関数です。`sph_bessel(0, x)` は `sin(x) / x` です。",
  "double sph_bessel(unsigned n, double x);", [("n", "unsigned", "次数"), ("x", "浮動小数点", "0 以上")], "`j_n(x)`", 'std::println("{:.4f}", std::sph_bessel(0, 1.0));', "0.8415", "球状の波の解析", ("負の x を渡す", "x は 0 以上です。"), [("[`sph_neumann`](sph_neumann.md)", "球ノイマン関数")], cr="sph_bessel", **SP)
M("sph_legendre", "球面調和関数の θ 部分を求める。", "球面上の関数を展開する球面調和関数のうち、角度 θ に依存する部分を求めます。環境光の球面調和関数（SH）による近似の理屈に登場します。",
  "double sph_legendre(unsigned l, unsigned m, double theta);", [("l, m", "unsigned", "次数（m ≤ l）"), ("theta", "浮動小数点", "角度（ラジアン）")], "球面調和関数の θ 部分", 'std::println("{:.4f}", std::sph_legendre(0, 0, 0.0));', "0.2821", "環境光の球面調和関数", ("角度の単位を度にする", "角度はラジアンです。"), [("[`assoc_legendre`](assoc_legendre.md)", "ルジャンドル陪関数")], cr="sph_legendre", **SP)
M("sph_neumann", "球ノイマン関数を求める。", "球ベッセル関数のもう 1 つの独立な解です。`sph_neumann(0, x)` は `-cos(x) / x` です。",
  "double sph_neumann(unsigned n, double x);", [("n", "unsigned", "次数"), ("x", "浮動小数点", "正の値")], "`n_n(x)`", 'std::println("{:.4f}", std::sph_neumann(0, 1.0));', "-0.5403", "球状の波の解析", ("0 を渡す", "x = 0 では発散します。"), [("[`sph_bessel`](sph_bessel.md)", "球ベッセル関数")], cr="sph_neumann", **SP)

# ---- マクロ
for nm, what, intro, body, out in [
    ("HUGE_VAL", "double の無限大を表すマクロ。", "古い C の関数は、範囲を超えた結果を `HUGE_VAL`（`double` の正の無限大）で知らせました。比較の相手としては `std::isinf` のほうが読みやすいです。", 'std::println("{}", HUGE_VAL);', "inf"),
    ("INFINITY", "float の無限大を表すマクロ。", "`float` の正の無限大を表します。`-INFINITY` で負の無限大です。除算で作る代わりに、意図を明示して書けます。", 'std::println("{} {}", INFINITY, -INFINITY);', "inf -inf"),
    ("NAN", "float の NaN（非数）を表すマクロ。", "「値がない」ことを `float` の NaN で表すためのマクロです。比較は常に偽になるので、判定は `std::isnan` を使います。", 'std::println("{}", std::isnan(NAN));', "true"),
    ("math_errhandling", "数学関数のエラーの知らせ方を表すマクロ。", "数学関数が範囲外の入力などを受けたとき、`errno` を設定するか、浮動小数点例外を立てるかは処理系で決まります。`math_errhandling` は、その方式を表すビットフラグ（`MATH_ERRNO`・`MATH_ERREXCEPT`）です。", 'std::println("{}", (math_errhandling & (MATH_ERRNO | MATH_ERREXCEPT)) != 0);', "true")]:
    Q(D + ("nan_macro" if nm == "NAN" else nm.lower()) + ".md", nm, what, "rare", ["cmath", "print"], intro,
      ["マクロ（式）。", "`std::` を付けずに書く。", "比較は専用関数（`isnan` など）で。"], f"#define {nm} /* 実装定義 */", [], "マクロの値", out=out, body=body,
      use="異常値の目印や、エラー処理の分岐に使う", miss=("値を `==` で比べる", "NaN は `==` で比べられません。`std::isnan`・`std::isinf` を使います。" if nm in ("NAN", "INFINITY", "HUGE_VAL") else "`math_errhandling` は、環境で値が変わります。両方のビットを確かめます。"),
      sim=[("[`isnan`](isnan.md)", "NaN の判定"), ("[`isinf`](isinf.md)", "無限大の判定")], cx="なし", hub=HUB, hubname="<cmath>", rj="cmath/" + nm.lower() + ".html", cr="numeric/math/" + nm)

if __name__ == "__main__":
    flush_hubs()
