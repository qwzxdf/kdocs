"""filesystem の薄いページを書き直す（バッチ 3: 種類の判定、リンク、時刻）。"""
from rw import rewrite

F = 'stl/io/filesystem/'

# --- is_socket / is_fifo / is_block_file / is_character_file / is_other ---

rewrite(F + 'is_socket.md',
  intro="""Unix 系の OS では、ネットワーク通信の窓口（ソケット）に、ファイルシステム上の名前が付くことがあります（Unix ドメイン ソケット）。ゲーム サーバーと管理ツールが、`/tmp/game.sock` のようなファイルで話し合う、という使い方です。

`std::filesystem::is_socket` は、<strong>パスがそのようなソケット ファイルか</strong>を調べます。通常のファイルやフォルダーなら `false` です。""",
  tips=["`is_socket(p)` は、`p` がソケット ファイルなら `true`",
        "Windows の通常の環境では、ほぼ `false`（Windows のソケットは名前付きファイルではない）",
        "存在しないパスは `false`。リンクは先をたどって判定する",
        "判定は [`status`](status.md) の結果の種類（`file_type::socket`）の確認"],
  details="""### is_socket {#is_socket}

<span class="ver ver-17">C++17</span>

```cpp
bool is_socket(const path& p);
bool is_socket(const path& p, std::error_code& ec) noexcept;
bool is_socket(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::socket` と同じ判定です。Unix ドメイン ソケットが対象で、TCP や UDP のソケットは、ファイルシステム上に名前を持たないので、対象外です。

Windows には、Unix ドメイン ソケットに当たる物（AF_UNIX）がありますが、Windows の C++ 標準ライブラリは、ふつう `socket` とは判定せず、`false` になります。マルチプラットフォームのコードでは、「Windows では常に `false`」と考えて作ります。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";
  fs::create_directory("folder");

  std::println("通常のファイル: {}", fs::is_socket("plain.txt"));
  std::println("フォルダー: {}", fs::is_socket("folder"));
  std::println("存在しない: {}", fs::is_socket("missing"));
}""",
  out="""通常のファイル: false
フォルダー: false
存在しない: false""",
  uses="""Linux や macOS 向けに、ゲーム サーバーを作るときに使います。サーバーを起動する前に、前回の実行で消し忘れたソケット ファイルが残っていないかを `is_socket` で確かめ、残っていれば `remove` してから `bind` します（残っていると `bind` が失敗するため）。

Windows 専用のクライアント ゲームでは、ほぼ出番がありません。""",
  mistakes=[("ネットワーク ソケットを調べられると思う", "対象は、ファイルシステム上の名前を持つ Unix ドメイン ソケットだけです。TCP のソケットは、パスで表せません。"),
            ("Windows で `true` になると期待して分岐を書く", "Windows では `false` が返るのがふつうです。OS ごとの処理は、別に分けます。")],
  similar=[("[`is_fifo`](is_fifo.md)", "名前付きパイプ（FIFO）か"),
           ("[`is_other`](is_other.md)", "通常のファイル、フォルダー、リンクのどれでもないか")],
  memo=["Unix ドメイン ソケットのファイルか", "Windows ではほぼ `false`", "存在しなければ `false`"])

rewrite(F + 'is_fifo.md',
  intro="""別のプログラムと、ファイルのような名前を通してデータをやり取りしたい。それも、ファイルに書き溜めるのではなく、書いた分を相手がすぐ読める「管」のようにしたい。Unix 系の OS には、そのための名前付きパイプ（FIFO）があります。

`std::filesystem::is_fifo` は、<strong>パスが名前付きパイプか</strong>を調べます。""",
  tips=["`is_fifo(p)` は、`p` が名前付きパイプ（FIFO）なら `true`",
        "Windows の名前付きパイプ（`\\\\.\\pipe\\...`）は、ファイルシステムのパスではないので、対象外",
        "存在しないパスは `false`。リンクは先をたどって判定する",
        "データの出入りは、ふつうのファイルと同じ `fstream` で行う"],
  details="""### is_fifo {#is_fifo}

<span class="ver ver-17">C++17</span>

```cpp
bool is_fifo(const path& p);
bool is_fifo(const path& p, std::error_code& ec) noexcept;
bool is_fifo(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::fifo` と同じ判定です。FIFO は、`mkfifo` コマンドや関数で作ります。標準の `std::filesystem` には、FIFO を作る関数はありません。

FIFO は、書き込む側と読む側が両方そろわないと、`open` が止まることがあります。`is_fifo` で見分けておけば、通常のファイルのつもりで開いて固まる、という事故を避けられます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  std::println("通常のファイル: {}", fs::is_fifo("plain.txt"));
  std::println("カレント ディレクトリ: {}", fs::is_fifo("."));
  std::println("存在しない: {}", fs::is_fifo("missing"));
}""",
  out="""通常のファイル: false
カレント ディレクトリ: false
存在しない: false""",
  uses="""Linux や macOS で、ゲームと外部ツール（ログビューアーやデバッグ コンソール）をつなぐときに使います。ツールが作った FIFO にゲームがログを書き込む、という構成です。書き込む前に `is_fifo` で、相手が用意した管かを確かめます。

フォルダーの走査で、通常のファイル以外が混ざっていないか調べる処理でも、`is_regular_file` と組み合わせて使います。Windows 専用のゲームでは、出番はほとんどありません。""",
  mistakes=[("FIFO を通常のファイルとして開いて、固まる", "相手がつながっていない FIFO を開くと、`open` が待ち続けます。`is_regular_file` で通常のファイルだけを対象にするのが安全です。"),
            ("Windows の名前付きパイプも調べられると思う", "`\\\\.\\pipe\\name` は、ファイルシステムのパスではありません。Windows API（`CreateNamedPipe`）で扱います。")],
  similar=[("[`is_socket`](is_socket.md)", "ソケット ファイルか"),
           ("[`is_other`](is_other.md)", "通常のファイル、フォルダー、リンクのどれでもないか")],
  memo=["名前付きパイプ（FIFO）か", "Windows では対象外", "通常のファイルのつもりで開かない"])

rewrite(F + 'is_block_file.md',
  intro="""Unix 系の OS では、ディスクのような「ブロック単位で読み書きする装置」にも、`/dev/sda` のようなファイルの名前が付きます。ふつうのファイルと同じように `open` できますが、扱いを間違えると、ディスクの中身を壊します。

`std::filesystem::is_block_file` は、<strong>パスがブロック デバイスか</strong>を調べます。""",
  tips=["`is_block_file(p)` は、`p` がブロック デバイスなら `true`",
        "Windows には、ブロック デバイスのファイルがないので、ふつう `false`",
        "存在しないパスは `false`。リンクは先をたどって判定する",
        "キーボードなどの「1 文字ずつ」の装置は [`is_character_file`](is_character_file.md)"],
  details="""### is_block_file {#is_block_file}

<span class="ver ver-17">C++17</span>

```cpp
bool is_block_file(const path& p);
bool is_block_file(const path& p, std::error_code& ec) noexcept;
bool is_block_file(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::block` と同じ判定です。ハード ディスク、SSD、USB メモリ、ループバック デバイスなどが、ブロック デバイスの例です。

ゲームでこのファイルを直接開くことは、ほとんどありません。ユーザーが入力したパスを検査して、「ふつうのファイルでないものを開かない」ためのチェックの 1 つとして知っておきます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  std::println("通常のファイル: {}", fs::is_block_file("plain.txt"));
  std::println("カレント ディレクトリ: {}", fs::is_block_file("."));
}""",
  out="""通常のファイル: false
カレント ディレクトリ: false""",
  uses="""ユーザーが指定したパスを開く前の検査で使います。MOD のフォルダーとして `/dev/sda` のような装置が指定されると、読み込み処理が意図しない動きをします。`is_regular_file` が `true` のものだけを開く、とすれば、ブロック デバイスも自然に除外されます。

`is_block_file` を単独で使うのは、ディスク ツールのような特殊なプログラムだけです。""",
  mistakes=[("ブロック デバイスを通常のファイルとして書き込む", "ディスクの中身を壊すおそれがあります。ユーザーの入力したパスに書き込む前に、`is_regular_file` で確かめます。"),
            ("Windows のドライブ（`C:\\\\`）が `true` になると思う", "ドライブ文字は、ファイルシステムのブロック デバイスのファイルではなく、フォルダー（ルート）として扱われます。")],
  similar=[("[`is_character_file`](is_character_file.md)", "文字デバイスか"),
           ("[`is_regular_file`](is_regular_file.md)", "通常のファイルか"),
           ("[`is_other`](is_other.md)", "通常のファイル、フォルダー、リンクのどれでもないか")],
  memo=["ブロック デバイスか", "Windows では `false`", "通常のファイルだけ開くなら `is_regular_file`"])

rewrite(F + 'is_character_file.md',
  intro="""Unix 系の OS では、キーボード、端末、乱数の発生源（`/dev/urandom`）なども、ファイルの名前で扱います。これらは、ディスクと違って、バイトが 1 つずつ流れてくる「文字デバイス」です。

`std::filesystem::is_character_file` は、<strong>パスが文字デバイスか</strong>を調べます。""",
  tips=["`is_character_file(p)` は、`p` が文字デバイスなら `true`",
        "`/dev/null`、`/dev/urandom`、`/dev/tty` などが該当する",
        "Windows では、`NUL` や `CON` といった特別な名前があるが、ふつう `false` になる",
        "存在しないパスは `false`。リンクは先をたどって判定する"],
  details="""### is_character_file {#is_character_file}

<span class="ver ver-17">C++17</span>

```cpp
bool is_character_file(const path& p);
bool is_character_file(const path& p, std::error_code& ec) noexcept;
bool is_character_file(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::character` と同じ判定です。文字デバイスは、サイズの概念がなく、読み込みが終わらないこともあります。`/dev/urandom` は、永遠にデータが出てきます。

そのため、ファイルを丸ごと読み込む処理（`ifstream` で最後まで読む）を、文字デバイスに行うと、終わらなくなります。ユーザーの指定したパスを読み込む前に、この種類を除外します。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  std::println("通常のファイル: {}", fs::is_character_file("plain.txt"));
  std::println("カレント ディレクトリ: {}", fs::is_character_file("."));
}""",
  out="""通常のファイル: false
カレント ディレクトリ: false""",
  uses="""設定ファイルや MOD のファイルを読み込む前の検査で使います。ユーザーが `/dev/zero` のようなパスを指定すると、全部を読み込もうとして終わらなくなるので、`is_regular_file` が `true` のものだけを対象にします。その除外に、この関数は直接は要らず、`is_regular_file` で足ります。

文字デバイスと分かった上で、読み込み方を変えたい特殊なツール（端末の入力を扱うものなど）だけが、直接使います。""",
  mistakes=[("文字デバイスを丸ごと読み込もうとして、終わらなくなる", "`/dev/urandom` や `/dev/zero` は、読み続けても終わりません。サイズが不明なファイルは、読み込む量の上限を決めます。"),
            ("Windows の `NUL` や `CON` で `true` を期待する", "これらは Win32 の特別な名前で、`std::filesystem` からは通常のファイルとして見える、または存在しないように見えるなど、環境で変わります。")],
  similar=[("[`is_block_file`](is_block_file.md)", "ブロック デバイスか"),
           ("[`is_regular_file`](is_regular_file.md)", "通常のファイルか")],
  memo=["文字デバイスか", "読み込みが終わらないことがある", "ユーザーの入力したパスは `is_regular_file` で絞る"])

rewrite(F + 'is_other.md',
  intro="""フォルダーを走査すると、通常のファイルやフォルダーに混じって、リンクや特殊なファイル（ソケット、パイプ、デバイス）が出てくることがあります。通常のファイル、フォルダー、シンボリックリンクのどれでもない物をまとめて除外したい、というとき、いくつも `is_xxx` を並べるのは面倒です。

`std::filesystem::is_other` は、<strong>存在するが、通常のファイル、フォルダー、シンボリックリンクのどれでもない</strong>とき `true` になります。""",
  tips=["`is_other(p)` は、ソケット、FIFO、ブロック デバイス、文字デバイスなどのとき `true`",
        "存在しないパスは `false`。通常のファイル、フォルダー、リンクも `false`",
        "リンクは先をたどって判定する。リンクの先が特殊なファイルなら `true`",
        "個別に知りたいときは、`is_socket` などを使う"],
  details="""### is_other {#is_other}

<span class="ver ver-17">C++17</span>

```cpp
bool is_other(const path& p);
bool is_other(const path& p, std::error_code& ec) noexcept;
bool is_other(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`exists(s) && !is_regular_file(s) && !is_directory(s) && !is_symlink(s)` と同じです。ここで、`status` は通常、リンクをたどるので、`is_symlink` が `true` になる場面は少なく、実質は<strong>「通常のファイルでもフォルダーでもない、存在する物」</strong>です。

存在しないものが `false` なのは、「その他」の中に「無い」は含まれないからです。「通常のファイルとして読める」を確かめたいなら、`!is_other` ではなく、`is_regular_file` を使います。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";
  fs::create_directory("folder");

  std::println("通常のファイル: {}", fs::is_other("plain.txt"));
  std::println("フォルダー: {}", fs::is_other("folder"));
  std::println("存在しない: {}", fs::is_other("missing"));
}""",
  out="""通常のファイル: false
フォルダー: false
存在しない: false""",
  uses="""フォルダーを走査して、読み込み対象のファイルを集めるときに、特殊なファイルを除外する目的で使います。ただし、ふつうは `is_regular_file` が `true` のものだけを拾えば足ります。`is_other` は、除外した物を「警告として報告したい」ときに便利です。

ログに「特殊なファイル `...` はスキップしました」と出したい、といった診断用の使い方が主です。""",
  mistakes=[("存在しないものも `true` になると思う", "存在しないパスは `false` です。「通常のファイルではない」を調べるなら `!is_regular_file(p)` です。"),
            ("`!is_other` を「ふつうのファイル」の判定に使う", "フォルダーも `!is_other` になります。ふつうのファイルは `is_regular_file` で判定します。")],
  similar=[("[`is_regular_file`](is_regular_file.md)", "通常のファイルか"),
           ("[`is_socket`](is_socket.md)", "ソケットか"),
           ("[`is_fifo`](is_fifo.md)", "名前付きパイプか")],
  memo=["特殊な存在するファイルか", "通常のファイル、フォルダー、リンクは `false`", "存在しなければ `false`"])

rewrite(F + 'is_symlink.md',
  intro="""パスが、別の場所への「近道」であるシンボリックリンクなのかどうかを知りたい。ファイルをコピーするときに、リンクをたどって実体をコピーするのか、リンクそのものをコピーするのかを、決めなくてはなりません。

`std::filesystem::is_symlink` は、<strong>パスがシンボリックリンクそのもの</strong>であるかを調べます。ここが他の `is_xxx` と違う点で、リンクをたどらず、リンクの種類を見ます。""",
  tips=["`is_symlink(p)` は、`p` がシンボリックリンクなら `true`。他の `is_xxx` と違い、リンクをたどらない",
        "内部では [`symlink_status`](symlink_status.md) を使う",
        "リンクの先が存在しなくても、リンク自体があれば `true`",
        "Windows でも使えるが、リンクを作るには権限（開発者モードなど）が要る"],
  details="""### is_symlink {#is_symlink}

<span class="ver ver-17">C++17</span>

```cpp
bool is_symlink(const path& p);
bool is_symlink(const path& p, std::error_code& ec) noexcept;
bool is_symlink(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | `symlink_status` で取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`symlink_status(p).type() == file_type::symlink` と同じです。他の `is_directory` や `is_regular_file` が `status`（リンクをたどる）を使うのに対し、`is_symlink` は `symlink_status`（リンクをたどらない）を使います。

`file_status` を受け取る版には注意が必要です。`status` で得た状態を渡しても、リンクはすでにたどられた後なので、`false` になります。リンクかどうかを調べたい `file_status` は、`symlink_status` で取得します。

指し先が存在しないリンク（ぶら下がったリンク）でも、`is_symlink` は `true` です。一方 `exists` は `false` になります。この組み合わせで、リンク切れを検出できます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";
  fs::create_directory("folder");

  std::println("通常のファイル: {}", fs::is_symlink("plain.txt"));
  std::println("フォルダー: {}", fs::is_symlink("folder"));
  std::println("存在しない: {}", fs::is_symlink("missing"));

  // リンク切れの検出: リンクだが、先が存在しない
  fs::path p = "plain.txt";
  bool broken = fs::is_symlink(p) && !fs::exists(p);
  std::println("リンク切れ: {}", broken);
}""",
  out="""通常のファイル: false
フォルダー: false
存在しない: false
リンク切れ: false""",
  uses="""アセットのコピーやパッケージ作成のツールで、リンクの扱いを決めるときに使います。リンクを実体としてコピーするなら `copy_options::copy_symlinks` を指定しない（既定）、リンクのまま複製するなら指定する、と選びますが、その前に、対象にリンクが含まれるかを `is_symlink` で数えて、ログに出す使い方があります。

リンク切れの検査にも使います。`is_symlink(p) && !exists(p)` が `true` なら、指し先が消えたリンクです。""",
  mistakes=[("`status` で得た `file_status` を渡して、常に `false` になる", "`status` はリンクをたどった後の状態です。`is_symlink(file_status)` に渡すなら、`symlink_status` で取得したものにします。"),
            ("リンク切れを `exists` だけで判定する", "リンク切れは `exists` が `false` になるだけで、「存在しない」のか「リンクが切れている」のか区別できません。`is_symlink` と組み合わせます。")],
  similar=[("[`symlink_status`](symlink_status.md)", "リンクをたどらずに状態を取る"),
           ("[`read_symlink`](read_symlink.md)", "リンクの指し先を読む"),
           ("[`create_symlink`](create_symlink.md)", "リンクを作る")],
  memo=["シンボリックリンクそのものか", "リンクをたどらない", "リンク切れは `is_symlink` かつ `!exists`"])

rewrite(F + 'symlink_status.md',
  intro="""[`status`](status.md) は、シンボリックリンクがあると、その指し先の情報を返します。リンクのファイルそのものがどんな状態なのかを知りたいときには、先をたどってしまう `status` は役に立ちません。

`std::filesystem::symlink_status` は、<strong>リンクをたどらずに</strong>、パスそのものの種類と権限を [`file_status`](file_status.md) として返します。""",
  tips=["`status` と同じ使い方で、リンクだけを「たどらない」",
        "パスがリンクなら `type()` が `symlink` になる",
        "リンクの先が存在しなくても、リンクがあれば取得できる",
        "リンク以外のパスでは、`status` と同じ結果になる"],
  details="""### symlink_status {#symlink_status}

<span class="ver ver-17">C++17</span>

```cpp
file_status symlink_status(const path& p);
file_status symlink_status(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status` との違いは、パスの最後の部分がシンボリックリンクのときだけです。`status` は先をたどり、`symlink_status` はたどりません。パスの途中にあるリンク（`dir_link/file` の `dir_link` など）は、どちらも通常どおり先をたどって解決されます。

リンクの先が存在しない場合、`status` は `not_found` を返しますが、`symlink_status` は `symlink` を返します。この差が、リンク切れの検出に使えます。

パスが存在しなければ、`status` と同じく、`not_found` が返ります（例外ではありません）。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  // リンクではないパスでは、status と同じ結果
  fs::file_status a = fs::status("plain.txt");
  fs::file_status b = fs::symlink_status("plain.txt");
  std::println("通常のファイルでは同じ: {}", a.type() == b.type());
  std::println("リンクではない: {}", b.type() != fs::file_type::symlink);

  // 存在しないパスは not_found
  std::println("存在しない: {}", fs::symlink_status("missing").type() == fs::file_type::not_found);
}""",
  out="""通常のファイルでは同じ: true
リンクではない: true
存在しない: true""",
  uses="""ファイルの走査やコピーのツールで、リンクを実体として扱うか、リンクのまま扱うかを分けるときに使います。ディレクトリ ツリーを再帰的にたどるとき、リンクをたどると、リンクが親を指していた場合に無限ループになります。`symlink_status` でリンクかどうかを見て、たどらないようにします。

`recursive_directory_iterator` は、既定でリンクをたどりません。自分で再帰を書くときに、この関数が必要になります。""",
  mistakes=[("リンク切れを `status` で検出しようとして、普通の「存在しない」と区別できない", "`status` はどちらも `not_found` です。`symlink_status` が `symlink` で、`status` が `not_found` なら、リンク切れです。"),
            ("自分で再帰してリンクをたどり、無限ループになる", "フォルダーへのリンクが親を指すと、ぐるぐる回ります。リンクをたどらない設計にします。")],
  similar=[("[`status`](status.md)", "リンクをたどる版"),
           ("[`is_symlink`](is_symlink.md)", "リンクかどうかだけを返す補助関数")],
  memo=["リンクをたどらない `status`", "リンクなら `symlink` を返す", "リンク切れの検出に使える"])

rewrite(F + 'copy_symlink.md',
  intro="""フォルダーのコピーなどで、シンボリックリンクに出会ったとき、リンクの指し先の実体をコピーするのか、リンクそのものを新しい場所に作るのか、選ぶ必要があります。後者のために用意された関数が、`std::filesystem::copy_symlink` です。

<strong>リンクそのもの</strong>を、新しい場所へコピーします。新しいリンクは、元と同じ指し先を指します。""",
  tips=["コピーするのは、リンクの中身（指し先のパス）。指し先の実体ではない",
        "引数が両方とも、パス。コピー元がシンボリックリンクでないとエラー",
        "新しいリンクの指し先は、元と同じ文字列。相対パスなら、新しい場所から見て別の場所を指すことがある",
        "Windows では、リンクを作る権限が要る"],
  details="""### copy_symlink {#copy_symlink}

<span class="ver ver-17">C++17</span>

```cpp
void copy_symlink(const path& existing_symlink, const path& new_symlink);
void copy_symlink(const path& existing_symlink, const path& new_symlink, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `existing_symlink` | `const path&` | コピー元。シンボリックリンクである必要がある |
| `new_symlink` | `const path&` | 作る新しいリンクのパス。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`read_symlink(existing)` で指し先を読んで、同じ指し先の新しいリンクを作る、という処理と同じです。指し先がファイルかフォルダーかで、`create_symlink` と `create_directory_symlink` を使い分けます。

注意するのは、<strong>相対パスのリンクをコピーすると、意味が変わりうる</strong>ことです。`../data` を指すリンクを別のフォルダーにコピーすると、新しい場所から見た `../data` を指します。元と同じ実体を指したいなら、リンクを絶対パスで作っておきます。

`copy` 関数で `copy_options::copy_symlinks` を指定すると、フォルダーの再帰コピーの中でリンクに出会ったとき、内部でこの処理が行われます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  // コピー元がリンクでないと、エラーになる
  std::error_code ec;
  fs::copy_symlink("plain.txt", "copy_link", ec);
  std::println("エラー: {}", static_cast<bool>(ec));
  std::println("コピー先が作られた: {}", fs::exists("copy_link"));
}""",
  out="""エラー: true
コピー先が作られた: false""",
  uses="""ゲームのインストーラーや、アセットのパッケージ作成ツールで、フォルダー構造を複製するときに使います。リンクを実体にして展開するか、リンクのまま保つかは、ツールの方針です。通常は `copy` に `copy_options::copy_symlinks` を渡して任せ、この関数を直接呼ぶのは、リンクだけを特別扱いしたいときです。

ゲームの実行中に使うことは、ほとんどありません。""",
  mistakes=[("リンクではないものを渡して、エラーになる", "コピー元がリンクでないと失敗します。通常のファイルは `copy_file` を使います。"),
            ("相対リンクをコピーして、リンク切れになる", "指し先の文字列だけがコピーされるので、新しい場所から見た相対パスが、存在しない場所を指すことがあります。")],
  similar=[("[`copy`](copy.md)", "ファイルやフォルダーをまとめてコピー。`copy_symlinks` オプションで内部的にこの処理を使う"),
           ("[`create_symlink`](create_symlink.md)", "指し先を指定して、新しいリンクを作る"),
           ("[`read_symlink`](read_symlink.md)", "リンクの指し先を読む")],
  memo=["リンクそのものをコピーする", "コピー元はリンクである必要がある", "相対リンクは意味が変わりうる"])

rewrite(F + 'file_time_type.md',
  intro="""ファイルの更新時刻を、前回のビルドと比べて「新しくなったか」を判定したい。ところが、`last_write_time` が返す時刻の型は、`std::chrono::system_clock` ではありません。`std::filesystem::file_time_type` という、ファイルシステム専用の時刻の型です。

この型は、`std::chrono::time_point` の別名です。<strong>ファイルシステムの時刻専用の時計</strong>（`std::filesystem::__file_clock`、C++20 以降は `std::chrono::file_clock`）を使います。""",
  tips=["`last_write_time` が返す型。`std::chrono::time_point` の別名",
        "比較（`<`, `>`, `==`）と、差の計算（`-`）は、そのまま使える",
        "`system_clock` とは別の時計。日時として表示するには変換が要る（C++20 は `clock_cast`）",
        "時計の起点（エポック）は実装しだい。数値として他の環境と比べない"],
  details="""### file_time_type {#file_time_type}

<span class="ver ver-17">C++17</span>

```cpp
using file_time_type = std::chrono::time_point<std::chrono::file_clock>;   // C++20 以降。C++17 では実装定義の時計
```

C++17 では、`file_time_type` が使う時計の名前は規定されていませんでした（`trivial-clock` として実装定義）。C++20 で、`std::chrono::file_clock` が標準になり、`system_clock` や `utc_clock` との変換（`clock_cast`）も、可能になりました。

比較と差の計算は、普通の `time_point` として行えます。2 つのファイルの更新時刻を比べて新しい方を選ぶ、現在時刻との差を求める、といった処理には、変換が要りません。

人が読む日時に直す場合は、`system_clock` に変換します。C++20 以降なら `std::chrono::clock_cast<std::chrono::system_clock>(ft)` です。C++17 までは、この変換に標準の方法がありませんでした。

時計のエポック（起点）は、実装ごとに違います。MSVC は Windows のファイル時刻にそろえて 1601 年 1 月 1 日が起点ですが、他の実装では違います。<strong>`time_since_epoch().count()` の数値を、環境をまたいで比べてはいけません</strong>。""",
  code="""#include <chrono>
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("old.txt") << "x";
  std::ofstream("new.txt") << "x";

  // old.txt を、1 時間前の時刻にする
  fs::file_time_type now = fs::file_time_type::clock::now();
  fs::last_write_time("old.txt", now - std::chrono::hours(1));

  fs::file_time_type t_old = fs::last_write_time("old.txt");
  fs::file_time_type t_new = fs::last_write_time("new.txt");

  // 比較と差の計算は、そのまま使える
  std::println("new.txt のほうが新しい: {}", t_new > t_old);
  auto diff = std::chrono::duration_cast<std::chrono::minutes>(t_new - t_old);
  std::println("約 {} 分以上の差", diff.count() >= 59 ? 59 : diff.count());
}""",
  out="""new.txt のほうが新しい: true
約 59 分以上の差""",
  uses="""ホット リロードや、ビルド システムで、「ソースがアセットより新しいか」を判定するときに使います。`last_write_time(src) > last_write_time(asset)` と書けば、変換なしで比べられます。

更新時刻をログに出すときは、`clock_cast` で `system_clock` に直してから、`std::format("{}", ...)` に渡します。数値のまま出さないようにします。""",
  mistakes=[("`file_time_type` と `system_clock::time_point` を直接比べて、コンパイル エラー", "別の時計の `time_point` は、比べられません。`clock_cast` で時計をそろえます。"),
            ("`time_since_epoch().count()` の数値を、保存して別の環境で使う", "エポックが実装ごとに違うので、数値に意味がありません。保存するなら、`system_clock` に直した UTC の時刻にします。")],
  similar=[("[`last_write_time`](last_write_time.md)", "この型の時刻を読み書きする関数"),
           ("`std::chrono::system_clock`", "カレンダー時刻に使う時計。変換が要る")],
  memo=["ファイルシステム専用の時刻の型", "比較と差の計算はそのまま", "数値のエポックは環境ごとに違う"])
print('fs3 ok')
