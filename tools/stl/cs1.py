"""cstdio の主要な関数を書き直す（バッチ 1: ファイルの開閉と読み書き）。"""
from rw import rewrite

C = 'stl/io/cstdio/'

rewrite(C + 'fopen.md',
  intro="""セーブ データを書き出したい。設定ファイルを読み込みたい。C++ では `std::ofstream` や `std::ifstream` を使うのがふつうですが、C のライブラリ（zlib、SQLite、各種ミドルウェア）は、`FILE*` を受け取る関数で動いています。それらとつなぐとき、最初に出会うのが `std::fopen` です。

<strong>ファイル名とモードを渡すと、ファイルを開いて `FILE*` を返す</strong>関数です。使い終わったら `fclose` で閉じます。""",
  tips=["戻り値は `FILE*`。開けなかったときは `nullptr`。使う前に必ず確かめる",
        "モードは `\"r\"`（読む）、`\"w\"`（書く。中身を消す）、`\"a\"`（末尾に追記）が基本",
        "バイナリを扱うなら `\"rb\"`、`\"wb\"`。Windows のテキスト モードは、改行を変換するため",
        "開いたら、必ず `fclose` する。C++ なら `unique_ptr` と組み合わせて自動化できる"],
  details="""### std::fopen {#fopen}

```cpp
std::FILE* fopen(const char* filename, const char* mode);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` | 開くファイルのパス |
| `mode` | `const char*` | 開き方を表す文字列 |

モードの意味は、次のとおりです。

`"r"` は読み込みです。ファイルが存在しないと失敗します。`"w"` は書き込みで、ファイルがなければ作り、あれば<strong>中身を空にして</strong>から書き始めます。うっかり使うと、既存のセーブ データが消えます。`"a"` は追記で、ファイルの末尾から書き足します。

後ろに `+` を付けると、読み書きの両方ができます（`"r+"`、`"w+"`、`"a+"`）。`b` を付けるとバイナリ モードです。`"rb"` のように書きます。

`b` が要るのは Windows です。テキスト モードでは、書くときに `\\n` が `\\r\\n` に、読むときに `\\r\\n` が `\\n` に変換され、バイナリ データが壊れることがあります。セーブ データ、画像、圧縮ファイルなどには、必ず `b` を付けます。

戻り値の `nullptr` は、ファイルがない、権限がない、ディスクが一杯、パスが不正、などを表します。原因は `errno` や `perror` で調べます。確かめずに使うと、`nullptr` を `fread` などに渡して落ちます。

MSVC は、`fopen` を安全でないとして警告（C4996）を出します。`fopen_s` を使うか、警告を無効にするか、`std::ofstream` を使います。""",
  code="""#include <cstdio>
#include <print>

int main() {
  // 書く。ファイルがなければ作り、あれば中身を消して書き始める
  std::FILE* out = std::fopen("save.txt", "w");
  if (!out) {
    std::println("開けなかった");
    return 1;
  }
  std::fputs("HP=100\\n", out);
  std::fclose(out);

  // 読む
  std::FILE* in = std::fopen("save.txt", "r");
  char line[64];
  std::fgets(line, sizeof(line), in);
  std::println("読んだ: {}", line);
  std::fclose(in);

  // 存在しないファイルを読むと nullptr
  std::FILE* none = std::fopen("missing.txt", "r");
  std::println("存在しない: {}", none == nullptr);
}""",
  out="""読んだ: HP=100

存在しない: true""",
  uses="""C のライブラリにファイルを渡す場面で使います。zlib の `gzdopen`、`stb_image` の `stbi_load_from_file`、SQLite などは、`FILE*` を受け取ります。自分のコードは `std::ofstream` で書き、C のライブラリとつなぐ部分だけ `fopen` を使う、と使い分けます。

`FILE*` を例外安全に扱うには、`std::unique_ptr<std::FILE, decltype(&std::fclose)> f(std::fopen(path, "rb"), &std::fclose);` と書くと、スコープを抜けるときに自動で閉じます。""",
  mistakes=[("`nullptr` を確かめずに使って落ちる", "ファイルがないだけで `nullptr` が返ります。`if (!f)` で必ず確かめます。"),
            ("`\"w\"` で既存のファイルを消してしまう", "`\"w\"` は開いた時点で中身が空になります。追記したいなら `\"a\"`、上書きしたくないなら `\"wx\"`（C11。すでにあれば失敗する）を使います。"),
            ("バイナリのデータをテキスト モードで読み書きして壊れる", "Windows では、`\\r\\n` の変換が入ります。バイナリは `\"rb\"`、`\"wb\"` です。")],
  similar=[("[`fclose`](fclose.md)", "ファイルを閉じる"),
           ("[`freopen`](freopen.md)", "開き直す"),
           ("`std::ofstream` / `std::ifstream`", "C++ のストリーム。通常はこちらを使う")],
  memo=["ファイルを開いて `FILE*` を返す", "`nullptr` を必ず確かめる", "バイナリは `\"rb\"` / `\"wb\"`"])

rewrite(C + 'fclose.md',
  intro="""ファイルを開いたら、使い終わったときに閉じなければなりません。閉じないと、書いたつもりのデータが、まだバッファーの中にあって、ディスクに届いていないことがあります。開けるファイルの数にも、OS ごとに上限があります。

`std::fclose` は、<strong>バッファーに残ったデータを書き出してから、ファイルを閉じて</strong>、`FILE*` を使えなくします。""",
  tips=["戻り値は、成功なら 0、失敗なら `EOF`。書き込みのエラーは、ここで初めて分かることがある",
        "閉じた後の `FILE*` を使ってはいけない。`nullptr` を入れておくと安全",
        "プログラムが終了すれば自動で閉じられるが、途中で閉じておくのが基本",
        "`nullptr` を渡すと未定義動作。開けたことを確かめてから呼ぶ"],
  details="""### std::fclose {#fclose}

```cpp
int fclose(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 閉じるファイル。`fopen` などで得たもの |

閉じる前に、書き込み用のバッファーに残っているデータを、ファイルへ書き出します（`fflush` と同じ処理）。このとき、ディスクが一杯だったなどの理由で書き出しに失敗すると、`fclose` が `EOF` を返します。<strong>書き込みの成否を確かめるなら、`fclose` の戻り値まで見る</strong>必要があります。`fputs` が成功していても、書き出しはここで初めて行われることがあるからです。

閉じた後の `FILE*` は、解放されたメモリを指すのと同じです。もう一度 `fclose` したり、`fgets` に渡したりすると、未定義動作です。閉じたら `f = nullptr;` としておくと、誤用に気づきやすくなります。

`stdin`、`stdout`、`stderr` は閉じません。プログラムが開始と終了に自動で扱います。""",
  code="""#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("log.txt", "w");
  std::fputs("start\\n", f);

  int r = std::fclose(f);   // バッファーの内容を書き出して閉じる
  f = nullptr;              // 閉じた FILE* を使わないように
  std::println("fclose の戻り値: {}", r);

  // 閉じた後なので、内容が読める
  std::FILE* in = std::fopen("log.txt", "r");
  char buf[16];
  std::fgets(buf, sizeof(buf), in);
  std::println("中身: {}", buf);
  std::fclose(in);
}""",
  out="""fclose の戻り値: 0
中身: start
""",
  uses="""セーブ データの書き込みでは、`fclose` の戻り値を確かめます。ディスクの空きが足りなかった場合、`fputs` が成功を返しても、`fclose` で初めて失敗が分かります。失敗したら、書きかけのファイルを消し、前のセーブ データを残します。

C++ では、`unique_ptr` に削除関数として `fclose` を渡すと、例外が起きても閉じ忘れません。ただし、戻り値を確かめる場面（セーブ）では、明示的に `fclose` を呼びます。""",
  mistakes=[("閉じ忘れて、データが書き出されない", "プログラムが異常終了すると、バッファーが書き出されません。書き終わったらすぐ閉じます。"),
            ("閉じた後の `FILE*` を使う", "閉じたあとは使えません。`nullptr` を代入する習慣をつけます。")],
  similar=[("[`fopen`](fopen.md)", "ファイルを開く"),
           ("[`fflush`](fflush.md)", "閉じずにバッファーだけを書き出す")],
  memo=["バッファーを書き出して閉じる", "戻り値で書き込みの失敗が分かる", "閉じたら使わない"])
print('cs1 ok')
