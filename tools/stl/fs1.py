"""filesystem の薄いページを書き直す（バッチ 1）。"""
from rw import rewrite

F = 'stl/io/filesystem/'

rewrite(F + 'equivalent.md',
  intro="""ゲームのアセット管理で、`Data/hero.png` と `./Data/../Data/hero.png` と `C:\\Game\\Data\\hero.png` が、実は同じファイルだった、ということが起きます。文字列で比べると全部別のものに見えるので、同じ画像を 3 回読み込んでしまいます。

`std::filesystem::equivalent` は、<strong>パスの文字列ではなく、指している実体</strong>が同じかどうかを調べます。ファイルシステムに問い合わせるので、相対パスでも、`..` を含んでいても、リンク経由でも、同じものなら `true` が返ります。""",
  tips=["比べるのは文字列ではなく、ファイルシステム上の実体。表記の違いに左右されない",
        "両方のパスが存在している必要がある。存在しないパスを渡すと、例外（または `error_code`）になる",
        "文字列だけで比べたいなら `path::operator==`。ファイルシステムに問い合わせないので軽い",
        "シンボリックリンクとその指し先は、同じ実体として `true` になる"],
  details="""### equivalent {#equivalent}

<span class="ver ver-17">C++17</span>

```cpp
bool equivalent(const path& p1, const path& p2);
bool equivalent(const path& p1, const path& p2, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p1`, `p2` | `const path&` | 比べる 2 つのパス。文字列から暗黙に変換できる |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先。渡すと例外を投げない |

内部では、両方のパスについてファイルのボリュームと識別番号（Windows ではボリューム シリアル番号とファイル インデックス、POSIX では `st_dev` と `st_ino`）を取り出して比べています。パスの文字列の組み立てを見ているわけではないので、`.` や `..` の扱いを自分で考える必要はありません。

戻り値は、同じ実体なら `true`、別の実体なら `false` です。ここで間違えやすいのは、<strong>両方が存在しないときは `false` ではなくエラー</strong>になることです。片方だけが存在しないときは `false` が返ります。「存在しない 2 つのパスは、どちらも同じ『無』だから等しい」とは扱われません。例外を避けたいときは `error_code` を受け取る版を使い、`ec` を見て判断します。

ハード リンクで同じ実体に 2 つの名前を付けたときも、`true` になります。名前が違っても、ディスク上の実体が 1 つなら同じ物として扱う、という考え方です。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("a.txt") << "x";
  std::ofstream("b.txt") << "y";

  // 表記が違っても、同じファイルなら true
  std::println("a.txt と ./a.txt: {}", fs::equivalent("a.txt", "./a.txt"));
  std::println("a.txt と 絶対パス: {}", fs::equivalent("a.txt", fs::absolute("a.txt")));
  std::println("a.txt と b.txt: {}", fs::equivalent("a.txt", "b.txt"));

  // 両方が存在しないときは、エラーになる
  std::error_code ec;
  bool r = fs::equivalent("none1.txt", "none2.txt", ec);
  std::println("両方なし: 結果={} エラー={}", r, static_cast<bool>(ec));
}""",
  out="""a.txt と ./a.txt: true
a.txt と 絶対パス: true
a.txt と b.txt: false
両方なし: 結果=false エラー=true""",
  uses="""アセットの二重読み込みを防ぐときに使います。読み込み済みのファイルの一覧に新しいパスを足す前に、すでにある物と `equivalent` で比べれば、表記の違いで重複することがありません。

ただし、比べるたびにファイルシステムへ問い合わせるので、数千のアセットと総当たりで比べると遅くなります。普通は、`canonical` で正規化したパスの文字列をキーにして `unordered_set` に入れるほうが速く、`equivalent` は「怪しいときの最終確認」に使います。

セーブ データの保存先と、読み込み元が同じファイルかどうかを確かめて、上書きの警告を出す場面にも向いています。""",
  mistakes=[("存在しないパスを渡して、例外で落ちる", """ファイルを作る前や消した後に比べると、`std::filesystem::filesystem_error` が投げられます。先に `exists` で確かめるか、`error_code` を受け取る版を使います。"""),
            ("文字列が同じだから、同じファイルだと思い込む", """相対パスは、実行中のカレント ディレクトリに依存します。`"a.txt"` という同じ文字列でも、別のカレント ディレクトリなら別のファイルです。`equivalent` は、その時点で解決される実体を比べます。""")],
  similar=[("[`canonical`](canonical.md)", "パスを正規化して返す。比べる前の下ごしらえに使う"),
           ("`path::operator==`", "文字列として比べるだけ。ファイルシステムに問い合わせない")],
  memo=["実体が同じかを調べる", "表記が違ってもよい", "両方の存在が必要（なければエラー）"])

rewrite(F + 'space.md',
  intro="""セーブ データを書き込む前に、ディスクの空きが足りるか確かめたい。ダウンロードしたアセットを展開する前に、容量を調べたい。書き込みの途中でディスクが一杯になると、壊れたセーブ ファイルが残ってしまうからです。

`std::filesystem::space` は、パスが乗っているボリューム（ドライブやパーティション）の<strong>全体の容量、空き容量、現在のユーザーが使える空き容量</strong>を、`space_info` として返します。""",
  tips=["パスに指定するのは、調べたいボリューム上の既存のパス。ファイルでもフォルダーでもよい",
        "返る `space_info` は、`capacity`（全体）、`free`（空き）、`available`（使える空き）の 3 つ",
        "ユーザーごとの容量制限（クォータ）があると、`available` は `free` より小さくなる",
        "調べた後に書き込むまでの間に、空きは変わりうる。結果は目安で、保証ではない"],
  details="""### space {#space}

<span class="ver ver-17">C++17</span>

```cpp
space_info space(const path& p);
space_info space(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べたいボリューム上に実在するパス。そのボリュームのルート（`C:\\` など）でも、中のファイルでもよい |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先。渡すと例外を投げない |

戻り値の [`space_info`](space_info.md) は、バイト数を `std::uintmax_t` で持つ 3 つのメンバーです。`capacity` はボリュームの総容量、`free` は空きの合計、`available` は<strong>今のプロセスが使える</strong>空きです。ふつうのデスクトップの単独ユーザーでは、`free` と `available` はほぼ同じ値になります。

保存前の判定には、`free` ではなく `available` を使います。サーバーや共有マシンのように、ユーザーごとに容量制限が掛かる環境では、`free` が十分あっても、書き込めないことがあるからです。

パスが存在しないときは、例外（または `ec` のエラー）になります。ネットワーク ドライブなど、情報を取れないボリュームでは、各メンバーが `static_cast<std::uintmax_t>(-1)` になることがあります。この値は「不明」を表すので、そのまま「とても大きい空き」と受け取らないでください。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::space_info info = fs::space(fs::current_path());

  // 値はマシンごとに違うので、関係だけを確かめる
  std::println("全体 >= 空き: {}", info.capacity >= info.free);
  std::println("空き >= 使える空き: {}", info.free >= info.available);

  // 100 MB 以上の空きがあれば保存してよい、という判定
  const std::uintmax_t need = 100ull * 1024 * 1024;
  std::println("保存してよい: {}", info.available >= need);
}""",
  out="""全体 >= 空き: true
空き >= 使える空き: true
保存してよい: true""",
  uses="""大きなセーブ データやスクリーンショットを保存する前に、`available` が必要な量より大きいかを確かめ、足りなければ「ディスクの空きが足りません」とプレイヤーに知らせます。何も言わずに書き込みを失敗させるより、ずっと親切です。

ダウンロード コンテンツの展開や、シェーダー キャッシュの作成の前にも使えます。必要量は、展開後の合計サイズに余裕（1 割程度）を足しておきます。

ただし、確認してから書き込むまでの間に、他のプログラムが容量を使うことがあります。この判定は「ほぼ大丈夫」の確認で、書き込み自体の失敗は、別に処理する必要があります。""",
  mistakes=[("`free` を見て保存したのに、容量制限で失敗した", "`free` はボリューム全体の空きです。現在のユーザーが使える量は `available` なので、保存可否の判定にはこちらを使います。"),
            ("存在しないフォルダーを渡して例外になる", "保存先のフォルダーを先に作ってから調べるか、存在する親フォルダーを渡します。ボリュームが同じなら、結果は同じです。")],
  similar=[("[`space_info`](space_info.md)", "この関数が返す構造体。3 つのメンバーの意味はこちら"),
           ("[`file_size`](file_size.md)", "ファイル 1 つの大きさ。ボリュームの容量ではない")],
  memo=["ボリュームの容量と空きを調べる", "保存の判定には `available` を使う", "調べた後に変わりうる"])

rewrite(F + 'space_info.md',
  intro="""ディスクの空きを調べると、「全体で何バイト」「空きは何バイト」「自分が使えるのは何バイト」の 3 つの数字が欲しくなります。`std::filesystem::space_info` は、この 3 つをまとめて持つ小さな構造体です。[`space`](space.md) の戻り値として受け取ります。""",
  tips=["メンバーは `capacity`、`free`、`available` の 3 つ。どれも `std::uintmax_t` のバイト数",
        "自分で作ることはほとんどない。`space` が返す値を読むための型",
        "`capacity >= free >= available` が成り立つのがふつう",
        "値が `static_cast<std::uintmax_t>(-1)` のときは、取得できなかったという意味"],
  details="""### space_info {#space_info}

<span class="ver ver-17">C++17</span>

```cpp
struct space_info {
  std::uintmax_t capacity;
  std::uintmax_t free;
  std::uintmax_t available;
};
```

| メンバー | 意味 |
| --- | --- |
| `capacity` | ボリュームの総容量（バイト） |
| `free` | ボリューム全体の空き（バイト） |
| `available` | 現在のプロセスが使える空き（バイト） |

`capacity` は、ボリュームの大きさです。500 GB の SSD なら、パーティションの大きさに近い値になります。`free` は、使われていない領域の合計で、管理者だけが使える予約領域も含みます。

`available` が実際に書き込める量です。ユーザーごとの容量制限があるときや、ファイルシステムが一部を予約しているときは、`free` より小さくなります。ゲームの保存判定は、この値で行います。

3 つとも<strong>バイト単位の符号なし整数</strong>なので、引き算で「使用中の量」を求めるときは、`capacity - free` の順に書きます。逆にすると、符号なしの引き算で巨大な値になります。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::space_info info = fs::space(".");

  // 使用中の量は、capacity から free を引いて求める
  std::uintmax_t used = info.capacity - info.free;
  std::println("使用中 + 空き == 全体: {}", used + info.free == info.capacity);

  // 単位を GiB に直して表示する形（値はマシンによる）
  double gib = static_cast<double>(info.available) / (1024.0 * 1024.0 * 1024.0);
  std::println("使える空きが 0 GiB より大きい: {}", gib > 0.0);
}""",
  out="""使用中 + 空き == 全体: true
使える空きが 0 GiB より大きい: true""",
  uses="""設定画面や起動時のログに、ディスクの空きを表示するときに使います。バイト数のままでは読みにくいので、GiB や MiB に直して、小数 1 桁ほどで出します。

セーブ前の容量チェックでは、`available` を見ます。「使用中の量」を出したい（キャッシュ フォルダーの上限を、ボリュームの何割までにするか決めたい）ときは、`capacity - free` を使います。""",
  mistakes=[("符号なしの引き算で、巨大な値になる", "`info.free - info.capacity` のように大きいほうを後ろに書くと、マイナスにならず、2 の 64 乗に近い値になります。引く順番を確かめます。"),
            ("取得できなかった値を、そのまま容量として使う", "ネットワーク ドライブなどでは、`-1` を `uintmax_t` にした最大値が入ることがあります。`available` が `static_cast<std::uintmax_t>(-1)` のときは、「不明」として扱います。")],
  similar=[("[`space`](space.md)", "この構造体を返す関数")],
  memo=["`capacity`、`free`、`available` の 3 つ", "保存の判定は `available`", "全部バイト単位の符号なし整数"])

rewrite(F + 'status.md',
  intro="""パスがファイルなのかフォルダーなのか、読み取り専用なのか、それとも存在しないのか。ファイルを開く前に知りたい情報は、いくつもあります。`exists` や `is_directory` を順に呼ぶと、そのたびにファイルシステムへ問い合わせます。

`std::filesystem::status` は、<strong>1 回の問い合わせで、種類（`type`）と権限（`permissions`）をまとめて</strong>取り出して、[`file_status`](file_status.md) として返します。`exists` や `is_regular_file` も、中身はこの関数です。""",
  tips=["戻り値の `file_status` から `type()` と `permissions()` を読む",
        "パスがシンボリックリンクなら、指し先の情報を返す。リンク自体を調べるなら `symlink_status`",
        "パスが存在しなくても、例外にはならない。`type()` が `not_found` になる",
        "判定をいくつも書くより、`status` を 1 回呼んで使い回すほうが、問い合わせが減る"],
  details="""### status {#status}

<span class="ver ver-17">C++17</span>

```cpp
file_status status(const path& p);
file_status status(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は [`file_status`](file_status.md) です。`type()` で `regular`（ふつうのファイル）、`directory`、`symlink` などの種類が、`permissions()` で読み書きの権限が分かります。

パスが存在しないときの扱いが、他の関数と違います。<strong>存在しないこと自体はエラーではなく</strong>、`type()` が `file_type::not_found` の `file_status` が返ります。例外を投げるのは、権限がなくて調べられない、パスの形式が不正、といった本当の失敗のときだけです。このため、「存在するかどうか」を例外なしで判定できます。

シンボリックリンクは、たどった先の情報を返します。リンク自体の情報が欲しいときは、[`symlink_status`](symlink_status.md) を使います。

`exists(p)`、`is_directory(p)` などは、`status(p)` の結果を調べる補助関数です。複数の種類を続けて調べるなら、`status` を一度だけ呼んで、その結果に `fs::is_directory(st)` のように渡すほうが、問い合わせの回数が減ります。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("save.dat") << "data";
  fs::create_directory("saves");

  // 1 回だけ status を呼んで、結果を使い回す
  fs::file_status st = fs::status("save.dat");
  std::println("save.dat は通常のファイル: {}", fs::is_regular_file(st));
  std::println("save.dat はフォルダー: {}", fs::is_directory(st));

  std::println("saves はフォルダー: {}", fs::is_directory(fs::status("saves")));

  // 存在しなくても例外にならない
  fs::file_status none = fs::status("missing.dat");
  std::println("missing.dat は not_found: {}", none.type() == fs::file_type::not_found);
  std::println("missing.dat は存在する: {}", fs::exists(none));
}""",
  out="""save.dat は通常のファイル: true
save.dat はフォルダー: false
saves はフォルダー: true
missing.dat は not_found: true
missing.dat は存在する: false""",
  uses="""ファイルの読み込み前の検査に使います。設定ファイルが「ふつうのファイルとして存在するか」を確かめてから開き、なければ既定の設定を使う、という流れです。ファイルのつもりでフォルダーを開こうとして失敗する、という事故も、種類を見れば防げます。

フォルダーを走査するときは、[`directory_entry`](directory_entry.md) が情報をキャッシュしているので、毎回 `status` を呼ぶより、そちらを使うほうが軽くなります。""",
  mistakes=[("リンクの指し先ではなく、リンクそのものを調べたかった", "`status` はリンクをたどります。リンク自体の種類（`symlink`）を知りたいときは、`symlink_status` を使います。"),
            ("存在しないパスで、例外が出ると思って try を書く", "存在しないだけなら例外は出ません。`type()` が `not_found` になるので、`exists` で判定できます。")],
  similar=[("[`symlink_status`](symlink_status.md)", "リンクをたどらずに、リンク自体を調べる"),
           ("[`exists`](exists.md)", "`status` の結果が not_found でないかの補助関数"),
           ("[`file_status`](file_status.md)", "この関数が返す型")],
  memo=["種類と権限をまとめて取る", "存在しなくても例外にならない", "リンクはたどる（`symlink_status` はたどらない）"])

rewrite(F + 'temp_directory_path.md',
  intro="""ダウンロードしたファイルを一時的に置きたい。圧縮ファイルを展開する作業場所が欲しい。クラッシュ レポートを書き出したい。こうした「あとで消えてよいファイル」の置き場は、アプリが勝手にフォルダーを決めるより、OS が用意している一時フォルダーを使うのが作法です。

`std::filesystem::temp_directory_path` は、<strong>その OS の一時フォルダーのパス</strong>を返します。Windows では `C:\\Users\\<名前>\\AppData\\Local\\Temp`、Linux では `/tmp` です。""",
  tips=["戻り値は、OS が決めた一時フォルダーの絶対パス。実在するフォルダーを指す",
        "環境変数（Windows は `TMP`、`TEMP` など、POSIX は `TMPDIR` など）で場所が変わる",
        "フォルダー自体は共有されている。ファイル名がぶつからないよう、自分用のサブフォルダーを作って使う",
        "ここに置いたファイルは、自動で消えるとは限らない。使い終わったら、自分で消す"],
  details="""### temp_directory_path {#temp_directory_path}

<span class="ver ver-17">C++17</span>

```cpp
path temp_directory_path();
path temp_directory_path(std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先。渡すと例外を投げない |

引数なしの版は、失敗すると `filesystem_error` を投げます。`ec` を渡す版は、失敗したときに空のパスを返し、`ec` にエラーを入れます。

返されるパスは、実在するフォルダーです。ただし、<strong>誰でも書ける共有の場所</strong>なので、`temp_directory_path() / "save.tmp"` のような決まった名前を使うと、他のプログラムや、同じゲームの別のプロセスと衝突します。自分専用のサブフォルダー（`temp_directory_path() / "MyGame"` など）を作り、その中に置くのが基本です。

名前がぶつからない一時ファイル名が欲しいときは、プロセス番号や乱数、時刻を名前に混ぜます。C++ の標準には、一時ファイルの名前を作る関数がないので、自分で組み立てます。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::path tmp = fs::temp_directory_path();

  std::println("空ではない: {}", !tmp.empty());
  std::println("実在するフォルダー: {}", fs::is_directory(tmp));
  std::println("絶対パス: {}", tmp.is_absolute());

  // 自分専用のサブフォルダーを作って使う
  fs::path work = tmp / "MyGameWork";
  fs::create_directories(work);
  std::println("作業フォルダーを作れた: {}", fs::is_directory(work));
  fs::remove_all(work);   // 使い終わったら消す
}""",
  out="""空ではない: true
実在するフォルダー: true
絶対パス: true
作業フォルダーを作れた: true""",
  uses="""ダウンロードしたパッチの一時保存、圧縮ファイルの展開、クラッシュ ダンプの書き出しなど、<strong>消えても困らないデータ</strong>の置き場所に使います。

セーブ データや設定のように、残したいものを置いてはいけません。OS やクリーナー ソフトが、一時フォルダーを掃除することがあるからです。残したい物は、ユーザー データ用のフォルダー（Windows なら `%APPDATA%` や `Saved Games`）に置きます。""",
  mistakes=[("決まった名前のファイルを直接置いて、他のプロセスとぶつかる", "`temp / \"work.tmp\"` のような名前は、複数起動で上書きし合います。プロセス番号や乱数を混ぜるか、自分用のサブフォルダーを作ります。"),
            ("置いたファイルを消さず、一時フォルダーがゲームのデータで一杯になる", "OS は自動で消すとは限りません。終了時に `remove_all` で片付けます。クラッシュに備えて、起動時に古い作業フォルダーを消す処理も入れておくと安心です。")],
  similar=[("[`current_path`](current_path.md)", "カレント ディレクトリ。一時フォルダーではない"),
           ("[`create_directories`](create_directories.md)", "サブフォルダーを作る")],
  memo=["OS の一時フォルダーを返す", "共有の場所なので、サブフォルダーを作って使う", "使い終わったら消す"])

rewrite(F + 'resize_file.md',
  intro="""ログ ファイルを一定の大きさで切り詰めたい。ダウンロード用に、最終的な大きさのファイルを先に確保しておきたい。ファイルを開いて、書き込んで、閉じる、という手順を踏まずに、<strong>ファイルの大きさだけを変えたい</strong>場面があります。

`std::filesystem::resize_file` は、指定した大きさにファイルを切り詰めるか、伸ばします。伸ばした部分は、0 で埋められます。""",
  tips=["縮めると、末尾が失われる。元に戻せない",
        "伸ばすと、増えた部分は 0 で埋められる",
        "存在しないファイルを渡すと、新しく作らずにエラーになる",
        "ファイルを開いたままのストリームがあるときは、先に閉じる（環境によって失敗する）"],
  details="""### resize_file {#resize_file}

<span class="ver ver-17">C++17</span>

```cpp
void resize_file(const path& p, std::uintmax_t new_size);
void resize_file(const path& p, std::uintmax_t new_size, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 大きさを変えるファイル。ふつうのファイルで、実在している必要がある |
| `new_size` | `std::uintmax_t` | 新しい大きさ（バイト） |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`new_size` が今の大きさより小さければ、後ろが切り捨てられます。大きければ、足りない分が 0 バイトで埋められます。内容の中身を保ったまま大きさを変えるわけではなく、<strong>縮めた部分のデータは戻ってきません</strong>。

戻り値はありません。失敗すると、`filesystem_error` を投げます（`ec` の版では `ec` を見ます）。失敗の典型は、ファイルが存在しない、権限がない、書き込み禁止になっている、といったものです。

ファイルを開いている別のストリームがあると、OS によっては失敗します。Windows では、他のプロセスが開いているファイルの大きさを変えられないことがあります。""",
  code="""#include <filesystem>
#include <fstream>
#include <iterator>
#include <print>
#include <string>

int main() {
  namespace fs = std::filesystem;
  {
    std::ofstream out("log.txt", std::ios::binary);
    out << "0123456789";   // 10 バイト
  }
  std::println("最初: {} バイト", fs::file_size("log.txt"));

  fs::resize_file("log.txt", 4);   // 末尾を切り詰める
  std::println("縮めた後: {} バイト", fs::file_size("log.txt"));

  fs::resize_file("log.txt", 8);   // 伸ばす。増えた部分は 0 で埋まる
  std::println("伸ばした後: {} バイト", fs::file_size("log.txt"));

  std::ifstream in("log.txt", std::ios::binary);
  std::string data((std::istreambuf_iterator<char>(in)), {});
  std::println("先頭 4 文字: {}", data.substr(0, 4));
  std::println("5 バイト目は 0: {}", data[4] == '\\0');
}""",
  out="""最初: 10 バイト
縮めた後: 4 バイト
伸ばした後: 8 バイト
先頭 4 文字: 0123
5 バイト目は 0: true""",
  uses="""ログ ファイルが上限を超えたら、先頭を残して切り詰める、といった単純なローテーションに使えます（古い部分を捨てたいなら、別のファイルに書き出して置き換えるほうが普通です）。

大きなダウンロードでは、受信前に最終サイズでファイルを確保しておくと、途中でディスクが足りなくなる問題に早く気づけます。ただし、確保した部分は 0 で埋まるだけなので、「まだ書いていない」ことを別に管理する必要があります。""",
  mistakes=[("ファイルがなくても、作ってくれると思う", "`resize_file` は新しいファイルを作りません。存在しないと失敗するので、先に空のファイルを作ります。"),
            ("ストリームで開いたまま呼んで失敗する", "`ofstream` を開いたままだと、環境によって失敗します。閉じてから呼びます。")],
  similar=[("[`file_size`](file_size.md)", "ファイルの今の大きさを調べる"),
           ("[`remove`](remove.md)", "ファイルごと消す")],
  memo=["ファイルの大きさだけを変える", "縮めた部分は戻らない", "伸ばした部分は 0 で埋まる"])

rewrite(F + 'u8path.md',
  intro="""UTF-8 の文字列から、`path` を作りたい。Windows では、`path` の内部は UTF-16 で、`const char*` の文字列は「そのときのコード ページ」で解釈されます。日本語のファイル名を UTF-8 の文字列から作ろうとすると、文字化けします。

`std::filesystem::u8path` は、<strong>UTF-8 の文字列を、文字コードを変換しながら `path` にする</strong>関数でした。ただし、C++20 から、`char8_t` の文字列を直接受け取る `path` のコンストラクターが加わり、この関数は非推奨になっています。""",
  tips=["C++17 で追加され、C++20 で非推奨になった。新しいコードでは使わない",
        "代わりに、`std::u8string` や `char8_t` の文字列から `fs::path` を直接作る",
        "UTF-8 の `char` 文字列を、そのコード ページ解釈のまま `path` に渡すと、Windows では文字化けする",
        "ASCII だけの文字列なら、どの方法でも結果は同じ"],
  details="""### u8path {#u8path}

<span class="ver ver-17">C++17</span> <span class="ver ver-20">C++20 で非推奨</span>

```cpp
template <class Source>
path u8path(const Source& source);
template <class InputIt>
path u8path(InputIt first, InputIt last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `source` | 文字列 | UTF-8 でエンコードされた `std::string` や `const char*` など |
| `first`, `last` | イテレータ | UTF-8 の文字の範囲 |

渡された UTF-8 の文字列を、その OS が `path` に使う形式（Windows は UTF-16、Linux は UTF-8 のまま）に変換して、`path` を返します。変換されるので、<strong>`path` を作ったあとに `.string()` で取り出すと、Windows では UTF-8 ではなく、コード ページの文字列になります</strong>。UTF-8 で取り出すには、`.u8string()` を使います。

C++20 では、`char8_t` が導入され、`path` のコンストラクターが `std::u8string` や `u8"..."` を受け取れるようになりました。これで十分なので、`u8path` は非推奨です。コンパイラが警告を出すことがあります。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;

  // 新しい書き方（C++20）: u8 の文字列から直接 path を作る
  fs::path p = u8"assets/hero.png";
  std::println("ファイル名: {}", p.filename().string());
  std::println("拡張子: {}", p.extension().string());

  // 日本語のファイル名も、u8 の文字列なら文字化けしない（内部では UTF-16 になる）
  fs::path jp = u8"assets/ボス.png";
  std::println("拡張子は .png: {}", jp.extension() == ".png");
}""",
  out="""ファイル名: hero.png
拡張子: .png
拡張子は .png: true""",
  uses="""UTF-8 でデータを持つゲーム（設定ファイルや JSON の中のアセット名を UTF-8 で書いている）が、日本語のパスを扱うときに必要になります。Windows でファイルを開く直前に、UTF-8 から `path` へ変換するのが、この関数の役割でした。

新しいコードでは、`u8"..."` のリテラルや `std::u8string` から `path` を作ります。`char` の UTF-8 文字列しか手元にない場合は、`reinterpret_cast` で `char8_t` に見せる、もしくは文字コード変換の関数を自分で用意します。文字コード全般は、[文字コード](../../../encoding/index.md)の章を参照してください。""",
  mistakes=[("UTF-8 の `char` 文字列を、そのまま `path` に渡して化ける", "`fs::path(\"ボス.png\")` は、Windows では文字列を現在のコード ページ（日本語環境なら Shift_JIS）として解釈します。ソースを UTF-8 で保存していると、別の文字に変わります。`u8` のリテラルから作ります。"),
            ("`.string()` の結果が UTF-8 だと思い込む", "Windows の `.string()` は、コード ページの文字列です。UTF-8 が欲しいなら `.u8string()` で取り出します。")],
  similar=[("`path(std::u8string)`", "C++20 以降の標準的な作り方"),
           ("[`path`](path.md)", "パスの型。文字コードの扱いは、こちらも参照")],
  memo=["UTF-8 から `path` を作る関数", "C++20 では非推奨", "新しいコードでは `u8` の文字列から直接作る"])
print('fs1 ok')
