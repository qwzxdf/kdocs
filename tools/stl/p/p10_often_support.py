import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from patch import P, run  # noqa: E402

TT = "テンプレートの基本（型を引数にする関数やクラス）が分かると読みやすいです。"

P("support/concepts/integral.md",
  intro="""`Half(int)` と書いた関数に `float` を渡すと、小数部が切り捨てられて、気づかないうちに結果が変わります。テンプレートにして `template <class T> T Half(T v)` と書くと、今度は `std::string` を渡してもコンパイルが通りかけて、中で長いエラーを出します。`std::integral<T>` は、T が整数型（`int`、`char`、`bool` など）であることを要求するコンセプトです。`template <std::integral T>` と書けば、整数以外は、呼び出しの時点で分かりやすいエラーになります。""",
  info=TT,
  sections={"しくみ": """`std::integral<T>` は、`std::is_integral_v<T>` が `true` の型だけを通すコンセプトです。コンセプトはテンプレートの引数に直接書けるので、`std::enable_if` を使うより、ずっと読みやすくなります。

`template <std::integral T>` の代わりに、`void F(std::integral auto v)` と書く省略形もあります。型の名前を後で使わないなら、こちらが短く済みます。

符号付きだけを許すなら `std::signed_integral`、符号なしだけなら `std::unsigned_integral` です。浮動小数点を許すなら `std::floating_point`、数値全般なら `integral` と `floating_point` を `||` でつなぎます。"""},
  game="""整数のIDやフラグだけを受け取るテンプレート関数に使います。ビット演算のヘルパー（`SetBit`、`HasBit`）は、整数以外を渡されると意味がないので、`std::integral` で制約します。

数学ヘルパーでは、整数と小数で実装を分ける場面があります。`template <std::integral T> T Half(T v) { return v / 2; }` と `template <std::floating_point T> T Half(T v) { return v * 0.5; }` のように、コンセプトでオーバーロードを分けられます。

ゲームエンジンのシリアライズ関数で、整数型をバイナリに書き出す版と、小数を書き出す版を分けるときにも使います。""",
  mistakes=[("`bool` や `char` も通ってしまう",
            """`bool` と `char` も整数型です。`Half(true)` が通ってしまいます。「数としての整数」だけにしたいなら、`requires (!std::same_as<T, bool>)` を足します。"""),
           ("`enum` を通そうとして失敗する",
            """`enum` と `enum class` は整数型ではないので、`std::integral` を満たしません。列挙型を受けたいなら、`std::is_enum_v` で別のコンセプトを作ります。"""),
           ("C++17 以前で使おうとする",
            """コンセプトは C++20 の機能です。C++17 では、`std::enable_if_t<std::is_integral_v<T>, int> = 0` を使います。""")],
  similar=[("[`std::is_integral`](../type_traits/is_integral.md)", "型特性版。`bool` の値として使え、`if constexpr` に向く"),
           ("`std::floating_point`", "小数型を要求するコンセプト"),
           ("[`std::same_as`](same_as.md)", "特定の型と同じであることを要求する")],
  memo=["整数だけを受け取るテンプレートは `template <std::integral T>`。", "`bool` と `char` も整数型。", "C++20 の機能。C++17 は `enable_if` で書く。"])

P("support/concepts/same_as.md",
  intro="""「引数は `int` でなければならない」というテンプレートを書きたいとき、`template <class T>` だけでは、どんな型でも受け付けてしまいます。`std::same_as<T, U>` は、T と U がまったく同じ型であることを要求するコンセプトです。`template <std::same_as<int> T>` と書けば、`int` 以外はコンパイルの時点で弾かれます。型特性の `is_same_v` と違って、関数テンプレートの引数に直接書けます。""",
  info=TT,
  sections={"しくみ": """`std::same_as<T, U>` は、`is_same_v<T, U>` と `is_same_v<U, T>` の両方が真のとき満たされます。型の同一性の判定なので、`const int` と `int`、`int&` と `int` は別の型として扱われます。

引数の型をそろえる用途では、`template <class T> void F(T a, std::same_as<T> auto b)` のように書けます。`a` と `b` が同じ型でなければならない、という制約になります。

戻り値の型を要求する `requires` 式と組み合わせると、「この式の結果が `int` であること」を表せます。`{ x.Size() } -> std::same_as<int>;` と書くと、`Size()` の戻り値が `int` である型だけを通すコンセプトが作れます。"""},
  game="""型を限定した関数テンプレートに使います。たとえば `template <std::same_as<float> T> void SetVolume(T v)` なら、`double` が渡されたときにコンパイルエラーにでき、意図しない型の変換を防げます。

コンセプトの組み立て部品としても使います。自作の `Drawable` コンセプトで、`{ obj.Draw() } -> std::same_as<void>;` と書けば、「`Draw()` が `void` を返す型」を表現できます。

ECS のコンポーネントを型で探すテンプレートで、「この型は、コンポーネントの一覧のどれかと同じか」を `std::same_as` で判断する場面でも使われます。""",
  mistakes=[("`const` や参照を無視して比べてしまう",
            """`std::same_as<const int&, int>` は偽です。引数が参照で来る場合は、`std::same_as<std::remove_cvref_t<T>, int>` のように、外してから比べます。"""),
           ("コンセプトの引数の順序を取り違える",
            """`template <std::same_as<int> T>` では、`std::same_as<T, int>` の意味になります。第 1 引数が自動的に `T` になる点を覚えておきます。"""),
           ("C++17 以前で使おうとする",
            """コンセプトは C++20 の機能です。C++17 では、`static_assert(std::is_same_v<T, int>)` を使います。""")],
  similar=[("[`std::is_same`](../type_traits/is_same.md)", "型特性版。`bool` の値として使え、`if constexpr` に向く"),
           ("[`std::integral`](integral.md)", "整数型であることを要求する"),
           ("`std::convertible_to`", "変換できることを要求する。型が同じでなくてよい")],
  memo=["特定の型だけを許すなら `template <std::same_as<int> T>`。", "`const` や参照は区別される。", "型特性の `is_same_v` のコンセプト版。"])

P("support/exceptions/out_of_range.md",
  intro="""`vector` の添え字に範囲外の値を渡すと、`v[i]` は何も検査せず、メモリのどこかを読んでしまいます。バグの原因は後から別の場所で壊れた形で現れ、探すのが大変です。`v.at(i)` は添え字を検査して、範囲外なら `std::out_of_range` の例外を投げます。`std::out_of_range` は、範囲外の添え字やキーにアクセスしたときの例外です。""",
  info="""[例外の基本](../exceptions.md)（`try` と `catch`）を先に読んでください。""",
  sections={"しくみ": """`out_of_range` は `std::logic_error` の派生クラスで、「プログラムを正しく書いていれば起きないはずのエラー」を表します。呼び出す側のミスで起きるものなので、実行時に起きうる失敗（ファイルが無いなど）を表す `runtime_error` とは区別されます。

`vector::at()`、`string::at()`、`map::at()`、`bitset::test()` などが投げます。`bitset::operator[]` や `vector::operator[]` は投げません。検査のコストを避けるためです。

メッセージは `what()` で取り出せますが、文言は実装によって違います。"""},
  game="""開発中のデバッグ用に、検査付きの `at()` を使う場面があります。範囲外のアクセスをしたときに、すぐ例外で止まるので、原因の場所が分かります。ただし、毎フレーム回るループでは、検査のコストが積み重なるので、リリースビルドでは `[]` を使うことが多いです。

設定ファイルの値を `map::at` で引くと、キーが無いときに `out_of_range` が出ます。設定ファイルは外部の入力なので、`try` と `catch` で受けて、初期値で補う形が使われます。

自分で例外を投げるときにも使えます。`if (index >= size) throw std::out_of_range("index");` と書くと、標準の例外と同じ形で伝えられます。""",
  mistakes=[("`[]` が例外を投げると思う",
            """`vector::operator[]` は範囲を検査しません。範囲外では未定義動作で、例外は投げられません。検査したいなら `at()` を使います。"""),
           ("例外を `catch` しないで落ちる",
            """`at()` の例外を捕まえていないと、プログラムが異常終了します。外部の入力に由来する添え字は、`try` で守るか、事前に範囲を確かめます。"""),
           ("例外を握りつぶす",
            """`catch (...) {}` で何もせず無視すると、バグが見えなくなります。ログを出すか、再度投げます。""")],
  similar=[("[`std::runtime_error`](runtime_error.md)", "実行時に起きうる失敗。プログラムのミスではないもの"),
           ("[`std::invalid_argument`](invalid_argument.md)", "引数の値が不正なとき"),
           ("[`std::logic_error`](logic_error.md)", "`out_of_range` の親。プログラムのミスを表す")],
  memo=["`at()` は範囲を検査して `out_of_range` を投げる。`[]` は投げない。", "`logic_error` の派生クラス。", "外部の入力に由来する添え字は、`try` で守る。"])

P("support/exceptions/runtime_error.md",
  intro="""ファイルが開けない、データが壊れている、通信に失敗した。プログラムを正しく書いていても起きるエラーを、呼び出し元へ伝えるには、例外が便利です。`std::runtime_error` は、実行時に起こりうるエラーを表す例外で、メッセージの文字列を渡して投げます。自作の例外クラスの基底としてもよく使われます。""",
  info="""[例外の基本](../exceptions.md)（`try`、`catch`、`throw`）を先に読んでください。""",
  sections={"しくみ": """`runtime_error` は `std::exception` の派生クラスで、コンストラクターに文字列を渡します。`catch (const std::exception& e)` で受けると、`e.what()` でそのメッセージが取れます。

`logic_error`（プログラムのミス）と対になる分類です。`runtime_error` は、環境や入力が原因で、プログラムの正しさとは関係なく起きるエラーに使います。派生に `range_error`、`overflow_error`、`underflow_error`、`system_error` があります。

自作の例外は、`runtime_error` を継承して作ると、`std::exception` で受けるコードがそのまま動きます。`struct LoadError : std::runtime_error { using std::runtime_error::runtime_error; };` と 1 行で書けます。"""},
  game="""ファイルの読み込みやセーブデータの解析で、失敗を投げる用途が代表的です。`throw std::runtime_error("セーブデータが壊れている: " + path);` と書き、ゲームの上位の層で `catch` して、エラー画面を出します。

ゲームでは、例外を使わない設定でビルドすることも多いです。そのときは、`std::expected` や戻り値でエラーを返す設計にします。

ツールやエディターの側では、例外のほうが書きやすく、広く使われます。ファイルが無い、形式が違うといったエラーは、`runtime_error` を継承した自作の例外で区別します。""",
  mistakes=[("値渡しで `catch` して、派生クラスの情報が切れる",
            """`catch (std::exception e)` と値で受けると、派生クラスの部分が切り取られます。`catch (const std::exception& e)` と、参照で受けます。"""),
           ("メッセージに `std::string` を渡して、`what()` のポインターが無効になる",
            """`what()` が返す `const char*` は、例外オブジェクトが生きている間だけ有効です。`catch` の外へ持ち出さず、中で使い切ります。"""),
           ("プログラムのミスを `runtime_error` で表す",
            """引数が範囲外といったミスは、`logic_error` や `out_of_range` を使います。分類を分けておくと、`catch` で扱い方を変えられます。""")],
  similar=[("[`std::logic_error`](logic_error.md)", "プログラムのミスを表す"),
           ("[`std::system_error`](system_error.md)", "OS のエラーコードを持つ"),
           ("[`std::out_of_range`](out_of_range.md)", "範囲外のアクセス。`logic_error` の派生")],
  memo=["実行時に起こりうるエラーは `runtime_error` で投げる。", "`catch` は `const std::exception&` で受ける。", "自作の例外は `runtime_error` を継承すると扱いやすい。"])

P("support/iterator/back_inserter.md",
  intro="""`std::copy` で別の `vector` に写すとき、コピー先の大きさが足りないと、範囲外に書き込んでしまいます。先に `resize` するのも手間です。`std::back_inserter(c)` は、代入するたびにコンテナの末尾へ `push_back` するイテレーターを作ります。これを出力先に渡せば、結果が自動で末尾へ足され、コンテナが必要なだけ大きくなります。""",
  info="""[イテレーター](../../../basics/iterator.md)の基本と、`copy` や `transform` の使い方を先に読んでください。""",
  sections={"しくみ": """`back_inserter` が返すのは `back_insert_iterator` というイテレーターで、`*it = value` と代入すると、中でコンテナの `push_back(value)` を呼びます。進める（`++it`）操作は何もしません。

出力先を「書き込み先の位置」ではなく「追加するコンテナ」で指定する、という考え方です。出力先の大きさを気にしなくてよくなる反面、`push_back` の回数だけ、要素が必要に応じて再確保されることがあります。

`push_back` がないコンテナ（`set` や `map`）には使えません。先頭に追加するなら `front_inserter`、任意の位置に追加するなら `inserter` があります。"""},
  game="""別のコンテナに結果を集める処理に使います。`std::ranges::copy_if(enemies, std::back_inserter(alive), IsAlive)` なら、生きている敵だけが `alive` に集まります。

事前に `alive.reserve(enemies.size())` で容量を確保しておくと、再確保が起きず速くなります。件数が分からないときは、最大の件数で `reserve` するか、`std::ranges::to` で `vector` に変換する方法もあります。

`transform` の出力先にも向いています。変換の結果を別の `vector` に溜めたいときに、`std::back_inserter(out)` を渡します。""",
  mistakes=[("`reserve` せずに大量に追加して、再確保が何度も起きる",
            """`push_back` が繰り返されるたびに、容量が足りなくなると再確保されます。件数の目安が分かるなら、事前に `reserve` しておきます。"""),
           ("コピー元とコピー先が同じコンテナ",
            """`copy(v, back_inserter(v))` は、`push_back` で `v` が再確保され、読み取り中のイテレーターが壊れます。別のコンテナに写します。"""),
           ("`set` や `map` に使ってコンパイルエラーになる",
            """`push_back` が無いコンテナには使えません。`std::inserter(s, s.end())` を使います。""")],
  similar=[("`std::front_inserter`", "先頭に追加する。`push_front` があるコンテナ向け"),
           ("`std::inserter`", "任意の位置に追加する。`set` や `map` でも使える"),
           ("[`std::ranges::to`](../../algorithms/ranges_to.md)", "ビューの結果を新しいコンテナに作り直す。C++23")],
  memo=["出力先に渡すと、代入のたびに `push_back` される。", "事前に `reserve` すると速い。", "`set` や `map` には `inserter` を使う。"])

P("support/iterator/size.md",
  intro="""配列の要素数を調べるとき、昔は `sizeof(a) / sizeof(a[0])` と書いていました。見慣れた書き方ですが、ポインターに変換された配列に使うと、間違った値が静かに返ってきます。`std::size(c)` は、コンテナや配列の要素数を返す関数です。`c.size()` と同じ意味ですが、生の配列 `int a[5]` にも使えます。ポインターに変換された配列に使うと、コンパイルエラーで教えてくれます。""",
  info="""配列とポインターの違いが分かると読みやすいです。配列は、関数の引数に渡すとポインターに変換されて、大きさの情報が消えます。""",
  sections={"しくみ": """`std::size(c)` は、`c.size()` を呼びます。生の配列には、専用のオーバーロードが用意されていて、テンプレートの引数から大きさを取り出して返します。

ポインターに変換された配列は、大きさの情報がないので、`std::size` を呼ぶとコンパイルエラーになります。`sizeof(p) / sizeof(p[0])` のように書いて、ポインターのサイズを要素数と取り違える事故がなくなります。

戻り値は符号なしの `size_t` です。符号付きの値が欲しいときは、`std::ssize(c)` を使います。ループの条件 `i < std::size(a)` で、`int` の `i` と比べると、符号の警告が出る場合に便利です。"""},
  game="""固定長の配列の要素数を取るときに使います。`constexpr int kSlots[] = {...};` のような定数の配列を、`for (size_t i = 0; i < std::size(kSlots); ++i)` で回せます。要素を増やしても、数を書き直す必要がありません。

`array` と `vector` のどちらでも同じ書き方になるので、テンプレート関数の中で、どちらのコンテナも受け付けるときに便利です。

C の API とやり取りするときは、配列がポインターになっていないか注意します。関数の引数で受けた配列には、`std::size` が使えません。`std::span` で受ければ、大きさも一緒に持ち運べます。""",
  mistakes=[("関数の引数で受けた配列に使う",
            """`void F(int a[10])` は、引数 `a` が `int*` になっているので、`std::size(a)` はコンパイルエラーになります。`std::span<int>` や `std::array` で受けます。"""),
           ("符号なしの戻り値を、`int` と比べて警告になる",
            """`int i = ...; i < std::size(a)` は、符号の違う比較の警告になります。`std::ssize(a)` を使うか、`i` を `size_t` にします。"""),
           ("`sizeof` との取り違え",
            """`sizeof(a)` はバイト数で、要素数ではありません。`std::size(a)` が要素数です。""")],
  similar=[("[`std::ssize`](ssize.md)", "符号付きの要素数を返す"),
           ("`c.size()`", "コンテナのメンバー関数。生の配列には使えない"),
           ("[`std::span`](../../containers/span.md)", "大きさも一緒に持ち運べる")],
  memo=["`std::size(c)` で、コンテナにも生の配列にも使える。", "ポインターに変換された配列はコンパイルエラー。", "符号付きが欲しいときは `ssize`。"])

P("support/type_traits/is_integral.md",
  intro="""テンプレートの関数で、整数のときは割り算を、小数のときは掛け算を使うなど、型によって処理を切り替えたいことがあります。型を人の目で判断するのではなく、コンパイラーに聞くのが `std::is_integral_v<T>` です。型 `T` が整数型（`int`、`char`、`bool` など）なら `true` です。`if constexpr` と組み合わせて、型ごとの処理を書き分けます。""",
  info=TT,
  sections={"しくみ": """`is_integral_v<T>` は、`T` が `bool`、`char` の各種、`short`、`int`、`long`、`long long` と、その符号なしの版のどれかなら `true` です。`const` や `volatile` が付いていても `true` ですが、参照やポインターは `false` です。

`enum` は整数型ではありません。`enum` を整数として扱いたいなら、`std::is_enum_v` で別に調べ、`std::to_underlying` で変換します。`float` や `double` は、`is_floating_point_v` で調べます。

C++20 のコンセプト `std::integral` は、同じ判定を `template <std::integral T>` の形で書けます。条件を `if constexpr` で使うときは型特性、関数の制約に使うときはコンセプトを選びます。"""},
  game="""数値を扱うテンプレート関数の中で、整数と小数の処理を切り替えるために使います。

```cpp
template <class T>
T Half(T v) {
  if constexpr (std::is_integral_v<T>) {
    return v / 2;  // 整数は割り算
  } else {
    return v * 0.5;  // 小数は掛け算
  }
}
```

シリアライズでは、整数型はそのままバイナリに書き込み、小数は別の書式にする、といった分岐で使います。

数学ライブラリの関数に、不正な型が渡されたときの `static_assert` にも使えます。`static_assert(std::is_integral_v<T> || std::is_floating_point_v<T>, "数値型のみ");` と書くと、文字列などを渡したときに分かりやすいメッセージが出ます。""",
  mistakes=[("`bool` や `char` も整数型であることを忘れる",
            """`is_integral_v<bool>` は `true` です。`Half(true)` が通ってしまいます。数としての整数だけを許すなら、`bool` を別に除きます。"""),
           ("`enum` を整数型だと思う",
            """`enum` は `is_integral_v` が `false` です。`std::is_enum_v` で別に調べます。"""),
           ("参照型で `false` になって困惑する",
            """`is_integral_v<int&>` は `false` です。テンプレートが参照で型を受けているときは、`std::remove_cvref_t<T>` を通してから調べます。""")],
  similar=[("[`std::is_floating_point`](is_floating_point.md)", "小数型かを調べる"),
           ("`std::is_arithmetic`", "整数または小数のどちらかか"),
           ("[`std::integral`](../concepts/integral.md)", "コンセプト版。関数の制約に使う")],
  memo=["`is_integral_v<T>` で整数型かを調べる。", "`bool` と `char` も整数型。`enum` は違う。", "参照型には `remove_cvref_t` を通してから使う。"])

P("support/type_traits/is_floating_point.md",
  intro="""テンプレートの数値計算で、整数と小数の処理を分けたいとき、型をコンパイラーに聞くのが `std::is_floating_point_v<T>` です。型 `T` が小数型（`float`、`double`、`long double`）なら `true` を返します。`if constexpr` と組み合わせて、小数のときだけ誤差を考えた比較にする、などの分岐に使います。""",
  info=TT,
  sections={"しくみ": """`is_floating_point_v<T>` は、`T` が `float`、`double`、`long double` のどれか（`const` や `volatile` は無視）なら `true` です。C++23 の `std::float16_t`、`std::float32_t` なども、含まれます。

整数型は `false`、参照とポインターも `false` です。テンプレートが参照で型を受けているなら、`remove_cvref_t` を通してから調べます。

C++20 のコンセプト `std::floating_point` は、同じ判定を `template <std::floating_point T>` と書ける形にしたものです。"""},
  game="""数値の比較関数で、整数と小数を分けるのが代表例です。小数なら `std::abs(a - b) < epsilon`、整数なら `a == b` と書き分けます。

```cpp
template <class T>
bool NearlyEqual(T a, T b) {
  if constexpr (std::is_floating_point_v<T>) {
    return std::abs(a - b) < static_cast<T>(1e-5);
  } else {
    return a == b;
  }
}
```

ベクトルや行列のテンプレートで、要素の型が小数であることを制約するときにも使います。`static_assert(std::is_floating_point_v<T>)` と書いておけば、整数の行列を作ったときに、早めに気づけます。""",
  mistakes=[("整数を小数として扱うつもりで `true` を期待する",
            """`is_floating_point_v<int>` は `false` です。整数と小数をまとめて「数値」とするなら `std::is_arithmetic_v` を使います。"""),
           ("参照型で `false` になる",
            """`is_floating_point_v<float&>` は `false` です。`std::remove_cvref_t<T>` を通してから調べます。"""),
           ("`half` などの拡張型を期待する",
            """GPU 向けの `half` のような独自の型は、`is_floating_point_v` が `false` です。標準の拡張型（`std::float16_t`）は、C++23 で含まれます。""")],
  similar=[("[`std::is_integral`](is_integral.md)", "整数型かを調べる"),
           ("`std::is_arithmetic`", "整数または小数のどちらかか"),
           ("`std::floating_point`", "コンセプト版。関数の制約に使う")],
  memo=["`is_floating_point_v<T>` で小数型かを調べる。", "参照型には `remove_cvref_t` を通してから使う。", "C++20 では `std::floating_point` コンセプトでも書ける。"])

P("support/type_traits/is_same.md",
  intro="""テンプレートの中で、型が `float` のときだけ別の処理をしたい、2 つの型が同じかどうかを確かめたい。型を人の目で判断するのではなく、コンパイラーに聞くのが `std::is_same_v<A, B>` です。2 つの型が、まったく同じ型なら `true` になります。`const` や参照の有無も区別されます。`if constexpr` と組み合わせて、型ごとの処理を書き分けます。""",
  info=TT,
  sections={"しくみ": """`is_same_v<A, B>` は、A と B が同一の型のときだけ `true` です。`int` と `const int` は別の型、`int` と `int&` も別の型、`int` と `long` も別の型です。`using` で別名を付けただけの型は、元の型と同じものとして扱われます。

型を比べる前に、`const` や参照を取り除きたいなら、`std::remove_cvref_t<T>` を通します。引数が `const int&` で来ても `int&&` で来ても、`remove_cvref_t` で `int` に直してから比べられます。

C++20 のコンセプト `std::same_as` は、同じ判定を `template <std::same_as<int> T>` の形で書けます。"""},
  game="""型によって処理を切り替える場面で使います。

```cpp
template <class T>
void Save(const T& v) {
  if constexpr (std::is_same_v<T, std::string>) {
    // 文字列は長さを先に書く
  } else {
    // それ以外は、バイトをそのまま書く
  }
}
```

エンジンのコンポーネント管理（ECS）で、「このコンポーネントの型は、登録済みの型か」を調べる場面にも使います。可変長テンプレートで、型のリストの中に特定の型があるかを調べる再帰の部品として、`is_same_v` を使います。

`static_assert(std::is_same_v<decltype(x), float>)` のように、`decltype` と組み合わせて、型の推論結果が思った通りかを確かめられます。""",
  mistakes=[("`const` や参照を無視して比べて `false` になる",
            """テンプレートの引数 `T` が `const std::string&` で来ているのに、`is_same_v<T, std::string>` と比べると `false` です。`std::remove_cvref_t<T>` を通してから比べます。"""),
           ("`int` と `long` が同じだと思う",
            """サイズが同じでも、別の型です。Windows の `long` と `int` はどちらも 32 ビットですが、`is_same_v<int, long>` は `false` です。"""),
           ("`if` の条件に使って、通らない枝がコンパイルエラーになる",
            """型によって存在しないメンバーを使う枝は、普通の `if` ではコンパイルされてしまい、エラーになります。`if constexpr` を使うと、通らない枝は捨てられます。""")],
  similar=[("[`std::same_as`](../concepts/same_as.md)", "コンセプト版。関数の制約に使う"),
           ("[`std::remove_cvref`](remove_cvref.md)", "`const` と参照を外す。比べる前に通す"),
           ("`std::is_convertible`", "変換できるかを調べる。同じ型でなくてよい")],
  memo=["2 つの型が同じかを、コンパイル時に調べる。", "`const` と参照は区別される。比べる前に `remove_cvref_t` を通す。", "型ごとの処理は `if constexpr` で書き分ける。"])

P("support/type_traits/remove_cvref.md",
  intro="""テンプレートの関数は、`const int&` や `int&&`、`int` など、様々な形で引数を受け取ります。型を比べたいとき、これらがすべて別の型として扱われると、一つ一つ書き分けるのが大変です。`std::remove_cvref_t<T>` は、型 `T` から `const`、`volatile`、参照を全部外した型を返します。受け取った型の「素の型」に直して比べるために使います。""",
  info=TT,
  sections={"しくみ": """`remove_cvref_t<T>` は、`remove_cv_t<remove_reference_t<T>>` と同じです。参照を先に外し、その結果から `const` と `volatile` を外します。

ポインターの指す先の `const` は外れません。`const int*` は、`int` を指す `const` なポインターではなく、`const int` を指すポインターという型で、`remove_cvref_t<const int*>` は `const int*` のままです。

配列や関数の型は変わりません。それらを値渡し用の型に変えたいときは、`std::decay_t` を使います。C++20 より前の環境では、`decay_t` で代用していました。"""},
  game="""転送参照（`T&&`）の引数を受けるテンプレートで、本当の型を調べるときに使います。

```cpp
template <class T>
void Add(T&& component) {
  using Raw = std::remove_cvref_t<T>;
  // Raw は、const も参照も付かない素の型
  static_assert(std::is_same_v<Raw, Position>, "Position のみ");
}
```

ECS で、コンポーネントの型をキーにして保存する場面では、`const` や参照の違いで別の型として登録されないよう、`remove_cvref_t` を通します。`std::type_index(typeid(Raw))` の形が定番です。

コンセプトの定義でも使います。`std::same_as<std::remove_cvref_t<T>, int>` と書けば、引数の渡され方にかかわらず、「`int` かどうか」を調べられます。""",
  mistakes=[("ポインターの指す先の `const` も外れると思う",
            """`remove_cvref_t<const int*>` は `const int*` のままです。外れるのは、型そのものについた `const` や参照だけです。指す先の `const` を外したいなら、`remove_pointer_t` と `remove_cv_t` を順に適用します。"""),
           ("配列や関数の型を渡して、期待と違う結果になる",
            """`remove_cvref_t<int[3]>` は `int[3]` のままで、`int*` にはなりません。配列を値渡し用の型にしたいときは `decay_t` です。"""),
           ("C++17 以前で使おうとする",
            """`remove_cvref_t` は C++20 の機能です。C++17 以前では `std::decay_t` で代用するか、`remove_cv_t<remove_reference_t<T>>` と書きます。""")],
  similar=[("`std::decay`", "配列や関数も値渡し用の型に変える。`remove_cvref` より広く変換する"),
           ("`std::remove_const`", "`const` だけを外す"),
           ("`std::remove_reference`", "参照だけを外す")],
  memo=["`const`、`volatile`、参照をすべて外した「素の型」にする。", "転送参照の型を調べるときに使う。", "ポインターの指す先の `const` は外れない。"])

run()
