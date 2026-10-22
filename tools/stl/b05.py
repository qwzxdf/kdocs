"""バッチ 5: ratio / complex / 文字列の別名 / 文字列↔数値 / ctime / random の未登録分。"""
from mk import *  # noqa: F401,F403

# ================= ratio =================
R = "numeric/ratio/"
RI = "[`std::ratio`](../ratio.md) を先に読んでください。"
RHUB = "numeric/ratio.md"

for nm, op, expr, res, meaning in [
    ("ratio_add", "足し算", "std::ratio_add<std::ratio<1, 3>, std::ratio<1, 6>>", "1 2", "1/3 + 1/6 = 1/2"),
    ("ratio_subtract", "引き算", "std::ratio_subtract<std::ratio<1, 2>, std::ratio<1, 3>>", "1 6", "1/2 - 1/3 = 1/6"),
    ("ratio_multiply", "かけ算", "std::ratio_multiply<std::ratio<2, 3>, std::ratio<3, 4>>", "1 2", "2/3 × 3/4 = 1/2"),
    ("ratio_divide", "割り算", "std::ratio_divide<std::ratio<1, 2>, std::ratio<1, 4>>", "2 1", "(1/2) ÷ (1/4) = 2")]:
    P(R + nm + ".md", "std::" + nm, f"2 つの `ratio` の{op}を、コンパイル時に計算して `ratio` で返す。", "rare", "ratio",
      f"単位の換算や精度の計算で、分数どうしの{op}をコンパイル時に済ませておきたいことがあります。`{nm}<R1, R2>` は、約分された結果の `ratio` 型をつくります。実行時のコストはありません。",
      ["結果は自動で約分される。", "`::num` と `::den` で分子と分母を取り出す。", "計算がオーバーフローするとコンパイルエラーになる。"],
      [("単位の係数をコンパイル時に作る", f"`{nm}<A, B>::num`")],
      ("オーバーフローを気にしない", "分子や分母が `intmax_t` に入らないとコンパイルエラーです。極端に大きな値を組み合わせないようにします。"),
      [("[`std::ratio`](../ratio.md)", "分数の型"), ("[`ratio_equal`](ratio_equal.md)", "等しいか比べる")],
      [f"ratio の{op}（コンパイル時）", "結果は約分される", "num / den で取り出す"],
      sig=f"template <class R1, class R2>\nusing {nm} = ratio</* 結果の分子 */, /* 結果の分母 */>;",
      args=[("R1, R2", "ratio", "計算する 2 つの `ratio`")], ret=f"{meaning} を表す `ratio`", cx="コンパイル時のみ",
      code=f"""#include <ratio>
#include <print>

int main() {{
  using R = {expr};
  std::println("{{}} {{}}", R::num, R::den);
}}""", out=res, ver=("11", "C++11"), info=RI, hub=RHUB, hubname="std::ratio", rj=f"ratio/{nm}.html", cr="numeric/ratio/ratio_add")

for nm, op, expr, res, meaning in [
    ("ratio_equal", "==", "std::ratio_equal<std::ratio<1, 2>, std::ratio<2, 4>>::value", "true", "等しいか"),
    ("ratio_not_equal", "!=", "std::ratio_not_equal<std::ratio<1, 2>, std::ratio<1, 3>>::value", "true", "等しくないか"),
    ("ratio_less", "<", "std::ratio_less<std::ratio<1, 3>, std::ratio<1, 2>>::value", "true", "小さいか"),
    ("ratio_less_equal", "<=", "std::ratio_less_equal<std::ratio<1, 2>, std::ratio<1, 2>>::value", "true", "以下か"),
    ("ratio_greater", ">", "std::ratio_greater<std::ratio<1, 2>, std::ratio<1, 3>>::value", "true", "大きいか"),
    ("ratio_greater_equal", ">=", "std::ratio_greater_equal<std::ratio<1, 3>, std::ratio<1, 2>>::value", "false", "以上か")]:
    P(R + nm + ".md", "std::" + nm, f"2 つの `ratio` を `{op}` で比べる（コンパイル時）。", "rare", "ratio",
      f"単位の大きさを比べたいとき、分数の通分をして比べる必要はありません。`{nm}<R1, R2>::value` が、`R1 {op} R2` をコンパイル時に計算します。`static_assert` と組み合わせると、単位の前提をコンパイル時に確認できます。",
      ["`::value` が `bool` の定数。", "約分されていなくても、値として比べられる（`1/2` と `2/4` は等しい）。", "`_v` 版（C++17）もある。"],
      [("単位の前提をコンパイル時に確認", f"`static_assert(std::{nm}_v<A, B>);`")],
      ("文字列として比べたつもりになる", "約分前の形が違っても、値が同じなら等しいと判定されます。"),
      [("[`std::ratio`](../ratio.md)", "分数の型"), ("[`ratio_add`](ratio_add.md)", "足し算")],
      [f"ratio を {op} で比べる（コンパイル時）", "::value が bool", "static_assert に使える"],
      sig=f"template <class R1, class R2>\nstruct {nm} : bool_constant</* R1 {op} R2 */> {{}};\ntemplate <class R1, class R2>\ninline constexpr bool {nm}_v = {nm}<R1, R2>::value;",
      args=[("R1, R2", "ratio", "比べる 2 つの `ratio`")], ret=f"`R1 {op} R2` なら `true`（{meaning}）", cx="コンパイル時のみ",
      code=f"""#include <ratio>
#include <print>

int main() {{
  std::println("{{}}", {expr});
}}""", out=res, ver=("11", "C++11"), info=RI, hub=RHUB, hubname="std::ratio", rj=f"ratio/{nm}.html", cr="numeric/ratio/ratio_equal")

for nm, n, d, val in [("nano", 1, 10**9, "10 億分の 1"), ("micro", 1, 10**6, "100 万分の 1"), ("milli", 1, 1000, "1000 分の 1"), ("centi", 1, 100, "100 分の 1"),
                      ("deci", 1, 10, "10 分の 1"), ("deca", 10, 1, "10 倍"), ("hecto", 100, 1, "100 倍"), ("kilo", 1000, 1, "1000 倍"),
                      ("mega", 10**6, 1, "100 万倍"), ("giga", 10**9, 1, "10 億倍"), ("tera", 10**12, 1, "1 兆倍"), ("peta", 10**15, 1, "1000 兆倍"), ("exa", 10**18, 1, "100 京倍")]:
    P(R + nm + ".md", "std::" + nm, f"SI 接頭辞「{nm}」（{val}）を表す `ratio` の別名。", "rare", "ratio",
      f"長さ・時間・容量などの単位に「{nm}」をつけたいとき、`1/{d}` のような分数を自分で書くのはミスのもとです。`std::{nm}` は、SI 接頭辞 {nm}（{val}）をそのまま表す `ratio` の別名です。`std::chrono::duration` の単位の指定にも使います。",
      [f"中身は `std::ratio<{n}, {d}>`。", "`::num` と `::den` で分子と分母を取り出す。", "`duration<double, std::milli>` のように単位として使う。"],
      [("ミリ秒の duration を作る", "`std::chrono::duration<int, std::milli>`")],
      ("接頭辞の向きを取り違える", f"`{nm}` は {val}です。「小さい単位」か「大きい単位」かを、倍率で確かめます。"),
      [("[`std::ratio`](../ratio.md)", "分数の型"), ("[`std::chrono::duration`](../../utilities/chrono/duration.md)", "時間の長さ")],
      [f"SI 接頭辞 {nm} = {val}", "ratio の別名", "duration の単位に使う"],
      sig=f"using {nm} = ratio<{n}, {d}>;  // 実装により intmax_t に収まらない場合は定義されない（yotta など）",
      args=[], ret=f"{val}を表す `ratio`", cx="コンパイル時のみ",
      code=f"""#include <ratio>
#include <print>

int main() {{
  std::println("{{}} {{}}", std::{nm}::num, std::{nm}::den);
}}""", out=f"{n} {d}", ver=("11", "C++11"), info=RI, hub=RHUB, hubname="std::ratio", rj="ratio/ratio.html", cr="numeric/ratio/ratio")

# ================= complex =================
CX = "numeric/complex/"
CI = "[`std::complex`](../complex.md) を先に読んでください。"
CHUB = "numeric/complex.md"
for nm, what, intro, sig, code, out, rj in [
    ("real", "複素数の実部を取り出す。", "複素数 `a + bi` の `a`（実部）を取り出すには、`z.real()` というメンバ関数と、`std::real(z)` という関数の 2 通りがあります。関数版は、`double` などの普通の数にも使えるので、テンプレートで型を問わず書けます。",
     "template <class T> constexpr T real(const complex<T>& z);\nconstexpr T complex<T>::real() const;", """#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  std::println("{} {}", std::real(z), z.real());
}""", "3 3", "real"),
    ("imag", "複素数の虚部を取り出す。", "複素数 `a + bi` の `b`（虚部）を取り出します。`z.imag()` と `std::imag(z)` の 2 通りがあります。2D の回転や波の計算で、実部と虚部を座標として使うときに便利です。",
     "template <class T> constexpr T imag(const complex<T>& z);\nconstexpr T complex<T>::imag() const;", """#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  std::println("{} {}", std::imag(z), z.imag());
}""", "4 4", "imag"),
    ("arg", "複素数の偏角（実軸からの角度）をラジアンで返す。", "複素数を平面の点 `(実部, 虚部)` と見ると、原点からの向きが角度になります。`std::arg(z)` は、その角度（−π 〜 π）をラジアンで返し、`atan2(虚部, 実部)` と同じ値です。",
     "template <class T> T arg(const complex<T>& z);", """#include <complex>
#include <print>

int main() {
  std::complex<double> z{1.0, 1.0};
  std::println("{:.4f}", std::arg(z));
}""", "0.7854", "arg"),
    ("norm", "複素数の大きさの 2 乗を返す。", "複素数の大きさ `|z|` は `sqrt(a² + b²)` ですが、比べるだけなら平方根は不要です。`std::norm(z)` は `a² + b²` を返し、`sqrt` を使わない分だけ速く計算できます。",
     "template <class T> T norm(const complex<T>& z);", """#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  std::println("{} {}", std::norm(z), std::abs(z));
}""", "25 5", "norm"),
    ("conj", "共役複素数（虚部の符号を反転したもの）を返す。", "複素数 `a + bi` の共役は `a - bi` です。2D の回転を打ち消したいとき（逆回転）や、複素数の割り算の計算に使います。",
     "template <class T> complex<T> conj(const complex<T>& z);", """#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  auto c = std::conj(z);
  std::println("{} {}", c.real(), c.imag());
}""", "3 -4", "conj"),
    ("proj", "複素数をリーマン球面への射影に直す（無限大の扱いをそろえる）。", "複素数に無限大が混ざると、`(inf, 1)` と `(inf, -1)` のように、同じ「無限遠点」でも表現が何通りもできます。`std::proj(z)` は、有限の値はそのまま、無限大を含むものを `(inf, ±0)` の 1 つの形にそろえます。",
     "template <class T> complex<T> proj(const complex<T>& z);", """#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  auto p = std::proj(z);
  std::println("{} {}", p.real(), p.imag());
}""", "3 4", "proj"),
    ("polar", "大きさと角度から複素数を作る。", "回転や波の計算では、「大きさ r と角度 θ」の形（極形式）で考えるほうが自然なことがあります。`std::polar(r, theta)` は、その極形式から `r·(cosθ + i·sinθ)` の複素数を作ります。",
     "template <class T> complex<T> polar(const T& rho, const T& theta = T());", """#include <complex>
#include <numbers>
#include <print>

int main() {
  auto z = std::polar(2.0, std::numbers::pi / 2);
  std::println("{:.1f} {:.1f}", z.real(), z.imag());
}""", "0.0 2.0", "polar")]:
    P(CX + nm + ".md", "std::" + nm, what, "rare", "complex", intro,
      ["メンバ関数と同名の自由関数がある。" if nm in ("real", "imag") else "引数は `std::complex<T>`。", "ゲームでは 2D の回転や周期的な波の計算で登場する。", "`float` / `double` / `long double` で使える。"],
      [("2D の向きと回転", f"`std::{nm}(z)`")], ("float の変数に double を混ぜる", "`complex<float>` に `double` の値を混ぜると型が合わずコンパイルエラーになります。型をそろえます。"),
      [("[`std::complex`](../complex.md)", "複素数の型")], [what.rstrip("。"), "std::complex の関数", "2D の回転で使える"],
      sig=sig, args=[("z", "complex<T>", "対象の複素数")] if nm != "polar" else [("rho", "T", "大きさ"), ("theta", "T", "角度（ラジアン）")], ret=what.rstrip("。") + "結果", cx="定数",
      code=code, out=out, info=CI, hub=CHUB, hubname="std::complex", rj=f"complex/{rj}.html", cr=f"numeric/complex/{rj}")

# ================= 文字列の別名 =================
S = "containers/"
SI = "[`std::string`](string.md) を先に読んでください。"
for nm, ch, lit, code, out, intro in [
    ("wstring", "wchar_t", "L", '  std::wstring s = L"abc";\n  std::println("{}", s.size());', "3",
     "Windows の API は `wchar_t`（UTF-16）の文字列を使います。`std::wstring` は、その `wchar_t` の並びを扱う文字列です。`std::string` と同じ関数がそのまま使えます。"),
    ("u8string", "char8_t", "u8", '  std::u8string s = u8"abc";\n  std::println("{}", s.size());', "3",
     "UTF-8 の文字列であることを型で示したいときに使います。`char8_t` は C++20 で追加された、UTF-8 のコード単位の型です。`std::string` との相互の自動変換はありません。"),
    ("u16string", "char16_t", "u", '  std::u16string s = u"あい😀";\n  std::println("{}", s.size());', "4",
     "UTF-16 の文字列です。`あ` や `い` は 1 コード単位、絵文字などは 2 コード単位（サロゲートペア）になります。`size()` は文字数ではなく、コード単位の数です。"),
    ("u32string", "char32_t", "U", '  std::u32string s = U"あい😀";\n  std::println("{}", s.size());', "3",
     "UTF-32 の文字列です。1 コード単位が 1 つのコードポイントなので、`size()` が「文字数」（コードポイント数）と一致します。メモリは多く使います。")]:
    P(S + nm + ".md", "std::" + nm, f"`{ch}` を文字の型にもつ文字列。", "rare", "string", intro,
      [f"`std::basic_string<{ch}>` の別名。", f"文字列リテラルは `{lit}\"...\"` と書く。", "`std::string` と同じ関数が使える。"],
      [("プラットフォームの API に渡す", f"`std::{nm}`")], ("文字列の長さ = 文字数だと思う", "`size()` は**コード単位**の数です。サロゲートペアや結合文字が入ると、見た目の文字数と一致しません。"),
      [("[`std::string`](string.md)", "char の文字列"), ("[`basic_string`](basic_string.md)", "元になるテンプレート")],
      [f"{ch} の文字列", "std::string と同じ使い方", "size() はコード単位の数"],
      sig=f"using {nm} = basic_string<{ch}>;", args=[], ret=f"`{nm}` の値", cx="string と同じ",
      code="#include <print>\n#include <string>\n\nint main() {\n" + code + "\n}", out=out, ver=("20", "C++20") if nm == "u8string" else ("11", "C++11"),
      info=SI, rj="string/basic_string.html", cr="string/basic_string")

for nm, ch, lit, code, out, intro in [
    ("wstring_view", "wchar_t", "L", '  std::wstring_view v = L"abc";\n  std::println("{}", v.size());', "3", "`wstring` の中身を、コピーせずに見るだけの型です。Windows の API に渡す文字列を、関数の引数で受けるときに使います。"),
    ("u8string_view", "char8_t", "u8", '  std::u8string_view v = u8"abc";\n  std::println("{}", v.size());', "3", "`u8string` を、コピーせずに見るだけの型です。UTF-8 であることを型で示した文字列を、関数の引数で受けるときに使います。"),
    ("u16string_view", "char16_t", "u", '  std::u16string_view v = u"あい";\n  std::println("{}", v.size());', "2", "`u16string` を、コピーせずに見るだけの型です。"),
    ("u32string_view", "char32_t", "U", '  std::u32string_view v = U"😀";\n  std::println("{}", v.size());', "1", "`u32string` を、コピーせずに見るだけの型です。1 コード単位が 1 コードポイントです。")]:
    P("utilities/" + nm + ".md", "std::" + nm, f"`{ch}` を文字の型にもつ、文字列を借りて見るだけの型。", "rare", "string_view", intro,
      [f"`std::basic_string_view<{ch}>` の別名。", "持ち主ではないので、元の文字列より長く生きてはいけない。", "`string_view` と同じ関数が使える。"],
      [("関数の引数で文字列を受ける", f"`void F(std::{nm} s);`")], ("元の文字列が先に消える", "借りている先が消えると、中身は壊れます。一時オブジェクトから作った `string_view` を保存しないようにします。"),
      [("[`string_view`](string_view.md)", "char の版"), ("[`basic_string_view`](basic_string_view.md)", "元になるテンプレート")],
      [f"{ch} の string_view", "借りるだけで持ち主ではない", "string_view と同じ使い方"],
      sig=f"using {nm} = basic_string_view<{ch}>;", args=[], ret=f"`{nm}` の値", cx="string_view と同じ",
      code="#include <print>\n#include <string_view>\n\nint main() {\n" + code + "\n}", out=out, ver=("20", "C++20") if nm == "u8string_view" else ("17", "C++17"),
      info="[`std::string_view`](string_view.md) を先に読んでください。", rj="string_view/basic_string_view.html", cr="string/basic_string_view")

P("utilities/basic_string_view.md", "std::basic_string_view", "string_view / wstring_view などの元になる、文字の型を選べるテンプレート。", "rare", "string_view",
  "`std::string_view` は、実は `basic_string_view<char>` の別名です。文字の型が `wchar_t` や `char8_t` のときも同じ仕組みで使えるように、元になるクラステンプレートがあります。自分で直接書くことは少なく、別名を使います。",
  ["`string_view` = `basic_string_view<char>`。", "文字の型を `CharT` で選ぶ。", "テンプレートの引数で任意の文字型を受けるとき（ジェネリックな関数）に書く。"],
  [("文字の型を問わない関数", "`template <class CharT> void F(std::basic_string_view<CharT> s);`")],
  ("別名と取り違える", "関数の引数には `std::string_view` を書けば、たいていは足ります。`basic_string_view` は、型を問わない関数を書くときだけ登場します。"),
  [("[`string_view`](string_view.md)", "char の版"), ("[`wstring_view`](wstring_view.md)", "wchar_t の版")],
  ["string_view の元のテンプレート", "CharT で文字の型を選ぶ", "ふつうは別名を使う"],
  sig="template <class CharT, class Traits = char_traits<CharT>>\nclass basic_string_view;", args=[("CharT", "型", "文字の型"), ("Traits", "型", "省略可。比較などの規則")], ret="string_view と同じ関数をもつ", cx="string_view と同じ",
  code="""#include <print>
#include <string_view>

int main() {
  std::basic_string_view<char> v = "hello";
  std::println("{}", v.substr(1, 3));
}""", out="ell", ver=("17", "C++17"), info="[`std::string_view`](string_view.md) を先に読んでください。", rj="string_view/basic_string_view.html", cr="string/basic_string_view")

# 文字列 ↔ 数値
CV = "containers/"
for nm, ret_t, desc, call, res in [
    ("stol", "long", "文字列を long に変換する（失敗すると例外）。", 'std::stol("-42")', "-42"),
    ("stoul", "unsigned long", "文字列を unsigned long に変換する（失敗すると例外）。", 'std::stoul("42")', "42"),
    ("stoull", "unsigned long long", "文字列を unsigned long long に変換する（失敗すると例外）。", 'std::stoull("18446744073709551615")', "18446744073709551615"),
    ("stold", "long double", "文字列を long double に変換する（失敗すると例外）。", 'std::stold("3.5")', "3.5")]:
    P(CV + nm + ".md", "std::" + nm, desc, "rare", "string",
      f"`{nm}` は、`stoi` の仲間で、文字列を `{ret_t}` に変換します。大きな整数や高い精度の小数が必要なときに使います。",
      ["失敗したときは例外を投げる。", "第 2 引数で、読み終えた位置を受け取れる。" if nm != "stold" else "小数の変換は `stof`・`stod`・`stold`。", "例外を避けたいなら [`from_chars`](../io/from_chars.md)。"],
      [("設定ファイルの数値を読む", f"`{call}`")], ("例外を捕まえない", "`std::invalid_argument`（数字でない）と `std::out_of_range`（範囲外）を投げます。外から入った文字列は `try` で囲むか、`from_chars` を使います。"),
      [("[`stoi`](stoi.md)", "int の版"), ("[`from_chars`](../io/from_chars.md)", "例外を投げない版")],
      [f"文字列を {ret_t} に変換", "失敗は例外", "例外が嫌なら from_chars"],
      sig=f"{ret_t} {nm}(const std::string& str, std::size_t* pos = nullptr{', int base = 10' if nm != 'stold' else ''});",
      args=[("str", "string", "変換する文字列"), ("pos", "size_t*", "省略可。読み終えた位置を受け取る")] + ([("base", "int", "省略可。進数（既定は 10）")] if nm != "stold" else []), ret=f"変換した {ret_t}", cx="O(文字数)",
      code=f"""#include <print>
#include <string>

int main() {{
  std::println("{{}}", {call});
}}""", out=res, ver=("11", "C++11"), info=SI, rj=f"string/{nm}.html", cr="string/basic_string/stol")
P(CV + "to_wstring.md", "std::to_wstring", "数値を wstring に変換する。", "rare", "string",
  "`std::to_string` の `wstring` 版です。Windows の API に数値を文字列で渡すときなどに使います。整数と浮動小数点のオーバーロードがあります。",
  ["`to_string` の `wchar_t` 版。", "小数は固定小数点の形（`%f` 相当）で出る。", "書式を指定したいなら `std::format`。"],
  [("Windows API に数値を文字列で渡す", "`std::to_wstring(value)`")], ("小数の桁数を指定したい", "`to_wstring(3.5)` は `3.500000` になります。桁数は `std::format` で指定します。"),
  [("[`to_string`](to_string.md)", "char の版"), ("[`format`](../utilities/format.md)", "書式を指定する")], ["数値を wstring に", "to_string の wchar_t 版", "書式は format"],
  sig="std::wstring to_wstring(int value);\nstd::wstring to_wstring(double value);  // ほかの整数・浮動小数点型もある", args=[("value", "数値", "変換する数値")], ret="変換した `wstring`", cx="O(桁数)",
  code="""#include <print>
#include <string>

int main() {
  std::wstring w = std::to_wstring(42);
  std::println("{}", w.size());
}""", out="2", ver=("11", "C++11"), info=SI, rj="string/to_wstring.html", cr="string/basic_string/to_wstring")

# ================= ctime =================
T = "io/ctime/"
TI = "[`<ctime>`](../ctime.md) の概要が分かると読みやすいです。" if False else "[`std::time`](time.md) を先に読んでください。"
P(T + "difftime.md", "std::difftime", "2 つの time_t の差を、秒（double）で返す。", "rare", "ctime",
  "`time_t` は整数とは限らず、単位も処理系ごとに違うことがあります。時刻の差を安全に秒で求めるには、引き算ではなく `std::difftime` を使います。",
  ["戻り値は秒（`double`）。", "`end - start` の順で渡す（`difftime(end, start)`）。", "ゲームの経過時間は [`steady_clock`](../../utilities/chrono/steady_clock.md) が正確。"],
  [("セーブデータの経過日数", "`std::difftime(now, saved) / 86400`")], ("引数の順を逆にする", "`difftime(a, b)` は `a - b` です。新しいほうを先に渡します。"),
  [("[`time`](time.md)", "今の時刻"), ("[`steady_clock`](../../utilities/chrono/steady_clock.md)", "精度のよい計測")], ["time_t の差を秒で返す", "第 1 引数 - 第 2 引数", "計測には steady_clock"],
  sig="double difftime(std::time_t time_end, std::time_t time_beg);", args=[("time_end", "time_t", "新しいほうの時刻"), ("time_beg", "time_t", "古いほうの時刻")], ret="秒数（`double`）", cx="定数",
  code="""#include <ctime>
#include <print>

int main() {
  std::time_t a = 100;
  std::time_t b = 40;
  std::println("{}", std::difftime(a, b));
}""", out="60", info=TI, rj="ctime/difftime.html", cr="chrono/c/difftime")
P(T + "mktime.md", "std::mktime", "tm（年月日時分秒）を time_t に変換する（ローカル時刻として）。", "rare", "ctime",
  "年月日を自分で組み立てた日時を、`time_t` に変換したいことがあります。`std::mktime` は、`tm` をローカル時刻として解釈し、`time_t` を返します。同時に、範囲外の値（1 月 32 日など）を正しい日時に**正規化**します。",
  ["`tm` の `tm_year` は 1900 からの差、`tm_mon` は 0〜11。", "引数の `tm` は書き換わる（正規化される）。", "`tm_isdst` は -1 にすると、夏時間を自動判定する。"],
  [("月日を足して日付を進める", "`t.tm_mday += 30; std::mktime(&t);`")], ("月を 1 から数える", "`tm_mon` は 0 始まりです。`tm_year` も `年 - 1900` です。"),
  [("[`localtime`](localtime.md)", "time_t を tm に"), ("[`gmtime`](gmtime.md)", "UTC の tm に")], ["tm を time_t に変換", "tm を正規化する", "tm_mon は 0 始まり"],
  sig="std::time_t mktime(std::tm* time);", args=[("time", "tm*", "変換する日時（正規化されて書き換わる）")], ret="`time_t`（変換できないと `-1`）", cx="定数",
  code="""#include <ctime>
#include <print>

int main() {
  std::tm t{};
  t.tm_year = 124;  // 2024 年
  t.tm_mon = 0;     // 1 月
  t.tm_mday = 32;   // 1 月 32 日 → 2 月 1 日に正規化される
  t.tm_isdst = -1;
  std::mktime(&t);
  std::println("{} {}", t.tm_mon, t.tm_mday);
}""", out="1 1", info=TI, rj="ctime/mktime.html", cr="chrono/c/mktime")
P(T + "localtime.md", "std::localtime", "time_t を、ローカル時刻の tm に変換する。", "rare", "ctime",
  "`time_t`（秒数）を、年月日時分秒に分けたいときに使います。`std::localtime` はローカル時刻（OS のタイムゾーン）で、UTC なら [`gmtime`](gmtime.md) です。",
  ["戻り値は**静的な領域**を指すので、次に呼ぶと上書きされる。", "スレッドをまたぐなら `localtime_s`（Windows）/ `localtime_r`（POSIX）。", "新しいコードでは `std::chrono` のほうが安全。"],
  [("セーブの日付を表示", "`std::localtime(&t)`")], ("戻り値を保存する", "戻り値のポインタは、次の呼び出しで上書きされます。必要なら `tm` を値でコピーします。"),
  [("[`gmtime`](gmtime.md)", "UTC の版"), ("[`mktime`](mktime.md)", "逆の変換")], ["time_t をローカル時刻の tm に", "戻りは静的領域", "スレッドでは _s / _r 版"],
  sig="std::tm* localtime(const std::time_t* timer);", args=[("timer", "const time_t*", "変換する時刻")], ret="`tm` へのポインタ（失敗すると `nullptr`）", cx="定数",
  code="""#include <ctime>
#include <print>

int main() {
  std::time_t t = 86400LL * 365 * 30;  // 1999 年の終わりごろ
  std::tm* local = std::localtime(&t);
  std::println("{}", local->tm_year);
}""", out="99", info=TI, rj="ctime/localtime.html", cr="chrono/c/localtime")
P(T + "asctime.md", "std::asctime", "tm を、決まった形の文字列にする。", "rare", "ctime",
  "`tm` を `Mon Jan  1 00:00:00 2024` のような英語の決まった形にしたいときに使います。末尾に改行が付きます。形式が固定で、自由に変えられないので、新しいコードでは `strftime` や `std::format` のほうが便利です。",
  ["形式は `曜日 月 日 時:分:秒 年\\n`。", "戻り値は静的な領域を指す（スレッドセーフでない）。", "日本語や別の形式は `strftime`。"],
  [("デバッグログの日時", "`std::asctime(&tm)`")], ("形式を変えたい", "`asctime` の形式は変えられません。`std::strftime` や `std::format` を使います。"),
  [("[`strftime`](strftime.md)", "形式を指定できる"), ("[`ctime`](ctime.md)", "time_t から直接")], ["tm を固定形式の文字列に", "末尾に改行", "形式を変えるなら strftime"],
  sig="char* asctime(const std::tm* time_ptr);", args=[("time_ptr", "const tm*", "文字列にする日時")], ret="文字列へのポインタ（静的な領域）", cx="定数",
  code="""#include <ctime>
#include <print>

int main() {
  std::tm t{};
  t.tm_year = 124;
  t.tm_mon = 0;
  t.tm_mday = 1;
  t.tm_wday = 1;  // 月曜
  std::print("{}", std::asctime(&t));
}""", out="Mon Jan  1 00:00:00 2024", info=TI, rj="ctime/asctime.html", cr="chrono/c/asctime")
P(T + "ctime.md", "std::ctime", "time_t を、ローカル時刻の決まった形の文字列にする。", "rare", "ctime",
  "`localtime` して `asctime` するのを 1 回で済ませる関数です。`Mon Jan  1 09:00:00 2024\\n` のような形になります。タイムゾーンによって結果が変わります。",
  ["`asctime(localtime(t))` と同じ。", "戻り値は静的な領域（スレッドセーフでない）。", "新しいコードは `std::chrono` と `std::format`。"],
  [("手軽なログの日時", "`std::ctime(&t)`")], ("結果が環境で変わる", "ローカル時刻なので、同じ `time_t` でも環境のタイムゾーンで文字列が変わります。"),
  [("[`asctime`](asctime.md)", "tm から"), ("[`strftime`](strftime.md)", "形式を指定できる")], ["time_t を文字列にする", "ローカル時刻", "末尾に改行"],
  sig="char* ctime(const std::time_t* timer);", args=[("timer", "const time_t*", "文字列にする時刻")], ret="文字列へのポインタ（静的な領域）", cx="定数",
  code="""#include <ctime>
#include <print>

int main() {
  std::time_t t = 0;
  std::print("{}", std::ctime(&t));  // タイムゾーンにより結果が変わる
}""", out=None, info=TI, rj="ctime/ctime.html", cr="chrono/c/ctime")
P(T + "timespec_get.md", "std::timespec_get", "現在の時刻を、秒とナノ秒の組（timespec）で取得する。", "rare", "ctime",
  "`time` は秒の精度しかありません。`timespec_get` は、ナノ秒の精度で現在時刻を取れる C の関数です。ゲームの計測には [`steady_clock`](../../utilities/chrono/steady_clock.md) のほうが向いています。",
  ["`TIME_UTC` を渡すと、UTC の現在時刻が取れる。", "戻り値は `base`（成功）か 0（失敗）。", "時計の巻き戻りがありうるので計測には不向き。"],
  [("ナノ秒単位のタイムスタンプ", "`std::timespec_get(&ts, TIME_UTC)`")], ("経過時間の計測に使う", "壁時計なので巻き戻ることがあります。計測には `steady_clock` を使います。"),
  [("[`time`](time.md)", "秒の精度"), ("[`steady_clock`](../../utilities/chrono/steady_clock.md)", "計測に向く")], ["秒とナノ秒の現在時刻", "TIME_UTC を渡す", "計測は steady_clock"],
  sig="int timespec_get(std::timespec* ts, int base);", args=[("ts", "timespec*", "結果を入れる変数"), ("base", "int", "`TIME_UTC` を指定")], ret="成功なら `base`、失敗なら 0", cx="定数",
  code="""#include <ctime>
#include <print>

int main() {
  std::timespec ts;
  int r = std::timespec_get(&ts, TIME_UTC);
  std::println("{}", r == TIME_UTC);
}""", out="true", ver=("17", "C++17"), info=TI, rj="ctime/timespec_get.html", cr="chrono/c/timespec_get")
P(T + "timespec.md", "std::timespec", "秒とナノ秒の組を表す構造体。", "rare", "ctime",
  "秒だけでは足りない細かい時刻や時間を、C の API とやり取りするときに使う構造体です。`tv_sec`（秒）と `tv_nsec`（ナノ秒）の 2 つのメンバをもちます。",
  ["`tv_sec` は秒、`tv_nsec` は 0〜999,999,999 のナノ秒。", "`timespec_get` の結果を受ける。", "POSIX の API（`nanosleep` など）とも共通。"],
  [("ナノ秒単位の時刻を受ける", "`std::timespec ts;`")], ("ナノ秒が 10 億以上", "`tv_nsec` は 1 秒未満の範囲に収めます。あふれた分は `tv_sec` に繰り上げます。"),
  [("[`timespec_get`](timespec_get.md)", "現在時刻を取得する"), ("[`std::chrono::duration`](../../utilities/chrono/duration.md)", "C++ の時間の型")], ["秒 + ナノ秒の構造体", "tv_sec と tv_nsec", "timespec_get が使う"],
  sig="struct timespec {\n  std::time_t tv_sec;  // 秒\n  long tv_nsec;        // ナノ秒（0〜999,999,999）\n};", args=[], ret="なし（構造体）", cx="なし",
  code="""#include <ctime>
#include <print>

int main() {
  std::timespec ts{1, 500000000};
  std::println("{} {}", ts.tv_sec, ts.tv_nsec);
}""", out="1 500000000", ver=("17", "C++17"), info=TI, rj="ctime/timespec.html", cr="chrono/c/timespec")
P(T + "tm.md", "std::tm", "年月日時分秒を分けて持つ構造体。", "rare", "ctime",
  "`time_t` は秒数の 1 つの値です。年月日時分秒に分けて扱いたいときに使うのが `std::tm` で、`gmtime` / `localtime` が作り、`mktime` が `time_t` に戻します。",
  ["`tm_year` は 1900 からの経過年。", "`tm_mon` は 0〜11（1 月が 0）。", "`tm_wday` は日曜が 0、`tm_yday` は 1 月 1 日が 0。"],
  [("日付の取り出し", "`std::gmtime(&t)->tm_year + 1900`")], ("月を 1 から数える", "`tm_mon` は 0 始まり、`tm_year` は年 - 1900 です。足し忘れ・引き忘れでずれます。"),
  [("[`gmtime`](gmtime.md)", "UTC の tm に"), ("[`mktime`](mktime.md)", "time_t に戻す")], ["年月日時分秒の構造体", "月は 0 始まり、年は -1900", "gmtime / mktime と組む"],
  sig="struct tm {\n  int tm_sec;    // 秒 [0, 60]\n  int tm_min;    // 分 [0, 59]\n  int tm_hour;   // 時 [0, 23]\n  int tm_mday;   // 日 [1, 31]\n  int tm_mon;    // 月 [0, 11]\n  int tm_year;   // 1900 からの年\n  int tm_wday;   // 曜日 [0, 6]（日曜 = 0）\n  int tm_yday;   // 1 月 1 日からの日数 [0, 365]\n  int tm_isdst;  // 夏時間（正: 有効、0: 無効、負: 不明）\n};",
  args=[], ret="なし（構造体）", cx="なし",
  code="""#include <ctime>
#include <print>

int main() {
  std::time_t t = 0;
  std::tm* p = std::gmtime(&t);
  std::println("{} {} {}", p->tm_year, p->tm_mon, p->tm_mday);
}""", out="70 0 1", info=TI, rj="ctime/tm.html", cr="chrono/c/tm")
P(T + "time_t.md", "std::time_t", "時刻（エポックからの秒数）を表す型。", "rare", "ctime",
  "`std::time` が返す型で、基準時刻（普通は 1970-01-01 00:00:00 UTC）からの経過秒数を表します。実際の型（32 / 64 ビット）は処理系次第です。",
  ["算術型（多くは 64 ビット整数）。", "差は `difftime` で求める。", "年月日に分けるには `gmtime` / `localtime`。"],
  [("セーブデータのタイムスタンプ", "`std::time(nullptr)`")], ("32 ビットの time_t", "古い環境の 32 ビットは、2038 年に桁あふれします。64 ビットの環境を使います。"),
  [("[`time`](time.md)", "現在時刻を取る"), ("[`difftime`](difftime.md)", "差を求める")], ["エポックからの秒数の型", "処理系ごとに違う", "difftime で差を取る"],
  sig="using time_t = /* 算術型（実装定義） */;", args=[], ret="なし（型）", cx="なし",
  code="""#include <ctime>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_arithmetic_v<std::time_t>);
  std::println("{}", std::time(nullptr) > 0);
}""", out="true\ntrue", info=TI, rj="ctime/time_t.html", cr="chrono/c/time_t")
P(T + "clock_t.md", "std::clock_t", "プロセッサ時間（clock の戻り値）を表す型。", "rare", "ctime",
  "`std::clock()` が返すのは、プログラムが使ったプロセッサ時間のカウントです。その型が `clock_t` で、秒に直すには `CLOCKS_PER_SEC` で割ります。",
  ["算術型（実装定義）。", "秒に直すには `CLOCKS_PER_SEC` で割る。", "壁時計の時間ではなく CPU 時間。"],
  [("処理時間の簡易計測", "`(double)(end - start) / CLOCKS_PER_SEC`")], ("壁時計と取り違える", "スリープ中は進みません。実際の経過時間は `steady_clock` で測ります。"),
  [("[`clock`](clock.md)", "CPU 時間を取る"), ("[`CLOCKS_PER_SEC`](clocks_per_sec.md)", "1 秒あたりのカウント")], ["clock() の戻り値の型", "秒には CLOCKS_PER_SEC で割る", "CPU 時間"],
  sig="using clock_t = /* 算術型（実装定義） */;", args=[], ret="なし（型）", cx="なし",
  code="""#include <ctime>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_arithmetic_v<std::clock_t>);
}""", out="true", info=TI, rj="ctime/clock_t.html", cr="chrono/c/clock_t")
P(T + "clocks_per_sec.md", "CLOCKS_PER_SEC", "clock() の値を、秒に直すための 1 秒あたりのカウント数。", "rare", "ctime",
  "`clock()` が返すカウントは、処理系ごとに単位が違います（Linux では 100 万、Windows では 1000 など）。秒に直すには、この `CLOCKS_PER_SEC` で割ります。",
  ["マクロ（式）で、値は処理系ごとに違う。", "`double(end - start) / CLOCKS_PER_SEC` で秒にする。", "精度の良い計測には `steady_clock`。"],
  [("CPU 時間を秒に直す", "`double(c) / CLOCKS_PER_SEC`")], ("値を決め打ちする", "`1000` などと決め打ちすると、環境が変わったときにずれます。必ず `CLOCKS_PER_SEC` を使います。"),
  [("[`clock`](clock.md)", "CPU 時間を取る")], ["clock() の単位を秒に直すマクロ", "値は処理系ごと", "決め打ちしない"],
  sig="#define CLOCKS_PER_SEC /* 実装定義 */", args=[], ret="1 秒あたりのカウント数", cx="なし",
  code="""#include <ctime>
#include <print>

int main() {
  std::clock_t start = std::clock();
  // ... 計測したい処理 ...
  std::clock_t end = std::clock();
  double sec = static_cast<double>(end - start) / CLOCKS_PER_SEC;
  std::println("{}", sec >= 0.0);
}""", out="true", info=TI, rj="ctime/clock.html", cr="chrono/c/CLOCKS_PER_SEC")

# ================= random =================
RN = "utilities/random/"
RNI = "[`std::mt19937`](mt19937.md) と [乱数](../random.md) を先に読むと分かりやすいです。"
RNH = None
for nm, what, intro, sig, code, out, tenth, cxx in [
    ("mt19937_64", "64 ビット版のメルセンヌ・ツイスタ（高品質な乱数エンジン）。", "`mt19937` は 32 ビットの乱数を作ります。64 ビットの値が欲しいとき（大きな ID、`uint64_t` の乱数）には、`mt19937_64` が向いています。品質と速さのバランスがよく、ゲームの乱数で最も使われるエンジンの 64 ビット版です。",
     "using mt19937_64 = mersenne_twister_engine<uint_fast64_t, 64, 312, 156, 31, 0xb5026f5aa96619e9, 29, 0x5555555555555555, 17, 0x71d67fffeda60000, 37, 0xfff7eee000000000, 43, 6364136223846793005>;",
     """#include <print>
#include <random>

int main() {
  std::mt19937_64 e;  // 既定のシード
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}""", "9981545732273789042", True, ""),
    ("minstd_rand0", "古典的な線形合同法の乱数エンジン（軽いが品質は低め）。", "状態が小さく、1 回の計算も軽い乱数エンジンが欲しいことがあります。`minstd_rand0` は、`x ← 16807 × x mod (2³¹−1)` で次の値を作る、最も素朴な線形合同法です。品質は低いので、本格的な用途には `mt19937` を使います。",
     "using minstd_rand0 = linear_congruential_engine<uint_fast32_t, 16807, 0, 2147483647>;",
     """#include <print>
#include <random>

int main() {
  std::minstd_rand0 e;  // 既定のシードは 1
  std::println("{}", e());
  std::println("{}", e());
}""", "16807\n282475249", False, ""),
    ("ranlux24_base", "ranlux24 の土台になる、キャリーつき引き算法のエンジン。", "`ranlux24` は高品質な乱数エンジンですが、その中身は `ranlux24_base` の出力を間引いたものです。`ranlux24_base` 自体は速いものの、単独では統計的な品質が劣ります。",
     "using ranlux24_base = subtract_with_carry_engine<uint_fast32_t, 24, 10, 24>;",
     """#include <print>
#include <random>

int main() {
  std::ranlux24_base e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}""", "7937952", True, ""),
    ("ranlux48_base", "ranlux48 の土台になる、キャリーつき引き算法のエンジン。", "`ranlux48` の土台になる、48 ビット幅のエンジンです。`ranlux48_base` は単独では品質が劣り、そのまま使うことは少なく、`ranlux48` を使います。",
     "using ranlux48_base = subtract_with_carry_engine<uint_fast64_t, 48, 5, 12>;",
     """#include <print>
#include <random>

int main() {
  std::ranlux48_base e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}""", "61839128582725", True, ""),
    ("linear_congruential_engine", "線形合同法の乱数エンジンのテンプレート（`minstd_rand` の元）。", "「次の値 = (a × 今の値 + c) mod m」で乱数を作る方法が、線形合同法です。`linear_congruential_engine<UInt, a, c, m>` は、そのパラメータを自分で選べるテンプレートで、`minstd_rand0` や `minstd_rand` はその特定の設定です。",
     "template <class UIntType, UIntType a, UIntType c, UIntType m>\nclass linear_congruential_engine;",
     """#include <cstdint>
#include <print>
#include <random>

int main() {
  // minstd_rand0 と同じパラメータ
  std::linear_congruential_engine<std::uint_fast32_t, 16807, 0, 2147483647> e;
  std::println("{}", e());
}""", "16807", False, ""),
    ("mersenne_twister_engine", "メルセンヌ・ツイスタの乱数エンジンのテンプレート（`mt19937` の元）。", "`mt19937` や `mt19937_64` は、`mersenne_twister_engine` に特定のパラメータを入れたものです。自分でパラメータ（語長、状態の大きさ、マスク）を選べますが、ふつうは `mt19937` を使います。",
     "template <class UIntType, size_t w, size_t n, size_t m, size_t r, UIntType a, size_t u, UIntType d, size_t s, UIntType b, size_t t, UIntType c, size_t l, UIntType f>\nclass mersenne_twister_engine;",
     """#include <cstdint>
#include <print>
#include <random>

int main() {
  // mt19937 と同じパラメータ
  std::mersenne_twister_engine<std::uint_fast32_t, 32, 624, 397, 31, 0x9908b0df, 11,
                               0xffffffff, 7, 0x9d2c5680, 15, 0xefc60000, 18, 1812433253> e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}""", "4123659995", True, ""),
    ("subtract_with_carry_engine", "キャリーつき引き算法の乱数エンジンのテンプレート（`ranlux24_base` の元）。", "過去の 2 つの値の差とキャリー（繰り下がり）から次の値を作る方法です。`ranlux24_base` と `ranlux48_base` は、これの特定の設定です。",
     "template <class UIntType, size_t w, size_t s, size_t r>\nclass subtract_with_carry_engine;",
     """#include <cstdint>
#include <print>
#include <random>

int main() {
  // ranlux24_base と同じパラメータ
  std::subtract_with_carry_engine<std::uint_fast32_t, 24, 10, 24> e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}""", "7937952", True, ""),
    ("discard_block_engine", "別のエンジンの出力を、ブロックごとに間引くアダプタ（`ranlux24` の元）。", "品質の低いエンジンの出力は、続けて使うと偏りが出ることがあります。`discard_block_engine<Engine, P, R>` は、`P` 個ごとのブロックのうち `R` 個だけ使い、残りを捨てることで品質を上げます。`ranlux24` は `ranlux24_base` にこれを適用したものです。",
     "template <class Engine, size_t p, size_t r>\nclass discard_block_engine;",
     """#include <print>
#include <random>

int main() {
  // ranlux24 と同じ組み合わせ
  std::discard_block_engine<std::ranlux24_base, 223, 23> e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}""", "9901578", True, ""),
    ("independent_bits_engine", "別のエンジンの出力から、指定したビット数の乱数を作るアダプタ。", "エンジンの出力のビット幅と、欲しいビット幅が合わないことがあります。`independent_bits_engine<Engine, W, UInt>` は、元のエンジンを何回か呼び、W ビットの乱数を組み立てます。",
     "template <class Engine, size_t w, class UIntType>\nclass independent_bits_engine;",
     """#include <cstdint>
#include <print>
#include <random>

int main() {
  using E = std::independent_bits_engine<std::mt19937, 16, std::uint32_t>;
  std::println("{}", E::max());  // 16 ビットなので 65535
}""", "65535", False, ""),
    ("shuffle_order_engine", "別のエンジンの出力の順番を入れ替えるアダプタ（`knuth_b` の元）。", "線形合同法のような単純なエンジンは、出力の並びに規則性が出ます。`shuffle_order_engine<Engine, K>` は、K 個の値を貯めておき、ランダムな順番で取り出すことで規則性を崩します。`knuth_b` は `minstd_rand0` にこれを適用したものです。",
     "template <class Engine, size_t k>\nclass shuffle_order_engine;",
     """#include <print>
#include <random>

int main() {
  // knuth_b と同じ組み合わせ
  std::shuffle_order_engine<std::minstd_rand0, 256> e;
  e.discard(9999);
  std::println("{}", e());  // 10000 回目の値（標準で決まっている）
}""", "1112339016", True, "")]:
    P(RN + nm + ".md", "std::" + nm, what, "rare", "random", intro,
      ["`<random>` のエンジン（乱数を作る部品）。", "分布（`uniform_int_distribution` など）と組み合わせて使う。", "シードは `std::random_device` などで与える。"],
      [("ゲームの乱数", f"`std::{nm} e{{seed}}; dist(e);`")], ("シードを固定のまま使う", "シードを与えないと毎回同じ並びになります。本番では `random_device` などで初期化します。"),
      [("[`mt19937`](mt19937.md)", "標準的な高品質エンジン"), ("[`default_random_engine`](default_random_engine.md)", "処理系おまかせ")],
      [what.rstrip("。"), "分布と組み合わせて使う", "シードは random_device で"],
      sig=sig, args=[("seed", "整数", "省略可。初期状態を決める値")], ret="`operator()` で次の乱数を返す", cx="1 回あたり定数",
      code=code, out=out, ver=("11", "C++11"), info=RNI, rj=f"random/{nm}.html", cr=f"numeric/random/{nm}")

if __name__ == "__main__":
    flush_hubs()
