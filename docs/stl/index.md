# STL

C++23 の標準ライブラリをゲーム制作でよく使う順にまとめています。見出しをクリックすると一覧が開きます。

迷ったら [コンテナの選び方](../container-chart.md) も見てください。

??? abstract "コンテナ（19）: データをまとめて持つ入れ物"
    | コンテナ | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::vector`](containers/vector.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | あとから増減できる配列。要素が隣り合って並ぶので速い。迷ったらこれ。 |
    | [`std::array`](containers/array.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 個数が最初から決まっている配列。サイズ固定でヒープを使わない。 |
    | [`std::string`](containers/string.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-3">○</span> | 文字列を持つ型。連結・検索・切り出しができる。長さに応じて自動で伸びる。 |
    | [`std::unordered_map`](containers/unordered_map.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-3">○</span> | ハッシュ表。「キー → 値」をほぼ一定の時間で引ける。ID でデータを探すときに。 |
    | [`std::map`](containers/map.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | キーの順に並ぶ「キー → 値」の表。範囲で探したいとき・順番に回したいときに。 |
    | [`std::unordered_set`](containers/unordered_set.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 重複なしの集合。「入っているか」を素早く調べる。順番は気にしない。 |
    | [`std::span`](containers/span.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 配列の一部を「借りて」見る窓。コピーせず `vector` でも配列でも同じ関数で受けられる。 |
    | [`std::deque`](containers/deque.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 先頭にも末尾にも素早く追加できる配列。ブロックに分かれて並ぶ。 |
    | [`std::priority_queue`](containers/priority_queue.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 一番優先度の高いものを、先に取り出せるキュー。A* の探索やイベント管理に。 |
    | [`std::queue`](containers/queue.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 先に入れたものを先に取り出す（先入れ先出し）。順番待ち・メッセージの受け渡しに。 |
    | [`std::stack`](containers/stack.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 後に入れたものを先に取り出す（後入れ先出し）。元に戻す（アンドゥ）や探索の履歴に。 |
    | [`std::set`](containers/set.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 順番に並んだ、重複なしの集合。範囲での検索（「以上・以下」）ができる。 |
    | [`std::flat_map`](containers/flat_map.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | `vector` で作った `map`。検索は速く回すのも速いが挿入・削除は遅い。 <span class="ver ver-23">C++23</span> |
    | [`std::mdspan`](containers/mdspan.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 1 次元の配列を 2 次元・3 次元として見る窓（コピーしない）。タイルマップや画像に。 <span class="ver ver-23">C++23</span> |
    | [`std::bitset`](containers/bitset.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 固定長のビット列。フラグをまとめて持つ。1 ビットずつのオン・オフを少ないメモリで。 |
    | [`std::list`](containers/list.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-1">×</span> | 連結リスト。途中の挿入・削除は速いが全体が遅く、ほとんど使わない。 |
    | [`std::forward_list`](containers/forward_list.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-1">×</span> | 片方向だけにつながるリスト。`list` より軽いが使う場面はほとんどない。 |
    | [`std::multimap` / `multiset`](containers/multimap.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同じキーを、複数持てる `map` / `set`。同じキーに複数の値をまとめたいときに。 |
    | [`std::flat_set`](containers/flat_set.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | `vector` で作った `set`。検索と巡回が速い。挿入・削除は遅い。 <span class="ver ver-23">C++23</span> |

??? abstract "アルゴリズム（25）: 並べ替え・検索・変換"
    C++20 以降は `std::ranges::` 版を使うのが基本です。

    | アルゴリズム | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::ranges::sort`](algorithms/sort.md) | <span class="rank rank-must">必須</span> | 要素を小さい順（または指定の順）に並べ替える。比較の関数も渡せる。 |
    | [`std::erase_if`](algorithms/erase_if.md) | <span class="rank rank-must">必須</span> | 条件に合う要素をまとめて消す。`erase-remove` を 1 行で書ける。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::find` / `find_if`](algorithms/find.md) | <span class="rank rank-must">必須</span> | 条件に合う最初の要素を探す。見つからなければ `end()` が返る。 |
    | [`std::ranges::any_of` / `all_of` / `none_of`](algorithms/any_of.md) | <span class="rank rank-often">よく使う</span> | 条件を満たす要素が、1 つでもあるか・全部か・1 つもないかを調べる。 |
    | [`std::ranges::count_if`](algorithms/count_if.md) | <span class="rank rank-often">よく使う</span> | 条件に合う要素が、いくつあるかを数える。 |
    | [`std::ranges::min` / `max` / `minmax`](algorithms/min_max.md) | <span class="rank rank-often">よく使う</span> | 2 つ以上の値や、範囲の中から最小・最大を求める。 |
    | [`std::clamp`](algorithms/clamp.md) | <span class="rank rank-often">よく使う</span> | 値を下限と上限の範囲内に収める（はみ出したら端の値にする）。 |
    | [`std::ranges::min_element` / `max_element`](algorithms/min_element.md) | <span class="rank rank-often">よく使う</span> | 範囲の中で、最小・最大の要素の「位置（イテレータ）」を返す。 |
    | [`std::views::filter` / `transform`](algorithms/views.md) | <span class="rank rank-often">よく使う</span> | 範囲をコピーせずに絞り込み（`filter`）や変換（`transform`）をして「見る」。 |
    | [`std::ranges::to`](algorithms/ranges_to.md) | <span class="rank rank-often">よく使う</span> | 範囲（`views` の結果など）を `vector` などのコンテナに作り直す。 <span class="ver ver-23">C++23</span> |
    | [`std::accumulate` / `ranges::fold_left`](algorithms/accumulate.md) | <span class="rank rank-sometimes">たまに</span> | 要素を順に足し込んで合計や、畳み込みの結果を 1 つ作る。 |
    | [`std::ranges::shuffle`](algorithms/shuffle.md) | <span class="rank rank-sometimes">たまに</span> | 要素をランダムな順に並べ替える（カードの山のシャッフル）。 |
    | [`std::ranges::reverse`](algorithms/reverse.md) | <span class="rank rank-sometimes">たまに</span> | 要素の並びを逆順にする。 |
    | [`std::ranges::binary_search` / `lower_bound`](algorithms/binary_search.md) | <span class="rank rank-sometimes">たまに</span> | 並んでいる範囲から、二分探索で素早く探す（半分ずつ絞る）。 |
    | [`std::ranges::unique`](algorithms/unique.md) | <span class="rank rank-sometimes">たまに</span> | 隣り合う同じ値の重複を 1 つにまとめる（先に並べ替えておくと全体の重複を除ける）。 |
    | [`std::ranges::copy` / `fill`](algorithms/copy_fill.md) | <span class="rank rank-sometimes">たまに</span> | 範囲を別の場所にコピーする・同じ値で埋める。 |
    | [`std::ranges::stable_sort`](algorithms/stable_sort.md) | <span class="rank rank-sometimes">たまに</span> | 並べ替えるとき同じ値の要素の元の順番を、変えない。 |
    | [`std::ranges::partial_sort` / `nth_element`](algorithms/partial_sort.md) | <span class="rank rank-rare">知ってるだけ</span> | 全部は並べず上位 N 件だけを、並べる。ランキングの上位表示に。 |
    | [`std::ranges::for_each`](algorithms/for_each.md) | <span class="rank rank-sometimes">たまに</span> | 全要素に関数を呼ぶ。普段は範囲 for のほうが読みやすい。 |
    | [`std::ranges::replace` / `remove`](algorithms/replace.md) | <span class="rank rank-sometimes">たまに</span> | 特定の値を別の値に置き換える・条件に合う要素を、前に詰める。 |
    | [`std::ranges::partition`](algorithms/partition.md) | <span class="rank rank-sometimes">たまに</span> | 条件に合うものと合わないものに、2 つに分ける（並びを入れ替える）。 |
    | [`std::ranges::equal` / `mismatch`](algorithms/equal.md) | <span class="rank rank-sometimes">たまに</span> | 2 つの範囲が、同じ中身か・最初に違う場所はどこかを調べる。 |
    | [`std::ranges::search` / `adjacent_find` / `is_sorted`](algorithms/search.md) | <span class="rank rank-rare">知ってるだけ</span> | ある並びのパターンが、含まれているか・隣り合う同じ値・並んでいるかを調べる。 |
    | [集合演算（`set_union` など）](algorithms/set_operations.md) | <span class="rank rank-rare">知ってるだけ</span> | 並んだ 2 つの範囲の、共通部分・和・差を作る。 |
    | [`std::ranges::make_heap` など](algorithms/heap.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲をヒープ（最大値を、すぐ取り出せる並び）にして扱う。 |

??? abstract "ユーティリティ（14）: optional, unique_ptr, format などの便利な部品"
    | 機能 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::unique_ptr`](utilities/unique_ptr.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 持ち主が 1 つだけの、スマートポインタ。スコープを出ると自動で解放される。 |
    | [`std::optional`](utilities/optional.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 値が「あるかもしれない・ないかもしれない」を表す。見つからないことを `nullptr` なしで示せる。 <span class="ver ver-17">C++17</span> |
    | [`std::format` / `std::print`](utilities/format.md) | <span class="rank rank-must">必須</span> | — | `{}` を使って、文字列を整形する（`printf` の安全版）。`print` でそのまま出力もできる。 <span class="ver ver-23">C++23</span> |
    | [`std::pair` / `std::tuple`](utilities/pair_tuple.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 2 つ以上の値を、1 つにまとめる。関数が複数の値を返すときに。 |
    | [`std::shared_ptr` / `weak_ptr`](utilities/shared_ptr.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 持ち主が複数いる、スマートポインタ。最後の持ち主が消えたときに解放される。 |
    | [`std::function`](utilities/function.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 関数・ラムダ式を変数に入れて持つ。コールバックの保存に。 |
    | [`std::move` / `std::forward`](utilities/move.md) | <span class="rank rank-often">よく使う</span> | — | コピーせず中身を「移す」ための道具（`move`・`forward`）。 |
    | [`std::expected`](utilities/expected.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 「成功した値」か「エラー」の、どちらかを返す。例外を使わないエラー処理に。 <span class="ver ver-23">C++23</span> |
    | [`std::string_view`](utilities/string_view.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 文字列をコピーせずに「借りて」見る。引数で文字列を受け取るときの定番。 <span class="ver ver-17">C++17</span> |
    | [`std::variant`](utilities/variant.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 「複数の型のうちどれか 1 つ」を持つ。状態や種類ごとのデータを型安全に持てる。 <span class="ver ver-17">C++17</span> |
    | [`std::chrono`](utilities/chrono.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 時間の長さ・時刻を扱う。フレームの時間計測や待ち時間に。 |
    | [`<random>`](utilities/random.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 乱数を作る。シードと分布（一様・正規など）を組み合わせて使う。 |
    | [`std::any`](utilities/any.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | どんな型でも入る箱。型を実行時に確かめて取り出す。使う場面は少ない。 |
    | [`std::hash`](utilities/hash.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 値から、ハッシュ値を作る。自作の型を `unordered_map` のキーにするときに。 |

??? abstract "メモリ（5）: 確保の仕組みアロケータ、C 由来の関数"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`new` と `delete`・配置 new](memory/new_delete.md) | <span class="rank rank-often">よく使う</span> | メモリの確保と、オブジェクトの作成・破棄。配置 `new`、`construct_at` も含む。 |
    | [`std::allocator`](memory/allocator.md) | <span class="rank rank-sometimes">たまに</span> | コンテナのメモリの取り先。自作のアロケータで確保の方法を変えられる。 |
    | [`std::pmr`](memory/pmr.md) | <span class="rank rank-sometimes">たまに</span> | コンテナの型を変えずにメモリの取り先を、切り替える。フレーム用の領域に。 |
    | [`malloc` / `free`](memory/c-memory.md) | <span class="rank rank-sometimes">たまに</span> | C 由来の `malloc` / `free`。C のライブラリとの橋渡しに。 |
    | [文字列・メモリ操作（cstring）](memory/cstring.md) | <span class="rank rank-sometimes">たまに</span> | `memcpy`、`memset`、`strlen` などバイト列のコピーや比較。 |

??? abstract "入出力・文字列（6）: ファイル、パス、文字列と数値の変換"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::filesystem`](io/filesystem.md) | <span class="rank rank-often">よく使う</span> | ファイルやフォルダの存在確認・一覧・コピー・削除。パスの扱い。 |
    | [`std::ifstream` / `std::ofstream`](io/fstream.md) | <span class="rank rank-often">よく使う</span> | ファイルの読み書き（テキスト・バイナリ）。 |
    | [`std::stringstream`](io/sstream.md) | <span class="rank rank-sometimes">たまに</span> | 文字列をストリームとして読み書きして、分解・組み立てをする。 |
    | [`std::from_chars` / `to_chars`](io/charconv.md) | <span class="rank rank-sometimes">たまに</span> | 数値と文字列の変換。速くて例外を投げない。 |
    | [`std::cout` / `std::cin`](io/iostream.md) | <span class="rank rank-sometimes">たまに</span> | 標準入出力（`cin` / `cout`）と、書式のフラグ。 |
    | [`std::regex`](io/regex.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現による文字列の検索・置換。便利だが遅い。 |

??? abstract "数値（6）: 数学関数、定数、整数型、ビット操作"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`<cmath>`](numeric/cmath.md) | <span class="rank rank-must">必須</span> | `sqrt`、`sin` / `cos`、`atan2`、`lerp` など数学の関数。 |
    | [`<cstdint>`](numeric/cstdint.md) | <span class="rank rank-often">よく使う</span> | `std::int32_t` など大きさが決まった整数の型。 |
    | [`std::numeric_limits`](numeric/limits.md) | <span class="rank rank-often">よく使う</span> | 型の最大値・最小値・誤差の大きさを、調べる。 |
    | [`<numbers>`](numeric/numbers.md) | <span class="rank rank-often">よく使う</span> | π などの数学の定数。 |
    | [`<numeric>`](numeric/numeric.md) | <span class="rank rank-sometimes">たまに</span> | 最大公約数（`gcd`）、最小公倍数、中間値、累積和など。 |
    | [`<bit>`](numeric/bit.md) | <span class="rank rank-sometimes">たまに</span> | ビットを数える（`popcount`）・型を読み替える（`bit_cast`）など、ビット操作。 |

??? abstract "並行処理（6）: スレッドとデータの守り方"
    | 名前 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::thread` / `std::jthread`](concurrency/thread.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 別のスレッドで、処理を動かす。 |
    | [`std::mutex`](concurrency/mutex.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 共有のデータを同時に触れないよう、鍵で守る。 |
    | [`std::atomic`](concurrency/atomic.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 複数スレッドから、安全に読み書きできる数値・フラグ。 |
    | [`std::async` / `std::future`](concurrency/future.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 処理を別スレッドに任せ結果を、あとで受け取る。 |
    | [`std::condition_variable`](concurrency/condition_variable.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 条件が満たされるまで、スレッドを眠らせて待たせる。 |
    | [セマフォ・ラッチ・バリア](concurrency/semaphore.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 同時に入れる数を、制限する。待ち合わせの道具。 |

??? abstract "型・言語サポート（7）: イテレータの道具、関数オブジェクト、型の性質、例外"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`<iterator>`](support/iterator.md) | <span class="rank rank-sometimes">たまに</span> | イテレータを進める・距離を測る・挿入するなどの道具（`next`、`distance`、`back_inserter`）。 |
    | [`<functional>`](support/functional.md) | <span class="rank rank-sometimes">たまに</span> | 比較（`greater`）・参照渡し（`ref`）・引数の固定（`bind_front`）などの、関数の道具。 |
    | [`<type_traits>`](support/type_traits.md) | <span class="rank rank-sometimes">たまに</span> | 型の性質（整数かポインタかなど）を、コンパイル時に調べる。 |
    | [小さな便利機能](support/utility-misc.md) | <span class="rank rank-sometimes">たまに</span> | `to_underlying`、`cmp_less`、`byte` など細かい便利道具。 |
    | [標準の例外](support/exceptions.md) | <span class="rank rank-sometimes">たまに</span> | 標準の例外の種類（`runtime_error`、`out_of_range` など）と使い分け。 |
    | [`std::source_location` / `stacktrace`](support/source_location.md) | <span class="rank rank-sometimes">たまに</span> | 呼ばれた場所（ファイル・行）や、呼び出し履歴を取得する。ログに便利。 |
    | [`std::generator`](support/generator.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンで、値を 1 つずつ作って返す（C++23）。 |

STL を読むための前提知識は [基礎](../basics/index.md) にまとめています。
