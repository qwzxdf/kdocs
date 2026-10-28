"""io ルートの操作子を書き直す（バッチ 1: 整数の基数、幅、そろえ、浮動小数点の書式）。"""
from rw import rewrite

I = 'stl/io/'


def sig(name, params, desc):
    return None


rewrite(I + 'hex.md',
  intro="""ピクセルの色を 16 進数で `FF8800` と表示したい。メモリのアドレスやフラグの値を、16 進数で確かめたい。`std::cout << 255` は、10 進数の `255` を出します。ストリームの基数を切り替える操作子の 1 つが `std::hex` です。

<strong>以降の整数の出力と入力を、16 進数にする</strong>操作子です。`std::cout << std::hex << 255` で `ff` と出ます。""",
  tips=["`std::hex` を流すと、そのストリームの整数の基数が 16 進数に変わる",
        "設定は残り続ける。戻すには `std::dec`",
        "英字は小文字。大文字にするには `std::uppercase`、`0x` を付けるには `std::showbase`",
        "負の数は、符号なしとして解釈されたビット列（`ffffffff` など）で出る"],
  details="""### std::hex {#hex}

```cpp
std::ios_base& hex(std::ios_base& str);
```

`std::cout << std::hex` のように、ストリームに流して使います。引数は、ストリームの書式フラグで、`basefield`（基数のグループ）を 16 進数に設定します。10 進数なら [`dec`](dec.md)、8 進数なら [`oct`](oct.md)です。

効果は、<strong>設定を戻すまで続きます</strong>。1 回の出力で終わりではないので、`hex` の後に出した整数は、すべて 16 進数になります。ログの途中で `hex` を使って、戻し忘れると、その後の数値が全部 16 進数で出て、混乱します。

標準では、`hex` で出る英字は小文字です。`std::uppercase` を併用すると大文字になり、`std::showbase` を併用すると、先頭に `0x` が付きます。

`bool` や `char` には効きません。`char` はそのまま文字として出るので、バイトを 16 進数で見たいときは、`int` に変換して出します。

C++23 の `std::print` では、`{:x}` のように書式で指定できて、設定が残る問題がありません。新しいコードでは、そちらのほうが安全です。""",
  code="""#include <iostream>

int main() {
  int color = 0xFF8800;

  std::cout << std::hex << color << '\\n';                       // ff8800
  std::cout << std::uppercase << color << '\\n';                 // FF8800
  std::cout << std::showbase << 255 << '\\n';                    // 0XFF
  std::cout << std::dec << std::nouppercase << std::noshowbase;  // 元に戻す
  std::cout << 255 << '\\n';                                     // 255

  // バイトを 16 進数で見たいときは、int に変換する
  unsigned char byte = 0x7F;
  std::cout << std::hex << static_cast<int>(byte) << '\\n';
}""",
  out="""ff8800
FF8800
0XFF
255
7f""",
  uses="""色コード、メモリのアドレス、フラグのビット列を、ログや画面に出すときに使います。ゲーム エンジンのデバッグ出力で、ハンドルや ID を 16 進数で出すのは定番です。

設定が残る性質のため、ログ関数の中で使うときは、出力のあとで必ず `dec` に戻すか、ストリームの状態を保存・復元します。`std::format` や `std::print` なら、この問題はありません。""",
  mistakes=[("`hex` を戻さず、その後の数値が全部 16 進数になる", "`std::dec` で戻します。ログ関数ごとに状態を戻す習慣をつけます。"),
            ("`char` を `hex` で出しても、文字のまま出る", "`static_cast<int>` で整数にします。"),
            ("`std::cout << std::hex << 255.0` が効かない", "基数は整数だけに効きます。浮動小数点数の 16 進表記は `hexfloat` です。")],
  similar=[("[`dec`](dec.md)", "10 進数にする"),
           ("[`oct`](oct.md)", "8 進数にする"),
           ("[`setbase`](setbase.md)", "基数を数値で指定する"),
           ("[`showbase`](showbase.md)", "`0x` を付ける")],
  memo=["以降の整数を 16 進数にする", "戻すまで続く", "大文字は `uppercase`、`0x` は `showbase`"])

rewrite(I + 'dec.md',
  intro="""`hex` で 16 進数にした出力を、元の 10 進数に戻したい。ストリームの基数は、設定が残り続けるので、いったん変えたら、戻す操作が必要です。それが `std::dec` です。

<strong>整数の入出力を 10 進数にする</strong>操作子で、ストリームの既定の状態です。""",
  tips=["ストリームの既定は 10 進数。`dec` は、`hex` や `oct` から戻すために使う",
        "入力にも効く。`std::cin >> std::hex >> x` で、16 進数の文字列を読み取れる",
        "設定は、次に変えるまで残る",
        "`std::cout << std::dec` は、現在の基数に関係なく 10 進数にする"],
  details="""### std::dec {#dec}

```cpp
std::ios_base& dec(std::ios_base& str);
```

ストリームの書式フラグのうち、基数のグループ（`basefield`）を 10 進数にします。出力だけでなく、入力にも効くので、`std::cin >> std::dec >> n` は、`0x` で始まる入力も 10 進数として読もうとします（`0` で止まります）。

基数を指定せず、入力から自動で判定させたい場合は、`std::cin >> std::setbase(0) >> n` とします。`0x` なら 16 進数、`0` で始まれば 8 進数、そうでなければ 10 進数として読みます。

`hex` を使う関数の後始末として、`dec` を呼ぶのが定番です。ストリームの状態を一時的に変えて、元に戻す処理は、保存と復元（`std::ios::fmtflags f = os.flags(); ... os.flags(f);`）でも書けます。""",
  code="""#include <iostream>

int main() {
  std::cout << std::hex << 255 << '\\n';   // ff
  std::cout << 255 << '\\n';               // hex が残っているので ff
  std::cout << std::dec << 255 << '\\n';   // 255 に戻る

  int n = 0;
  std::cin >> std::dec >> n;
  std::cout << "入力なし: " << std::cin.fail() << '\\n';
}""",
  out="""ff
ff
255
入力なし: 1""",
  uses="""16 進数や 8 進数で出したあとに、元の表示へ戻すときに使います。ログ関数やデバッグ出力の関数の最後に `std::dec` を流して、呼び出し側の出力に影響しないようにします。""",
  mistakes=[("`hex` の後に戻さず、数値の表示が崩れる", "戻す操作を忘れずに入れます。")],
  similar=[("[`hex`](hex.md)", "16 進数にする"),
           ("[`oct`](oct.md)", "8 進数にする"),
           ("[`setbase`](setbase.md)", "基数を数値で指定する")],
  memo=["整数を 10 進数にする", "既定の状態に戻す", "入力にも効く"])

rewrite(I + 'oct.md',
  intro="""Unix のファイル権限は、`0644` のように 8 進数で表します。`std::cout << 420` では `420` と出るところを、`644` と表示したい。整数を 8 進数にする操作子が `std::oct` です。""",
  tips=["`std::cout << std::oct << 420` で `644` と出る",
        "戻すには `std::dec`。設定は残り続ける",
        "`std::showbase` を併用すると、先頭に `0` が付く",
        "入力にも効く。`0` で始まる文字列を 8 進数として読む"],
  details="""### std::oct {#oct}

```cpp
std::ios_base& oct(std::ios_base& str);
```

ストリームの基数を 8 進数にします。[`hex`](hex.md) の 8 進数版で、残り続ける性質も同じです。

`showbase` と併用すると、8 進数の印として、先頭に `0` が付きます（`0644`）。ただし値が 0 のときは、`0` だけです。

ゲームで 8 進数を使う場面は少ないのですが、ファイルの権限（`std::filesystem::perms` の値は 8 進数で定義されています）を表示するときは、`std::cout << std::oct << static_cast<unsigned>(perms)` と書くと、`chmod` と同じ見た目で確認できます。""",
  code="""#include <iostream>

int main() {
  std::cout << std::oct << 420 << '\\n';              // 644
  std::cout << std::showbase << 420 << '\\n';         // 0644
  std::cout << std::noshowbase << std::dec << 420 << '\\n';   // 420
}""",
  out="""644
0644
420""",
  uses="""ファイルの権限の確認や、古い形式のデータの解析で使います。ゲーム本体で使うことは、あまりありません。""",
  mistakes=[("戻し忘れて、数値の表示が崩れる", "`std::dec` で戻します。")],
  similar=[("[`hex`](hex.md)", "16 進数にする"),
           ("[`dec`](dec.md)", "10 進数にする"),
           ("[`setbase`](setbase.md)", "基数を数値で指定する")],
  memo=["整数を 8 進数にする", "戻すまで続く", "権限の表示に使う"])

rewrite(I + 'setbase.md',
  intro="""`hex`、`dec`、`oct` は、基数をそれぞれ名前で選びます。変数で基数を切り替えたい（ユーザーが選んだ表示形式に従う）ときは、数値で指定できる `std::setbase` が便利です。""",
  tips=["`std::setbase(16)` は `std::hex` と同じ。8 と 10 も使える",
        "それ以外の数を渡すと、10 進数になる（出力）",
        "入力では `setbase(0)` が特別で、接頭辞から基数を自動判定する",
        "`<iomanip>` が必要"],
  details="""### std::setbase {#setbase}

```cpp
/* 未規定 */ setbase(int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `base` | `int` | 基数。8、10、16 のいずれか。ほかの値は 10 進数になる |

出力では、`8`、`10`、`16` のどれかを受け付けます。2 進数は指定できません。2 進数で出したいときは、`std::bitset` を使うか、`std::format("{:b}", n)` を使います。

入力では、`0` を渡すと、接頭辞による自動判定になります。`0x1F` は 16 進数、`017` は 8 進数、`17` は 10 進数として読まれます。設定ファイルから、基数の決まっていない数値を読むときに便利です。

使うには `<iomanip>` が必要です。`hex` などは `<ios>` に入っているのと、違う点です。""",
  code="""#include <iomanip>
#include <iostream>
#include <sstream>

int main() {
  std::cout << std::setbase(16) << 255 << '\\n';   // ff
  std::cout << std::setbase(8) << 255 << '\\n';    // 377
  std::cout << std::setbase(10) << 255 << '\\n';   // 255

  // 入力: 0 を指定すると、接頭辞で判定する
  std::istringstream in("0x1F 017 17");
  int a, b, c;
  in >> std::setbase(0) >> a >> b >> c;
  std::cout << a << ' ' << b << ' ' << c << '\\n';
}""",
  out="""ff
377
255
31 15 17""",
  uses="""ユーザーが表示形式を選べるツール（メモリ ビューアーなど）で、基数を変数で切り替えるときに使います。設定ファイルで、数値が 10 進数なのか 16 進数なのかが混在する場合の読み込みにも使えます。""",
  mistakes=[("2 進数を指定して、10 進数になる", "`setbase` は 8、10、16 だけです。2 進数は `bitset` か `std::format` を使います。"),
            ("`<iomanip>` を include し忘れてコンパイル エラー", "`hex` などと違い、`<iomanip>` が必要です。")],
  similar=[("[`hex`](hex.md)", "16 進数にする"),
           ("[`dec`](dec.md)", "10 進数にする"),
           ("[`oct`](oct.md)", "8 進数にする")],
  memo=["基数を数値で指定する", "入力では `0` で自動判定", "`<iomanip>` が要る"])

rewrite(I + 'setw.md',
  intro="""ステータス画面を文字で表示するとき、名前と数値を縦にそろえて並べたい。文字数の違う名前を、同じ幅の欄に収めたい。次の出力の「最小の幅」を指定するのが `std::setw` です。""",
  tips=["`std::setw(10)` で、次の 1 つの出力を、10 文字分の幅の欄に入れる",
        "<strong>次の 1 回の出力にしか効かない</strong>。毎回指定し直す",
        "既定では、右にそろえる。左にそろえるなら `std::left`",
        "幅より長い文字列は、切り詰められず、はみ出す"],
  details="""### std::setw {#setw}

```cpp
/* 未規定 */ setw(int n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `int` | 次の出力の最小の幅（文字数） |

次の出力が `n` 文字に満たなければ、足りない分を詰め物（既定では空白）で埋めます。詰め物は [`setfill`](setfill.md) で変えられ、どちら側に埋めるかは [`left`](left.md)、[`right`](right.md)、[`internal`](internal.md) で決まります。

他の操作子と違って、<strong>幅の指定は、1 回の出力で解除されます</strong>。`std::cout << std::setw(5) << a << b` と書くと、`a` は幅 5 で出ますが、`b` は幅の指定なしで出ます。表を作るときは、各欄の前に毎回 `setw` を書きます。

幅より長い内容は、切り詰められません。欄をはみ出して、そのまま出ます。

日本語の全角文字は、幅としては 1 文字と数えられ、画面上の見た目では 2 文字分の幅を取ります。`setw` は文字数で数えるので、日本語を含む表は、そろいません。表示幅の計算は、別に自前で行う必要があります。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::left;                    // 左にそろえる
  std::cout << std::setw(8) << "name" << std::setw(5) << "hp" << '|' << '\\n';
  std::cout << std::setw(8) << "hero" << std::setw(5) << 100 << '|' << '\\n';
  std::cout << std::setw(8) << "slime" << std::setw(5) << 7 << '|' << '\\n';

  // 幅は 1 回の出力で解除される
  std::cout << std::right << std::setw(5) << 1 << 2 << '\\n';

  // 幅より長いと、はみ出す
  std::cout << std::setw(2) << "long" << '\\n';
}""",
  out="""name    hp   |
hero    100  |
slime   7    |
    12
long""",
  uses="""コンソール ツールのログや、デバッグ表示で、表の形に並べるときに使います。ステータス、アセット名とサイズの一覧、プロファイラーの結果などです。

C++20 以降は、`std::format("{:<8}{:>5}", name, hp)` のように、書式の中で幅とそろえを指定できます。設定が残らない点で、`setw` より扱いやすいので、新しいコードではそちらを選びます。""",
  mistakes=[("幅の指定が続くと思って、2 つ目以降がそろわない", "毎回 `setw` を書きます。"),
            ("日本語を含む表がずれる", "文字数と表示幅が違います。表示幅を別に計算するか、日本語を含まない欄でそろえます。")],
  similar=[("[`setfill`](setfill.md)", "詰め物の文字を指定する"),
           ("[`left`](left.md)", "左にそろえる"),
           ("[`right`](right.md)", "右にそろえる")],
  memo=["次の 1 回の出力の最小の幅を決める", "毎回指定する", "はみ出す分は切らない"])

rewrite(I + 'setfill.md',
  intro="""スコアを `00042` のように、ゼロ埋めで表示したい。`setw` で幅を指定すると、足りない分は空白で埋まります。その詰め物を、ほかの文字に変えるのが `std::setfill` です。""",
  tips=["`std::setfill('0')` で、詰め物をゼロにする。`setw` と組み合わせて使う",
        "<strong>`setw` と違い、設定が残り続ける</strong>。戻すには `setfill(' ')`",
        "`setw` で決めた幅に対して効く。幅がないと、詰め物は使われない",
        "引数は `char`（ワイド ストリームなら `wchar_t`）"],
  details="""### std::setfill {#setfill}

```cpp
template <class CharT>
/* 未規定 */ setfill(CharT c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | 文字型 | 詰め物にする文字 |

[`setw`](setw.md) で幅を決めたとき、内容が幅に足りない分を、`c` で埋めます。既定は空白です。

`setw` の効果は 1 回の出力で解除されますが、`setfill` は、変えるまで残り続けます。ゼロ埋めの表示をしたあと、`setfill('0')` を戻さないと、その後の `setw` を使った出力が、すべてゼロ埋めになります。

数値のゼロ埋めには、`std::internal` と組み合わせて、符号を左に、数字を右に寄せる使い方もあります（`-0042`）。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setfill('0') << std::setw(5) << 42 << '\\n';     // 00042
  std::cout << std::setw(5) << 7 << '\\n';                          // setfill が残るので 00007

  std::cout << std::setfill('*') << std::left << std::setw(8) << "hi" << "|\\n";   // hi******|

  // 元に戻す
  std::cout << std::setfill(' ') << std::right << std::setw(5) << 7 << '\\n';
}""",
  out="""00042
00007
hi******|
    7""",
  uses="""連番のファイル名（`shot_0001.png`）、タイマーの表示（`03:07`）、スコアの桁そろえで使います。

C++20 以降なら、`std::format("{:05}", 42)` のように、書式の中でゼロ埋めを指定できます。設定が残らないので、安全です。""",
  mistakes=[("`setfill` が残って、あとの出力がずっと埋まる", "使い終わったら `setfill(' ')` に戻します。"),
            ("`setw` なしで使って、効果がない", "`setw` で幅を決めた欄にだけ使われます。")],
  similar=[("[`setw`](setw.md)", "幅を決める"),
           ("[`internal`](internal.md)", "符号と数字の間を埋める")],
  memo=["詰め物の文字を決める", "設定は残り続ける", "`setw` と組み合わせる"])

rewrite(I + 'left.md',
  intro="""`setw` で幅を決めた欄に、内容が収まるとき、余りの空白は、左と右のどちらに入るのでしょう。既定では、内容が右に寄り、空白は左に入ります。名前の列のように、左に寄せたいときは、`std::left` を使います。""",
  tips=["`std::left` で、幅の欄の内容を左に寄せ、余りを右に詰める",
        "設定は残り続ける。戻すには `std::right`",
        "`setw` で幅を決めた欄にだけ効く",
        "文字列にも数値にも効く"],
  details="""### std::left {#left}

```cpp
std::ios_base& left(std::ios_base& str);
```

[`setw`](setw.md) で決めた幅の中で、内容を左端に置きます。余った分は、右側に詰め物（既定は空白）で埋められます。

名前や説明のような文字列の列は左そろえ、数値の列は右そろえ、が表の見やすい基本です。そのため、表の中で `left` と `right` を切り替える場面が出てきます。

設定が残るので、列ごとに切り替えるなら、その都度流します。`internal` は、符号や基数の印を左に、数字を右に寄せる、数値専用の指定です。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::left  << std::setw(8) << "name" << '|' << '\\n';
  std::cout << std::right << std::setw(8) << "name" << '|' << '\\n';
}""",
  out="""name    |
    name|""",
  uses="""コンソール表示の表で、名前の列を左にそろえるときに使います。数値の列は `right` にして、桁をそろえます。""",
  mistakes=[("`setw` なしで使って、効果が見えない", "幅を決めた欄の中でだけ意味があります。")],
  similar=[("[`right`](right.md)", "右に寄せる"),
           ("[`internal`](internal.md)", "符号と数字の間を埋める"),
           ("[`setw`](setw.md)", "幅を決める")],
  memo=["幅の欄で左に寄せる", "設定は残る", "名前の列に向く"])

rewrite(I + 'right.md',
  intro="""数値の列は、桁をそろえるために、右にそろえたい。`std::right` は、`setw` で決めた幅の欄で、<strong>内容を右に寄せ、余りを左に詰め</strong>ます。出力ストリームの既定の状態でもあります。""",
  tips=["`std::right` で、幅の欄の内容を右に寄せ、余りを左に詰める",
        "ストリームの既定は右そろえ。`left` の後に戻すときに使う",
        "設定は残り続ける",
        "`setw` で幅を決めた欄にだけ効く"],
  details="""### std::right {#right}

```cpp
std::ios_base& right(std::ios_base& str);
```

[`setw`](setw.md) で決めた幅の中で、内容を右端に置きます。余った分は、左側が詰め物で埋まります。

数値の列は、桁数が違っても、1 の位がそろうほうが、読みやすくなります。名前の列を `left`、数値の列を `right` にして表を作るのが、基本の形です。

出力の既定が右そろえなので、何も指定しなくても同じ見た目になりますが、前に `left` を流した後なら、`right` で戻す必要があります。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::right;
  std::cout << std::setw(6) << 1 << '\\n';
  std::cout << std::setw(6) << 100 << '\\n';
  std::cout << std::setw(6) << 12345 << '\\n';
}""",
  out="""     1
   100
 12345""",
  uses="""数値の列を右にそろえて、桁を見やすくするときに使います。プロファイラーの結果、スコアのランキング、ダメージの一覧などです。""",
  mistakes=[("`left` を流したまま、数値の列もずれる", "数値の列の前に `right` を流します。")],
  similar=[("[`left`](left.md)", "左に寄せる"),
           ("[`internal`](internal.md)", "符号と数字の間を埋める"),
           ("[`setw`](setw.md)", "幅を決める")],
  memo=["幅の欄で右に寄せる", "既定の状態", "数値の列に向く"])

rewrite(I + 'internal.md',
  intro="""負の数をゼロ埋めで表示すると、`00-42` のように、符号が数字の間に入って見づらくなります。符号は左端に、数字は右端に置いて、その間を詰め物で埋めたい。そのための寄せ方が `std::internal` です。""",
  tips=["`std::internal` で、符号や基数の印（`0x`）を左端に、数字を右端に置き、間を埋める",
        "`setfill('0')` と組み合わせて、`-0042` や `0x00ff` の形にする",
        "数値にだけ意味がある。文字列では右そろえと同じ",
        "設定は残り続ける"],
  details="""### std::internal {#internal}

```cpp
std::ios_base& internal(std::ios_base& str);
```

`setw` で決めた幅の中で、符号（`-`、`+`）と基数の印（`0x`）を左端に、数字の部分を右端に置き、間を詰め物で埋めます。

`std::right` と `setfill('0')` の組み合わせだと、詰め物は数値全体の左に入るので、`-42` が `000-42` になります。`internal` なら、`-0042` になります。符号つきの数値をゼロ埋めするときの、正しい形です。

16 進数で `showbase` を併用すると、`0x` が左に残り、数字がゼロで埋まります（`0x00ff`）。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setfill('0');

  std::cout << std::right << std::setw(6) << -42 << '\\n';      // 000-42
  std::cout << std::internal << std::setw(6) << -42 << '\\n';   // -00042

  std::cout << std::hex << std::showbase << std::setw(8) << 255 << '\\n';   // 0x0000ff
}""",
  out="""000-42
-00042
0x0000ff""",
  uses="""符号つきの数値や、16 進数のアドレスを、固定の幅でゼロ埋めして表示するときに使います。メモリのダンプや、座標の表示で見かけます。

C++20 以降の `std::format("{:+06}", -42)` でも、同じ形（`-00042`）が書けます。""",
  mistakes=[("`right` とゼロ埋めで、符号が間に入る", "`internal` を使います。"),
            ("文字列に使って、効果がないと思う", "文字列では右そろえと同じです。数値向けの指定です。")],
  similar=[("[`left`](left.md)", "左に寄せる"),
           ("[`right`](right.md)", "右に寄せる"),
           ("[`setfill`](setfill.md)", "詰め物を決める")],
  memo=["符号と数字の間を埋める", "ゼロ埋めの数値に向く", "設定は残る"])

rewrite(I + 'setprecision.md',
  intro="""`std::cout << 3.14159265` は、既定では `3.14159` と出ます。小数点以下 2 桁で出したい。有効数字を 10 桁出したい。浮動小数点数の「桁数」を決めるのが `std::setprecision` です。""",
  tips=["`std::setprecision(n)` で、浮動小数点数の精度（桁数）を `n` にする",
        "<strong>既定の書式では「有効数字の桁数」、`fixed` や `scientific` と併用すると「小数点以下の桁数」</strong>になる",
        "設定は残り続ける",
        "`<iomanip>` が必要"],
  details="""### std::setprecision {#setprecision}

```cpp
/* 未規定 */ setprecision(int n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `int` | 精度。書式によって意味が変わる |

精度の意味が、書式のフラグによって変わるのが、いちばん混乱するところです。

何も指定しない既定の書式（`defaultfloat`）では、`n` は<strong>有効数字の桁数</strong>です。`setprecision(3)` で `3.14159` は `3.14`、`314.159` は `314`、`3141.59` は `3.14e+03` になります。整数部が長いと、指数表記に切り替わります。

[`fixed`](fixed.md) と併用すると、`n` は<strong>小数点以下の桁数</strong>になります。`fixed << setprecision(2)` で `3.14159` は `3.14`、`314.159` は `314.16` です。固定の小数点以下の桁数で表示したいなら、この形です。

[`scientific`](scientific.md) と併用しても、小数点以下の桁数です。

既定の精度は 6 です。`double` を完全に往復できる桁数にするには、17 桁（`std::numeric_limits<double>::max_digits10`）が必要です。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  double v = 3.14159265;

  std::cout << std::setprecision(3) << v << '\\n';                       // 有効数字 3 桁: 3.14
  std::cout << std::setprecision(3) << 314.159 << '\\n';                 // 314
  std::cout << std::fixed << std::setprecision(2) << v << '\\n';         // 小数点以下 2 桁: 3.14
  std::cout << std::fixed << std::setprecision(2) << 314.159 << '\\n';   // 314.16
}""",
  out="""3.14
314
3.14
314.16""",
  uses="""座標、スコア、時間の表示で、小数点以下の桁数をそろえるときに使います。`fixed` と組み合わせて、`std::fixed << std::setprecision(2)` と書くのが定番です。

C++20 以降では、`std::format("{:.2f}", v)` で同じことが、設定を残さずに書けます。""",
  mistakes=[("`fixed` なしで使って、有効数字になる", "小数点以下の桁数が欲しいなら、`fixed` を併用します。"),
            ("設定が残って、あとの表示が変わる", "使い終わったら、元の精度（6）と `defaultfloat` に戻します。")],
  similar=[("[`fixed`](fixed.md)", "小数点以下の桁数にする"),
           ("[`scientific`](scientific.md)", "指数表記にする"),
           ("[`defaultfloat`](defaultfloat.md)", "既定の書式に戻す")],
  memo=["浮動小数点数の桁数を決める", "`fixed` だと小数点以下", "設定は残る"])

rewrite(I + 'fixed.md',
  intro="""座標を `10.5` と `10.50` のどちらで出すか。桁をそろえて、小数点以下を必ず 2 桁出したい。浮動小数点数を、指数表記ではなく、固定小数点の形で出すのが `std::fixed` です。""",
  tips=["`std::fixed` で、`123.456000` のような固定小数点の形で出す",
        "`setprecision(n)` と組み合わせると、小数点以下 `n` 桁になる",
        "精度の既定は 6 桁。`fixed` だけなら、`3.140000` と出る",
        "設定は残り続ける。戻すには `defaultfloat`"],
  details="""### std::fixed {#fixed}

```cpp
std::ios_base& fixed(std::ios_base& str);
```

浮動小数点数を、`123.456` のような固定小数点の形で出します。桁が大きくても小さくても、指数表記（`1.23e+10`）には切り替わりません。

[`setprecision`](setprecision.md) との組み合わせが前提です。`fixed` を流すと、精度の意味が「小数点以下の桁数」に変わります。`fixed` だけで精度を指定しないと、既定の 6 桁になり、`3.140000` のように末尾のゼロが並びます。

表示が必要な桁数を超えた部分は、四捨五入されます。`std::fixed << std::setprecision(1) << 0.25` は、`0.2` か `0.3` のどちらかになります。浮動小数点数の内部表現が 2 進数のため、0.25 は正確に表せますが、丸め方は偶数丸めが一般的で `0.2` です。

整数には効きません。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::fixed;
  std::cout << 3.14 << '\\n';                         // 3.140000（既定の精度 6）
  std::cout << std::setprecision(2) << 3.14159 << '\\n';   // 3.14
  std::cout << 1e10 << '\\n';                         // 指数表記にならない
  std::cout << 0.5 << '\\n';                          // 0.50
}""",
  out="""3.140000
3.14
10000000000.00
0.50""",
  uses="""座標、体力の割合、経過時間の表示で、小数点以下の桁数をそろえるときに使います。桁がそろうと、一覧表が読みやすくなります。

C++20 の `std::format("{:.2f}", v)` なら、設定を残さずに同じ表示ができます。""",
  mistakes=[("`fixed` を流したまま、あとの数値が全部固定小数点になる", "`std::defaultfloat` で戻します。"),
            ("`setprecision` を忘れて、`3.140000` が出る", "桁数を指定します。")],
  similar=[("[`scientific`](scientific.md)", "指数表記にする"),
           ("[`defaultfloat`](defaultfloat.md)", "既定の書式に戻す"),
           ("[`setprecision`](setprecision.md)", "桁数を決める")],
  memo=["固定小数点の形で出す", "`setprecision` で小数点以下の桁数", "戻すのは `defaultfloat`"])

rewrite(I + 'scientific.md',
  intro="""とても大きい値や小さい値（`6.02e23` や `1e-9`）を、桁数に悩まずに、指数表記で出したい。浮動小数点数を、`1.234560e+03` の形で出すのが `std::scientific` です。""",
  tips=["`std::scientific` で、`d.ddddde+XX` の形（仮数と指数）で出す",
        "`setprecision(n)` と組み合わせると、仮数の小数点以下 `n` 桁になる",
        "大文字の `E` にするなら `std::uppercase`",
        "設定は残り続ける。戻すには `defaultfloat`"],
  details="""### std::scientific {#scientific}

```cpp
std::ios_base& scientific(std::ios_base& str);
```

浮動小数点数を、仮数部が 1 以上 10 未満の、指数表記で出します。`1234.5` は `1.234500e+03` です。

[`setprecision`](setprecision.md) と組み合わせると、精度は<strong>仮数部の小数点以下の桁数</strong>になります。`setprecision(2)` なら `1.23e+03` です。

科学計算やログで、桁の大きさをそろえて比べたいとき、極端な値を見やすく出したいときに使います。ゲームでは、物理シミュレーションの誤差や、確率の小さな値の表示などで出てきます。

既定の書式（`defaultfloat`）でも、桁数が多いと自動で指数表記に切り替わります。`scientific` は、それを常に強制する指定です。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::scientific;
  std::cout << 1234.5 << '\\n';                           // 1.234500e+03
  std::cout << std::setprecision(2) << 1234.5 << '\\n';   // 1.23e+03
  std::cout << 0.000123 << '\\n';                         // 1.23e-04
  std::cout << std::uppercase << 1234.5 << '\\n';         // 1.23E+03
}""",
  out="""1.234500e+03
1.23e+03
1.23e-04
1.23E+03""",
  uses="""物理演算の誤差、確率、非常に大きな座標など、桁の幅が広い値のデバッグ出力で使います。

`std::format("{:.2e}", v)` でも書けて、設定が残りません。""",
  mistakes=[("戻し忘れて、あとの数値が全部指数表記になる", "`std::defaultfloat` で戻します。")],
  similar=[("[`fixed`](fixed.md)", "固定小数点にする"),
           ("[`defaultfloat`](defaultfloat.md)", "既定の書式に戻す"),
           ("[`hexfloat`](hexfloat.md)", "16 進の浮動小数点表記にする")],
  memo=["指数表記で出す", "`setprecision` で仮数部の桁数", "戻すのは `defaultfloat`"])

rewrite(I + 'defaultfloat.md',
  intro="""`fixed` や `scientific` を使ったあと、元の「ちょうどよく選ぶ」書式に戻したい。`std::defaultfloat` は、<strong>浮動小数点数の書式を、既定の状態に戻す</strong>操作子です。値の大きさで、固定小数点と指数表記を自動で選びます。""",
  tips=["`fixed` と `scientific` の両方を解除する。ストリームの初期状態の書式",
        "精度は「有効数字の桁数」になる（既定は 6）",
        "値が大きすぎる、または小さすぎると、指数表記に自動で切り替わる",
        "末尾の 0 は省かれる（`3.5` が `3.500000` にならない）"],
  details="""### std::defaultfloat {#defaultfloat}

```cpp
std::ios_base& defaultfloat(std::ios_base& str);
```

`fixed` と `scientific` のフラグを両方消します。出力は `printf` の `%g` に相当する書式になります。精度の桁数の有効数字で、値に応じて固定小数点か指数表記かを選び、末尾の不要な 0 は出しません。

`std::cout << 3.5` が `3.5` と出て、`3.500000` にならないのは、この書式のためです。

`fixed` / `scientific` の設定は残るので、使ったあとの後始末に `defaultfloat` を流します。精度も変えていたなら、`std::setprecision(6)` で戻します。""",
  code="""#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::fixed << std::setprecision(2) << 3.14159 << '\\n';   // 3.14
  std::cout << std::defaultfloat << std::setprecision(6);                // 元に戻す
  std::cout << 3.5 << '\\n';                                             // 3.5
  std::cout << 1234567.0 << '\\n';                                       // 1.23457e+06
  std::cout << 0.0001 << '\\n';                                          // 0.0001
}""",
  out="""3.14
3.5
1.23457e+06
0.0001""",
  uses="""ログ関数が、`fixed` などを使った後に、呼び出し側のストリームの状態を壊さないよう、最後に戻すために使います。""",
  mistakes=[("`defaultfloat` だけで精度が戻ると思う", "精度は別の設定です。`setprecision(6)` で戻します。")],
  similar=[("[`fixed`](fixed.md)", "固定小数点にする"),
           ("[`scientific`](scientific.md)", "指数表記にする"),
           ("[`hexfloat`](hexfloat.md)", "16 進の浮動小数点表記にする")],
  memo=["浮動小数点の書式を既定に戻す", "値の大きさで自動選択", "精度は別に戻す"])

rewrite(I + 'showpos.md',
  intro="""ダメージの増減を「+10」「-5」のように、符号つきで表示したい。`std::cout << 10` は `10` と出て、プラスの符号は付きません。`std::showpos` は、<strong>0 以上の数値にも `+` を付けて</strong>出します。""",
  tips=["`std::showpos` で、正の数や 0 に `+` を付けて出す",
        "負の数は、いつも `-` が付く",
        "設定は残る。戻すには `std::noshowpos`",
        "整数にも浮動小数点数にも効く"],
  details="""### std::showpos {#showpos}

```cpp
std::ios_base& showpos(std::ios_base& str);
```

`showpos` フラグを立てます。0 以上の数値を出力するとき、先頭に `+` を付けます。0 も `+0` になります。

増減を表す値（ダメージ、回復量、補正値、ゲージの変化）の表示で、符号が見えると、意味が伝わりやすくなります。

`hex` と組み合わせた場合、符号つきの数値の 16 進表記は、環境によって扱いが異なります。符号の付く 10 進数に使うのが無難です。

`noshowpos` で元に戻します。C++20 の `std::format("{:+}", n)` も、同じ表示ができます。""",
  code="""#include <iostream>

int main() {
  std::cout << std::showpos;
  std::cout << 10 << ' ' << -5 << ' ' << 0 << ' ' << 2.5 << '\\n';
  std::cout << std::noshowpos << 10 << '\\n';
}""",
  out="""+10 -5 +0 +2.5
10""",
  uses="""ダメージ表示の「+12」「-3」、補正値の表示、差分の表示などで使います。増えたのか減ったのかが、符号で分かります。""",
  mistakes=[("戻し忘れて、他の数値にも `+` が付く", "`noshowpos` で戻します。")],
  similar=[("[`showbase`](showbase.md)", "基数の印を付ける"),
           ("[`showpoint`](showpoint.md)", "小数点を必ず出す")],
  memo=["正の数にも `+` を付ける", "設定は残る", "戻すのは `noshowpos`"])

rewrite(I + 'showbase.md',
  intro="""16 進数で `ff` と出ただけでは、`ff` という文字列なのか、10 進の何かなのか、紛らわしい。`0xff` のように、基数の印を付けて出したい。そのための操作子が `std::showbase` です。""",
  tips=["`std::showbase` で、16 進数に `0x`、8 進数に `0` を付ける",
        "10 進数には付かない",
        "`std::uppercase` を併用すると `0X` と大文字になる",
        "設定は残る。戻すには `std::noshowbase`"],
  details="""### std::showbase {#showbase}

```cpp
std::ios_base& showbase(std::ios_base& str);
```

整数を [`hex`](hex.md) で出すとき、`0x` の接頭辞を付けます。[`oct`](oct.md) では先頭に `0` が付きます。10 進数には何も付きません。

値が 0 のときは、`0` だけが出て、`0x0` にはなりません。16 進数のゼロ埋めで `0x00` と出したいときは、`internal` と `setfill('0')` を併用します。

プログラマー向けのログでは、16 進数に必ず `0x` を付けると、10 進数との区別が付きます。メモリのアドレスや、フラグの値を出すときの、基本の設定です。""",
  code="""#include <iostream>

int main() {
  std::cout << std::hex << 255 << '\\n';               // ff
  std::cout << std::showbase << 255 << '\\n';          // 0xff
  std::cout << std::oct << 8 << '\\n';                 // 010
  std::cout << std::hex << 0 << '\\n';                 // 0（0x は付かない）
  std::cout << std::dec << 255 << '\\n';               // 255（10 進数には付かない）
}""",
  out="""ff
0xff
010
0
255""",
  uses="""メモリのアドレスやハンドルの値をログに出すときに使います。10 進数と区別がつくよう、`0x` を付けます。""",
  mistakes=[("ゼロ埋めで `0x` が欠ける", "`internal` と `setfill('0')` を併用します。")],
  similar=[("[`hex`](hex.md)", "16 進数にする"),
           ("[`uppercase`](uppercase.md)", "大文字にする")],
  memo=["基数の印（`0x`、`0`）を付ける", "10 進数には付かない", "戻すのは `noshowbase`"])

rewrite(I + 'showpoint.md',
  intro="""`3.0` と出したいのに、`std::cout << 3.0` は `3` と出ます。小数点以下が全部 0 のとき、小数点も 0 も省かれるからです。`std::showpoint` は、<strong>小数点と、末尾の 0 を必ず出す</strong>操作子です。""",
  tips=["`std::showpoint` で、`3` が `3.00000` のように、小数点と精度の桁数ぶんの 0 を付けて出る",
        "既定の書式（`defaultfloat`）で、精度の桁数までを出す",
        "`fixed` では、もともと小数点が付く",
        "設定は残る。戻すには `std::noshowpoint`"],
  details="""### std::showpoint {#showpoint}

```cpp
std::ios_base& showpoint(std::ios_base& str);
```

既定の書式では、浮動小数点数の末尾の 0 は省かれ、整数と同じ値なら小数点も出ません。`showpoint` を立てると、精度で決まる桁数まで 0 を出して、小数点も必ず出します。

`std::cout << std::showpoint << 3.0` は、既定の精度 6（有効数字）なので `3.00000` です。有効数字の桁数分が出る点に注意します。小数点以下の桁数を決めたいときは、`fixed` と `setprecision` を使います。

整数型には効きません。""",
  code="""#include <iostream>

int main() {
  std::cout << 3.0 << '\\n';                          // 3
  std::cout << std::showpoint << 3.0 << '\\n';        // 3.00000
  std::cout << 2.5 << '\\n';                          // 2.50000
  std::cout << std::noshowpoint << 2.5 << '\\n';      // 2.5
}""",
  out="""3
3.00000
2.50000
2.5""",
  uses="""小数であることを、見た目ではっきりさせたいときに使います。桁をそろえる目的なら、`fixed` と `setprecision` のほうが確実です。""",
  mistakes=[("`showpoint` で小数点以下 2 桁が出ると期待する", "出るのは有効数字の桁数です。小数点以下の桁数は `fixed` と `setprecision` で決めます。")],
  similar=[("[`fixed`](fixed.md)", "固定小数点にする"),
           ("[`setprecision`](setprecision.md)", "桁数を決める")],
  memo=["小数点と末尾の 0 を必ず出す", "有効数字の桁数まで出る", "戻すのは `noshowpoint`"])

rewrite(I + 'uppercase.md',
  intro="""16 進数の `ff8800` を、`FF8800` と大文字で出したい。浮動小数点数の指数表記の `e` も、`E` にしたい。出力に出る英字を大文字にする操作子が `std::uppercase` です。""",
  tips=["`std::uppercase` で、16 進数の `a`〜`f`、`0x`、指数表記の `e` を大文字にする",
        "`showbase` と組み合わせると、`0XFF` になる（`0x` の x も大文字）",
        "設定は残る。戻すには `std::nouppercase`",
        "文字列には効かない（文字列の英字は変換されない）"],
  details="""### std::uppercase {#uppercase}

```cpp
std::ios_base& uppercase(std::ios_base& str);
```

数値の出力に現れる英字を大文字にします。対象は、16 進数の桁（`a`〜`f`）、基数の接頭辞（`0x` の `x`）、浮動小数点数の指数部（`e`）、`inf` や `nan` です。

`"hello"` のような文字列には効きません。文字列を大文字にするには、`std::toupper` などで変換します。

色コードを `#FF8800` のように大文字で出すのが一般的なので、16 進数の出力では、ほぼセットで使います。""",
  code="""#include <iostream>

int main() {
  std::cout << std::hex << 0xFF8800 << '\\n';           // ff8800
  std::cout << std::uppercase << 0xFF8800 << '\\n';     // FF8800
  std::cout << std::showbase << 255 << '\\n';           // 0XFF
  std::cout << std::scientific << 1234.5 << '\\n';      // 1.234500E+03
}""",
  out="""ff8800
FF8800
0XFF
1.234500E+03""",
  uses="""色コードやハッシュ値、アドレスの表示で使います。16 進数を大文字にそろえると、見た目が整います。""",
  mistakes=[("文字列が大文字になると期待する", "数値の英字だけが対象です。"),
            ("`showbase` と併用して `0X` になって驚く", "`x` も大文字になります。`0x` を保ちたいなら、`uppercase` を使わず、桁だけ自前で大文字にします。")],
  similar=[("[`hex`](hex.md)", "16 進数にする"),
           ("[`showbase`](showbase.md)", "基数の印を付ける")],
  memo=["数値の英字を大文字にする", "`0x` も `0X` になる", "戻すのは `nouppercase`"])

rewrite(I + 'boolalpha.md',
  intro="""`bool` を出力すると、`1` や `0` と出ます。ログに「フラグ: 1」と出ても意味が分かりにくい。`true` や `false` と書いてほしい。`std::boolalpha` は、<strong>`bool` を文字で出し入れする</strong>操作子です。""",
  tips=["`std::boolalpha` で、`bool` を `true` / `false` で出力する",
        "入力にも効く。`true` / `false` の文字列を `bool` として読む",
        "設定は残る。戻すには `std::noboolalpha`",
        "ロケールによっては、`true` / `false` が別の言葉になる"],
  details="""### std::boolalpha {#boolalpha}

```cpp
std::ios_base& boolalpha(std::ios_base& str);
```

既定では、`bool` は整数の `1` と `0` で出入力されます。`boolalpha` を立てると、ロケールで決まる文字列、つまり "C" ロケールなら `true` と `false` を使います。

入力では、`true` / `false` の文字列だけを受け付けます。`boolalpha` を立てたまま `1` を読み込もうとすると、失敗します。設定ファイルの読み込みで、期待する形式に合わせて設定します。

日本語ロケールを設定しても、標準のロケールには `true` / `false` の日本語訳が用意されていないことが多く、結果は英語のままです。

`std::print` / `std::format` は、`bool` を既定で `true` / `false` と出すので、`boolalpha` は不要です。""",
  code="""#include <iostream>
#include <sstream>

int main() {
  bool alive = true;
  std::cout << alive << '\\n';                           // 1
  std::cout << std::boolalpha << alive << '\\n';         // true
  std::cout << false << '\\n';                           // false
  std::cout << std::noboolalpha << false << '\\n';       // 0

  // 入力にも効く
  std::istringstream in("true false");
  bool a, b;
  in >> std::boolalpha >> a >> b;
  std::cout << a << b << '\\n';                          // 10
}""",
  out="""1
true
false
0
10""",
  uses="""ログに真偽値を出すときに使います。「alive: true」と出ると、一目で分かります。設定ファイルから `true` / `false` を読むときにも使えます。""",
  mistakes=[("`boolalpha` を立てたまま、`1` を読み込んで失敗する", "入力の形式に合わせて、設定を切り替えます。"),
            ("戻し忘れて、他の `bool` も文字になる", "`noboolalpha` で戻します。")],
  similar=[("`std::format`", "C++20 で `bool` を `true`/`false` と出す"),
           ("`std::print`", "C++23。同上")],
  memo=["`bool` を `true` / `false` で出し入れする", "入力にも効く", "戻すのは `noboolalpha`"])

rewrite(I + 'endl.md',
  intro="""画面に 1 行出して、改行したい。`'\\n'` でも改行できますが、`std::endl` は、改行を出したうえで、<strong>バッファーを書き出す</strong>ところまで行います。便利に見えますが、使いすぎると出力が遅くなることでも有名な操作子です。""",
  tips=["`std::endl` は、`'\\n'` を出して `flush` する",
        "毎回 `flush` するので、大量の出力では `'\\n'` より、はるかに遅くなる",
        "クラッシュの直前のログを確実に残したいときには役立つ",
        "普段の改行は `'\\n'` で十分。必要なときだけ `flush` を足す"],
  details="""### std::endl {#endl}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& endl(std::basic_ostream<CharT, Traits>& os);
```

`os.put(os.widen('\\n'))` を呼んだあと、`os.flush()` を呼びます。2 つの動作が 1 つにまとまっているのがこの操作子で、ここが誤解のもとです。

`flush` は、バッファーに溜まった出力を、OS に渡す処理です。ファイルやコンソールへの書き込みは、まとめて行うほうが効率が良いので、ストリームは溜めてから書き出します。`endl` を毎回使うと、その溜める利点が失われ、1 行ごとに書き込み処理が走ります。10 万行を出力するようなループでは、`'\\n'` との差が、数倍から数十倍になることがあります。

書き出しが必要なのは、クラッシュしても最後のログを残したい場合や、対話型の入出力で、プロンプトを出してから入力を待つ場合です。その場面では、`std::flush` を明示するほうが、意図が伝わります。

C++23 の `std::println` は、改行だけを出します。`flush` が必要なときは、別に `std::fflush` などを呼びます。""",
  code="""#include <iostream>
#include <sstream>

int main() {
  std::ostringstream out;
  out << "line1" << std::endl;      // 改行 + flush
  out << "line2" << '\\n';           // 改行だけ
  std::cout << out.str();
}""",
  out="""line1
line2""",
  uses="""クラッシュ ログのように、書いた直後に確実に残したい出力に使います。通常のログや、大量の出力では、`'\\n'` を使います。ゲームのデバッグ ログで、毎フレーム `endl` を出すと、フレームレートが落ちる原因になることがあります。""",
  mistakes=[("大量の出力で `endl` を使って、遅くなる", "`'\\n'` に置き換えます。"),
            ("`endl` を改行の標準だと思って、いつも使う", "改行と書き出しは別の操作です。必要なときだけ `flush` します。")],
  similar=[("[`flush`](flush.md)", "書き出しだけ（改行なし）"),
           ("[`ends`](ends.md)", "`'\\0'` を出す"),
           ("`'\\n'`", "改行だけ。通常はこれ")],
  memo=["改行して、書き出す", "毎回使うと遅い", "普段は `'\\n'`"])

rewrite(I + 'flush.md',
  intro="""出力は、ストリームのバッファーに溜められてから、まとめて書き出されます。プロンプトを出して入力を待つとき、「>」が画面に出てこない。クラッシュの直前のログが、ファイルに残っていない。そんなときは、溜まっている内容を今すぐ書き出す必要があります。それが `std::flush` です。""",
  tips=["`std::cout << std::flush` で、バッファーの内容を今すぐ書き出す",
        "改行は出さない。`endl` から改行を除いたもの",
        "`os.flush()` と同じ。`<<` でつなげて書ける",
        "対話型の入出力、クラッシュ ログ、進捗表示で使う"],
  details="""### std::flush {#flush}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& flush(std::basic_ostream<CharT, Traits>& os);
```

`os.flush()` を呼ぶ操作子です。バッファーに溜まっている出力を、OS に渡します。

`std::cout` は、`std::cin` から読む前に、自動で書き出されるように結び付けられています（`cin.tie()`）。そのため、普通の対話型プログラムでは、プロンプトの `flush` を意識する必要はありません。必要になるのは、ファイルのストリームや、改行のない進捗表示（`\\r` で上書きする表示）などです。

`flush` が成功しても、データがディスクに物理的に届いたとは限りません。OS のキャッシュに残っていることがあります。電源断にも耐えたい書き込みには、OS の機能（`FlushFileBuffers` や `fsync`）まで使います。

C++20 の `std::osyncstream` を使うと、複数のスレッドからの出力が混ざらないよう、まとめて書き出せます（[`emit_on_flush`](emit_on_flush.md) も参照）。""",
  code="""#include <fstream>
#include <iostream>
#include <string>

int main() {
  std::ofstream log("crash.log");
  log << "starting..." << std::flush;   // 改行なしで、すぐ書き出す

  std::ifstream peek("crash.log");
  std::string line;
  std::getline(peek, line);
  std::cout << "別のハンドルから読めた: " << line << '\\n';
}""",
  out="別のハンドルから読めた: starting...",
  uses="""クラッシュの原因を調べるためのログで、書いた直後に `flush` しておくと、直後にクラッシュしても内容が残ります。進捗を `\\r` で上書き表示するときも、`flush` で即座に見せます。""",
  mistakes=[("毎回 `flush` して、出力が遅くなる", "必要な行だけにします。"),
            ("`flush` したから、ディスクに確実に届いたと思う", "OS のキャッシュに残る場合があります。")],
  similar=[("[`endl`](endl.md)", "改行 + 書き出し"),
           ("[`ends`](ends.md)", "`'\\0'` を出す"),
           ("[`unitbuf`](unitbuf.md)", "毎回、自動で書き出す設定")],
  memo=["バッファーを今すぐ書き出す", "改行は出さない", "`endl` は改行も出す"])
print('io1 ok')
