"""バッチ 3: memory / utility / variant / any / expected の未登録分。"""
from mk import *  # noqa: F401,F403

PTR = "[ポインタ](@/basics/pointer.md) が分かると読みやすいです。"
SP = "[`std::shared_ptr`](@/stl/utilities/shared_ptr.md) を先に読んでください。"
TPL = "[テンプレート](@/basics/template.md) が分かると読みやすいです。"
M = "memory/"
N = "memory/new_delete/"
U = "utilities/"

# ---------------- memory ----------------
P(M + "owner_hash.md", "std::owner_hash", "shared_ptr / weak_ptr を、持ち主（制御ブロック）で数えたハッシュ値を作る。", "rare", "memory",
  "`shared_ptr` を `unordered_map` のキーにするとき、普通のハッシュは**指している先のアドレス**で決まります。同じ持ち主でも、別のポインタ（エイリアス）を指すと別のキー扱いになります。`owner_hash` は**持ち主（制御ブロック）**を基準にハッシュを作ります。",
  ["`shared_ptr` と `weak_ptr` の両方に使え、同じ持ち主なら同じ値になる。", "`unordered_map` のキーに `weak_ptr` を使うときに、[`owner_equal`](owner_equal.md) とセットで使う。"],
  [("`weak_ptr` をキーにした表", "`std::unordered_map<std::weak_ptr<T>, V, std::owner_hash, std::owner_equal>`")],
  ("通常の `hash` と取り違える", "`std::hash<std::shared_ptr<T>>` は指している先のアドレスで決まります。持ち主基準にしたいときに限って `owner_hash` を使います。"),
  [("[`owner_less`](owner_less.md)", "持ち主基準の順序"), ("[`owner_equal`](owner_equal.md)", "持ち主基準の比較")],
  ["持ち主基準のハッシュ", "shared_ptr と weak_ptr で同じ値", "owner_equal とセット"],
  sig="struct owner_hash {\n  template <class T> size_t operator()(const shared_ptr<T>&) const noexcept;\n  template <class T> size_t operator()(const weak_ptr<T>&) const noexcept;\n  using is_transparent = void;\n};",
  args=[("p", "shared_ptr / weak_ptr", "ハッシュを作りたいポインタ")], ret="持ち主に対して決まる `size_t`", cx="定数",
  code="""#include <memory>
#include <print>

int main() {
  auto a = std::make_shared<int>(1);
  std::weak_ptr<int> w = a;
  std::println("{}", std::owner_hash{}(a) == std::owner_hash{}(w));
}""", out="true", ver=("26", "C++26"), info=SP, rj="memory/owner_hash.html", cr="memory/owner_hash", compiler="C++26 の機能です。新しい標準ライブラリで使えます。")

P(M + "owner_equal.md", "std::owner_equal", "shared_ptr / weak_ptr が、同じ持ち主（制御ブロック）かを比べる。", "rare", "memory",
  "`shared_ptr` を `==` で比べると「指している先が同じか」です。ところが、同じ持ち主を共有しつつ別の場所を指す（エイリアス）場合は、持ち主が同じかどうかを別に調べたくなります。`owner_equal` が、持ち主基準の比較を `shared_ptr` と `weak_ptr` の間でもできるようにします。",
  ["`shared_ptr` と `weak_ptr` を混ぜて比べられる。", "[`owner_hash`](owner_hash.md) とセットで、連想コンテナのキーに使う。"],
  [("`weak_ptr` が指していた持ち主かを調べる", "`std::owner_equal{}(shared, weak)`")],
  ("`==` と取り違える", "`==` は指している先、`owner_equal` は持ち主です。エイリアスのときに結果が変わります。"),
  [("[`owner_less`](owner_less.md)", "持ち主基準の順序"), ("[`owner_hash`](owner_hash.md)", "持ち主基準のハッシュ")],
  ["持ち主基準の等しさ", "shared_ptr と weak_ptr で比べられる", "owner_hash とセット"],
  sig="struct owner_equal {\n  template <class T, class U> bool operator()(const shared_ptr<T>&, const shared_ptr<U>&) const noexcept;\n  template <class T, class U> bool operator()(const weak_ptr<T>&, const weak_ptr<U>&) const noexcept;\n  using is_transparent = void;\n};",
  args=[("a, b", "shared_ptr / weak_ptr", "比べる 2 つ")], ret="同じ持ち主なら `true`", cx="定数",
  code="""#include <memory>
#include <print>

int main() {
  auto a = std::make_shared<int>(1);
  std::weak_ptr<int> w = a;
  auto b = std::make_shared<int>(1);
  std::println("{}", std::owner_equal{}(a, w));
  std::println("{}", std::owner_equal{}(a, b));
}""", out="true\nfalse", ver=("26", "C++26"), info=SP, rj="memory/owner_equal.html", cr="memory/owner_equal", compiler="C++26 の機能です。新しい標準ライブラリで使えます。")

P(M + "allocator_arg.md", "std::allocator_arg", "「次の引数はアロケータ」と示す目印。", "rare", "memory",
  "コンストラクタの引数にアロケータを渡したいとき、引数の並びだけでは「普通の引数」と区別できません。そこで `std::allocator_arg` という目印を最初に置いて、「次がアロケータです」と伝えます。`tuple` や `function` などのコンストラクタが使います。",
  ["`std::allocator_arg_t` 型の定数。", "`tuple(std::allocator_arg, alloc, 値...)` の形で使う。", "自作の型でアロケータを受けるときもこの形に合わせる。"],
  [("アロケータを指定して `tuple` を作る", "`std::tuple<int> t(std::allocator_arg, std::allocator<int>{}, 5);`")],
  ("目印を忘れる", "`allocator_arg` を置かないと、アロケータが普通の引数として扱われ、コンパイルエラーになります。"),
  [("[`uses_allocator`](uses_allocator.md)", "アロケータを受けられる型か調べる")],
  ["アロケータを渡す目印", "最初の引数に置く", "tuple などが使う"],
  sig="struct allocator_arg_t { explicit allocator_arg_t() = default; };\ninline constexpr allocator_arg_t allocator_arg{};",
  args=[], ret="なし（目印）", cx="なし",
  code="""#include <memory>
#include <print>
#include <tuple>

int main() {
  std::tuple<int> t(std::allocator_arg, std::allocator<int>{}, 5);
  std::println("{}", std::get<0>(t));
}""", out="5", info=PTR, rj="memory/allocator_arg_t.html", cr="memory/allocator_arg_t")

P(M + "uses_allocator.md", "std::uses_allocator", "型が、指定したアロケータを受け取れるかを調べる型特性。", "rare", "memory",
  "コンテナの中のコンテナのように、入れ物の中の要素にもアロケータを渡したいことがあります。そのために、要素の型が**そのアロケータを受け取れる型か**を調べるのが `uses_allocator` です。`vector` や `string` のように `allocator_type` を持つ型なら `true` になります。",
  ["`T::allocator_type` があり、`Alloc` に変換できれば `true`。", "標準コンテナは `std::allocator` に対して `true`。", "`scoped_allocator_adaptor` や pmr が内部で使う。"],
  [("要素がアロケータ対応かをコンパイル時に分岐", "`if constexpr (std::uses_allocator_v<T, Alloc>)`")],
  ("`int` などで `true` を期待する", "`allocator_type` を持たない型は `false` です。"),
  [("[`allocator_arg`](allocator_arg.md)", "アロケータを渡す目印"), ("[`make_obj_using_allocator`](make_obj_using_allocator.md)", "アロケータを渡して作る")],
  ["アロケータを受けられる型かの特性", "`_v` 版で bool", "標準コンテナは true"],
  sig="template <class T, class Alloc> struct uses_allocator;\ntemplate <class T, class Alloc> inline constexpr bool uses_allocator_v = uses_allocator<T, Alloc>::value;",
  args=[("T", "型", "調べる型"), ("Alloc", "型", "アロケータの型")], ret="受けられるなら `true`", cx="コンパイル時のみ",
  code="""#include <memory>
#include <print>
#include <vector>

int main() {
  std::println("{}", std::uses_allocator_v<std::vector<int>, std::allocator<int>>);
  std::println("{}", std::uses_allocator_v<int, std::allocator<int>>);
}""", out="true\nfalse", info=TPL, rj="memory/uses_allocator.html", cr="memory/uses_allocator")

P(M + "make_obj_using_allocator.md", "std::make_obj_using_allocator", "アロケータを渡しながら、オブジェクトを作る。", "rare", "memory",
  "アロケータを受けられる型を作るとき、「コンストラクタにアロケータを渡す形」は型によってまちまちです（先頭に `allocator_arg`、末尾に渡すなど）。`make_obj_using_allocator` は、型に合った形を自動で選んで作ります。",
  ["型がアロケータ対応かどうかで、渡し方を自動で選ぶ。", "結果は値で返る（ヒープ確保はしない）。", "`scoped_allocator_adaptor` や pmr のコンテナの中身を作るのに使われる。"],
  [("アロケータ付きの `vector` を作る", "`std::make_obj_using_allocator<std::vector<int>>(alloc, 3, 7);`")],
  ("アロケータ非対応の型に渡す", "`uses_allocator` が `false` の型では、アロケータは無視され、普通に構築されます。"),
  [("[`uses_allocator`](uses_allocator.md)", "対応型の判定"), ("[`construct_at`](new_delete/construct_at.md)", "場所を指定して作る")],
  ["アロケータ対応の作り方を自動で選ぶ", "値で返る", "pmr で活躍"],
  sig="template <class T, class Alloc, class... Args>\nconstexpr T make_obj_using_allocator(const Alloc& alloc, Args&&... args);",
  args=[("T", "テンプレート引数", "作りたい型"), ("alloc", "アロケータ", "渡すアロケータ"), ("args...", "引数", "`T` のコンストラクタに渡す引数")], ret="作った `T`", cx="`T` のコンストラクタに依存",
  code="""#include <memory>
#include <print>
#include <vector>

int main() {
  auto v = std::make_obj_using_allocator<std::vector<int>>(std::allocator<int>{}, 3, 7);
  std::println("{}", v);
}""", out="[7, 7, 7]", ver=("20", "C++20"), info=TPL, rj="memory/make_obj_using_allocator.html", cr="memory/make_obj_using_allocator")

P(M + "pointer_traits.md", "std::pointer_traits", "ポインタ（生ポインタやスマートポインタ）の性質を、同じ書き方で調べる。", "rare", "memory",
  "アロケータやコンテナを書くとき、「ポインタの指す型」や「ポインタを作る方法」を、生ポインタでも自作のスマートポインタでも同じ書き方で扱いたくなります。`pointer_traits<P>` は、そのための統一された入り口です。",
  ["`element_type` が指す先の型、`pointer_to(r)` が参照からポインタを作る。", "生ポインタ `T*` にも特殊化がある。", "自作のアロケータ `pointer` 型を扱うときに使う。"],
  [("ポインタ型に依存しない書き方", "`std::pointer_traits<Ptr>::element_type`")],
  ("生ポインタ以外に `&x` を使う", "自作のポインタ型では `&x` ではなく `pointer_to(x)` を使います。"),
  [("[`to_address`](to_address.md)", "ポインタから生ポインタを取り出す"), ("[`allocator_traits`](allocator_traits.md)", "アロケータの性質")],
  ["ポインタの性質をそろえて扱う入り口", "`element_type` と `pointer_to`", "アロケータ作りで登場"],
  sig="template <class Ptr> struct pointer_traits {\n  using pointer = Ptr;\n  using element_type = /* Ptr が指す型 */;\n  using difference_type = /* 差の型 */;\n  static pointer pointer_to(element_type& r);\n};",
  args=[("Ptr", "型", "調べるポインタ型")], ret="`element_type` などの型メンバと `pointer_to`", cx="コンパイル時のみ",
  code="""#include <memory>
#include <print>
#include <type_traits>

int main() {
  int x = 5;
  int* p = std::pointer_traits<int*>::pointer_to(x);
  std::println("{}", *p);
  std::println("{}", std::is_same_v<std::pointer_traits<int*>::element_type, int>);
}""", out="5\ntrue", info=PTR, rj="memory/pointer_traits.html", cr="memory/pointer_traits")

P(M + "assume_aligned.md", "std::assume_aligned", "ポインタが N バイト境界にあると、コンパイラに約束する。", "rare", "memory",
  "SIMD などで配列を速く処理するとき、コンパイラは「先頭アドレスが 16 バイト境界か」を知らないと、保守的なコードを出します。`assume_aligned<N>(p)` は、「このポインタは N バイト境界にある」と約束して、速いコードを出してもらう道具です。",
  ["約束が嘘だと**未定義動作**になる。", "N は 2 のべき乗。", "配列自体は `alignas(N)` や `aligned_alloc` で用意する。"],
  [("16 バイト境界の float 配列を SIMD で処理する前に伝える", "`float* p = std::assume_aligned<16>(buf);`")],
  ("境界に合っていないポインタを渡す", "約束が嘘だと未定義動作です。`alignas` で確保したものだけに使います。"),
  [("[`align`](align.md)", "ポインタを境界に合わせる"), ("[`aligned_alloc`](aligned_alloc.md)", "境界を指定して確保する")],
  ["「N バイト境界にある」とコンパイラに約束する", "嘘は未定義動作", "確保は alignas / aligned_alloc で"],
  sig="template <size_t N, class T>\nconstexpr T* assume_aligned(T* ptr);",
  args=[("N", "テンプレート引数", "境界のバイト数（2 のべき乗）"), ("ptr", "T*", "約束するポインタ")], ret="`ptr` と同じ値のポインタ", cx="定数",
  code="""#include <memory>
#include <print>

int main() {
  alignas(16) float buf[4] = {1, 2, 3, 4};
  float* p = std::assume_aligned<16>(buf);
  std::println("{}", p[2]);
}""", out="3", ver=("20", "C++20"), info=PTR, rj="memory/assume_aligned.html", cr="memory/assume_aligned")

P(M + "start_lifetime_as.md", "std::start_lifetime_as", "バイト列を、そのままの値で指定した型のオブジェクトとして使い始める。", "rare", "memory",
  "ネットワークやファイルから読んだバイト列を、`reinterpret_cast` で構造体として読むのは、厳密にはオブジェクトが存在しないので未定義動作です。`start_lifetime_as<T>(p)` は、「ここから `T` として使い始める」と宣言して、バイトの値を壊さずにオブジェクトの寿命を始めます。",
  ["`T` は暗黙的に寿命を始められる型（トリビアルな型）に限る。", "バイト列の中身は変わらない（初期化し直さない）。", "`memcpy` でコピーする方法の代わりになる。"],
  [("受信バッファを構造体として読む", "`auto* h = std::start_lifetime_as<Header>(buf);`")],
  ("非トリビアルな型を指定する", "コンストラクタが必要な型には使えません。`construct_at` や placement new を使います。"),
  [("[`launder`](new_delete/launder.md)", "同じ場所に作り直したオブジェクトを指す"), ("[`bit_cast`](../numeric/bit/bit_cast.md)", "値をコピーして型を変える")],
  ["バイト列をそのまま T として使い始める", "トリビアルな型だけ", "reinterpret_cast より安全"],
  sig="template <class T> T* start_lifetime_as(void* p) noexcept;\ntemplate <class T> const T* start_lifetime_as(const void* p) noexcept;",
  args=[("p", "void*", "`T` として使い始める場所（大きさと境界が合っていること）")], ret="寿命を始めた `T` へのポインタ", cx="定数",
  code="""#include <memory>
#include <print>

int main() {
  alignas(int) unsigned char buf[sizeof(int)] = {7, 0, 0, 0};
  int* p = std::start_lifetime_as<int>(buf);
  std::println("{}", sizeof(*p));
}""", out="4", ver=("23", "C++23"), info=PTR, rj="memory/start_lifetime_as.html", cr="memory/start_lifetime_as", compiler="C++23 の機能です。対応は新しい標準ライブラリに限られます。")

P(M + "scoped_allocator_adaptor.md", "std::scoped_allocator_adaptor", "入れ子のコンテナの全体に、同じアロケータを渡してくれる。", "rare", "memory",
  "`vector<string>` のように入れ子のコンテナで、外側の `vector` に渡したアロケータは、中の `string` には自動では渡りません。`scoped_allocator_adaptor` で包むと、**外側のアロケータを中の要素にも自動で渡して**くれます。",
  ["外側のアロケータで、中の要素もまとめて管理したいときに使う。", "pmr の `polymorphic_allocator` は、この伝播が最初から入っている。", "ふつうのゲームのコードでは、pmr を使うほうが簡単。"],
  [("入れ子の vector / string を同じ領域で確保する", "`std::vector<std::string, std::scoped_allocator_adaptor<MyAlloc<std::string>>>`")],
  ("pmr を使えば足りる場面で使う", "pmr のコンテナなら、同じ目的を [`pmr`](../memory/pmr.md) だけで書けて簡単です。"),
  [("[`polymorphic_allocator`](pmr/polymorphic_allocator.md)", "最初から伝播する"), ("[`allocator`](allocator.md)", "普通のアロケータ")],
  ["入れ子の要素にもアロケータを渡す", "pmr のほうが簡単", "<scoped_allocator>"],
  sig="template <class OuterAlloc, class... InnerAllocs>\nclass scoped_allocator_adaptor;",
  args=[("OuterAlloc", "アロケータ", "外側のアロケータ"), ("InnerAllocs...", "アロケータ", "省略可。内側のアロケータ")], ret="アロケータとして使う", cx="確保は外側のアロケータに依存",
  code="""#include <memory>
#include <print>
#include <scoped_allocator>
#include <string>
#include <vector>

int main() {
  using Alloc = std::scoped_allocator_adaptor<std::allocator<std::string>>;
  std::vector<std::string, Alloc> v;
  v.emplace_back("a");
  std::println("{}", v[0]);
}""", out="a", info=TPL, rj="scoped_allocator/scoped_allocator_adaptor.html", cr="memory/scoped_allocator_adaptor")

P(M + "pmr/pool_options.md", "std::pmr::pool_options", "プールのメモリリソースの、ブロックの大きさと数の設定。", "rare", "memory_resource",
  "プール方式のメモリリソースは、同じ大きさのブロックをまとめて用意します。「1 回にいくつ取るか」「どの大きさまでプールにするか」を、`pool_options` で指定します。",
  ["`max_blocks_per_chunk` と `largest_required_pool_block` の 2 つのメンバ。", "0 を指定すると実装の既定値になる。", "`unsynchronized_pool_resource` と `synchronized_pool_resource` に渡す。"],
  [("小さなオブジェクトを大量に作るプールの調整", "`opts.largest_required_pool_block = 256;`")],
  ("大きすぎる値を入れる", "`largest_required_pool_block` を大きくすると、プールを用意するメモリが増えます。実測してから決めます。"),
  [("[`unsynchronized_pool_resource`](unsynchronized_pool_resource.md)", "スレッド非対応のプール"), ("[`synchronized_pool_resource`](synchronized_pool_resource.md)", "スレッド対応のプール")],
  ["プールの設定をまとめた構造体", "0 は既定値", "プールの resource に渡す"],
  sig="struct pool_options {\n  size_t max_blocks_per_chunk = 0;\n  size_t largest_required_pool_block = 0;\n};",
  args=[("max_blocks_per_chunk", "size_t", "1 回の確保で用意するブロックの最大数"), ("largest_required_pool_block", "size_t", "プールで扱う最大のブロックサイズ（バイト）")], ret="なし（設定値）", cx="なし",
  code="""#include <memory_resource>
#include <print>

int main() {
  std::pmr::pool_options opts;
  opts.max_blocks_per_chunk = 64;
  opts.largest_required_pool_block = 256;
  std::pmr::unsynchronized_pool_resource pool(opts);
  std::println("{}", pool.options().max_blocks_per_chunk);
}""", out="64", info="[`memory_resource`](memory_resource.md) を先に読んでください。", rj="memory_resource/pool_options.html", cr="memory/pool_options", compiler="C++17 から使えます。", ver=("17", "C++17"))

# ---- uninitialized / destroy 系
dg = "メモリを用意してから 1 つずつ作る"
P(N + "destroy.md", "std::destroy", "範囲のオブジェクトのデストラクタを呼ぶ（メモリは返さない）。", "rare", "memory",
  "`vector` の中のように、自分で確保した領域に `construct_at` などで作ったオブジェクトを、まとめて壊したいときがあります。`std::destroy(first, last)` は範囲の全オブジェクトのデストラクタを呼びます。メモリは返さないので、そのあと自分で解放します。",
  ["デストラクタを呼ぶだけで、メモリは返さない。", "`int` のようなトリビアルな型では何もしない。", "個数を数で渡す版は [`destroy_n`](destroy_n.md)。"],
  [("自前のプールの中身を壊す", "`std::destroy(pool.begin(), pool.begin() + count);`")],
  ("デストラクタを二重に呼ぶ", "壊したあとのオブジェクトにもう一度 `destroy` を呼ぶと未定義動作です。"),
  [("[`destroy_at`](destroy_at.md)", "1 つだけ壊す"), ("[`destroy_n`](destroy_n.md)", "個数で指定")],
  ["範囲のデストラクタを呼ぶ", "メモリは返さない", "二重に呼ばない"],
  sig="template <class ForwardIt>\nconstexpr void destroy(ForwardIt first, ForwardIt last);",
  args=[("first, last", "イテレータ", "壊す範囲")], ret="なし", cx="線形（トリビアルな型なら何もしない）",
  code="""#include <memory>
#include <new>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  ~Tracer() { --alive; }
};

int main() {
  alignas(Tracer) unsigned char buf[sizeof(Tracer) * 2];
  auto* p = reinterpret_cast<Tracer*>(buf);
  std::construct_at(p);
  std::construct_at(p + 1);
  std::println("{}", Tracer::alive);
  std::destroy(p, p + 2);
  std::println("{}", Tracer::alive);
}""", out="2\n0", ver=("17", "C++17"), info=PTR, hub=None, rj="memory/destroy.html", cr="memory/destroy")

P(N + "destroy_n.md", "std::destroy_n", "先頭から n 個のオブジェクトのデストラクタを呼ぶ。", "rare", "memory",
  "壊す範囲を「先頭と個数」で持っているとき、`destroy` のようにペアでなく、個数で渡せる版が `destroy_n` です。最後に壊した位置の次を返します。",
  ["デストラクタを呼ぶだけで、メモリは返さない。", "戻り値は壊した最後の次の位置。"],
  [("先頭と個数で持っている配列を壊す", "`std::destroy_n(p, count);`")],
  ("個数を実際より多く指定する", "作っていない領域のデストラクタを呼ぶと未定義動作です。"),
  [("[`destroy`](destroy.md)", "範囲で指定"), ("[`destroy_at`](destroy_at.md)", "1 つだけ")],
  ["先頭と個数で壊す", "メモリは返さない", "戻り値は最後の次"],
  sig="template <class ForwardIt, class Size>\nconstexpr ForwardIt destroy_n(ForwardIt first, Size n);",
  args=[("first", "イテレータ", "壊す先頭"), ("n", "整数", "壊す個数")], ret="壊した最後の次の位置", cx="線形",
  code="""#include <memory>
#include <new>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  ~Tracer() { --alive; }
};

int main() {
  alignas(Tracer) unsigned char buf[sizeof(Tracer) * 3];
  auto* p = reinterpret_cast<Tracer*>(buf);
  for (int i = 0; i < 3; ++i) std::construct_at(p + i);
  auto* end = std::destroy_n(p, 3);
  std::println("{} {}", Tracer::alive, end - p);
}""", out="0 3", ver=("17", "C++17"), info=PTR, rj="memory/destroy_n.html", cr="memory/destroy_n")


def uninit(name, what, intro, game_rows, sig_a, sig_b, argsa, argsb, code, out, rjname, base_ret="最後に作った位置の次"):
    f1 = fn("std::" + name, sig_a, argsa, "最後に作った位置の次のイテレータ", "線形", None, ids=name)
    f2 = fn("std::" + name + "_n", sig_b, argsb, "最後に作った位置の次のイテレータ", "線形", None, ids=name + "_n")
    P(N + name + ".md", "std::" + name, what, "rare", "memory", intro,
      ["未初期化のメモリに、オブジェクトを作る。", "途中で例外が出たら、すでに作ったぶんを壊してから投げる。", f"個数で指定する版は `{name}_n`（同じページの下）。"],
      game_rows, ("すでにオブジェクトがある場所に使う", "この関数は**未初期化の領域**専用です。作ってあるオブジェクトの上に使うと、デストラクタが呼ばれずに壊れます。"),
      [("[`construct_at`](construct_at.md)", "1 つだけ作る"), ("[`destroy`](destroy.md)", "壊す")],
      ["未初期化のメモリにオブジェクトを作る", "例外が出たら作ったぶんを壊す", "`_n` は個数で指定"],
      secs=[f1, f2], code=code, out=out, ver=("17", "C++17") if "move" in name or "default" in name or "value" in name else None,
      info=PTR, rj=f"memory/{name}.html", cr=f"memory/{name}")


uninit("uninitialized_fill", "未初期化のメモリの範囲を、同じ値のコピーで埋める。",
       "自分で確保した領域に、同じ値のコピーをまとめて作りたいことがあります。`uninitialized_fill` は、`fill`（代入）と違い、まだオブジェクトがない領域に**コピーコンストラクタで作ります**。",
       [("確保した領域を 0 で埋めて使い始める", "`std::uninitialized_fill(p, p + n, 0);`")],
       "template <class ForwardIt, class T>\nvoid uninitialized_fill(ForwardIt first, ForwardIt last, const T& value);",
       "template <class ForwardIt, class Size, class T>\nForwardIt uninitialized_fill_n(ForwardIt first, Size n, const T& value);",
       [("first, last", "イテレータ", "未初期化の領域"), ("value", "T", "コピー元の値")], [("first", "イテレータ", "未初期化の領域の先頭"), ("n", "整数", "作る個数"), ("value", "T", "コピー元の値")],
       """#include <memory>
#include <print>
#include <string>

int main() {
  alignas(std::string) unsigned char buf[sizeof(std::string) * 2];
  auto* p = reinterpret_cast<std::string*>(buf);
  std::uninitialized_fill(p, p + 2, std::string("hi"));
  std::println("{} {}", p[0], p[1]);
  std::destroy(p, p + 2);
}""", "hi hi", "uninitialized_fill")
uninit("uninitialized_move", "未初期化のメモリに、範囲の要素をムーブして作る。",
       "`vector` の再確保のように、古い領域の中身を新しい未初期化の領域へ引っ越したいことがあります。`uninitialized_move` は、移動元をムーブして、移動先に新しいオブジェクトを作ります。",
       [("自作コンテナの再確保で、要素を新領域へ引っ越す", "`std::uninitialized_move(old_begin, old_end, new_begin);`")],
       "template <class InputIt, class NoThrowForwardIt>\nNoThrowForwardIt uninitialized_move(InputIt first, InputIt last, NoThrowForwardIt d_first);",
       "template <class InputIt, class Size, class NoThrowForwardIt>\npair<InputIt, NoThrowForwardIt> uninitialized_move_n(InputIt first, Size n, NoThrowForwardIt d_first);",
       [("first, last", "イテレータ", "移動元の範囲"), ("d_first", "イテレータ", "未初期化の移動先の先頭")], [("first", "イテレータ", "移動元の先頭"), ("n", "整数", "移動する個数"), ("d_first", "イテレータ", "未初期化の移動先の先頭")],
       """#include <memory>
#include <print>
#include <string>

int main() {
  std::string src[2] = {"a", "b"};
  alignas(std::string) unsigned char buf[sizeof(std::string) * 2];
  auto* p = reinterpret_cast<std::string*>(buf);
  std::uninitialized_move(src, src + 2, p);
  std::println("{} {}", p[0], p[1]);
  std::destroy(p, p + 2);
}""", "a b", "uninitialized_move")
uninit("uninitialized_default_construct", "未初期化のメモリに、デフォルト初期化でオブジェクトを作る。",
       "未初期化の領域にオブジェクトを並べたいが、値は何でもよいとき（あとで上書きする）、`uninitialized_default_construct` が使えます。`int` のような型は**初期化されないまま**（ゴミの値）ですが、クラスは既定コンストラクタが呼ばれます。",
       [("あとで全部上書きする配列を高速に用意する", "`std::uninitialized_default_construct(p, p + n);`")],
       "template <class ForwardIt>\nvoid uninitialized_default_construct(ForwardIt first, ForwardIt last);",
       "template <class ForwardIt, class Size>\nForwardIt uninitialized_default_construct_n(ForwardIt first, Size n);",
       [("first, last", "イテレータ", "未初期化の領域")], [("first", "イテレータ", "未初期化の領域の先頭"), ("n", "整数", "作る個数")],
       """#include <memory>
#include <print>
#include <string>

int main() {
  alignas(std::string) unsigned char buf[sizeof(std::string) * 2];
  auto* p = reinterpret_cast<std::string*>(buf);
  std::uninitialized_default_construct(p, p + 2);
  std::println("[{}] [{}]", p[0], p[1]);
  std::destroy(p, p + 2);
}""", "[] []", "uninitialized_default_construct")
uninit("uninitialized_value_construct", "未初期化のメモリに、値初期化でオブジェクトを作る。",
       "`int` のような型を 0 で初期化した状態で並べたいとき、`uninitialized_value_construct` を使います。`default_construct` と違い、`int` は **0 になります**。",
       [("0 初期化された配列を用意する", "`std::uninitialized_value_construct(p, p + n);`")],
       "template <class ForwardIt>\nvoid uninitialized_value_construct(ForwardIt first, ForwardIt last);",
       "template <class ForwardIt, class Size>\nForwardIt uninitialized_value_construct_n(ForwardIt first, Size n);",
       [("first, last", "イテレータ", "未初期化の領域")], [("first", "イテレータ", "未初期化の領域の先頭"), ("n", "整数", "作る個数")],
       """#include <memory>
#include <print>

int main() {
  alignas(int) unsigned char buf[sizeof(int) * 3];
  auto* p = reinterpret_cast<int*>(buf);
  std::uninitialized_value_construct(p, p + 3);
  std::println("{} {} {}", p[0], p[1], p[2]);
}""", "0 0 0", "uninitialized_value_construct")

add_secs("memory/new_delete/uninitialized_copy.md", fn("std::uninitialized_copy_n", "template <class InputIt, class Size, class NoThrowForwardIt>\nNoThrowForwardIt uninitialized_copy_n(InputIt first, Size n, NoThrowForwardIt d_first);",
  [("first", "イテレータ", "コピー元の先頭"), ("n", "整数", "コピーする個数"), ("d_first", "イテレータ", "未初期化のコピー先の先頭")], "最後に作った位置の次のイテレータ", "線形", None,
  notes="`uninitialized_copy` の個数指定版です。コピー元を「先頭と個数」で持っているときに使います。", ids="uninitialized_copy_n"))

# ---------------- utilities ----------------
P(U + "make_optional.md", "std::make_optional", "値から optional を作る（型を書かなくてよい）。", "sometimes", "optional",
  "`std::optional<int>{42}` のように型を書くのが面倒なとき、`make_optional(42)` なら型を推論して作ってくれます。`make_pair` や `make_tuple` の optional 版です。コンストラクタ引数だけを渡して、中でオブジェクトを作る形もあります。",
  ["値を渡すと型を推論する（`make_optional(42)` は `optional<int>`）。", "型を指定して引数を渡すと、その場でオブジェクトを作る。", "C++17 の CTAD（`std::optional o{42};`）でも同じことが書ける。"],
  [("関数の戻り値を optional で返す", "`return std::make_optional(value);`")],
  ("参照を渡したつもりでコピーされる", "`make_optional(x)` は `x` をコピーまたはムーブします。参照のまま保持するわけではありません。"),
  [("[`optional`](optional.md)", "optional の本体"), ("[`nullopt`](nullopt.md)", "値がない状態")],
  ["値から optional を作る", "型を指定して引数でも作れる", "CTAD でも同じ"],
  sig="template <class T> constexpr optional<decay_t<T>> make_optional(T&& value);\ntemplate <class T, class... Args> constexpr optional<T> make_optional(Args&&... args);",
  args=[("value", "T", "中に入れる値"), ("args...", "引数", "`T` のコンストラクタに渡す引数")], ret="作った `optional`", cx="定数 + 中身の構築",
  code="""#include <optional>
#include <print>
#include <string>

int main() {
  auto a = std::make_optional(42);
  auto b = std::make_optional<std::string>(3, 'a');
  std::println("{} {}", *a, *b);
}""", out="42 aaa", ver=("17", "C++17"), info="[`std::optional`](optional.md) を先に読んでください。", rj="optional/make_optional.html", cr="utility/optional/make_optional")

P(U + "in_place_type.md", "std::in_place_type", "variant / any / optional に、型を指定してその場で作らせる目印。", "rare", "utility",
  "`std::variant<int, std::string>` に文字列を入れたいとき、コンストラクタ引数だけでは「どの型で作るか」が曖昧です。`std::in_place_type<T>` を先頭に置くと、「T の型で、その場で作る」ことを指定できます。コピーやムーブが入らないので効率的です。",
  ["`variant`、`any` のコンストラクタや `emplace` で使う。", "型で指定するのが `in_place_type`、番号で指定するのが [`in_place_index`](in_place_index.md)。", "`optional` / `expected` は型が 1 つなので [`in_place`](in_place.md) を使う。"],
  [("variant にその場で文字列を作る", "`std::variant<int, std::string> v(std::in_place_type<std::string>, 3, 'x');`")],
  ("型が重複する variant で使う", "同じ型が複数あると型では選べません。`in_place_index` を使います。"),
  [("[`in_place`](in_place.md)", "型がひとつの場合"), ("[`in_place_index`](in_place_index.md)", "番号で指定")],
  ["型を指定してその場で作る目印", "variant / any で使う", "重複があれば in_place_index"],
  sig="template <class T> struct in_place_type_t { explicit in_place_type_t() = default; };\ntemplate <class T> inline constexpr in_place_type_t<T> in_place_type{};",
  args=[("T", "テンプレート引数", "その場で作る型")], ret="なし（目印）", cx="なし",
  code="""#include <print>
#include <string>
#include <utility>
#include <variant>

int main() {
  std::variant<int, std::string> v(std::in_place_type<std::string>, 3, 'x');
  std::println("{}", std::get<std::string>(v));
}""", out="xxx", ver=("17", "C++17"), info="[`std::variant`](variant.md) を先に読んでください。", rj="utility/in_place_type_t.html", cr="utility/in_place")

P(U + "in_place_index.md", "std::in_place_index", "variant に、番号を指定してその場で作らせる目印。", "rare", "utility",
  "`variant<int, int>` のように同じ型が複数あると、型では選べません。`std::in_place_index<N>` は、「N 番目の選択肢で、その場で作る」と番号で指定します。",
  ["番号は 0 から。", "型が重複しているときの選び方として使う。", "型で選ぶなら [`in_place_type`](in_place_type.md)。"],
  [("同じ型が並ぶ variant の 2 番目に入れる", "`std::variant<int, int> v(std::in_place_index<1>, 5);`")],
  ("番号が範囲外", "選択肢の数以上の番号を指定すると、コンパイルエラーになります。"),
  [("[`in_place_type`](in_place_type.md)", "型で指定")],
  ["番号を指定してその場で作る目印", "0 から数える", "型が重複するときに使う"],
  sig="template <size_t I> struct in_place_index_t { explicit in_place_index_t() = default; };\ntemplate <size_t I> inline constexpr in_place_index_t<I> in_place_index{};",
  args=[("I", "テンプレート引数", "選択肢の番号（0 から）")], ret="なし（目印）", cx="なし",
  code="""#include <print>
#include <utility>
#include <variant>

int main() {
  std::variant<int, int> v(std::in_place_index<1>, 5);
  std::println("{} {}", v.index(), std::get<1>(v));
}""", out="1 5", ver=("17", "C++17"), info="[`std::variant`](variant.md) を先に読んでください。", rj="utility/in_place_index_t.html", cr="utility/in_place")

P(U + "forward_like.md", "std::forward_like", "別の式の値カテゴリ（左辺値 / 右辺値、const）を、メンバにも引き継いで転送する。", "rare", "utility",
  "`this auto&& self` を使ったメンバ関数（deducing this）で、`self` が右辺値なら中のメンバも右辺値として返したいことがあります。`std::forward_like<T>(x)` は、`T` の左辺値・右辺値・const の性質を `x` に写して転送します。",
  ["`std::forward` は型 T のまま転送し、`forward_like` は **T の性質を別の x に写す**。", "deducing this で、メンバを返す関数を 1 つで書くときに使う。"],
  [("オブジェクトが右辺値ならメンバもムーブして返す", "`return std::forward_like<decltype(self)>(self.name);`")],
  ("`forward` と取り違える", "`forward<T>(x)` は x を T として転送します。`forward_like<T>(x)` は x の型を保ったまま、T の参照・const の性質を写します。"),
  [("[`forward`](forward.md)", "同じ型で転送する"), ("[`move`](move.md)", "右辺値にする")],
  ["T の性質を別の式に写して転送", "deducing this と相性がよい", "forward とは違う"],
  sig="template <class T, class U>\nconstexpr auto&& forward_like(U&& x) noexcept;",
  args=[("T", "テンプレート引数", "性質を借りる型（`decltype(self)` など）"), ("x", "U&&", "転送する式（メンバなど）")], ret="`T` の性質を写した `x` の参照", cx="定数",
  code="""#include <print>
#include <string>
#include <type_traits>
#include <utility>

struct Player {
  std::string name = "alice";
  auto&& GetName(this auto&& self) {
    return std::forward_like<decltype(self)>(self.name);
  }
};

int main() {
  Player p;
  std::println("{}", std::is_lvalue_reference_v<decltype(p.GetName())>);
  std::println("{}", std::is_rvalue_reference_v<decltype(std::move(p).GetName())>);
}""", out="true\ntrue", ver=("23", "C++23"), info="[`std::forward`](forward.md) と [`std::move`](move.md) を先に読んでください。", rj="utility/forward_like.html", cr="utility/forward_like")

P(U + "index_sequence.md", "std::index_sequence", "0, 1, 2, … の番号の並びを、型で表す。", "rare", "utility",
  "タプルの要素を順番に取り出したいとき、`get<0>`、`get<1>`… と手で書くのは要素数が変わると破綻します。`index_sequence<0, 1, 2>` は、番号の並びを**テンプレート引数のパック**として持ち運べる型で、`get<I>(t)...` のように展開できます。",
  ["`std::index_sequence<I...>` は `integer_sequence<size_t, I...>` の別名。", "番号の並びは [`make_index_sequence`](make_index_sequence.md) で作る。", "関数の引数に `std::index_sequence<I...>` を受けて、パックとして展開する。"],
  [("タプルの全要素に同じ処理をする", "`((f(std::get<I>(t))), ...);` を `index_sequence<I...>` の関数に書く")],
  ("size_t 以外の番号にしたい", "`index_sequence` は `size_t` 固定です。別の整数型なら [`integer_sequence`](integer_sequence.md) を使います。"),
  [("[`integer_sequence`](integer_sequence.md)", "整数型を選べる"), ("[`make_index_sequence`](make_index_sequence.md)", "0〜N-1 を作る")],
  ["番号の並びを型として持つ", "パックとして展開して使う", "作るのは make_index_sequence"],
  sig="template <size_t... Is>\nusing index_sequence = integer_sequence<size_t, Is...>;",
  args=[("Is...", "size_t のパック", "番号の並び")], ret="型（値は持たない）", cx="コンパイル時のみ",
  code="""#include <print>
#include <tuple>
#include <utility>

template <class T, size_t... Is>
void PrintAll(const T& t, std::index_sequence<Is...>) {
  (std::println("{}", std::get<Is>(t)), ...);
}

int main() {
  std::tuple<int, double, const char*> t{1, 2.5, "abc"};
  PrintAll(t, std::make_index_sequence<3>{});
}""", out="1\n2.5\nabc", ver=("14", "C++14"), info=TPL, rj="utility/index_sequence.html", cr="utility/integer_sequence")

P(U + "make_index_sequence.md", "std::make_index_sequence", "0 から N-1 までの index_sequence を作る。", "rare", "utility",
  "`index_sequence<0, 1, 2, 3>` を手で書くのは大変です。`make_index_sequence<4>` と書けば、同じ型が作られます。タプルやパックの展開に使う番号列を作るときの入り口です。",
  ["`make_index_sequence<N>` は `index_sequence<0, 1, ..., N-1>`。", "N が 0 なら空の列。", "`N` は定数式でなければならない。"],
  [("タプルのサイズぶんの番号列を作る", "`std::make_index_sequence<std::tuple_size_v<T>>{}`")],
  ("N を実行時の値にする", "N はコンパイル時の定数です。実行時に決まる回数のループには使えません。"),
  [("[`index_sequence`](index_sequence.md)", "番号の並びの型"), ("[`index_sequence_for`](index_sequence_for.md)", "型のパックの個数ぶん")],
  ["0〜N-1 の番号列を作る", "N はコンパイル時の定数", "タプル展開の入り口"],
  sig="template <size_t N>\nusing make_index_sequence = make_integer_sequence<size_t, N>;",
  args=[("N", "size_t", "番号の個数")], ret="`index_sequence<0, ..., N-1>`", cx="コンパイル時のみ",
  code="""#include <array>
#include <print>
#include <utility>

template <size_t... Is>
auto ToArray(std::index_sequence<Is...>) {
  return std::array<size_t, sizeof...(Is)>{Is...};
}

int main() {
  std::println("{}", ToArray(std::make_index_sequence<4>{}));
}""", out="[0, 1, 2, 3]", ver=("14", "C++14"), info=TPL, rj="utility/make_index_sequence.html", cr="utility/integer_sequence")

P(U + "make_integer_sequence.md", "std::make_integer_sequence", "0 から N-1 までの integer_sequence を、整数型を選んで作る。", "rare", "utility",
  "`make_index_sequence` は番号の型が `size_t` 固定です。`int` や `unsigned` の番号が欲しいときは、`make_integer_sequence<T, N>` で整数型を指定します。",
  ["`make_integer_sequence<int, 4>` は `integer_sequence<int, 0, 1, 2, 3>`。", "`size_t` なら [`make_index_sequence`](make_index_sequence.md) と同じ。"],
  [("int の番号列で配列を初期化する", "`std::make_integer_sequence<int, 4>{}`")],
  ("負の N を指定する", "N は 0 以上の値です。"),
  [("[`make_index_sequence`](make_index_sequence.md)", "size_t 版"), ("[`integer_sequence`](integer_sequence.md)", "並びの型")],
  ["整数型を選べる番号列", "size_t なら make_index_sequence", "N はコンパイル時の定数"],
  sig="template <class T, T N>\nusing make_integer_sequence = integer_sequence<T, /* 0, 1, ..., N-1 */>;",
  args=[("T", "整数型", "番号の型"), ("N", "T", "番号の個数")], ret="`integer_sequence<T, 0, ..., N-1>`", cx="コンパイル時のみ",
  code="""#include <array>
#include <print>
#include <utility>

template <int... Is>
auto ToArray(std::integer_sequence<int, Is...>) {
  return std::array<int, sizeof...(Is)>{Is...};
}

int main() {
  std::println("{}", ToArray(std::make_integer_sequence<int, 4>{}));
}""", out="[0, 1, 2, 3]", ver=("14", "C++14"), info=TPL, rj="utility/make_integer_sequence.html", cr="utility/integer_sequence")

P(U + "index_sequence_for.md", "std::index_sequence_for", "型のパックの個数ぶんの index_sequence を作る。", "rare", "utility",
  "可変長テンプレート引数 `Ts...` と同じ個数の番号列がほしいとき、`index_sequence_for<Ts...>` と書けば `make_index_sequence<sizeof...(Ts)>` と同じものが作れます。",
  ["`index_sequence_for<Ts...>` は `make_index_sequence<sizeof...(Ts)>`。", "型のパックと番号を並べて展開したいときに使う。"],
  [("引数の型ごとに番号を振る", "`std::index_sequence_for<Args...>{}`")],
  ("パックが空", "パックが空なら空の列になります。展開側がそれに耐えるように書きます。"),
  [("[`make_index_sequence`](make_index_sequence.md)", "個数を直接指定")],
  ["型パックの個数ぶんの番号列", "sizeof... を書かずに済む", "展開に使う"],
  sig="template <class... T>\nusing index_sequence_for = make_index_sequence<sizeof...(T)>;",
  args=[("T...", "型のパック", "個数を数える型")], ret="`index_sequence<0, ..., sizeof...(T)-1>`", cx="コンパイル時のみ",
  code="""#include <print>
#include <utility>

int main() {
  using Seq = std::index_sequence_for<int, double, char>;
  std::println("{}", Seq::size());
}""", out="3", ver=("14", "C++14"), info=TPL, rj="utility/index_sequence_for.html", cr="utility/integer_sequence")

for nm, op, expr, res, rj in [
    ("cmp_not_equal", "a != b", "std::cmp_not_equal(-1, 4294967295u)", "true", "cmp_not_equal"),
    ("cmp_greater", "a > b", "std::cmp_greater(-1, 0u)", "false", "cmp_greater"),
    ("cmp_less_equal", "a <= b", "std::cmp_less_equal(-1, 0u)", "true", "cmp_less_equal"),
    ("cmp_greater_equal", "a >= b", "std::cmp_greater_equal(0u, -1)", "true", "cmp_greater_equal")]:
    raw = {"cmp_not_equal": "-1 != 4294967295u", "cmp_greater": "-1 > 0u", "cmp_less_equal": "-1 <= 0u", "cmp_greater_equal": "0u >= -1"}[nm]
    rawres = {"cmp_not_equal": "false（-1 が 4294967295 に変換されて等しくなる）", "cmp_greater": "true（-1 が大きな符号なしの値に変換される）", "cmp_less_equal": "false", "cmp_greater_equal": "false"}[nm]
    P("support/" + nm + ".md", "std::" + nm, f"符号付きと符号なしの整数を、安全に `{op.split()[1]}` で比べる。", "rare", "utility",
      f"`int` と `unsigned` を `{op.split()[1]}` で比べると、符号付きの側が符号なしに変換されて、`{raw}` が{rawres}。数学的に正しい比較にしたいときに、`{nm}` を使います。",
      ["整数型どうしだけで使える（`bool` や `char` は不可）。", "符号付きと符号なしを混ぜても、数学的に正しい結果になる。", "同系列: `cmp_equal`・`cmp_less` ほか。"],
      [("`vector::size()` と `int` の比較", f"`std::{nm}(i, v.size())`")],
      ("浮動小数点や char に使う", "整数型（`bool`・`char` 型を除く）だけが対象です。それ以外はコンパイルエラーになります。"),
      [("[`cmp_equal`](cmp_equal.md)", "`==`"), ("[`cmp_less`](cmp_less.md)", "`<`"), ("[`in_range`](in_range.md)", "値が型の範囲に入るか")],
      ["符号を考慮した整数の比較", "int と unsigned を混ぜても安全", "整数型だけ"],
      sig=f"template <class T, class U>\nconstexpr bool {nm}(T a, U b) noexcept;",
      args=[("a, b", "整数型", "比べる 2 つの値")], ret=f"`{op}` を数学的に評価した結果", cx="定数",
      code=f"""#include <print>
#include <utility>

int main() {{
  std::println("{{}}", {expr});
}}""", out=res, ver=("20", "C++20"), hub="support/utility-misc.md", hubname="小さな便利機能", rj=f"utility/{rj}.html", cr=f"utility/{rj}", group="小さな便利機能（<utility>）")

# ---- variant / any / expected
P(U + "variant_alternative.md", "std::variant_alternative", "variant の N 番目の選択肢の型を取り出す。", "rare", "variant",
  "`variant<int, double, std::string>` の「2 番目の型は何か」を、テンプレートの中で知りたいことがあります。`variant_alternative_t<N, V>` が、N 番目の選択肢の型を教えてくれます。",
  ["番号は 0 から。", "`_t` 版で型がそのまま取れる。", "選択肢の数は [`variant_size`](variant.md) で調べる。"],
  [("variant の各選択肢の型でテンプレートを展開", "`std::variant_alternative_t<I, V>`")],
  ("範囲外の番号", "選択肢の数以上の番号を渡すと、コンパイルエラーになります。"),
  [("[`std::variant`](variant.md)", "variant の本体")],
  ["N 番目の選択肢の型を取り出す", "`_t` 版を使う", "番号は 0 から"],
  sig="template <size_t I, class V> struct variant_alternative;\ntemplate <size_t I, class V> using variant_alternative_t = typename variant_alternative<I, V>::type;",
  args=[("I", "size_t", "選択肢の番号"), ("V", "variant 型", "調べる variant")], ret="I 番目の選択肢の型", cx="コンパイル時のみ",
  code="""#include <print>
#include <string>
#include <type_traits>
#include <variant>

int main() {
  using V = std::variant<int, double, std::string>;
  std::println("{}", std::is_same_v<std::variant_alternative_t<1, V>, double>);
}""", out="true", ver=("17", "C++17"), info="[`std::variant`](variant.md) を先に読んでください。", rj="variant/variant_alternative.html", cr="utility/variant/variant_alternative")

P(U + "variant_npos.md", "std::variant_npos", "variant が値を持たない状態を表す、index() の値。", "rare", "variant",
  "`variant` の代入中に例外が起きると、中身が壊れた「値なし」の状態（valueless）になることがあります。そのとき `v.index()` が返す特別な値が `std::variant_npos` です。",
  ["`size_t` の最大値（`-1`）。", "`v.valueless_by_exception()` でも同じ状態を調べられる。", "普通は気にしなくてよい。"],
  [("例外安全のテストで状態を確認する", "`v.index() == std::variant_npos`")],
  ("通常の variant で期待する", "例外が出ない限り、`index()` はこの値になりません。"),
  [("[`std::variant`](variant.md)", "variant の本体")],
  ["値なしの状態の index()", "size_t の最大値", "valueless_by_exception でも調べられる"],
  sig="inline constexpr size_t variant_npos = -1;",
  args=[], ret="なし（定数）", cx="なし",
  code="""#include <cstddef>
#include <print>
#include <variant>

int main() {
  std::variant<int, double> v;
  std::println("{}", v.index() == std::variant_npos);
  std::println("{}", std::variant_npos == static_cast<std::size_t>(-1));
}""", out="false\ntrue", ver=("17", "C++17"), info="[`std::variant`](variant.md) を先に読んでください。", rj="variant/variant_npos.html", cr="utility/variant/variant_npos")

P(U + "bad_any_cast.md", "std::bad_any_cast", "any_cast で、入っている型と違う型を取り出したときの例外。", "rare", "any",
  "`std::any` は、何でも入れられる代わりに、取り出すときに型を間違えると失敗します。参照やコピーで取り出す `any_cast<T>(a)` は、型が違うと `bad_any_cast` を投げます。ポインタ版の `any_cast<T>(&a)` は、投げずに `nullptr` を返します。",
  ["`std::exception` から派生。", "参照・値の `any_cast` が型違いのときに投げる。", "投げたくないなら、ポインタ版（`any_cast<T>(&a)`）で `nullptr` を確かめる。"],
  [("型が違うかもしれない取り出し", "`if (auto* p = std::any_cast<int>(&a)) { ... }`")],
  ("空の any から取り出す", "空の `any` からの取り出しも `bad_any_cast` です。`has_value()` で確かめます。"),
  [("[`std::any`](any.md)", "any の本体"), ("[`bad_variant_access`](../support/exceptions/bad_variant_access.md)", "variant の類似の例外")],
  ["any_cast の型違いで投げる例外", "ポインタ版は投げない", "has_value() で空を確かめる"],
  sig="class bad_any_cast : public bad_cast {\n public:\n  const char* what() const noexcept override;\n};",
  args=[], ret="`what()` はエラーを表す文字列", cx="なし",
  code="""#include <any>
#include <print>
#include <string>

int main() {
  std::any a = std::string("hello");
  try {
    int x = std::any_cast<int>(a);
    std::println("{}", x);
  } catch (const std::bad_any_cast&) {
    std::println("型が違う");
  }
}""", out="型が違う", ver=("17", "C++17"), info="[`std::any`](any.md) を先に読んでください。", rj="any/bad_any_cast.html", cr="utility/bad_any_cast")

P(U + "unexpect.md", "std::unexpect", "expected に、エラー側をその場で作らせる目印。", "rare", "expected",
  "`std::expected<int, std::string>` に、成功ではなく失敗を作りたいとき、コンストラクタ引数だけでは成功側と区別できません。先頭に `std::unexpect` を置くと、「次の引数でエラー側を作る」と指定できます。",
  ["`std::unexpect_t` 型の定数。", "`expected(std::unexpect, エラーの引数...)` の形で使う。", "エラーの値を作ってから包む [`std::unexpected`](unexpected.md) の別の書き方。"],
  [("エラーをその場で作った expected を返す", "`return std::expected<int, std::string>(std::unexpect, \"failed\");`")],
  ("成功側に使う", "成功側を作る場合は [`in_place`](in_place.md) です。"),
  [("[`unexpected`](unexpected.md)", "エラーを包む型"), ("[`in_place`](in_place.md)", "成功側をその場で作る")],
  ["エラー側をその場で作る目印", "expected の第 1 引数に置く", "unexpected の別の書き方"],
  sig="struct unexpect_t { explicit unexpect_t() = default; };\ninline constexpr unexpect_t unexpect{};",
  args=[], ret="なし（目印）", cx="なし",
  code="""#include <expected>
#include <print>
#include <string>

int main() {
  std::expected<int, std::string> e(std::unexpect, "error");
  std::println("{}", e.error());
}""", out="error", ver=("23", "C++23"), info="[`std::expected`](expected.md) を先に読んでください。", rj="expected/unexpect.html", cr="utility/expected/unexpect")

# utilities の pointer cast 3 つ
for nm, what, intro, code_, out_, miss_ in [
    ("static_pointer_cast", "shared_ptr の指す先を、static_cast で別の型に変える（持ち主は共有）。",
     "`shared_ptr<Base>` を `shared_ptr<Derived>` に変えたいとき、`shared_ptr(static_cast<Derived*>(p.get()))` と書くと、**別々の持ち主**になって二重解放します。`static_pointer_cast` なら**同じ持ち主を共有したまま**型だけ変えられます。",
     """#include <memory>
#include <print>

struct Base { virtual ~Base() = default; };
struct Derived : Base { int value = 42; };

int main() {
  std::shared_ptr<Base> b = std::make_shared<Derived>();
  auto d = std::static_pointer_cast<Derived>(b);
  std::println("{} {}", d->value, b.use_count());
}""", "42 2", ("型が違うオブジェクトに使う", "`static_cast` と同じで、実際の型が合っていなくても通ります。確実でないなら `dynamic_pointer_cast` を使います。")),
    ("const_pointer_cast", "shared_ptr の指す先から const を外す（持ち主は共有）。",
     "`shared_ptr<const T>` から const を外したいとき、`const_cast` で生ポインタを取り出して作り直すと別の持ち主になります。`const_pointer_cast` は持ち主を共有したまま const を外します。",
     """#include <memory>
#include <print>

int main() {
  std::shared_ptr<const int> c = std::make_shared<int>(1);
  auto m = std::const_pointer_cast<int>(c);
  *m = 5;
  std::println("{}", *c);
}""", "5", ("本当に const なオブジェクトを書き換える", "元のオブジェクトが const で作られていると、書き換えは未定義動作です。")),
    ("reinterpret_pointer_cast", "shared_ptr の指す先を、reinterpret_cast で別の型に見せる（持ち主は共有）。",
     "メモリの内容を別の型として見たいとき、`shared_ptr` を `reinterpret_cast` するには持ち主を共有したままにする必要があります。`reinterpret_pointer_cast` は、持ち主を共有したまま `reinterpret_cast` します。",
     """#include <memory>
#include <print>

int main() {
  auto u = std::make_shared<unsigned>(1);
  auto b = std::reinterpret_pointer_cast<unsigned char>(u);
  std::println("{}", u.use_count());
}""", "2", ("型の別名規則に反する読み書き", "`reinterpret_cast` と同じ制約があります。安全に読める保証があるときだけ使います。"))]:
    ver = ("17", "C++17") if nm == "reinterpret_pointer_cast" else None
    P(U + nm + ".md", "std::" + nm, what, "rare", "memory", intro,
      ["持ち主（制御ブロック）は共有される。", "生ポインタで作り直すと別の持ち主になり、二重解放になる。", "`dynamic_pointer_cast` は実行時に型を確かめる。"],
      [("基底クラスのポインタから派生クラスに" if nm == "static_pointer_cast" else "const の外し方を持ち主を保ったまま", f"`std::{nm}<T>(p);`")], miss_,
      [("[`dynamic_pointer_cast`](dynamic_pointer_cast.md)", "実行時に型を確かめる"), ("[`shared_ptr`](shared_ptr.md)", "共有所有のスマートポインタ")],
      ["持ち主を共有したまま型を変える", "生ポインタで作り直さない", "use_count が増える"],
      sig=f"template <class T, class U>\nshared_ptr<T> {nm}(const shared_ptr<U>& r) noexcept;",
      args=[("T", "テンプレート引数", "変換後の型"), ("r", "shared_ptr<U>", "変換元")], ret="変換後の `shared_ptr<T>`（持ち主は共有）", cx="定数",
      code=code_, out=out_, ver=ver, info=SP, rj=f"memory/{nm}.html", cr=f"memory/{nm}")

# make_unique / make_shared の for_overwrite 版
add_secs("utilities/make_unique.md", fn("std::make_unique_for_overwrite", "template <class T>\nunique_ptr<T> make_unique_for_overwrite();\ntemplate <class T>\nunique_ptr<T> make_unique_for_overwrite(size_t n);  // T[] 用",
  [("n", "size_t", "配列の要素数（`T[]` のとき）")], "`unique_ptr<T>`", "確保 1 回 + 初期化（なし）", None,
  notes="`make_unique<int[]>(n)` は全要素を 0 で値初期化します。`make_unique_for_overwrite` は**初期化せず**確保だけします（`int` なら中身は不定）。あとで全部上書きすると分かっている大きな配列で、0 埋めの時間を省けます。", ver=("20", "C++20"), ids="make_unique_for_overwrite"))
add_secs("utilities/make_shared.md", fn("std::make_shared_for_overwrite", "template <class T>\nshared_ptr<T> make_shared_for_overwrite();\ntemplate <class T>\nshared_ptr<T> make_shared_for_overwrite(size_t n);  // T[] 用",
  [("n", "size_t", "配列の要素数（`T[]` のとき）")], "`shared_ptr<T>`", "確保 1 回 + 初期化（なし）", None,
  notes="`make_shared<int[]>(n)` は全要素を 0 で値初期化します。`make_shared_for_overwrite` は**初期化せず**確保だけします。あとで全部上書きする大きな配列で、0 埋めを省くために使います。", ver=("20", "C++20"), ids="make_shared_for_overwrite"))

P("support/exceptions/bad_weak_ptr.md", "std::bad_weak_ptr", "期限切れの weak_ptr から shared_ptr を作ろうとしたときの例外。", "rare", "memory",
  "`weak_ptr` は、指している先がすでに解放されているかもしれません。`std::shared_ptr<T> s(w);` のように、`weak_ptr` から `shared_ptr` をコンストラクタで作ろうとして、先が解放済みだと `bad_weak_ptr` が投げられます。",
  ["`weak_ptr::lock()` は例外を投げず、空の `shared_ptr` を返す。", "コンストラクタで作ろうとしたときだけ例外になる。", "`std::exception` から派生。"],
  [("期限切れの確認", "`if (auto s = w.lock()) { ... }`（例外を使わない）")],
  ("コンストラクタで直接作る", "`shared_ptr<T> s(w);` は期限切れで例外です。普通は `lock()` を使います。"),
  [("[`weak_ptr`](../../utilities/weak_ptr.md)", "弱い参照"), ("[`shared_ptr`](../../utilities/shared_ptr.md)", "共有所有")],
  ["期限切れの weak_ptr から shared_ptr を作ると投げる", "lock() は投げない", "<memory>"],
  sig="class bad_weak_ptr : public exception {\n public:\n  const char* what() const noexcept override;\n};",
  args=[], ret="`what()` はエラーを表す文字列", cx="なし",
  code="""#include <memory>
#include <print>

int main() {
  std::weak_ptr<int> w;
  try {
    std::shared_ptr<int> s(w);
  } catch (const std::bad_weak_ptr&) {
    std::println("期限切れ");
  }
}""", out="期限切れ", info=SP, rj="memory/bad_weak_ptr.html", cr="memory/bad_weak_ptr")

if __name__ == "__main__":
    flush_hubs()
