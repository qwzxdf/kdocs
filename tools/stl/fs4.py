"""filesystem の薄いページを書き直す（バッチ 4: 基本の判定と操作）。"""
from rw import rewrite

F = 'stl/io/filesystem/'

rewrite(F + 'perms.md',
  intro="""ファイルの「読める」「書ける」「実行できる」は、誰に対して許すのかまで含めて、9 個のスイッチで表せます。持ち主、同じグループの人、それ以外の人の 3 者に、それぞれ読み・書き・実行の 3 つです。Unix 系の OS が長年使っている、この考え方を表したのが `std::filesystem::perms` です。

<strong>1 つの権限が、1 つのビット</strong>になっている列挙型で、`|` で組み合わせ、`&` で取り出します。""",
  tips=["`owner_read`、`group_write`、`others_exec` のように、「誰が」「何を」の 9 通りが基本",
        "`owner_all`、`group_all`、`others_all`、`all` は、まとめた値",
        "`|` で組み合わせ、`&` で取り出す。結果も `perms` 型なので、`none` と比べて判定する",
        "Windows では、実質的に「読み取り専用か」だけ。細かい権限は反映されない"],
  details="""### perms {#perms}

<span class="ver ver-17">C++17</span>

```cpp
enum class perms : unsigned {
  none = 0,
  owner_read = 0400,  owner_write = 0200,  owner_exec = 0100,  owner_all = 0700,
  group_read = 040,   group_write = 020,   group_exec = 010,   group_all = 070,
  others_read = 04,   others_write = 02,   others_exec = 01,   others_all = 07,
  all = 0777,
  set_uid = 04000,    set_gid = 02000,     sticky_bit = 01000,
  mask = 07777,
  unknown = 0xFFFF
};
```

値は 8 進数で、`chmod` コマンドの数字と同じです。`0644` なら、持ち主は読み書き、他は読むだけ、という意味で、`owner_read | owner_write | group_read | others_read` になります。

`none` は「権限が 1 つもない」、`unknown` は「権限が取得できなかった」ことを表します。この 2 つは別物で、`unknown` と `&` を取ると意味のない値になるので、先に `status_known` や `permissions() != unknown` を確かめます。

`set_uid`、`set_gid`、`sticky_bit` は、Unix 固有の特別なビットで、Windows では意味を持ちません。

`enum class` なので、`|` や `&` は、標準が演算子を用意しています。ただし結果が `perms` 型のため、`if (st.permissions() & fs::perms::owner_read)` とは書けず、`!= fs::perms::none` と比べます。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  using fs::perms;

  // 0644: 持ち主は読み書き、他の人は読むだけ
  perms p = perms::owner_read | perms::owner_write | perms::group_read | perms::others_read;
  std::println("8 進数: {:o}", static_cast<unsigned>(p));

  // 取り出して判定する
  bool owner_can_write = (p & perms::owner_write) != perms::none;
  bool others_can_write = (p & perms::others_write) != perms::none;
  std::println("持ち主が書ける: {}", owner_can_write);
  std::println("他の人が書ける: {}", others_can_write);

  // まとめた値
  std::println("all: {:o}", static_cast<unsigned>(perms::all));
  std::println("owner_all: {:o}", static_cast<unsigned>(perms::owner_all));
}""",
  out="""8 進数: 644
持ち主が書ける: true
他の人が書ける: false
all: 777
owner_all: 700""",
  uses="""ファイルの保存先に書き込めるかの判定や、セーブ データを読み取り専用にして誤った上書きを防ぐ場面で使います。`permissions` 関数にこの値を渡して、権限を変更します。

Windows 中心のゲームでは、読み取り専用にするかどうかだけを意識します。書き込みのビット 3 つ（`owner_write | group_write | others_write`）をまとめて外すと、Windows では読み取り専用属性になります。""",
  mistakes=[("`if (p & perms::owner_read)` と書いて、コンパイル エラー", "`perms` は `enum class` なので、`bool` に変換できません。`(p & perms::owner_read) != perms::none` と比べます。"),
            ("Windows で `owner_write` だけを外して、読み取り専用にならない", "Windows は、書き込みのビット 3 つを全部外したときだけ、読み取り専用として扱います。")],
  similar=[("[`permissions`](permissions.md)", "権限を変更する関数"),
           ("[`perm_options`](perm_options.md)", "`permissions` の動かし方（追加、削除、置き換え）を選ぶ"),
           ("[`file_status`](file_status.md)", "`permissions()` で、この型の現在値を返す")],
  memo=["権限を 1 ビットずつ表す列挙型", "`|` で組み合わせ、`& ... != none` で判定", "Windows は書き込みの有無が中心"])

rewrite(F + 'create_hard_link.md',
  intro="""同じアセットを、2 つのフォルダーに置きたい。コピーするとディスクを 2 倍使いますし、片方を更新したときに、もう片方との差が出ます。ハード リンクなら、ファイルの実体は 1 つのまま、名前だけを増やせます。

`std::filesystem::create_hard_link` は、<strong>既存のファイルに、もう 1 つの名前（パス）を付ける</strong>関数です。どちらの名前から書き換えても、同じ実体が変わります。""",
  tips=["実体が共有されるので、片方への書き込みは、もう片方でも見える",
        "どちらの名前を消しても、最後の名前が消えるまで、データは残る",
        "同じボリュームの中でだけ作れる。別のドライブとの間では失敗する",
        "フォルダーには、ふつう作れない。ファイル用"],
  details="""### create_hard_link {#create_hard_link}

<span class="ver ver-17">C++17</span>

```cpp
void create_hard_link(const path& target, const path& link);
void create_hard_link(const path& target, const path& link, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | `const path&` | すでに存在するファイル |
| `link` | `const path&` | 新しく付ける名前。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

引数の順番は、<strong>「元」が先、「新しい名前」が後</strong>です。`create_symlink` も同じ順なので、`std::filesystem::copy` のように「コピー元、コピー先」と読めば、覚えやすくなります。

成功すると、`link` と `target` は、ディスク上の同じ実体を指します。[`hard_link_count`](hard_link_count.md) が 2 になり、[`equivalent`](equivalent.md) で比べると `true` になります。

シンボリックリンクと違い、`target` の名前を変えたり、消したりしても、`link` は壊れません。実体がある限り、`link` からそのまま読めます。一方、ファイルシステムが対応していないと失敗します（FAT 系など）。NTFS や ext4 などは対応しています。""",
  code="""#include <filesystem>
#include <fstream>
#include <iterator>
#include <print>
#include <string>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("orig.txt") << "hello";

  fs::create_hard_link("orig.txt", "alias.txt");
  std::println("同じ実体: {}", fs::equivalent("orig.txt", "alias.txt"));
  std::println("リンク数: {}", fs::hard_link_count("orig.txt"));

  // 元の名前を消しても、別の名前から読める
  fs::remove("orig.txt");
  std::ifstream in("alias.txt");
  std::string text((std::istreambuf_iterator<char>(in)), {});
  std::println("alias.txt の中身: {}", text);
}""",
  out="""同じ実体: true
リンク数: 2
alias.txt の中身: hello""",
  uses="""ビルド システムや、パッケージ作成ツールで、同じアセットを複数のフォルダーに置くときに使います。コピーに比べて、ディスクを使わず、作成も速くなります。

ただし、書き換えを「片方だけに反映したい」場面には向きません。実体が 1 つなので、片方への書き込みが、もう片方にも反映されます。独立した複製が欲しいなら、`copy_file` を使います。""",
  mistakes=[("引数の順番を逆にして、既存の名前を上書きしようとする", "第 1 引数が元のファイル、第 2 引数が新しい名前です。第 2 引数がすでに存在すると、失敗します。"),
            ("別のドライブに作ろうとして失敗する", "ハード リンクは、同じボリュームの中でしか作れません。ボリュームをまたぐなら `copy_file` を使います。")],
  similar=[("[`create_symlink`](create_symlink.md)", "別の名前を指す参照を作る。実体は共有しない"),
           ("[`copy_file`](copy_file.md)", "独立した複製を作る"),
           ("[`hard_link_count`](hard_link_count.md)", "名前の数を調べる")],
  memo=["同じ実体に別の名前を付ける", "引数は「元、新しい名前」の順", "同じボリュームの中だけ"])

rewrite(F + 'create_directory_symlink.md',
  intro="""フォルダーを、別の場所にあるように見せたい。たとえば、巨大なアセット フォルダーをディスクの別の場所に置いて、ゲーム フォルダーの `assets` という名前から指したい。このとき使うのが、フォルダーへのシンボリックリンクです。

`std::filesystem::create_directory_symlink` は、<strong>フォルダーを指すシンボリックリンク</strong>を作ります。[`create_symlink`](create_symlink.md) と同じ働きですが、Windows ではファイル用とフォルダー用が別の種類なので、フォルダーを指すときは、こちらを使います。""",
  tips=["フォルダーを指すリンクを作る専用の関数。POSIX では `create_symlink` と同じ動き",
        "Windows ではフォルダー用のリンクとファイル用のリンクが区別され、種類を間違えるとリンクが機能しない",
        "Windows では、リンクを作る権限（開発者モードなど）が必要",
        "引数の順番は、「指し先、リンクの名前」"],
  details="""### create_directory_symlink {#create_directory_symlink}

<span class="ver ver-17">C++17</span>

```cpp
void create_directory_symlink(const path& target, const path& link);
void create_directory_symlink(const path& target, const path& link, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | `const path&` | 指し先のフォルダー |
| `link` | `const path&` | 作るリンクの名前。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

Windows の NTFS では、シンボリックリンクにファイル用とフォルダー用の 2 種類があります。指し先がフォルダーなのにファイル用のリンクを作ると、`cd` や、フォルダーとして開く操作が失敗します。そのため、フォルダーを指すときは、`create_symlink` ではなく、この関数を使います。

`target` は、書いたとおりの文字列がリンクに保存されます。相対パスなら、リンクのあるフォルダーから見た位置として解釈されます。実在しなくても作れます。

Windows 10 以降は、「開発者モード」を有効にするか、管理者として実行しているときに、作れます。権限がないと失敗するので、`error_code` 版で調べるか、例外を処理します。""",
  code="""#include <filesystem>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  fs::create_directory("real_assets");

  std::error_code ec;
  fs::create_directory_symlink("real_assets", "assets", ec);

  // 作れたか、権限がなくて作れなかったか。どちらの環境でも、結果は整合している
  std::println("結果が整合している: {}", static_cast<bool>(ec) == !fs::is_symlink("assets"));
}""",
  out="結果が整合している: true",
  uses="""ゲームの開発環境で、巨大なアセット フォルダーを別のドライブに置き、プロジェクトからは同じ名前で見せる、という構成に使います。ビルド システムが、プロジェクト フォルダーにリンクを作る処理を持つことがあります。

製品版の配布物に、シンボリックリンクを含めることは、あまりしません。権限の問題があり、Windows では ZIP の展開などでリンクが壊れることがあるためです。""",
  mistakes=[("フォルダーを指すのに `create_symlink` を使い、Windows で開けないリンクになる", "フォルダーへのリンクには、この関数を使います。"),
            ("権限がなくて失敗する", "Windows では、開発者モードを有効にするか、管理者権限が必要です。`error_code` 版を使い、失敗したらコピーで代用する、といった逃げ道を用意します。")],
  similar=[("[`create_symlink`](create_symlink.md)", "ファイルを指すシンボリックリンク"),
           ("[`create_hard_link`](create_hard_link.md)", "ファイルの実体を共有する別名"),
           ("[`read_symlink`](read_symlink.md)", "リンクの指し先を読む")],
  memo=["フォルダーを指すシンボリックリンクを作る", "Windows ではファイル用と区別される", "権限が必要なことがある"])

rewrite(F + 'is_regular_file.md',
  intro="""設定ファイルを読み込む前に、「そこにあるのは、ふつうのファイルか」を確かめたい。パスがフォルダーだったり、デバイスだったり、そもそも存在しなかったりすると、読み込みに失敗します。

`std::filesystem::is_regular_file` は、<strong>パスが通常のファイル</strong>（フォルダーでも、リンクでも、デバイスでもない）であるかを調べます。ファイルを開く前の検査として、いちばんよく使う判定です。""",
  tips=["`is_regular_file(p)` は、`p` が通常のファイルなら `true`",
        "存在しないパスは `false`。例外にはならない",
        "リンクは先をたどって判定する。リンクがファイルを指していれば `true`",
        "ファイルを開く前の検査は、`exists` よりこちら。フォルダーも `exists` は `true` になる"],
  details="""### is_regular_file {#is_regular_file}

<span class="ver ver-17">C++17</span>

```cpp
bool is_regular_file(const path& p);
bool is_regular_file(const path& p, std::error_code& ec) noexcept;
bool is_regular_file(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::regular` と同じです。存在しない、フォルダー、デバイス、ソケット、パイプのとき、`false` になります。

`exists` との違いに注意します。`exists("saves")` は、フォルダーでも `true` ですが、`is_regular_file("saves")` は `false` です。ファイルを開く前の検査は、`exists` では足りません。

ファイルの存在判定に、`std::ifstream` を開いて `is_open()` を見る方法もありますが、読み取り権限がなくて開けないだけのファイルと、存在しないファイルを区別できません。`is_regular_file` なら、存在だけを調べられます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("config.ini") << "x";
  fs::create_directory("saves");

  std::println("config.ini: {}", fs::is_regular_file("config.ini"));
  std::println("saves: {}", fs::is_regular_file("saves"));
  std::println("missing.ini: {}", fs::is_regular_file("missing.ini"));

  // exists との違い: フォルダーでも true になる
  std::println("exists(saves): {}", fs::exists("saves"));
}""",
  out="""config.ini: true
saves: false
missing.ini: false
exists(saves): true""",
  uses="""設定ファイルやセーブ データを読み込む前の検査に使います。`is_regular_file` が `true` のときだけ開き、`false` なら既定値で起動する、と書くと、パスがフォルダーだった場合も、まとめて安全に扱えます。

フォルダーを走査して、アセットを集めるときも、`entry.is_regular_file()` で通常のファイルだけを拾います。デバイスやパイプが混ざっても、読み込みが固まりません。""",
  mistakes=[("`exists` で確かめて、フォルダーを開こうとして失敗する", "`exists` はフォルダーでも `true` です。ファイルとして開くなら、`is_regular_file` で確かめます。"),
            ("確かめた直後に、ファイルが消えて失敗する", "確認と使用の間に状態が変わることがあります（TOCTOU）。最終的には、開く処理の失敗を処理する必要があります。")],
  similar=[("[`exists`](exists.md)", "種類を問わず、存在するか"),
           ("[`is_directory`](is_directory.md)", "フォルダーか"),
           ("[`is_other`](is_other.md)", "通常のファイルでもフォルダーでもない存在するものか")],
  memo=["通常のファイルか", "存在しなければ `false`", "ファイルを開く前の検査に使う"])

rewrite(F + 'is_directory.md',
  intro="""ユーザーが指定したパスが、フォルダーなのか、ファイルなのか。ドラッグ アンド ドロップされたものがフォルダーなら、中身を取り込む。ファイルなら、そのまま開く。この分岐に使うのが、`std::filesystem::is_directory` です。

<strong>パスがフォルダー</strong>であるかを調べます。""",
  tips=["`is_directory(p)` は、`p` がフォルダーなら `true`",
        "存在しないパスは `false`。例外にはならない",
        "リンクは先をたどって判定する。フォルダーを指すシンボリックリンクは `true`",
        "ファイルの判定は `is_regular_file`。ファイルでなければフォルダー、とは限らない"],
  details="""### is_directory {#is_directory}

<span class="ver ver-17">C++17</span>

```cpp
bool is_directory(const path& p);
bool is_directory(const path& p, std::error_code& ec) noexcept;
bool is_directory(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::directory` と同じです。存在しない、通常のファイル、デバイスなどのときは、`false` を返します。

ファイルかフォルダーかの 2 択で考えがちですが、現実のパスには、存在しない、デバイス、ソケット、といった第 3 の状態があります。`!is_directory(p)` を「ファイルである」と読み替えると、存在しないパスも「ファイル」になってしまいます。ファイルかどうかは、`is_regular_file` で直接調べます。

フォルダーを走査している途中の項目には、`directory_entry::is_directory()` を使うほうが速くなります。走査のときに得た情報を、そのまま使えるからです。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("file.txt") << "x";
  fs::create_directory("folder");

  for (const char* name : {"file.txt", "folder", "missing"}) {
    std::println("{}: フォルダー={} ファイル={}", name,
                 fs::is_directory(name), fs::is_regular_file(name));
  }
}""",
  out="""file.txt: フォルダー=false ファイル=true
folder: フォルダー=true ファイル=false
missing: フォルダー=false ファイル=false""",
  uses="""ドラッグ アンド ドロップされたパスの処理や、コマンドライン引数でフォルダーが渡されたときの分岐に使います。フォルダーなら中のファイルを走査して取り込み、ファイルなら 1 つだけ取り込む、という流れです。

保存先のフォルダーが存在するかの確認にも使います。`create_directories` を呼ぶ前に確認すれば、無駄な処理を避けられます（`create_directories` は、すでにあれば何もせず `false` を返すので、確認を省くこともできます）。""",
  mistakes=[("`!is_directory` を「ファイルである」と読む", "存在しないパスも `!is_directory` になります。ファイルかどうかは `is_regular_file` で調べます。"),
            ("走査の途中で、毎回 `is_directory(path)` を呼び、遅くなる", "`directory_entry` の `is_directory()` なら、走査時の情報を使えて、追加の問い合わせが減ります。")],
  similar=[("[`is_regular_file`](is_regular_file.md)", "通常のファイルか"),
           ("[`exists`](exists.md)", "種類を問わず、存在するか"),
           ("[`directory_entry`](directory_entry.md)", "走査の途中の項目。種類の判定を持っている")],
  memo=["フォルダーか", "存在しなければ `false`", "`!is_directory` はファイルの意味ではない"])

rewrite(F + 'file_size.md',
  intro="""ファイルを丸ごと読み込むために、先に大きさを知って、その分のバッファーを確保したい。ダウンロードの進み具合を、保存されたファイルの大きさから計算したい。ファイルを開いて `seekg` するよりも、手軽に大きさを知る方法が `std::filesystem::file_size` です。

<strong>通常のファイルのバイト数</strong>を返します。""",
  tips=["戻り値は `std::uintmax_t`（符号なしの大きな整数）",
        "存在しないパスはエラー。フォルダーに使った結果は、実装によって違う（エラーになる環境も、値が返る環境もある）",
        "リンクは先をたどった、実体のファイルの大きさ",
        "ファイルを書いている途中は、書き込み済みの量とずれることがある（バッファーのため）"],
  details="""### file_size {#file_size}

<span class="ver ver-17">C++17</span>

```cpp
std::uintmax_t file_size(const path& p);
std::uintmax_t file_size(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 大きさを調べるファイル |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値の型 `std::uintmax_t` は、最も大きな符号なし整数型なので、4 GB を超えるファイルでも扱えます。`int` に代入すると、2 GB を超えたところで壊れるので、`std::size_t` や `std::uintmax_t` で受けます。

存在しないパスに使うと、例外（または `ec` のエラー）になります。標準はフォルダーなど通常のファイルでないものもエラーとしていますが、手元の MSVC ではエラーにならず、値が返りました。フォルダーには使わないようにします。`error_code` を渡す版は、エラーのときに `static_cast<std::uintmax_t>(-1)` を返します。<strong>この値を、そのまま大きさとして使わない</strong>ようにします。

ファイルのバッファーに、まだ書き込まれていないデータがあると、実際に書いた量より小さい値になります。確実に調べたいときは、ストリームを `flush` するか閉じてから呼びます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  {
    std::ofstream out("data.bin", std::ios::binary);
    out << "0123456789";
  }
  std::println("data.bin: {} バイト", fs::file_size("data.bin"));

  // 存在しないパスは、エラーになる
  std::error_code ec;
  auto size = fs::file_size("missing.bin", ec);
  std::println("存在しない: エラー={} 戻り値は最大値={}", static_cast<bool>(ec),
               size == static_cast<std::uintmax_t>(-1));
}""",
  out="""data.bin: 10 バイト
存在しない: エラー=true 戻り値は最大値=true""",
  uses="""ファイルを丸ごと読み込むときの、バッファーの確保に使います。`std::vector<char> buf(fs::file_size(path))` で、ちょうどの大きさを用意して、`read` で一気に読み込みます。

ダウンロードの進行状況の表示や、セーブ データが空（0 バイト）でないかの確認、キャッシュ フォルダーの合計サイズの計算にも使います。合計サイズは、フォルダーを走査して、通常のファイルの `file_size` を足し上げます。""",
  mistakes=[("フォルダーに使って、フォルダー全体の大きさだと思う", "この関数は、フォルダーの中身の合計を返しません。環境によっては、エラーや、意味のない値になります。中のファイルを走査して足し合わせます。"),
            ("`int` で受けて、大きなファイルで負の値になる", "`std::uintmax_t` で受けます。`size_t` に直すときも、範囲を確かめます。")],
  similar=[("[`space`](space.md)", "ボリュームの空き容量"),
           ("[`resize_file`](resize_file.md)", "ファイルの大きさを変更する"),
           ("[`is_empty`](is_empty.md)", "空かどうかだけを調べる")],
  memo=["通常のファイルのバイト数を返す", "`uintmax_t` で受ける", "フォルダーにはエラー"])

rewrite(F + 'create_directory.md',
  intro="""セーブ データの保存先 `saves` フォルダーを、初回の起動で作りたい。ファイルを書き込む前に、置き場所のフォルダーが無いと、書き込みは失敗します。

`std::filesystem::create_directory` は、<strong>フォルダーを 1 つ作る</strong>関数です。すでにあっても失敗せず、戻り値で「新しく作ったか」を教えてくれます。""",
  tips=["作るのは、最後の 1 階層だけ。途中のフォルダーが無いとエラー",
        "すでにフォルダーがあるときは、エラーではなく `false` を返す",
        "途中の階層もまとめて作るなら `create_directories`",
        "同じ名前のファイルがあるときは、エラー"],
  details="""### create_directory {#create_directory}

<span class="ver ver-17">C++17</span>

```cpp
bool create_directory(const path& p);
bool create_directory(const path& p, std::error_code& ec) noexcept;
bool create_directory(const path& p, const path& existing_p);
bool create_directory(const path& p, const path& existing_p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 作るフォルダーのパス |
| `existing_p` | `const path&` | 属性を真似る既存のフォルダー。省略すると既定の属性 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、<strong>新しく作ったら `true`、すでにフォルダーがあって何もしなかったら `false`</strong> です。「あっても大丈夫」という性質のため、起動時の初期化に便利で、`if (!exists) create` と書く必要がありません。

作れない場合は例外（または `ec`）になります。典型的な原因は、親のフォルダーが存在しない、同じ名前のファイルがある、書き込む権限がない、の 3 つです。

`existing_p` を渡す版は、既存のフォルダーと同じ属性（権限など）で、新しいフォルダーを作ります。あまり使いません。""",
  code="""#include <filesystem>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;

  std::println("1 回目: {}", fs::create_directory("saves"));   // 新しく作った
  std::println("2 回目: {}", fs::create_directory("saves"));   // すでにある

  // 途中のフォルダーが無いと、作れない
  std::error_code ec;
  bool r = fs::create_directory("a/b/c", ec);
  std::println("a/b/c: 作った={} エラー={}", r, static_cast<bool>(ec));
}""",
  out="""1 回目: true
2 回目: false
a/b/c: 作った=false エラー=true""",
  uses="""起動時の初期化で、セーブ フォルダーやキャッシュ フォルダーを用意するときに使います。1 階層だけなら `create_directory`、`Saved/Profiles/Player1` のように複数の階層がまとめて必要なら、`create_directories` を使います。

戻り値が `true` のときだけ、初期データを書き込む、という使い方もできます。`false` なら、すでにユーザーのデータがあるので、触らない、という分岐です。""",
  mistakes=[("複数階層を `create_directory` で作ろうとして、エラー", "途中のフォルダーが無いと失敗します。`create_directories` を使います。"),
            ("同じ名前のファイルがあって失敗する", "フォルダーを作ろうとした名前に、すでにファイルがあるとエラーです。`is_directory` で確かめてから処理を分けます。")],
  similar=[("[`create_directories`](create_directories.md)", "途中の階層もまとめて作る"),
           ("[`remove`](remove.md)", "空のフォルダーを消す"),
           ("[`is_directory`](is_directory.md)", "フォルダーがあるか確かめる")],
  memo=["フォルダーを 1 階層だけ作る", "すでにあれば `false`（エラーではない）", "複数階層は `create_directories`"])

rewrite(F + 'remove.md',
  intro="""一時ファイルを使い終わったので消したい。セーブ データを削除したい。ファイルやフォルダーを消す処理は、うっかり使うと大事なデータを失うので、振る舞いをよく知っておきたい関数です。

`std::filesystem::remove` は、<strong>ファイル 1 つ、または空のフォルダー 1 つ</strong>を消します。中身のあるフォルダーは消せません。""",
  tips=["消せたら `true`、もともと存在しなかったら `false`（エラーではない）",
        "フォルダーは、空のときだけ消せる。中身があるとエラー",
        "中身ごと消すなら `remove_all`",
        "シンボリックリンクは、リンクだけを消す。指し先は消さない"],
  details="""### remove {#remove}

<span class="ver ver-17">C++17</span>

```cpp
bool remove(const path& p);
bool remove(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 消すファイルまたは空のフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、<strong>実際に消したなら `true`、もともと無かったなら `false`</strong> です。存在しないものを消そうとしても、エラーにはなりません。「消えた状態にする」という目的は達成されているからです。一時ファイルの後片付けのように、あってもなくてもよい物に向きます。

中身のあるフォルダーを渡すと、エラー（例外または `ec`）になります。フォルダーの中身が消える危険のある操作なので、`remove` では許されていません。

Windows では、他のプロセスが開いているファイルは消せません。読み取り専用属性のファイルも、そのままでは消せない場合があります。その場合は、`permissions` で書き込み権限を戻してから消します。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("temp.txt") << "x";
  fs::create_directories("full/sub");
  fs::create_directory("empty");

  std::println("temp.txt を消した: {}", fs::remove("temp.txt"));
  std::println("もう一度: {}", fs::remove("temp.txt"));       // もう無いので false
  std::println("空のフォルダー: {}", fs::remove("empty"));

  // 中身のあるフォルダーは、消せない
  std::error_code ec;
  fs::remove("full", ec);
  std::println("中身のあるフォルダー: エラー={} 残っている={}", static_cast<bool>(ec), fs::exists("full"));
}""",
  out="""temp.txt を消した: true
もう一度: false
空のフォルダー: true
中身のあるフォルダー: エラー=true 残っている=true""",
  uses="""一時ファイルの後片付けに使います。終了時に `remove(tmp)` を呼んでおけば、あってもなくても安全に終わります。セーブ データの削除（「このスロットを消す」）にも使います。

フォルダーごと消すときは `remove_all` を使いますが、これは危険な操作です。パスの組み立てを間違えると、意図しない場所を丸ごと消します。呼ぶ前に、消す対象が自分の作業フォルダーの内側かを、`weakly_canonical` などで確かめるのが安全です。""",
  mistakes=[("中身のあるフォルダーを `remove` で消そうとして失敗する", "空でないフォルダーは消せません。`remove_all` を使います。"),
            ("存在しないものを消して、エラーになると思い、try-catch を書く", "存在しないだけなら、エラーではなく `false` です。")],
  similar=[("[`remove_all`](remove_all.md)", "フォルダーを中身ごと消す"),
           ("[`rename`](rename.md)", "名前を変える。ゴミ箱へ移す代わりに使うこともある")],
  memo=["ファイルまたは空のフォルダーを消す", "存在しなければ `false`", "中身ごとなら `remove_all`"])

rewrite(F + 'last_write_time.md',
  intro="""アセットを最後に更新した時刻を調べて、ビルドの必要があるかを判断したい。セーブ データの一覧を、新しい順に並べたい。ファイルの「最後に書き込まれた時刻」を取得する関数が `std::filesystem::last_write_time` で、同じ名前で時刻の設定もできます。""",
  tips=["引数を 1 つ渡すと取得、時刻も渡すと設定",
        "時刻の型は [`file_time_type`](file_time_type.md)。`system_clock` とは別の時計",
        "新しさの比較（`<`、`>`）や、時間差の計算は、そのまま行える",
        "人が読む日時に直すには、`clock_cast`（C++20）で `system_clock` に変換する"],
  details="""### last_write_time {#last_write_time}

<span class="ver ver-17">C++17</span>

```cpp
file_time_type last_write_time(const path& p);
file_time_type last_write_time(const path& p, std::error_code& ec) noexcept;
void last_write_time(const path& p, file_time_type new_time);
void last_write_time(const path& p, file_time_type new_time, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 対象のファイルまたはフォルダー |
| `new_time` | `file_time_type` | 設定する時刻 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

取得する版は、`file_time_type` を返します。ファイルが存在しない、権限がない、といったときは、例外（または `ec`）です。

設定する版は、ファイルの内容を変えずに、更新時刻だけを書き換えます。ビルド システムが、「この出力は、この入力より新しい」と見せかけたいときや、テストで古いファイルを用意したいときに使います。

返ってくる時刻の精度は、ファイルシステムによって違います（NTFS は 100 ナノ秒、FAT は 2 秒など）。書き込んだ時刻と、すぐ読み取った時刻が、丸められて少し違うことがあります。<strong>等しいかどうかで比べず</strong>、大小や、ある幅の差で比べます。""",
  code="""#include <chrono>
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("shader.hlsl") << "x";
  std::ofstream("shader.cso") << "x";

  // ソース（hlsl）のほうを新しい時刻にして、「再コンパイルが必要」を作る
  auto now = fs::file_time_type::clock::now();
  fs::last_write_time("shader.cso", now - std::chrono::hours(2));
  fs::last_write_time("shader.hlsl", now);

  bool need_rebuild = fs::last_write_time("shader.hlsl") > fs::last_write_time("shader.cso");
  std::println("再コンパイルが必要: {}", need_rebuild);

  // 出力のほうを新しくすると、不要になる
  fs::last_write_time("shader.cso", now + std::chrono::minutes(1));
  need_rebuild = fs::last_write_time("shader.hlsl") > fs::last_write_time("shader.cso");
  std::println("更新後は不要: {}", !need_rebuild);
}""",
  out="""再コンパイルが必要: true
更新後は不要: true""",
  uses="""ビルド パイプラインやホット リロードで、「元のファイルが、生成物より新しいか」を判定します。シェーダー、テクスチャ、モデルを、変更されたものだけ再変換する仕組みの基本です。

ゲーム内のセーブ データ一覧では、各ファイルの更新時刻を取得して、新しい順に並べ、「最終プレイ日時」として表示します。表示するときは、`system_clock` に直してから書式化します。""",
  mistakes=[("`==` で更新時刻の一致を判定して、環境によって外れる", "精度や丸めの違いで、書いた値と読んだ値がぴったり一致するとは限りません。大小で比べます。"),
            ("`file_time_type` を `system_clock::time_point` と直接比べて、コンパイル エラー", "時計が違うので、そのままでは比べられません。`clock_cast` で変換します。")],
  similar=[("[`file_time_type`](file_time_type.md)", "この関数が使う時刻の型"),
           ("[`directory_entry`](directory_entry.md)", "走査の途中で更新時刻を持っている")],
  memo=["最後に書き込まれた時刻の取得と設定", "型は `file_time_type`", "`==` ではなく大小で比べる"])
print('fs4 ok')
