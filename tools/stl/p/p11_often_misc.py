import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from patch import P, run  # noqa: E402

P("memory/new_delete/new.md",
  intro="""ゲームのオブジェクトを、関数を抜けたあとも生かしたいとき、ヒープ（自由に使えるメモリ領域）に置く必要があります。`new` は、ヒープにメモリを確保して、そこにオブジェクトを作る式です。確保（`operator new`）とコンストラクターの呼び出しを一度に行います。作ったものは、`delete` で解放する責任が生じます。現代の C++ では、直接 `new` を書かず、`std::make_unique` などに任せます。""",
  info="""[ヒープとスタックの違い](../../../basics/heap.md)を先に読んでください。`new` はヒープに置く式です。""",
  sections={"しくみ": """`new T(args)` は、2 段階に分かれています。1 段階目は `operator new(sizeof(T))` を呼んでメモリを確保すること、2 段階目はそのメモリに `T` のコンストラクターを呼ぶことです。コンストラクターが例外を投げたときは、確保したメモリが自動で返されます。

確保に失敗すると `std::bad_alloc` を投げます。`new (std::nothrow) T` と書くと、例外を投げず `nullptr` を返します。ゲームでは例外を使わない設定にすることが多いので、`nothrow` を使う場面もあります。

配列は `new T[n]` と書き、解放は `delete[]` で行います。`delete` と `delete[]` を取り違えると、未定義動作になります。確保した場所を自分で決めたいときは、配置 `new`（`new (ptr) T`）を使います。"""},
  game="""通常のゲームのコードで、`new` を直接書く場面は、ほとんどありません。オブジェクトの持ち主は `std::make_unique`、配列は `std::vector` で表します。

直接使うのは、オブジェクトプールを自作するときです。あらかじめ確保した大きな領域の中に、配置 `new` でオブジェクトを作ります。確保済みの領域を使い回すので、毎フレームのメモリ確保の遅さを避けられます。

古いコードを読むときには、`new` が頻繁に出てきます。誰が `delete` するのかを追いかけながら、`unique_ptr` に置き換えられるかを考えます。""",
  mistakes=[("`new` で作ったのに `delete` を忘れる",
            """関数を抜ける前に `return` や例外が起きると、`delete` に届かずリークします。`unique_ptr` に任せれば、どの経路でも解放されます。"""),
           ("`new[]` を `delete` で解放する",
            """`new int[10]` は `delete[]` で解放します。`delete` だと未定義動作です。配列の確保は `std::vector` を使えば、この間違いがなくなります。"""),
           ("`new` の結果を確かめずに使う",
            """通常の `new` は、失敗すると例外を投げるので、戻り値を `nullptr` と比べる必要はありません。比べるのは `nothrow` 版のときです。""")],
  similar=[("[`std::make_unique`](../../utilities/make_unique.md)", "`new` の代わり。持ち主を `unique_ptr` で表す"),
           ("[`delete`](delete.md)", "`new` で作ったものを解放する"),
           ("[配置 new](placement_new.md)", "確保済みの場所にオブジェクトを作る")],
  memo=["生の `new` は書かない。`make_unique` か `vector` を使う。", "`new` は「確保」と「コンストラクターの呼び出し」の 2 段階。", "失敗は `bad_alloc`。`nothrow` なら `nullptr`。"])

P("memory/new_delete/delete.md",
  intro="""`new` で作ったオブジェクトは、使い終わったら自分で片付けなければ、メモリリークになります。`delete` は、`new` で作ったオブジェクトのデストラクターを呼んで、メモリを解放する式です。`nullptr` に対しては何もしないので、確かめずに呼べます。解放したあとのポインターは使えません。現代の C++ では、`unique_ptr` が自動で `delete` してくれます。""",
  info="""[`new` 式](new.md)を先に読んでください。`delete` は `new` と対になっています。""",
  sections={"しくみ": """`delete p` は、2 段階で動きます。まず `p` が指すオブジェクトのデストラクターを呼び、次に `operator delete` でメモリを返します。

基底クラスのポインターで派生クラスのオブジェクトを `delete` するとき、基底クラスのデストラクターが `virtual` でないと、派生クラスのデストラクターが呼ばれず、未定義動作になります。継承して使うクラスは、デストラクターを `virtual` にします。

`delete` したあとのポインターは、解放されたメモリを指したままです（ぶら下がりポインター）。再び使うと未定義動作になるので、`p = nullptr;` として、使えない印を付ける習慣があります。"""},
  game="""通常のゲームのコードでは、`unique_ptr` や `vector` に任せるので、`delete` を直接書く場面は少なめです。

自作のメモリ管理（オブジェクトプールなど）を書くときには、配置 `new` で作ったオブジェクトを `delete` で解放してはいけません。確保したのはプールで、`delete` は `operator delete` を呼んでしまうからです。破棄は、デストラクターだけを呼ぶ `std::destroy_at` で行い、メモリはプールへ返します。

古いコードを引き継ぐときは、`delete` の呼び出し場所から、持ち主の設計を読み取ります。誰が `new` して、誰が `delete` するのかを整理して、`unique_ptr` に置き換えます。""",
  mistakes=[("同じポインターを二重に `delete` する",
            """コピーしたポインターを、別々の場所で `delete` すると、二重解放でクラッシュします。持ち主は 1 人にして、他は参照や生ポインターで見るだけにします。"""),
           ("`new[]` を `delete` で解放する",
            """`new[]` で作った配列は、`delete[]` で解放します。`delete` だと、要素のデストラクターが 1 つ目しか呼ばれないなど、未定義動作になります。"""),
           ("基底クラスのデストラクターが `virtual` でない",
            """`Base* p = new Derived; delete p;` で、`Base` のデストラクターが `virtual` でないと、`Derived` の後始末が行われません。継承するクラスのデストラクターは `virtual` にします。""")],
  similar=[("[`new` 式](new.md)", "オブジェクトを作る。`delete` と対"),
           ("`std::unique_ptr`", "スコープを抜けると自動で `delete` する"),
           ("`std::destroy_at`", "デストラクターだけを呼ぶ。配置 `new` で作ったものに使う")],
  memo=["`new` には `delete`、`new[]` には `delete[]`。", "二重に `delete` しない。解放後は `nullptr` を入れる。", "`unique_ptr` に任せれば書かなくてよい。"])

P("utilities/chrono/duration_cast.md",
  intro="""ミリ秒で測った処理時間を、秒に直して画面に出したい。細かい単位から粗い単位へ変換すると、端数が失われます。C++ は、そのような情報が失われる変換を、`=` で暗黙には許しません。`std::chrono::duration_cast` は、`duration` を別の単位へ明示的に変換する関数です。端数は切り捨てられます。""",
  info="""[`std::chrono::duration`](duration.md) の単位と、型でのそろえ方を先に読んでください。""",
  sections={"しくみ": """`duration_cast<ToDuration>(d)` は、`d` の値を `ToDuration` の単位に換算して、整数なら 0 に向かって切り捨てて返します。`duration_cast<seconds>(milliseconds(1999))` は `1s` です。

粗い単位から細かい単位（秒からミリ秒）への変換は、情報を失わないので、`duration_cast` なしで暗黙に変換できます。浮動小数点型の `duration`（`duration<double>`）への変換も、暗黙にできます。

切り捨てではなく、切り上げや四捨五入が欲しいときは、C++17 で追加された `std::chrono::ceil`、`round`、`floor` を使います。"""},
  game="""処理時間の計測結果を、画面やログに出すために使います。`steady_clock` の差は、ナノ秒の `duration` で得られるので、`duration_cast<milliseconds>(end - start).count()` でミリ秒の整数に直します。

小数で欲しいときは、`duration_cast` を使わず、`duration<float, std::milli>` のように浮動小数点の型で受けます。`std::chrono::duration<float, std::milli> ms = end - start;` と書けば、端数を失いません。

タイマーの残り時間を「分:秒」で表示するときにも使います。`duration_cast<minutes>(remain)` で分を取り、残りの秒は `remain - minutes` で求めます。""",
  mistakes=[("端数が切り捨てられて、0 になる",
            """`duration_cast<seconds>(milliseconds(900))` は `0s` です。1 秒未満の処理時間を秒に変換して `0` と表示してしまう、というミスがよく起きます。小数の秒で受けるか、ミリ秒のまま表示します。"""),
           ("`count()` を取ってから単位を変えようとする",
            """`ms.count() / 1000` は、整数の割り算で端数が消えるうえ、単位の情報も失います。`duration` のまま変換して、最後に `count()` を呼びます。"""),
           ("粗い単位への変換を `=` で書いてコンパイルエラー",
            """`seconds s = milliseconds(1500);` はコンパイルエラーです。切り捨てが起きることを明示するために、`duration_cast` を使います。""")],
  similar=[("[`duration`](duration.md)", "時間の長さを表す型"),
           ("`std::chrono::round`", "四捨五入する"),
           ("`std::chrono::floor` / `ceil`", "切り捨て（`duration_cast` と同じ向き）/ 切り上げ")],
  memo=["単位を明示的に変換する。端数は切り捨て。", "粗い単位から細かい単位への変換は、暗黙にできる。", "小数で欲しいときは `duration<float>` で受ける。"])

P("utilities/chrono/literals.md",
  intro="""`sleep_for(16)` と書いたとき、これがミリ秒なのか、マイクロ秒なのか、コードを読んだだけでは分かりません。単位を取り違えて、思ったより何千倍も待ってしまうバグもあります。`std::chrono_literals` を使うと、`16ms`、`2s`、`1.5min` のように、数値の後ろに単位を付けて `duration` を書けます。`using namespace std::chrono_literals;` と書くと使えます。""",
  info="""[`std::chrono::duration`](duration.md) が分かると読みやすいです。リテラルは、`duration` を短く書く書き方です。""",
  sections={"しくみ": """`16ms` は、`operator""ms(16)` という関数を呼びます。この関数が `std::chrono::milliseconds(16)` を返します。整数のリテラルは、整数の `duration`（`2s` は `seconds`）になり、小数のリテラルは `double` の `duration`（`1.5s` は `duration<double>`）になります。

使える単位は、`ns`（ナノ秒）、`us`（マイクロ秒）、`ms`（ミリ秒）、`s`（秒）、`min`（分）、`h`（時）です。C++20 では、日付用の `d`（日）と `y`（年）も加わりました。

`using namespace std::chrono_literals;` は、関数の中や、自分の名前空間の中に書きます。ヘッダーファイルの先頭の、グローバルな場所には書かないようにします。"""},
  game="""待ち時間の指定に使います。`std::this_thread::sleep_for(16ms)` と書くと、単位が一目で分かります。タイムアウトの判定は `now - start > 5s` と読みやすくなります。

ゲームの設定値に使うと、単位の取り違えが減ります。`constexpr auto kCooldown = 500ms;` とすれば、クールダウンの長さが明確です。

デルタタイムを秒の `float` で受けたいときは、`duration<float>` に代入します。`std::chrono::duration<float> dt = 16ms;` で `0.016` 秒です。""",
  mistakes=[("`using namespace` をヘッダーの先頭に書く",
            """ヘッダーに書くと、そのヘッダーを読み込むすべてのファイルに影響します。名前の衝突が起きることがあるので、関数の中か `.cpp` の中に書きます。"""),
           ("`1.5s` を整数の `duration` だと思う",
            """`1.5s` は `double` の `duration` です。`seconds` 型の変数には、そのまま代入できません。`duration_cast<seconds>` を使うか、`duration<double>` で受けます。"""),
           ("`min` が `std::min` と衝突する",
            """`using namespace std;` と一緒に使うと、`min` が名前の衝突を起こす場面があります。`std::chrono_literals` だけを `using` します。""")],
  similar=[("[`duration`](duration.md)", "リテラルが作る型"),
           ("`std::chrono::milliseconds`", "リテラルを使わずに書く場合の型名"),
           ("[`duration_cast`](duration_cast.md)", "単位を変換する")],
  memo=["`16ms`、`2s` のように、数値の後ろに単位を付ける。", "`using namespace std::chrono_literals;` は、ヘッダーの先頭に書かない。", "小数のリテラルは `double` の `duration`。"])

P("utilities/chrono/time_point.md",
  intro="""「処理を開始した時刻」と「いまの時刻」を覚えておいて、差を取りたい。時刻と時間の長さは別のものです。「午後 3 時」は時刻、「2 時間」は長さで、時刻どうしを引くと長さに、時刻に長さを足すと別の時刻になります。`std::chrono::time_point` は、ある時計の上の「ある時点」を表すクラスで、この関係を型で守ってくれます。""",
  info="""[`std::chrono::duration`](duration.md) と、[`steady_clock`](steady_clock.md) を先に読んでください。`time_point` は、時計の上の時点を表します。""",
  sections={"しくみ": """`time_point<Clock, Duration>` は、内部に「その時計の基準時刻からの経過時間」を `duration` として持っています。時計が違うと基準も違うので、違う時計の時点どうしは比べられません（型が違うため、コンパイルエラーになります）。

使える演算は決まっています。`time_point - time_point` は `duration`、`time_point + duration` と `time_point - duration` は `time_point` です。時点どうしを足すことはできません。

`time_since_epoch()` で、基準時刻からの経過時間が取れますが、基準時刻は時計の実装次第です。`steady_clock` では意味のある値にならないので、差を取ったときにだけ使います。"""},
  game="""処理時間の計測の起点と終点を、`auto start = steady_clock::now();` として保存しておくのが基本です。差が `duration` になります。

イベントを時刻で管理するとき、`std::vector<std::pair<time_point, Event>>` のように、予定の時刻を持たせます。いまの時刻と比べて、過ぎていれば実行します。

保存したい日時は、`system_clock` の `time_point` を使います。`steady_clock` の時点は、再起動で意味が変わるので、ファイルに保存してはいけません。""",
  mistakes=[("違う時計の時点を引き算する",
            """`steady_clock::now() - system_clock::now()` は、型が違うのでコンパイルエラーです。基準が違う時計の時点を、直接比べることはできません。"""),
           ("`steady_clock` の時点をファイルに保存する",
            """`steady_clock` の基準は、実装ごとに違い、再起動でも変わります。保存した値を後で読み込んでも、意味を持ちません。日時を保存するなら `system_clock` です。"""),
           ("時点どうしを足そうとする",
            """時点を足す演算はありません。差（`duration`）を足すのは正しい操作です。""")],
  similar=[("[`duration`](duration.md)", "時間の長さ。時点の差"),
           ("[`steady_clock`](steady_clock.md)", "巻き戻らない時計。計測用"),
           ("[`system_clock`](system_clock.md)", "世の中の時刻。日時の保存用")],
  memo=["`time_point - time_point` が `duration`、`time_point + duration` が `time_point`。", "違う時計の時点は比べられない。", "保存するのは `system_clock` の時点。"])

P("utilities/random/bernoulli_distribution.md",
  intro="""「30% の確率で会心の一撃」「5% でレアドロップ」。ゲームでは、確率で成功か失敗かを決める判定が、あちこちに出てきます。`uniform_real_distribution` で 0 から 1 の値を作って `< 0.3f` と比べる書き方もありますが、何をしているのかが、少し読み取りにくくなります。`std::bernoulli_distribution` は、確率 `p` で `true`、`1 - p` で `false` を出す分布です。意図がそのまま名前に出ます。""",
  info="""[`std::mt19937`](mt19937.md) の乱数エンジンの使い方を先に読んでください。分布は、エンジンの出力を目的の形に変える部品です。""",
  sections={"しくみ": """`bernoulli_distribution(p)` の `p` は、`true` が出る確率で、0.0 から 1.0 の範囲で指定します。範囲外は未定義です。`p` を省略すると 0.5 です。

使い方は、他の分布と同じです。`std::bernoulli_distribution crit(0.3); bool hit = crit(rng);` と書きます。分布オブジェクトは軽く、使う場所で作っても構いません。

何回か試した合計を知りたいときは、`binomial_distribution` を使います。「10 回挑戦して何回成功するか」を一度に決められます。"""},
  game="""会心やクリティカルの判定が代表的です。`std::bernoulli_distribution crit(0.3);` と作り、攻撃のたびに `crit(rng)` で判定します。

レアドロップの判定にも使います。ただし、確率が低いドロップを何回も引かないと出ない、という体験を避けたいゲームでは、「天井」を設けて、一定回数で必ず出るようにします。この場合の確率は、毎回変わるので、`p` を引くたびに作り直します。

敵の行動のランダム化（待機するか攻撃するか）や、パーティクルを出すかどうかの判定にも使えます。""",
  mistakes=[("確率を百分率で渡す",
            """`bernoulli_distribution(30)` は、`p` が 30 で範囲外の未定義動作です。確率は 0.0 から 1.0 で渡します。30% は `0.3` です。"""),
           ("毎回エンジンを作り直す",
            """判定のたびに `mt19937` を作ると、遅く、乱数の質も落ちます。エンジンは 1 つ作って使い回します。"""),
           ("`p` が 0 や 1 のときの扱いを忘れる",
            """`p = 0.0` なら常に `false`、`p = 1.0` なら常に `true` です。これらは正しい指定ですが、確率の設定値を外部から読み込むときに、範囲外の値が混ざっていないかを確かめます。""")],
  similar=[("[`uniform_real_distribution`](uniform_real_distribution.md)", "0〜1 の値を作って比べる書き方。意図は読み取りにくい"),
           ("[`binomial_distribution`](binomial_distribution.md)", "複数回の試行の合計"),
           ("[`discrete_distribution`](discrete_distribution.md)", "3 つ以上の選択肢を重みで選ぶ")],
  memo=["確率 `p` で `true` を返す。`p` は 0.0〜1.0。", "会心やドロップの判定に使う。", "エンジンは使い回す。"])

P("utilities/random/random_device.md",
  intro="""乱数エンジンは、種（シード）を決めないと、起動のたびに同じ乱数列を出します。毎回違う乱数にしたいなら、種を予測できない値にする必要があります。`std::random_device` は、OS が用意する予測しにくい乱数を出すクラスです。ハードウェアのノイズなどを使うので質が高い反面、遅いことがあります。エンジンの種を作る場面だけで使い、実際の乱数は `mt19937` などに任せます。""",
  info="""[`std::mt19937`](mt19937.md) の乱数エンジンの役割を先に読んでください。`random_device` は、その種を作る部品です。""",
  sections={"しくみ": """`random_device` は、OS の乱数源（Windows なら `BCryptGenRandom`、Linux なら `/dev/urandom` や `getrandom`）を呼びます。呼び出しごとにシステムの助けを借りるので、`mt19937` より桁違いに遅くなります。

定番の使い方は、`std::mt19937 rng(std::random_device{}());` です。32 ビットの値を 1 つ取って、それを種にします。この方法だと、種の候補が 40 億通りしかありませんが、ゲームの用途では十分です。

`entropy()` は、乱数源の質を示す値ですが、実装によって意味が違い、当てにならないことがあります。"""},
  game="""ゲームの起動時に、乱数エンジンの種を作るために 1 回だけ使います。ステージやダンジョンを生成するときの種としても使います。生成に使った種をセーブデータに保存しておけば、同じステージを再現できます。

テストやデバッグのときは、種を固定の値にして、毎回同じ乱数列にします。バグが乱数に依存しているときに、再現しやすくなります。

暗号に使う乱数（トークンなど）には、`random_device` を直接使うほうが適切です。ただし、ゲームの通信の認証などは、専用のライブラリに任せるのが安全です。""",
  mistakes=[("ゲーム中に何度も呼んで遅くなる",
            """毎フレームの乱数に `random_device` を使うと、OS を呼ぶコストが積み重なります。起動時に 1 回だけ使い、あとはエンジンに任せます。"""),
           ("毎回同じ値になる古い実装を知らない",
            """MinGW の古い版では、`random_device` が毎回同じ値を返すことがありました。現代の MSVC、GCC、Clang では問題ありませんが、疑わしいときは時刻を併用します。"""),
           ("種を 1 つの 32 ビット値だけにする",
            """`mt19937` の内部状態は 624 個の値を持ちますが、種が 1 つだと、状態の候補が少なくなります。ゲームの用途では問題ないので、気にするのは暗号などに限られます。""")],
  similar=[("[`mt19937`](mt19937.md)", "実際の乱数を出すエンジン。種を `random_device` から作る"),
           ("`std::seed_seq`", "複数の値から種を作る。`mt19937` の初期化の質を上げる"),
           ("[`uniform_int_distribution`](uniform_int_distribution.md)", "エンジンの出力を範囲に変える")],
  memo=["エンジンの種を作るときだけ使う。", "ゲーム中に何度も呼ばない。遅い。", "再現したいときは、種を固定してセーブデータに残す。"])

P("io/filesystem/directory_entry.md",
  intro="""フォルダの中のファイルを順に調べながら、それぞれがファイルかフォルダか、サイズはどれくらいか、といった情報も知りたい。パスだけを受け取って、毎回 `file_size(path)` や `is_directory(path)` を呼ぶと、そのたびにファイルシステムへ問い合わせることになります。`std::filesystem::directory_entry` は、フォルダを回したときの 1 つの項目で、パスのほかに、種類やサイズなどをキャッシュして持っています。""",
  info="""[`directory_iterator`](directory_iterator.md) を先に読んでください。`directory_entry` は、そのイテレーターが返す要素です。""",
  sections={"しくみ": """`directory_iterator` で回すと、各項目が `directory_entry` として返ります。OS によっては、フォルダの一覧を取る時点で、ファイルの種類や、サイズなどの一部の情報も一緒に取れるので、それをキャッシュして持っています。

`is_regular_file()`、`is_directory()`、`file_size()` などは、このキャッシュを使って答えます。別途 `fs::file_size(path)` を呼ぶより、システムへの問い合わせが減ります。ただし、キャッシュは取得した時点の情報なので、その後ファイルが変わっても反映されません。最新にするには `refresh()` を呼びます。

`directory_entry` は、パスに暗黙に変換できます。`fs::path p = entry;` と書けるので、`path` を受け取る関数にそのまま渡せます。"""},
  game="""アセットフォルダの内容を調べるときに使います。

```cpp
for (const auto& entry : fs::directory_iterator("assets")) {
  if (entry.is_regular_file() && entry.path().extension() == ".png") {
    // 画像ファイルとして読み込む
  }
}
```

ファイルの更新時刻を調べて、ホットリロード（ファイルが変わったら読み直す）に使うこともあります。`entry.last_write_time()` で更新時刻を取り、前回の値と比べます。

サイズが大きいファイルを先に調べたり、容量の合計を出したりするときも、`file_size()` を使います。""",
  mistakes=[("キャッシュが古くて、最新の情報と違う",
            """`entry` が持つ情報は、取得した時点のものです。ファイルが書き換えられても、自動では更新されません。最新の値が必要なら `refresh()` を呼びます。"""),
           ("ファイルとフォルダを区別せずに開こうとする",
            """フォルダを `ifstream` で開こうとして失敗します。`entry.is_regular_file()` で、ファイルだけを対象にします。"""),
           ("例外で落ちる",
            """権限のないファイルの情報を取ろうとすると、例外が投げられます。`std::error_code` を渡す版を使うと、例外なしで結果を受け取れます。""")],
  similar=[("[`directory_iterator`](directory_iterator.md)", "フォルダの直下を回す。この項目を返す"),
           ("[`recursive_directory_iterator`](recursive_directory_iterator.md)", "サブフォルダも含めて回す"),
           ("[`path`](path.md)", "パスだけを持つ。`entry.path()` で取り出せる")],
  memo=["フォルダを回して得られる 1 つの項目。パスと情報を持つ。", "種類やサイズはキャッシュされる。最新にするには `refresh()`。", "`path` にそのまま変換できる。"])

P("io/filesystem/directory_iterator.md",
  intro="""フォルダに入っているファイルを、全部調べたい。ファイルの一覧を取る関数は OS ごとに違い、Windows の `FindFirstFile` や Linux の `readdir` を使い分けるのは面倒です。`std::filesystem::directory_iterator` は、フォルダの直下にあるファイルやフォルダを順に回す標準のイテレーターで、OS の違いを吸収してくれます。サブフォルダの中までは入りません。""",
  info="""[`std::filesystem::path`](path.md) の書き方と、[`directory_entry`](directory_entry.md) を先に読んでください。""",
  sections={"しくみ": """`directory_iterator(dir)` を作ると、`dir` の直下にある項目を指します。範囲 for で回すと、各項目が [`directory_entry`](directory_entry.md) として得られます。`.` と `..` は含まれません。

順番は決まっていません。OS やファイルシステムによって、作成順だったり、名前順だったり、バラバラだったりします。順番が必要なら、いったん `vector` に集めて `sort` します。

`directory_options` を第 2 引数に渡すと、動きを変えられます。`skip_permission_denied` は、権限のないフォルダを無視して、例外を出さずに進みます。`follow_directory_symlink` は、シンボリックリンクの先まで入ります。"""},
  game="""ゲームの起動時に、アセットフォルダやセーブデータのフォルダを調べるのに使います。

```cpp
std::vector<fs::path> saves;
for (const auto& entry : fs::directory_iterator("saves")) {
  if (entry.path().extension() == ".sav") {
    saves.push_back(entry.path());
  }
}
std::ranges::sort(saves);  // 順番は不定なので、並べる
```

セーブデータ選択の画面で、スロットを一覧にするときに使います。MOD やプラグインのフォルダを調べて、読み込むファイルを見つける用途にも使えます。

サブフォルダの中まで調べたいときは、`recursive_directory_iterator` に替えます。""",
  mistakes=[("順番が決まっていると思う",
            """OS やファイルシステムによって、順番が変わります。画面に一覧を出すなら、必ず `sort` します。"""),
           ("フォルダが存在しないのに回して、例外で落ちる",
            """存在しないフォルダを渡すと、`filesystem_error` を投げます。先に `exists` と `is_directory` で確かめるか、`std::error_code` を渡す版を使います。"""),
           ("回している最中にフォルダの中身を変更する",
            """ファイルの追加や削除を、回している最中に行うと、イテレーターの挙動が不定になります。いったん結果を集めてから、あとで操作します。""")],
  similar=[("[`recursive_directory_iterator`](recursive_directory_iterator.md)", "サブフォルダの中まで回す"),
           ("[`directory_entry`](directory_entry.md)", "回して得られる 1 つの項目"),
           ("[`exists`](exists.md)", "回す前に、フォルダがあるかを確かめる")],
  memo=["フォルダの直下を順に回す。サブフォルダの中には入らない。", "順番は不定。必要なら集めて `sort`。", "存在しないフォルダは例外になる。先に確かめる。"])

P("io/filesystem/recursive_directory_iterator.md",
  intro="""アセットフォルダの中の画像を、サブフォルダの中も含めて全部探したい。`directory_iterator` はフォルダの直下しか見ないので、サブフォルダに入るたびに、自分で再帰の関数を書くことになります。`std::filesystem::recursive_directory_iterator` は、フォルダの中身を、サブフォルダの奥まで全部たどって回します。再帰の関数を書かなくて済みます。""",
  info="""[`directory_iterator`](directory_iterator.md) を先に読んでください。`recursive_directory_iterator` は、その再帰版です。""",
  sections={"しくみ": """`recursive_directory_iterator(dir)` は、深さ優先でフォルダをたどります。サブフォルダを見つけたら、その中を先に全部回してから、次の項目へ進みます。各項目は [`directory_entry`](directory_entry.md) として返ります。

フォルダも項目の 1 つとして返るので、ファイルだけが欲しいなら、`entry.is_regular_file()` で絞ります。

イテレーターの `depth()` で現在の深さが取れ、`disable_recursion_pending()` を呼ぶと、いま見ているフォルダの中には入らず、次へ進めます。特定のフォルダ（`.git` など）を飛ばしたいときに使います。"""},
  game="""アセットの一括読み込みに使います。

```cpp
for (const auto& entry : fs::recursive_directory_iterator("assets")) {
  if (entry.is_regular_file() && entry.path().extension() == ".png") {
    LoadTexture(entry.path());
  }
}
```

ホットリロードの対象を探すときも同じです。ファイルの更新時刻を調べて、変わったものだけを読み直します。

フォルダの数が多いと、全部をたどるのに時間がかかります。起動のたびに全部を調べると遅くなるので、一覧をキャッシュするか、ゲームの本番ではパッケージ（1 つのファイルにまとめたアセット）を使います。""",
  mistakes=[("フォルダも項目に含まれることを忘れる",
            """フォルダ自体も項目として返ります。ファイルだけを処理するなら、`entry.is_regular_file()` で絞ります。"""),
           ("回しながらフォルダの中身を変更する",
            """ファイルの追加や削除を、回している最中に行うと、挙動が不定になります。いったん集めてから操作します。"""),
           ("巨大なフォルダを毎回たどって遅くなる",
            """`.git` や `node_modules` のような大きなフォルダに入ると、非常に時間がかかります。`disable_recursion_pending()` で飛ばすか、対象のフォルダを絞ります。""")],
  similar=[("[`directory_iterator`](directory_iterator.md)", "フォルダの直下だけを回す"),
           ("[`directory_entry`](directory_entry.md)", "回して得られる 1 つの項目"),
           ("[`path`](path.md)", "拡張子の取り出し（`extension()`）などに使う")],
  memo=["サブフォルダの中まで全部たどって回す。", "フォルダも項目に含まれる。ファイルだけなら `is_regular_file()` で絞る。", "巨大なフォルダに入らないよう、対象を絞る。"])

run()
