# STL

C++23 の標準ライブラリを、ゲーム制作でよく使う順にまとめています。見出しをクリックすると一覧が開きます。

迷ったら [コンテナの選び方](../container-chart.md) も見てください。

??? abstract "コンテナ（19）: データをまとめて持つ入れ物"
    | コンテナ | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::vector`](containers/vector.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 伸びる配列。迷ったらこれ |
    | [`std::array`](containers/array.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 固定長の配列 |
    | [`std::string`](containers/string.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-3">○</span> | 文字列 |
    | [`std::unordered_map`](containers/unordered_map.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-3">○</span> | ハッシュ表。キーで高速に検索 |
    | [`std::map`](containers/map.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | キーが順番に並ぶ表 |
    | [`std::unordered_set`](containers/unordered_set.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 重複なしの集合 |
    | [`std::span`](containers/span.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 配列を借りる「窓」 |
    | [`std::deque`](containers/deque.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 両端に追加できる配列 |
    | [`std::priority_queue`](containers/priority_queue.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 優先度付きキュー（A* など） |
    | [`std::queue`](containers/queue.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 先入れ先出し |
    | [`std::stack`](containers/stack.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 後入れ先出し |
    | [`std::set`](containers/set.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 順序付きの集合 |
    | [`std::flat_map`](containers/flat_map.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | vector ベースの map <span class="ver ver-23">C++23</span> |
    | [`std::mdspan`](containers/mdspan.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 多次元配列のビュー <span class="ver ver-23">C++23</span> |
    | [`std::bitset`](containers/bitset.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 固定長のビット列 |
    | [`std::list`](containers/list.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-1">×</span> | 連結リスト。ほぼ使わない |
    | [`std::forward_list`](containers/forward_list.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-1">×</span> | 片方向リスト |
    | [`std::multimap` / `multiset`](containers/multimap.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | キー重複ありの map / set |
    | [`std::flat_set`](containers/flat_set.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | vector ベースの set <span class="ver ver-23">C++23</span> |

??? abstract "アルゴリズム（25）: 並べ替え・検索・変換"
    C++20 以降は `std::ranges::` 版を使うのが基本です。

    | アルゴリズム | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::ranges::sort`](algorithms/sort.md) | <span class="rank rank-must">必須</span> | 並べ替え |
    | [`std::erase_if`](algorithms/erase_if.md) | <span class="rank rank-must">必須</span> | 条件に合う要素を削除 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::find` / `find_if`](algorithms/find.md) | <span class="rank rank-must">必須</span> | 要素を探す |
    | [`std::ranges::any_of` / `all_of` / `none_of`](algorithms/any_of.md) | <span class="rank rank-often">よく使う</span> | 条件を満たすものがあるか |
    | [`std::ranges::count_if`](algorithms/count_if.md) | <span class="rank rank-often">よく使う</span> | 条件に合う数を数える |
    | [`std::ranges::min` / `max` / `minmax`](algorithms/min_max.md) | <span class="rank rank-often">よく使う</span> | 最小・最大 |
    | [`std::clamp`](algorithms/clamp.md) | <span class="rank rank-often">よく使う</span> | 範囲内に収める |
    | [`std::ranges::min_element` / `max_element`](algorithms/min_element.md) | <span class="rank rank-often">よく使う</span> | 最小・最大の要素の位置 |
    | [`std::views::filter` / `transform`](algorithms/views.md) | <span class="rank rank-often">よく使う</span> | 範囲を加工して見る |
    | [`std::ranges::to`](algorithms/ranges_to.md) | <span class="rank rank-often">よく使う</span> | 範囲をコンテナに変換 <span class="ver ver-23">C++23</span> |
    | [`std::accumulate` / `ranges::fold_left`](algorithms/accumulate.md) | <span class="rank rank-sometimes">たまに</span> | 合計・畳み込み |
    | [`std::ranges::shuffle`](algorithms/shuffle.md) | <span class="rank rank-sometimes">たまに</span> | ランダムに並べ替え |
    | [`std::ranges::reverse`](algorithms/reverse.md) | <span class="rank rank-sometimes">たまに</span> | 逆順にする |
    | [`std::ranges::binary_search` / `lower_bound`](algorithms/binary_search.md) | <span class="rank rank-sometimes">たまに</span> | ソート済み範囲の二分探索 |
    | [`std::ranges::unique`](algorithms/unique.md) | <span class="rank rank-sometimes">たまに</span> | 連続する重複を除く |
    | [`std::ranges::copy` / `fill`](algorithms/copy_fill.md) | <span class="rank rank-sometimes">たまに</span> | コピー・埋める |
    | [`std::ranges::stable_sort`](algorithms/stable_sort.md) | <span class="rank rank-sometimes">たまに</span> | 同じ値の順番を保つ並べ替え |
    | [`std::ranges::partial_sort` / `nth_element`](algorithms/partial_sort.md) | <span class="rank rank-rare">知ってるだけ</span> | 上位 N 件だけ並べる |
    | [`std::ranges::for_each`](algorithms/for_each.md) | <span class="rank rank-sometimes">たまに</span> | 全要素に関数を呼ぶ（普段は範囲 for） |
    | [`std::ranges::replace` / `remove`](algorithms/replace.md) | <span class="rank rank-sometimes">たまに</span> | 値の置き換え・前に詰める |
    | [`std::ranges::partition`](algorithms/partition.md) | <span class="rank rank-sometimes">たまに</span> | 条件で 2 つに分ける |
    | [`std::ranges::equal` / `mismatch`](algorithms/equal.md) | <span class="rank rank-sometimes">たまに</span> | 2 つの範囲が同じか・どこが違うか |
    | [`std::ranges::search` / `adjacent_find` / `is_sorted`](algorithms/search.md) | <span class="rank rank-rare">知ってるだけ</span> | 並びのパターンを探す |
    | [集合演算（`set_union` など）](algorithms/set_operations.md) | <span class="rank rank-rare">知ってるだけ</span> | ソート済み範囲の共通部分・和・差 |
    | [`std::ranges::make_heap` など](algorithms/heap.md) | <span class="rank rank-rare">知ってるだけ</span> | ヒープの操作 |

??? abstract "ユーティリティ（14）: optional, unique_ptr, format などの便利な部品"
    | 機能 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::unique_ptr`](utilities/unique_ptr.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 所有権が 1 つのスマートポインタ |
    | [`std::optional`](utilities/optional.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 値がないかもしれない <span class="ver ver-17">C++17</span> |
    | [`std::format` / `std::print`](utilities/format.md) | <span class="rank rank-must">必須</span> | — | 文字列の整形と出力 <span class="ver ver-23">C++23</span> |
    | [`std::pair` / `std::tuple`](utilities/pair_tuple.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 複数の値をまとめる |
    | [`std::shared_ptr` / `weak_ptr`](utilities/shared_ptr.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 共有するスマートポインタ |
    | [`std::function`](utilities/function.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 関数を変数に入れる |
    | [`std::move` / `std::forward`](utilities/move.md) | <span class="rank rank-often">よく使う</span> | — | ムーブと転送 |
    | [`std::expected`](utilities/expected.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 値かエラーのどちらか <span class="ver ver-23">C++23</span> |
    | [`std::string_view`](utilities/string_view.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 文字列を借りる <span class="ver ver-17">C++17</span> |
    | [`std::variant`](utilities/variant.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 複数の型のどれか 1 つ <span class="ver ver-17">C++17</span> |
    | [`std::chrono`](utilities/chrono.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 時間の計測 |
    | [`<random>`](utilities/random.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 乱数 |
    | [`std::any`](utilities/any.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 何でも入る箱 |
    | [`std::hash`](utilities/hash.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | ハッシュ値。自作の型を unordered_map のキーにする |

??? abstract "メモリ（5）: 確保の仕組み、アロケータ、C 由来の関数"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`new` と `delete`・配置 new](memory/new_delete.md) | <span class="rank rank-often">よく使う</span> | 確保 + 作成、破棄 + 解放。配置 new、`construct_at` |
    | [`std::allocator`](memory/allocator.md) | <span class="rank rank-sometimes">たまに</span> | コンテナのメモリの取り先。自作アロケータ |
    | [`std::pmr`](memory/pmr.md) | <span class="rank rank-sometimes">たまに</span> | 型を変えずに取り先を切り替える。フレーム用の領域 |
    | [`malloc` / `free`](memory/c-memory.md) | <span class="rank rank-sometimes">たまに</span> | C 由来の確保。C ライブラリとの橋渡し |
    | [文字列・メモリ操作（cstring）](memory/cstring.md) | <span class="rank rank-sometimes">たまに</span> | `memcpy`、`memset`、`strlen` など |

??? abstract "入出力・文字列（6）: ファイル、パス、文字列と数値の変換"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::filesystem`](io/filesystem.md) | <span class="rank rank-often">よく使う</span> | ファイル・フォルダの操作、パス |
    | [`std::ifstream` / `std::ofstream`](io/fstream.md) | <span class="rank rank-often">よく使う</span> | ファイルの読み書き |
    | [`std::stringstream`](io/sstream.md) | <span class="rank rank-sometimes">たまに</span> | 文字列を `>>` で分解する |
    | [`std::from_chars` / `to_chars`](io/charconv.md) | <span class="rank rank-sometimes">たまに</span> | 速くて例外なしの数値変換 |
    | [`std::cout` / `std::cin`](io/iostream.md) | <span class="rank rank-sometimes">たまに</span> | 標準入出力と書式フラグ |
    | [`std::regex`](io/regex.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現（遅い） |

??? abstract "数値（6）: 数学関数、定数、整数型、ビット操作"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`<cmath>`](numeric/cmath.md) | <span class="rank rank-must">必須</span> | sqrt、sin / cos、atan2、lerp など |
    | [`<cstdint>`](numeric/cstdint.md) | <span class="rank rank-often">よく使う</span> | `std::int32_t` など大きさの決まった整数 |
    | [`std::numeric_limits`](numeric/limits.md) | <span class="rank rank-often">よく使う</span> | 型の最大値・最小値 |
    | [`<numbers>`](numeric/numbers.md) | <span class="rank rank-often">よく使う</span> | π などの定数 |
    | [`<numeric>`](numeric/numeric.md) | <span class="rank rank-sometimes">たまに</span> | gcd、lcm、midpoint、累積和 |
    | [`<bit>`](numeric/bit.md) | <span class="rank rank-sometimes">たまに</span> | popcount、bit_cast など |

??? abstract "並行処理（6）: スレッドと、データの守り方"
    | 名前 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::thread` / `std::jthread`](concurrency/thread.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 別スレッドで動かす |
    | [`std::mutex`](concurrency/mutex.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 共有データを守る鍵 |
    | [`std::atomic`](concurrency/atomic.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 壊れない共有の数値・フラグ |
    | [`std::async` / `std::future`](concurrency/future.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 投げて、あとで結果を受け取る |
    | [`std::condition_variable`](concurrency/condition_variable.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 条件が満たされるまで眠って待つ |
    | [セマフォ・ラッチ・バリア](concurrency/semaphore.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 待ち合わせの道具 |

??? abstract "型・言語サポート（7）: イテレータの道具、関数オブジェクト、型の性質、例外"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`<iterator>`](support/iterator.md) | <span class="rank rank-sometimes">たまに</span> | next、distance、back_inserter |
    | [`<functional>`](support/functional.md) | <span class="rank rank-sometimes">たまに</span> | greater、hash、ref、bind_front |
    | [`<type_traits>`](support/type_traits.md) | <span class="rank rank-sometimes">たまに</span> | 型の性質を調べる |
    | [小さな便利機能](support/utility-misc.md) | <span class="rank rank-sometimes">たまに</span> | to_underlying、cmp_less、byte |
    | [標準の例外](support/exceptions.md) | <span class="rank rank-sometimes">たまに</span> | runtime_error、out_of_range など |
    | [`std::source_location` / `stacktrace`](support/source_location.md) | <span class="rank rank-sometimes">たまに</span> | 呼んだ場所・呼び出し履歴 |
    | [`std::generator`](support/generator.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンで値を順に作る |

STL を読むための前提知識は [基礎](../basics/index.md) にまとめています。
