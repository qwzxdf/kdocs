"""バッチ 11: 例外・system_error・new・compare・コンテナ周辺の未登録分。"""
from mk import *  # noqa: F401,F403
from pathlib import Path

EX = "support/exceptions/"
EXI = "[例外](@/basics/index.md) の基本と、[`std::exception`](exception.md) を先に読んでください。"
EXH = None


def E(rel, name, summary, intro, sig, args, ret, body, out, use, miss, sim, inc=("exception", "print"), pre="", ver=None, tips=None, cx="定数", rank="rare", cr=None, rjd="exception", info=EXI, group=None):
    Q(rel, name, summary, rank, list(inc), intro, tips or ["例外の関連の部品。", "`try` / `catch` と組み合わせて使う。", "ゲームでは、ファイルや外部入力のエラーの扱いに登場する。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx=cx, ver=ver, info=info, pre=pre, rj=f"{rjd}/{Path(rel).stem}.html", cr=f"error/{cr or Path(rel).stem}", **({"group": group} if group else {}))


# ---- stdexcept
for nm, base, what, intro, ex in [
    ("domain_error", "logic_error", "関数の定義域の外の引数を表す例外。", "数学関数の引数が、定義されている範囲の外にあるときに使う例外です（`sqrt` に負の数を渡す、など）。`logic_error` の仲間で、プログラムの書き方で防げるエラーです。", "domain_error"),
    ("range_error", "runtime_error", "計算の結果が、表せる範囲を超えたことを表す例外。", "引数は正しいのに、計算した結果が型の範囲に収まらない、という実行時のエラーを表します。`overflow_error`・`underflow_error` の親にあたるものではなく、`runtime_error` の仲間のひとつです。", "range_error"),
    ("underflow_error", "runtime_error", "計算の結果が小さすぎて表せないことを表す例外。", "浮動小数点で、0 に近すぎて表せない結果（アンダーフロー）になったことを表します。標準のライブラリが自動で投げることは少なく、自分のコードで使います。", "underflow_error")]:
    E(EX + nm + ".md", "std::" + nm, what, intro, f"class {nm} : public {base} {{\n public:\n  explicit {nm}(const std::string& what_arg);\n  explicit {nm}(const char* what_arg);\n}};",
      [("what_arg", "文字列", "エラーの説明（`what()` で取り出せる）")], "`what()` が説明を返す",
      f'try {{\n  throw std::{ex}("bad input");\n}} catch (const std::{base}& e) {{\n  std::println("{{}}", e.what());\n}}', "bad input",
      "自作の関数で、引数や結果の異常を知らせる", ("ゲームの通常のフローに使う", "例外は遅いので、頻繁に起きるエラーには使いません。戻り値や `expected` を使います。"), [(f"[`{base}`]({base}.md)", "親のクラス")], inc=("stdexcept", "print"), tips=[f"`{base}` から派生。", "`throw` するときに説明の文字列を渡す。", "`what()` で説明を取り出す。"])

# ---- exception.h 周辺
E(EX + "bad_exception.md", "std::bad_exception", "予期しない例外を表す例外クラス。", "かつての「動的例外仕様」に反する例外が出たときに、投げられていた型です。例外仕様は C++17 で削除されたので、いまは使われません。名前だけが残っている、歴史的な型です。",
  "class bad_exception : public exception {\n public:\n  const char* what() const noexcept override;\n};", [], "`what()` はエラーを表す文字列",
  'try {\n  throw std::bad_exception();\n} catch (const std::exception& e) {\n  std::println("caught");\n}', "caught", "（現在はほぼ使われない）", ("新しいコードで期待する", "動的例外仕様は削除されたので、標準が自動でこれを投げることはありません。"), [("[`exception`](exception.md)", "親のクラス")], tips=["`std::exception` から派生。", "C++17 で削除された例外仕様（`throw(...)`）に関係していた。", "いまは使わない。"])
E(EX + "nested_exception.md", "std::nested_exception", "別の例外を中に抱えられる例外の土台。", "「ファイルを開けなかった」という低レベルの例外を、「セーブに失敗した」という高レベルの例外に包んで投げ直したい、ということがあります。元の例外の情報を失わずに包めるのが、`nested_exception` です。ふつうは [`throw_with_nested`](throw_with_nested.md) 経由で使います。",
  "class nested_exception {\n public:\n  nested_exception() noexcept;  // 今処理中の例外を覚える\n  exception_ptr nested_ptr() const noexcept;\n  [[noreturn]] void rethrow_nested() const;\n};", [], "`nested_ptr()` が包んだ例外へのポインタ",
  'try {\n  try {\n    throw std::runtime_error("inner");\n  } catch (...) {\n    std::throw_with_nested(std::logic_error("outer"));\n  }\n} catch (const std::exception& e) {\n  std::println("{}", e.what());\n  try {\n    std::rethrow_if_nested(e);\n  } catch (const std::exception& inner) {\n    std::println("{}", inner.what());\n  }\n}', "outer\ninner",
  "ロード失敗の原因の鎖を保つ", ("`catch` の外で作る", "`nested_exception` を作るとき、例外の処理中（`catch` の中）でないと、包むものがありません。"), [("[`throw_with_nested`](throw_with_nested.md)", "包んで投げる"), ("[`rethrow_if_nested`](rethrow_if_nested.md)", "包まれたものを取り出す")], inc=("exception", "stdexcept", "print"), ver=("11", "C++11"))
E(EX + "throw_with_nested.md", "std::throw_with_nested", "いま処理中の例外を包んだ上で、新しい例外を投げる。", "低レベルの例外を `catch` して、意味のある高レベルの例外に変えたいが、元の原因も残したいとき、`catch` の中で `throw_with_nested(新しい例外)` を呼びます。新しい例外の中に、元の例外が入った状態で投げられます。",
  "template <class T>\n[[noreturn]] void throw_with_nested(T&& t);", [("t", "例外", "投げる新しい例外")], "戻らない（例外を投げる）",
  'try {\n  try {\n    throw std::runtime_error("file not found");\n  } catch (...) {\n    std::throw_with_nested(std::runtime_error("save failed"));\n  }\n} catch (const std::exception& e) {\n  std::println("{}", e.what());\n}', "save failed",
  "ロード処理の失敗の理由をたどれるようにする", ("`catch` の外で呼ぶ", "処理中の例外がないと、包むものがなく、`std::terminate` になることがあります。"), [("[`nested_exception`](nested_exception.md)", "包まれた形"), ("[`rethrow_if_nested`](rethrow_if_nested.md)", "取り出す")], inc=("exception", "stdexcept", "print"), ver=("11", "C++11"))
E(EX + "rethrow_if_nested.md", "std::rethrow_if_nested", "包まれた例外があれば、それを取り出して投げ直す。", "`throw_with_nested` で包まれた例外には、元の例外が入っています。`rethrow_if_nested(e)` は、`e` が包まれた例外をもっていれば、それを投げ直し、もっていなければ何もしません。再帰で原因の鎖をたどるときに使います。",
  "template <class E>\nvoid rethrow_if_nested(const E& e);", [("e", "例外", "調べる例外")], "なし（包まれた例外があれば投げ直す）",
  'try {\n  try {\n    throw std::runtime_error("inner");\n  } catch (...) {\n    std::throw_with_nested(std::logic_error("outer"));\n  }\n} catch (const std::exception& e) {\n  std::println("{}", e.what());\n  try {\n    std::rethrow_if_nested(e);\n  } catch (const std::exception& inner) {\n    std::println("{}", inner.what());\n  }\n}', "outer\ninner",
  "例外の原因の鎖をログに全部出す", ("包まれていない例外を気にして `try` を省く", "包まれていなければ何も起きません。`catch` の中で使うので、`try` で囲む必要があります。"), [("[`throw_with_nested`](throw_with_nested.md)", "包んで投げる")], inc=("exception", "stdexcept", "print"), ver=("11", "C++11"))
E(EX + "current_exception.md", "std::current_exception", "いま処理中の例外を、exception_ptr として取り出す。", "例外をそのまま別のスレッドに渡したい、あとで投げ直したい、というときに、`catch` の中で `current_exception()` を呼んで `exception_ptr` に保存します。`catch` の外で呼ぶと、空の `exception_ptr` が返ります。",
  "std::exception_ptr current_exception() noexcept;", [], "処理中の例外の `exception_ptr`（なければ空）",
  'try {\n  throw std::runtime_error("boom");\n} catch (...) {\n  std::exception_ptr p = std::current_exception();\n  std::println("{}", p != nullptr);\n}\nstd::println("{}", std::current_exception() != nullptr);', "true\nfalse",
  "別スレッドの例外をメインスレッドに渡す", ("`catch` の外で呼ぶ", "処理中の例外がないと、空のポインタが返ります。"), [("[`exception_ptr`](exception_ptr.md)", "例外を持ち歩く型"), ("[`rethrow_exception`](rethrow_exception.md)", "投げ直す")], inc=("exception", "stdexcept", "print"), ver=("11", "C++11"))
E(EX + "rethrow_exception.md", "std::rethrow_exception", "保存した exception_ptr の例外を、もう一度投げる。", "`current_exception()` や `make_exception_ptr()` で保存した例外を、別の場所で投げ直します。`std::async` や `future::get` が、別スレッドの例外を呼び出し元に渡す仕組みも、この関数と同じ考え方です。",
  "[[noreturn]] void rethrow_exception(std::exception_ptr p);", [("p", "exception_ptr", "投げ直す例外（空でないこと）")], "戻らない（例外を投げる）",
  'std::exception_ptr p = std::make_exception_ptr(std::runtime_error("boom"));\ntry {\n  std::rethrow_exception(p);\n} catch (const std::runtime_error& e) {\n  std::println("{}", e.what());\n}', "boom",
  "ワーカースレッドの例外をメインスレッドで投げ直す", ("空のポインタを渡す", "空の `exception_ptr` を渡すと未定義動作です。"), [("[`current_exception`](current_exception.md)", "保存する"), ("[`make_exception_ptr`](make_exception_ptr.md)", "例外から作る")], inc=("exception", "stdexcept", "print"), ver=("11", "C++11"))
E(EX + "make_exception_ptr.md", "std::make_exception_ptr", "例外オブジェクトから、exception_ptr を作る。", "`throw` せずに、例外オブジェクトを `exception_ptr` に包みたいことがあります（`promise::set_exception` に渡すときなど）。`make_exception_ptr(e)` が、`throw` と `catch` を省いて作ってくれます。",
  "template <class E>\nstd::exception_ptr make_exception_ptr(E e) noexcept;", [("e", "例外", "包む例外オブジェクト")], "包んだ `exception_ptr`",
  'std::exception_ptr p = std::make_exception_ptr(std::runtime_error("boom"));\ntry {\n  std::rethrow_exception(p);\n} catch (const std::exception& e) {\n  std::println("{}", e.what());\n}', "boom",
  "`promise` にエラーを入れる", ("例外の型が切り落とされる", "値渡しで受けるので、派生クラスを渡すなら、そのままの型で渡します。基底型の変数に入れると切り落とされます。"), [("[`rethrow_exception`](rethrow_exception.md)", "投げ直す"), ("[`current_exception`](current_exception.md)", "処理中の例外を取る")], inc=("exception", "stdexcept", "print"), ver=("11", "C++11"))
E(EX + "set_terminate.md", "std::set_terminate", "プログラムが異常終了する直前に呼ばれる関数を設定する。", "`catch` されない例外が出ると、`std::terminate` が呼ばれて終了します。その直前に、ログを書いたり、クラッシュレポートを出したりしたいときは、`set_terminate` で自分の関数を設定します。設定した関数は、最後にプログラムを終了させる必要があります。",
  "std::terminate_handler set_terminate(std::terminate_handler f) noexcept;", [("f", "関数ポインタ", "`void()` の関数")], "それまでのハンドラ",
  'std::set_terminate(Handler);\nstd::println("{}", std::get_terminate() == Handler);', "true",
  "クラッシュ時にログを書き出す", ("ハンドラから戻る", "ハンドラは戻ってはいけません。`std::abort()` などで終了させます。"), [("[`get_terminate`](get_terminate.md)", "現在のハンドラを取る"), ("[`terminate`](terminate.md)", "終了する")], inc=("exception", "cstdlib", "print"), ver=None,
  pre="void Handler() {\n  std::abort();\n}")
E(EX + "get_terminate.md", "std::get_terminate", "現在設定されている terminate ハンドラを取得する。", "`set_terminate` で設定したハンドラを、あとで読み出します。ハンドラを一時的に差し替えて、あとで元に戻したいときなどに使います。",
  "std::terminate_handler get_terminate() noexcept;", [], "現在のハンドラ（既定ではライブラリが決めた関数）",
  'std::terminate_handler h = std::get_terminate();\nstd::println("{}", h != nullptr);', "true",
  "ハンドラを一時的に差し替えて元に戻す", ("ヌルだと思う", "既定でも、ライブラリが用意した関数が返ります。"), [("[`set_terminate`](set_terminate.md)", "ハンドラを設定する")], inc=("exception", "print"), ver=("11", "C++11"))
E(EX + "uncaught_exceptions.md", "std::uncaught_exceptions", "いま処理中（スタックを巻き戻している最中）の例外の数を返す。", "デストラクタの中で、「例外のせいで呼ばれたのか、普通に抜けたのか」を知りたいことがあります（スコープガードが、失敗したときだけ後始末をする場合など）。`uncaught_exceptions()` が、いま巻き戻している最中の例外の数を返します。",
  "int uncaught_exceptions() noexcept;", [], "処理中の例外の数", '{\n  Guard g;\n}\ntry {\n  Guard g;\n  throw 1;\n} catch (...) {\n}', "0\n1",
  "スコープガードで、成功と失敗を区別する", ("`uncaught_exception()`（単数）を使う", "古い `uncaught_exception()` は C++17 で削除されました。数を返す版を使います。"), [("[`exception_ptr`](exception_ptr.md)", "例外を持ち歩く")], inc=("exception", "print"), ver=("17", "C++17"),
  pre="struct Guard {\n  ~Guard() { std::println(\"{}\", std::uncaught_exceptions()); }\n};")
E(EX + "bad_typeid.md", "std::bad_typeid", "ヌルの多態型ポインタに typeid を使ったときの例外。", "`typeid(*p)` で、仮想関数を持つクラスの実際の型を調べるとき、`p` が `nullptr` だと、`bad_typeid` が投げられます。ふつうの `nullptr` の参照は未定義動作ですが、この場合に限って例外になる、と決められています。",
  "class bad_typeid : public exception {\n public:\n  const char* what() const noexcept override;\n};", [], "`what()` はエラーを表す文字列",
  'Base* p = nullptr;\ntry {\n  std::println("{}", typeid(*p).name() != nullptr);\n} catch (const std::bad_typeid&) {\n  std::println("bad_typeid");\n}', "bad_typeid",
  "実行時の型を調べる処理の安全確認", ("非多態型で期待する", "仮想関数を持たない型では、`typeid` は静的な型を返し、例外になりません。"), [("[`typeid`](../typeid.md)", "実行時の型"), ("[`bad_cast`](bad_cast.md)", "`dynamic_cast` の失敗")], inc=("typeinfo", "print"), pre="struct Base {\n  virtual ~Base() = default;\n};", ver=None, rjd="typeinfo", cr="bad_typeid")
E("memory/new_delete/bad_array_new_length.md", "std::bad_array_new_length", "配列の new で、要素数が不正だったときの例外。", "`new int[n]` で、`n` が負だったり、確保できる上限を超えていたりすると、`bad_alloc` の派生の `bad_array_new_length` が投げられます。メモリ不足の `bad_alloc` と区別して、要素数のミスを知らせます。",
  "class bad_array_new_length : public bad_alloc {\n public:\n  const char* what() const noexcept override;\n};", [], "`what()` はエラーを表す文字列",
  'volatile int n = -1;\ntry {\n  int* p = new int[n];\n  delete[] p;\n} catch (const std::bad_array_new_length&) {\n  std::println("bad length");\n}', "bad length",
  "外から読み込んだ要素数で配列を確保する前の保険", ("要素数を検査せずに使う", "ファイルから読んだ数でそのまま `new[]` せず、範囲を確かめてから確保します。"), [("[`bad_alloc`](../../support/exceptions/bad_alloc.md)", "メモリ不足")], inc=("new", "print"), ver=("11", "C++11"), info="[`new[]` と `delete[]`](new_array.md) を先に読んでください。", group="new / delete まわり", rjd="new")
E("memory/new_delete/get_new_handler.md", "std::get_new_handler", "現在設定されている new ハンドラを取得する。", "`new` でメモリが足りなくなったとき、呼ばれる関数が `new_handler` です。いま設定されているものを `get_new_handler()` で取り出せます。一時的に差し替えて元に戻すときなどに使います。",
  "std::new_handler get_new_handler() noexcept;", [], "現在のハンドラ（未設定なら `nullptr`）", 'std::println("{}", std::get_new_handler() == nullptr);', "true",
  "メモリ不足時の動作を一時的に変える", ("ヌルのまま呼ぶ", "戻り値は未設定のとき `nullptr` です。呼ぶ前に確かめます。"), [("[`set_new_handler`](set_new_handler.md)", "ハンドラを設定する")], inc=("new", "print"), ver=("11", "C++11"), info="[`set_new_handler`](set_new_handler.md) を先に読んでください。", group="new / delete まわり", rjd="new")
E("memory/hardware_constructive_interference_size.md", "std::hardware_constructive_interference_size", "同じキャッシュラインに載せたいデータの、大きさの上限。", "2 つのデータを同時に読み書きするなら、同じキャッシュラインに乗せたほうが速くなります。逆に、別のスレッドが別々に書き込むデータは、別のラインに離すべきです（偽共有の回避）。`hardware_constructive_interference_size` は、前者の「同じラインに収める」上限の目安です。",
  "inline constexpr std::size_t hardware_constructive_interference_size = /* 実装定義 */;", [], "キャッシュラインの大きさ（多くは 64）", 'std::println("{}", std::hardware_constructive_interference_size > 0);', "true",
  "一緒に使うデータをキャッシュ 1 ライン内にまとめる", ("コンパイル環境と実行環境が違う", "値はコンパイル時に決まります。別の CPU で動かすとずれることがあります。"), [("[`hardware_destructive_interference_size`](hardware_destructive_interference_size.md)", "離すべき距離")], inc=("new", "print"), ver=("17", "C++17"), info="[`hardware_destructive_interference_size`](hardware_destructive_interference_size.md) を先に読んでください。", rjd="new")

# ---- system_error
SE = "support/"
SEI = "[`std::error_code`](error_code.md) を先に読んでください。"
GRP = "エラーコード（<system_error>）"
E(SE + "error_category.md", "std::error_category", "エラーコードの種類（分類）を表す基底クラス。", "`error_code` の数値は、それだけでは意味が決まりません。`2` はファイルシステムでは「ファイルがない」、自作のゲームでは別の意味かもしれません。数値の意味を決めるのが `error_category` で、自分のエラーの種類を足したいときは、この基底クラスを継承して作ります。",
  "class error_category {\n public:\n  virtual const char* name() const noexcept = 0;\n  virtual std::string message(int condition) const = 0;\n  virtual bool equivalent(const error_code& code, int condition) const noexcept;\n  // ...\n};", [], "`name()` は分類の名前、`message(c)` は説明",
  'std::error_code ec(1, Game());\nstd::println("{}: {}", ec.category().name(), ec.message());', "game: out of mana",
  "ゲーム固有のエラーコードに名前をつける", ("カテゴリを関数ごとに作る", "カテゴリは**1 つの実体**（グローバルに 1 つ）である必要があります。`static` の関数内変数で返します。"), [("[`error_code`](error_code.md)", "エラーコード"), ("[`generic_category`](generic_category.md)", "標準の分類")], inc=("system_error", "string", "print"), ver=("11", "C++11"), info=SEI, group=GRP,
  pre="struct GameCategory : std::error_category {\n  const char* name() const noexcept override { return \"game\"; }\n  std::string message(int c) const override { return c == 1 ? \"out of mana\" : \"unknown\"; }\n};\nconst GameCategory& Game() {\n  static GameCategory c;\n  return c;\n}")
for nm, nme, desc in [("generic_category", "generic", "OS に依存しない標準のエラー（`errc`）の分類"), ("system_category", "system", "OS 固有のエラー（Windows の `GetLastError`、POSIX の `errno`）の分類"), ("iostream_category", "iostream", "入出力ストリームのエラー（`io_errc`）の分類")]:
    E(SE + nm + ".md", "std::" + nm, f"{desc}を表す error_category を返す。", f"`error_code` を作るとき、数値がどの分類に属するかを指定します。`{nm}()` は、{desc}の唯一の実体を返します。`name()` は `\"{nme}\"` です。",
      f"const std::error_category& {nm}() noexcept;", [], f"{desc}の `error_category` への参照", f'std::println("{{}}", std::{nm}().name());', nme,
      "OS のエラーと標準のエラーを区別する", ("カテゴリの違うコードを `==` で比べる", "数値が同じでも、分類が違えば別のエラーです。比べるときは `error_condition` に直します。"), [("[`error_category`](error_category.md)", "基底クラス"), ("[`error_code`](error_code.md)", "エラーコード")], inc=("system_error", "print"), ver=("11", "C++11"), info=SEI, group=GRP)
E(SE + "make_error_code.md", "std::make_error_code", "errc などの列挙値から、error_code を作る。", "`std::errc::no_such_file_or_directory` のような、読みやすい名前の列挙値から、`error_code` を作ります。自作のエラー列挙型にも、同じ名前の関数を定義すると、`error_code` に暗黙に変換できるようになります。",
  "std::error_code make_error_code(std::errc e) noexcept;", [("e", "errc", "標準のエラーの列挙値")], "対応する `error_code`", 'std::error_code ec = std::make_error_code(std::errc::no_such_file_or_directory);\nstd::println("{}", ec.value() == ENOENT);', "true",
  "ファイル操作の失敗を、標準のエラーとして返す", ("`value()` を直接比べる", "OS によって `value()` の数値は違います。`ec == std::errc::...` で比べます。"), [("[`make_error_condition`](make_error_condition.md)", "移植性のある条件を作る"), ("[`is_error_code_enum`](is_error_code_enum.md)", "自作の列挙型を対応させる")], inc=("system_error", "cerrno", "print"), ver=("11", "C++11"), info=SEI, group=GRP)
E(SE + "make_error_condition.md", "std::make_error_condition", "errc などの列挙値から、error_condition を作る。", "`error_condition` は、OS に依存しない、移植性のあるエラーの条件です。`error_code`（OS 固有の値）と比べるときに使い、`ec == make_error_condition(errc::...)` の形で、エラーの種類を判定できます。",
  "std::error_condition make_error_condition(std::errc e) noexcept;", [("e", "errc", "標準のエラーの列挙値")], "対応する `error_condition`", 'std::error_code ec = std::make_error_code(std::errc::invalid_argument);\nstd::error_condition c = std::make_error_condition(std::errc::invalid_argument);\nstd::println("{}", ec == c);', "true",
  "OS が違っても同じ書き方でエラーを判定する", ("`error_code` と `error_condition` を混同する", "`error_code` は具体的な値、`error_condition` は移植性のある意味です。比較は条件に対して行います。"), [("[`make_error_code`](make_error_code.md)", "コードを作る"), ("[`error_condition`](error_condition.md)", "エラー条件")], inc=("system_error", "print"), ver=("11", "C++11"), info=SEI, group=GRP)
E(SE + "is_error_code_enum.md", "std::is_error_code_enum", "自作の列挙型を、error_code に暗黙変換できるようにする特性。", "ゲーム固有のエラー（`GameError::OutOfMana`）を、`std::error_code` として扱いたいとき、`is_error_code_enum<GameError>` を `true_type` に特殊化し、`make_error_code(GameError)` を定義します。すると、`std::error_code ec = GameError::OutOfMana;` と書けます。",
  "template <class T>\nstruct is_error_code_enum : false_type {};\ntemplate <class T>\ninline constexpr bool is_error_code_enum_v = is_error_code_enum<T>::value;", [("T", "型", "調べる列挙型")], "`error_code` に変換できる列挙型なら `true`",
  'std::error_code ec = GameError::OutOfMana;\nstd::println("{}", ec.message());', "out of mana",
  "自作のエラー列挙型を標準のエラーの仕組みに乗せる", ("`std` 名前空間の外で特殊化する", "特殊化は `namespace std` の中に書きます。`make_error_code` は、列挙型と同じ名前空間に置きます。"), [("[`error_category`](error_category.md)", "分類を作る"), ("[`make_error_code`](make_error_code.md)", "コードを作る")], inc=("system_error", "string", "print"), ver=("11", "C++11"), info=SEI, group=GRP,
  pre="struct GameCategory : std::error_category {\n  const char* name() const noexcept override { return \"game\"; }\n  std::string message(int c) const override { return c == 1 ? \"out of mana\" : \"unknown\"; }\n};\nconst GameCategory& Game() {\n  static GameCategory c;\n  return c;\n}\n\nenum class GameError { OutOfMana = 1 };\n\nnamespace std {\ntemplate <>\nstruct is_error_code_enum<GameError> : true_type {};\n}  // namespace std\n\nstd::error_code make_error_code(GameError e) {\n  return {static_cast<int>(e), Game()};\n}")
E(SE + "is_error_condition_enum.md", "std::is_error_condition_enum", "自作の列挙型を、error_condition に暗黙変換できるようにする特性。", "`is_error_code_enum` の、`error_condition` 版です。`std::errc` がこれに対応しています。自作の列挙型を、移植性のあるエラー条件として使いたいときに特殊化します。",
  "template <class T>\nstruct is_error_condition_enum : false_type {};\ntemplate <class T>\ninline constexpr bool is_error_condition_enum_v = is_error_condition_enum<T>::value;", [("T", "型", "調べる列挙型")], "`error_condition` に変換できる列挙型なら `true`",
  'std::println("{}", std::is_error_condition_enum_v<std::errc>);\nstd::println("{}", std::is_error_condition_enum_v<int>);', "true\nfalse",
  "エラーの意味を表す列挙型を作る", ("`is_error_code_enum` と取り違える", "変換先が違います。コード（具体的な値）か、条件（移植性のある意味）かで使い分けます。"), [("[`is_error_code_enum`](is_error_code_enum.md)", "error_code の版")], inc=("system_error", "print"), ver=("11", "C++11"), info=SEI, group=GRP)
E(SE + "io_errc.md", "std::io_errc", "入出力ストリームのエラーを表す列挙型。", "`ios_base::failure` の `code()` は、`io_errc::stream` を返します。ストリームのエラーを、標準の `error_code` の仕組みで扱うための列挙型です。",
  "enum class io_errc { stream = 1 };\nconst error_category& iostream_category() noexcept;", [], "`io_errc::stream` だけがある",
  'std::error_code ec = std::make_error_code(std::io_errc::stream);\nstd::println("{}", ec.category().name());', "iostream",
  "ストリームの例外を `error_code` として扱う", ("`failbit` と取り違える", "`io_errc` は例外のコード、`failbit` はストリームの状態のフラグです。"), [("[`iostream_category`](iostream_category.md)", "分類")], inc=("system_error", "ios", "print"), ver=("11", "C++11"), info=SEI, group=GRP)

# ---- compare
CM = "support/"
CMI = "[`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。"
CMG = "比較（<compare>）"


def C3(name, summary, intro, sig, args, ret, body, out, use, miss, sim, pre="", inc=("compare", "print"), ver=("20", "C++20"), cx="定数"):
    Q(CM + name + ".md", "std::" + name, summary, "rare", list(inc), intro, ["`<compare>` の部品。", "C++20 の三方比較（`<=>`）と組み合わせて使う。", "ふつうは `=default` の `<=>` で足りる。"],
      sig, args, ret, body, out, use=use, miss=miss, sim=sim, cx=cx, ver=ver, info=CMI, pre=pre, rj=f"compare/{name}.html", cr=f"utility/{name}", group=CMG)


C3("common_comparison_category", "複数の順序型から、全部を含む共通の順序型を求める。", "`strong_ordering`・`weak_ordering`・`partial_ordering` のうち、複数のメンバが混ざった構造体の `<=>` の戻り値は、一番弱いものに合わせる必要があります。`common_comparison_category_t<...>` が、その型を求めます。",
   "template <class... Ts>\nstruct common_comparison_category { using type = /* 共通の順序型 */; };", [("Ts...", "順序型", "比べる順序型")], "共通の順序型（`::type`）", 'using R = std::common_comparison_category_t<std::strong_ordering, std::partial_ordering>;\nstd::println("{}", std::is_same_v<R, std::partial_ordering>);', "true",
   "メンバごとに順序型が違う構造体の `<=>` の戻り値を決める", ("強い順序型と思い込む", "1 つでも `partial_ordering`（`double` など）が混ざると、全体が `partial_ordering` になります。"), [("[`partial_ordering`](partial_ordering.md)", "半順序")], inc=("compare", "type_traits", "print"))
C3("compare_three_way", "`<=>` を関数オブジェクトにしたもの。", "`std::less` が `<` を関数オブジェクトにしたように、`compare_three_way` は `<=>` を関数オブジェクトにしたものです。アルゴリズムに三方比較を渡したいときに使います。",
   "struct compare_three_way {\n  template <class T, class U>\n  constexpr auto operator()(T&& t, U&& u) const;  // t <=> u\n};", [("t, u", "型", "比べる 2 つの値")], "`t <=> u` の結果（順序型）", 'std::println("{}", std::compare_three_way{}(1, 2) == std::strong_ordering::less);', "true",
   "`lexicographical_compare_three_way` の比較に渡す", ("`std::less` と取り違える", "`less` は `bool`、`compare_three_way` は 3 通りの順序型を返します。"), [("[`spaceship`](spaceship.md)", "`<=>` 演算子")])
C3("compare_three_way_result", "`<=>` の戻り値の型を求める。", "型 `T` を `<=>` で比べたときの結果の型（`strong_ordering` か `partial_ordering` など）を、テンプレートの中で知りたいときに使います。",
   "template <class T, class U = T>\nstruct compare_three_way_result { using type = /* <=> の結果の型 */; };", [("T, U", "型", "比べる 2 つの型")], "順序型（`::type`）", 'std::println("{}", std::is_same_v<std::compare_three_way_result_t<int>, std::strong_ordering>);\nstd::println("{}", std::is_same_v<std::compare_three_way_result_t<double>, std::partial_ordering>);', "true\ntrue",
   "ジェネリックな比較関数の戻り値の型を決める", ("`<=>` を持たない型に使う", "`<=>` が使えない型では、`::type` がありません。"), [("[`three_way_comparable`](three_way_comparable.md)", "`<=>` で比べられるか")], inc=("compare", "type_traits", "print"))
C3("three_way_comparable", "`<=>` と、`==`・`<` などで比べられる型を要求する。", "`<=>` が使える型で、さらに `==`・`<` などの普通の比較も一貫して使えることを要求するコンセプトです。",
   "template <class T, class Cat = partial_ordering>\nconcept three_way_comparable = /* T 同士で <=> と比較演算子が使える */;", [("T", "型", "調べる型"), ("Cat", "順序型", "省略可。最低限の強さ")], "条件を満たせば `true`", 'std::println("{}", std::three_way_comparable<int>);\nstd::println("{}", std::three_way_comparable<NoCmp>);', "true\nfalse",
   "`<=>` で比べられる型だけ受け付ける", ("`<=>` だけ定義して `==` を忘れる", "`==` も使えることが条件です。"), [("[`three_way_comparable_with`](three_way_comparable_with.md)", "異なる型どうし")], pre="struct NoCmp {};")
C3("three_way_comparable_with", "2 つの型を `<=>` で比べられることを要求する。", "`int` と `long` のように、型が違う値を `<=>` で比べられるかを調べるコンセプトです。",
   "template <class T, class U, class Cat = partial_ordering>\nconcept three_way_comparable_with = /* T と U で <=> が使える */;", [("T, U", "型", "調べる 2 つの型"), ("Cat", "順序型", "省略可。最低限の強さ")], "条件を満たせば `true`", 'std::println("{}", std::three_way_comparable_with<int, long>);\nstd::println("{}", std::three_way_comparable_with<int, std::string>);', "true\nfalse",
   "異なる型を比べるテンプレートの制約", ("暗黙変換できるだけで満たすと思う", "共通の参照型を持ち、両方向の `<=>` が使える必要があります。"), [("[`three_way_comparable`](three_way_comparable.md)", "同じ型どうし")], inc=("compare", "string", "print"))
for nm, what, ex_ in [("strong_order", "強い順序（等しいものは区別できない）で比べる。", "std::strong_order(1, 2)"), ("weak_order", "弱い順序（等しいものを同一視する）で比べる。", "std::weak_order(1.0, 2.0)"), ("partial_order", "半順序（比べられない場合がある）で比べる。", "std::partial_order(1.0, std::nan(\"\"))")]:
    cat = {"strong_order": "strong_ordering", "weak_order": "weak_ordering", "partial_order": "partial_ordering"}[nm]
    body = {"strong_order": 'std::println("{}", std::is_lt(std::strong_order(1, 2)));', "weak_order": 'std::println("{}", std::is_lt(std::weak_order(1.0, 2.0)));', "partial_order": 'std::println("{}", std::partial_order(1.0, std::nan("")) == std::partial_ordering::unordered);'}[nm]
    C3(nm, what, f"`<=>` は型によって結果の強さが違います。`{nm}(a, b)` は、`{cat}` を必ず返す比較で、型が `<=>` を持たなくても、浮動小数点なら全順序のルールに従って比べます。" if nm != "partial_order" else "`partial_order(a, b)` は `partial_ordering` を返す比較です。NaN のように比べられない値の組は `unordered` になります。",
       f"inline constexpr /* カスタマイズポイント */ {nm};", [("a, b", "型", "比べる 2 つの値")], f"`std::{cat}`", body, "true", "浮動小数点も含めて、一貫した順序で整列する", ("浮動小数点で `<` と混ぜる", f"`{nm}` は NaN を含めた順序を決めます。`<` の結果とは違うことがあります。"),
       [(f"[`{cat}`]({cat}.md)", "結果の型")], inc=("compare", "cmath", "print"))
for nm, cat in [("compare_strong_order_fallback", "strong_ordering"), ("compare_weak_order_fallback", "weak_ordering"), ("compare_partial_order_fallback", "partial_ordering")]:
    C3(nm, f"`<=>` が無い型も、`==` と `<` で `{cat}` として比べる。", f"`<=>` を持たない古い型でも、`==` と `<` があれば順序づけたいことがあります。`{nm}` は、`<=>` があればそれを使い、なければ `==` と `<` から `{cat}` を作ります。",
       f"inline constexpr /* カスタマイズポイント */ {nm};", [("a, b", "型", "比べる 2 つの値")], f"`std::{cat}`", f'std::println("{{}}", std::{nm}(V{{1}}, V{{2}}) == std::{cat}::less);', "true",
       "古い型を `<=>` ベースの仕組みに乗せる", ("`==` と `<` が整合しない型", "`==` と `<` の結果が矛盾していると、結果は意味を持ちません。"), [(f"[`{nm.replace('compare_', '').replace('_fallback', '')}`]({nm.replace('compare_', '').replace('_fallback', '')}.md)", "`<=>` ありの版")],
       pre="struct V {\n  int x;\n  bool operator==(const V&) const = default;\n  bool operator<(const V& o) const { return x < o.x; }\n};", ver=("20", "C++20"))
for nm, cond, ex_t, ex_f in [("is_eq", "等しい", "std::strong_ordering::equal", "std::strong_ordering::less"), ("is_neq", "等しくない", "std::strong_ordering::less", "std::strong_ordering::equal"),
                             ("is_lt", "小さい", "std::strong_ordering::less", "std::strong_ordering::equal"), ("is_lteq", "以下", "std::strong_ordering::equal", "std::strong_ordering::greater"),
                             ("is_gt", "大きい", "std::strong_ordering::greater", "std::strong_ordering::equal"), ("is_gteq", "以上", "std::strong_ordering::equal", "std::strong_ordering::less")]:
    C3(nm, f"順序型の結果が「{cond}」かを `bool` で返す。", f"`<=>` の結果（`strong_ordering` など）は、`== 0` や `< 0` と書いて判定します。`{nm}(結果)` なら、その判定を名前つきの関数で書けます。`{cond}` かを `bool` で返します。",
       f"constexpr bool {nm}(std::partial_ordering cmp) noexcept;", [("cmp", "順序型", "`<=>` の結果")], f"{cond}なら `true`", f'std::println("{{}}", std::{nm}({ex_t}));\nstd::println("{{}}", std::{nm}({ex_f}));', "true\nfalse",
       "`<=>` の結果を読みやすく判定する", ("順序型を `int` と比べる", "`cmp < 0` と書けるのは `0` との比較だけです。他の整数とは比べられません。"), [("[`spaceship`](spaceship.md)", "`<=>` 演算子")])

if __name__ == "__main__":
    flush_hubs()
