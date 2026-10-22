"""バッチ 10: <type_traits> の未登録分。"""
from mk import *  # noqa: F401,F403

TT = "support/type_traits/"
TTH = "support/type_traits.md"
V = {"11": ("11", "C++11"), "14": ("14", "C++14"), "17": ("17", "C++17"), "20": ("20", "C++20"), "23": ("23", "C++23"), "26": ("26", "C++26")}


def T(name, summary, intro, t_expr, f_expr, pre="", ver="11", args=None, miss=None, sim=None, rank="rare", params=("T",), tips=None, true_out="true", false_out="false", extra_inc=()):
    """is_xxx の型特性（2 つの式を println で出す）。"""
    sig = f"template <class {', class '.join(params)}>\nstruct {name};\ntemplate <class {', class '.join(params)}>\ninline constexpr bool {name}_v = {name}<{', '.join(params)}>::value;"
    body = f'std::println("{{}}", {t_expr});\nstd::println("{{}}", {f_expr});'
    Q(TT + name + ".md", "std::" + name, summary, rank, ["type_traits", "print", *extra_inc], intro,
      tips or ["`::value`（または `_v` 版）が `bool` の定数。", "コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。", "型だけを見る（値は見ない）。"],
      sig, args or [(p, "型", "調べる型") for p in params], "条件を満たせば `true`（コンパイル時の定数）", body, f"{true_out}\n{false_out}",
      use="テンプレートの中で、型の性質に応じて処理を切り替える", miss=miss or ("値と型を取り違える", f"`{name}` は型を調べます。変数を渡すときは `decltype(x)` にします。"),
      sim=sim or [("[`is_same`](is_same.md)", "同じ型か")], cx="コンパイル時のみ", ver=V[ver] if ver != "11" else V["11"], hub=TTH, hubname="<type_traits>", rj=f"type_traits/{name}.html", cr=f"types/{name}", pre=pre)


S = "struct S {};"
T("is_void", "型が `void` かを調べる。", "戻り値が `void` の関数だけ特別扱いしたいときなど、`void` かどうかを型から判定します。`void` は値を持たない型なので、変数や引数にはできません。", "std::is_void_v<void>", "std::is_void_v<int>")
T("is_null_pointer", "型が `std::nullptr_t` かを調べる。", "`nullptr` の型は `std::nullptr_t` という専用の型です。テンプレートに `nullptr` が渡されたかを、型から判定できます。", "std::is_null_pointer_v<decltype(nullptr)>", "std::is_null_pointer_v<int*>", ver="14", extra_inc=("cstddef",))
T("is_array", "型が配列かを調べる。", "`int[3]` のような配列の型かを判定します。`std::array` は配列ではなくクラスなので `false` です。", "std::is_array_v<int[3]>", "std::is_array_v<int>", miss=("`std::array` に使う", "`std::array<int, 3>` は配列型ではなくクラスです。`false` になります。"))
T("is_union", "型が共用体（union）かを調べる。", "`union` は同じ場所に複数の型の値を入れる型です。クラスとは別扱いなので、`is_class` とは区別されます。", "std::is_union_v<U>", "std::is_union_v<S>", pre="union U { int a; float b; };\nstruct S {};")
T("is_class", "型がクラス（struct を含む）かを調べる。", "`class` と `struct` は、どちらもクラスです。`union` や `enum` は含みません。", "std::is_class_v<S>", "std::is_class_v<U>", pre="struct S {};\nunion U { int a; float b; };", miss=("`union` を含むと思う", "`union` は `is_class` で `false` です。`is_union` を使います。"))
T("is_function", "型が関数の型かを調べる。", "`void(int)` のような関数そのものの型かを判定します。関数ポインタ（`void(*)(int)`）は関数の型ではありません。", "std::is_function_v<void(int)>", "std::is_function_v<void (*)(int)>", miss=("関数ポインタに使う", "関数ポインタは `is_pointer` です。`is_function` は関数そのものの型だけです。"))
T("is_lvalue_reference", "型が左辺値参照かを調べる。", "`int&` のような参照の型かを判定します。右辺値参照（`int&&`）は含みません。", "std::is_lvalue_reference_v<int&>", "std::is_lvalue_reference_v<int&&>")
T("is_rvalue_reference", "型が右辺値参照かを調べる。", "`int&&` のような右辺値参照の型かを判定します。", "std::is_rvalue_reference_v<int&&>", "std::is_rvalue_reference_v<int&>")
T("is_member_object_pointer", "型がメンバ変数へのポインタかを調べる。", "`int S::*` のように、クラスのメンバ変数を指すポインタの型かを判定します。", "std::is_member_object_pointer_v<int S::*>", "std::is_member_object_pointer_v<void (S::*)()>", pre="struct S {\n  int m;\n  void f();\n};")
T("is_member_function_pointer", "型がメンバ関数へのポインタかを調べる。", "`void (S::*)()` のように、クラスのメンバ関数を指すポインタの型かを判定します。", "std::is_member_function_pointer_v<void (S::*)()>", "std::is_member_function_pointer_v<int S::*>", pre="struct S {\n  int m;\n  void f();\n};")
T("is_fundamental", "型が基本型（算術型・`void`・`nullptr_t`）かを調べる。", "`int`・`float`・`char`・`bool`・`void`・`nullptr_t` など、言語が最初から持つ型かを判定します。", "std::is_fundamental_v<int>", "std::is_fundamental_v<S>", pre=S, extra_inc=())
T("is_scalar", "型がスカラー型（算術型・列挙・ポインタなど）かを調べる。", "値を 1 つだけ持つ型です。算術型・列挙型・ポインタ・メンバへのポインタ・`nullptr_t` を含み、クラスや配列は含みません。", "std::is_scalar_v<int*>", "std::is_scalar_v<S>", pre=S)
T("is_object", "型がオブジェクト型（関数・参照・`void` 以外）かを調べる。", "メモリ上に実体を持つ型です。参照や関数や `void` は実体を持たないので `false` です。", "std::is_object_v<int>", "std::is_object_v<int&>")
T("is_compound", "型が複合型（基本型以外）かを調べる。", "配列・関数・ポインタ・参照・クラス・共用体・列挙型など、基本型以外の型です。`is_fundamental` の逆です。", "std::is_compound_v<S>", "std::is_compound_v<int>", pre=S)
T("is_reference", "型が参照（左辺値でも右辺値でも）かを調べる。", "`int&` と `int&&` のどちらかなら `true` です。", "std::is_reference_v<int&>", "std::is_reference_v<int>")
T("is_member_pointer", "型がメンバへのポインタかを調べる。", "メンバ変数へのポインタと、メンバ関数へのポインタの、どちらかなら `true` です。", "std::is_member_pointer_v<int S::*>", "std::is_member_pointer_v<int*>", pre="struct S {\n  int m;\n};")
T("is_volatile", "型が `volatile` 修飾されているかを調べる。", "`volatile int` のように、最適化されない（毎回読み書きされる）と指定された型かを判定します。", "std::is_volatile_v<volatile int>", "std::is_volatile_v<int>")
T("is_trivial", "型がトリビアル（自明な構築・コピー・破棄ができる）かを調べる。", "ユーザー定義のコンストラクタやデストラクタを持たず、`memcpy` で安全にコピーできる、単純な型かを判定します。", "std::is_trivial_v<int>", "std::is_trivial_v<std::string>", extra_inc=("string",))
T("is_standard_layout", "型が標準レイアウト（C 言語と互換のメモリ配置）かを調べる。", "メンバの並びが予測でき、C の構造体と同じように扱える型です。仮想関数を持つ型は満たしません。", "std::is_standard_layout_v<A>", "std::is_standard_layout_v<B>", pre="struct A {\n  int x;\n  int y;\n};\nstruct B {\n  virtual void f();\n};")
T("is_pod", "型が POD（トリビアルかつ標準レイアウト）かを調べる。", "C の構造体と同じように扱える、単純な型です。C++20 で非推奨になったので、`is_trivial` と `is_standard_layout` を組み合わせて使います。", "std::is_pod_v<A>", "std::is_pod_v<std::string>", pre="struct A {\n  int x;\n  int y;\n};", miss=("新しいコードで使う", "C++20 以降は非推奨です。コンパイル時に警告が出ることがあります。"), sim=[("[`is_trivial`](is_trivial.md)", "トリビアルか"), ("[`is_standard_layout`](is_standard_layout.md)", "標準レイアウトか")], extra_inc=("string",))
T("is_polymorphic", "型が仮想関数を持つ（多態的な）かを調べる。", "`virtual` 関数を 1 つでも持つクラスかを判定します。`dynamic_cast` が使える型かの目安になります。", "std::is_polymorphic_v<B>", "std::is_polymorphic_v<A>", pre="struct A {\n  int x;\n};\nstruct B {\n  virtual void f();\n};")
T("is_abstract", "型が抽象クラス（純粋仮想関数を持つ）かを調べる。", "`= 0` の純粋仮想関数を持つクラスは、インスタンスを作れません。それを判定します。", "std::is_abstract_v<Abs>", "std::is_abstract_v<A>", pre="struct A {\n  int x;\n};\nstruct Abs {\n  virtual void f() = 0;\n};")
T("is_final", "型が `final`（継承できない）かを調べる。", "`final` が付いていて、継承できないクラスかを判定します。", "std::is_final_v<F>", "std::is_final_v<A>", ver="14", pre="struct A {};\nstruct F final {};")
T("is_implicit_lifetime", "型が「暗黙的に寿命を始められる」型かを調べる。", "`malloc` や `memcpy` で用意したメモリを、そのまま `T` のオブジェクトとして使い始められる型かを判定します。`int` や単純な構造体は満たし、コンストラクタやデストラクタが必要な型は満たしません。", "std::is_implicit_lifetime_v<int>", "std::is_implicit_lifetime_v<std::string>", ver="23", extra_inc=("string",))
T("is_unsigned", "型が符号なしの算術型かを調べる。", "`unsigned` や `size_t` などの符号なし整数型かを判定します。`bool` も含みます。", "std::is_unsigned_v<unsigned>", "std::is_unsigned_v<int>")
T("is_bounded_array", "型が要素数の決まった配列かを調べる。", "`int[3]` のように、要素数がわかっている配列かを判定します。", "std::is_bounded_array_v<int[3]>", "std::is_bounded_array_v<int[]>", ver="20")
T("is_unbounded_array", "型が要素数の決まっていない配列かを調べる。", "`int[]` のように、要素数が不明な配列の型かを判定します。`new int[n]` の型などに登場します。", "std::is_unbounded_array_v<int[]>", "std::is_unbounded_array_v<int[3]>", ver="20")
T("is_scoped_enum", "型がスコープ付き列挙型（`enum class`）かを調べる。", "`enum class` で宣言した型かを判定します。暗黙に整数へ変換されない列挙型です。", "std::is_scoped_enum_v<E>", "std::is_scoped_enum_v<Old>", ver="23", pre="enum class E {};\nenum Old {};")
T("is_constructible", "指定した引数で構築できる型かを調べる。", "`T(args...)` と書ける型の組かを判定します。`emplace` 系の関数のように、引数で作れる型にだけ処理を絞りたいときに使います。", "std::is_constructible_v<std::string, const char*>", "std::is_constructible_v<std::string, int>", params=("T", "Args..."), extra_inc=("string",), sim=[("[`is_default_constructible`](is_default_constructible.md)", "引数なしで作れる")])
T("is_trivially_constructible", "指定した引数で、自明に（特別な処理なしで）構築できる型かを調べる。", "ユーザー定義のコンストラクタを経由せず、メモリのコピーだけで作れるかを判定します。", "std::is_trivially_constructible_v<int, int>", "std::is_trivially_constructible_v<std::string, const char*>", params=("T", "Args..."), extra_inc=("string",))
T("is_nothrow_constructible", "指定した引数で、例外を投げずに構築できる型かを調べる。", "`noexcept` で構築できるかを判定します。例外安全な実装（`vector` の再確保でムーブを選ぶなど）の分岐に使われます。", "std::is_nothrow_constructible_v<int, int>", "std::is_nothrow_constructible_v<std::string, const char*>", params=("T", "Args..."), extra_inc=("string",))
T("is_move_constructible", "ムーブして構築できる型かを調べる。", "他のオブジェクトからムーブして作れるかを判定します。ムーブコンストラクタを `delete` した型は `false` です。", "std::is_move_constructible_v<std::string>", "std::is_move_constructible_v<NoMove>", pre="struct NoMove {\n  NoMove() = default;\n  NoMove(NoMove&&) = delete;\n};", extra_inc=("string",), sim=[("[`is_copy_constructible`](is_copy_constructible.md)", "コピーして作れる")])
T("is_assignable", "代入できる型の組かを調べる。", "`T = U` が書けるかを判定します。左辺は参照の型で渡します（`int&`）。", "std::is_assignable_v<int&, int>", "std::is_assignable_v<int, int>", params=("T", "U"), miss=("左辺に値の型を渡す", "`is_assignable<int, int>` は `false` です。左辺は `int&` のように参照で渡します。"))
T("is_copy_assignable", "コピー代入できる型かを調べる。", "同じ型の左辺値を代入できるかを判定します。`unique_ptr` のようなコピー不可の型は `false` です。", "std::is_copy_assignable_v<std::string>", "std::is_copy_assignable_v<std::unique_ptr<int>>", extra_inc=("string", "memory"))
T("is_move_assignable", "ムーブ代入できる型かを調べる。", "同じ型の右辺値を代入できるかを判定します。`const` の型は代入できません。", "std::is_move_assignable_v<std::string>", "std::is_move_assignable_v<const int>", extra_inc=("string",))
T("is_destructible", "破棄できる型かを調べる。", "デストラクタが呼べる型かを判定します。デストラクタが `private` や `delete` の型は `false` です。", "std::is_destructible_v<int>", "std::is_destructible_v<PD>", pre="struct PD {\n private:\n  ~PD();\n};")
T("is_trivially_destructible", "破棄が自明（何もしなくてよい）な型かを調べる。", "デストラクタで何もする必要がない型かを判定します。この型の配列は、解放の際にデストラクタを呼ぶ手間が省けます。", "std::is_trivially_destructible_v<int>", "std::is_trivially_destructible_v<std::string>", extra_inc=("string",))
T("is_nothrow_destructible", "デストラクタが例外を投げない型かを調べる。", "`noexcept` で破棄できるかを判定します。デストラクタは基本的に `noexcept` なので、多くの型が `true` です。", "std::is_nothrow_destructible_v<int>", "std::is_nothrow_destructible_v<TD>", pre="struct TD {\n  ~TD() noexcept(false) {}\n};")
T("is_swappable", "`swap` で入れ替えられる型かを調べる。", "`std::swap` が使える型かを判定します。`const` の型は入れ替えられません。", "std::is_swappable_v<int>", "std::is_swappable_v<const int>", ver="17", extra_inc=("utility",))
T("is_swappable_with", "2 つの型の値を、たがいに `swap` できるかを調べる。", "異なる型の値を入れ替えられるかを判定します。参照の型を渡します。", "std::is_swappable_with_v<int&, int&>", "std::is_swappable_with_v<int&, long&>", ver="17", params=("T", "U"), extra_inc=("utility",))
T("is_nothrow_swappable", "`swap` が例外を投げない型かを調べる。", "`noexcept` で入れ替えられるかを判定します。`vector` が再確保でムーブを使えるかの判断などに使われます。", "std::is_nothrow_swappable_v<int>", "std::is_nothrow_swappable_v<const int>", ver="17", extra_inc=("utility",))
T("has_virtual_destructor", "型が仮想デストラクタを持つかを調べる。", "基底クラスのポインタ経由で `delete` するとき、デストラクタが `virtual` でないと、派生クラスの後始末が走りません。それを判定します。", "std::has_virtual_destructor_v<VB>", "std::has_virtual_destructor_v<A>", pre="struct A {\n  int x;\n};\nstruct VB {\n  virtual ~VB() = default;\n};")
T("has_unique_object_representations", "同じ値なら必ず同じビット列になる型かを調べる。", "型の値のバイト列を、そのままハッシュしたり比べたりしてよいかを判定します。パディングや浮動小数点（`-0.0` と `0.0` など）がある型は満たしません。", "std::has_unique_object_representations_v<int>", "std::has_unique_object_representations_v<float>", ver="17")
T("is_layout_compatible", "2 つの型のメモリ配置が互換かを調べる。", "メンバの型と並びが同じで、一方を他方として読み替えても安全かを判定します。", "std::is_layout_compatible_v<L1, L2>", "std::is_layout_compatible_v<L1, A>", ver="20", params=("T", "U"), pre="struct L1 {\n  int a;\n};\nstruct L2 {\n  int b;\n};\nstruct A {\n  int x;\n  int y;\n};")
T("is_pointer_interconvertible_base_of", "基底クラスのポインタと派生クラスのポインタを、相互に変換できるかを調べる。", "派生クラスのオブジェクトの先頭が基底クラスと一致し、ポインタを `reinterpret_cast` で行き来しても安全かを判定します。", "std::is_pointer_interconvertible_base_of_v<Base, Derived>", "std::is_pointer_interconvertible_base_of_v<Derived, Base>", ver="20", params=("Base", "Derived"), pre="struct Base {};\nstruct Derived : Base {};")
T("is_convertible", "型 `From` から `To` へ暗黙に変換できるかを調べる。", "`To x = from;` と書けるかを判定します。`explicit` のコンストラクタ経由の変換は含みません。", "std::is_convertible_v<int, double>", "std::is_convertible_v<int*, int>", params=("From", "To"))
T("is_nothrow_convertible", "暗黙の変換が例外を投げないかを調べる。", "`is_convertible` に、`noexcept` であることを加えた条件です。", "std::is_nothrow_convertible_v<int, double>", "std::is_nothrow_convertible_v<const char*, std::string>", ver="20", params=("From", "To"), extra_inc=("string",))
T("is_invocable", "指定した引数で呼び出せる型かを調べる。", "`f(args...)` と書ける型の組かを判定します。関数・関数ポインタ・ラムダ・メンバ関数ポインタを統一して調べられます。", "std::is_invocable_v<int (*)(int), int>", "std::is_invocable_v<int (*)(int), std::string>", ver="17", params=("F", "Args..."), extra_inc=("string",), sim=[("[`invoke_result`](invoke_result.md)", "戻り値の型を取る")])
T("is_invocable_r", "指定した引数で呼び出せ、結果を `R` に変換できる型かを調べる。", "`is_invocable` に、戻り値が `R` へ暗黙に変換できる条件を足したものです。", "std::is_invocable_r_v<double, int (*)(int), int>", "std::is_invocable_r_v<std::string, int (*)(int), int>", ver="17", params=("R", "F", "Args..."), extra_inc=("string",))
T("is_nothrow_invocable", "指定した引数で、例外を投げずに呼び出せるかを調べる。", "`noexcept` な関数だけを受け入れたいときに使います。", "std::is_nothrow_invocable_v<decltype(&Safe), int>", "std::is_nothrow_invocable_v<decltype(&Maybe), int>", ver="17", params=("F", "Args..."), pre="int Safe(int) noexcept;\nint Maybe(int);")
T("reference_constructs_from_temporary", "参照が、一時オブジェクトを作って束縛されるかを調べる。", "`const int&` を `int` から作ると、一時オブジェクトに束縛されます。その一時オブジェクトが、参照より先に消えてしまう危険を、コンパイル時に検出するために使います。", "std::reference_constructs_from_temporary_v<const int&, int>", "std::reference_constructs_from_temporary_v<const int&, int&>", ver="23", params=("T", "U"))
T("reference_converts_from_temporary", "参照が、暗黙の変換で一時オブジェクトに束縛されるかを調べる。", "`reference_constructs_from_temporary` の、暗黙の変換版です。`std::pair` などのライブラリが、ぶら下がった参照を禁止するために使います。", "std::reference_converts_from_temporary_v<const int&, int>", "std::reference_converts_from_temporary_v<const int&, int&>", ver="23", params=("T", "U"))

# ---- 値を返す特性
Q(TT + "alignment_of.md", "std::alignment_of", "型のアライメント（配置できる境界のバイト数）を調べる。", "rare", ["type_traits", "print"],
  "CPU はアドレスが決まった倍数でないと遅くなる（または動かない）ことがあります。型ごとに必要な倍数が「アライメント」で、`alignment_of_v<T>` で取れます。`alignof(T)` と同じ値です。",
  ["`alignof(T)` と同じ値。", "`double` は 8、`char` は 1 が多い。", "テンプレートの中で型から取りたいときに使う。"],
  "template <class T>\nstruct alignment_of : integral_constant<size_t, alignof(T)> {};\ntemplate <class T>\ninline constexpr size_t alignment_of_v = alignment_of<T>::value;", [("T", "型", "調べる型")], "アライメント（バイト）", 'std::println("{}", std::alignment_of_v<double>);\nstd::println("{}", std::alignment_of_v<char>);', "8\n1",
  use="自前のメモリプールで、型に合う境界に配置する", miss=("`sizeof` と取り違える", "`sizeof` は大きさ、`alignment_of` は置ける境界です。"), sim=[("[`std::align`](../../memory/align.md)", "ポインタを境界に合わせる")], cx="コンパイル時のみ", hub=TTH, hubname="<type_traits>", rj="type_traits/alignment_of.html", cr="types/alignment_of")
Q(TT + "is_corresponding_member.md", "std::is_corresponding_member", "2 つのメンバが、2 つの構造体の対応する位置にあるかを調べる。", "rare", ["type_traits", "print"],
  "先頭部分が同じ並びの 2 つの構造体で、「このメンバとこのメンバは対応しているか」を判定します。一方のメンバを、他方のメンバのように読み書きしてよいかの根拠になります。",
  ["メンバへのポインタを 2 つ渡す。", "`constexpr` の関数。", "ほとんど使わない。"],
  "template <class S1, class S2, class M1, class M2>\nconstexpr bool is_corresponding_member(M1 S1::* m1, M2 S2::* m2) noexcept;", [("m1, m2", "メンバへのポインタ", "比べる 2 つのメンバ")], "対応していれば `true`",
  'std::println("{}", std::is_corresponding_member(&P1::a, &P2::c));\nstd::println("{}", std::is_corresponding_member(&P1::a, &P2::d));', "true\nfalse",
  use="共通の先頭部分を持つ構造体の扱い", miss=("標準レイアウトでない型に使う", "標準レイアウトの型だけが対象です。"), sim=[("[`is_layout_compatible`](is_layout_compatible.md)", "全体のレイアウトが互換か")], cx="コンパイル時のみ", ver=V["20"], hub=TTH, hubname="<type_traits>", rj="type_traits/is_corresponding_member.html", cr="types/is_corresponding_member",
  pre="struct P1 {\n  int a;\n  char b;\n};\nstruct P2 {\n  int c;\n  char d;\n};")
Q(TT + "is_within_lifetime.md", "std::is_within_lifetime", "ポインタが指すオブジェクトが、いま寿命の中にあるかを調べる。", "rare", ["type_traits"],
  "`union` のどのメンバが有効かは、実行時に決まります。`constexpr` の中で「いま有効なメンバか」を調べたいときに、`is_within_lifetime(&u.i)` が使えます。定数式の中でだけ使える関数です。",
  ["定数式（`constexpr`）の中で使う。", "`union` の有効なメンバの判定に使う。", "C++26 の機能。"],
  "template <class T>\nconstexpr bool is_within_lifetime(const T* p) noexcept;", [("p", "const T*", "調べたいオブジェクトのポインタ")], "寿命の中なら `true`",
  'union U {\n  int i;\n  char c;\n};\n\nconstexpr bool Check() {\n  U u{.i = 1};\n  return std::is_within_lifetime(&u.i);\n}\nstatic_assert(Check());', None,
  use="`constexpr` の `union` で、有効なメンバを調べる", miss=("実行時に使う", "定数式の中でだけ使えます。"), sim=[("[`launder`](../../memory/new_delete/launder.md)", "寿命を新しくしたオブジェクトを指す")], cx="コンパイル時のみ", ver=V["26"], hub=TTH, hubname="<type_traits>", rj="type_traits/is_within_lifetime.html", cr="types/is_within_lifetime", compiler="C++26 の機能です。新しい標準ライブラリで使えます。")

# ---- 修飾・変換
def MOD(name, summary, intro, expr, ex_t, ver="11", params=("T",), miss=None, sim=None, extra=""):
    Q(TT + name + ".md", "std::" + name, summary, "rare", ["type_traits", "print"], intro,
      [f"`::type` の代わりに `std::{name}_t<T>` と書ける。", "コンパイル時に型を作り換える。", "値ではなく型を扱う。"],
      f"template <class {', class '.join(params)}>\nstruct {name} {{ using type = /* {summary.rstrip('。')} */; }};\ntemplate <class {', class '.join(params)}>\nusing {name}_t = typename {name}<{', '.join(params)}>::type;",
      [(p, "型", "元の型") for p in params], "変換後の型（`::type`）", f'using R = std::{name}_t<{expr}>;\nstd::println("{{}}", std::is_same_v<R, {ex_t}>);', "true",
      use="テンプレートの中で、型から余計な修飾を取り除く・付け足す", miss=miss or ("`::type` を付け忘れる", f"`std::{name}<T>` は型を持つ構造体です。型そのものが欲しいときは `_t` を使います。"),
      sim=sim or [("[`remove_cvref`](remove_cvref.md)", "const・volatile・参照をまとめて外す")], cx="コンパイル時のみ", ver=V[ver], hub=TTH, hubname="<type_traits>", rj=f"type_traits/{name}.html", cr=f"types/{name}")


MOD("remove_cv", "`const` と `volatile` を取り除く。", "`const int` や `volatile int` から、`const`・`volatile` を外した `int` を作りたいときに使います。参照やポインタの修飾は外しません。", "const volatile int", "int")
MOD("remove_const", "`const` を取り除く。", "`const int` から `const` を外した `int` を作ります。`volatile` は残ります。", "const int", "int")
MOD("remove_volatile", "`volatile` を取り除く。", "`volatile int` から `volatile` を外した `int` を作ります。`const` は残ります。", "volatile int", "int")
MOD("add_cv", "`const volatile` を付け足す。", "型に `const` と `volatile` をまとめて付けます。", "int", "const volatile int")
MOD("add_const", "`const` を付け足す。", "型に `const` を付けます。参照には付けられない（参照自体は const にならない）ので、そのままです。", "int", "const int")
MOD("add_volatile", "`volatile` を付け足す。", "型に `volatile` を付けます。", "int", "volatile int")
MOD("remove_reference", "参照を取り除く。", "`int&` や `int&&` から参照を外して、`int` にします。`std::move` の実装でも使われます。", "int&", "int", sim=[("[`remove_cvref`](remove_cvref.md)", "const も外す"), ("[`add_lvalue_reference`](add_lvalue_reference.md)", "参照を付ける")])
MOD("add_lvalue_reference", "左辺値参照を付け足す。", "`int` から `int&` を作ります。`void` には付けられないので、そのままです。", "int", "int&")
MOD("add_rvalue_reference", "右辺値参照を付け足す。", "`int` から `int&&` を作ります。`std::declval` の実装でも使われます。", "int", "int&&")
MOD("make_signed", "符号なしの整数型を、同じ大きさの符号付きにする。", "`unsigned int` から `int` を作ります。符号を気にせず、同じサイズの符号付き整数を得たいときに使います。", "unsigned", "int", sim=[("[`make_unsigned`](make_unsigned.md)", "逆の変換")])
MOD("remove_extent", "配列の最初の次元を取り除く。", "`int[3]` から `int` を作ります。多次元配列では、一番外側の次元だけを外します。", "int[3]", "int", sim=[("[`remove_all_extents`](remove_all_extents.md)", "全部の次元を外す")])
MOD("remove_all_extents", "配列の全部の次元を取り除く。", "`int[2][3]` から `int` を作ります。", "int[2][3]", "int")
MOD("remove_pointer", "ポインタを取り除く。", "`int*` から `int` を作ります。ポインタでない型は、そのままです。", "int*", "int", sim=[("[`add_pointer`](add_pointer.md)", "ポインタを付ける")])
MOD("add_pointer", "ポインタを付け足す。", "`int` から `int*` を作ります。参照があれば、先に外してからポインタを付けます。", "int", "int*")
Q(TT + "aligned_storage.md", "std::aligned_storage", "指定した大きさと境界の、生のメモリ領域の型。", "rare", ["type_traits", "print"],
  "`std::optional` や自作のコンテナのように、あとでオブジェクトを作る前の「ただのメモリ」を用意したいことがあります。`aligned_storage<Size, Align>` は、その大きさと境界のメモリを表す型です。C++23 で非推奨になり、`alignas` を付けた `std::byte` 配列に置き換えるのが推奨されています。",
  ["C++23 で非推奨。`alignas(T) std::byte buf[sizeof(T)];` が代わりになる。", "`::type` が領域の型、`_t` 版もある。", "領域は初期化されない。"],
  "template <size_t Len, size_t Align = /* 既定 */>\nstruct aligned_storage { using type = /* Len バイト、Align 境界の POD */; };\ntemplate <size_t Len, size_t Align = /* 既定 */>\nusing aligned_storage_t = typename aligned_storage<Len, Align>::type;",
  [("Len", "size_t", "大きさ（バイト）"), ("Align", "size_t", "境界（省略可）")], "領域の型（`::type`）", 'std::println("{}", sizeof(std::aligned_storage_t<16, 8>));\nstd::println("{}", alignof(std::aligned_storage_t<16, 8>));', "16\n8",
  use="あとでオブジェクトを作るためのメモリを用意する", miss=("新しいコードで使う", "非推奨です。`alignas(T) std::byte buf[sizeof(T)];` を使います。"), sim=[("[`aligned_union`](aligned_union.md)", "複数の型を入れられる領域")], cx="コンパイル時のみ", hub=TTH, hubname="<type_traits>", rj="type_traits/aligned_storage.html", cr="types/aligned_storage", compiler="C++11 から使えます。C++23 で非推奨になりました。")
Q(TT + "aligned_union.md", "std::aligned_union", "複数の型のどれでも入れられる、生のメモリ領域の型。", "rare", ["type_traits", "print"],
  "いくつかの型のどれか 1 つを入れられる領域（`union` のようなもの）が欲しいが、`union` は非トリビアルな型を入れにくい、ということがあります。`aligned_union<MinLen, Types...>` は、すべての型を入れられる大きさと境界の領域を表します。C++23 で非推奨になりました。",
  ["C++23 で非推奨。", "`::type` が領域の型、`alignment_value` が境界。", "`variant` を使うほうが安全。"],
  "template <size_t Len, class... Types>\nstruct aligned_union {\n  static constexpr size_t alignment_value = /* 最大のアライメント */;\n  using type = /* 領域の型 */;\n};",
  [("Len", "size_t", "最低限の大きさ"), ("Types...", "型", "入れたい型の一覧")], "領域の型と境界", 'std::println("{}", std::aligned_union<0, int, double>::alignment_value);\nstd::println("{}", sizeof(std::aligned_union_t<0, int, double>));', "8\n8",
  use="複数の型のどれかを入れる領域を用意する", miss=("新しいコードで使う", "非推奨です。`std::variant` か、`alignas` の `std::byte` 配列を使います。"), sim=[("[`aligned_storage`](aligned_storage.md)", "1 つの型の領域")], cx="コンパイル時のみ", hub=TTH, hubname="<type_traits>", rj="type_traits/aligned_union.html", cr="types/aligned_union", compiler="C++11 から使えます。C++23 で非推奨になりました。")

# ---- メタ関数
Q(TT + "enable_if.md", "std::enable_if", "条件が真のときだけ、型を存在させる（SFINAE のための道具）。", "sometimes", ["type_traits", "print", "string"],
  "同じ名前の関数を、整数用と小数用で書き分けたいとき、テンプレートの条件で「この型のときだけ有効」と決めたくなります。`enable_if<条件, T>` は、条件が真のときだけ `::type` を持ち、偽だと型がなくなるため、その関数が候補から外れます（SFINAE）。C++20 では `requires` やコンセプトが読みやすいです。",
  ["`enable_if_t<条件, T>`: 条件が真なら `T`、偽ならコンパイルエラー（候補から外れる）。", "関数テンプレートの追加の引数に、`std::enable_if_t<条件, int> = 0` と書くのが定番。", "C++20 以降は `requires` を優先する。"],
  "template <bool B, class T = void>\nstruct enable_if {};  // B が false のとき ::type はない\ntemplate <class T>\nstruct enable_if<true, T> { using type = T; };\ntemplate <bool B, class T = void>\nusing enable_if_t = typename enable_if<B, T>::type;",
  [("B", "bool", "条件"), ("T", "型", "条件が真のときの型（既定は `void`）")], "条件が真なら `T`", 'std::println("{} {}", Describe(1), Describe(1.0f));', "integer float",
  use="型ごとに関数を書き分ける", miss=("両方の条件が重なる", "条件が重なると、候補が複数になり、曖昧でコンパイルエラーになります。条件は排他的にします。"), sim=[("[`conditional`](conditional.md)", "条件で型を選ぶ"), ("[`concepts`](../concepts/same_as.md)", "C++20 の書き方")], cx="コンパイル時のみ",
  pre="template <class T, std::enable_if_t<std::is_integral_v<T>, int> = 0>\nstd::string Describe(T) {\n  return \"integer\";\n}\ntemplate <class T, std::enable_if_t<std::is_floating_point_v<T>, int> = 0>\nstd::string Describe(T) {\n  return \"float\";\n}",
  hub=TTH, hubname="<type_traits>", rj="type_traits/enable_if.html", cr="types/enable_if")
for nm, summ, intro, expr, tr, fa, sim_ in [
    ("conjunction", "複数の条件がすべて真かを調べる（短絡評価）。", "`is_integral<T> && is_signed<T>` のような条件を、型特性のまま組み合わせます。先に偽になった時点で、残りの型を調べずに止まります。", "std::conjunction_v<std::is_integral<int>, std::is_signed<int>>", "true", "std::conjunction_v<std::is_integral<int>, std::is_unsigned<int>>", [("[`disjunction`](disjunction.md)", "どれかが真か"), ("[`negation`](negation.md)", "否定")]),
    ("disjunction", "複数の条件のどれかが真かを調べる（短絡評価）。", "`is_integral<T> || is_floating_point<T>` のような条件を、型特性のまま組み合わせます。先に真になった時点で、残りを調べずに止まります。", "std::disjunction_v<std::is_integral<float>, std::is_floating_point<float>>", "true", "std::disjunction_v<std::is_integral<float>, std::is_void<float>>", [("[`conjunction`](conjunction.md)", "すべてが真か"), ("[`negation`](negation.md)", "否定")]),
    ("negation", "型特性の結果を反転する。", "`!is_void<T>::value` のように書く代わりに、`negation<is_void<T>>` と書くと、型特性として他の組み合わせ（`conjunction` など）に渡せます。", "std::negation_v<std::is_void<int>>", "true", "std::negation_v<std::is_void<void>>", [("[`conjunction`](conjunction.md)", "すべてが真か")])]:
    Q(TT + nm + ".md", "std::" + nm, summ, "rare", ["type_traits", "print"], intro, ["`_v` 版で `bool` の定数が取れる。", "型特性を組み合わせる道具（メタ関数）。", "C++20 では `requires` の `&&` `||` `!` が読みやすい。"],
      f"template <class... B>\nstruct {nm};\ntemplate <class... B>\ninline constexpr bool {nm}_v = {nm}<B...>::value;" if nm != "negation" else "template <class B>\nstruct negation;\ntemplate <class B>\ninline constexpr bool negation_v = negation<B>::value;",
      [("B...", "型特性", "組み合わせる型特性（`::value` をもつ型）")], "結果の `bool`（`::value`）", f'std::println("{{}}", {expr});\nstd::println("{{}}", {fa});', f"{tr}\nfalse",
      use="テンプレートの条件を、複数の型特性で組み合わせる", miss=("`::value` を持たない型を渡す", "型特性（`::value` を持つ型）を渡します。値の `bool` ではなく型です。"), sim=sim_, cx="コンパイル時のみ", ver=V["17"], hub=TTH, hubname="<type_traits>", rj=f"type_traits/{nm}.html", cr=f"types/{nm}")
Q(TT + "common_reference.md", "std::common_reference", "複数の型が共有できる、共通の参照型を求める。", "rare", ["type_traits", "print"],
  "`a ? b : c` のように、2 つの型を 1 つの式で扱うとき、型の「共通の姿」が必要です。`common_type` は値の型を、`common_reference` は参照も含めた型を決めます。`int&` と `const int&` からは `const int&` が得られます。",
  ["`common_reference_t<T...>` で型が取れる。", "共通の参照型がなければ、型を持たない（SFINAE で使える）。", "`ranges` ライブラリが内部で使う。"],
  "template <class... T>\nstruct common_reference { using type = /* 共通の参照型 */; };\ntemplate <class... T>\nusing common_reference_t = typename common_reference<T...>::type;", [("T...", "型", "共通の参照型を求めたい型")], "共通の参照型（`::type`）",
  'using R = std::common_reference_t<int&, const int&>;\nstd::println("{}", std::is_same_v<R, const int&>);', "true",
  use="ジェネリックなライブラリで、型の共通の姿を決める", miss=("`common_type` と取り違える", "`common_type` は値（コピー）の型です。参照が保たれません。"), sim=[("[`common_type`](common_type.md)", "値の型")], cx="コンパイル時のみ", ver=V["20"], hub=TTH, hubname="<type_traits>", rj="type_traits/common_reference.html", cr="types/common_reference")
Q(TT + "type_identity.md", "std::type_identity", "何もしない型変換（テンプレート引数の推論を止めるのに使う）。", "rare", ["type_traits", "print"],
  "`Max2(1.5, 1)` のように、`double` と `int` を混ぜて呼ぶと、`template <class T> T Max2(T a, T b)` は T を 2 通りに推論して失敗します。片方を `type_identity_t<T>` で包むと、その引数からは T を推論しなくなり、`double` に統一できます。",
  ["`type_identity_t<T>` は `T` そのもの。", "推論に使われない文脈（non-deduced context）にするために使う。", "「ここは推論しない」と示す、目印として働く。"],
  "template <class T>\nstruct type_identity { using type = T; };\ntemplate <class T>\nusing type_identity_t = typename type_identity<T>::type;", [("T", "型", "そのまま返す型")], "`T` そのもの", 'std::println("{}", Max2(1.5, 1));', "1.5",
  use="第 1 引数の型で、第 2 引数を決める", miss=("両方を包む", "全部の引数を包むと、どこからも T を推論できなくなります。1 つは普通に書きます。"), sim=[("[`decay`](decay.md)", "型を値渡し用に変換")], cx="コンパイル時のみ", ver=V["20"],
  pre="template <class T>\nT Max2(T a, std::type_identity_t<T> b) {\n  return a > b ? a : b;\n}", hub=TTH, hubname="<type_traits>", rj="type_traits/type_identity.html", cr="types/type_identity")
Q(TT + "void_t.md", "std::void_t", "どんな型を渡しても `void` になる別名（検出イディオム用）。", "rare", ["type_traits", "print", "vector"],
  "「この型に `size()` というメンバがあるか」をコンパイル時に調べたいとき、`void_t<decltype(declval<T>().size())>` と書きます。式が正しければ `void` になり、間違っていれば SFINAE で候補から外れます。これで、メンバの有無を調べる型特性が書けます（検出イディオム）。C++20 では `requires` が簡単です。",
  ["どんな型も `void` に変える。", "式の正しさを、SFINAE で調べるのに使う。", "C++20 では `requires` 式のほうが読みやすい。"],
  "template <class... Ts>\nusing void_t = void;", [("Ts...", "型", "SFINAE で調べたい型（式の `decltype` など）")], "常に `void`", 'std::println("{} {}", HasSize<std::vector<int>>::value, HasSize<int>::value);', "true false",
  use="メンバや式が使えるかをコンパイル時に調べる", miss=("`void` を返すと思って使う", "`void_t` は「式が正しいか」を調べる道具です。戻り値の型として使うものではありません。"), sim=[("[`enable_if`](enable_if.md)", "条件で型を存在させる")], cx="コンパイル時のみ", ver=V["17"],
  pre="template <class T, class = void>\nstruct HasSize : std::false_type {};\ntemplate <class T>\nstruct HasSize<T, std::void_t<decltype(std::declval<T>().size())>> : std::true_type {};", hub=TTH, hubname="<type_traits>", rj="type_traits/void_t.html", cr="types/void_t")
Q(TT + "is_constant_evaluated.md", "std::is_constant_evaluated", "いま、コンパイル時に評価されているかを調べる。", "rare", ["type_traits", "print"],
  "同じ `constexpr` 関数でも、コンパイル時には正確だが遅い方法を、実行時には速い方法を使い分けたいことがあります。`is_constant_evaluated()` は、その関数がコンパイル時の評価中なら `true` を返します。C++23 では `if consteval` が読みやすいです。",
  ["コンパイル時に評価されているときだけ `true`。", "`constexpr` 変数の初期化や `static_assert` の中が対象。", "C++23 では `if consteval` を優先する。"],
  "constexpr bool is_constant_evaluated() noexcept;", [], "コンパイル時に評価中なら `true`", 'constexpr int a = F(3);\nint n = 3;\nint b = F(n);\nstd::println("{} {}", a, b);', "3 -3",
  use="コンパイル時と実行時で処理を変える", miss=("`if constexpr` の条件に使う", "`if constexpr (std::is_constant_evaluated())` は常に `true` になります。普通の `if` に書きます。"), sim=[("[`if consteval`](@/basics/compiler.md)", "C++23 の書き方")], cx="定数", ver=V["20"],
  pre="constexpr int F(int n) {\n  return std::is_constant_evaluated() ? n : -n;\n}", hub=TTH, hubname="<type_traits>", rj="type_traits/is_constant_evaluated.html", cr="types/is_constant_evaluated")
for nm, what, intro, expr, val in [
    ("integral_constant", "コンパイル時の定数を、型として表す。", "型特性は、結果を `::value` に持つ型です。その土台になっているのが `integral_constant<T, v>` で、値 `v` を型の中に持ちます。自分でも、整数の定数を型として渡したいときに使えます。", "std::integral_constant<int, 5>::value", "5"),
    ("bool_constant", "`bool` のコンパイル時の定数を、型として表す。", "`integral_constant<bool, B>` の別名です。型特性の戻りの型として、`true_type` / `false_type` と共に使います。", "std::bool_constant<true>::value", "true"),
    ("true_type", "`true` を表すコンパイル時の定数の型。", "`bool_constant<true>` の別名です。型特性を自分で書くとき、真のときに継承します（`struct IsFoo : std::true_type {}`）。", "std::true_type::value", "true"),
    ("false_type", "`false` を表すコンパイル時の定数の型。", "`bool_constant<false>` の別名です。型特性の既定の結果として、`struct IsFoo : std::false_type {}` のように継承します。", "std::false_type::value", "false")]:
    Q(TT + nm + ".md", "std::" + nm, what, "rare", ["type_traits", "print"], intro, ["`::value` で値が取れる。", "型特性が継承する土台。", "`constexpr` 変数としても使える。"],
      "template <class T, T v>\nstruct integral_constant {\n  static constexpr T value = v;\n  using value_type = T;\n  using type = integral_constant;\n};" if nm == "integral_constant" else f"using {nm} = integral_constant<bool, {'true' if nm != 'false_type' else 'false'}>;",
      [("T, v", "型, 値", "定数の型と値")] if nm == "integral_constant" else [], "`value`（定数）", f'std::println("{{}}", {expr});', val,
      use="自作の型特性の土台にする", miss=("実行時の値を渡す", "テンプレート引数は、コンパイル時の定数です。"), sim=[("[`is_same`](is_same.md)", "型が同じか")], cx="コンパイル時のみ", ver=V["11"], hub=TTH, hubname="<type_traits>", rj=f"type_traits/{nm}.html", cr="types/integral_constant")

if __name__ == "__main__":
    flush_hubs()
