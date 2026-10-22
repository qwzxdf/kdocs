"""バッチ 13: <climits> / <cfloat> / <cstdint> / <numbers> / <stdfloat> / <limits> / <cinttypes> の未登録分。"""
from mk import *  # noqa: F401,F403

N = "numeric/"

# ================= <climits> =================
CLIMITS = [
    ("CHAR_BIT", "1 バイトのビット数（ほぼ 8）。", "8"),
    ("SCHAR_MIN", "`signed char` の最小値。", "-128"), ("SCHAR_MAX", "`signed char` の最大値。", "127"), ("UCHAR_MAX", "`unsigned char` の最大値。", "255"),
    ("CHAR_MIN", "`char` の最小値（符号つきの環境では `SCHAR_MIN`、符号なしでは 0）。", "-128"), ("CHAR_MAX", "`char` の最大値。", "127"),
    ("SHRT_MIN", "`short` の最小値。", "-32768"), ("SHRT_MAX", "`short` の最大値。", "32767"), ("USHRT_MAX", "`unsigned short` の最大値。", "65535"),
    ("INT_MIN", "`int` の最小値。", "-2147483648"), ("INT_MAX", "`int` の最大値。", "2147483647"), ("UINT_MAX", "`unsigned int` の最大値。", "4294967295"),
    ("LONG_MIN", "`long` の最小値（Windows では 32 ビット）。", None), ("LONG_MAX", "`long` の最大値（Windows では 32 ビット）。", None), ("ULONG_MAX", "`unsigned long` の最大値。", None),
    ("LLONG_MIN", "`long long` の最小値。", "-9223372036854775808"), ("LLONG_MAX", "`long long` の最大値。", "9223372036854775807"), ("ULLONG_MAX", "`unsigned long long` の最大値。", "18446744073709551615"),
    ("MB_LEN_MAX", "マルチバイト文字 1 文字の最大のバイト数。", None),
]
for nm, what, val in CLIMITS:
    ex = f'  std::println("{{}}", {nm});' if val is not None else f'  std::println("{{}}", {nm} > 0 || {nm} < 0);'
    notes = f"{what}\n\n```cpp\n#include <climits>\n#include <print>\n\nint main() {{\n{ex}\n}}\n```\n" + (f"\n```text title=\"実行結果\"\n{val}\n```" if val is not None else "")
    notes = notes.replace("{ex}", ex)
    add_secs(N + "climits.md", fn(nm, f"#define {nm} /* 実装定義 */", None, f"{what.rstrip('。')}（整数の定数）", "コンパイル時", None,
                                    notes=f"{what}" + ("`char` の符号は処理系で決まります。" if nm in ("CHAR_MIN", "CHAR_MAX") else "") + ("値は環境で変わります（Windows は 32 ビット、Linux の 64 ビット環境は 64 ビット）。" if nm.startswith(("LONG_", "ULONG")) else "") + "\n\n`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。",
                                    ids=nm))

# ================= <cfloat> =================
CF = N + "cfloat.md"
FLT = [("FLT", "float"), ("DBL", "double"), ("LDBL", "long double")]
for suffix, what in [("EPSILON", "1 と、1 より大きい次の値との差（機械イプシロン）"), ("MAX", "表せる最大の有限値"), ("MIN", "表せる最小の正の正規数"), ("DIG", "10 進数で、情報を失わずに往復できる桁数"),
                     ("MANT_DIG", "仮数部のビット数（基数 `FLT_RADIX` の桁数）")]:
    for pre_, t in FLT:
        nm = f"{pre_}_{suffix}"
        add_secs(CF, fn(nm, f"#define {nm} /* 実装定義 */", None, f"`{t}` の{what}", "コンパイル時", None,
                        notes=f"`{t}` の{what}です。" + ("比べるときの許容誤差の目安に使えますが、値の大きさに応じた比べ方（相対誤差）が必要です。" if suffix == "EPSILON" else "") + "\n\n`std::numeric_limits<" + t + ">` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。", ids=nm))
add_secs(CF, fn("FLT_RADIX", "#define FLT_RADIX 2", None, "浮動小数点の基数（ほぼ 2）", "コンパイル時", None, notes="浮動小数点数の指数の基数です。ほとんどの環境で 2 です。", ids="FLT_RADIX"))
add_secs(CF, fn("FLT_EVAL_METHOD", "#define FLT_EVAL_METHOD /* 0, 1, 2 のどれか */", None, "式を評価するときの精度の方式", "コンパイル時", None, notes="`float` どうしの式を、`float` のまま計算するか（0）、`double` に拡張して計算するか（1）、`long double` に拡張するか（2）を表します。x87 の古い環境では 2 になり、計算結果が微妙に変わります。", ids="FLT_EVAL_METHOD"))
add_secs(CF, fn("FLT_ROUNDS", "#define FLT_ROUNDS /* 丸めモード */", None, "現在の丸めモード", "実行時", None, notes="浮動小数点の加算の丸めモード（0: 0 方向、1: 最近接、2: 正の無限大、3: 負の無限大）を表します。変えるのは `std::fesetround` です。", ids="FLT_ROUNDS"))
add_secs(CF, fn("DECIMAL_DIG", "#define DECIMAL_DIG /* 実装定義 */", None, "最大の浮動小数点型を、10 進数に往復するのに必要な桁数", "コンパイル時", None, notes="最も精度の高い浮動小数点型（`long double`）の値を、10 進数に変換して戻しても同じ値になるのに必要な桁数です。", ids="DECIMAL_DIG"))

# ================= <cstdint> =================
CI = N + "cstdint.md"
for nm, t, what in [("int_fast8_t", "int", "8 ビット以上で、最も速く扱える符号つき整数型"), ("int_least8_t", "signed char", "8 ビット以上で、最も小さい符号つき整数型"),
                    ("intmax_t", "long long", "最も大きい符号つき整数型"), ("uintmax_t", "unsigned long long", "最も大きい符号なし整数型")]:
    add_secs(CI, fn("std::" + nm, f"using {nm} = /* {t} など */;", None, f"{what}の別名", "コンパイル時", None,
                    notes=f"{what}です。" + ("速さを優先する計算に使います。" if "fast" in nm else "メモリの大きさを優先するときに使います。" if "least" in nm else "ビット幅を気にせず、最大の範囲を確保したいときに使います。") + "\n\n```cpp\n#include <cstdint>\n#include <print>\n\nint main() {\n  std::println(\"{}\", sizeof(std::" + nm + ") >= 1);\n}\n```\n\n```text title=\"実行結果\"\ntrue\n```", ids=nm))
add_secs(CI, fn("SIZE_MAX", "#define SIZE_MAX /* size_t の最大値 */", None, "`size_t` の最大値（定数）", "コンパイル時", None,
                notes="`size_t` で表せる最大値のマクロです。「見つからない」を表す値（`std::string::npos` など）として使われます。\n\n```cpp\n#include <cstdint>\n#include <print>\n\nint main() {\n  std::println(\"{}\", SIZE_MAX == static_cast<std::size_t>(-1));\n}\n```\n\n```text title=\"実行結果\"\ntrue\n```", ids="SIZE_MAX"))
for nm, val in [("INT32_MAX", "2147483647"), ("INT64_MAX", "9223372036854775807"), ("UINT32_MAX", "4294967295"), ("UINT64_MAX", "18446744073709551615")]:
    add_secs(CI, fn(nm, f"#define {nm} {val}", None, "固定幅の整数型の最大値（定数）", "コンパイル時", None,
                    notes=f"幅が決まった整数型の最大値です（{val}）。\n\n```cpp\n#include <cstdint>\n#include <print>\n\nint main() {{\n  std::println(\"{{}}\", {nm});\n}}\n```\n\n```text title=\"実行結果\"\n{val}\n```", ids=nm))

# ================= <numbers> =================
NB = N + "numbers.md"
for nm, val, what, show in [
    ("log2e", "1.4426950408889634", "log₂(e)（自然対数の底 e の、2 を底とした対数）", "1.442695"),
    ("log10e", "0.4342944819032518", "log₁₀(e)（e の常用対数）", "0.434294"),
    ("inv_sqrtpi", "0.5641895835477563", "1/√π", "0.564190"),
    ("ln2", "0.6931471805599453", "ln(2)（2 の自然対数）", "0.693147"),
    ("ln10", "2.302585092994046", "ln(10)（10 の自然対数）", "2.302585"),
    ("inv_sqrt3", "0.5773502691896258", "1/√3", "0.577350"),
    ("egamma", "0.5772156649015329", "オイラー・マスケローニ定数 γ", "0.577216")]:
    add_secs(NB, fn("std::numbers::" + nm, f"template <class T> inline constexpr T {nm}_v = /* {what} */;\ninline constexpr double {nm} = {nm}_v<double>;", None, f"{what}（約 {val[:8]}）", "コンパイル時", None,
                    notes=f"{what}の定数です。`float` 用は `std::numbers::{nm}_v<float>` です。\n\n```cpp\n#include <numbers>\n#include <print>\n\nint main() {{\n  std::println(\"{{:.6f}}\", std::numbers::{nm});\n}}\n```\n\n```text title=\"実行結果\"\n{show}\n```", ver=("20", "C++20"), ids=nm))

# ================= <stdfloat> =================
SF = N + "stdfloat.md"
for nm, size, what in [("float32_t", 4, "32 ビット（IEEE 754 binary32）の浮動小数点型"), ("float64_t", 8, "64 ビット（IEEE 754 binary64）の浮動小数点型"), ("float128_t", 16, "128 ビット（IEEE 754 binary128）の浮動小数点型")]:
    add_secs(SF, fn("std::" + nm, f"using {nm} = /* 実装定義の {size * 8} ビット浮動小数点型 */;", None, f"{what}", "コンパイル時", None,
                    notes=f"{what}です。実装が対応していない環境では定義されないので、`#ifdef __STDCPP_FLOAT{size * 8}_T__` で確かめます。\n\n```cpp\n#include <print>\n#include <stdfloat>\n\nint main() {{\n#ifdef __STDCPP_FLOAT{size * 8}_T__\n  std::println(\"{{}}\", sizeof(std::{nm}));\n#endif\n}}\n```\n\n```text title=\"実行結果\"\n{size}\n```", ver=("23", "C++23"), ids=nm))

# ================= <limits> の列挙型 =================
LM = N + "limits.md"
add_secs(LM, fn("std::float_round_style", "enum float_round_style {\n  round_indeterminate = -1,\n  round_toward_zero = 0,\n  round_to_nearest = 1,\n  round_toward_infinity = 2,\n  round_toward_neg_infinity = 3\n};", None, "浮動小数点の丸め方を表す列挙型", "コンパイル時", None,
                notes="`numeric_limits<T>::round_style` の型です。多くの環境では `round_to_nearest`（最も近い値へ丸める）です。\n\n```cpp\n#include <limits>\n#include <print>\n\nint main() {\n  std::println(\"{}\", std::numeric_limits<float>::round_style == std::round_to_nearest);\n}\n```\n\n```text title=\"実行結果\"\ntrue\n```", ids="float_round_style"))
add_secs(LM, fn("std::float_denorm_style", "enum float_denorm_style {\n  denorm_indeterminate = -1,\n  denorm_absent = 0,\n  denorm_present = 1\n};", None, "非正規数（0 に非常に近い小さな値）を持つかを表す列挙型", "コンパイル時", None,
                notes="`numeric_limits<T>::has_denorm` の型です（C++23 で `has_denorm` は非推奨）。多くの環境で `denorm_present` です。\n\n```cpp\n#include <limits>\n#include <print>\n\nint main() {\n  std::println(\"{}\", std::numeric_limits<double>::denorm_min() > 0);\n}\n```\n\n```text title=\"実行結果\"\ntrue\n```", ids="float_denorm_style"))

# ================= <cinttypes> =================
CIN = N + "cinttypes/"
CINI = "[`<cstdint>`](../cstdint.md) を先に読んでください。"
for nm, summ, intro, sig, args, ret, body, out in [
    ("imaxabs", "`intmax_t` の絶対値を返す。", "最も大きい符号つき整数型（`intmax_t`）の絶対値を求める関数です。`std::abs` で足りるので、ほとんど使いません。", "std::intmax_t imaxabs(std::intmax_t n);", [("n", "intmax_t", "絶対値を求める値")], "`|n|`", 'std::println("{}", std::imaxabs(-5));', "5"),
    ("imaxdiv", "`intmax_t` の割り算で、商と余りをいっしょに返す。", "`div`・`ldiv` の `intmax_t` 版です。", "std::imaxdiv_t imaxdiv(std::intmax_t x, std::intmax_t y);", [("x, y", "intmax_t", "割られる数・割る数")], "`quot`（商）と `rem`（余り）をもつ構造体", 'auto r = std::imaxdiv(7, 2);\nstd::println("{} {}", r.quot, r.rem);', "3 1"),
    ("strtoimax", "文字列を `intmax_t` に変換する。", "`strtoll` の `intmax_t` 版です。進数を指定でき、読み終えた位置も受け取れます。", "std::intmax_t strtoimax(const char* str, char** str_end, int base);", [("str", "const char*", "変換する文字列"), ("str_end", "char**", "読み終えた位置を受け取る（不要なら `nullptr`）"), ("base", "int", "進数")], "変換した値", 'std::println("{}", std::strtoimax("-42", nullptr, 10));', "-42"),
    ("strtoumax", "文字列を `uintmax_t` に変換する。", "`strtoull` の `uintmax_t` 版です。", "std::uintmax_t strtoumax(const char* str, char** str_end, int base);", [("str", "const char*", "変換する文字列"), ("str_end", "char**", "読み終えた位置を受け取る（不要なら `nullptr`）"), ("base", "int", "進数")], "変換した値", 'std::println("{}", std::strtoumax("42", nullptr, 10));', "42")]:
    Q(CIN + nm + ".md", "std::" + nm, summ, "rare", ["cinttypes", "print"], intro, ["`<cinttypes>` の関数。", "`intmax_t` / `uintmax_t` を扱う。", "新しいコードでは `std::from_chars` が安全。"], sig, args, ret, body, out,
      use="最大幅の整数の扱い", miss=("範囲外を確かめない", "変換が範囲外だと `errno` が `ERANGE` になります。" if nm.startswith("strto") else "`INTMAX_MIN` の絶対値は表せず、未定義動作です。"), sim=[("[`cstdint`](../cstdint.md)", "固定幅の整数型")], cx="定数" if not nm.startswith("strto") else "O(文字数)", ver=("11", "C++11"), info=CINI, rj=f"cinttypes/{nm}.html", cr=f"c/{nm}")

if __name__ == "__main__":
    flush_hubs()
