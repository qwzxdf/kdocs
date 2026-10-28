"""cstdio の主要な関数を書き直す（バッチ 2: 読み書き、位置、バッファー）。"""
from rw import rewrite

C = 'stl/io/cstdio/'

rewrite(C + 'fread.md',
  intro="""セーブ データがバイナリで保存されている。画像やモデルのファイルを、そのままメモリに読み込みたい。1 文字ずつ読んでいては遅いので、<strong>まとまったバイト列を、一度にメモリへ読み込む</strong>のが `std::fread` です。""",
  tips=["`fread(buf, 1 要素の大きさ, 要素数, ファイル)` の形。戻り値は、読めた要素の数",
        "戻り値が要求より少ないのは、ファイルの終わりか、エラー。`feof` と `ferror` で見分ける",
        "バイナリ データには `\"rb\"` で開いたファイルを使う",
        "構造体をそのまま読み込めるのは、パディングや型の大きさがそろう同じ環境のときだけ"],
  details="""### std::fread {#fread}

```cpp
std::size_t fread(void* buffer, std::size_t size, std::size_t count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `void*` | 読み込んだデータを入れる場所。`size * count` バイト以上の領域が必要 |
| `size` | `size_t` | 1 要素の大きさ（バイト） |
| `count` | `size_t` | 読み込む要素の数 |
| `stream` | `FILE*` | 読み込むファイル |

戻り値は、<strong>実際に読めた要素の数</strong>（バイト数ではありません）です。`size` を 1 にして `count` をバイト数にすると、戻り値がそのままバイト数になるので、扱いやすくなります。

戻り値が `count` より小さいときは、2 つの場合があります。ファイルの終わりに達した場合と、読み込みエラーが起きた場合です。`feof(stream)` が真なら終わり、`ferror(stream)` が真ならエラーです。ファイルの大きさが分からないときは、少なめの `count` で呼び、戻り値が `count` より小さくなった時点で終わり、とする使い方ができます。

`buffer` が小さいと、メモリを破壊します。`size * count` が確保した領域に収まっているかを、呼ぶ前に確かめます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  // 4 バイトのデータを書き出す
  std::FILE* out = std::fopen("data.bin", "wb");
  const unsigned char src[4] = {10, 20, 30, 40};
  std::fwrite(src, 1, 4, out);
  std::fclose(out);

  // 8 バイト読もうとするが、ファイルには 4 バイトしかない
  std::FILE* in = std::fopen("data.bin", "rb");
  unsigned char buf[8] = {};
  std::size_t n = std::fread(buf, 1, 8, in);
  std::println("読めたバイト数: {}", n);
  std::println("ファイルの終わり: {}", std::feof(in) != 0);
  std::println("先頭の値: {}", buf[0]);
  std::fclose(in);
}""",
  out="""読めたバイト数: 4
ファイルの終わり: true
先頭の値: 10""",
  uses="""アセットや、独自形式のバイナリ ファイルを読み込むときに使います。ファイルの先頭にあるヘッダー（マジック ナンバーとバージョン）を `fread` で読み、形式が正しいと確かめてから、続きを読み進めます。

構造体を丸ごと読み込むのは手軽ですが、コンパイラや設定が変わるとパディングが変わり、読めなくなります。保存する形式は、1 フィールドずつ、大きさとバイト順を決めて書き出すほうが、長持ちします。""",
  mistakes=[("戻り値を確かめずに、読めたと仮定する", "ファイルが短いと、読み残しがあります。バッファーの残りは、初期化していなければ、ゴミのままです。戻り値を確かめます。"),
            ("テキスト モードで開いて、バイナリが壊れる", "Windows のテキスト モードは、`\\r\\n` を変換し、`0x1A` を終端と見なすことがあります。`\"rb\"` で開きます。"),
            ("`size` と `count` の積がバッファーを超える", "メモリを破壊します。`sizeof(buf)` で確かめて、`count` を決めます。")],
  similar=[("[`fwrite`](fwrite.md)", "対になる、書き出す関数"),
           ("[`fgets`](fgets.md)", "1 行ずつ読む。テキスト向け"),
           ("`std::ifstream::read`", "C++ のストリームでの同等の関数")],
  memo=["バイト列を一度に読み込む", "戻り値は読めた要素の数", "短いときは `feof` と `ferror` で見分ける"])

rewrite(C + 'fwrite.md',
  intro="""セーブ データや、書き出したメッシュをバイナリで保存したい。1 バイトずつ書くと遅いので、<strong>メモリ上のまとまったデータを、一度にファイルへ書き出す</strong>のが `std::fwrite` です。""",
  tips=["`fwrite(データ, 1 要素の大きさ, 要素数, ファイル)` の形。戻り値は、書けた要素の数",
        "戻り値が `count` より小さいときは、書き込みの失敗（ディスクが一杯など）",
        "バイナリには `\"wb\"` で開く。`\"w\"` だと Windows で `\\n` が `\\r\\n` に変わる",
        "書いた内容は、バッファーに残っていることがある。確実に書き出すには `fclose` か `fflush`"],
  details="""### std::fwrite {#fwrite}

```cpp
std::size_t fwrite(const void* buffer, std::size_t size, std::size_t count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `const void*` | 書き出すデータの先頭 |
| `size` | `size_t` | 1 要素の大きさ（バイト） |
| `count` | `size_t` | 書き出す要素の数 |
| `stream` | `FILE*` | 書き出す先のファイル |

戻り値は、<strong>書けた要素の数</strong>です。`count` と同じなら成功です。小さいときは、ディスクが一杯、書き込み禁止、デバイスのエラーなどで、書ききれませんでした。

`fwrite` が `count` を返しても、データが実際にディスクに届いたとは限りません。C のライブラリは、いったん内部のバッファーに溜めて、まとめて書き出します。確実に届けたいときは、`fflush` を呼ぶか、`fclose` で閉じます。それでも OS のキャッシュに残る場合があり、電源が切れても残したいセーブでは、OS の機能（`FlushFileBuffers`、`fsync`）まで使います。

`void*` を受け取るので、型の安全性はありません。構造体をそのまま書くと、パディングの中のゴミまで保存され、同じデータでも毎回ファイルの内容が違うことがあります。""",
  code="""#include <cstdio>
#include <print>

struct Header {
  char magic[4];
  int version;
};

int main() {
  Header h = {{'S', 'A', 'V', 'E'}, 2};

  std::FILE* f = std::fopen("save.bin", "wb");
  std::size_t written = std::fwrite(&h, sizeof(h), 1, f);   // 構造体 1 個を書く
  std::println("書けた要素の数: {}", written);
  std::fclose(f);

  // 読み直して確かめる
  std::FILE* in = std::fopen("save.bin", "rb");
  Header back = {};
  std::fread(&back, sizeof(back), 1, in);
  std::fclose(in);
  std::println("magic: {}{}{}{}", back.magic[0], back.magic[1], back.magic[2], back.magic[3]);
  std::println("version: {}", back.version);
}""",
  out="""書けた要素の数: 1
magic: SAVE
version: 2""",
  uses="""独自形式のセーブ データ、頂点バッファーのキャッシュ、シェーダーのコンパイル結果の保存などに使います。ファイルの先頭に、識別用の文字列とバージョン番号を書くと、あとで形式を変えたときに、古いファイルを見分けられます。

セーブの失敗は、プレイヤーにとって大きな損失です。`fwrite` の戻り値と `fclose` の戻り値の両方を確かめ、失敗したら前のセーブ データを残す、一時ファイルに書いてから `rename` で置き換える、といった設計にします。""",
  mistakes=[("戻り値を確かめず、書けなかったことに気づかない", "ディスクが一杯のときも、プログラムは続きます。戻り値が `count` と等しいかを確かめます。"),
            ("構造体をそのまま書いて、別の環境で読めない", "パディングとバイト順は環境しだいです。保存形式は、フィールドごとに大きさを決めて書き出します。"),
            ("書いた直後に別のプロセスで読んで、内容が足りない", "バッファーに残っています。`fflush` か `fclose` の後に読みます。")],
  similar=[("[`fread`](fread.md)", "対になる、読み込む関数"),
           ("[`fputs`](fputs.md)", "文字列を書き出す。テキスト向け"),
           ("[`fflush`](fflush.md)", "バッファーを書き出す"),
           ("`std::ofstream::write`", "C++ のストリームでの同等の関数")],
  memo=["バイト列を一度に書き出す", "戻り値は書けた要素の数", "確実に届けるには `fflush` か `fclose`"])

rewrite(C + 'fgets.md',
  intro="""設定ファイルを 1 行ずつ読んで解釈したい。`scanf` は空白で区切ってしまうので、スペースを含む行は読みにくい。<strong>1 行を、長さの上限つきで読み込む</strong>のが `std::fgets` です。上限があるので、バッファーを溢れさせる危険がありません。""",
  tips=["`fgets(buf, 大きさ, ファイル)` で、改行までを `buf` に入れる。改行文字も含まれる",
        "戻り値は `buf`。ファイルの終わりかエラーなら `nullptr`",
        "1 行が `大きさ - 1` より長いと、途中で切れる。続きは次の呼び出しで読める",
        "末尾の `\\n` を取り除きたいなら、`strcspn` などで自分で消す"],
  details="""### std::fgets {#fgets}

```cpp
char* fgets(char* str, int count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `char*` | 読み込んだ行を入れるバッファー |
| `count` | `int` | バッファーの大きさ（終端の `\\0` を含む） |
| `stream` | `FILE*` | 読み込むファイル |

最大で `count - 1` 文字を読み、末尾に `\\0` を付けます。改行に達したら、<strong>改行文字も含めて</strong>読み込んで止まります。そのため、行末の `\\n` が文字列に残ります。比較するときは、これを取り除いてからにします。

1 行が長すぎてバッファーに入りきらないときは、入る分だけを返し、残りは次の `fgets` で読めます。行の最後に `\\n` が無いことで、「途中で切れた」と見分けられます。

戻り値の `nullptr` は、ファイルの終わりで 1 文字も読めなかった場合と、エラーの場合です。ループの条件に `while (fgets(...))` と書く形が定番です。`gets` という似た関数は、大きさの上限が無く危険なため、C++14 で削除されました。""",
  code="""#include <cstdio>
#include <cstring>
#include <print>

int main() {
  std::FILE* out = std::fopen("config.txt", "w");
  std::fputs("name=hero\\nhp=100\\n", out);
  std::fclose(out);

  std::FILE* in = std::fopen("config.txt", "r");
  char line[64];
  while (std::fgets(line, sizeof(line), in)) {
    line[std::strcspn(line, "\\r\\n")] = '\\0';   // 末尾の改行を取り除く
    std::println("[{}]", line);
  }
  std::fclose(in);
}""",
  out="""[name=hero]
[hp=100]""",
  uses="""設定ファイルや、簡単なテキスト形式のデータを 1 行ずつ読んで、`key=value` に分解する処理に使います。バッファーの大きさが決まっているので、異常に長い行が入っていても、メモリを壊しません。

C++ では、`std::getline` が `std::string` に読めて、長さの制限もないので、通常はそちらが楽です。`fgets` は、`FILE*` を扱う C のライブラリとつなぐ部分や、一時的に確保するメモリを抑えたい場面で使います。""",
  mistakes=[("行末の `\\n` を取り除かずに比較して、一致しない", "`fgets` は改行を含めて返します。比較の前に取り除きます。"),
            ("`sizeof(buf)` ではなく、ポインターに `sizeof` を使う", "関数に渡した後の `char*` に `sizeof` を使うと、ポインターの大きさ（8）になります。配列の大きさを別に渡します。"),
            ("1 行が長いとき、切れた行を 1 行と思い込む", "バッファーに入りきらない行は、複数回に分けて返ります。末尾に `\\n` があるかで見分けます。")],
  similar=[("[`fputs`](fputs.md)", "文字列を書き出す"),
           ("[`fscanf`](fscanf.md)", "書式を指定して読む"),
           ("`std::getline`", "C++ のストリームで 1 行読む。長さの制限がない")],
  memo=["1 行を上限つきで読む", "改行文字も含まれる", "終わりかエラーで `nullptr`"])

rewrite(C + 'fputs.md',
  intro="""ログやテキスト ファイルに、文字列を書き出したい。`fprintf` は書式を解釈するので、文字列に `%` が含まれていると、予期しない動きをします。<strong>文字列をそのまま書き出す</strong>には、`std::fputs` が安全です。""",
  tips=["`fputs(文字列, ファイル)` で、`\\0` の手前までを書き出す",
        "改行は自動では付かない。`puts` との違い",
        "書式を解釈しないので、`%` を含んでいても、そのまま出る",
        "戻り値は、成功なら 0 以上、失敗なら `EOF`"],
  details="""### std::fputs {#fputs}

```cpp
int fputs(const char* str, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 書き出す文字列。`\\0` で終わっている必要がある |
| `stream` | `FILE*` | 書き出す先のファイル。`stdout` や `stderr` も渡せる |

`str` の `\\0` の手前までを書き出します。<strong>終端の `\\0` や、改行は書き出しません</strong>。同じ仲間の `puts` は、改行を自動で足しますが、`fputs` は足しません。行にしたければ、文字列に `\\n` を入れます。

`fprintf(f, str)` との違いは、書式の解釈です。ユーザー入力のような、`%` を含みうる文字列を `fprintf` の書式として渡すと、`%s` や `%n` が解釈され、クラッシュや脆弱性の原因になります。`fputs` なら、その心配がありません。

文字列の長さを `strlen` で数えて書くので、バイナリ データには向きません。`\\0` を含むデータは `fwrite` を使います。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("log.txt", "w");
  std::fputs("HP: 100%\\n", f);   // % が含まれていても、そのまま出る
  std::fputs("MP: 50", f);        // 改行は付かない
  std::fclose(f);

  std::FILE* in = std::fopen("log.txt", "r");
  char buf[64];
  while (std::fgets(buf, sizeof(buf), in)) std::print("{}", buf);
  std::println("");
  std::fclose(in);
}""",
  out="""HP: 100%
MP: 50""",
  uses="""ログ ファイルに、1 行ずつ書き込むときに使います。メッセージに `%` が含まれうる（ユーザー名やファイル名など）場面で、`fprintf` より安全です。

C++ では、`std::ofstream` と `<<`、または `std::print(FILE*, ...)`（C++23）でも書けます。`FILE*` を扱う C のライブラリとの連携では、`fputs` が手軽です。""",
  mistakes=[("改行が付くと思って、ログが 1 行につながる", "`fputs` は改行を足しません。`puts` と混同しないようにします。"),
            ("ユーザー入力を `fprintf` の書式にして、クラッシュ", "`fprintf(f, input)` の形は危険です。`fputs(input, f)` か、`fprintf(f, \"%s\", input)` にします。")],
  similar=[("[`puts`](puts.md)", "`stdout` に書いて、改行を足す"),
           ("[`fprintf`](fprintf.md)", "書式つきで書く"),
           ("[`fwrite`](fwrite.md)", "バイト列を書く。`\\0` を含んでもよい")],
  memo=["文字列をそのまま書き出す", "改行は付かない", "書式を解釈しないので安全"])

rewrite(C + 'fseek.md',
  intro="""大きなファイルの途中にあるデータだけを読みたい。先頭から全部読んでいては遅いので、<strong>読み書きする位置を、ファイルの好きな場所に動かす</strong>のが `std::fseek` です。パックファイルから、特定のアセットの場所へ飛ぶときの基本の道具です。""",
  tips=["`fseek(ファイル, 動かす量, 基準)` の形。基準は `SEEK_SET`（先頭）、`SEEK_CUR`（今の位置）、`SEEK_END`（末尾）",
        "戻り値は、成功なら 0、失敗なら 0 以外",
        "ファイルの大きさを知るには、`SEEK_END` に動かして `ftell` を呼ぶ定番の手順がある",
        "テキスト モードでは、動かせる量に制約がある。バイナリ モードで使う"],
  details="""### std::fseek {#fseek}

```cpp
int fseek(std::FILE* stream, long offset, int origin);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を動かすファイル |
| `offset` | `long` | 基準から動かすバイト数。負の値で戻れる |
| `origin` | `int` | 基準。[`SEEK_SET`](seek_set.md)、[`SEEK_CUR`](seek_cur.md)、[`SEEK_END`](seek_end.md) のどれか |

`SEEK_SET` は先頭が基準で、`offset` は先頭からの位置です。`SEEK_CUR` は今の位置が基準で、`offset` が負なら戻ります。`SEEK_END` は末尾が基準で、`offset` が 0 なら末尾そのものです。

`long` は、Windows では 32 ビットなので、<strong>2 GB を超えるファイルでは使えません</strong>。大きなファイルを扱うなら、`_fseeki64`（Windows）や `fseeko`（POSIX）を使うか、`std::ifstream::seekg` を使います。

テキスト モードで開いたファイルでは、`offset` に、`ftell` が返した値か 0 しか使えません。`\\r\\n` の変換があるため、バイト数の計算が合わなくなるからです。位置を計算して飛ぶ処理は、`\"rb\"` で開いたバイナリ モードで行います。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("data.bin", "wb");
  std::fputs("0123456789", out);
  std::fclose(out);

  std::FILE* f = std::fopen("data.bin", "rb");

  std::fseek(f, 5, SEEK_SET);                 // 先頭から 5 バイト目へ
  std::println("先頭から 5: {}", static_cast<char>(std::fgetc(f)));

  std::fseek(f, -1, SEEK_END);                // 末尾の 1 つ前へ
  std::println("末尾の 1 つ前: {}", static_cast<char>(std::fgetc(f)));

  std::fseek(f, 0, SEEK_END);                 // 末尾に移動して大きさを知る
  std::println("大きさ: {}", std::ftell(f));
  std::fclose(f);
}""",
  out="""先頭から 5: 5
末尾の 1 つ前: 9
大きさ: 10""",
  uses="""パックファイル（複数のアセットを 1 つにまとめたファイル）の読み込みで使います。先頭の目次から、目的のアセットの位置と大きさを読み取り、`fseek` で位置に飛んでから `fread` で読み込みます。

ファイルの大きさを調べる定番の手順（末尾に動かして `ftell`）にも使いますが、C++17 以降なら、`std::filesystem::file_size` のほうが簡単です。""",
  mistakes=[("2 GB を超えるファイルで失敗する", "`long` が 32 ビットの環境（Windows）では、位置を表せません。64 ビット版の関数を使います。"),
            ("テキスト モードで位置を計算して、ずれる", "`\\r\\n` の変換があり、バイト数が合いません。位置計算をするファイルは、バイナリ モードで開きます。"),
            ("戻り値を確かめずに、失敗に気づかない", "範囲外に動かすなどで失敗します。0 以外が返ったら、読み書きを続けません。")],
  similar=[("[`ftell`](ftell.md)", "今の位置を調べる"),
           ("[`rewind`](rewind.md)", "先頭に戻る"),
           ("[`fgetpos`](fgetpos.md)", "位置を保存する。巨大なファイルにも使える")],
  memo=["読み書きの位置を動かす", "基準は先頭、今の位置、末尾", "2 GB を超えるなら 64 ビット版"])

rewrite(C + 'ftell.md',
  intro="""ファイルのどこまで読んだか、どこに書いたかを知りたい。パックファイルに書いたアセットの位置を、目次に記録したい。<strong>今の読み書きの位置</strong>を、先頭からのバイト数で返すのが `std::ftell` です。""",
  tips=["戻り値は、先頭からのバイト数（`long`）。失敗すると `-1L`",
        "`fseek(f, 0, SEEK_END)` の後に呼ぶと、ファイルの大きさになる",
        "Windows では `long` が 32 ビットなので、2 GB を超える位置は表せない",
        "テキスト モードでは、返る値は位置の目印であり、バイト数とは限らない"],
  details="""### std::ftell {#ftell}

```cpp
long ftell(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を調べるファイル |

読み書きの位置を、ファイルの先頭からのバイト数で返します。開いた直後は 0 で、`fread` や `fwrite` で進みます。追記モード（`\"a\"`）で開いたファイルは、書き込みのたびに末尾へ移るため、書く前に調べた位置は当てになりません。

失敗したときは `-1L` を返します。端末のような、位置を持たないものに使うと失敗します。

戻り値をそのまま `fseek` に渡すと、その位置に戻れます。パックファイルを書くとき、アセットを書く直前に `ftell` で位置を記録し、目次に残す、という使い方ができます。

2 GB を超える位置は `long`（Windows では 32 ビット）で表せません。`_ftelli64`（Windows）や `ftello`（POSIX）を使います。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("pack.bin", "wb");

  long pos1 = std::ftell(f);           // 最初のアセットの位置
  std::fwrite("AAAA", 1, 4, f);
  long pos2 = std::ftell(f);           // 2 つ目のアセットの位置
  std::fwrite("BBBBBB", 1, 6, f);
  long end = std::ftell(f);

  std::println("1 つ目: {} から", pos1);
  std::println("2 つ目: {} から", pos2);
  std::println("全体の大きさ: {}", end);
  std::fclose(f);
}""",
  out="""1 つ目: 0 から
2 つ目: 4 から
全体の大きさ: 10""",
  uses="""自作のパックファイルを書き出すツールで、各アセットの先頭位置を記録するときに使います。書く直前に `ftell` で位置を取り、書いた後の `ftell` との差が、アセットの大きさになります。目次は最後にまとめて書くか、先頭に空きを取っておいて、あとから書き戻します。

読み込みでは、ファイルを読み進めた量を知るのに使いますが、`fread` の戻り値を足し合わせるほうが、確実です。""",
  mistakes=[("戻り値の `-1` を確かめずに、そのまま位置として使う", "失敗の値です。`fseek` に渡すと、さらに失敗します。"),
            ("追記モードで、書く前の位置を使う", "追記モードは、書き込みのたびに末尾へ移ります。書いた後の位置で考えます。")],
  similar=[("[`fseek`](fseek.md)", "位置を動かす"),
           ("[`fgetpos`](fgetpos.md)", "位置を保存する。巨大なファイルにも使える")],
  memo=["今の位置を先頭からのバイト数で返す", "失敗は `-1L`", "2 GB を超えるなら 64 ビット版"])

rewrite(C + 'rewind.md',
  intro="""ファイルを最後まで読んだあと、もう一度、先頭から読み直したい。1 回目で行数を数え、2 回目で中身を読む、という 2 パスの処理では、いったん閉じて開き直さずに、先頭へ戻れると便利です。

`std::rewind` は、<strong>読み書きの位置を先頭に戻し、エラーとファイルの終わりの印も消す</strong>関数です。""",
  tips=["`rewind(f)` は、`fseek(f, 0, SEEK_SET)` と、`clearerr(f)` を合わせたもの",
        "ファイルの終わりに達していても、`rewind` の後は、また読める",
        "戻り値はない。失敗しても分からないので、確実さが要る場面は `fseek` を使う",
        "ストリーム全体で「最初に戻る」だけなら、これで十分"],
  details="""### std::rewind {#rewind}

```cpp
void rewind(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 先頭に戻すファイル |

`fseek(stream, 0L, SEEK_SET)` を呼び、さらに、ファイルの終わりの印とエラーの印を消します（`clearerr`）。`fseek` だけでは、終わりの印は消えますが、エラーの印は残ることがある、という違いがあります。

戻り値が `void` なので、位置を戻せたかが分かりません。失敗を確かめたいときは、`fseek` を直接呼んで戻り値を見ます。

読み書き兼用で開いたファイル（`\"w+\"`、`\"r+\"`）では、書いた直後に読むために位置を戻す、という使い方もします。このとき、書き込みと読み込みの切り替えの間には、`fseek` か `rewind`、`fflush` のどれかを挟む決まりがあり、`rewind` がその役割も果たします。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("lines.txt", "w+");   // 読み書き兼用
  std::fputs("A\\nB\\nC\\n", f);

  std::rewind(f);                                 // 書いた後、先頭に戻って読む

  int count = 0;
  char buf[16];
  while (std::fgets(buf, sizeof(buf), f)) ++count;
  std::println("1 回目: {} 行", count);
  std::println("終わりに達した: {}", std::feof(f) != 0);

  std::rewind(f);                                 // もう一度、先頭から
  std::println("rewind 後の終わり: {}", std::feof(f) != 0);
  std::fgets(buf, sizeof(buf), f);
  std::println("先頭の行: {}", buf[0]);
  std::fclose(f);
}""",
  out="""1 回目: 3 行
終わりに達した: true
rewind 後の終わり: false
先頭の行: A""",
  uses="""2 パスの処理で使います。1 回目でデータの個数を数えて、配列を確保し、`rewind` で先頭に戻って、2 回目で中身を読み込みます。ファイルを閉じて開き直すより簡単です。

一時ファイルに書き込んで、すぐ読み戻す場面にも向いています。`tmpfile()` で作ったファイルは、読み書き兼用なので、書いた後に `rewind` するだけで、中身を確かめられます。""",
  mistakes=[("終わりに達したまま読み続けようとして、何も読めない", "`fgets` が `nullptr` を返した後は、`feof` が真のままです。再び読むなら、`rewind` や `clearerr` で印を消します。"),
            ("書いた直後にそのまま読んで、不定の結果になる", "読み書き兼用のファイルでは、書き込みと読み込みの間に、`rewind`、`fseek`、`fflush` のどれかが要ります。")],
  similar=[("[`fseek`](fseek.md)", "好きな位置に動かす。戻り値で成否が分かる"),
           ("[`clearerr`](clearerr.md)", "終わりとエラーの印だけを消す")],
  memo=["先頭に戻り、印も消す", "戻り値がないので成否は分からない", "2 パスの処理に便利"])

rewrite(C + 'feof.md',
  intro="""ファイルを読むループを書くとき、「ファイルの終わりまで繰り返す」と書きたくなります。`while (!feof(f))` と書くと、最後に 1 回余計に回ってしまう、という有名な落とし穴があります。`std::feof` が何を答える関数なのかを、正しく知っておくことが大事です。

<strong>「すでに、ファイルの終わりを読もうとして失敗した」</strong>かどうかを返します。「次が終わりか」を予告する関数ではありません。""",
  tips=["`feof(f)` は、終わりを超えて読もうとしたあとで、初めて真になる",
        "ループの条件には使わない。読み込み関数の戻り値で判定する",
        "読み込みが止まった理由を調べるために使う。終わりなのか、エラーなのかを見分ける",
        "`rewind` や `clearerr` で、印を消せる"],
  details="""### std::feof {#feof}

```cpp
int feof(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 調べるファイル |

終わりの印は、読み込み関数が、ファイルの終わりを超えて読もうとしたときに立ちます。最後のデータをちょうど読み終えた時点では、まだ立っていません。次の読み込みで 0 バイトしか読めなかったときに、立ちます。

そのため、`while (!feof(f)) { fgets(...); 使う }` と書くと、最後の行を読んだあとも条件が真のままで、もう一度ループに入ります。この回の `fgets` は失敗するのに、バッファーには前の内容が残っているため、最後の行が 2 回処理されます。

正しい書き方は、読み込み関数の戻り値を条件にすることです。`while (fgets(buf, n, f))`、`while (fread(...) == n)` のように書きます。ループを抜けたあとで、`feof` と `ferror` を調べて、終わりなのかエラーなのかを見分けます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("two.txt", "w");
  std::fputs("A\\nB\\n", out);
  std::fclose(out);

  std::FILE* f = std::fopen("two.txt", "r");
  char buf[16];

  // 正しい書き方: 読み込みの戻り値を条件にする
  int n = 0;
  while (std::fgets(buf, sizeof(buf), f)) ++n;
  std::println("読んだ行数: {}", n);
  std::println("終わりに達した: {}", std::feof(f) != 0);
  std::println("エラー: {}", std::ferror(f) != 0);
  std::fclose(f);

  // 悪い書き方: feof を先に調べると、1 回多く回る
  f = std::fopen("two.txt", "r");
  int bad = 0;
  while (!std::feof(f)) {
    std::fgets(buf, sizeof(buf), f);
    ++bad;
  }
  std::println("悪い書き方の回数: {}", bad);
  std::fclose(f);
}""",
  out="""読んだ行数: 2
終わりに達した: true
エラー: false
悪い書き方の回数: 3""",
  uses="""読み込みのループを抜けたあとで、理由を調べるために使います。`feof` が真なら、最後まで読み終えた正常な終了、`ferror` が真なら、読み込み中のエラーです。エラーのときは、途中までしか読めていないので、プレイヤーにファイルの破損を知らせます。

C++ の `std::ifstream` でも、`while (std::getline(in, line))` のように、読み込みの結果を条件にするのが定番で、`in.eof()` を条件にしないのは同じ理由です。""",
  mistakes=[("`while (!feof(f))` で、最後の行が 2 回処理される", "終わりの印は、読み込みが失敗してから立ちます。読み込み関数の戻り値を条件にします。"),
            ("`feof` が偽なら正常と考える", "エラーで止まった場合も、`feof` は偽です。`ferror` も確かめます。")],
  similar=[("[`ferror`](ferror.md)", "読み書きのエラーが起きたか"),
           ("[`clearerr`](clearerr.md)", "終わりとエラーの印を消す"),
           ("`std::ios::eof`", "C++ のストリームでの同等の判定")],
  memo=["終わりを超えて読んだ後で、真になる", "ループの条件に使わない", "ループの後で、理由を調べるのに使う"])

rewrite(C + 'ferror.md',
  intro="""ファイルから読んだデータが、途中で止まっている。読み込み関数が `nullptr` や 0 を返したが、それが、ファイルの終わりに達したからなのか、ディスクの故障のようなエラーなのか、見分けられない。

`std::ferror` は、<strong>そのファイルで、読み書きのエラーが起きたか</strong>を返します。終わりに達しただけなら、真にはなりません。""",
  tips=["エラーが起きていれば 0 以外、そうでなければ 0",
        "一度起きたエラーの印は、`clearerr` か `rewind` で消すまで残る",
        "読み込みが止まった後に、`feof` と組み合わせて、終わりかエラーかを見分ける",
        "詳しい原因は `errno` と `perror` で調べる"],
  details="""### std::ferror {#ferror}

```cpp
int ferror(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 調べるファイル |

読み書きで失敗したとき、`FILE` の内部にエラーの印が立ち、`ferror` が 0 以外を返します。印は、`clearerr` や `rewind` を呼ぶまで残り続けます。

読み込みが期待より早く止まったときは、2 つの可能性があります。終わりに達した場合（`feof` が真）と、エラーが起きた場合（`ferror` が真）です。2 つは別の印なので、同時に真になることもありません。ループの後に、次のように書き分けます。

```cpp
if (std::ferror(f)) { /* 読み込みの失敗。ファイルが壊れている可能性 */ }
else { /* 正常に最後まで読んだ */ }
```

ファイルが開けなかったとき（`fopen` が `nullptr`）は、`FILE*` がないので `ferror` は使えません。`fopen` の失敗は、`errno` で調べます。""",
  code="""#include <cstdio>
#include <print>

int main() {
  // 読み取り専用で開いたファイルに書こうとして、エラーを起こす
  std::FILE* out = std::fopen("ro.txt", "w");
  std::fputs("x", out);
  std::fclose(out);

  std::FILE* f = std::fopen("ro.txt", "r");
  std::println("最初のエラー: {}", std::ferror(f) != 0);

  int r = std::fputc('Y', f);   // 読み込み用に開いたので、書けない
  std::println("fputc の戻り値が EOF: {}", r == EOF);
  std::println("その後のエラー: {}", std::ferror(f) != 0);

  std::clearerr(f);             // 印を消す
  std::println("clearerr の後: {}", std::ferror(f) != 0);
  std::fclose(f);
}""",
  out="""最初のエラー: false
fputc の戻り値が EOF: true
その後のエラー: true
clearerr の後: false""",
  uses="""セーブ データの読み込みで、読み込みが途中で止まったときの原因を分けます。終わりに達しただけなら、データが足りない（ファイルが短い）という形式の問題、エラーなら、ディスクやネットワーク ドライブの問題、と案内を変えられます。

書き込みでも、`fwrite` を何回も呼んだあと、最後に `ferror` を 1 回だけ調べて、どこかで失敗したかをまとめて確かめる使い方があります。""",
  mistakes=[("`ferror` が偽だから、ファイルは正しいと考える", "ファイルの内容の正しさとは別の話です。読み書きのエラーが無かったことしか分かりません。"),
            ("エラーの印が残ったまま、続きの処理をして失敗が続く", "印は自動では消えません。`clearerr` で消してから、やり直します。")],
  similar=[("[`feof`](feof.md)", "ファイルの終わりに達したか"),
           ("[`clearerr`](clearerr.md)", "印を消す"),
           ("[`perror`](perror.md)", "`errno` の意味を表示する")],
  memo=["読み書きのエラーが起きたか", "終わりに達しただけでは真にならない", "`clearerr` で消すまで残る"])

rewrite(C + 'fflush.md',
  intro="""ログを `fprintf` で書き出したのに、ゲームがクラッシュしたら、最後の数行がファイルに残っていなかった。書き込みはすぐにはディスクへ行かず、メモリ上のバッファーに溜められ、まとめて書き出されるからです。

`std::fflush` は、<strong>バッファーに溜まっているデータを、今すぐ書き出す</strong>関数です。""",
  tips=["出力ストリームに対して、バッファーの内容を OS へ渡す",
        "戻り値は、成功なら 0、失敗なら `EOF`",
        "OS がさらにキャッシュするので、ディスクに完全に届いたとは限らない",
        "入力ストリームに使うと未定義動作（`stdin` の入力を捨てる目的で使ってはいけない）"],
  details="""### std::fflush {#fflush}

```cpp
int fflush(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 書き出すファイル。`nullptr` を渡すと、開いているすべての出力ストリームが対象 |

出力用のバッファーに残っている分を、OS に渡します。`fclose` は、閉じる前にこの処理を自動で行うので、閉じるなら不要です。

`fflush` が成功しても、データが物理的なディスクにあるとは限りません。OS がさらに内部のキャッシュに持っている場合があります。電源が切れても残したい情報には、OS の機能（Windows の `FlushFileBuffers`、POSIX の `fsync`）まで呼びます。

ログ ファイルのように、クラッシュ時に最後まで残したいものでは、書くたびに `fflush` を呼ぶと、確実さが上がります。そのぶん、書き込みの回数が増えて遅くなるので、重要なログだけにします。

入力ストリーム（`stdin`）に `fflush` を使って、入力の読み残しを捨てる書き方は、標準では未定義動作です。MSVC では動くことがありますが、環境をまたぐと動きません。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* log = std::fopen("crash.log", "w");
  std::fputs("起動\\n", log);
  std::fflush(log);          // ここまでは、クラッシュしても残る

  // ここで別のハンドルから読むと、書いた内容が見える
  std::FILE* peek = std::fopen("crash.log", "r");
  char buf[32] = {};
  std::fgets(buf, sizeof(buf), peek);
  std::println("読めた: {}", buf);
  std::fclose(peek);

  std::fclose(log);
}""",
  out="""読めた: 起動
""",
  uses="""クラッシュ ログに使います。致命的なエラーを書いた直後に `fflush` しておけば、その後に異常終了しても、ログが残ります。通常のログは、`fflush` を呼ばず、まとめて書き出して、速さを優先します。

標準出力に進捗を表示するときも使います。`stdout` は、行が完成するまで溜められることがあるので、改行なしの進捗表示（`\\r` で上書きする表示）を出すなら、`fflush(stdout)` で、すぐ表示させます。""",
  mistakes=[("`fflush(stdin)` で入力を捨てようとする", "標準では未定義です。入力の読み残しは、`getchar` などで読み捨てます。"),
            ("`fflush` で、ディスクに確実に届いたと考える", "OS のキャッシュに残っていることがあります。電源断にも耐えるなら、OS の関数まで使います。")],
  similar=[("[`fclose`](fclose.md)", "バッファーを書き出して閉じる"),
           ("[`setvbuf`](setvbuf.md)", "バッファリングの方式を変える"),
           ("`std::flush`", "C++ のストリームでの同等の操作")],
  memo=["バッファーを今すぐ書き出す", "入力ストリームには使わない", "ディスクへの到達までは保証しない"])
print('cs2 ok')
