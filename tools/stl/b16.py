"""バッチ 16: <regex> / <locale> の未登録分。"""
from mk import *  # noqa: F401,F403

RX = "io/regex/"
RXI = "[`std::regex`](../regex.md) を先に読んでください。"


def R(name, summary, intro, sig, args, ret, body, out, use, miss, sim, ver=("11", "C++11"), pre="", inc=("regex", "print"), tips=None, cr=None, secs=None):
    kw = {}
    if secs is not None:
        kw["secs"] = secs
    Q(RX + name + ".md", "std::" + name, summary, "rare", [*inc], intro,
      tips or ["`<regex>` の部品。", "ふつうは別名（`regex`・`smatch` など）を使う。", "正規表現は、複雑になりすぎる前に別の方法も検討する。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx="パターンと文字列に依存", ver=ver, info=RXI, pre=pre, rj=f"regex/{name}.html", cr=f"regex/{cr or name}", **kw)


R("basic_regex", "正規表現を保持するクラスの、元になるテンプレート（`regex` の元）。", "`std::regex` は、`basic_regex<char>` の別名です。文字の型を選べるように、元になるクラステンプレートがあります。正規表現のコンパイル（文字列を内部の形に直す処理）は重いので、何度も使うなら、1 回作って使い回します。", "template <class CharT, class Traits = regex_traits<CharT>>\nclass basic_regex;",
  [("CharT", "型", "文字の型"), ("Traits", "型", "省略可。文字の分類などの規則")], "正規表現のオブジェクト", 'std::basic_regex<char> re("a+");\nstd::println("{}", std::regex_match("aaa", re));', "true",
  "同じ正規表現を何度も使うときに保持する", ("ループの中で毎回作る", "正規表現の構築は重い処理です。ループの外で 1 回作ります。"), [("[`regex`](../regex.md)", "char 版の別名"), ("[`wregex`](wregex.md)", "wchar_t 版")])
R("wregex", "`wchar_t` 用の正規表現。", "`std::wregex` は、`basic_regex<wchar_t>` の別名です。`wchar_t` の文字列（`wstring`）を検索するときに使います。", "using wregex = basic_regex<wchar_t>;",
  [], "正規表現のオブジェクト", 'std::wregex re(L"a+");\nstd::wstring s = L"aaa";\nstd::println("{}", std::regex_match(s, re));', "true", "Windows の `wstring` に対して検索する", ("`regex` と `wstring` を混ぜる", "文字の型を合わせます。`wstring` には `wregex` を使います。"), [("[`regex`](../regex.md)", "char 版"), ("[`wsmatch`](wsmatch.md)", "結果の型")])
R("regex_iterator", "文字列から、正規表現に一致する部分を、順に取り出すイテレータ。", "`regex_search` は最初の一致だけを返します。全部の一致を順に処理したいとき、`regex_iterator` を使います。`std::sregex_iterator` は、これの `string` 用の別名です。", "template <class BidirIt, class CharT = typename iterator_traits<BidirIt>::value_type, class Traits = regex_traits<CharT>>\nclass regex_iterator;",
  [("BidirIt", "型", "文字列のイテレータの型")], "一致（`match_results`）を順に返す", 'std::string s = "a1b22c333";\nstd::regex re("\\\\d+");\nstd::regex_iterator<std::string::const_iterator> it(s.begin(), s.end(), re);\nstd::regex_iterator<std::string::const_iterator> end;\nstd::println("{}", std::distance(it, end));', "3",
  "テキストから数字を全部取り出す", ("一致が空の正規表現を渡す", "空の一致があると、無限ループにならないよう、1 文字ずつ進みます。"), [("[`sregex_iterator`](../sregex_iterator.md)", "string 用の別名"), ("[`cregex_iterator`](cregex_iterator.md)", "C 文字列用")], inc=("regex", "print", "string", "iterator"))
R("cregex_iterator", "C 文字列から、正規表現に一致する部分を順に取り出すイテレータ。", "`regex_iterator<const char*>` の別名です。`std::string` ではなく、C の文字列（`const char*`）に対して、全部の一致を順に取り出します。", "using cregex_iterator = regex_iterator<const char*>;",
  [], "一致（`cmatch`）を順に返す", 'const char* s = "a1b22c333";\nstd::regex re("\\\\d+");\nstd::cregex_iterator it(s, s + std::strlen(s), re);\nstd::cregex_iterator end;\nstd::println("{}", std::distance(it, end));', "3",
  "C の文字列から、一致を全部取り出す", ("終端の指定を忘れる", "`s + strlen(s)` で終端を渡します。"), [("[`regex_iterator`](regex_iterator.md)", "元のテンプレート"), ("[`sregex_iterator`](../sregex_iterator.md)", "string 用")], inc=("regex", "print", "cstring", "iterator"))
R("regex_token_iterator", "文字列を、正規表現で分割して（または一致を取り出して）、順に返すイテレータ。", "文字列を「,」で分割したいとき、`regex_token_iterator` で区切りの正規表現を渡し、最後の引数に `-1` を渡すと、区切りの**間**の部分を順に取り出せます。`0` なら一致した部分、`1` ならグループ 1 を取り出します。", "template <class BidirIt, class CharT = typename iterator_traits<BidirIt>::value_type, class Traits = regex_traits<CharT>>\nclass regex_token_iterator;",
  [("BidirIt", "型", "文字列のイテレータの型")], "部分文字列（`sub_match`）を順に返す", 'std::string s = "a,b,c";\nstd::regex sep(",");\nstd::regex_token_iterator<std::string::const_iterator> it(s.begin(), s.end(), sep, -1);\nstd::regex_token_iterator<std::string::const_iterator> end;\nfor (; it != end; ++it) {\n  std::println("{}", it->str());\n}', "a\nb\nc",
  "文字列を区切り文字で分割する", ("最後の引数を忘れる", "`-1` を渡さないと、区切り自体が返ります。"), [("[`sregex_token_iterator`](sregex_token_iterator.md)", "string 用の別名"), ("[`views::split`](../../algorithms/views/split.md)", "新しい分割の書き方")], inc=("regex", "print", "string"))
R("sregex_token_iterator", "string 用の regex_token_iterator。", "`regex_token_iterator<std::string::const_iterator>` の別名です。`std::string` を正規表現で分割するときに使います。", "using sregex_token_iterator = regex_token_iterator<std::string::const_iterator>;",
  [], "部分文字列（`ssub_match`）を順に返す", 'std::string s = "a,b,c";\nstd::regex sep(",");\nstd::sregex_token_iterator it(s.begin(), s.end(), sep, -1);\nstd::sregex_token_iterator end;\nstd::println("{}", std::distance(it, end));', "3",
  "`std::string` を区切り文字で分割する", ("一時オブジェクトの `string` を渡す", "イテレータが指す文字列が先に消えると、壊れます。"), [("[`regex_token_iterator`](regex_token_iterator.md)", "元のテンプレート")], inc=("regex", "print", "string", "iterator"))
R("match_results", "一致の結果（全体とグループ）を保持するクラスの、元になるテンプレート。", "`regex_search` や `regex_match` は、一致した部分を `match_results` に入れて返します。`m[0]` が一致した全体、`m[1]` 以降が括弧で囲んだグループです。`std::smatch` は、これの `string` 用の別名です。", "template <class BidirIt, class Alloc = allocator<sub_match<BidirIt>>>\nclass match_results;",
  [("BidirIt", "型", "文字列のイテレータの型")], "`m[n]` で n 番目のグループ（`sub_match`）", 'std::string s = "10-20";\nstd::match_results<std::string::const_iterator> m;\nstd::regex_search(s, m, std::regex("(\\\\d+)-(\\\\d+)"));\nstd::println("{} {}", m[1].str(), m[2].str());', "10 20",
  "テキストから数値を取り出す", ("`m[0]` を最初のグループと思う", "`m[0]` は一致した全体です。括弧のグループは `m[1]` からです。"), [("[`smatch`](../smatch.md)", "string 用の別名"), ("[`sub_match`](sub_match.md)", "各グループの型")], inc=("regex", "print", "string"))
R("cmatch", "C 文字列用の match_results。", "`match_results<const char*>` の別名です。`std::string` ではなく、C の文字列（`const char*`）を検索した結果を入れます。", "using cmatch = match_results<const char*>;",
  [], "`m[n]` で n 番目のグループ（`csub_match`）", 'const char* s = "x=5";\nstd::cmatch m;\nstd::regex_search(s, m, std::regex("(\\\\w)=(\\\\d)"));\nstd::println("{}", m[2].str());', "5",
  "C の文字列から値を取り出す", ("一時オブジェクトを検索する", "`std::string` の一時オブジェクトを渡すと、結果が壊れます（`smatch` も同じ）。"), [("[`smatch`](../smatch.md)", "string 用"), ("[`match_results`](match_results.md)", "元のテンプレート")], inc=("regex", "print"))
R("wsmatch", "wstring 用の match_results。", "`match_results<std::wstring::const_iterator>` の別名です。`wstring` を `wregex` で検索した結果を入れます。", "using wsmatch = match_results<std::wstring::const_iterator>;",
  [], "`m[n]` で n 番目のグループ（`wssub_match`）", 'std::wstring s = L"x=5";\nstd::wsmatch m;\nstd::regex_search(s, m, std::wregex(L"(\\\\d)"));\nstd::println("{}", m.size());', "2",
  "`wstring` から値を取り出す", ("`smatch` を使う", "`wstring` には `wsmatch` を使います。"), [("[`smatch`](../smatch.md)", "string 用"), ("[`wcmatch`](wcmatch.md)", "wchar_t の C 文字列用")], inc=("regex", "print", "string"))
R("wcmatch", "wchar_t の C 文字列用の match_results。", "`match_results<const wchar_t*>` の別名です。`const wchar_t*` を `wregex` で検索した結果を入れます。", "using wcmatch = match_results<const wchar_t*>;",
  [], "`m[n]` で n 番目のグループ（`wcsub_match`）", 'const wchar_t* s = L"x=5";\nstd::wcmatch m;\nstd::regex_search(s, m, std::wregex(L"(\\\\d)"));\nstd::println("{}", m.size());', "2",
  "Windows API が返した `wchar_t*` を検索する", ("`cmatch` を使う", "`wchar_t` には `wcmatch` を使います。"), [("[`cmatch`](cmatch.md)", "char の C 文字列用")], inc=("regex", "print"))
R("sub_match", "一致したグループ 1 つぶんを表すクラス。", "`match_results` の `m[1]` のように、取り出したグループ 1 つぶんが `sub_match` です。`matched`（一致したか）、`str()`（文字列にする）、`length()`（長さ）などをもちます。", "template <class BidirIt>\nclass sub_match : public pair<BidirIt, BidirIt>;",
  [("BidirIt", "型", "文字列のイテレータの型")], "`first` / `second` が範囲、`str()` で文字列", 'std::string s = "abc123";\nstd::smatch m;\nstd::regex_search(s, m, std::regex("(\\\\d+)"));\nconst auto& sm = m[1];\nstd::println("{} {}", sm.matched, sm.length());', "true 3",
  "グループが一致したか調べて取り出す", ("`matched` を確かめない", "省略されたグループ（`(a)?` など）は、`matched` が `false` で空になります。"), [("[`ssub_match`](ssub_match.md)", "string 用の別名"), ("[`match_results`](match_results.md)", "グループの集まり")], inc=("regex", "print", "string"))
R("ssub_match", "string 用の sub_match。", "`sub_match<std::string::const_iterator>` の別名です。`smatch` の `m[n]` の型です。", "using ssub_match = sub_match<std::string::const_iterator>;",
  [], "`str()` で文字列", 'std::string s = "abc123";\nstd::smatch m;\nstd::regex_search(s, m, std::regex("(\\\\d+)"));\nstd::ssub_match sm = m[1];\nstd::println("{}", sm.str());', "123",
  "`smatch` のグループを取り出す", ("文字列として保存せず参照を持ち続ける", "元の文字列が消えると壊れます。`str()` でコピーします。"), [("[`sub_match`](sub_match.md)", "元のテンプレート"), ("[`csub_match`](csub_match.md)", "C 文字列用")], inc=("regex", "print", "string"))
R("csub_match", "C 文字列用の sub_match。", "`sub_match<const char*>` の別名です。`cmatch` の `m[n]` の型です。", "using csub_match = sub_match<const char*>;",
  [], "`str()` で文字列", 'const char* s = "abc123";\nstd::cmatch m;\nstd::regex_search(s, m, std::regex("(\\\\d+)"));\nstd::csub_match sm = m[1];\nstd::println("{}", sm.str());', "123",
  "`cmatch` のグループを取り出す", ("元の文字列が先に消える", "`csub_match` は元の文字列を指すだけです。"), [("[`sub_match`](sub_match.md)", "元のテンプレート"), ("[`ssub_match`](ssub_match.md)", "string 用")], inc=("regex", "print"))
R("regex_error", "正規表現のパターンが不正なときに投げられる例外。", "`std::regex re(\"(\")` のように、括弧が閉じていないパターンを作ろうとすると、`regex_error` が投げられます。`code()` で原因（`regex_constants::error_paren` など）を取れます。外から受け取ったパターンは `try` で囲みます。", "class regex_error : public runtime_error {\n public:\n  regex_constants::error_type code() const;\n};",
  [], "`code()` が原因", 'try {\n  std::regex re("(");\n} catch (const std::regex_error& e) {\n  std::println("{}", e.code() == std::regex_constants::error_paren);\n}', "true",
  "ユーザーが入力したパターンを検査する", ("外から入ったパターンを `try` で囲まない", "不正なパターンで例外が飛び、プログラムが落ちます。"), [("[`regex`](../regex.md)", "正規表現")])
R("regex_traits", "文字の分類や変換の規則をまとめた、正規表現の部品。", "正規表現エンジンは、「数字か」「空白か」「大文字小文字を同一視するか」といった判断を、`regex_traits` に任せています。ロケールによって規則を変えたいときに、差し替えられます。ふつうは意識しません。", "template <class CharT>\nstruct regex_traits {\n  static std::size_t length(const CharT* p);\n  CharT translate(CharT c) const;\n  // ...\n};",
  [("CharT", "型", "文字の型")], "文字の分類・変換の関数", 'std::println("{}", std::regex_traits<char>::length("abc"));', "3",
  "（正規表現の挙動を差し替えるとき）", ("ふつうは触らない", "既定の `regex_traits` で足ります。"), [("[`basic_regex`](basic_regex.md)", "これを使う正規表現")])
R("regex_constants", "正規表現のオプションとエラーコードをまとめた名前空間。", "`std::regex_constants` の中に、`icase`（大文字小文字を区別しない）のような**構文オプション**、`match_continuous` のような**一致オプション**、`error_paren` のような**エラーコード**が入っています。", "namespace std::regex_constants {\n  // syntax_option_type, match_flag_type, error_type の定数\n}",
  [], "各種の定数", 'std::regex re("ABC", std::regex_constants::icase);\nstd::println("{}", std::regex_match("abc", re));', "true",
  "大文字小文字を区別しない検索", ("`using namespace` する", "名前が衝突するので、必要な名前だけを `std::regex_constants::icase` と書きます。"), [("[`syntax_option_type`](syntax_option_type.md)", "構文オプション"), ("[`match_flag_type`](match_flag_type.md)", "一致オプション")])
OPTS = [("icase", "大文字小文字を区別しない。"), ("nosubs", "グループを記録しない（速くなる）。"), ("optimize", "実行速度を優先して準備する（構築が遅くなる）。"), ("collate", "範囲指定（`[a-z]`）をロケールの順序で解釈する。"),
        ("multiline", "`^` と `$` を、行の先頭・末尾にも一致させる（C++17）。"), ("ECMAScript", "ECMAScript（JavaScript）風の構文（既定）。"), ("basic", "POSIX の基本正規表現。"), ("extended", "POSIX の拡張正規表現。"),
        ("awk", "POSIX の awk の構文。"), ("grep", "POSIX の grep の構文。"), ("egrep", "POSIX の egrep（grep -E）の構文。")]
R("syntax_option_type", "正規表現の構文やオプションを指定するビットマスク型。", "`std::regex` を作るときの第 2 引数に渡す型です。`icase | ECMAScript` のように `|` でつなぎます。構文は 1 つだけ選び、`icase` などのオプションは重ねられます。", "enum syntax_option_type : /* 実装定義 */;",
  [], "ビットマスク", 'std::regex::flag_type f = std::regex_constants::icase | std::regex_constants::ECMAScript;\nstd::regex re("abc", f);\nstd::println("{}", std::regex_match("ABC", re));', "true",
  "構文とオプションを指定して正規表現を作る", ("構文を 2 つ選ぶ", "構文（`ECMAScript`・`basic` など）は 1 つだけ選びます。"), [("[`regex_constants`](regex_constants.md)", "定数の名前空間")],
  secs=[fn("std::regex_constants::syntax_option_type", "enum syntax_option_type : /* 実装定義 */;", None, "ビットマスク型", "", None, ids="syntax_option_type")] + [fn("std::regex_constants::" + n, f"constexpr syntax_option_type {n} = /* 実装定義 */;", None, d.rstrip("。"), "", None, notes=d, ids=n) for n, d in OPTS])
FLAGS = [("match_default", "既定の動作。"), ("match_not_bol", "`^` を先頭に一致させない（文字列の先頭を行頭と扱わない）。"), ("match_not_eol", "`$` を末尾に一致させない。"), ("match_not_bow", "`\\b` を単語の先頭に一致させない。"),
         ("match_not_eow", "`\\b` を単語の末尾に一致させない。"), ("match_any", "複数の一致があるとき、どれでもよい（最初に見つかったもの）。"), ("match_not_null", "空の一致を認めない。"),
         ("match_continuous", "文字列の先頭からの一致だけを認める。"), ("match_prev_avail", "前の文字が使える（先頭ではない）ものとして扱う。"), ("format_default", "置換の書式に ECMAScript を使う（既定）。"),
         ("format_sed", "置換の書式に POSIX の sed を使う。"), ("format_no_copy", "置換で、一致しない部分をコピーしない。"), ("format_first_only", "置換で、最初の一致だけを置き換える。")]
R("match_flag_type", "一致や置換の動作を指定するビットマスク型。", "`regex_search`・`regex_match`・`regex_replace` の最後の引数に渡す型です。`match_continuous` や `format_first_only` のように、`|` でつなぎます。", "enum match_flag_type : /* 実装定義 */;",
  [], "ビットマスク", 'std::regex re("abc");\nstd::println("{}", std::regex_search("xabc", re, std::regex_constants::match_continuous));', "false",
  "先頭からの一致だけを調べる", ("置換用のフラグを検索に使う", "`format_*` は `regex_replace` 用です。"), [("[`regex_constants`](regex_constants.md)", "定数の名前空間")],
  secs=[fn("std::regex_constants::match_flag_type", "enum match_flag_type : /* 実装定義 */;", None, "ビットマスク型", "", None, ids="match_flag_type")] + [fn("std::regex_constants::" + n, f"constexpr match_flag_type {n} = /* 実装定義 */;", None, d.rstrip("。"), "", None, notes=d, ids=n) for n, d in FLAGS])

# ================= locale =================
LC = "io/locale/"
LCI = "[`std::locale`](../locale.md) を先に読んでください。"
LOC = "const std::locale& loc = std::locale::classic();\n"


def L(name, summary, intro, sig, args, ret, body, out, use, miss, sim, ver=None, pre="", inc=("locale", "print"), tips=None, cr=None, cx="定数", info=LCI):
    Q(LC + name.lower() + ".md", name if name.isupper() else "std::" + name, summary, "rare", [*inc], intro,
      tips or ["ロケール（言語・地域ごとの規則）の部品。", "ふつうは `std::locale` 経由で使う。", "ゲームのローカライズでは、書式（日付・数字）に関わる。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx=cx, ver=ver, info=info, pre=pre, rj=f"locale/{name}.html", cr=f"locale/{cr or name}")


L("facet", "ロケールを構成する、部品（ファセット）の基底クラス。", "ロケールは、数字の書式、日付の書式、文字の分類など、複数の「部品」で構成されます。その部品の共通の基底クラスが `std::locale::facet` です。自分で部品を作るときは、これを継承し、`static std::locale::id id;` を持たせます。", "class locale::facet {\n protected:\n  explicit facet(std::size_t refs = 0);\n  virtual ~facet();\n};",
  [("refs", "size_t", "参照カウントの管理（0 ならロケールが管理する）")], "ロケールに追加できる部品", 'std::locale loc(std::locale::classic(), new MyFacet);\nstd::println("{}", std::has_facet<MyFacet>(loc));', "true",
  "独自の書式を、ロケールの仕組みに乗せる", ("`delete` を自分で呼ぶ", "ロケールが参照を数えて破棄します。`new` で渡して、自分では消しません。"), [("[`use_facet`](use_facet.md)", "ファセットを取り出す"), ("[`has_facet`](has_facet.md)", "ファセットがあるか")],
  pre="struct MyFacet : std::locale::facet {\n  static std::locale::id id;\n};\nstd::locale::id MyFacet::id;")
L("use_facet", "ロケールから、ファセット（部品）を取り出す。", "`std::use_facet<ファセット>(ロケール)` で、そのロケールが持つ部品への参照を取り出します。持っていない部品を指定すると、`std::bad_cast` が投げられます。", "template <class Facet>\nconst Facet& use_facet(const std::locale& loc);",
  [("Facet", "テンプレート引数", "取り出したいファセットの型"), ("loc", "locale", "対象のロケール")], "ファセットへの参照", 'const auto& np = std::use_facet<std::numpunct<char>>(std::locale::classic());\nstd::println("{}", np.decimal_point());', ".",
  "ロケールごとの小数点記号を取り出す", ("存在しないファセットを指定する", "持っていないと `bad_cast` が投げられます。`has_facet` で確かめます。"), [("[`has_facet`](has_facet.md)", "あるかを調べる"), ("[`numpunct`](numpunct.md)", "数字の記号")])
L("has_facet", "ロケールが、指定したファセット（部品）を持っているかを調べる。", "`use_facet` は、持っていない部品を指定すると例外になります。`has_facet<ファセット>(ロケール)` で先に調べられます。", "template <class Facet>\nbool has_facet(const std::locale& loc) noexcept;",
  [("Facet", "テンプレート引数", "調べるファセットの型"), ("loc", "locale", "対象のロケール")], "持っていれば `true`", 'std::println("{}", std::has_facet<std::ctype<char>>(std::locale::classic()));', "true",
  "独自のファセットが入っているか確かめる", ("標準のファセットを疑う", "標準のロケールは、標準のファセットをすべて持っています。"), [("[`use_facet`](use_facet.md)", "取り出す")])
L("ctype", "文字の分類（数字か、英字か）と、大文字小文字の変換を担当するファセット。", "`isalpha`・`toupper` のようなロケール付きの文字の分類・変換は、`ctype` ファセットが担当しています。`std::use_facet<std::ctype<char>>(loc)` で取り出して使います。", "template <class CharT>\nclass ctype;  // is(), toupper(), tolower(), widen(), narrow() など",
  [("CharT", "型", "文字の型")], "分類・変換の関数をもつ", 'const auto& ct = std::use_facet<std::ctype<char>>(std::locale::classic());\nstd::println("{}", ct.toupper(\'a\'));', "A",
  "ロケールごとの大文字小文字の変換", ("日本語の変換を期待する", "大文字小文字の概念がない文字は変換されません。"), [("[`toupper`](../../numeric/cctype/toupper.md)", "C の関数")])
L("numpunct", "数値の書式（小数点・桁区切り）を担当するファセット。", "小数点が `.` か `,` か、1000 ごとの区切りを何にするかは、国によって違います。その規則を持っているのが `numpunct` ファセットです。`decimal_point()`・`thousands_sep()`・`grouping()` などを返します。", "template <class CharT>\nclass numpunct {\n public:\n  CharT decimal_point() const;\n  CharT thousands_sep() const;\n  std::string grouping() const;\n};",
  [("CharT", "型", "文字の型")], "小数点・桁区切りなど", 'const auto& np = std::use_facet<std::numpunct<char>>(std::locale::classic());\nstd::println("{}", np.decimal_point());', ".",
  "桁区切りを国ごとに変える", ("ストリームに設定し忘れる", "ロケールを `imbue` しないと、書式は変わりません。"), [("[`num_put`](num_put.md)", "数値を書き出す"), ("[`use_facet`](use_facet.md)", "取り出す")])
L("num_put", "数値を文字列に書き出す処理を担当するファセット。", "`cout << 42` が内部で呼んでいるのが、`num_put` です。ロケールの規則（小数点・桁区切り）に従って、数値を文字にして出力先に流します。", "template <class CharT, class OutIt = ostreambuf_iterator<CharT>>\nclass num_put {\n public:\n  OutIt put(OutIt out, std::ios_base& str, CharT fill, long v) const;\n};",
  [("out", "出力イテレータ", "書き出し先"), ("str", "ios_base&", "書式の設定の元になるストリーム"), ("fill", "文字", "幅を埋める文字"), ("v", "数値", "書く値")], "書き終えた後の出力イテレータ", 'std::ostringstream os;\nconst auto& np = std::use_facet<std::num_put<char>>(std::locale::classic());\nnp.put(std::ostreambuf_iterator<char>(os), os, \' \', 42L);\nstd::println("{}", os.str());', "42",
  "自作の出力関数で、ロケール付きの数値を書く", ("直接使う", "ふつうは `<<` を使います。`num_put` は、自作の書式に拡張するときに登場します。"), [("[`num_get`](num_get.md)", "読み込み側"), ("[`numpunct`](numpunct.md)", "書式の記号")], inc=("locale", "print", "sstream", "iterator"))
L("num_get", "文字列から数値を読み込む処理を担当するファセット。", "`cin >> n` が内部で呼んでいるのが、`num_get` です。ロケールの規則（小数点・桁区切り）に従って、文字から数値を作ります。", "template <class CharT, class InIt = istreambuf_iterator<CharT>>\nclass num_get {\n public:\n  InIt get(InIt in, InIt end, std::ios_base& str, std::ios_base::iostate& err, long& v) const;\n};",
  [("in, end", "入力イテレータ", "読み込み元の範囲"), ("str", "ios_base&", "書式の設定の元になるストリーム"), ("err", "iostate&", "エラーの状態を受け取る"), ("v", "数値", "結果を入れる変数")], "読み終えた位置の入力イテレータ", 'std::istringstream in("42");\nstd::istreambuf_iterator<char> b(in);\nstd::istreambuf_iterator<char> e;\nstd::ios_base::iostate err = std::ios_base::goodbit;\nlong v = 0;\nstd::use_facet<std::num_get<char>>(std::locale::classic()).get(b, e, in, err, v);\nstd::println("{}", v);', "42",
  "自作の入力関数で、ロケール付きの数値を読む", ("`err` を確かめない", "読み込みの失敗は `err` に入ります。"), [("[`num_put`](num_put.md)", "書き出し側")], inc=("locale", "print", "sstream", "iterator"))
L("collate", "文字列の照合（辞書順の比較）を担当するファセット。", "文字列の並び順は、言語によって違います。その比較規則を持っているのが `collate` ファセットです。`compare` で 2 つの文字列を比べます。`std::locale` の `operator()` は、これを使って文字列を並べ替えます。", "template <class CharT>\nclass collate {\n public:\n  int compare(const CharT* lo1, const CharT* hi1, const CharT* lo2, const CharT* hi2) const;\n};",
  [("lo1, hi1", "ポインタ", "1 つ目の文字列の範囲"), ("lo2, hi2", "ポインタ", "2 つ目の文字列の範囲")], "`-1`（小さい）・0（等しい）・1（大きい）", 'const char a[] = "a";\nconst char b[] = "b";\nconst auto& co = std::use_facet<std::collate<char>>(std::locale::classic());\nstd::println("{}", co.compare(a, a + 1, b, b + 1));', "-1",
  "名前を言語に合った順で並べ替える", ("文字コード順と同じだと思う", "ロケールによっては、大文字小文字の扱いや、アクセント付き文字の順序が違います。"), [("[`strcoll`](../../memory/cstring/strcoll.md)", "C の関数")])
L("time_put", "日時を、書式に従って文字列に書き出すファセット。", "`put_time` が内部で使っているのが `time_put` です。ロケールの規則（曜日・月の名前など）に従って、`tm` を `strftime` 風の書式で出力します。", "template <class CharT, class OutIt = ostreambuf_iterator<CharT>>\nclass time_put {\n public:\n  OutIt put(OutIt out, std::ios_base& str, CharT fill, const std::tm* t, const CharT* fmt_first, const CharT* fmt_last) const;\n};",
  [("out", "出力イテレータ", "書き出し先"), ("t", "const tm*", "書く日時"), ("fmt_first, fmt_last", "ポインタ", "書式の範囲")], "書き終えた後の出力イテレータ", 'std::tm t{};\nt.tm_year = 124;\nt.tm_mon = 0;\nt.tm_mday = 1;\nstd::ostringstream os;\nconst std::string fmt = "%Y-%m-%d";\nstd::use_facet<std::time_put<char>>(std::locale::classic()).put(std::ostreambuf_iterator<char>(os), os, \' \', &t, fmt.data(), fmt.data() + fmt.size());\nstd::println("{}", os.str());', "2024-01-01",
  "ロケールに従った日時の出力", ("直接使う", "ふつうは `std::put_time` を使います。"), [("[`put_time`](../put_time.md)", "ストリームに書く"), ("[`time_get`](time_get.md)", "読み込み側")], inc=("locale", "print", "sstream", "iterator", "string"))
L("time_get", "日時を、書式に従って文字列から読み込むファセット。", "`get_time` が内部で使っているのが `time_get` です。ロケールの規則に従って、文字列から `tm` を作ります。", "template <class CharT, class InIt = istreambuf_iterator<CharT>>\nclass time_get {\n public:\n  InIt get_time(InIt in, InIt end, std::ios_base& str, std::ios_base::iostate& err, std::tm* t) const;\n};",
  [("in, end", "入力イテレータ", "読み込み元の範囲"), ("err", "iostate&", "エラーの状態を受け取る"), ("t", "tm*", "結果を入れる変数")], "読み終えた位置の入力イテレータ", 'std::istringstream in("12:30:45");\nstd::istreambuf_iterator<char> b(in);\nstd::istreambuf_iterator<char> e;\nstd::tm t{};\nstd::ios_base::iostate err = std::ios_base::goodbit;\nstd::use_facet<std::time_get<char>>(std::locale::classic()).get_time(b, e, in, err, &t);\nstd::println("{} {} {}", t.tm_hour, t.tm_min, t.tm_sec);', "12 30 45",
  "ロケールに従った日時の入力", ("直接使う", "ふつうは `std::get_time` を使います。"), [("[`get_time`](../get_time.md)", "ストリームから読む"), ("[`time_put`](time_put.md)", "書き出し側")], inc=("locale", "print", "sstream", "iterator", "ctime"))
L("money_put", "金額を、ロケールの通貨の書式で書き出すファセット。", "`put_money` が内部で使っているのが `money_put` です。通貨記号、桁区切り、小数点以下の桁数を、`moneypunct` の規則に従って出力します。", "template <class CharT, class OutIt = ostreambuf_iterator<CharT>>\nclass money_put {\n public:\n  OutIt put(OutIt out, bool intl, std::ios_base& str, CharT fill, long double units) const;\n};",
  [("out", "出力イテレータ", "書き出し先"), ("intl", "bool", "国際表記にするか"), ("units", "数値", "金額（最小単位）")], "書き終えた後の出力イテレータ", 'std::ostringstream os;\nos.imbue(std::locale::classic());\nstd::use_facet<std::money_put<char>>(std::locale::classic()).put(std::ostreambuf_iterator<char>(os), false, os, \' \', 12345L);\nstd::println("{}", os.str());', "12345",
  "通貨を国ごとの書式で表示する", ("直接使う", "ふつうは `std::put_money` を使います。"), [("[`put_money`](../put_money.md)", "ストリームに書く"), ("[`moneypunct`](moneypunct.md)", "書式の記号")], inc=("locale", "print", "sstream", "iterator"))
L("money_get", "金額を、ロケールの通貨の書式から読み込むファセット。", "`get_money` が内部で使っているのが `money_get` です。ロケールの通貨の書式を解釈して、金額の数値に直します。", "template <class CharT, class InIt = istreambuf_iterator<CharT>>\nclass money_get {\n public:\n  InIt get(InIt in, InIt end, bool intl, std::ios_base& str, std::ios_base::iostate& err, std::basic_string<CharT>& digits) const;\n};",
  [("in, end", "入力イテレータ", "読み込み元の範囲"), ("intl", "bool", "国際表記か"), ("err", "iostate&", "エラーの状態を受け取る"), ("digits", "string", "結果の数字の文字列")], "読み終えた位置の入力イテレータ", 'std::istringstream in("1234");\nstd::istreambuf_iterator<char> b(in);\nstd::istreambuf_iterator<char> e;\nstd::ios_base::iostate err = std::ios_base::goodbit;\nstd::string digits;\nstd::use_facet<std::money_get<char>>(std::locale::classic()).get(b, e, false, in, err, digits);\nstd::println("{}", digits);', "1234",
  "通貨の入力を解釈する", ("直接使う", "ふつうは `std::get_money` を使います。"), [("[`get_money`](../get_money.md)", "ストリームから読む"), ("[`money_put`](money_put.md)", "書き出し側")], inc=("locale", "print", "sstream", "iterator", "string"))
L("moneypunct", "通貨の書式（記号・桁区切り・小数点以下の桁数）を担当するファセット。", "通貨の書式は、国によって大きく違います。その規則を持っているのが `moneypunct` ファセットです。`frac_digits()`（小数点以下の桁数）・`curr_symbol()`（通貨記号）などを返します。", "template <class CharT, bool International = false>\nclass moneypunct {\n public:\n  int frac_digits() const;\n  std::basic_string<CharT> curr_symbol() const;\n};",
  [("CharT", "型", "文字の型"), ("International", "bool", "国際表記か")], "通貨の書式の情報", 'const auto& mp = std::use_facet<std::moneypunct<char>>(std::locale::classic());\nstd::println("{}", mp.frac_digits());', "0",
  "通貨の小数点以下の桁数を調べる", ("日本円だと思う", "クラシックロケールは通貨の設定が空です。`ja_JP` などのロケールを使います。"), [("[`money_put`](money_put.md)", "書き出し")])
L("messages", "メッセージ（翻訳された文字列）をカタログから取り出すファセット。", "ゲームの多言語対応で、メッセージのカタログ（翻訳ファイル）から、言語ごとの文字列を取り出すための仕組みです。POSIX の `catgets` / gettext 風の機能で、Windows ではあまり使われません。", "template <class CharT>\nclass messages {\n public:\n  catalog open(const std::string& name, const std::locale& loc) const;\n  std::basic_string<CharT> get(catalog c, int set, int msgid, const std::basic_string<CharT>& dfault) const;\n  void close(catalog c) const;\n};",
  [("name", "string", "カタログの名前"), ("loc", "locale", "ロケール")], "カタログの識別子", '// 例: カタログを開いてメッセージを取り出す\n// auto cat = std::use_facet<std::messages<char>>(loc).open("game", loc);', None,
  "（POSIX の環境での翻訳）", ("Windows で使う", "標準のカタログ機能は、環境によってほぼ使えません。多言語対応は別のライブラリ（gettext など）を使います。"), [("[`std::locale`](../locale.md)", "ロケール")])
L("codecvt", "文字コードの変換を担当するファセット。", "ファイルの文字コードと、メモリ上の文字コードが違うとき、変換を担当するのが `codecvt` ファセットです。ストリームの `imbue` で、変換規則を設定します。`always_noconv()` が `true` なら、変換は不要です。", "template <class InternT, class ExternT, class StateT>\nclass codecvt {\n public:\n  bool always_noconv() const noexcept;\n  result in(StateT& state, const ExternT* from, const ExternT* from_end, const ExternT*& from_next, InternT* to, InternT* to_end, InternT*& to_next) const;\n};",
  [("InternT", "型", "メモリ上の文字の型"), ("ExternT", "型", "ファイル側の文字の型"), ("StateT", "型", "変換の途中状態（`mbstate_t`）")], "変換結果（`ok`・`partial`・`error`・`noconv`）", 'const auto& cv = std::use_facet<std::codecvt<char, char, std::mbstate_t>>(std::locale::classic());\nstd::println("{}", cv.always_noconv());', "true",
  "UTF-8 のファイルを読んで UTF-16 に変換する", ("`codecvt_utf8` を新しいコードで使う", "標準の変換ファセットの多くは C++17 で非推奨です。変換は変換用ライブラリ（ICU など）か、OS の API を使います。"), [("[`codecvt_utf8`](codecvt_utf8.md)", "UTF-8 の変換")])
L("codecvt_utf8", "UTF-8 と、UCS-2 / UTF-32 を変換するファセット（非推奨）。", "UTF-8 と、`char32_t` や `wchar_t` の間で変換するための、標準のファセットです。`wstring_convert` と組み合わせて使われましたが、C++17 で非推奨になりました。新しいコードでは、OS の API（`MultiByteToWideChar`）や ICU を使います。", "template <class Elem, unsigned long Maxcode = 0x10ffff, codecvt_mode Mode = codecvt_mode(0)>\nclass codecvt_utf8 : public codecvt<Elem, char, mbstate_t>;",
  [("Elem", "型", "メモリ上の文字の型（`char32_t` など）")], "UTF-8 との変換をするファセット", 'std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;\nstd::string s = conv.to_bytes(U\'あ\');\nstd::println("{}", s.size());', "3",
  "（古いコードの保守）", ("新しいコードで使う", "C++17 で非推奨になり、将来削除されます。"), [("[`codecvt`](codecvt.md)", "元のファセット"), ("[文字コード](@/encoding/index.md)", "変換の考え方")], inc=("codecvt", "locale", "print", "string"), ver=("11", "C++11"))
L("setlocale", "C のロケールを設定・取得する。", "`printf` や `strftime` など、C 由来の関数のロケールを設定します。`setlocale(LC_ALL, \"\")` で、環境のロケールを設定します。C++ のストリームのロケール（`std::locale`）とは別のものです。", "char* setlocale(int category, const char* locale);",
  [("category", "int", "対象の分類（`LC_ALL`・`LC_NUMERIC` など）"), ("locale", "const char*", "ロケール名（`nullptr` で取得のみ）")], "設定後のロケール名。失敗したら `nullptr`", 'std::println("{}", std::setlocale(LC_ALL, "C"));', "C",
  "コンソールの文字化けを防ぐ（環境のロケールを設定）", ("C++ のストリームにも効くと思う", "`std::locale::global` を使います。"), [("[`localeconv`](localeconv.md)", "現在の書式を調べる"), ("[`std::locale`](../locale.md)", "C++ のロケール")], inc=("clocale", "print"), cr="setlocale")
L("localeconv", "現在のロケールの数値・通貨の書式情報を取得する。", "C のロケールに設定されている、小数点記号・桁区切り・通貨記号などを、`lconv` 構造体で取得します。", "std::lconv* localeconv();",
  [], "`lconv` へのポインタ（書き換え禁止）", 'std::println("{}", std::localeconv()->decimal_point);', ".",
  "ロケールの小数点記号を調べる", ("戻り値を書き換える", "戻り値は読み取り専用です。次の `setlocale` で書き換わります。"), [("[`lconv`](lconv.md)", "構造体"), ("[`setlocale`](setlocale.md)", "ロケールを設定する")], inc=("clocale", "print"))
L("lconv", "数値と通貨の書式情報をまとめた構造体。", "`localeconv()` が返す構造体です。`decimal_point`（小数点）、`thousands_sep`（桁区切り）、`grouping`（桁のグループ）、`currency_symbol`（通貨記号）などのメンバをもちます。", "struct lconv {\n  char* decimal_point;\n  char* thousands_sep;\n  char* grouping;\n  char* currency_symbol;\n  // ...\n};",
  [], "なし（構造体）", 'const std::lconv* lc = std::localeconv();\nstd::println("{}", lc->thousands_sep[0] == \'\\0\');', "true",
  "桁区切りが設定されているかを調べる", ("文字列として保存せず、ポインタを保持する", "ポインタは、次の `setlocale` で無効になります。必要ならコピーします。"), [("[`localeconv`](localeconv.md)", "取得する関数")], inc=("clocale", "print"))

if __name__ == "__main__":
    flush_hubs()
