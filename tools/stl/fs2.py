"""filesystem の薄いページを書き直す（バッチ 2）。"""
from rw import rewrite

F = 'stl/io/filesystem/'

rewrite(F + 'canonical.md',
  intro="""パスは、同じファイルを指すのに、いくらでも書き方があります。`data/../data/./hero.png` も `data/hero.png` も、同じファイルです。ログに出す、重複を調べる、キャッシュのキーにする、という場面では、1 つの決まった形にそろえたくなります。

`std::filesystem::canonical` は、パスを<strong>絶対パスにして、`.` と `..` を取り除き、シンボリックリンクをたどった先の本当の場所</strong>に直して返します。""",
  tips=["結果は、必ず絶対パスで、`.`、`..`、シンボリックリンクを含まない",
        "パスが実在していないとエラーになる。存在しない部分があるなら `weakly_canonical`",
        "ファイルシステムに問い合わせるので、`lexically_normal` のような文字列だけの処理より遅い",
        "同じファイルを指すパスは、同じ `canonical` の結果になる。キーとして使いやすい"],
  details="""### canonical {#canonical}

<span class="ver ver-17">C++17</span>

```cpp
path canonical(const path& p);
path canonical(const path& p, const path& base);
path canonical(const path& p, std::error_code& ec);
path canonical(const path& p, const path& base, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 正規化するパス。実在している必要がある |
| `base` | `const path&` | `p` が相対パスのときの基準。省略するとカレント ディレクトリ |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`p` が相対パスなら、`base / p` として扱います。そのうえで、`.` を消し、`..` を 1 つ上のフォルダーに解決し、途中にシンボリックリンクがあれば、指し先に置き換えます。

[`absolute`](absolute.md) との違いは、`absolute` が文字列の上で絶対パスにするだけで、ファイルシステムに問い合わせず、`..` も消さないことです。`canonical` は、実際にフォルダーをたどるので、<strong>パスの途中が 1 つでも存在しなければ失敗</strong>します。存在しない部分を含むパスを正規化したいときは、[`weakly_canonical`](weakly_canonical.md) を使います。

Windows では、大文字と小文字が違う書き方（`DATA` と `data`）も、実際のフォルダー名に合わせた綴りに直るのがふつうです。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directory("data");
  std::ofstream("data/hero.png") << "x";

  // 回りくどい書き方でも、同じ実体なら canonical は同じ結果になる
  fs::path a = fs::canonical("data/../data/./hero.png");
  fs::path b = fs::canonical("data/hero.png");
  std::println("同じ結果: {}", a == b);
  std::println("絶対パス: {}", a.is_absolute());
  std::println("ファイル名: {}", a.filename().string());

  // 存在しないパスはエラー
  std::error_code ec;
  fs::path c = fs::canonical("data/none.png", ec);
  std::println("存在しない: 空={} エラー={}", c.empty(), static_cast<bool>(ec));
}""",
  out="""同じ結果: true
絶対パス: true
ファイル名: hero.png
存在しない: 空=true エラー=true""",
  uses="""アセットのキャッシュのキーに使います。`textures/hero.png`、`./textures/hero.png`、`textures/../textures/hero.png` のように、読み込みの呼び出しごとに表記が違っても、`canonical` を通せば同じ文字列になるので、`unordered_map` のキーとして使えます。

ログに、読み込んだファイルの本当の場所を出したいときや、ユーザーが指定した出力先が、ゲームのインストール フォルダーの中かどうかを調べるときにも使います。

存在しないファイル（これから作る保存先など）を扱うなら、`weakly_canonical` です。""",
  mistakes=[("これから作るファイルを渡して、例外になる", "`canonical` は実在しないパスを受け付けません。保存先のようにまだ無いものには、`weakly_canonical`、または親フォルダーに `canonical` を使います。"),
            ("毎フレーム呼んで、重くなる", "ファイルシステムに問い合わせるので、ホット パスでは呼びません。読み込み時に 1 回だけ正規化して、結果を持っておきます。")],
  similar=[("[`weakly_canonical`](weakly_canonical.md)", "存在しない部分があってもよい版"),
           ("[`absolute`](absolute.md)", "文字列の上で絶対パスにするだけ。問い合わせず、`..` も消さない"),
           ("[`equivalent`](equivalent.md)", "2 つのパスが同じ実体かを調べる")],
  memo=["絶対パスにして `.` `..` とリンクを解決する", "実在しないとエラー", "キャッシュのキーにしやすい"])

rewrite(F + 'weakly_canonical.md',
  intro="""セーブ データの保存先 `saves/slot1/save.dat` を正規化してログに出したい。でも `slot1` フォルダーも `save.dat` も、まだ作っていない。[`canonical`](canonical.md) は、存在しないパスを渡すと失敗するので、このような場面では使えません。

`std::filesystem::weakly_canonical` は、<strong>パスの前半の「存在する部分」だけを正規化し、残りは文字列の上で整える</strong>関数です。これから作るファイルの場所を、きれいな絶対パスにできます。""",
  tips=["存在する最も長い先頭部分に `canonical` を使い、残りは `lexically_normal` で整える",
        "存在しない部分があっても、エラーにならない",
        "`..` が存在しない部分の中にあっても、文字列の上で解決される",
        "シンボリックリンクの解決は、存在する部分だけ。存在しない部分には効かない"],
  details="""### weakly_canonical {#weakly_canonical}

<span class="ver ver-17">C++17</span>

```cpp
path weakly_canonical(const path& p);
path weakly_canonical(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 正規化するパス。存在しない部分があってもよい |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

動き方は 2 段階です。まず、パスを先頭から調べて、実在する最も長い部分を見つけます。その部分に `canonical` と同じ処理（絶対パス化、`..` の解決、リンクの解決）を行います。残りの、まだ存在しない部分は、文字列の上で `lexically_normal` のように整えて、後ろにつなげます。

そのため、<strong>存在しない部分にあるシンボリックリンクは解決されません</strong>。当たり前ですが、存在しないものはリンクではないからです。

`canonical` が使えない場面（ログ出力、これから作るファイルの重複チェック、保存先が許可された範囲内かの検査）で、代わりに使います。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directory("saves");

  // saves は存在するが、slot1 以降は存在しない
  fs::path p = fs::weakly_canonical("saves/slot1/../slot2/save.dat");
  std::println("絶対パス: {}", p.is_absolute());

  // カレント ディレクトリからの相対にして確かめる
  fs::path rel = fs::relative(p, fs::current_path());
  std::println("{}", rel.generic_string());
}""",
  out="saves/slot2/save.dat",
  uses="""保存先の検査に使います。ユーザーが入力した保存先が、ゲームの保存フォルダーの外に出ていないか（`../../Windows` のような指定）を調べるには、まず `weakly_canonical` で正規化し、保存フォルダーの正規化した結果と、先頭が一致するかを比べます。正規化しないまま文字列で比べると、`..` で簡単にすり抜けられます。

もう 1 つは、ファイルをこれから作るときの、ログの出力です。「どこに書き込むつもりか」を絶対パスで残せます。""",
  mistakes=[("文字列の `..` 処理だけで、安全だと思い込む", "存在する部分にシンボリックリンクがあると、見た目と実際の場所が違うことがあります。保存先の検査には、`weakly_canonical` で実際の場所に直してから比べます。"),
            ("存在する部分だけが正規化されることを知らない", "存在しない部分は、大文字小文字の揃え方も、リンクの解決もされません。")],
  similar=[("[`canonical`](canonical.md)", "全部が実在している必要がある版"),
           ("[`absolute`](absolute.md)", "文字列の上で絶対パスにするだけ")],
  memo=["存在しない部分があってもよい `canonical`", "存在する部分だけ実際に解決する", "保存先の検査に向く"])

rewrite(F + 'absolute.md',
  intro="""相対パス `data/hero.png` は、「今、どのフォルダーで実行しているか」で意味が変わります。ログに出したり、別のプロセスに渡したりするときは、場所がはっきりした絶対パスにしておきたくなります。

`std::filesystem::absolute` は、相対パスの前に<strong>カレント ディレクトリをつなげて</strong>、絶対パスにします。文字列の上の処理だけで、ファイルが存在するかは調べません。""",
  tips=["相対パスに、カレント ディレクトリを前置するだけ。ファイルが存在していなくてもよい",
        "`..` や `.` は取り除かない。取り除くなら `lexically_normal`、または `canonical`",
        "もともと絶対パスなら、そのまま返す（Windows では、ドライブ文字がない `\\foo` などに補う）",
        "シンボリックリンクは、たどらない"],
  details="""### absolute {#absolute}

<span class="ver ver-17">C++17</span>

```cpp
path absolute(const path& p);
path absolute(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 絶対パスにしたいパス。存在しなくてもよい |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

内部では、[`current_path`](current_path.md) を取得して、`p` の前につなげています。ファイルシステムに問い合わせるのは、カレント ディレクトリを調べるときだけです。このため、存在しないパスでも使えます。

[`canonical`](canonical.md) との違いは、`..` や `.` を<strong>消さない</strong>ことと、リンクを解決しないことです。`absolute("a/../b")` は `カレント/a/../b` です。きれいな形にしたいなら、さらに `lexically_normal()` を通します。

Windows では、`"\\\\foo"`（ドライブ文字なしのルート付きパス）や `"C:foo"`（ドライブごとのカレント ディレクトリからの相対）といった、中途半端なパスも、完全な絶対パスに補います。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::path rel = "data/hero.png";
  fs::path abs = fs::absolute(rel);

  std::println("絶対パスになった: {}", abs.is_absolute());
  std::println("カレントから始まる: {}", abs == fs::current_path() / rel);

  // ファイルが存在しなくてもよい
  std::println("存在する: {}", fs::exists(abs));

  // .. は消えない。きれいにするなら lexically_normal
  fs::path messy = fs::absolute("data/../hero.png");
  std::println("そのまま: {}", messy.generic_string().find("..") != std::string::npos);
  std::println("整えた後: {}", messy.lexically_normal().generic_string().find("..") == std::string::npos);
}""",
  out="""絶対パスになった: true
カレントから始まる: true
存在する: false
そのまま: true
整えた後: true""",
  uses="""ログやエラー メッセージに、ファイルの場所を出すときに使います。「`data/hero.png` が開けません」より、「`C:\\Games\\MyGame\\data\\hero.png` が開けません」のほうが、原因を探しやすくなります。

別のプロセス（外部ツールや、起動するコンバーター）にパスを渡すときも、相対パスのままだと、相手のカレント ディレクトリで解釈されて外れます。渡す前に `absolute` で固定します。""",
  mistakes=[("`absolute` が `..` を消してくれると思う", "消しません。比較やキーに使うなら、`canonical`（実在するとき）か、`absolute(p).lexically_normal()` を使います。"),
            ("起動後に `current_path` を変えて、結果がずれる", "`absolute` は呼んだ時点のカレント ディレクトリを使います。実行中にカレント ディレクトリを変えるコードがあると、同じ相対パスでも結果が変わります。起動直後の位置を保存しておく設計が安全です。")],
  similar=[("[`canonical`](canonical.md)", "`..` とリンクを解決する。実在が必要"),
           ("[`relative`](relative.md)", "逆に、基準からの相対パスにする"),
           ("[`current_path`](current_path.md)", "基準になるカレント ディレクトリ")],
  memo=["相対パスの前にカレントをつなげる", "存在しなくてもよい", "`..` は消さない"])

rewrite(F + 'relative.md',
  intro="""ログに出すパスが `C:\\Users\\kan\\Documents\\MyGame\\Assets\\Textures\\hero.png` のように長いと、読みづらい。ゲームのフォルダーからの相対パス `Assets/Textures/hero.png` なら、すぐ分かります。パックファイルに、ルートからの相対パスで名前を記録したい場面もあります。

`std::filesystem::relative` は、`p` を<strong>`base` から見た相対パス</strong>に直します。""",
  tips=["`relative(p, base)` は、`base` から `p` へ行くための相対パスを返す",
        "内部で `weakly_canonical` を使う。`p` や `base` が存在しなくてもよい",
        "2 つのパスのルートが違うと（別のドライブなど）、相対パスが作れず、空のパスを返す",
        "`base` を省略すると、カレント ディレクトリが基準になる"],
  details="""### relative {#relative}

<span class="ver ver-17">C++17</span>

```cpp
path relative(const path& p, const path& base = current_path());
path relative(const path& p, std::error_code& ec);
path relative(const path& p, const path& base, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 相対パスにしたいパス |
| `base` | `const path&` | 基準になるフォルダー。省略するとカレント ディレクトリ |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

先に `p` と `base` を `weakly_canonical` で正規化し、共通の先頭部分を取り除いて、足りない分を `..` で補います。`relative("/a/b/c", "/a/d")` は `../b/c` です。

2 つのパスが同じ場所なら、`.` を返します。ルートが違って、相対パスにできないとき（Windows で `C:` と `D:`）は、<strong>空のパスを返します</strong>。この空の結果を、そのままファイルの操作に渡さないよう、`empty()` で確かめます。

ファイルシステムに問い合わせる処理を含むので、文字列の上だけで済ませたいなら、`path::lexically_relative` を使います。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::path root = "/game";

  // 基準より下にあるパス
  std::println("{}", fs::relative("/game/assets/hero.png", root).generic_string());

  // 基準と別の枝にあるパス: .. で戻る
  std::println("{}", fs::relative("/game/assets/hero.png", "/game/saves").generic_string());

  // 同じ場所なら "."
  std::println("{}", fs::relative(root, root).generic_string());
}""",
  out="""assets/hero.png
../assets/hero.png
.""",
  uses="""ログや UI に、ゲーム フォルダーからの相対パスを出すために使います。絶対パスは長く、ユーザー名のような個人情報も含むので、画面やレポートには相対パスのほうが向いています。

パックファイル（アセットをまとめたファイル）を作るツールで、ルートからの相対パスを名前として記録するときにも使います。区切りは `generic_string()` で `/` にそろえておくと、OS が違っても同じ名前になります。""",
  mistakes=[("別のドライブのパスで、空の結果を使ってしまう", "`C:` と `D:` のように、ルートが違うと相対パスは作れず、空のパスが返ります。`empty()` を確かめるか、絶対パスのまま使う [`proximate`](proximate.md) を使います。"),
            ("`base` にファイルのパスを渡す", "`base` はフォルダーとして扱われます。ファイルの場所を渡すと、`..` が 1 つ多い結果になります。`parent_path()` を渡します。")],
  similar=[("[`proximate`](proximate.md)", "相対パスにできないときは `p` をそのまま返す版"),
           ("`path::lexically_relative`", "文字列の上だけで処理する。ファイルシステムに問い合わせない"),
           ("[`absolute`](absolute.md)", "逆に、絶対パスにする")],
  memo=["`base` から見た相対パスにする", "ルートが違うと空のパスが返る", "ログや pack の名前に使う"])

rewrite(F + 'proximate.md',
  intro="""[`relative`](relative.md) は便利ですが、ルートが違うパス（`C:` と `D:`）では空のパスを返します。ログの出力やパックのファイル名で、「相対にできるなら相対、できないなら絶対のまま」にしたいとき、空のパスを毎回確かめて分岐するのは面倒です。

`std::filesystem::proximate` は、`relative` と同じ動きで、<strong>相対パスにできないときは、`p` をそのまま返す</strong>関数です。""",
  tips=["相対パスにできるなら `relative` と同じ結果",
        "できないとき（別のドライブなど）は、空ではなく `p` を返す",
        "「近いほうの表記」を選ぶ関数。表示用途に向く",
        "`base` を省略すると、カレント ディレクトリが基準"],
  details="""### proximate {#proximate}

<span class="ver ver-17">C++17</span>

```cpp
path proximate(const path& p, const path& base = current_path());
path proximate(const path& p, std::error_code& ec);
path proximate(const path& p, const path& base, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 変換するパス |
| `base` | `const path&` | 基準になるフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

内部では、まず `relative(p, base)` を試します。その結果が空でなければ、それを返します。空だったときだけ、`weakly_canonical(p)` を返します。つまり、「近く（proximate）に表せるならその表記、無理なら絶対パス」です。

`relative` と違って、結果が空になることがないので、続けてそのまま文字列にして出力できます。ただし、戻り値が相対か絶対かは、パスの組み合わせで変わるので、<strong>返った値を基準のフォルダーに足して使う</strong>ような処理には向きません。表示と記録のための関数です。""",
  code="""#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;

  // 相対にできるときは、relative と同じ
  fs::path a = fs::proximate("/game/assets/hero.png", "/game");
  std::println("{}", a.generic_string());

  // 同じ場所なら "."
  fs::path b = fs::proximate("/game", "/game");
  std::println("{}", b.generic_string());

  // relative との違い: 結果が空になることはない
  std::println("空ではない: {}", !fs::proximate("/game/x", "/game/y").empty());
}""",
  out="""assets/hero.png
.
空ではない: true""",
  uses="""複数のドライブにまたがる可能性のあるファイルを、ログに出すときに使います。ゲーム フォルダーの中にあるアセットは相対で短く、ユーザーが外部から指定したファイルは絶対パスで、と自動で使い分けられます。

エラー レポートやデバッグ表示のように、見るための文字列を作る場面が中心です。""",
  mistakes=[("戻り値を、必ず相対パスだと思って基準に足す", "別のドライブなどで絶対パスが返ることがあります。`base / result` にすると、絶対パス同士の結合になり、意図と違う場所になります。"),
            ("`relative` と同じだと思って、空の結果の分岐を残す", "`proximate` は空を返しません。分岐が不要になります。")],
  similar=[("[`relative`](relative.md)", "相対にできないと空のパスを返す版")],
  memo=["相対にできれば `relative` と同じ", "できないときは `p` を返す", "表示や記録のための関数"])

rewrite(F + 'is_empty.md',
  intro="""ゲームの起動時に、設定ファイルが空（0 バイト）なら既定値を使いたい。ゴミ箱代わりの一時フォルダーが空なら、削除したい。「ファイルが空か」と「フォルダーが空か」は、別々の関数で調べなくてはなりません。

`std::filesystem::is_empty` は、<strong>ファイルなら 0 バイトか、フォルダーなら中身がないか</strong>を、1 つの関数で調べます。""",
  tips=["通常のファイルは、サイズが 0 なら `true`",
        "フォルダーは、直下に何も無ければ `true`（サブフォルダーがあれば `false`）",
        "パスが存在しないときは、`false` ではなくエラー（例外）",
        "フォルダーの中に空のフォルダーしかないときも `false`。深くたどるわけではない"],
  details="""### is_empty {#is_empty}

<span class="ver ver-17">C++17</span>

```cpp
bool is_empty(const path& p);
bool is_empty(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス。ふつうのファイルかフォルダー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

ふつうのファイルには [`file_size`](file_size.md) が 0 かどうか、フォルダーには [`directory_iterator`](directory_iterator.md) の最初の要素が終端かどうか、を調べています。フォルダーでは、全体を数えるわけではなく、最初の 1 件を見るだけなので、中身が多くても速く終わります。

ここで気をつけるのは、<strong>存在しないパスはエラー</strong>になることです。「空ファイルか、存在しないか」を区別したいので、`false` や `true` を返さず、例外（`ec` の版ではエラー）にしています。存在するかどうかが不確かなら、先に `exists` で確かめます。

ふつうのファイルでもフォルダーでもない特殊なファイル（デバイス ファイルなど）に使うと、失敗することがあります。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;

  std::ofstream("empty.txt");                // 0 バイトのファイル
  std::ofstream("full.txt") << "data";       // 4 バイトのファイル
  fs::create_directory("emptydir");
  fs::create_directories("fulldir/sub");

  std::println("empty.txt: {}", fs::is_empty("empty.txt"));
  std::println("full.txt: {}", fs::is_empty("full.txt"));
  std::println("emptydir: {}", fs::is_empty("emptydir"));
  std::println("fulldir: {}", fs::is_empty("fulldir"));   // sub がある

  std::error_code ec;
  fs::is_empty("missing", ec);
  std::println("存在しない: エラー={}", static_cast<bool>(ec));
}""",
  out="""empty.txt: true
full.txt: false
emptydir: true
fulldir: false
存在しない: エラー=true""",
  uses="""クリーンアップ処理で、中身が空になったフォルダーを消すときに使います。アセットを展開したあとに、空のフォルダーだけが残っていることがあります。`is_empty` で空だと確かめてから `remove` します。

設定ファイルやセーブ データが「0 バイトで壊れている」ケースの検出にも使います。クラッシュで書き込みが途中のまま終わると、空のファイルが残ることがあります。そのときは、バックアップから復元するか、既定値で作り直します。""",
  mistakes=[("存在しないパスで例外が出る", "`false` が返るのではなく、エラーです。`exists` で確かめるか、`error_code` を受け取る版を使います。"),
            ("サブフォルダーだけが入ったフォルダーを、空だと思う", "サブフォルダーがあれば、中が空でも `false` です。再帰的に調べたいなら、`recursive_directory_iterator` で走査します。")],
  similar=[("[`file_size`](file_size.md)", "ファイルのバイト数。0 と比べれば、空ファイルの判定になる"),
           ("[`directory_iterator`](directory_iterator.md)", "フォルダーの中身を 1 件ずつ見る")],
  memo=["ファイルは 0 バイト、フォルダーは中身なしで `true`", "存在しないとエラー", "フォルダーは最初の 1 件を見るだけ"])

rewrite(F + 'status_known.md',
  intro="""[`status`](status.md) が返した `file_status` が、「ちゃんとした結果」なのか、「調べられなかった」のかを知りたいことがあります。存在しないことは `not_found` として分かります。でも、権限などで調べられなかったときは、`type()` が `none`（不明）になります。

`std::filesystem::status_known` は、<strong>`file_status` の種類が分かっているか</strong>を返す関数です。`type()` が `none` でなければ `true` です。""",
  tips=["引数は `file_status`（パスではない）",
        "`not_found` も「分かっている」結果なので `true`。`none` のときだけ `false`",
        "`error_code` を渡した `status` の結果を調べるときに使う",
        "存在判定の `exists` は、内部でこの判定を含んでいる"],
  details="""### status_known {#status_known}

<span class="ver ver-17">C++17</span>

```cpp
bool status_known(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `file_status` | 調べる `file_status` の値 |

`s.type() != file_type::none` と同じです。`file_type::none` は、「状態の取得が失敗した」または「まだ何も入っていない」ことを表す値です。

`not_found` は、「調べた結果、存在しなかった」という情報なので、`status_known` は `true` を返します。この関数が `false` になるのは、権限がなくて調べられなかったとき、`error_code` 付きの `status` が失敗したとき、そして、デフォルト構築しただけの `file_status` です。

`exists(s)` は `status_known(s) && s.type() != not_found` として定義されているので、「存在する」と「存在しない」と「不明」の 3 つを区別するときに、この関数を組み合わせます。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("a.txt") << "x";

  // 存在するファイル: 種類が分かっている
  std::println("a.txt: {}", fs::status_known(fs::status("a.txt")));

  // 存在しないファイル: 「存在しない」と分かっているので true
  fs::file_status none = fs::status("missing.txt");
  std::println("missing.txt: 分かっている={} 存在する={}", fs::status_known(none), fs::exists(none));

  // 何も入っていない file_status: 不明
  fs::file_status blank;
  std::println("空の file_status: {}", fs::status_known(blank));
}""",
  out="""a.txt: true
missing.txt: 分かっている=true 存在する=false
空の file_status: false""",
  uses="""`error_code` を使って例外を避けるコードで、エラーの原因を分けて処理するときに使います。「存在しない」は正常な結果として扱い、「調べられなかった」だけを警告に回す、という分岐ができます。

ふつうのゲーム コードでは、`exists` や `is_regular_file` で済むので、直接使う機会は多くありません。""",
  mistakes=[("`status_known` を「存在するか」の意味で使う", "存在しなくても `true` です。存在判定は `exists` です。"),
            ("パスを渡そうとして、コンパイル エラー", "引数は `file_status` です。`status_known(fs::status(path))` の形で使います。")],
  similar=[("[`exists`](exists.md)", "存在するかを調べる。内部でこの判定を使う"),
           ("[`status`](status.md)", "`file_status` を取得する関数")],
  memo=["`file_status` の種類が分かっているか", "`not_found` でも `true`", "`none` のときだけ `false`"])

rewrite(F + 'hard_link_count.md',
  intro="""同じファイルに、複数の名前（パス）を付ける仕組みがあります。ハード リンクです。ファイルの実体は 1 つで、名前だけが複数あり、どの名前を消しても、最後の名前が消えるまで実体は残ります。

`std::filesystem::hard_link_count` は、<strong>その実体を指している名前が、いくつあるか</strong>を返します。ふつうのファイルは、名前が 1 つなので 1 です。""",
  tips=["戻り値は、ハード リンクの数（`std::uintmax_t`）。ふつうのファイルは 1",
        "`create_hard_link` で名前を増やすと、増える",
        "リンクを `remove` すると減る。0 になって初めて、データが解放される",
        "FAT など、ハード リンクをサポートしないファイルシステムでは、失敗する場合がある"],
  details="""### hard_link_count {#hard_link_count}

<span class="ver ver-17">C++17</span>

```cpp
std::uintmax_t hard_link_count(const path& p);
std::uintmax_t hard_link_count(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるファイル |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、そのファイルの実体を指している名前（ディレクトリ エントリ）の数です。[`create_hard_link`](create_hard_link.md) で別の名前を付けると 2 になり、どちらかの名前を `remove` すると 1 に戻ります。

フォルダーには、ふつう使いません。フォルダーのリンク数の意味は、ファイルシステムによって違います（POSIX では、サブフォルダーの数に関係する値になる）。

存在しないパスや、ハード リンクの数を取得できないファイルシステムでは、例外（または `ec` のエラー）になります。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("orig.dat") << "data";
  std::println("最初: {}", fs::hard_link_count("orig.dat"));

  fs::create_hard_link("orig.dat", "alias.dat");   // 同じ実体に別の名前を付ける
  std::println("リンク後: {}", fs::hard_link_count("orig.dat"));

  fs::remove("alias.dat");                         // 名前を 1 つ消す
  std::println("名前を消した後: {}", fs::hard_link_count("orig.dat"));
}""",
  out="""最初: 1
リンク後: 2
名前を消した後: 1""",
  uses="""ゲームの実行中に使うことはほとんどありません。ビルド ツールやインストーラーが、同じアセットを複数の場所に置くとき、コピーではなくハード リンクにしてディスクを節約する場合があります。`hard_link_count` は、そのような仕組みの検査や、削除の安全確認に使えます。

データを消す前に、「他の名前が残っているか」を知りたい、というツール側の用途が中心です。""",
  mistakes=[("コピーとハード リンクを同じものだと思う", "ハード リンクは実体を共有します。一方の名前から内容を書き換えると、もう一方の名前でも変わります。独立したコピーが必要なら `copy_file` を使います。"),
            ("別のボリュームにハード リンクを作ろうとして失敗する", "ハード リンクは、同じボリューム（同じファイルシステム）の中でしか作れません。")],
  similar=[("[`create_hard_link`](create_hard_link.md)", "ハード リンクを作る"),
           ("[`create_symlink`](create_symlink.md)", "別の名前を指す参照を作る。実体を共有するわけではない")],
  memo=["実体を指す名前の数を返す", "ふつうは 1", "同じボリュームの中だけで作れる"])

rewrite(F + 'file_status.md',
  intro="""ファイルについて知りたい情報は、種類（通常のファイル、フォルダー、リンク…）と、権限（読める、書ける…）の 2 つに大きく分かれます。この 2 つをひとまとめにして持つのが、`std::filesystem::file_status` です。[`status`](status.md) や [`symlink_status`](symlink_status.md) の戻り値であり、[`directory_entry`](directory_entry.md) からも取り出せます。""",
  tips=["`type()` で [`file_type`](file_type.md)、`permissions()` で [`perms`](perms.md) を読む",
        "`status` や `symlink_status` の戻り値として手に入る。自分で作ることはあまりない",
        "コピーが軽い小さな値型。引数は値渡しでよい",
        "`exists`、`is_directory` などの補助関数は、`file_status` を直接受け取る版もある"],
  details="""### file_status {#file_status}

<span class="ver ver-17">C++17</span>

```cpp
class file_status {
 public:
  explicit file_status(file_type ft = file_type::none, perms prms = perms::unknown) noexcept;

  file_type type() const noexcept;
  perms permissions() const noexcept;

  void type(file_type ft) noexcept;
  void permissions(perms prms) noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ft` | `file_type` | ファイルの種類。省略すると `none` |
| `prms` | `perms` | 権限。省略すると `unknown` |

`type()` は、`regular`（通常のファイル）、`directory`、`symlink`、`not_found`、`none` などを返します。`permissions()` は、`owner_read`、`owner_write` などのビットの組み合わせです。

Windows では、POSIX ほど細かい権限がないため、読み取り専用かどうかを中心に、ほぼ全員に同じ権限が付いた値になります。権限の細かさは OS に依存すると考えます。

デフォルト構築した値は、種類が `none`、権限が `unknown` で、[`status_known`](status_known.md) が `false` になります。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("hero.dat") << "x";

  fs::file_status st = fs::status("hero.dat");
  std::println("通常のファイル: {}", st.type() == fs::file_type::regular);

  // 権限ビットを調べる
  bool can_read = (st.permissions() & fs::perms::owner_read) != fs::perms::none;
  std::println("所有者が読める: {}", can_read);

  // 自分で作ることもできる
  fs::file_status custom(fs::file_type::directory, fs::perms::owner_all);
  std::println("directory: {}", custom.type() == fs::file_type::directory);
  custom.type(fs::file_type::regular);
  std::println("変更後 regular: {}", custom.type() == fs::file_type::regular);
}""",
  out="""通常のファイル: true
所有者が読める: true
directory: true
変更後 regular: true""",
  uses="""ファイルを走査するコードで、種類と権限をまとめて受け取って判定するときに使います。ゲームでは、MOD フォルダーのスキャンなどで、読み取れるふつうのファイルだけを対象にする、といった場面で出てきます。

1 つのファイルに対して種類を何度も調べるなら、`status` の戻り値を変数に取っておいて、`fs::is_regular_file(st)`、`fs::is_directory(st)` のように使い回します。呼ぶたびにファイルシステムへ問い合わせる無駄が省けます。""",
  mistakes=[("権限のビットを `&` だけで判定して、型エラーになる", "`perms` は列挙型のビット フラグで、`&` の結果は `perms` です。`!= fs::perms::none` と比べて判定します。"),
            ("Windows でも POSIX と同じ細かい権限が取れると思う", "Windows では、読み取り専用かどうかが中心です。権限のコードを OS をまたいで共有するときは、細かい差に頼りません。")],
  similar=[("[`status`](status.md)", "この型を返す関数"),
           ("[`file_type`](file_type.md)", "種類を表す列挙型"),
           ("[`perms`](perms.md)", "権限を表す列挙型")],
  memo=["種類と権限をまとめた値", "`type()` と `permissions()` で読む", "`status` の結果を使い回す"])

rewrite(F + 'read_symlink.md',
  intro="""シンボリックリンクは、別のパスを指すだけの小さなファイルです。`status` や `canonical` はリンクの先まで追いかけますが、「リンクが、どこを指すように書かれているか」を知りたいことがあります。

`std::filesystem::read_symlink` は、<strong>シンボリックリンクに書かれている指し先のパス</strong>を、そのまま返します。先を追いかけず、存在するかも調べません。""",
  tips=["リンクが指す先のパスを、書かれているとおりに返す（相対パスなら相対のまま）",
        "引数がシンボリックリンクでないとエラーになる",
        "指し先が存在していなくても、取り出せる",
        "Windows では、シンボリックリンクを作る権限（開発者モードなど）が要る"],
  details="""### read_symlink {#read_symlink}

<span class="ver ver-17">C++17</span>

```cpp
path read_symlink(const path& p);
path read_symlink(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | シンボリックリンクのパス |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、リンクの中身（ターゲット）のパスです。作成時に相対パスを指定していれば、相対パスのまま返ります。実際に開くときは、リンクのあるフォルダーを基準に解決されるので、必要なら `canonical` を組み合わせます。

引数がシンボリックリンクでないとき（通常のファイル、フォルダー、存在しないパス）は、エラーです。リンクかどうかを先に調べるなら、[`is_symlink`](is_symlink.md) を使います。

[`canonical`](canonical.md) は、最終的な本当の場所を返しますが、`read_symlink` は、リンク 1 段分の内容を返すだけです。リンクが別のリンクを指していても、1 段しかたどりません。""",
  code="""#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  // シンボリックリンクではないものに使うと、エラーになる
  std::error_code ec;
  fs::path target = fs::read_symlink("plain.txt", ec);
  std::println("結果が空: {}", target.empty());
  std::println("エラー: {}", static_cast<bool>(ec));
  std::println("リンクか: {}", fs::is_symlink("plain.txt"));
}""",
  out="""結果が空: true
エラー: true
リンクか: false""",
  uses="""リンクの張り直しや、ツールでのリンク切れの検査に使います。リンクが指している先の文字列を取り出して、その先が存在するかを調べる、という流れです。

ゲームの実行中に使うことはほとんどありません。Linux や macOS 向けのビルドで、共有ライブラリのバージョン リンク（`libfoo.so` → `libfoo.so.1.2`）を調べるツールを書くときなどに現れます。""",
  mistakes=[("リンクではないパスに使ってエラーになる", "通常のファイルやフォルダーでは失敗します。`is_symlink` で確かめてから呼びます。"),
            ("戻り値を、そのまま開けると思う", "相対パスで作られたリンクは、戻り値が相対パスのままです。現在のフォルダーからではなく、リンクのあるフォルダーを基準に解釈する必要があります。")],
  similar=[("[`create_symlink`](create_symlink.md)", "シンボリックリンクを作る"),
           ("[`is_symlink`](is_symlink.md)", "リンクかどうかを調べる"),
           ("[`canonical`](canonical.md)", "最終的な実体の絶対パスを返す")],
  memo=["リンクが指す先を返す", "リンクでないとエラー", "1 段分だけ読む"])
print('fs2 ok')
