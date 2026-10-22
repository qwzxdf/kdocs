"""バッチ 20: 次の層のクラス（path、stream、chrono、random、regex、locale ほか）のメンバ関数の節を足す。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import members  # noqa: E402
import b19  # noqa: E402
from b19 import GEN, SPEC, run  # noqa: E402

M = members.MEMBERS
M["containers/span.md"] = M["containers/span.md"]  # そのまま
M["utilities/variant.md"] = "index valueless_by_exception emplace swap operator= operator=="


def S(page, name, sig, desc, cx="定数"):
    SPEC[(page, name)] = (sig, desc, cx)


# ---- 既存のうち、個別の説明が要るもの
S("utilities/string_view.md", "at", "const_reference at(size_type pos) const;", "`pos` 番目の文字を、範囲チェックつきで返します。範囲外なら `std::out_of_range` を投げます。", "定数")
S("concurrency/thread.md", "join", "void join();", "スレッドが終わるまで待ちます。`join` も `detach` もしないままスレッドオブジェクトを破棄すると、`std::terminate` が呼ばれます。2 回呼ぶとエラーです。", "スレッドの終了まで待つ")
S("concurrency/unique_lock.md", "lock", "void lock();", "管理しているミューテックスをロックします。すでにロックを持っているときに呼ぶと、`std::system_error` です。`defer_lock` で作ったときに、あとからロックするのに使います。", "待つ時間による")
S("concurrency/shared_lock.md", "lock", "void lock();", "管理しているミューテックスを、共有ロックします。", "待つ時間による")
S("concurrency/timed_mutex.md", "lock", "void lock();", "ロックします。ほかのスレッドが持っているときは、解除されるまで待ちます。", "待つ時間による")
S("concurrency/timed_mutex.md", "try_lock", "bool try_lock();", "待たずに、ロックを試みます。取れたら `true`。", "定数")
S("concurrency/barrier.md", "arrive", "[[nodiscard]] arrival_token arrive(std::ptrdiff_t update = 1);", "フェーズの到着を知らせます（待ちません）。戻り値のトークンを `wait` に渡すと、フェーズの完了まで待てます。", "定数")
S("concurrency/barrier.md", "wait", "void wait(arrival_token&& arrival) const;", "`arrive` で得たトークンのフェーズが完了するまで、待ちます。", "待つ時間による")
S("io/ifstream.md", "get", "int get();\nistream& get(char& ch);\nistream& get(char* s, streamsize n, char delim = '\\n');", "空白や改行も含めて、1 文字（または複数文字）を読みます。`>>` が空白を読み飛ばすのと違い、そのまま読みます。", "O(読んだ文字数)")

# ---- path
P_ = "io/filesystem/path.md"
M[P_] = "operator= assign operator/= append operator+= concat clear make_preferred remove_filename replace_filename replace_extension swap native c_str string wstring u8string generic_string compare lexically_normal lexically_relative lexically_proximate root_name root_directory root_path relative_path parent_path filename stem extension empty has_root_name has_root_directory has_root_path has_relative_path has_parent_path has_filename has_stem has_extension is_absolute is_relative begin end operator/ operator== operator<=>"
PP = [
    ("operator=", "path& operator=(const path& p);\npath& operator=(path&& p) noexcept;\ntemplate <class Source> path& operator=(const Source& source);", "別の `path`、または文字列から代入します。", "O(長さ)"),
    ("assign", "template <class Source>\npath& assign(const Source& source);", "文字列などを代入します（`operator=` と同じ働き）。", "O(長さ)"),
    ("operator/=", "path& operator/=(const path& p);", "区切り文字（`/`）をはさんで、後ろにつなげます。`p` が絶対パスなら、置き換わります。", "O(長さ)"),
    ("append", "template <class Source>\npath& append(const Source& source);", "`operator/=` と同じ働きです。区切り文字をはさんで、後ろにつなげます。", "O(長さ)"),
    ("operator+=", "path& operator+=(const path& p);\npath& operator+=(const string_type& str);", "区切り文字を入れずに、後ろに文字列を足します。`player` に `.png` を足すときなどに使います。", "O(長さ)"),
    ("concat", "template <class Source>\npath& concat(const Source& source);", "`operator+=` と同じ働きです。区切り文字を入れずに、後ろに足します。", "O(長さ)"),
    ("clear", "void clear() noexcept;", "パスを空にします。", "定数"),
    ("make_preferred", "path& make_preferred();", "区切り文字を、その OS の好みの区切り（Windows なら `\\`）に変換します。", "O(長さ)"),
    ("remove_filename", "path& remove_filename();", "最後の要素（ファイル名）を取り除き、フォルダまでのパスにします。", "O(長さ)"),
    ("replace_filename", "path& replace_filename(const path& replacement);", "最後の要素（ファイル名）を、別のものに置き換えます。", "O(長さ)"),
    ("replace_extension", "path& replace_extension(const path& replacement = path());", "拡張子を置き換えます。空を渡すと、拡張子を取り除きます。`.` は自動で補われます。", "O(長さ)"),
    ("swap", "void swap(path& other) noexcept;", "2 つの `path` を入れ替えます。", "定数"),
    ("native", "const string_type& native() const noexcept;", "OS 固有の形式の文字列への参照。Windows では `std::wstring`、Linux では `std::string` です。OS の API に渡すときに使います。", "定数"),
    ("c_str", "const value_type* c_str() const noexcept;", "OS 固有の形式の、終端つきの C 文字列。Windows では `const wchar_t*` です。", "定数"),
    ("string", "std::string string() const;", "`std::string` に変換します。Windows では、実行時の文字コード（多くは ANSI）への変換が入るので、日本語の扱いに注意が必要です。", "O(長さ)"),
    ("wstring", "std::wstring wstring() const;", "`std::wstring` に変換します。Windows API に渡すときに便利です。", "O(長さ)"),
    ("u8string", "std::u8string u8string() const;", "UTF-8 の文字列に変換します（C++20 では `char8_t` の `u8string`）。文字コードを UTF-8 に統一するなら、これを使います。", "O(長さ)"),
    ("generic_string", "std::string generic_string() const;", "区切りを `/` にした、`std::string`（OS を問わず同じ形）。ログに出す、ファイルに保存する、といったときに使います。", "O(長さ)"),
    ("compare", "int compare(const path& p) const noexcept;", "要素ごとに比べて、小さければ負、等しければ 0、大きければ正を返します。", "O(長さ)"),
    ("lexically_normal", "path lexically_normal() const;", "`.` や `..` を取り除き、区切りを整えます。ファイルシステムは調べず、文字列だけで処理します。", "O(長さ)"),
    ("lexically_relative", "path lexically_relative(const path& base) const;", "`base` から見た相対パスを、文字列だけで求めます。ファイルシステムは調べません。", "O(長さ)"),
    ("lexically_proximate", "path lexically_proximate(const path& base) const;", "`lexically_relative` と同じですが、作れないときは元のパスを返します。", "O(長さ)"),
    ("root_name", "path root_name() const;", "ルートの名前（Windows のドライブ名 `C:` など）。", "O(長さ)"),
    ("root_directory", "path root_directory() const;", "ルートのフォルダ（`/`）。", "O(長さ)"),
    ("root_path", "path root_path() const;", "ルート名とルートフォルダを合わせたもの（`C:/`）。", "O(長さ)"),
    ("relative_path", "path relative_path() const;", "ルートを除いた残りのパス。", "O(長さ)"),
    ("parent_path", "path parent_path() const;", "親フォルダのパス（最後の要素を除いたもの）。", "O(長さ)"),
    ("filename", "path filename() const;", "最後の要素（ファイル名）。`assets/img/player.png` なら `player.png`。", "O(長さ)"),
    ("stem", "path stem() const;", "拡張子を除いたファイル名。`player.png` なら `player`。", "O(長さ)"),
    ("extension", "path extension() const;", "拡張子（`.` を含む）。`player.png` なら `.png`。拡張子がなければ空。", "O(長さ)"),
    ("empty", "[[nodiscard]] bool empty() const noexcept;", "パスが空なら `true`。", "定数"),
    ("has_root_name", "bool has_root_name() const;", "ルート名（ドライブ名）があれば `true`。", "O(長さ)"),
    ("has_root_directory", "bool has_root_directory() const;", "ルートフォルダ（先頭の `/`）があれば `true`。", "O(長さ)"),
    ("has_root_path", "bool has_root_path() const;", "ルートがあれば `true`。", "O(長さ)"),
    ("has_relative_path", "bool has_relative_path() const;", "ルート以降の部分があれば `true`。", "O(長さ)"),
    ("has_parent_path", "bool has_parent_path() const;", "親フォルダのパスがあれば `true`。", "O(長さ)"),
    ("has_filename", "bool has_filename() const;", "ファイル名があれば `true`。末尾が `/` だと `false`。", "O(長さ)"),
    ("has_stem", "bool has_stem() const;", "拡張子を除いたファイル名があれば `true`。", "O(長さ)"),
    ("has_extension", "bool has_extension() const;", "拡張子があれば `true`。", "O(長さ)"),
    ("is_absolute", "bool is_absolute() const;", "絶対パスなら `true`。Windows では、ドライブ名とルートの両方が必要です（`/a` は絶対パスではありません）。", "O(長さ)"),
    ("is_relative", "bool is_relative() const;", "相対パスなら `true`（`is_absolute()` の逆）。", "O(長さ)"),
    ("begin", "iterator begin() const;", "パスの要素（区切りごとの部分）の先頭。`for (auto& part : p)` でフォルダ名を順に取り出せます。", "定数"),
    ("end", "iterator end() const;", "パスの要素の終端。", "定数"),
    ("operator/", "path operator/(const path& lhs, const path& rhs);", "2 つのパスを、区切り文字ではさんでつなげた、新しい `path` を返します。`rhs` が絶対パスなら、`rhs` が結果です。", "O(長さ)"),
    ("operator==", "bool operator==(const path& lhs, const path& rhs) noexcept;", "パスが等しければ `true`。文字列の比較で、`a/b` と `a//b` は等しいと見なされますが、ファイルシステム上の同一性は調べません（それは `equivalent`）。", "O(長さ)"),
    ("operator<=>", "std::strong_ordering operator<=>(const path& lhs, const path& rhs) noexcept;", "パスを、要素ごとに比べる三方比較（C++20）。", "O(長さ)"),
]
for n, sg, d, cx in PP:
    S(P_, n, sg, d, cx)

# ---- directory_entry
D_ = "io/filesystem/directory_entry.md"
M[D_] = "assign replace_filename refresh path exists is_regular_file is_directory is_symlink is_other file_size hard_link_count last_write_time status symlink_status operator== operator<=>"
for n, sg, d, cx in [
    ("assign", "void assign(const path& p);", "別のパスを割り当てて、キャッシュをクリアします。", "定数"),
    ("replace_filename", "void replace_filename(const path& p);", "ファイル名を置き換えて、キャッシュをクリアします。", "定数"),
    ("refresh", "void refresh();", "キャッシュしている状態（サイズ・更新時刻など）を、いま調べ直します。走査のあとでファイルが変わった可能性があるときに使います。", "OS に依存"),
    ("path", "const path& path() const noexcept;\noperator const path&() const noexcept;", "エントリのパスを返します。`directory_iterator` で回したときに、ファイルの名前を取り出すのに使います。", "定数"),
    ("exists", "bool exists() const;", "存在するか。走査中に取得した情報のキャッシュを使うので、`fs::exists(p)` より速いことがあります。", "キャッシュがあれば定数"),
    ("is_regular_file", "bool is_regular_file() const;", "通常のファイルか。", "キャッシュがあれば定数"),
    ("is_directory", "bool is_directory() const;", "フォルダか。再帰的に走査するときの判定に使います。", "キャッシュがあれば定数"),
    ("is_symlink", "bool is_symlink() const;", "シンボリックリンクか。", "キャッシュがあれば定数"),
    ("is_other", "bool is_other() const;", "通常ファイル・フォルダ・リンクのどれでもない特殊なファイルか。", "キャッシュがあれば定数"),
    ("file_size", "std::uintmax_t file_size() const;", "ファイルの大きさ（バイト）。走査中のキャッシュを使うことがあります。", "キャッシュがあれば定数"),
    ("hard_link_count", "std::uintmax_t hard_link_count() const;", "ハードリンクの数。", "OS に依存"),
    ("last_write_time", "file_time_type last_write_time() const;", "最後に書き込まれた時刻。", "キャッシュがあれば定数"),
    ("status", "file_status status() const;", "ファイルの種類と権限（リンクをたどる）。", "キャッシュがあれば定数"),
    ("symlink_status", "file_status symlink_status() const;", "ファイルの種類と権限（リンクをたどらない）。", "キャッシュがあれば定数"),
    ("operator==", "bool operator==(const directory_entry& rhs) const noexcept;", "パスが等しければ `true`。", "O(長さ)"),
    ("operator<=>", "auto operator<=>(const directory_entry& rhs) const noexcept;", "パスで比べる三方比較（C++20）。", "O(長さ)"),
]:
    S(D_, n, sg, d, cx)

# ---- stringstream 系 / fstream
for pg, nm in [("io/istringstream.md", "istringstream"), ("io/ostringstream.md", "ostringstream"), ("io/stringstream.md", "stringstream")]:
    M[pg] = "str rdbuf swap view"
    S(pg, "str", "std::string str() const;\nvoid str(const std::string& s);", "中の文字列のコピーを返します。引数つきの版は、中の文字列を置き換え、読み書きの位置を先頭に戻します。", "O(長さ)")
    S(pg, "rdbuf", "std::stringbuf* rdbuf() const;", "中のバッファ（`stringbuf`）へのポインタ。", "定数")
    S(pg, "swap", f"void swap({nm}& other);", "中身（バッファとストリームの状態）を入れ替えます。", "定数")
    S(pg, "view", "std::string_view view() const noexcept;", "中の文字列を、コピーせずに `string_view` で見ます（C++20）。ストリームに書き込むと無効になります。", "定数")
M["io/fstream.md"] = "open close is_open rdbuf swap"
S("io/fstream.md", "open", "void open(const char* filename, std::ios_base::openmode mode = std::ios_base::in | std::ios_base::out);\nvoid open(const std::filesystem::path& p, std::ios_base::openmode mode = ...);", "ファイルを開きます。すでに開いているときは失敗します。開けたかどうかは、`is_open()` や `operator bool` で確かめます。", "OS に依存")
S("io/fstream.md", "close", "void close();", "ファイルを閉じます。バッファに残っているものは書き出されます。デストラクタでも自動で閉じられるので、早めに閉じたいときだけ呼びます。", "OS に依存")
S("io/fstream.md", "is_open", "bool is_open() const;", "ファイルが開いていれば `true`。", "定数")
S("io/fstream.md", "rdbuf", "std::filebuf* rdbuf() const;", "中のバッファ（`filebuf`）へのポインタ。", "定数")
S("io/fstream.md", "swap", "void swap(fstream& other);", "中身（ファイルとストリームの状態）を入れ替えます。", "定数")

# ---- mdspan / valarray / inplace_vector / flat_map
M["containers/mdspan.md"] = "accessor is_unique is_exhaustive is_strided swap operator= rank rank_dynamic extent static_extent"
for n, sg, d, cx in [
    ("accessor", "const accessor_type& accessor() const noexcept;", "要素へのアクセス方法（アクセサ）への参照。", "定数"),
    ("is_unique", "constexpr bool is_unique() const;", "異なる添字が、異なる要素を指すなら `true`。重なりがないことを示します。", "定数"),
    ("is_exhaustive", "constexpr bool is_exhaustive() const;", "すき間なく、全部の要素が連続して並ぶなら `true`。", "定数"),
    ("is_strided", "constexpr bool is_strided() const;", "各次元に一定のストライド（飛び幅）があれば `true`。", "定数"),
    ("swap", "friend constexpr void swap(mdspan& x, mdspan& y) noexcept;", "2 つの `mdspan` を入れ替えます。", "定数"),
    ("operator=", "mdspan& operator=(const mdspan&) = default;", "コピー代入。`mdspan` は軽い view なので、コピーはポインタなどのコピーです。", "定数"),
    ("rank_dynamic", "static constexpr rank_type rank_dynamic() noexcept;", "動的な（実行時に決まる）次元の数。", "定数"),
    ("static_extent", "static constexpr size_t static_extent(rank_type r) noexcept;", "r 番目の次元の、コンパイル時の大きさ（動的なら `dynamic_extent`）。", "定数"),
]:
    S("containers/mdspan.md", n, sg, d, cx)
M["containers/valarray.md"] = "apply shift cshift resize swap size operator[] operator="
for n, sg, d, cx in [
    ("apply", "valarray apply(T func(T)) const;", "全要素に関数を適用した、新しい `valarray` を返します。", "O(要素数)"),
    ("shift", "valarray shift(int count) const;", "要素を `count` だけずらします。あいた場所は 0 で埋めます（正で左、負で右）。", "O(要素数)"),
    ("cshift", "valarray cshift(int count) const;", "要素を `count` だけ循環させてずらします（あふれた要素が反対側に回る）。", "O(要素数)"),
    ("resize", "void resize(size_t n, T c = T());", "要素数を `n` にします。中身は `c` で埋められます（元の値は失われます）。", "O(n)"),
    ("swap", "void swap(valarray& v) noexcept;", "2 つの `valarray` を入れ替えます。", "定数"),
    ("size", "size_t size() const;", "要素の数。", "定数"),
    ("operator[]", "T& operator[](size_t n);\nslice_array<T> operator[](slice s);\nmask_array<T> operator[](const valarray<bool>& m);", "n 番目の要素を返します。`slice`・マスク・添字の配列を渡すと、その部分への参照が返ります。", "定数"),
    ("operator=", "valarray& operator=(const valarray& v);\nvalarray& operator=(const T& v);", "別の `valarray` を代入します。スカラーを代入すると、全要素がその値になります。", "O(要素数)"),
]:
    S("containers/valarray.md", n, sg, d, cx)
M["containers/inplace_vector.md"] = "unchecked_push_back unchecked_emplace_back try_emplace_back try_append_range"
for n, sg, d, cx in [
    ("unchecked_push_back", "constexpr reference unchecked_push_back(const T& value);", "容量の確認なしで、末尾に追加します。容量を超えると**未定義動作**です。確実に空きがあるとき（直前に `size() < capacity()` を確かめたなど）だけ使います。", "定数"),
    ("unchecked_emplace_back", "template <class... Args>\nconstexpr reference unchecked_emplace_back(Args&&... args);", "容量の確認なしで、末尾に要素をその場で作ります。容量を超えると未定義動作です。", "定数"),
    ("try_emplace_back", "template <class... Args>\nconstexpr pointer try_emplace_back(Args&&... args);", "空きがあれば末尾に要素を作って、そのポインタを返します。満杯なら例外を投げず、`nullptr` を返します。", "定数"),
    ("try_append_range", "template <ranges::input_range R>\nconstexpr ranges::borrowed_iterator_t<R> try_append_range(R&& rg);", "範囲の要素を、入るところまで末尾に追加します。入りきらない要素の手前で止まり、そのイテレータを返します。", "O(追加数)"),
]:
    S("containers/inplace_vector.md", n, sg, d, cx)
M["containers/flat_map.md"] = "emplace emplace_hint insert_or_assign count equal_range key_comp value_comp swap rbegin rend cbegin cend max_size operator=="
for n in ("emplace", "emplace_hint", "count", "equal_range", "key_comp", "value_comp", "swap", "cbegin", "cend", "max_size", "rbegin", "rend", "operator=="):
    pass  # GEN の説明を使う
S("containers/flat_map.md", "insert_or_assign", "template <class M>\npair<iterator, bool> insert_or_assign(const key_type& k, M&& obj);", "キーがなければ挿入し、あれば値を上書きします。`operator[]` と違い、値の型に既定構築が要りません。挿入は、ソート済みの配列の途中への挿入なので、後ろの要素が動きます。", "O(n)")

# ---- chrono
DU = "utilities/chrono/duration.md"
M[DU] = "operator+ operator- operator* operator/ operator% operator+= operator-= operator== operator<=>"
for n, sg, d, cx in [
    ("operator+", "template <class Rep1, class Period1, class Rep2, class Period2>\nconstexpr auto operator+(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);", "2 つの `duration` を足します。単位が違うときは、細かいほうの単位にそろえて計算します（`1s + 500ms` は `1500ms`）。", "定数"),
    ("operator-", "template <class Rep1, class Period1, class Rep2, class Period2>\nconstexpr auto operator-(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);", "2 つの `duration` を引きます。単位が違うときは、細かいほうの単位にそろえます。", "定数"),
    ("operator*", "template <class Rep1, class Period, class Rep2>\nconstexpr auto operator*(const duration<Rep1, Period>& d, const Rep2& s);", "`duration` を整数や小数倍します。`16ms * 3` は `48ms` です。", "定数"),
    ("operator/", "template <class Rep1, class Period, class Rep2>\nconstexpr auto operator/(const duration<Rep1, Period>& d, const Rep2& s);\ntemplate <class Rep1, class Period1, class Rep2, class Period2>\nconstexpr auto operator/(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);", "`duration` を数で割ると `duration`、`duration` どうしを割ると**数**（比率）が返ります。`1s / 16ms` は `62`（整数）です。", "定数"),
    ("operator%", "template <class Rep1, class Period, class Rep2>\nconstexpr auto operator%(const duration<Rep1, Period>& d, const Rep2& s);", "余りを求めます。周期的な時間の計算（`t % 1s`）に使います。", "定数"),
    ("operator+=", "constexpr duration& operator+=(const duration& d);", "自分に足します。", "定数"),
    ("operator-=", "constexpr duration& operator-=(const duration& d);", "自分から引きます。", "定数"),
    ("operator==", "template <class Rep1, class Period1, class Rep2, class Period2>\nconstexpr bool operator==(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);", "単位が違っても、同じ長さなら `true`（`1s == 1000ms`）。", "定数"),
    ("operator<=>", "template <class Rep1, class Period1, class Rep2, class Period2>\nconstexpr auto operator<=>(const duration<Rep1, Period1>& lhs, const duration<Rep2, Period2>& rhs);", "長さを比べる三方比較（C++20）。単位が違っても比べられます。", "定数"),
]:
    S(DU, n, sg, d, cx)
TP = "utilities/chrono/time_point.md"
M[TP] = "min max operator+ operator- operator+= operator-= operator== operator<=>"
for n, sg, d, cx in [
    ("min", "static constexpr time_point min() noexcept;", "表せる最も早い時点。", "定数"),
    ("max", "static constexpr time_point max() noexcept;", "表せる最も遅い時点。", "定数"),
    ("operator+", "constexpr time_point operator+(const time_point& tp, const duration& d);", "時点に `duration` を足して、あとの時点を作ります。", "定数"),
    ("operator-", "constexpr time_point operator-(const time_point& tp, const duration& d);\nconstexpr auto operator-(const time_point& lhs, const time_point& rhs);", "時点から `duration` を引く、または 2 つの時点の差（`duration`）を求めます。経過時間の計算に使います。", "定数"),
    ("operator+=", "constexpr time_point& operator+=(const duration& d);", "自分の時点を、`d` だけ進めます。", "定数"),
    ("operator-=", "constexpr time_point& operator-=(const duration& d);", "自分の時点を、`d` だけ戻します。", "定数"),
    ("operator==", "constexpr bool operator==(const time_point& lhs, const time_point& rhs);", "同じ時点なら `true`。", "定数"),
    ("operator<=>", "constexpr auto operator<=>(const time_point& lhs, const time_point& rhs);", "時点の先後を比べる三方比較（C++20）。", "定数"),
]:
    S(TP, n, sg, d, cx)
for pg, nm in [("utilities/chrono/system_clock.md", "system_clock"), ("utilities/chrono/steady_clock.md", "steady_clock"), ("utilities/chrono/high_resolution_clock.md", "high_resolution_clock")]:
    M[pg] = "now is_steady" + (" to_time_t from_time_t" if nm == "system_clock" else "")
    S(pg, "now", f"static time_point {nm}::now() noexcept;", "今の時点を返します。" + ("巻き戻らない時計なので、経過時間の計測に向いています。" if nm == "steady_clock" else "現実の日時の時計なので、時刻合わせで巻き戻ることがあります。" if nm == "system_clock" else "利用できる最も細かい時計です。"), "定数")
    S(pg, "is_steady", "static constexpr bool is_steady;", "巻き戻らず、一定の速さで進む時計なら `true`。" + ("`steady_clock` は常に `true` です。" if nm == "steady_clock" else "`system_clock` は `false` です。" if nm == "system_clock" else "実装によって違います。"), "コンパイル時")
S("utilities/chrono/system_clock.md", "to_time_t", "static std::time_t system_clock::to_time_t(const time_point& t) noexcept;", "`time_point` を C の `time_t`（秒単位）に変換します。`std::ctime`・`localtime` など、C の関数に渡すときに使います。", "定数")
S("utilities/chrono/system_clock.md", "from_time_t", "static time_point system_clock::from_time_t(std::time_t t) noexcept;", "C の `time_t` を `time_point` に変換します。", "定数")

# ---- random
RN = "utilities/random/"
ENG = ["mt19937", "minstd_rand", "knuth_b", "ranlux24", "default_random_engine", "mt19937_64", "minstd_rand0", "ranlux24_base", "ranlux48_base", "ranlux48"]
for e in ENG:
    pg = RN + e + ".md"
    if (Path(members.STL) / pg).exists():
        M[pg] = "operator() seed discard min max operator=="
        S(pg, "operator()", "result_type operator()();", "次の乱数を返します。呼ぶたびに内部の状態が進みます。", "定数")
        S(pg, "seed", "void seed(result_type value = default_seed);\ntemplate <class SeedSeq> void seed(SeedSeq& seq);", "内部の状態を、シードで初期化し直します。同じシードなら、同じ乱数の並びになります。", "O(状態の大きさ)")
        S(pg, "discard", "void discard(unsigned long long z);", "乱数を `z` 個ぶん、捨てて進めます。並びの途中から使いたいとき（セーブした位置から再開するなど）に使います。", "O(z)")
        S(pg, "min", "static constexpr result_type min();", "`operator()` が返しうる最小値。", "定数")
        S(pg, "max", "static constexpr result_type max();", "`operator()` が返しうる最大値。", "定数")
        S(pg, "operator==", "friend bool operator==(const " + e + "& a, const " + e + "& b);", "2 つのエンジンの内部状態が同じなら `true`（同じ並びを出す）。", "O(状態の大きさ)")
M[RN + "random_device.md"] = "operator() entropy min max"
S(RN + "random_device.md", "operator()", "result_type operator()();", "非決定的な乱数（ハードウェアや OS のエントロピー源）を 1 つ返します。シード用に使います。実装によっては遅い、あるいは決定的になる環境もあります。", "OS に依存")
S(RN + "random_device.md", "entropy", "double entropy() const noexcept;", "乱数源のエントロピーの見積もり（ビット数）。決定的な実装では 0 を返します。当てにならないことが多いです。", "定数")
S(RN + "random_device.md", "min", "static constexpr result_type min();", "`operator()` が返しうる最小値。", "定数")
S(RN + "random_device.md", "max", "static constexpr result_type max();", "`operator()` が返しうる最大値。", "定数")
DISTS = ["uniform_int_distribution", "uniform_real_distribution", "bernoulli_distribution", "binomial_distribution", "negative_binomial_distribution", "geometric_distribution", "poisson_distribution", "exponential_distribution", "gamma_distribution",
         "weibull_distribution", "extreme_value_distribution", "normal_distribution", "lognormal_distribution", "chi_squared_distribution", "cauchy_distribution", "fisher_f_distribution", "student_t_distribution", "discrete_distribution",
         "piecewise_constant_distribution", "piecewise_linear_distribution"]
for dn in DISTS:
    pg = RN + dn + ".md"
    if (Path(members.STL) / pg).exists():
        M[pg] = "operator() reset param min max"
        S(pg, "operator()", "template <class Generator>\nresult_type operator()(Generator& g);", "乱数エンジン `g` から乱数を取って、この分布に従う値を 1 つ返します。", "定数（アルゴリズムによる）")
        S(pg, "reset", "void reset();", "分布の内部状態を初期化します。直前の呼び出しで持ち越している値（正規分布の「余り」の値）を捨てます。", "定数")
        S(pg, "param", "param_type param() const;\nvoid param(const param_type& p);", "分布のパラメータ一式を取り出す、または設定します。", "定数")
        S(pg, "min", "result_type min() const;", "この分布が返しうる最小値。", "定数")
        S(pg, "max", "result_type max() const;", "この分布が返しうる最大値。", "定数")

# ---- regex / smatch / locale / error_code など
M["io/regex.md"] = "assign flags mark_count imbue getloc swap operator="
for n, sg, d, cx in [
    ("assign", "basic_regex& assign(const std::string& s, flag_type f = ECMAScript);", "新しいパターンを設定します（コンパイルし直します）。", "O(パターンの長さ)"),
    ("flags", "flag_type flags() const;", "構文のオプション（`icase` など）。", "定数"),
    ("mark_count", "unsigned mark_count() const;", "パターンの中のグループ（括弧）の数。", "定数"),
    ("imbue", "locale_type imbue(locale_type loc);", "正規表現が使うロケールを設定します。パターンは破棄されます。", "定数"),
    ("getloc", "locale_type getloc() const;", "正規表現が使うロケール。", "定数"),
    ("swap", "void swap(basic_regex& other) noexcept;", "2 つの正規表現を入れ替えます。", "定数"),
    ("operator=", "basic_regex& operator=(const basic_regex& rhs);\nbasic_regex& operator=(const std::string& s);", "別の正規表現、または文字列のパターンを代入します。", "O(パターンの長さ)"),
]:
    S("io/regex.md", n, sg, d, cx)
M["io/smatch.md"] = "size empty length position str operator[] prefix suffix begin end format ready swap max_size"
for n, sg, d, cx in [
    ("size", "size_type size() const noexcept;", "グループの数（全体の一致 `m[0]` を含む）。一致がなければ 0。", "定数"),
    ("empty", "bool empty() const noexcept;", "一致の結果がなければ `true`。", "定数"),
    ("length", "difference_type length(size_type n = 0) const;", "n 番目のグループの長さ。", "定数"),
    ("position", "difference_type position(size_type n = 0) const;", "n 番目のグループが、元の文字列の何文字目から始まるか。", "定数"),
    ("str", "string_type str(size_type n = 0) const;", "n 番目のグループを `std::string` で返します。", "O(長さ)"),
    ("operator[]", "const_reference operator[](size_type n) const;", "n 番目のグループ（`sub_match`）。`m[0]` は一致した全体、`m[1]` 以降が括弧のグループです。", "定数"),
    ("prefix", "const_reference prefix() const;", "一致した部分の**前**の文字列。", "定数"),
    ("suffix", "const_reference suffix() const;", "一致した部分の**後ろ**の文字列。", "定数"),
    ("begin", "const_iterator begin() const noexcept;", "グループ（`sub_match`）の先頭。", "定数"),
    ("end", "const_iterator end() const noexcept;", "グループ（`sub_match`）の終端。", "定数"),
    ("format", "string_type format(const string_type& fmt) const;", "`$1` や `$&` を含む書式文字列に、一致の結果を埋め込んだ文字列を返します。", "O(長さ)"),
    ("ready", "bool ready() const noexcept;", "一致の結果が設定済みなら `true`。", "定数"),
    ("swap", "void swap(match_results& other) noexcept;", "2 つの結果を入れ替えます。", "定数"),
    ("max_size", "size_type max_size() const noexcept;", "保持できるグループの最大数。", "定数"),
]:
    S("io/smatch.md", n, sg, d, cx)
M["io/locale.md"] = "name classic global combine operator() operator== operator!="
for n, sg, d, cx in [
    ("name", "std::string name() const;", "ロケールの名前（`\"C\"`・`\"ja_JP.UTF-8\"` など）。名前のないロケールは `\"*\"`。", "定数"),
    ("classic", "static const locale& classic();", "クラシックロケール（`\"C\"` ロケール）への参照。言語に依存しない、標準の振る舞いです。", "定数"),
    ("global", "static locale global(const locale& loc);", "プログラム全体の既定のロケールを設定し、それまでのロケールを返します。これ以降に作るストリームは、このロケールを使います。", "定数"),
    ("combine", "template <class Facet>\nlocale combine(const locale& other) const;", "ほかのロケールから、`Facet`（部品）だけを取り込んだ、新しいロケールを作ります。", "定数"),
    ("operator()", "template <class CharT, class Traits, class Alloc>\nbool operator()(const std::basic_string<CharT, Traits, Alloc>& s1, const std::basic_string<CharT, Traits, Alloc>& s2) const;", "ロケールの照合順（`collate`）で、2 つの文字列を比べます。`std::sort(v.begin(), v.end(), std::locale(\"ja_JP\"))` のように、比較関数として渡せます。", "O(長さ)"),
    ("operator==", "bool operator==(const locale& other) const;", "同じロケールなら `true`。", "定数"),
    ("operator!=", "bool operator!=(const locale& other) const;", "違うロケールなら `true`（C++20 では `==` から自動で導かれる）。", "定数"),
]:
    S("io/locale.md", n, sg, d, cx)
M["support/error_code.md"] = "value category message clear assign operator_bool default_error_condition operator= operator== operator<=>"
for n, sg, d, cx in [
    ("value", "int value() const noexcept;", "エラーの番号。意味は、`category()` が決めます。", "定数"),
    ("category", "const error_category& category() const noexcept;", "エラーの種類（`generic_category`・`system_category` など）。", "定数"),
    ("message", "std::string message() const;", "エラーの説明の文字列（`category().message(value())`）。ログに出すのに使います。", "定数"),
    ("clear", "void clear() noexcept;", "エラーなし（値 0、システムのカテゴリ）に戻します。", "定数"),
    ("assign", "void assign(int val, const error_category& cat) noexcept;", "エラーの番号とカテゴリを設定します。", "定数"),
    ("default_error_condition", "error_condition default_error_condition() const noexcept;", "OS に依存しない形の `error_condition` に変換します。`==` で `errc` と比べられるのは、これのおかげです。", "定数"),
    ("operator=", "error_code& operator=(ErrorCodeEnum e) noexcept;", "`errc` などの列挙値から代入します。", "定数"),
    ("operator==", "bool operator==(const error_code& lhs, const error_code& rhs) noexcept;\nbool operator==(const error_code& code, const error_condition& cond) noexcept;", "`error_code` どうし、または `error_condition` と比べます。`ec == std::errc::no_such_file_or_directory` のように使います。", "定数"),
    ("operator<=>", "std::strong_ordering operator<=>(const error_code& lhs, const error_code& rhs) noexcept;", "カテゴリ、番号の順で比べる三方比較（C++20）。", "定数"),
]:
    S("support/error_code.md", n, sg, d, cx)
SPEC[("support/error_code.md", "operator_bool")] = ("explicit operator bool() const noexcept;", "エラーがあれば（`value() != 0`）`true`。`if (ec) { ... }` と書けます。", "定数")
M["memory/pmr/polymorphic_allocator.md"] = "allocate deallocate allocate_bytes deallocate_bytes allocate_object deallocate_object new_object delete_object construct resource select_on_container_copy_construction"
for n, sg, d, cx in [
    ("allocate", "T* allocate(std::size_t n);", "`T` を `n` 個ぶんのメモリを、内部のメモリリソースから確保します。", "リソースによる"),
    ("deallocate", "void deallocate(T* p, std::size_t n);", "`allocate` で確保したメモリを返します。", "リソースによる"),
    ("allocate_bytes", "void* allocate_bytes(std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t));", "バイト数と境界を指定して、生のメモリを確保します。", "リソースによる"),
    ("deallocate_bytes", "void deallocate_bytes(void* p, std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t));", "`allocate_bytes` で確保したメモリを返します。", "リソースによる"),
    ("allocate_object", "template <class U>\nU* allocate_object(std::size_t n = 1);", "型 `U` を `n` 個ぶんのメモリを確保します（オブジェクトは作りません）。", "リソースによる"),
    ("deallocate_object", "template <class U>\nvoid deallocate_object(U* p, std::size_t n = 1);", "`allocate_object` で確保したメモリを返します。", "リソースによる"),
    ("new_object", "template <class U, class... Args>\nU* new_object(Args&&... args);", "メモリを確保して、そこにオブジェクトを作ります。`new` のメモリリソース版です。", "リソースによる + 構築"),
    ("delete_object", "template <class U>\nvoid delete_object(U* p);", "オブジェクトを破棄して、メモリを返します。`new_object` と対にします。", "リソースによる + 破棄"),
    ("construct", "template <class U, class... Args>\nvoid construct(U* p, Args&&... args);", "`p` の場所に、オブジェクトを作ります。内部のメモリリソースを、要素にも引き継ぎます（uses-allocator 構築）。", "構築による"),
    ("resource", "std::pmr::memory_resource* resource() const;", "このアロケータが使っているメモリリソース。", "定数"),
    ("select_on_container_copy_construction", "polymorphic_allocator select_on_container_copy_construction() const;", "コンテナをコピーするとき、コピー先が使うアロケータを返します。pmr では、既定のメモリリソースを使うアロケータです（元のリソースは引き継がれません）。", "定数"),
]:
    S("memory/pmr/polymorphic_allocator.md", n, sg, d, cx)
M["memory/pmr/memory_resource.md"] = "allocate deallocate is_equal"
S("memory/pmr/memory_resource.md", "allocate", "void* allocate(std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));", "`bytes` バイトのメモリを確保します。内部で、派生クラスの `do_allocate` を呼びます。失敗すると例外を投げます。", "リソースによる")
S("memory/pmr/memory_resource.md", "deallocate", "void deallocate(void* p, std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));", "`allocate` で確保したメモリを返します。内部で、派生クラスの `do_deallocate` を呼びます。", "リソースによる")
S("memory/pmr/memory_resource.md", "is_equal", "bool is_equal(const memory_resource& other) const noexcept;", "2 つのリソースが、互いのメモリを解放できる（同じ）ものなら `true`。", "定数")
M["utilities/bad_expected_access.md"] = "error what"
S("utilities/bad_expected_access.md", "error", "E& error() & noexcept;\nconst E& error() const& noexcept;", "`expected` が持っていたエラーの値への参照。`value()` が失敗したときに、原因を取り出せます。", "定数")
S("utilities/bad_expected_access.md", "what", "const char* what() const noexcept override;", "エラーを表す文字列（実装定義）。", "定数")
M["utilities/tuple.md"] = "swap operator= operator== operator<=>"
for n, sg, d, cx in [
    ("swap", "void swap(tuple& other);", "2 つのタプルの要素を、1 つずつ入れ替えます。", "要素数に比例"),
    ("operator=", "tuple& operator=(const tuple& other);\ntuple& operator=(tuple&& other);", "要素ごとに代入します。`pair` や、型が変換できるタプルからも代入できます。", "要素数に比例"),
    ("operator==", "template <class... T, class... U>\nbool operator==(const tuple<T...>& lhs, const tuple<U...>& rhs);", "全ての要素が順に等しければ `true`。", "要素数に比例"),
    ("operator<=>", "template <class... T, class... U>\nauto operator<=>(const tuple<T...>& lhs, const tuple<U...>& rhs);", "要素を先頭から順に比べる、辞書順の三方比較（C++20）。", "要素数に比例"),
]:
    S("utilities/tuple.md", n, sg, d, cx)

if __name__ == "__main__":
    run(sys.argv[1:])
