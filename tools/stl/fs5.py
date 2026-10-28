"""filesystem の残りと cstdio の定数・v*printf を書き直す（バッチ 5）。"""
from rw import rewrite

F = 'stl/io/filesystem/'
C = 'stl/io/cstdio/'

rewrite(F + 'copy.md',
  intro="""ゲームのインストールや、セーブ データのバックアップで、フォルダーをまるごとコピーしたい。ファイル 1 つなら `copy_file` ですが、フォルダーの中身や、リンクの扱いまで考えると、選ぶことが多くなります。

`std::filesystem::copy` は、<strong>ファイルでもフォルダーでも、`copy_options` の指定に従ってコピー</strong>する、いちばん汎用的な関数です。""",
  tips=["コピー元がファイルなら `copy_file` と同じ。フォルダーなら、既定では直下のファイルだけ",
        "フォルダーの中身まで全部なら `copy_options::recursive`",
        "既存のファイルがあると、既定ではエラー。`overwrite_existing` などで動きを選ぶ",
        "オプションなしでサブフォルダーを含むフォルダーをコピーすると、サブフォルダーは作られない"],
  details="""### copy {#copy}

<span class="ver ver-17">C++17</span>

```cpp
void copy(const path& from, const path& to);
void copy(const path& from, const path& to, copy_options options);
void copy(const path& from, const path& to, std::error_code& ec);
void copy(const path& from, const path& to, copy_options options, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `from` | `const path&` | コピー元のファイルまたはフォルダー |
| `to` | `const path&` | コピー先。フォルダーを指していれば、その中に入る |
| `options` | [`copy_options`](copy_options.md) | 動き方。省略すると `none` |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`from` がふつうのファイルで、`to` がフォルダーなら、`to` の中に同じ名前でコピーされます。`to` がファイルの名前なら、その名前でコピーされます。

`from` がフォルダーのときの動きが、いちばん間違えやすい所です。<strong>オプションなしでは、そのフォルダーの直下にあるファイルだけがコピーされ、サブフォルダーは無視されます</strong>。サブフォルダーの中身まで、全部をコピーするには、`copy_options::recursive` を付けます。`directories_only` を付けると、フォルダー構造だけが作られ、ファイルはコピーされません。

コピー先に同名のファイルがあるとき、オプションなしではエラーになります。`skip_existing` なら飛ばし、`overwrite_existing` なら上書き、`update_existing` なら、コピー元のほうが新しいときだけ上書きします。この 3 つは同時に指定できません。

シンボリックリンクの扱いも、オプションで決まります。`copy_symlinks` はリンクとしてコピーし、`skip_symlinks` は無視し、どちらも付けないと、リンクの指し先をコピーします。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("src/sub");
  std::ofstream("src/a.txt") << "a";
  std::ofstream("src/sub/b.txt") << "b";

  // オプションなし: 直下のファイルだけ
  fs::copy("src", "dst1");
  std::println("dst1/a.txt: {}", fs::exists("dst1/a.txt"));
  std::println("dst1/sub: {}", fs::exists("dst1/sub"));

  // recursive: サブフォルダーの中まで
  fs::copy("src", "dst2", fs::copy_options::recursive);
  std::println("dst2/sub/b.txt: {}", fs::exists("dst2/sub/b.txt"));

  // ファイルをフォルダーの中へ
  fs::copy("src/a.txt", "dst1/sub_copy");   // 名前が新規なので、そのままの名前でコピーされる
  std::println("dst1/sub_copy: {}", fs::is_regular_file("dst1/sub_copy"));
}""",
  out="""dst1/a.txt: true
dst1/sub: false
dst2/sub/b.txt: true
dst1/sub_copy: true""",
  uses="""ゲームのインストーラーや、セーブ データのバックアップで、フォルダー全体をコピーするときに使います。`recursive | update_existing` を指定すると、新しくなったファイルだけを上書きする、簡易な差分更新になります。

MOD や、ユーザーのカスタム データを取り込むときは、`skip_existing` を付けて、既存のファイルを守る使い方もあります。""",
  mistakes=[("フォルダーをコピーしたのに、サブフォルダーが無い", "オプションなしでは、直下のファイルしかコピーされません。`copy_options::recursive` を付けます。"),
            ("同名のファイルがあって、エラーになる", "既定では上書きしません。`overwrite_existing`、`skip_existing`、`update_existing` から選びます。")],
  similar=[("[`copy_file`](copy_file.md)", "ファイル 1 つだけをコピーする。動きが単純"),
           ("[`copy_options`](copy_options.md)", "この関数の動きを決めるフラグ"),
           ("[`copy_symlink`](copy_symlink.md)", "シンボリックリンクだけをコピーする")],
  memo=["ファイルもフォルダーもコピーする", "フォルダーの中身まで全部なら `recursive`", "既存のファイルの扱いは `copy_options` で決める"])

rewrite(F + 'remove_all.md',
  intro="""一時フォルダーを、中身ごと片付けたい。`remove` は空のフォルダーしか消せないので、中のファイルとサブフォルダーを、先に全部消す必要があります。それを 1 回の呼び出しでやるのが `std::filesystem::remove_all` です。

<strong>ファイルでもフォルダーでも、中身ごと再帰的に消し</strong>、消した数を返します。""",
  tips=["フォルダーは、中身（サブフォルダーを含む）ごと消す。ファイルなら、そのファイルだけ",
        "戻り値は、消したファイルとフォルダーの合計数。もともと無ければ 0",
        "存在しないことはエラーではない。後片付けに使いやすい",
        "危険な操作。パスが空やルートだと、意図しない範囲を消す"],
  details="""### remove_all {#remove_all}

<span class="ver ver-17">C++17</span>

```cpp
std::uintmax_t remove_all(const path& p);
std::uintmax_t remove_all(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 消すファイルまたはフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、<strong>消したものの数</strong>で、`p` 自身も数に入ります。中に 2 つのファイルがあるフォルダーなら 3 です。`p` が存在しなかったときは 0 を返し、エラーにはなりません。失敗したときは、例外（または `ec`）で、`error_code` の版では、戻り値は `static_cast<std::uintmax_t>(-1)` になります。

途中で失敗する場合があります。他のプロセスが開いているファイルや、権限のないファイルがあると、そこで止まり、それまでに消したぶんは戻りません。「全部消すか、何も消さないか」という保証はありません。

この関数の怖さは、<strong>パスを間違えると、広い範囲を消す</strong>ことです。変数が空文字列のまま `root / ""` で呼ぶと、`root` が丸ごと消えます。ユーザーの入力や設定ファイルから作ったパスは、消す前に、想定した場所の内側にあるかを確かめます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("work/sub");
  std::ofstream("work/a.txt") << "a";
  std::ofstream("work/sub/b.txt") << "b";

  // work, work/a.txt, work/sub, work/sub/b.txt の 4 つ
  std::uintmax_t n = fs::remove_all("work");
  std::println("消した数: {}", n);
  std::println("残っている: {}", fs::exists("work"));

  // もう無いので 0。エラーにはならない
  std::println("2 回目: {}", fs::remove_all("work"));
}""",
  out="""消した数: 4
残っている: false
2 回目: 0""",
  uses="""一時作業フォルダーの後片付け、ビルドや変換の出力フォルダーの掃除、アンインストールの処理で使います。起動時に、前回のクラッシュで残った作業フォルダーを消す、といった使い方もあります。

呼ぶ前に、`weakly_canonical` で正規化したパスが、自分の作業フォルダーの下にあるかを検査する習慣をつけます。パスの組み立てのバグで、ユーザーの Documents フォルダーが消える、といった事故を避けるためです。""",
  mistakes=[("空のパスや、ルートを渡して、広い範囲を消す", "消す前に、パスが空でないこと、想定した場所の内側にあることを確かめます。"),
            ("途中で失敗しても、全部消えたと思う", "開かれているファイルなどで止まります。戻り値と `ec` を確かめ、残りがないかを `exists` で見ます。")],
  similar=[("[`remove`](remove.md)", "ファイルか空のフォルダー 1 つだけを消す"),
           ("[`directory_iterator`](directory_iterator.md)", "消す前に中身を数える")],
  memo=["中身ごと再帰的に消す", "戻り値は消した数（`p` 自身を含む）", "パスの確認が命綱"])

rewrite(F + 'permissions.md',
  intro="""セーブ データを読み取り専用にして、誤った上書きを防ぎたい。スクリプトに実行権限を付けたい。ファイルの権限を変更するのが `std::filesystem::permissions` です。""",
  tips=["`permissions(パス, 権限, オプション)`。権限は [`perms`](perms.md) のビットの組み合わせ",
        "オプションで、置き換え（`replace`）、追加（`add`）、削除（`remove`）を選ぶ。省略は置き換え",
        "Windows では、読み取り専用かどうかだけが反映される",
        "シンボリックリンクは、既定で指し先を変える。リンク自体は `nofollow`"],
  details="""### permissions {#permissions}

<span class="ver ver-17">C++17</span>

```cpp
void permissions(const path& p, perms prms, perm_options opts = perm_options::replace);
void permissions(const path& p, perms prms, std::error_code& ec) noexcept;
void permissions(const path& p, perms prms, perm_options opts, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 権限を変えるファイルまたはフォルダー |
| `prms` | [`perms`](perms.md) | 設定するビット |
| `opts` | [`perm_options`](perm_options.md) | `replace`（全部を置き換え）、`add`（追加）、`remove`（削除）。`nofollow` を足せる |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

最も使うのは、`add` と `remove` です。`replace` は、渡したビットで権限をまるごと置き換えるので、書き込み権限を残したいのに、`prms` に入れ忘れると、読み取り専用になります。

<strong>Windows では、書き込みのビット 3 つ（`owner_write`、`group_write`、`others_write`）を全部外したときだけ、読み取り専用属性になります</strong>。1 つだけ外しても、変化しません。読み取り専用のファイルは、`remove` で消せないことがあるので、消す前に `add` で書き込みを戻します。

POSIX では、持ち主以外が権限を変更しようとすると、失敗します。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  using fs::perms;
  const perms all_write = perms::owner_write | perms::group_write | perms::others_write;

  std::ofstream("save.dat") << "x";

  // 書き込みを全部外して、読み取り専用にする
  fs::permissions("save.dat", all_write, fs::perm_options::remove);
  bool writable = (fs::status("save.dat").permissions() & perms::owner_write) != perms::none;
  std::println("書き込める: {}", writable);

  // 元に戻す
  fs::permissions("save.dat", all_write, fs::perm_options::add);
  writable = (fs::status("save.dat").permissions() & perms::owner_write) != perms::none;
  std::println("戻した後: {}", writable);
}""",
  out="""書き込める: false
戻した後: true""",
  uses="""完成したセーブ データを読み取り専用にして、誤って上書きしないようにする、MOD が配布データを書き換えないようにする、といった場面で使います。

バージョン管理から取り出したファイルが読み取り専用で、更新や削除ができない、というトラブルでも、`add` で書き込みを戻す処理が役に立ちます。""",
  mistakes=[("書き込みのビットを 1 つだけ外して、Windows で変化しない", "3 つとも外します。"),
            ("`replace` で権限をまるごと上書きして、意図しない権限になる", "一部だけ変えたいなら、`add` か `remove` を指定します。")],
  similar=[("[`perms`](perms.md)", "権限のビットの定義"),
           ("[`perm_options`](perm_options.md)", "この関数の動きを決めるフラグ"),
           ("[`status`](status.md)", "今の権限を調べる")],
  memo=["ファイルの権限を変更する", "一部だけ変えるなら `add` / `remove`", "Windows は書き込みビット 3 つが全部外れたときだけ読み取り専用"])

rewrite(F + 'perm_options.md',
  intro="""権限を変更するとき、「この権限だけを追加したい」「この権限だけを外したい」と、「全部をこれに置き換えたい」は、別の操作です。`std::filesystem::perm_options` は、[`permissions`](permissions.md) に、どちらの動きをするかを伝えるフラグです。""",
  tips=["`replace`（置き換え）、`add`（追加）、`remove`（削除）のどれか 1 つを選ぶ",
        "`nofollow` を足すと、シンボリックリンク自体の権限を変える",
        "`replace` は、指定しなかったビットを全部外す",
        "省略すると `replace`"],
  details="""### perm_options {#perm_options}

<span class="ver ver-17">C++17</span>

```cpp
enum class perm_options : unsigned {
  replace  = 0x1,
  add      = 0x2,
  remove   = 0x4,
  nofollow = 0x8
};
```

| 値 | 意味 |
| --- | --- |
| `replace` | 渡した `perms` で、権限をまるごと置き換える |
| `add` | 今の権限に、渡した `perms` のビットを足す |
| `remove` | 今の権限から、渡した `perms` のビットを外す |
| `nofollow` | シンボリックリンクをたどらず、リンク自体を対象にする |

`replace`、`add`、`remove` は、<strong>どれか 1 つだけ</strong>指定します。2 つ以上、または 0 個だと、`permissions` の動作は未定義です。省略したときの既定値は `replace` です。

`nofollow` は、これらのどれかと組み合わせて、`add | nofollow` のように使います。ただし、多くの環境では、リンク自体の権限を変更する方法がなく、無視されるか失敗します。

`replace` は便利ですが、渡したビット以外が全部消えます。`perms::owner_read` だけを渡して `replace` すると、書き込みも実行も外れ、読み取り専用で実行もできないファイルになります。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  using fs::perms;
  const perms w = perms::owner_write | perms::group_write | perms::others_write;
  std::ofstream("a.dat") << "x";

  auto can_write = [] { return (fs::status("a.dat").permissions() & perms::owner_write) != perms::none; };

  fs::permissions("a.dat", w, fs::perm_options::remove);
  std::println("remove の後: {}", can_write());

  fs::permissions("a.dat", w, fs::perm_options::add);
  std::println("add の後: {}", can_write());

  // replace: 渡したビット以外は全部外れる（読み取りだけにする）
  fs::permissions("a.dat", perms::owner_read | perms::group_read | perms::others_read, fs::perm_options::replace);
  std::println("replace の後: {}", can_write());

  fs::permissions("a.dat", w, fs::perm_options::add);   // 消せるように戻す
}""",
  out="""remove の後: false
add の後: true
replace の後: false""",
  uses="""`permissions` を呼ぶときに、ほぼ毎回指定します。読み取り専用にする（`remove` で書き込みを外す）、元に戻す（`add` で書き込みを足す）、という 2 つの操作が、ゲームのツール類で最もよく使われる組み合わせです。""",
  mistakes=[("`replace` のつもりで、`add` を使って権限が残る", "足すだけなので、既存のビットは残ります。"),
            ("`replace` を省略して、意図せず全部の権限が置き換わる", "既定は `replace` です。一部だけ変えたいなら、`add` か `remove` を明示します。")],
  similar=[("[`permissions`](permissions.md)", "この列挙型を受け取る関数"),
           ("[`perms`](perms.md)", "権限のビットの定義")],
  memo=["権限の変更の仕方を選ぶフラグ", "`replace` `add` `remove` のどれか 1 つ", "省略は `replace`"])

rewrite(F + 'create_symlink.md',
  intro="""別の場所にあるファイルを、ゲーム フォルダーの中にあるように見せたい。コピーするとディスクを使い、元との差も出ます。シンボリックリンクなら、「あのファイルの場所」という参照だけを、小さなファイルとして置けます。

`std::filesystem::create_symlink` は、<strong>ファイルを指すシンボリックリンク</strong>を作ります。""",
  tips=["`create_symlink(指し先, リンクの名前)`。引数の順は、「指し先」が先",
        "指し先が存在しなくても作れる（ぶら下がったリンク）",
        "フォルダーを指すリンクは、`create_directory_symlink` を使う（Windows で必要）",
        "Windows では、開発者モードか管理者権限が要る"],
  details="""### create_symlink {#create_symlink}

<span class="ver ver-17">C++17</span>

```cpp
void create_symlink(const path& target, const path& link);
void create_symlink(const path& target, const path& link, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | `const path&` | リンクが指す先。書いたとおりの文字列が保存される |
| `link` | `const path&` | 作るリンクの名前。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`target` が相対パスのとき、リンクを開く時点で、<strong>リンクのあるフォルダーを基準に</strong>解釈されます。作成時のカレント ディレクトリではないので、`create_symlink("data/a.txt", "link")` は、`link` の隣にある `data/a.txt` を指します。意図と違う場所にならないよう、絶対パスで作るか、リンクの位置から見た相対パスで書きます。

[`create_hard_link`](create_hard_link.md) とは違い、リンクは「名前を覚えているだけ」です。指し先を消したり、動かしたりすると、リンクは壊れます（リンク切れ）。

Windows では、シンボリックリンクを作る権限が要ります。権限がないと失敗するので、`error_code` 版を使うか、例外を処理します。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("real.txt") << "x";

  std::error_code ec;
  fs::create_symlink("real.txt", "link.txt", ec);

  // 作れたか、権限がなくて作れなかったか。どちらの環境でも、結果は整合している
  std::println("結果が整合している: {}", static_cast<bool>(ec) == !fs::is_symlink("link.txt"));
}""",
  out="結果が整合している: true",
  uses="""開発環境で、共通のアセットを複数のプロジェクトから参照するときに使います。ツールが作る生成物を、ゲームから見える場所にリンクする、という構成です。

製品版の配布物には含めません。権限の問題と、ZIP などの展開でリンクが壊れる問題があるためです。""",
  mistakes=[("相対パスのリンクが、意図と違う場所を指す", "リンクのあるフォルダーを基準に解釈されます。絶対パスにするか、基準に合わせて書きます。"),
            ("フォルダーを指すのに `create_symlink` を使う", "Windows では、フォルダー用は `create_directory_symlink` です。"),
            ("権限がなく失敗する", "開発者モードを有効にするか、`error_code` 版で失敗を処理して、コピーで代用します。")],
  similar=[("[`create_directory_symlink`](create_directory_symlink.md)", "フォルダーを指すリンク"),
           ("[`create_hard_link`](create_hard_link.md)", "実体を共有する別名"),
           ("[`read_symlink`](read_symlink.md)", "リンクの指し先を読む")],
  memo=["ファイルを指すシンボリックリンクを作る", "相対パスはリンクの位置が基準", "Windows は権限が必要"])

# ---- cstdio の定数・ストリーム ----

rewrite(C + 'stdout.md',
  intro="""`printf` や `puts` が出力する先は、どこでしょう。画面（コンソール）です。その出力先を表しているのが、`stdout`（標準出力）という、あらかじめ開かれている `FILE*` です。""",
  tips=["プログラムの開始時に、自動で開かれている。`fopen` も `fclose` も要らない",
        "`printf(...)` は `fprintf(stdout, ...)` と同じ",
        "端末につながっているときは行バッファー、ファイルにリダイレクトされているときはフル バッファー",
        "ログのようなエラー出力は、`stdout` ではなく `stderr` に出す"],
  details="""### stdout {#stdout}

```cpp
extern std::FILE* stdout;   // 実際はマクロの場合もある
```

`stdout` は、`printf`、`puts`、`putchar`、`std::print`（引数にファイルを取らない版）の出力先です。`fprintf(stdout, ...)` と書くと、`printf` と同じ意味になります。

シェルのリダイレクト（`game.exe > out.txt`）で、`stdout` はファイルに向きます。このとき、バッファーの方式が変わります。端末なら行ごとに書き出されますが、ファイルへのリダイレクトでは、バッファーが一杯になるまで溜まります。クラッシュすると、ファイルに最後の部分が入らないことがあります。

Windows の GUI アプリ（`WinMain` で始まるもの）では、コンソールがつながっていないので、`stdout` に出しても、どこにも表示されません。デバッグ出力は、`OutputDebugString` を使うか、`AllocConsole` でコンソールを作ります。

`stdout` を閉じてはいけません（`fclose(stdout)` はできるが、以降の出力が失われる）。出力先を変えるには、[`freopen`](freopen.md) を使います。""",
  code="""#include <cstdio>

int main() {
  std::printf("printf の出力\\n");
  std::fprintf(stdout, "fprintf(stdout) でも同じ\\n");
  std::fputs("fputs(..., stdout)\\n", stdout);
}""",
  out="""printf の出力
fprintf(stdout) でも同じ
fputs(..., stdout)""",
  uses="""通常の出力、つまり「プログラムの結果」を書き出す先です。ツール類では、結果を `stdout` に、診断やログを `stderr` に分けると、`> result.txt` でリダイレクトしたときに、結果だけをファイルに保存できます。

ゲームでは、デバッグ用の `printf` がこの先に出ます。製品版では、出力先を決めて、ログ ファイルに向けます（`freopen`）。""",
  mistakes=[("GUI アプリで `printf` を書いて、何も出ない", "コンソールがありません。`OutputDebugString` や `AllocConsole` を使います。"),
            ("リダイレクトしたとき、クラッシュ直前の出力が残らない", "フル バッファーのためです。`fflush(stdout)` を呼ぶか、`setvbuf` でバッファーを切ります。")],
  similar=[("[`stderr`](stderr.md)", "標準エラー出力。バッファーなし"),
           ("[`stdin`](stdin.md)", "標準入力"),
           ("[`freopen`](freopen.md)", "出力先を変える")],
  memo=["標準出力の `FILE*`", "`printf` の出力先", "結果は `stdout`、ログは `stderr`"])

rewrite(C + 'stderr.md',
  intro="""プログラムの結果と、エラーのメッセージが、同じ画面に混ざって出る。それでも、結果だけをファイルに保存したいときがあります。エラーを別の流れに分けるために、`stderr`（標準エラー出力）が用意されています。""",
  tips=["`stdout` とは別の出力先。既定ではバッファーなしで、書くとすぐに出る",
        "リダイレクト（`> out.txt`）しても、`stderr` は画面に出る（`2> err.txt` で別に向けられる）",
        "エラー、警告、診断の出力に使う",
        "クラッシュ直前のメッセージも、バッファーに残らずに出る"],
  details="""### stderr {#stderr}

```cpp
extern std::FILE* stderr;   // 実際はマクロの場合もある
```

`fprintf(stderr, "...")` のように使います。`stdout` と違って、既定で<strong>バッファーされません</strong>。書いた内容がすぐに出力されるので、プログラムが直後にクラッシュしても、メッセージが失われません。

シェルで `game.exe > result.txt` とすると、`stdout` だけがファイルへ向き、`stderr` は画面に出続けます。結果とエラーを分けて扱えるのが、利点です。`2> errors.txt` とすれば、エラーだけをファイルにも向けられます。

C++ には `std::cerr`（バッファーなし）と `std::clog`（バッファーあり）がありますが、C の `stderr` と同じ出力先に結び付いています（既定では同期されているため、混ぜて使っても順序が崩れません）。

Windows の GUI アプリでは、`stdout` と同様に、コンソールがないので、どこにも出ません。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::println("結果: 42");                                  // 標準出力
  std::fprintf(stderr, "警告: 設定ファイルがありません\\n");   // 標準エラー出力。別の流れ
}""",
  out="結果: 42",
  uses="""ツールの結果（`stdout`）と、診断メッセージ（`stderr`）を分けるために使います。ゲームでは、致命的なエラーを `stderr` に出してから終了することで、リダイレクト先のファイルにも、画面にも、メッセージが残ります。

アサートや、例外のハンドラーでの最後の出力にも向いています。バッファーを通らないので、書いた直後にクラッシュしても失われません。""",
  mistakes=[("エラー メッセージを `stdout` に出して、結果と混ざる", "リダイレクトした結果のファイルに、エラーが混入します。`stderr` に出します。"),
            ("GUI アプリで出して、見えない", "コンソールがありません。ログ ファイルか、`OutputDebugString` を使います。")],
  similar=[("[`stdout`](stdout.md)", "標準出力"),
           ("[`perror`](perror.md)", "`errno` の説明を `stderr` に出す"),
           ("`std::cerr`", "C++ のストリームでの標準エラー出力")],
  memo=["標準エラー出力の `FILE*`", "既定でバッファーなし", "エラーと診断は `stderr`"])

rewrite(C + 'stdin.md',
  intro="""キーボードから入力を受け取る関数 `scanf` や `getchar` は、どこから読んでいるのでしょう。その読み込み元が、`stdin`（標準入力）です。プログラムの開始時に、自動で開かれています。""",
  tips=["`scanf(...)` は `fscanf(stdin, ...)` と、`getchar()` は `fgetc(stdin)` と同じ",
        "端末では、キー入力が行単位でバッファーされる。Enter まで確定しない",
        "リダイレクト（`< input.txt`）やパイプで、ファイルや他のプログラムの出力を入力にできる",
        "`fflush(stdin)` で入力を捨てるのは、標準では未定義"],
  details="""### stdin {#stdin}

```cpp
extern std::FILE* stdin;   // 実際はマクロの場合もある
```

`stdin` は、`scanf`、`gets` 系、`getchar` の読み込み元です。`fgets(buf, n, stdin)` は、標準入力から 1 行を読む、定番の書き方です。

シェルで `game.exe < input.txt` とすると、`stdin` がファイルになります。自動テストで、入力をファイルから流し込む、ツール同士をパイプでつなぐ、といった使い方ができます。入力が尽きると、`fgets` などは `EOF` / `nullptr` を返します。

端末から読むときは、1 行入力されるまで待ちます。キーを押した瞬間に反応するゲームの操作には、向きません。Windows なら `_getch`、ゲーム全体では、ウィンドウ メッセージやゲームパッド API を使います。

入力の読み残しを消す目的で `fflush(stdin)` を書く例がありますが、標準では未定義動作です。読み捨てるなら、`getchar` を改行まで繰り返します。""",
  code="""#include <cstdio>
#include <print>

int main() {
  char line[64];
  // 入力が空だと nullptr が返る
  if (std::fgets(line, sizeof(line), stdin)) {
    std::print("入力: {}", line);
  } else {
    std::println("入力なし");
  }
}""",
  out="入力なし",
  uses="""コンソールの簡単なツールや、パイプでつなぐフィルターで使います。ゲーム本編の入力は、ここを使いません。

ツール同士を組み合わせる開発環境（ビルド スクリプト、アセット変換）では、`stdin` から読んで `stdout` に出す、というフィルター型のプログラムが便利です。""",
  mistakes=[("リアルタイム入力に使って、Enter まで反応しない", "行バッファリングのためです。ゲームの入力は別の仕組みで受けます。"),
            ("`fflush(stdin)` で入力を捨てる", "標準では未定義です。`getchar` で読み捨てます。")],
  similar=[("[`stdout`](stdout.md)", "標準出力"),
           ("[`getchar`](getchar.md)", "`stdin` から 1 文字"),
           ("`std::cin`", "C++ のストリームでの標準入力")],
  memo=["標準入力の `FILE*`", "`scanf` や `getchar` の読み込み元", "`fflush(stdin)` は使わない"])

rewrite(C + 'eof.md',
  intro="""読み込み関数が「もう読めない」ことを、戻り値で伝えたい。ところが `fgetc` の戻り値は、`0` から `255` の文字の値です。どの値も文字として使われうるので、終わりを表す値に、文字の値は使えません。そこで、文字の範囲に入らない負の値を、`EOF` として定めています。""",
  tips=["`EOF` は負の整数のマクロ。ふつうは `-1`",
        "`fgetc` や `getchar` は、終わりかエラーのときに、これを返す",
        "戻り値を受ける変数は `char` ではなく `int`。`char` だと、`0xFF` の文字と区別できない",
        "ファイルの終わりかエラーかは、`feof` と `ferror` で見分ける"],
  details="""### EOF {#EOF}

```cpp
#define EOF (-1)   // 値は処理系定義の、負の整数定数
```

`EOF` の名前は End Of File ですが、読み込みのエラーでも返されます。「もう文字を返せない」ことを表す印と考えます。

値は規格で「負の整数定数」としか決まっておらず、ほとんどの環境で `-1` です。値に頼らず、名前で比較します。

`fgetc` が `0` から `255` の値を返せるように、戻り値は `int` です。`char` で受けると、符号つき `char` の環境では `0xFF` が `-1` に見えて、`EOF` と区別できなくなります。ファイルの途中の 1 バイトで、読み込みが止まってしまいます。

出力関数（`fputc`、`fputs` など）は、失敗したときに `EOF` を返します。入力の終わりという意味ではなく、「失敗」を表す値として使われます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("empty.txt", "w");
  std::fclose(f);

  f = std::fopen("empty.txt", "r");
  int c = std::fgetc(f);              // 空のファイルなので EOF
  std::println("EOF が返った: {}", c == EOF);
  std::println("EOF は負の値: {}", EOF < 0);
  std::println("feof: {}", std::feof(f) != 0);
  std::fclose(f);
}""",
  out="""EOF が返った: true
EOF は負の値: true
feof: true""",
  uses="""1 文字ずつ読むループの終了条件に使います。`while ((c = fgetc(f)) != EOF)` が、定番の書き方です。ループを抜けたあとで、`feof` と `ferror` を調べて、終わりなのかエラーなのかを区別します。

`scanf` 系の関数も、入力が終わった（1 つも読めなかった）とき `EOF` を返します。""",
  mistakes=[("`char c = fgetc(f)` と書いて、`0xFF` で止まる", "`int` で受けます。"),
            ("`EOF` の値が `-1` だと決めつけて、数値で比較する", "名前で比較します。")],
  similar=[("[`feof`](feof.md)", "終わりの印を調べる"),
           ("[`ferror`](ferror.md)", "エラーの印を調べる"),
           ("[`fgetc`](fgetc.md)", "`EOF` を返す代表的な関数")],
  memo=["終わりやエラーを表す負の値", "戻り値は `int` で受ける", "名前で比較する"])

rewrite(C + 'bufsiz.md',
  intro="""標準ライブラリがファイルの入出力で使う、バッファーの大きさ。その既定の大きさを表すのが `BUFSIZ` です。自分でバッファーを用意して渡す `setbuf` では、この大きさ以上の配列が必要になります。""",
  tips=["`BUFSIZ` は整数定数のマクロ。環境ごとに値が違う（MSVC は 512、glibc は 8192 など）",
        "`setbuf(ファイル, 配列)` に渡す配列は、`BUFSIZ` 以上の大きさにする",
        "`setvbuf` では大きさを自由に指定できるので、`BUFSIZ` に縛られない",
        "最低でも 256 以上であることが、規格で決まっている"],
  details="""### BUFSIZ {#BUFSIZ}

```cpp
#define BUFSIZ /* 実装定義の整数定数式 */
```

標準ライブラリが、入出力のバッファーに使う標準の大きさです。規格が保証するのは、256 以上であることだけで、実際の値は実装しだいです。

`setbuf` は大きさを引数に取らず、`BUFSIZ` の大きさの配列を渡す決まりです。`char buf[BUFSIZ];` と宣言して渡します。

実際のバッファーの大きさとして、`BUFSIZ` が最適とは限りません。大量のデータを読み書きするなら、64 KB のような大きなバッファーを `setvbuf` で渡すと、システム呼び出しの回数が減って速くなることがあります。

「読み書きを 1 回の呼び出しで処理する単位」として使うこともできます。一時的な読み込みのバッファーに `char buf[BUFSIZ]` と書くのは、C の定番の書き方です。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::println("256 以上: {}", BUFSIZ >= 256);

  // setbuf に渡す配列は BUFSIZ 以上の大きさ
  static char buffer[BUFSIZ];
  std::FILE* f = std::fopen("buf.txt", "w");
  std::setbuf(f, buffer);
  std::fputs("hello", f);
  std::fclose(f);               // 閉じる前に buffer を破棄しない
  std::println("書けた");
}""",
  out="""256 以上: true
書けた""",
  uses="""`setbuf` と組み合わせるほか、ファイルを一定の単位で読み書きするときの、バッファーの大きさの目安に使います。ゲームでは、読み込みの速度が重要なら、`BUFSIZ` ではなく、数十 KB から数 MB の単位を自分で決めます。""",
  mistakes=[("`BUFSIZ` が固定の値だと思って、他の場所に書き込む", "環境によって違います。名前で使います。"),
            ("ファイルを閉じる前に、渡した配列を破棄する", "バッファーは閉じるまで使われます。`static` にするなど、寿命を長くします。")],
  similar=[("[`setbuf`](setbuf.md)", "この大きさのバッファーを渡す"),
           ("[`setvbuf`](setvbuf.md)", "大きさを自由に決められる")],
  memo=["既定のバッファーの大きさ", "環境ごとに値が違う", "`setbuf` の配列は `BUFSIZ` 以上"])

rewrite(C + 'file.md',
  intro="""ファイルを開くと、`FILE*` というポインターが返ってきます。その `FILE` は、ファイルの位置、バッファー、終わりやエラーの印など、入出力に必要な状態をまとめた型です。中身は処理系が決めていて、使う側は見えません。""",
  tips=["`std::FILE` は、中身の見えない型。`FILE*` として、関数に渡すだけ",
        "自分で `FILE` を作ったり、コピーしたりしてはいけない。`fopen` が返したポインターだけを使う",
        "ファイルを開いたら `fclose` で閉じる。`unique_ptr` と組み合わせると、閉じ忘れを防げる",
        "同じ `FILE*` を、複数のスレッドから同時に使うときは、排他が要る"],
  details="""### FILE {#FILE}

```cpp
using FILE = /* 実装定義 */;
```

`FILE` の中には、ファイルを表す OS のハンドル、読み書きの位置、バッファーの先頭、終わりとエラーの印などが入っています。構造が処理系ごとに違うので、`sizeof(FILE)` に意味はなく、コピーもできません。

`FILE*` を例外安全に扱うには、`std::unique_ptr` に削除関数を渡します。

```cpp
std::unique_ptr<std::FILE, decltype(&std::fclose)> f(std::fopen("a.txt", "rb"), &std::fclose);
```

こう書くと、関数を抜けるときに、例外が起きても自動で `fclose` されます。`f.get()` で、C の関数に渡せます。

C の標準ライブラリの関数は、`FILE*` を受け取るので、C のライブラリ（zlib、libpng など）とつなぐ共通の形になっています。`FILE*` から C++ のストリームを作る標準の方法はなく、逆もありません。""",
  code="""#include <cstdio>
#include <memory>
#include <print>

int main() {
  // 例外が起きても閉じ忘れない書き方
  std::unique_ptr<std::FILE, decltype(&std::fclose)> f(std::fopen("auto.txt", "w"), &std::fclose);
  if (!f) return 1;

  std::fputs("auto close", f.get());
  std::println("書いた");
}   // ここで fclose が呼ばれる""",
  out="書いた",
  uses="""C のライブラリとの連携で、`FILE*` を受け渡す場面で出てきます。C++ のコードでは、`std::ofstream` と `std::ifstream` を使うほうが自然ですが、`FILE*` を要求するライブラリには、`unique_ptr` で包んで渡します。""",
  mistakes=[("`FILE` を値として宣言・コピーする", "`FILE` は不完全な型として扱います。`FILE*` だけを使います。"),
            ("開いた `FILE*` を閉じ忘れる", "`unique_ptr` で包み、閉じ忘れを防ぎます。")],
  similar=[("[`fopen`](fopen.md)", "`FILE*` を得る"),
           ("[`fclose`](fclose.md)", "`FILE*` を閉じる"),
           ("`std::ofstream`", "C++ のストリーム")],
  memo=["ファイルの状態をまとめた型", "`FILE*` として受け渡す", "`unique_ptr` で閉じ忘れを防ぐ"])

for name, base, what in (('seek_set', 'SEEK_SET', '先頭'), ('seek_cur', 'SEEK_CUR', '今の位置'), ('seek_end', 'SEEK_END', '末尾')):
    pass

rewrite(C + 'seek_set.md',
  intro="""`fseek` に位置を伝えるとき、「何バイト動かすか」だけでは足りません。先頭から数えるのか、今の位置から数えるのか。その基準を選ぶ 3 つの定数のうち、先頭を基準にするのが `SEEK_SET` です。""",
  tips=["`fseek(f, n, SEEK_SET)` で、先頭から `n` バイトの位置へ移る",
        "`n` は 0 以上。負の値は失敗する",
        "`fseek(f, 0, SEEK_SET)` は先頭へ戻る。`rewind` と似ている",
        "値そのものは環境定義。名前で使う"],
  details="""### SEEK_SET {#SEEK_SET}

```cpp
#define SEEK_SET /* 整数定数 */
```

`fseek` の第 3 引数 `origin` に渡し、位置の基準を「ファイルの先頭」にします。`offset` が、先頭からのバイト数です。

パックファイルの目次に「アセット A は 先頭から 1024 バイト目」と記録してあるなら、読み込むときに `fseek(f, 1024, SEEK_SET)` で飛びます。位置が絶対的な値で表されるので、ほとんどの場面で、これを使います。

テキスト モードで開いたファイルでは、`SEEK_SET` と共に使える `offset` は、`ftell` が返した値と 0 だけです。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("abc.txt", "w");
  std::fputs("ABCDEF", out);
  std::fclose(out);

  std::FILE* f = std::fopen("abc.txt", "rb");
  std::fseek(f, 3, SEEK_SET);       // 先頭から 3 バイト目へ
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fseek(f, 0, SEEK_SET);       // 先頭へ戻る
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}""",
  out="""D
A""",
  uses="""パックファイルから、目次で指定された位置のアセットを読み込むときに使います。アセットの位置は絶対的な値なので、基準は先頭です。""",
  mistakes=[("負の `offset` を渡して失敗する", "先頭より前には行けません。末尾からの相対位置なら `SEEK_END` です。")],
  similar=[("[`SEEK_CUR`](seek_cur.md)", "今の位置を基準にする"),
           ("[`SEEK_END`](seek_end.md)", "末尾を基準にする"),
           ("[`fseek`](fseek.md)", "これらを受け取る関数")],
  memo=["先頭を基準にする", "絶対的な位置へ飛ぶ", "`offset` は 0 以上"])

rewrite(C + 'seek_cur.md',
  intro="""`fseek` の基準のうち、<strong>今の位置</strong>から数えるのが `SEEK_CUR` です。「今の場所から 4 バイト飛ばしたい」「1 バイト戻りたい」といった、相対的な移動に使います。""",
  tips=["`fseek(f, n, SEEK_CUR)` で、今の位置から `n` バイト動く。負の値で戻る",
        "`fseek(f, 0, SEEK_CUR)` は、位置を変えずに、読み書きの切り替えをするときに使う",
        "テキスト モードでは、`offset` は 0 のときだけ使える",
        "値そのものは環境定義。名前で使う"],
  details="""### SEEK_CUR {#SEEK_CUR}

```cpp
#define SEEK_CUR /* 整数定数 */
```

位置の基準を「今の位置」にします。`offset` が正なら先へ、負なら手前へ動きます。

構造のあるバイナリ ファイルを順に読むとき、不要な部分を読み飛ばす用途で使います。たとえば、サイズ 16 バイトのヘッダーの後ろに、使わない 8 バイトのパディングがあるなら、`fseek(f, 8, SEEK_CUR)` で飛ばします。

読み書き兼用で開いたファイルで、書き込みから読み込みに切り替える間には、`fseek` を挟む決まりがあります。位置を変えたくないときは、`fseek(f, 0, SEEK_CUR)` が、その役割を果たします。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("abc.txt", "w");
  std::fputs("ABCDEF", out);
  std::fclose(out);

  std::FILE* f = std::fopen("abc.txt", "rb");
  std::fgetc(f);                    // A を読む
  std::fseek(f, 2, SEEK_CUR);       // B, C を飛ばす
  std::println("{}", static_cast<char>(std::fgetc(f)));   // D
  std::fseek(f, -2, SEEK_CUR);      // 2 つ戻る（C へ）
  std::println("{}", static_cast<char>(std::fgetc(f)));   // C
  std::fclose(f);
}""",
  out="""D
C""",
  uses="""バイナリ形式の読み込みで、不要な領域を読み飛ばすときに使います。読んだ量に関係なく、「ここから N バイト」と相対的に指定できるので、レコードの長さが変わる形式の解析で重宝します。""",
  mistakes=[("テキスト モードで 0 以外の `offset` を使う", "テキスト モードでは、`\\r\\n` の変換のため、バイト数の計算が合いません。バイナリ モードで使います。")],
  similar=[("[`SEEK_SET`](seek_set.md)", "先頭を基準にする"),
           ("[`SEEK_END`](seek_end.md)", "末尾を基準にする"),
           ("[`fseek`](fseek.md)", "これらを受け取る関数")],
  memo=["今の位置を基準にする", "負の値で戻れる", "テキスト モードでは 0 だけ"])

rewrite(C + 'seek_end.md',
  intro="""ファイルの大きさを知りたい。末尾の数バイトだけを読みたい。どちらも、基準が<strong>末尾</strong>だと簡単です。そのための `fseek` の基準が `SEEK_END` です。""",
  tips=["`fseek(f, 0, SEEK_END)` で、末尾へ移る。続けて `ftell` を呼ぶと、ファイルの大きさ",
        "`fseek(f, -n, SEEK_END)` で、末尾から `n` バイト手前へ移る",
        "バイナリの `SEEK_END` は、規格では保証されない（実際には、ほぼ動く）",
        "C++17 以降は、大きさなら `std::filesystem::file_size` が簡単"],
  details="""### SEEK_END {#SEEK_END}

```cpp
#define SEEK_END /* 整数定数 */
```

位置の基準を「ファイルの末尾」にします。`offset` が 0 なら末尾そのもの、負の値なら末尾から手前へ戻った位置です。

ファイルの大きさを調べる、古くからの定番手順は次のとおりです。

```cpp
std::fseek(f, 0, SEEK_END);
long size = std::ftell(f);
std::rewind(f);
```

末尾の数バイトが特別な意味を持つ形式（ZIP の末尾の目次など）を読むときにも使います。末尾から決まった長さだけ手前に飛んで、そこから読みます。

規格上、バイナリ ストリームでの `SEEK_END` の動作は、意味のある実装を保証していません（ファイルの末尾に余計な 0 が付く古いシステムを考慮したため）。現代の環境では、問題なく動きます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("abc.txt", "w");
  std::fputs("ABCDEF", out);
  std::fclose(out);

  std::FILE* f = std::fopen("abc.txt", "rb");
  std::fseek(f, 0, SEEK_END);
  std::println("大きさ: {}", std::ftell(f));

  std::fseek(f, -2, SEEK_END);      // 末尾から 2 つ手前
  std::println("末尾から 2 つ手前: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}""",
  out="""大きさ: 6
末尾から 2 つ手前: E""",
  uses="""ZIP のように、ファイルの末尾に目次を持つ形式を読むときに使います。末尾から固定長だけ戻って、目次の位置を読み取り、そこへ飛びます。

大きさを知るためだけなら、`std::filesystem::file_size` が簡単で、位置も動かしません。""",
  mistakes=[("大きさを調べたあと、先頭に戻すのを忘れる", "`rewind` か `fseek(f, 0, SEEK_SET)` で戻します。"),
            ("2 GB を超えるファイルで、`long` が足りない", "`_fseeki64` や `_ftelli64` を使います。")],
  similar=[("[`SEEK_SET`](seek_set.md)", "先頭を基準にする"),
           ("[`SEEK_CUR`](seek_cur.md)", "今の位置を基準にする"),
           ("[`file_size`](../filesystem/file_size.md)", "大きさだけを知るなら")],
  memo=["末尾を基準にする", "大きさは `SEEK_END` と `ftell`", "戻すのを忘れない"])

for name, desc in (('vprintf', 'stdout'),):
    pass

rewrite(C + 'vprintf.md',
  intro="""自作のログ関数 `Log("HP: %d", hp)` を作りたい。引数の数が決まっていない（可変個引数）関数の中で、受け取った引数をそのまま `printf` に渡したい。ところが、`printf(fmt, ...)` の `...` を、別の関数に転送する方法はありません。

そのために、可変個引数を `va_list` という 1 つの値にまとめて渡す、`std::vprintf` があります。""",
  tips=["`vprintf(書式, va_list)`。`printf` の可変個引数を、`va_list` に置き換えた版",
        "自作のログ関数で、受け取った `...` を、`va_start` で `va_list` にして渡す",
        "使ったあとは `va_end` を呼ぶ",
        "戻り値は、書いた文字数。失敗は負の値"],
  details="""### std::vprintf {#vprintf}

```cpp
int vprintf(const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び。`va_start` で作る |

自作のログ関数は、次の形になります。

```cpp
void Log(const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);      // fmt の次の引数から
  std::vprintf(fmt, args);
  va_end(args);
}
```

`va_start` は、最後の固定引数（ここでは `fmt`）を渡します。`va_end` を忘れると、環境によってはメモリがリークします。

`va_list` は、一度 `vprintf` に渡すと、中身が壊れる場合があります。同じ引数で 2 回出力したいときは、`va_copy` でコピーを作ってから使います。

書式と値の型が合わないと、未定義動作になる点は、`printf` と同じです。GCC / Clang の `__attribute__((format(printf, 1, 2)))` を付けると、自作のログ関数にも書式のチェックが効きます。C++20 以降なら `std::format` を使うと、この問題はコンパイル時に検出されます。""",
  code="""#include <cstdarg>
#include <cstdio>

void Log(const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vprintf(fmt, args);   // 受け取った ... を、そのまま渡す
  va_end(args);
}

int main() {
  Log("HP: %d / %d\\n", 85, 120);
  Log("名前: %s\\n", "hero");
}""",
  out="""HP: 85 / 120
名前: hero""",
  uses="""自作のログ関数やデバッグ出力の関数で、`printf` と同じ書き方を提供するときに使います。ログ レベルや時刻の接頭辞を付けたい場合も、この形でラップします。

C++20 以降では、`std::format` / `std::vformat` を使った、型安全なログ関数のほうが、書式のミスを防げます。C のライブラリとの境界など、`va_list` が必要な場面で使います。""",
  mistakes=[("`va_end` を忘れる", "必ず対にして呼びます。"),
            ("`va_list` を 2 回使って、壊れた値が出る", "`va_copy` でコピーしてから使います。"),
            ("ユーザー入力を書式にして渡す", "`Log(\"%s\", input)` のように、値として渡します。")],
  similar=[("[`vfprintf`](vfprintf.md)", "出力先を選べる"),
           ("[`vsnprintf`](vsnprintf.md)", "文字配列に、大きさを指定して書く"),
           ("[`printf`](printf.md)", "可変個引数のまま受け取る")],
  memo=["`va_list` を受け取る `printf`", "自作のログ関数で使う", "`va_start` と `va_end` を対にする"])

rewrite(C + 'vfprintf.md',
  intro="""自作のログ関数で、出力先のファイルを呼び出し側が選べるようにしたい。`vprintf` は標準出力に固定ですが、<strong>出力先を指定でき、可変個引数を `va_list` で受け取る</strong>のが `std::vfprintf` です。""",
  tips=["`vfprintf(ファイル, 書式, va_list)`。`fprintf` の可変個引数を `va_list` にした版",
        "`va_start` と `va_end` を対にして使う",
        "戻り値は、書いた文字数。失敗は負の値",
        "ログ ファイルへの出力を包む関数で使う"],
  details="""### std::vfprintf {#vfprintf}

```cpp
int vfprintf(std::FILE* stream, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 出力先 |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び |

[`vprintf`](vprintf.md) の出力先を選べる版です。自作のログ関数で、`stdout` や `stderr`、ログ ファイルへ振り分けるときに使います。

```cpp
void LogTo(std::FILE* out, const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vfprintf(out, fmt, args);
  va_end(args);
}
```

`va_list` を使い回す際の注意は、`vprintf` と同じです。複数の出力先に同じ内容を書くなら、`va_copy` でコピーします。""",
  code="""#include <cstdarg>
#include <cstdio>

void LogTo(std::FILE* out, const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vfprintf(out, fmt, args);
  va_end(args);
}

int main() {
  LogTo(stdout, "level=%d name=%s\\n", 3, "cave");
}""",
  out="level=3 name=cave",
  uses="""ログの出力先（コンソール、ファイル、`stderr`）を切り替えられるロガーで使います。レベルごとに出力先を変える、という設計の中心になる関数です。""",
  mistakes=[("`va_end` を忘れる", "必ず対にします。"),
            ("2 つの出力先に、同じ `va_list` を渡して壊れる", "`va_copy` で複製します。")],
  similar=[("[`vprintf`](vprintf.md)", "標準出力に固定"),
           ("[`fprintf`](fprintf.md)", "可変個引数のまま受け取る"),
           ("[`vsnprintf`](vsnprintf.md)", "文字配列に書く")],
  memo=["出力先を選べる `vprintf`", "ログ関数で使う", "`va_copy` で複数の出力先"])

rewrite(C + 'vsprintf.md',
  intro="""自作の関数で、書式つきの文字列を作って返したい。`sprintf` の可変個引数版が `std::vsprintf` ですが、`sprintf` と同じく、<strong>書き込み先の大きさを確かめない</strong>ため、バッファーを溢れさせる危険があります。""",
  tips=["`vsprintf(バッファー, 書式, va_list)`。大きさを指定できない",
        "溢れると、メモリを破壊する。新しいコードでは使わない",
        "代わりに `vsnprintf` を使う",
        "戻り値は、書いた文字数（終端を除く）"],
  details="""### std::vsprintf {#vsprintf}

```cpp
int vsprintf(char* buffer, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 結果を入れる配列 |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び |

[`sprintf`](sprintf.md) の可変個引数を `va_list` にした版で、同じ危険があります。出力の長さは、書式と値によって実行時に決まるので、固定の大きさの配列では、足りなくなる可能性があります。

[`vsnprintf`](vsnprintf.md) なら、バッファーの大きさを渡せて、溢れが起きません。さらに、戻り値が「書けたはずの長さ」なので、足りなかったときに、必要な大きさが分かります。

MSVC は警告 C4996 を出します。警告を無効にするのではなく、`vsnprintf` に置き換えます。""",
  code="""#include <cstdarg>
#include <cstdio>
#include <print>

void Format(char* out, std::size_t size, const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vsnprintf(out, size, fmt, args);   // 安全な版を使う
  va_end(args);
}

int main() {
  char buf[32];
  Format(buf, sizeof(buf), "Player_%02d.png", 7);
  std::println("{}", buf);
}""",
  out="Player_07.png",
  uses="""新しいコードでは使いません。古い C のコードを移植するときに出てきたら、`vsnprintf` に置き換えます。""",
  mistakes=[("バッファーが足りず、メモリを壊す", "`vsnprintf` を使います。")],
  similar=[("[`vsnprintf`](vsnprintf.md)", "大きさを指定する安全な版"),
           ("[`sprintf`](sprintf.md)", "可変個引数のまま受け取る")],
  memo=["`va_list` を受け取る `sprintf`", "大きさを指定できず危険", "`vsnprintf` を使う"])

rewrite(C + 'vsnprintf.md',
  intro="""自作のログ関数で、書式つきの文字列を、固定の配列に安全に作りたい。出力が長すぎたときも、メモリを壊さずに切り詰めたい。それをやる、いちばん安全な書式出力の関数が `std::vsnprintf` です。

<strong>バッファーの大きさを受け取り、溢れないように切り詰め、本来の長さを返します</strong>。""",
  tips=["`vsnprintf(バッファー, 大きさ, 書式, va_list)`。必ず `\\0` で終わらせる（大きさが 1 以上なら）",
        "戻り値は、切り詰めがなければ書けたはずの文字数。`大きさ` 以上なら切れている",
        "`nullptr` と大きさ 0 を渡すと、必要な長さだけが分かる",
        "動的に確保した配列に、ちょうどの大きさで書く 2 段階の手順に使える"],
  details="""### std::vsnprintf {#vsnprintf}

```cpp
int vsnprintf(char* buffer, std::size_t buf_size, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 結果を入れる配列。`nullptr` も可（`buf_size` が 0 のとき） |
| `buf_size` | `size_t` | 配列の大きさ（終端の `\\0` を含む） |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び |

書き込みは、最大で `buf_size - 1` 文字までで、必ず `\\0` を付けます。戻り値は、<strong>バッファーが無限に大きかったら書けたはずの文字数</strong>（`\\0` を除く）です。そのため、戻り値が `buf_size` 以上なら、切り詰められています。失敗時は負の値を返します。

この戻り値を使うと、ちょうどの大きさで確保し直せます。1 回目は `nullptr` と 0 を渡して長さだけを調べ、2 回目で、その長さ + 1 の配列に書きます。`va_list` は 1 回使うと壊れるため、`va_copy` で複製してから、1 回目の呼び出しに使います。

自作のロガーで、固定長の配列に溜めてから出力する、というときの標準的な道具です。C++20 以降なら `std::format_to_n` や `std::vformat` も選べます。""",
  code="""#include <cstdarg>
#include <cstdio>
#include <print>
#include <string>

std::string Format(const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);

  std::va_list copy;
  va_copy(copy, args);
  int len = std::vsnprintf(nullptr, 0, fmt, copy);   // 必要な長さだけを調べる
  va_end(copy);

  std::string result(static_cast<std::size_t>(len), '\\0');
  std::vsnprintf(result.data(), result.size() + 1, fmt, args);   // ちょうどの大きさに書く
  va_end(args);
  return result;
}

int main() {
  std::println("{}", Format("HP: %d / %d (%s)", 85, 120, "ok"));
}""",
  out="HP: 85 / 120 (ok)",
  uses="""自作のログ関数や、書式つきの文字列を `std::string` で返すヘルパーを作るときに使います。長さを 2 回に分けて調べる手順は、定番のイディオムです。

C++20 の `std::format` が使える環境では、型安全なので、そちらを選びます。`vsnprintf` は、C のライブラリの書式（`%d` など）に合わせる必要がある場面や、`va_list` を受け渡す境界で使います。""",
  mistakes=[("戻り値が `buf_size` 以上なのを確かめず、切れたまま使う", "戻り値と `buf_size` を比べて、切り詰めを検出します。"),
            ("`va_list` を 2 回使って、2 回目が壊れる", "`va_copy` で複製します。"),
            ("終端の `\\0` の分を、大きさに入れ忘れる", "`std::string` に書くなら、`size() + 1` を渡します。")],
  similar=[("[`vsprintf`](vsprintf.md)", "大きさを指定できない危険な版"),
           ("[`sprintf`](sprintf.md)", "可変個引数のまま受け取る"),
           ("`std::format`", "C++20 の型安全な組み立て")],
  memo=["大きさを指定して `va_list` から書く", "戻り値は書けたはずの長さ", "長さを調べて 2 段階で書ける"])
print('fs5 ok')
