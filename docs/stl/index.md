# STL

C++23 の標準ライブラリをゲーム制作でよく使う順にまとめています。見出しをクリックすると一覧が開きます。

迷ったら [コンテナの選び方](../basics/container-chart.md) も見てください。

??? abstract "コンテナ（39）: データをまとめて持つ入れ物"
    | コンテナ | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::vector`](containers/vector.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | あとから増減できる配列。要素が隣り合って並ぶので速い。迷ったらこれ。 |
    | [`std::array`](containers/array.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 個数が最初から決まっている配列。サイズ固定でヒープを使わない。 |
    | [`std::string`](containers/string.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-3">○</span> | 文字列を持つ型。連結・検索・切り出しができる。長さに応じて自動で伸びる。 |
    | [`std::unordered_map`](containers/unordered_map.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-3">○</span> | ハッシュ表。「キー → 値」をほぼ一定の時間で引ける。ID でデータを探すときに。 |
    | [`std::map`](containers/map.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | キーの順に並ぶ「キー → 値」の表。範囲で探したいとき・順番に回したいときに。 |
    | [`std::unordered_set`](containers/unordered_set.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 重複なしの集合。「入っているか」を素早く調べる。順番は気にしない。 |
    | [`std::span`](containers/span.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 配列の一部を「借りて」見る窓。コピーせず `vector` でも配列でも同じ関数で受けられる。 <span class="ver ver-20">C++20</span> |
    | [`std::deque`](containers/deque.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 先頭にも末尾にも素早く追加できる配列。ブロックに分かれて並ぶ。 |
    | [`std::priority_queue`](containers/priority_queue.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 一番優先度の高いものを、先に取り出せるキュー。A* の探索やイベント管理に。 |
    | [`std::queue`](containers/queue.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 先に入れたものを先に取り出す（先入れ先出し）。順番待ち・メッセージの受け渡しに。 |
    | [`std::stack`](containers/stack.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 後に入れたものを先に取り出す（後入れ先出し）。元に戻す（アンドゥ）や探索の履歴に。 |
    | [`std::set`](containers/set.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 順番に並んだ、重複なしの集合。範囲での検索（「以上・以下」）ができる。 |
    | [`std::flat_map`](containers/flat_map.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | `vector` で作った `map`。検索は速く回すのも速いが挿入・削除は遅い。 <span class="ver ver-23">C++23</span> |
    | [`std::mdspan`](containers/mdspan.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 1 次元の配列を 2 次元・3 次元として見る窓（コピーしない）。タイルマップや画像に。 <span class="ver ver-23">C++23</span> |
    | [`std::bitset`](containers/bitset.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 固定長のビット列。フラグをまとめて持つ。1 ビットずつのオン・オフを少ないメモリで。 |
    | [`std::initializer_list`](containers/initializer_list.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | {1, 2, 3} という波かっこの並びを、関数やコンストラクタが受け取るための型。 |
    | [`std::inplace_vector`](containers/inplace_vector.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 最大の大きさが決まっていて、ヒープを使わない vector。 <span class="ver ver-26">C++26</span> |
    | [`std::basic_string`](containers/basic_string.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 文字列クラスの正体。char 以外の文字型（wchar_t、char8_t など）にも使える。 |
    | [`std::list`](containers/list.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-1">×</span> | 連結リスト。途中の挿入・削除は速いが全体が遅く、ほとんど使わない。 |
    | [`std::forward_list`](containers/forward_list.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-1">×</span> | 片方向だけにつながるリスト。`list` より軽いが使う場面はほとんどない。 |
    | [`std::multimap`](containers/multimap.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同じキーを、複数持てる `map`。同じキーに複数の値をまとめたいときに。 |
    | [`std::flat_set`](containers/flat_set.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | `vector` で作った `set`。検索と巡回が速い。挿入・削除は遅い。 <span class="ver ver-23">C++23</span> |
    | [`std::multiset`](containers/multiset.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同じ値を複数持てる set。キーの順に並ぶ。同点を残したいときに。 |
    | [`std::unordered_multimap`](containers/unordered_multimap.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同じキーを複数持てる、ハッシュ表の map。順番はない。 |
    | [`std::unordered_multiset`](containers/unordered_multiset.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同じ値を複数持てる、ハッシュ表の set。順番はない。 |
    | [`std::flat_multimap`](containers/flat_multimap.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同じキーを複数持てる flat_map。vector 上に整列して並ぶ。 <span class="ver ver-23">C++23</span> |
    | [`std::flat_multiset`](containers/flat_multiset.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同じ値を複数持てる flat_set。vector 上に整列して並ぶ。 <span class="ver ver-23">C++23</span> |
    | [`std::vector<bool>`](containers/vector_bool.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-4">◎</span> | bool を 1 ビットずつに詰める、vector の特殊版。ふつうの vector とは別物。 |
    | [`std::valarray`](containers/valarray.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-4">◎</span> | 要素ごとの計算（足し算、掛け算）を、配列全体にまとめて書ける数値用の配列。 |
    | [`std::char_traits`](containers/char_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 文字型ごとの、比較・長さ・コピーといった基本の操作をまとめた部品。 |
    | [`std::extents`](containers/extents.md) | <span class="rank rank-rare">知ってるだけ</span> | — | mdspan の「各次元の大きさ」を表す型。コンパイル時に決める次元と、実行時に決める次元を混ぜられる。 <span class="ver ver-23">C++23</span> |
    | [`std::layout_right`](containers/layout_right.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 多次元の添字を、1 次元の位置に変える規則（行優先）。mdspan の既定。 <span class="ver ver-23">C++23</span> |
    | [`std::layout_left`](containers/layout_left.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 多次元の添字を、1 次元の位置に変える規則（列優先）。 <span class="ver ver-23">C++23</span> |
    | [`std::layout_stride`](containers/layout_stride.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 次元ごとの「歩幅」を自分で決める配置規則。 <span class="ver ver-23">C++23</span> |

    **文字列と数値の変換**

    | コンテナ | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::to_string`](containers/to_string.md) | <span class="rank rank-often">よく使う</span> | — | 数値を文字列にする。 |
    | [`std::stoi`](containers/stoi.md) | <span class="rank rank-often">よく使う</span> | — | 文字列を int に変換する（失敗すると例外）。 |
    | [`std::stof`](containers/stof.md) | <span class="rank rank-often">よく使う</span> | — | 文字列を float に変換する（失敗すると例外）。 |
    | [`std::stod`](containers/stod.md) | <span class="rank rank-sometimes">たまに</span> | — | 文字列を double に変換する（失敗すると例外）。 |
    | [`std::stoll`](containers/stoll.md) | <span class="rank rank-sometimes">たまに</span> | — | 文字列を long long に変換する（失敗すると例外）。 |

??? abstract "アルゴリズム（127）: 並べ替え・検索・変換"
    C++20 以降は `std::ranges::` 版を使うのが基本です。

    | アルゴリズム | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::ranges::sort`](algorithms/sort.md) | <span class="rank rank-must">必須</span> | 要素を小さい順（または指定の順）に並べ替える。比較の関数も渡せる。 <span class="ver ver-20">C++20</span> |
    | [`std::erase_if`](algorithms/erase_if.md) | <span class="rank rank-must">必須</span> | 条件に合う要素をまとめて消す。`erase-remove` を 1 行で書ける。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::find`](algorithms/find.md) | <span class="rank rank-must">必須</span> | 条件に合う最初の要素を探す。見つからなければ `end()` が返る。 <span class="ver ver-20">C++20</span> |
    | [`std::max`](algorithms/max.md) | <span class="rank rank-must">必須</span> | 2 つ以上の値や、範囲の中から、大きいほうを求める。 |
    | [`std::min`](algorithms/min.md) | <span class="rank rank-must">必須</span> | 2 つ以上の値や、範囲の中から、小さいほうを求める。 |
    | [`std::ranges::contains`](algorithms/contains.md) | <span class="rank rank-often">よく使う</span> | 範囲に、ある値が含まれているかを `bool` で答える。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::any_of`](algorithms/any_of.md) | <span class="rank rank-often">よく使う</span> | 条件を満たす要素が、1 つでもあるかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::all_of`](algorithms/all_of.md) | <span class="rank rank-often">よく使う</span> | 範囲の要素が全部、条件を満たすかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::count`](algorithms/count.md) | <span class="rank rank-often">よく使う</span> | 条件に合う要素が、いくつあるかを数える。 <span class="ver ver-20">C++20</span> |
    | [`std::clamp`](algorithms/clamp.md) | <span class="rank rank-often">よく使う</span> | 値を下限と上限の範囲内に収める（はみ出したら端の値にする）。 <span class="ver ver-17">C++17</span> |
    | [`std::ranges::min_element`](algorithms/min_element.md) | <span class="rank rank-often">よく使う</span> | 範囲の中で、最小の要素の「位置（イテレータ）」を返す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::max_element`](algorithms/max_element.md) | <span class="rank rank-often">よく使う</span> | 範囲の中で、最大の要素の「位置（イテレータ）」を返す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::to`](algorithms/ranges_to.md) | <span class="rank rank-often">よく使う</span> | 範囲（`views` の結果など）を `vector` などのコンテナに作り直す。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::transform`](algorithms/transform.md) | <span class="rank rank-often">よく使う</span> | 範囲の全要素を変換して、別の場所（または同じ場所）に書き出す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::remove`](algorithms/remove.md) | <span class="rank rank-often">よく使う</span> | 条件に合う要素を前に詰めて取り除く（remove-erase のイディオム）。 <span class="ver ver-20">C++20</span> |
    | [`std::accumulate`](algorithms/accumulate.md) | <span class="rank rank-sometimes">たまに</span> | 要素を先頭から順に足し込んで、合計などの 1 つの値を作る。 |
    | [`std::ranges::fold_left`](algorithms/fold_left.md) | <span class="rank rank-sometimes">たまに</span> | 範囲を左から畳み込んで、1 つの値にする（`accumulate` の範囲版）。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::none_of`](algorithms/none_of.md) | <span class="rank rank-sometimes">たまに</span> | 範囲の要素が 1 つも条件を満たさないかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::minmax`](algorithms/minmax.md) | <span class="rank rank-sometimes">たまに</span> | 最小と最大を、1 回の走査で両方求める。 |
    | [`std::ranges::search`](algorithms/search.md) | <span class="rank rank-sometimes">たまに</span> | 別の範囲の「連続した並び」が、含まれている場所を探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::shuffle`](algorithms/shuffle.md) | <span class="rank rank-sometimes">たまに</span> | 要素をランダムな順に並べ替える（カードの山のシャッフル）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::reverse`](algorithms/reverse.md) | <span class="rank rank-sometimes">たまに</span> | 範囲の並びを逆順にする（コピーして逆順にする版もある）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::rotate`](algorithms/rotate.md) | <span class="rank rank-sometimes">たまに</span> | 範囲の要素を回転させる（指定した要素が先頭に来る）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::stable_sort`](algorithms/stable_sort.md) | <span class="rank rank-sometimes">たまに</span> | 並べ替えるとき同じ値の要素の元の順番を、変えない。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::for_each`](algorithms/for_each.md) | <span class="rank rank-sometimes">たまに</span> | 全要素に関数を呼ぶ。普段は範囲 for のほうが読みやすい。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::lower_bound`](algorithms/lower_bound.md) | <span class="rank rank-sometimes">たまに</span> | 整列済みの範囲で、値以上の最初の要素の位置を、二分探索で探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::unique`](algorithms/unique.md) | <span class="rank rank-sometimes">たまに</span> | 隣り合う重複を 1 つにまとめる（並べ替えておくと全体の重複を除ける）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::binary_search`](algorithms/binary_search.md) | <span class="rank rank-sometimes">たまに</span> | 整列済みの範囲に、値があるかを、二分探索で調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::copy`](algorithms/copy.md) | <span class="rank rank-sometimes">たまに</span> | 範囲の要素を、別の場所にコピーする（条件つき・個数指定もある）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::equal`](algorithms/equal.md) | <span class="rank rank-sometimes">たまに</span> | 2 つの範囲の中身が、全部同じかを調べる。型が違う範囲どうしでも比べられる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::mismatch`](algorithms/mismatch.md) | <span class="rank rank-sometimes">たまに</span> | 2 つの範囲を先頭から比べて、最初に違うところを探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::replace`](algorithms/replace.md) | <span class="rank rank-sometimes">たまに</span> | 範囲の中の特定の値（または条件に合う要素）を、別の値に置き換える。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::fill`](algorithms/fill.md) | <span class="rank rank-sometimes">たまに</span> | 範囲の全要素を、同じ値で埋める。 <span class="ver ver-20">C++20</span> |
    | [`std::iota`](algorithms/iota.md) | <span class="rank rank-sometimes">たまに</span> | 範囲を、1 ずつ増える連番で埋める。 |
    | [`std::ranges::partition`](algorithms/partition.md) | <span class="rank rank-sometimes">たまに</span> | 条件に合う要素を前、合わない要素を後ろに分ける（並びを入れ替える）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::generate`](algorithms/generate.md) | <span class="rank rank-sometimes">たまに</span> | 範囲の各要素を、関数を呼んだ結果で埋める。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::partition_copy`](algorithms/partition_copy.md) | <span class="rank rank-sometimes">たまに</span> | 条件に合う要素と合わない要素を、元を残したまま 2 つの場所に振り分ける。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::adjacent_find`](algorithms/adjacent_find.md) | <span class="rank rank-sometimes">たまに</span> | 隣り合う 2 つの要素が等しい（または条件を満たす）最初の場所を探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::is_sorted`](algorithms/is_sorted.md) | <span class="rank rank-sometimes">たまに</span> | 範囲が並んでいるか（または、どこまで並んでいるか）を調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::find_last`](algorithms/find_last.md) | <span class="rank rank-rare">知ってるだけ</span> | 条件に合う（または等しい）最後の要素を探す。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::fold_right`](algorithms/fold_right.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を右から畳み込んで、1 つの値にする。 <span class="ver ver-23">C++23</span> |
    | [`std::reduce`](algorithms/reduce.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を合計などにまとめる。順序を問わないので、並列に実行できる。 <span class="ver ver-17">C++17</span> |
    | [`std::transform_reduce`](algorithms/transform_reduce.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を変換してから、合計などにまとめる（内積に使える）。 <span class="ver ver-17">C++17</span> |
    | [`std::inner_product`](algorithms/inner_product.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの範囲の内積（要素ごとの積の合計）を求める。 |
    | [`std::partial_sum`](algorithms/partial_sum.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭からの累積和（途中までの合計）を求める。 |
    | [`std::adjacent_difference`](algorithms/adjacent_difference.md) | <span class="rank rank-rare">知ってるだけ</span> | 隣り合う要素の差を求める。 |
    | [`std::inclusive_scan`](algorithms/inclusive_scan.md) | <span class="rank rank-rare">知ってるだけ</span> | 累積和（各位置までの合計、その位置を含む）を求める。並列化できる。 <span class="ver ver-17">C++17</span> |
    | [`std::ranges::minmax_element`](algorithms/minmax_element.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の中で、最小と最大の要素の位置を、1 回の走査で両方返す。 <span class="ver ver-20">C++20</span> |
    | [`std::exclusive_scan`](algorithms/exclusive_scan.md) | <span class="rank rank-rare">知ってるだけ</span> | 累積和（各位置の手前までの合計、その位置を含まない）を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::ranges::sample`](algorithms/sample.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲からランダムに N 個を選んで取り出す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::partial_sort`](algorithms/partial_sort.md) | <span class="rank rank-rare">知ってるだけ</span> | 全部は並べず、先頭の N 件だけを整列させる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::nth_element`](algorithms/nth_element.md) | <span class="rank rank-rare">知ってるだけ</span> | N 番目に小さい要素を、正しい位置に置く（中央値などを速く求める）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::upper_bound`](algorithms/upper_bound.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの範囲で、値より大きい最初の要素の位置を、二分探索で探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::unique_copy`](algorithms/unique_copy.md) | <span class="rank rank-rare">知ってるだけ</span> | 隣り合う重複をまとめた結果を、元を残したまま別の場所に作る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::equal_range`](algorithms/equal_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの範囲で、値と等しい要素の範囲を、二分探索で求める。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::lexicographical_compare`](algorithms/lexicographical_compare.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの範囲を辞書順で比べて、前のほうが小さいかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::is_permutation`](algorithms/is_permutation.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの範囲が、並べ替えれば同じになる（要素の種類と数が同じ）かを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::replace_copy`](algorithms/replace_copy.md) | <span class="rank rank-rare">知ってるだけ</span> | 値を置き換えた結果を、元を残したまま別の場所へ作る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::remove_copy`](algorithms/remove_copy.md) | <span class="rank rank-rare">知ってるだけ</span> | 条件に合わない要素だけを、別の場所へコピーする（元は変わらない）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::stable_partition`](algorithms/stable_partition.md) | <span class="rank rank-rare">知ってるだけ</span> | 元の順序を保ったまま、条件に合う要素を前に、合わない要素を後ろに分ける。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::copy_backward`](algorithms/copy_backward.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を、後ろの要素から順にコピーする（コピー先が後ろに重なるとき）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::partition_point`](algorithms/partition_point.md) | <span class="rank rank-rare">知ってるだけ</span> | `partition` 済みの範囲で、境目を二分探索で見つける。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::is_partitioned`](algorithms/is_partitioned.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲が、条件で分けられているかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::move`](algorithms/move.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素を、コピーせずに別の場所へ「移す」。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::move_backward`](algorithms/move_backward.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素を、後ろから順にムーブして移す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::swap_ranges`](algorithms/swap_ranges.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの範囲の要素を、先頭から順に入れ替える。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::search_n`](algorithms/search_n.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じ値が n 個続いている場所を探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::starts_with`](algorithms/starts_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲が、別の範囲の並びで始まるかを調べる。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::ends_with`](algorithms/ends_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲が、別の範囲の並びで終わるかを調べる。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::find_first_of`](algorithms/find_first_of.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の中で、候補のどれかと等しい最初の要素を探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::find_end`](algorithms/find_end.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の中で、別の範囲の並びが最後に現れる場所を探す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::next_permutation`](algorithms/next_permutation.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素の並びを、辞書順で次の並べ方にする。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::prev_permutation`](algorithms/prev_permutation.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素の並びを、辞書順で前の並べ方にする。 <span class="ver ver-20">C++20</span> |
    | [`std::shift_left`](algorithms/shift_left.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素を、前（左）へずらす。空いた後ろは放置する。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::make_heap`](algorithms/make_heap.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を、最大の要素が先頭に来るヒープに並べ替える。 <span class="ver ver-20">C++20</span> |
    | [`std::shift_right`](algorithms/shift_right.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素を、後ろ（右）へずらす。空いた前は放置する。 <span class="ver ver-20">C++20</span> |
    | [`std::iter_swap`](algorithms/iter_swap.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのイテレータが指す要素を入れ替える。 |
    | [`std::ranges::push_heap`](algorithms/push_heap.md) | <span class="rank rank-rare">知ってるだけ</span> | 末尾に足した要素を、ヒープに入れる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::pop_heap`](algorithms/pop_heap.md) | <span class="rank rank-rare">知ってるだけ</span> | ヒープの最大の要素を末尾に動かして、残りをヒープに保つ。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::sort_heap`](algorithms/sort_heap.md) | <span class="rank rank-rare">知ってるだけ</span> | ヒープを、小さい順に整列した範囲にする。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::is_heap`](algorithms/is_heap.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲がヒープになっているかを調べる（どこまでかを調べる版もある）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::set_union`](algorithms/set_union.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの 2 つの範囲の「和集合」を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::set_intersection`](algorithms/set_intersection.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの 2 つの範囲の「共通部分」を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::set_difference`](algorithms/set_difference.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの 2 つの範囲の「差集合」（前にだけある要素）を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::set_symmetric_difference`](algorithms/set_symmetric_difference.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの 2 つの範囲の、どちらか片方にだけある要素を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::includes`](algorithms/includes.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの範囲が、別の整列済みの範囲を全部含んでいるかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::merge`](algorithms/merge.md) | <span class="rank rank-rare">知ってるだけ</span> | 整列済みの 2 つの範囲を、整列を保ったまま 1 つに併合する。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::inplace_merge`](algorithms/inplace_merge.md) | <span class="rank rank-rare">知ってるだけ</span> | 1 つの範囲の前半・後半（どちらも整列済み）を、その場で併合する。 <span class="ver ver-20">C++20</span> |
    | [実行ポリシー（std::execution）](algorithms/execution.md) | <span class="rank rank-rare">知ってるだけ</span> | アルゴリズムに「並列に実行してよい」と伝える指定。 <span class="ver ver-17">C++17</span> |

    **ビュー（std::views）**

    | アルゴリズム | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::views::filter`](algorithms/views/filter.md) | <span class="rank rank-must">必須</span> | 条件に合う要素だけが見える範囲を作る（元は変わらない）。 <span class="ver ver-20">C++20</span> |
    | [`std::views::transform`](algorithms/views/transform.md) | <span class="rank rank-must">必須</span> | 各要素を変換した結果が見える範囲を作る（元は変わらない）。 <span class="ver ver-20">C++20</span> |
    | [std::views（範囲を加工して見る）](algorithms/views.md) | <span class="rank rank-often">よく使う</span> | 範囲をコピーせずに絞り込み（`filter`）や変換（`transform`）をして「見る」。 <span class="ver ver-20">C++20</span> |
    | [`std::views::take`](algorithms/views/take.md) | <span class="rank rank-often">よく使う</span> | 先頭から n 個だけが見える範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::drop`](algorithms/views/drop.md) | <span class="rank rank-often">よく使う</span> | 先頭の n 個を飛ばした、残りが見える範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::reverse`](algorithms/views/reverse.md) | <span class="rank rank-often">よく使う</span> | 逆順に並んで見える範囲を作る（コピーも書き換えもしない）。 <span class="ver ver-20">C++20</span> |
    | [`std::views::iota`](algorithms/views/iota.md) | <span class="rank rank-often">よく使う</span> | 連番（0, 1, 2, …）を、配列を作らずに並べて見る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::enumerate`](algorithms/views/enumerate.md) | <span class="rank rank-often">よく使う</span> | 各要素に 0 から始まる番号を付けた組 (番号, 要素) として見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::zip`](algorithms/views/zip.md) | <span class="rank rank-often">よく使う</span> | 複数の範囲を、同じ位置どうしの組にして同時に回す。 <span class="ver ver-23">C++23</span> |
    | [`std::views::take_while`](algorithms/views/take_while.md) | <span class="rank rank-sometimes">たまに</span> | 条件を満たす間だけが見える範囲を作る（最初に満たさなくなった所で終わる）。 <span class="ver ver-20">C++20</span> |
    | [`std::views::drop_while`](algorithms/views/drop_while.md) | <span class="rank rank-sometimes">たまに</span> | 条件を満たす間は飛ばし、そのあとの全部が見える範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::join`](algorithms/views/join.md) | <span class="rank rank-sometimes">たまに</span> | 入れ子の範囲（範囲の範囲）を、1 本につなげて見る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::split`](algorithms/views/split.md) | <span class="rank rank-sometimes">たまに</span> | 区切りの値（または並び）で、範囲を分割して見る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::keys`](algorithms/views/keys.md) | <span class="rank rank-sometimes">たまに</span> | map などから、キーだけが見える範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::values`](algorithms/views/values.md) | <span class="rank rank-sometimes">たまに</span> | map などから、値だけが見える範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::subrange`](algorithms/views/subrange.md) | <span class="rank rank-sometimes">たまに</span> | 2 つのイテレータ（または先頭と終わり）で表す範囲。 <span class="ver ver-20">C++20</span> |
    | [`std::views::slide`](algorithms/views/slide.md) | <span class="rank rank-sometimes">たまに</span> | 長さ n の窓を、1 つずつずらしながら見る（移動平均など）。 <span class="ver ver-23">C++23</span> |
    | [`std::views::chunk`](algorithms/views/chunk.md) | <span class="rank rank-sometimes">たまに</span> | 範囲を、n 個ずつの塊に区切って見る（重ならない）。 <span class="ver ver-23">C++23</span> |
    | [`std::views::chunk_by`](algorithms/views/chunk_by.md) | <span class="rank rank-sometimes">たまに</span> | 隣り合う要素の条件で、範囲を塊に区切って見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::stride`](algorithms/views/stride.md) | <span class="rank rank-sometimes">たまに</span> | n 個おきに要素を取って見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::join_with`](algorithms/views/join_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 入れ子の範囲を、区切りを挟んで 1 本につなげて見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::lazy_split`](algorithms/views/lazy_split.md) | <span class="rank rank-rare">知ってるだけ</span> | 区切りで分割する（入力範囲にも使える、遅延する版）。 <span class="ver ver-20">C++20</span> |
    | [`std::views::elements`](algorithms/views/elements.md) | <span class="rank rank-rare">知ってるだけ</span> | tuple（や pair）の範囲から、N 番目の要素だけを取り出して見る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::repeat`](algorithms/views/repeat.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じ値を、繰り返し並べて見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::single`](algorithms/views/single.md) | <span class="rank rank-rare">知ってるだけ</span> | 1 つの値だけを持つ範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::empty`](algorithms/views/empty.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素が 1 つもない範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::counted`](algorithms/views/counted.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭の位置と個数から、範囲を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::views::common`](algorithms/views/common.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭と終わりの型が違う範囲を、同じ型の範囲に整える。 <span class="ver ver-20">C++20</span> |
    | [`std::views::all`](algorithms/views/all.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を、軽いビューとして扱えるようにする。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::ref_view`](algorithms/views/ref_view.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を参照する、軽いビュー。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::owning_view`](algorithms/views/owning_view.md) | <span class="rank rank-rare">知ってるだけ</span> | 右辺値の範囲を引き取って、所有するビュー。 <span class="ver ver-20">C++20</span> |
    | [`std::views::as_const`](algorithms/views/as_const.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を読み取り専用にして見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::as_rvalue`](algorithms/views/as_rvalue.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を右辺値（ムーブ可能）として見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::zip_transform`](algorithms/views/zip_transform.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の範囲の同じ位置どうしに関数を適用した結果を並べる。 <span class="ver ver-23">C++23</span> |
    | [`std::views::adjacent`](algorithms/views/adjacent.md) | <span class="rank rank-rare">知ってるだけ</span> | 隣り合う n 個を、1 つの組にして順にずらしながら見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::adjacent_transform`](algorithms/views/adjacent_transform.md) | <span class="rank rank-rare">知ってるだけ</span> | 隣り合う n 個に関数を適用した結果を並べる。 <span class="ver ver-23">C++23</span> |
    | [`std::views::cartesian_product`](algorithms/views/cartesian_product.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の範囲の、すべての組み合わせを並べて見る。 <span class="ver ver-23">C++23</span> |
    | [`std::views::istream_view`](algorithms/views/istream_view.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力ストリームから、値を 1 つずつ読み出す範囲を作る。 <span class="ver ver-20">C++20</span> |

??? abstract "ユーティリティ（96）: optional, unique_ptr, format などの便利な部品"
    | 機能 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::unique_ptr`](utilities/unique_ptr.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 持ち主が 1 つだけの、スマートポインタ。スコープを出ると自動で解放される。 |
    | [`std::optional`](utilities/optional.md) | <span class="rank rank-must">必須</span> | <span class="perf perf-4">◎</span> | 値が「あるかもしれない・ないかもしれない」を表す。見つからないことを `nullptr` なしで示せる。 <span class="ver ver-17">C++17</span> |
    | [`std::print`](utilities/print.md) | <span class="rank rank-must">必須</span> | — | 書式に従って、そのまま画面（標準出力）に出す。println は末尾に改行を付ける。 <span class="ver ver-23">C++23</span> |
    | [`std::format`](utilities/format.md) | <span class="rank rank-must">必須</span> | — | `{}` を使って、文字列を整形する（`printf` の安全版）。書式の書き方を一通りまとめている。 <span class="ver ver-20">C++20</span> |
    | [`std::make_unique`](utilities/make_unique.md) | <span class="rank rank-must">必須</span> | — | オブジェクトを作って unique_ptr にする。普通はこれで unique_ptr を作る。 |
    | [`std::make_shared`](utilities/make_shared.md) | <span class="rank rank-must">必須</span> | — | オブジェクトを作って shared_ptr にする。普通はこれで shared_ptr を作る。 |
    | [`std::pair`](utilities/pair.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 2 つの値を、1 つにまとめる。map の要素や、関数が 2 つの値を返すときに。 |
    | [`std::shared_ptr`](utilities/shared_ptr.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 持ち主が複数いる、スマートポインタ。最後の持ち主が消えたときに解放される。 |
    | [`std::function`](utilities/function.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | 関数・ラムダ式を変数に入れて持つ。コールバックの保存に。 |
    | [`std::get`](utilities/get.md) | <span class="rank rank-often">よく使う</span> | — | pair / tuple / array / variant の N 番目（または型で）の要素を取り出す。 |
    | [`std::weak_ptr`](utilities/weak_ptr.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-3">○</span> | shared_ptr の持ち物を、持ち主にならずに見る。相手が消えたかを確かめられる。 |
    | [`std::move`](utilities/move.md) | <span class="rank rank-often">よく使う</span> | — | コピーせず中身を「移す」ための道具（`move`・`forward`）。 |
    | [`std::expected`](utilities/expected.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 「成功した値」か「エラー」の、どちらかを返す。例外を使わないエラー処理に。 <span class="ver ver-23">C++23</span> |
    | [`std::string_view`](utilities/string_view.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 文字列をコピーせずに「借りて」見る。引数で文字列を受け取るときの定番。 <span class="ver ver-17">C++17</span> |
    | [`std::visit`](utilities/visit.md) | <span class="rank rank-often">よく使う</span> | — | variant の中身の型に応じて、処理を呼び分ける。 <span class="ver ver-17">C++17</span> |
    | [`std::get_if`](utilities/get_if.md) | <span class="rank rank-often">よく使う</span> | — | variant から、その型の値へのポインターを取る（違う型ならヌル）。 <span class="ver ver-17">C++17</span> |
    | [`std::hash`](utilities/hash.md) | <span class="rank rank-often">よく使う</span> | <span class="perf perf-4">◎</span> | 値から、ハッシュ値を作る。自作の型を `unordered_map` のキーにするときに。 |
    | [`std::move_only_function`](utilities/move_only_function.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | ムーブだけできる関数を保持する（std::function のコピー不要版）。 <span class="ver ver-23">C++23</span> |
    | [`std::format_to`](utilities/format_to.md) | <span class="rank rank-sometimes">たまに</span> | — | 文字列を、既にある場所に書き込む。確保を減らしたいときに。 <span class="ver ver-20">C++20</span> |
    | [`std::tuple`](utilities/tuple.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 3 つ以上の値を、型がバラバラのまま 1 つにまとめる。 |
    | [`std::formatter`](utilities/formatter.md) | <span class="rank rank-sometimes">たまに</span> | — | 自作の型を、{} で出せるようにする。 <span class="ver ver-20">C++20</span> |
    | [`std::tie`](utilities/tie.md) | <span class="rank rank-sometimes">たまに</span> | — | 変数の参照をまとめた tuple を作る。複数の条件での比較に使う。 |
    | [`std::forward`](utilities/forward.md) | <span class="rank rank-sometimes">たまに</span> | — | テンプレートで受け取った引数を、左辺値・右辺値のまま次の関数へ渡す（完全転送）。 |
    | [`std::make_pair`](utilities/make_pair.md) | <span class="rank rank-sometimes">たまに</span> | — | 型を推論して pair を作る。 |
    | [`std::exchange`](utilities/exchange.md) | <span class="rank rank-sometimes">たまに</span> | — | 新しい値を入れて、古い値を返す。 |
    | [`std::swap`](utilities/swap.md) | <span class="rank rank-sometimes">たまに</span> | — | 2 つの値を入れ替える。 |
    | [`std::variant`](utilities/variant.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 「複数の型のうちどれか 1 つ」を持つ。状態や種類ごとのデータを型安全に持てる。 <span class="ver ver-17">C++17</span> |
    | [`std::holds_alternative`](utilities/holds_alternative.md) | <span class="rank rank-sometimes">たまに</span> | — | variant が今、その型の値を持っているかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::unexpected`](utilities/unexpected.md) | <span class="rank rank-sometimes">たまに</span> | — | expected に「失敗」の値を入れるための包み。 <span class="ver ver-23">C++23</span> |
    | [`std::nullopt`](utilities/nullopt.md) | <span class="rank rank-sometimes">たまに</span> | — | optional を「空」にするための印。 <span class="ver ver-17">C++17</span> |
    | [`std::vformat`](utilities/vformat.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式の文字列を、実行時に決める。 <span class="ver ver-20">C++20</span> |
    | [`std::allocate_shared`](utilities/allocate_shared.md) | <span class="rank rank-rare">知ってるだけ</span> | — | アロケータを指定して、オブジェクトを作って shared_ptr にする。 |
    | [`std::enable_shared_from_this`](utilities/enable_shared_from_this.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 自分自身を指す shared_ptr を、メンバ関数の中で安全に作る。 |
    | [`std::make_tuple`](utilities/make_tuple.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 型を推論して tuple を作る。 |
    | [`std::apply`](utilities/apply.md) | <span class="rank rank-rare">知ってるだけ</span> | — | tuple の中身をばらして、関数の引数として渡す。 <span class="ver ver-17">C++17</span> |
    | [`std::dynamic_pointer_cast`](utilities/dynamic_pointer_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | shared_ptr を、派生クラスの shared_ptr に変換する（static / const / reinterpret 版もある）。 |
    | [`std::make_from_tuple`](utilities/make_from_tuple.md) | <span class="rank rank-rare">知ってるだけ</span> | — | tuple の要素を引数にして、クラスのオブジェクトを作る。 <span class="ver ver-17">C++17</span> |
    | [`std::move_if_noexcept`](utilities/move_if_noexcept.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ムーブが例外を投げないときだけ、ムーブにする（そうでなければコピー）。 |
    | [`std::tuple_cat`](utilities/tuple_cat.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 複数の tuple を連結して、1 つの tuple にする。 |
    | [`std::any`](utilities/any.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | どんな型でも入る箱。型を実行時に確かめて取り出す。使う場面は少ない。 <span class="ver ver-17">C++17</span> |
    | [`std::forward_as_tuple`](utilities/forward_as_tuple.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 引数を完全転送のまま、参照の tuple にまとめる。 |
    | [`std::ignore`](utilities/ignore.md) | <span class="rank rank-rare">知ってるだけ</span> | — | tie や構造化束縛的な代入で、「この値は使わない」と書くための印。 |
    | [`std::monostate`](utilities/monostate.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 何も入っていない状態を表す、空の型。variant の先頭に置く。 <span class="ver ver-17">C++17</span> |
    | [`std::tuple_size`](utilities/tuple_size.md) | <span class="rank rank-rare">知ってるだけ</span> | — | tuple や pair、array の要素数、各要素の型を、コンパイル時に調べる。 |
    | [`std::any_cast`](utilities/any_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | any に入っている値を、型を指定して取り出す。 <span class="ver ver-17">C++17</span> |
    | [`std::piecewise_construct`](utilities/piecewise_construct.md) | <span class="rank rank-rare">知ってるだけ</span> | — | pair の 2 つの要素を、それぞれ別のコンストラクタ引数で作るための印。 |
    | [`std::make_any`](utilities/make_any.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 値を作りながら any に入れる。 <span class="ver ver-17">C++17</span> |
    | [`std::in_place`](utilities/in_place.md) | <span class="rank rank-rare">知ってるだけ</span> | — | optional / variant / any の中に、オブジェクトをその場で構築するための印。 <span class="ver ver-17">C++17</span> |
    | [`std::bad_expected_access`](utilities/bad_expected_access.md) | <span class="rank rank-rare">知ってるだけ</span> | — | エラーを持つ expected から value() で値を取り出したときの例外。 <span class="ver ver-23">C++23</span> |
    | [`std::addressof`](utilities/addressof.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `operator&` が書き換えられていても、オブジェクトの本当のアドレスを取る。 |
    | [`std::declval`](utilities/declval.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 式の中でだけ使う、「その型の値があるとみなす」ための関数（decltype 専用）。 |
    | [`std::integer_sequence`](utilities/integer_sequence.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 整数の並び（0, 1, 2, …）をコンパイル時に作る。テンプレートで tuple などを展開する部品。 |
    | [`std::out_ptr`](utilities/out_ptr.md) | <span class="rank rank-rare">知ってるだけ</span> | — | C のAPI が「ポインターのポインター」で返すオブジェクトを、スマートポインターで受け取る。 <span class="ver ver-23">C++23</span> |
    | [`std::inout_ptr`](utilities/inout_ptr.md) | <span class="rank rank-rare">知ってるだけ</span> | — | C のAPI に、既存のポインターを渡して、置き換えてもらう。 <span class="ver ver-23">C++23</span> |

    **乱数の分布（std::xxx_distribution）**

    | 機能 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::uniform_int_distribution`](utilities/random/uniform_int_distribution.md) | <span class="rank rank-must">必須</span> | — | 範囲内の整数を、同じ確率で出す（両端を含む）。 |
    | [`std::uniform_real_distribution`](utilities/random/uniform_real_distribution.md) | <span class="rank rank-must">必須</span> | — | 範囲内の小数を、同じ確率で出す（上限は含まない）。 |
    | [`std::bernoulli_distribution`](utilities/random/bernoulli_distribution.md) | <span class="rank rank-often">よく使う</span> | — | 確率 p で true、そうでなければ false を出す。 |
    | [`std::discrete_distribution`](utilities/random/discrete_distribution.md) | <span class="rank rank-sometimes">たまに</span> | — | 重みに比例した確率で、添字を選ぶ（ガチャ・ドロップ抽選）。 |
    | [`std::normal_distribution`](utilities/random/normal_distribution.md) | <span class="rank rank-sometimes">たまに</span> | — | 正規分布（釣り鐘型）。平均の近くが出やすい。 |
    | [`std::binomial_distribution`](utilities/random/binomial_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「確率 p の試行を t 回やったとき、成功した回数」を出す。 |
    | [`std::negative_binomial_distribution`](utilities/random/negative_binomial_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「k 回成功するまでに、失敗した回数」を出す。 |
    | [`std::geometric_distribution`](utilities/random/geometric_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「最初に成功するまでに、失敗した回数」を出す。 |
    | [`std::poisson_distribution`](utilities/random/poisson_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「一定時間に起きる出来事の回数」を出す。 |
    | [`std::exponential_distribution`](utilities/random/exponential_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「出来事と出来事の間隔」を出す。 |
    | [`std::gamma_distribution`](utilities/random/gamma_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ガンマ分布。待ち時間の合計や、偏った正の値に。 |
    | [`std::weibull_distribution`](utilities/random/weibull_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ワイブル分布。故障までの時間などに使う。 |
    | [`std::extreme_value_distribution`](utilities/random/extreme_value_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 極値分布（ガンベル分布）。最大値・最小値のばらつきに。 |
    | [`std::lognormal_distribution`](utilities/random/lognormal_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 対数正規分布。正の値で、右に裾が長い。 |
    | [`std::chi_squared_distribution`](utilities/random/chi_squared_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | カイ二乗分布。統計の検定に使われる。 |
    | [`std::cauchy_distribution`](utilities/random/cauchy_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | コーシー分布。極端な外れ値が出やすい。 |
    | [`std::fisher_f_distribution`](utilities/random/fisher_f_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | F 分布。分散の比の検定に使われる。 |
    | [`std::student_t_distribution`](utilities/random/student_t_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | スチューデントの t 分布。少ないデータでの平均の検定に使う。 |
    | [`std::piecewise_constant_distribution`](utilities/random/piecewise_constant_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 区間ごとに重みを決めた、連続値の乱数。 |
    | [`std::piecewise_linear_distribution`](utilities/random/piecewise_linear_distribution.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 境界点の重みを直線でつないだ、連続値の乱数。 |
    | [`std::generate_canonical`](utilities/random/generate_canonical.md) | <span class="rank rank-rare">知ってるだけ</span> | — | エンジンから、[0, 1) の小数の乱数を直接作る。 |

    **乱数エンジン**

    | 機能 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::mt19937`](utilities/random/mt19937.md) | <span class="rank rank-must">必須</span> | — | メルセンヌ・ツイスター。品質が良く速い、定番の乱数エンジン（32 ビット / 64 ビット版）。 |
    | [`std::random_device`](utilities/random/random_device.md) | <span class="rank rank-often">よく使う</span> | — | OS が用意する、予測しにくい乱数。エンジンの種を作るのに使う。 |
    | [`std::seed_seq`](utilities/random/seed_seq.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 複数の値から、エンジンの種を作る。 |
    | [`std::minstd_rand`](utilities/random/minstd_rand.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 軽い乱数エンジン（状態が 4 バイト）。品質は mt19937 より低い。 |
    | [`std::ranlux24`](utilities/random/ranlux24.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 品質が非常に高いが、遅い乱数エンジン（24 ビット / 48 ビット版）。 |
    | [`std::knuth_b`](utilities/random/knuth_b.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 内部で並べ替えを使う乱数エンジン。 |
    | [`std::default_random_engine`](utilities/random/default_random_engine.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 実装が選ぶ既定の乱数エンジン。環境によって中身が違うので、再現性が必要なら使わない。 |

    **乱数（std::random）**

    | 機能 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [<random>（乱数）](utilities/random.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 乱数を作る。シードと分布（一様・正規など）を組み合わせて使う。 |

    **時間（std::chrono）**

    | 機能 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::chrono::duration`](utilities/chrono/duration.md) | <span class="rank rank-must">必須</span> | — | 時間の長さ。単位（ミリ秒、秒など）を型で持つので、取り違えない。 |
    | [`std::chrono::steady_clock`](utilities/chrono/steady_clock.md) | <span class="rank rank-must">必須</span> | — | 巻き戻らない時計。時間の計測に使う。 |
    | [`std::chrono::time_point`](utilities/chrono/time_point.md) | <span class="rank rank-often">よく使う</span> | — | 時計の上の「ある時点」。 |
    | [`std::chrono::duration_cast`](utilities/chrono/duration_cast.md) | <span class="rank rank-often">よく使う</span> | — | 時間の単位を変換する（切り捨て）。 |
    | [`std::chrono_literals`](utilities/chrono/literals.md) | <span class="rank rank-often">よく使う</span> | — | 16ms、2s のように、単位つきの時間を書けるリテラル。 |
    | [`std::chrono::system_clock`](utilities/chrono/system_clock.md) | <span class="rank rank-sometimes">たまに</span> | — | 現実の時刻（カレンダー）を表す時計。 |
    | [`std::chrono`](utilities/chrono.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-4">◎</span> | 時間の長さ・時刻を扱う。フレームの時間計測や待ち時間に。 |
    | [`std::chrono::high_resolution_clock`](utilities/chrono/high_resolution_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 最も細かい時計（実体は環境しだい）。使わず steady_clock を使う。 |
    | [`std::chrono::floor`](utilities/chrono/floor.md) | <span class="rank rank-rare">知ってるだけ</span> | — | duration（または time_point）を、別の単位に丸める（切り捨て・切り上げ・四捨五入）。 <span class="ver ver-17">C++17</span> |
    | [`std::chrono::year_month_day`](utilities/chrono/year_month_day.md) | <span class="rank rank-rare">知ってるだけ</span> | — | カレンダーの日付（年・月・日）。曜日や日数の計算もできる。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::hh_mm_ss`](utilities/chrono/hh_mm_ss.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 経過時間を「時・分・秒」に分解する。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::zoned_time`](utilities/chrono/zoned_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | タイムゾーンつきの日時。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::file_clock`](utilities/chrono/file_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ファイルの更新日時に使われる時計。 <span class="ver ver-20">C++20</span> |

??? abstract "メモリ（50）: 確保の仕組み、アロケータ、C 由来の関数"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [new と delete・配置 new](memory/new_delete.md) | <span class="rank rank-often">よく使う</span> | メモリの確保と、オブジェクトの作成・破棄。配置 `new`、`construct_at` も含む。 |
    | [`std::allocator`](memory/allocator.md) | <span class="rank rank-sometimes">たまに</span> | コンテナのメモリの取り先。自作のアロケータで確保の方法を変えられる。 |
    | [`std::pmr`](memory/pmr.md) | <span class="rank rank-sometimes">たまに</span> | コンテナの型を変えずにメモリの取り先を、切り替える。フレーム用の領域に。 <span class="ver ver-17">C++17〜</span> |
    | [文字列・メモリ操作（cstring）](memory/cstring.md) | <span class="rank rank-sometimes">たまに</span> | `memcpy`、`memset`、`strlen` などバイト列のコピーや比較。 |
    | [`std::allocator_traits`](memory/allocator_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | アロケータの機能を、足りない部分を補って一様に使えるようにする窓口。 |
    | [`std::align`](memory/align.md) | <span class="rank rank-rare">知ってるだけ</span> | 確保済みの領域の中で、指定した境界にそろった位置を求める。 |
    | [`std::to_address`](memory/to_address.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインターやイテレータ（スマートポインターなど）から、生のポインターを取る。 <span class="ver ver-20">C++20</span> |
    | [`std::owner_less`](memory/owner_less.md) | <span class="rank rank-rare">知ってるだけ</span> | shared_ptr / weak_ptr を、「管理の持ち主」で並べ替える比較。 |
    | [`std::default_delete`](memory/default_delete.md) | <span class="rank rank-rare">知ってるだけ</span> | unique_ptr が既定で使う、`delete` を呼ぶだけの削除関数。 |
    | [`std::hardware_destructive_interference_size`](memory/hardware_destructive_interference_size.md) | <span class="rank rank-rare">知ってるだけ</span> | フォルス・シェアリングを避けるためにそろえる、キャッシュラインの大きさ。 <span class="ver ver-17">C++17</span> |

    **C の文字列・メモリ関数（<cstring>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [memcpy](memory/cstring/memcpy.md) | <span class="rank rank-sometimes">たまに</span> | メモリのバイト列を、別の場所へコピーする（重なっていてはいけない）。 |
    | [memset](memory/cstring/memset.md) | <span class="rank rank-sometimes">たまに</span> | メモリの範囲を、同じバイト値で埋める。 |
    | [strlen](memory/cstring/strlen.md) | <span class="rank rank-sometimes">たまに</span> | C 文字列（終端が \0）の長さを調べる。 |
    | [strcmp](memory/cstring/strcmp.md) | <span class="rank rank-sometimes">たまに</span> | C 文字列どうしを比べる。 |
    | [snprintf](memory/cstring/snprintf.md) | <span class="rank rank-sometimes">たまに</span> | 書式に従って、バッファの大きさを守って文字列を書き込む。 |
    | [memmove](memory/cstring/memmove.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリのバイト列を、別の場所へコピーする（重なっていてもよい）。 |
    | [memcmp](memory/cstring/memcmp.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのメモリを、バイト単位で比べる。 |
    | [strncmp](memory/cstring/strncmp.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列の先頭 n 文字だけを比べる。 |
    | [memchr](memory/cstring/memchr.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリの中から、1 バイトの値を探す。 |
    | [strchr](memory/cstring/strchr.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列の中から、1 文字を探す。 |
    | [strstr](memory/cstring/strstr.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列の中から、別の文字列を探す。 |
    | [strcpy](memory/cstring/strcpy.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列をコピーする（大きさを確認しない・危険）。 |
    | [strncpy](memory/cstring/strncpy.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列を最大 n 文字コピーする（終端に注意）。 |
    | [strcat](memory/cstring/strcat.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列の後ろに、別の C 文字列をつなげる（危険）。 |

    **C の確保関数（<cstdlib>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [malloc](memory/malloc.md) | <span class="rank rank-sometimes">たまに</span> | C 由来のメモリ確保（初期化しない）。 |
    | [free](memory/free.md) | <span class="rank rank-sometimes">たまに</span> | malloc で確保したメモリを解放する。 |
    | [calloc](memory/calloc.md) | <span class="rank rank-rare">知ってるだけ</span> | 0 で初期化して、メモリを確保する。 |
    | [realloc](memory/realloc.md) | <span class="rank rank-rare">知ってるだけ</span> | 確保したメモリの大きさを変える。 |
    | [aligned_alloc](memory/aligned_alloc.md) | <span class="rank rank-rare">知ってるだけ</span> | アラインメントを指定して、メモリを確保する。 |

    **new / delete まわり**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [new 式](memory/new_delete/new.md) | <span class="rank rank-often">よく使う</span> | オブジェクトをヒープに作る式。メモリ確保とコンストラクターの呼び出しを一度に行う。 |
    | [delete 式](memory/new_delete/delete.md) | <span class="rank rank-often">よく使う</span> | new で作ったオブジェクトを壊して、メモリを解放する式。 |
    | [new[] と delete[]](memory/new_delete/new_array.md) | <span class="rank rank-rare">知ってるだけ</span> | 配列をヒープに作り、解放する式。 |
    | [`std::nothrow`](memory/new_delete/nothrow.md) | <span class="rank rank-rare">知ってるだけ</span> | new が失敗したとき、例外ではなく nullptr を返させる指定。 |
    | [配置 new（placement new）](memory/new_delete/placement_new.md) | <span class="rank rank-rare">知ってるだけ</span> | 用意したメモリの上に、オブジェクトを作る。 |
    | [`std::construct_at`](memory/new_delete/construct_at.md) | <span class="rank rank-rare">知ってるだけ</span> | 確保済みのメモリの上に、オブジェクトを作る（配置 new の安全版）。 <span class="ver ver-20">C++20</span> |
    | [`std::destroy_at`](memory/new_delete/destroy_at.md) | <span class="rank rank-rare">知ってるだけ</span> | オブジェクトのデストラクターを呼ぶ（メモリは解放しない）。 <span class="ver ver-17">C++17</span> |
    | [operator new / operator delete](memory/new_delete/operator_new.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリの確保・解放だけを行う関数（new 式の内部で使われる）。 |
    | [`std::uninitialized_copy`](memory/new_delete/uninitialized_copy.md) | <span class="rank rank-rare">知ってるだけ</span> | 未初期化のメモリへ、要素を（コンストラクターで）コピーして作る。 |
    | [`std::launder`](memory/new_delete/launder.md) | <span class="rank rank-rare">知ってるだけ</span> | オブジェクトの置き換えを、コンパイラに知らせてポインターを取り直す。 <span class="ver ver-17">C++17</span> |
    | [`std::align_val_t`](memory/new_delete/align_val_t.md) | <span class="rank rank-rare">知ってるだけ</span> | new にアラインメントを指定するための型。 <span class="ver ver-17">C++17</span> |
    | [`std::set_new_handler`](memory/new_delete/set_new_handler.md) | <span class="rank rank-rare">知ってるだけ</span> | `new` が失敗したときに呼ばれる関数を登録する。 |

    **pmr のメモリリソースと部品**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::pmr::monotonic_buffer_resource`](memory/pmr/monotonic_buffer_resource.md) | <span class="rank rank-sometimes">たまに</span> | 積むだけで、個別には解放しないメモリ領域。フレーム用に一括解放する。 |
    | [`std::pmr::polymorphic_allocator`](memory/pmr/polymorphic_allocator.md) | <span class="rank rank-sometimes">たまに</span> | メモリリソースを実行時に切り替えられるアロケータ。pmr コンテナが使う。 |
    | [`std::pmr::vector`](memory/pmr/pmr_containers.md) | <span class="rank rank-sometimes">たまに</span> | メモリの取り先を渡せる、pmr 版のコンテナ（vector・string・map など）。 |
    | [`std::pmr::unsynchronized_pool_resource`](memory/pmr/unsynchronized_pool_resource.md) | <span class="rank rank-rare">知ってるだけ</span> | 大きさごとの置き場を持ち、解放した分を再利用するメモリ領域（スレッド非対応）。 |
    | [`std::pmr::synchronized_pool_resource`](memory/pmr/synchronized_pool_resource.md) | <span class="rank rank-rare">知ってるだけ</span> | 大きさごとの置き場を持つ、スレッドセーフなメモリ領域。 |
    | [`std::pmr::new_delete_resource`](memory/pmr/new_delete_resource.md) | <span class="rank rank-rare">知ってるだけ</span> | 普通の new / delete を使うメモリリソース（既定）。 |
    | [`std::pmr::null_memory_resource`](memory/pmr/null_memory_resource.md) | <span class="rank rank-rare">知ってるだけ</span> | 確保しようとすると必ず失敗するメモリリソース。 |
    | [`std::pmr::memory_resource`](memory/pmr/memory_resource.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリの取り先を表す、抽象基底クラス。 |
    | [`std::pmr::set_default_resource`](memory/pmr/default_resource.md) | <span class="rank rank-rare">知ってるだけ</span> | pmr コンテナの既定のメモリリソースを取得・変更する。 |

??? abstract "入出力・文字列（78）: ファイル、パス、文字列と数値の変換"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::ifstream`](io/ifstream.md) | <span class="rank rank-must">必須</span> | ファイルを読むための型（テキスト・バイナリ）。 |
    | [`std::ofstream`](io/ofstream.md) | <span class="rank rank-must">必須</span> | ファイルに書くための型（テキスト・バイナリ）。 |
    | [`std::getline`](io/getline.md) | <span class="rank rank-must">必須</span> | ストリームから 1 行を読んで、std::string に入れる。 |
    | [`std::filesystem`](io/filesystem.md) | <span class="rank rank-often">よく使う</span> | ファイルやフォルダの存在確認・一覧・コピー・削除。パスの扱い。 <span class="ver ver-17">C++17</span> |
    | [`std::ios_base`](io/ios_base.md) | <span class="rank rank-sometimes">たまに</span> | ストリームの状態と、開き方・書式のフラグをまとめた土台のクラス。 |
    | [`std::cout`](io/cout.md) | <span class="rank rank-sometimes">たまに</span> | 標準出力。画面に文字や値を出す（<< でつなぐ）。 |
    | [`std::stringstream`](io/stringstream.md) | <span class="rank rank-sometimes">たまに</span> | 文字列を、ストリームとして読み書きする（分解・組み立て）。 |
    | [`std::istringstream`](io/istringstream.md) | <span class="rank rank-sometimes">たまに</span> | 文字列から、値を読み出す（読む専用）。 |
    | [`std::ostringstream`](io/ostringstream.md) | <span class="rank rank-sometimes">たまに</span> | 値をつなげて、文字列を組み立てる（書く専用）。 |
    | [`std::from_chars`](io/from_chars.md) | <span class="rank rank-sometimes">たまに</span> | 文字列を数値に変換する。速くて、例外を投げない。 <span class="ver ver-17">C++17</span> |
    | [`std::to_chars`](io/to_chars.md) | <span class="rank rank-sometimes">たまに</span> | 数値を文字列に変換する。速くて、例外を投げない。 <span class="ver ver-17">C++17</span> |
    | [`std::ostream`](io/ostream.md) | <span class="rank rank-sometimes">たまに</span> | すべての出力ストリームの共通の親クラス。関数の引数にすると、画面にもファイルにも出せる。 |
    | [`std::istream`](io/istream.md) | <span class="rank rank-sometimes">たまに</span> | すべての入力ストリームの共通の親クラス。関数の引数にすると、キーボードにもファイルにも対応できる。 |
    | [assert](io/assert.md) | <span class="rank rank-sometimes">たまに</span> | デバッグ中だけ「ここは必ず真」と確かめる。偽ならプログラムを止める。 |
    | [`std::fstream`](io/fstream.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じファイルを、読んだり書いたりできる型。 |
    | [`std::regex`](io/regex.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現による文字列の検索・置換。便利だが遅い。 |
    | [`std::cin`](io/cin.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準入力。キーボードなどから値を読む（>> で読む）。 |
    | [`std::cerr`](io/cerr.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準エラー出力。エラーやログを出す（バッファなしで即座に出る）。 |
    | [`std::endl`](io/endl.md) | <span class="rank rank-rare">知ってるだけ</span> | 改行を出して、バッファを書き出す（flush する）。 |
    | [`std::flush`](io/flush.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力のバッファにたまった中身を、すぐ書き出す。 |
    | [`std::setw`](io/setw.md) | <span class="rank rank-rare">知ってるだけ</span> | 次に出す値の「幅」を決める（右寄せでそろえる）。 |
    | [`std::setprecision`](io/setprecision.md) | <span class="rank rank-rare">知ってるだけ</span> | 小数の桁数を決める。 |
    | [`std::setfill`](io/setfill.md) | <span class="rank rank-rare">知ってるだけ</span> | 幅を埋める文字を決める。 |
    | [`std::hex`](io/hex.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数を 16 進数で出力・入力するように切り替える（dec / oct も同じ仲間）。 |
    | [`std::fixed`](io/fixed.md) | <span class="rank rank-rare">知ってるだけ</span> | 小数を「固定小数点の形」（小数点以下の桁数を指定）で出力する。 |
    | [`std::boolalpha`](io/boolalpha.md) | <span class="rank rank-rare">知ってるだけ</span> | bool を `1` / `0` ではなく `true` / `false` で出力する。 |
    | [`std::regex_search`](io/regex_search.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列のどこかに、パターンに合う部分があるか探す。 |
    | [`std::regex_match`](io/regex_match.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の全体が、パターンに一致するか調べる。 |
    | [`std::regex_replace`](io/regex_replace.md) | <span class="rank rank-rare">知ってるだけ</span> | パターンに合う部分を、別の文字列に置き換える。 |
    | [`std::smatch`](io/smatch.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現で見つかった部分と、グループを持つ結果。 |
    | [`std::sregex_iterator`](io/sregex_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | パターンに合う部分を、全部順に回す。 |
    | [`std::streambuf`](io/streambuf.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームの裏側にある、バッファと入出力先を扱う土台のクラス。 |
    | [`std::osyncstream`](io/osyncstream.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数のスレッドが同時に出力しても、行が混ざらないようにする出力ストリーム。 <span class="ver ver-20">C++20</span> |
    | [`std::spanstream`](io/spanstream.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリ上の既存のバッファを、コピーせずにストリームとして読み書きする。 <span class="ver ver-23">C++23</span> |
    | [`std::locale`](io/locale.md) | <span class="rank rank-rare">知ってるだけ</span> | 言語・地域ごとの書式（小数点、通貨、日付）の設定。 |
    | [errno](io/cerrno.md) | <span class="rank rank-rare">知ってるだけ</span> | C 由来の関数が失敗した理由を入れる、グローバルなエラー番号。 |
    | [`std::signal`](io/csignal.md) | <span class="rank rank-rare">知ってるだけ</span> | Ctrl+C やクラッシュ（シグナル）を受け取る関数を登録する。 |
    | [va_list](io/cstdarg.md) | <span class="rank rank-rare">知ってるだけ</span> | 引数の数が決まっていない関数（C 風の可変長引数）を書く。 |
    | [setjmp / longjmp](io/csetjmp.md) | <span class="rank rank-rare">知ってるだけ</span> | 離れた場所へ一気に戻る（C 由来・C++ では危険）。 |

    **C の入出力（<cstdio>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::printf`](io/cstdio/printf.md) | <span class="rank rank-sometimes">たまに</span> | 書式に従って画面に出す（C 由来・型の安全がない）。 |
    | [`std::fopen`](io/cstdio/fopen.md) | <span class="rank rank-rare">知ってるだけ</span> | C 由来のファイルを開く関数。 |
    | [`std::fread`](io/cstdio/fread.md) | <span class="rank rank-rare">知ってるだけ</span> | C 由来のバイナリ読み込み。 |
    | [`std::fwrite`](io/cstdio/fwrite.md) | <span class="rank rank-rare">知ってるだけ</span> | C 由来のバイナリ書き込み。 |
    | [`std::fgets`](io/cstdio/fgets.md) | <span class="rank rank-rare">知ってるだけ</span> | C 由来の 1 行読み込み。 |

    **ファイル操作（std::filesystem）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::filesystem::path`](io/filesystem/path.md) | <span class="rank rank-must">必須</span> | ファイルやフォルダの場所（パス）を表す型。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::exists`](io/filesystem/exists.md) | <span class="rank rank-must">必須</span> | ファイルやフォルダがあるか調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::create_directories`](io/filesystem/create_directories.md) | <span class="rank rank-must">必須</span> | 途中のフォルダも含めて、フォルダを作る。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::directory_iterator`](io/filesystem/directory_iterator.md) | <span class="rank rank-often">よく使う</span> | フォルダの中身（直下のファイル）を順に回す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::recursive_directory_iterator`](io/filesystem/recursive_directory_iterator.md) | <span class="rank rank-often">よく使う</span> | フォルダの中身を、サブフォルダの中まで全部回す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::directory_entry`](io/filesystem/directory_entry.md) | <span class="rank rank-often">よく使う</span> | フォルダを回して得られる、1 つの項目（パスと情報）。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::create_directory`](io/filesystem/create_directory.md) | <span class="rank rank-sometimes">たまに</span> | フォルダを 1 階層だけ作る。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::remove`](io/filesystem/remove.md) | <span class="rank rank-sometimes">たまに</span> | ファイルか空のフォルダを 1 つ消す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::remove_all`](io/filesystem/remove_all.md) | <span class="rank rank-sometimes">たまに</span> | フォルダを中身ごと、まとめて消す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::rename`](io/filesystem/rename.md) | <span class="rank rank-sometimes">たまに</span> | ファイルやフォルダの名前を変える（移動もできる）。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_regular_file`](io/filesystem/is_regular_file.md) | <span class="rank rank-sometimes">たまに</span> | 普通のファイルか調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_directory`](io/filesystem/is_directory.md) | <span class="rank rank-sometimes">たまに</span> | フォルダか調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::file_size`](io/filesystem/file_size.md) | <span class="rank rank-sometimes">たまに</span> | ファイルの大きさ（バイト数）を取得する。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::copy_file`](io/filesystem/copy_file.md) | <span class="rank rank-sometimes">たまに</span> | ファイルを 1 つコピーする。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::copy`](io/filesystem/copy.md) | <span class="rank rank-sometimes">たまに</span> | ファイルやフォルダを（中身ごと）コピーする。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::current_path`](io/filesystem/current_path.md) | <span class="rank rank-sometimes">たまに</span> | 今の作業フォルダを取得・変更する。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::last_write_time`](io/filesystem/last_write_time.md) | <span class="rank rank-sometimes">たまに</span> | ファイルの最終更新日時を取得する。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::absolute`](io/filesystem/absolute.md) | <span class="rank rank-sometimes">たまに</span> | 相対パスを絶対パスにする。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::filesystem_error`](io/filesystem/filesystem_error.md) | <span class="rank rank-sometimes">たまに</span> | filesystem の関数が投げる例外。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::relative`](io/filesystem/relative.md) | <span class="rank rank-rare">知ってるだけ</span> | 基準のフォルダからの、相対パスにする。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::temp_directory_path`](io/filesystem/temp_directory_path.md) | <span class="rank rank-rare">知ってるだけ</span> | 一時ファイル用のフォルダの場所を返す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::canonical`](io/filesystem/canonical.md) | <span class="rank rank-rare">知ってるだけ</span> | パスを正規化する（`..` やリンクを解決する）。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::equivalent`](io/filesystem/equivalent.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのパスが同じファイルを指すか調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::space`](io/filesystem/space.md) | <span class="rank rank-rare">知ってるだけ</span> | ディスクの空き容量を取得する。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::resize_file`](io/filesystem/resize_file.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの大きさを変える（切り詰め・拡張）。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::status`](io/filesystem/status.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの種類と権限を取得する（file_status）。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::permissions`](io/filesystem/permissions.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの権限（読み書きの許可）を取得・変更する。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_empty`](io/filesystem/is_empty.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルが空（サイズ 0）か、フォルダが空かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::weakly_canonical`](io/filesystem/weakly_canonical.md) | <span class="rank rank-rare">知ってるだけ</span> | 存在しない部分を含むパスも正規化する（canonical の緩い版）。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::create_symlink`](io/filesystem/create_symlink.md) | <span class="rank rank-rare">知ってるだけ</span> | シンボリックリンク（別の場所を指す印）を作る。 <span class="ver ver-17">C++17</span> |

    **時刻（<ctime>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::time`](io/ctime/time.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在時刻を、1970 年からの秒数で取得する（C 由来）。 |
    | [`std::clock`](io/ctime/clock.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラムが使った CPU 時間を取得する（C 由来）。 |
    | [`std::strftime`](io/ctime/strftime.md) | <span class="rank rank-rare">知ってるだけ</span> | 日時を、書式に従った文字列にする（C 由来）。 |
    | [`std::gmtime`](io/ctime/gmtime.md) | <span class="rank rank-rare">知ってるだけ</span> | 秒数を、UTC の年月日時分秒に分解する（C 由来）。 |

??? abstract "数値（90）: 数学関数、定数、整数型、ビット操作"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [<cmath>（数学関数）](numeric/cmath.md) | <span class="rank rank-must">必須</span> | `sqrt`、`sin` / `cos`、`atan2`、`lerp` など数学の関数。 |
    | [<cstdint>（大きさの決まった整数型）](numeric/cstdint.md) | <span class="rank rank-often">よく使う</span> | `std::int32_t` など大きさが決まった整数の型。 |
    | [`std::numeric_limits`](numeric/limits.md) | <span class="rank rank-often">よく使う</span> | 型の最大値・最小値・誤差の大きさを、調べる。 |
    | [<numbers>（数学定数）](numeric/numbers.md) | <span class="rank rank-often">よく使う</span> | π などの数学の定数。 <span class="ver ver-20">C++20</span> |
    | [<numeric>（gcd / lcm / midpoint など）](numeric/numeric.md) | <span class="rank rank-sometimes">たまに</span> | 最大公約数（`gcd`）、最小公倍数、中間値、累積和など。 <span class="ver ver-17">C++17</span> |
    | [<bit>（ビット操作）](numeric/bit.md) | <span class="rank rank-sometimes">たまに</span> | ビットを数える（`popcount`）・型を読み替える（`bit_cast`）など、ビット操作。 <span class="ver ver-20">C++20</span> |
    | [<climits>（整数の限界マクロ）](numeric/climits.md) | <span class="rank rank-rare">知ってるだけ</span> | `INT_MAX` など、整数型の最大値・最小値を表す C 由来のマクロ。 |
    | [<cfloat>（小数の限界マクロ）](numeric/cfloat.md) | <span class="rank rank-rare">知ってるだけ</span> | `FLT_EPSILON` など、小数型の精度・範囲を表す C 由来のマクロ。 |
    | [<stdfloat>（float16_t・bfloat16_t など）](numeric/stdfloat.md) | <span class="rank rank-rare">知ってるだけ</span> | 大きさが決まった浮動小数点型（16・32・64・128 ビット）。 <span class="ver ver-23">C++23</span> |
    | [`std::complex`](numeric/complex.md) | <span class="rank rank-rare">知ってるだけ</span> | 複素数（実部 + 虚部）。回転・波・フーリエ変換に。 |
    | [`std::ratio`](numeric/ratio.md) | <span class="rank rank-rare">知ってるだけ</span> | 分数（1/3 など）を、型としてコンパイル時に表す。chrono の単位の土台。 |
    | [`std::fesetround`](numeric/fesetround.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点の丸め方（最近接・切り上げ・切り捨てなど）を切り替える。 |

    **<cctype> の文字判定**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::isalpha`](numeric/cctype/isalpha.md) | <span class="rank rank-rare">知ってるだけ</span> | 英字（A-Z, a-z）かを調べる。 |
    | [`std::isdigit`](numeric/cctype/isdigit.md) | <span class="rank rank-rare">知ってるだけ</span> | 数字（0-9）かを調べる。 |
    | [`std::isspace`](numeric/cctype/isspace.md) | <span class="rank rank-rare">知ってるだけ</span> | 空白文字（スペース・タブ・改行）かを調べる。 |
    | [`std::toupper`](numeric/cctype/toupper.md) | <span class="rank rank-rare">知ってるだけ</span> | 英字を大文字にする。 |
    | [`std::tolower`](numeric/cctype/tolower.md) | <span class="rank rank-rare">知ってるだけ</span> | 英字を小文字にする。 |

    **<cstdlib> の関数**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::div`](numeric/cstdlib/div.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数の割り算で、商と余りを同時に求める。 |
    | [`std::atoi`](numeric/cstdlib/atoi.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を整数に変換する（失敗を検出できない古い関数）。 |
    | [`std::strtol`](numeric/cstdlib/strtol.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を整数に変換する（進数の指定・終了位置・エラーの検出ができる）。 |
    | [`std::rand`](numeric/cstdlib/rand.md) | <span class="rank rank-rare">知ってるだけ</span> | 乱数を作る古い関数（品質が低いので使わない）。 |
    | [`std::exit`](numeric/cstdlib/exit.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラムを終了する（後片付けをしてから）。 |
    | [`std::abort`](numeric/cstdlib/abort.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラムを異常終了する（後片付けなし）。 |
    | [`std::getenv`](numeric/cstdlib/getenv.md) | <span class="rank rank-rare">知ってるだけ</span> | 環境変数の値を取得する。 |
    | [`std::qsort`](numeric/cstdlib/qsort.md) | <span class="rank rank-rare">知ってるだけ</span> | C 由来の並べ替え（比較関数を渡す）。 |
    | [`std::bsearch`](numeric/cstdlib/bsearch.md) | <span class="rank rank-rare">知ってるだけ</span> | C 由来の二分探索（整列済みの配列から探す）。 |

    **<numeric> の整数・補間関数**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::gcd`](numeric/gcd.md) | <span class="rank rank-sometimes">たまに</span> | 最大公約数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::lcm`](numeric/lcm.md) | <span class="rank rank-rare">知ってるだけ</span> | 最小公倍数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::midpoint`](numeric/midpoint.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの値の中間を、桁あふれなしで求める。 <span class="ver ver-20">C++20</span> |

    **ビット操作（<bit>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::popcount`](numeric/bit/popcount.md) | <span class="rank rank-sometimes">たまに</span> | 立っているビット（1）の数を数える。 <span class="ver ver-20">C++20</span> |
    | [`std::has_single_bit`](numeric/bit/has_single_bit.md) | <span class="rank rank-sometimes">たまに</span> | ビットが 1 つだけ立っているか（2 のべき乗か）を調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::bit_ceil`](numeric/bit/bit_ceil.md) | <span class="rank rank-sometimes">たまに</span> | 自分以上で最小の、2 のべき乗に切り上げる。 <span class="ver ver-20">C++20</span> |
    | [`std::bit_width`](numeric/bit/bit_width.md) | <span class="rank rank-sometimes">たまに</span> | 値を表すのに必要なビット数を返す。 <span class="ver ver-20">C++20</span> |
    | [`std::bit_cast`](numeric/bit/bit_cast.md) | <span class="rank rank-sometimes">たまに</span> | 値のビット列を保ったまま、別の型として読み替える。 <span class="ver ver-20">C++20</span> |
    | [`std::countr_zero`](numeric/bit/countr_zero.md) | <span class="rank rank-sometimes">たまに</span> | 下位（右）から数えて、連続する 0 のビット数を数える。 <span class="ver ver-20">C++20</span> |
    | [`std::bit_floor`](numeric/bit/bit_floor.md) | <span class="rank rank-rare">知ってるだけ</span> | 自分以下で最大の、2 のべき乗に切り捨てる。 <span class="ver ver-20">C++20</span> |
    | [`std::countl_zero`](numeric/bit/countl_zero.md) | <span class="rank rank-rare">知ってるだけ</span> | 上位（左）から数えて、連続する 0 のビット数を数える。 <span class="ver ver-20">C++20</span> |
    | [`std::countl_one`](numeric/bit/countl_one.md) | <span class="rank rank-rare">知ってるだけ</span> | 上位（左）から数えて、連続する 1 のビット数を数える。 <span class="ver ver-20">C++20</span> |
    | [`std::countr_one`](numeric/bit/countr_one.md) | <span class="rank rank-rare">知ってるだけ</span> | 下位（右）から数えて、連続する 1 のビット数を数える。 <span class="ver ver-20">C++20</span> |
    | [`std::rotl`](numeric/bit/rotl.md) | <span class="rank rank-rare">知ってるだけ</span> | ビットを左に回転させる（はみ出したビットが反対側に戻る）。 <span class="ver ver-20">C++20</span> |
    | [`std::rotr`](numeric/bit/rotr.md) | <span class="rank rank-rare">知ってるだけ</span> | ビットを右に回転させる（はみ出したビットが反対側に戻る）。 <span class="ver ver-20">C++20</span> |
    | [`std::byteswap`](numeric/bit/byteswap.md) | <span class="rank rank-rare">知ってるだけ</span> | バイトの並び順を反転する（リトルエンディアン ⇄ ビッグエンディアン）。 <span class="ver ver-23">C++23</span> |
    | [`std::endian`](numeric/bit/endian.md) | <span class="rank rank-rare">知ってるだけ</span> | 環境のバイト順序（エンディアン）を調べる。 <span class="ver ver-20">C++20</span> |

    **数学関数（<cmath>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::sqrt`](numeric/cmath/sqrt.md) | <span class="rank rank-must">必須</span> | 平方根（ルート）を求める。 |
    | [`std::abs`](numeric/cmath/abs.md) | <span class="rank rank-must">必須</span> | 絶対値を求める（整数・小数に対応）。 |
    | [`std::sin`](numeric/cmath/sin.md) | <span class="rank rank-must">必須</span> | サイン（正弦）を求める。引数はラジアン。 |
    | [`std::cos`](numeric/cmath/cos.md) | <span class="rank rank-must">必須</span> | コサイン（余弦）を求める。引数はラジアン。 |
    | [`std::atan2`](numeric/cmath/atan2.md) | <span class="rank rank-must">必須</span> | x と y から、向きの角度（ラジアン）を求める。 |
    | [`std::floor`](numeric/cmath/floor.md) | <span class="rank rank-must">必須</span> | 小数を切り捨てる（小さいほうの整数にする）。 |
    | [`std::lerp`](numeric/cmath/lerp.md) | <span class="rank rank-must">必須</span> | 2 つの値の間を、割合で補間する（線形補間）。 <span class="ver ver-20">C++20</span> |
    | [`std::tan`](numeric/cmath/tan.md) | <span class="rank rank-often">よく使う</span> | タンジェント（正接）を求める。引数はラジアン。 |
    | [`std::round`](numeric/cmath/round.md) | <span class="rank rank-often">よく使う</span> | 小数を四捨五入する（半分は 0 から遠いほうへ）。 |
    | [`std::ceil`](numeric/cmath/ceil.md) | <span class="rank rank-often">よく使う</span> | 小数を切り上げる（大きいほうの整数にする）。 |
    | [`std::pow`](numeric/cmath/pow.md) | <span class="rank rank-often">よく使う</span> | べき乗（x の y 乗）を求める。 |
    | [`std::asin`](numeric/cmath/asin.md) | <span class="rank rank-sometimes">たまに</span> | アークサイン（逆正弦）を求める。結果はラジアン。 |
    | [`std::acos`](numeric/cmath/acos.md) | <span class="rank rank-sometimes">たまに</span> | アークコサイン（逆余弦）を求める。結果はラジアン。 |
    | [`std::hypot`](numeric/cmath/hypot.md) | <span class="rank rank-sometimes">たまに</span> | √(x² + y²) を、桁あふれしにくく求める。 |
    | [`std::fmod`](numeric/cmath/fmod.md) | <span class="rank rank-sometimes">たまに</span> | 小数の割り算の余りを求める。 |
    | [`std::exp`](numeric/cmath/exp.md) | <span class="rank rank-sometimes">たまに</span> | e の x 乗（指数関数）を求める。 |
    | [`std::log`](numeric/cmath/log.md) | <span class="rank rank-sometimes">たまに</span> | 自然対数（底が e の対数）を求める。 |
    | [`std::isnan`](numeric/cmath/isnan.md) | <span class="rank rank-sometimes">たまに</span> | 値が NaN（数ではない）かを調べる。 |
    | [`std::atan`](numeric/cmath/atan.md) | <span class="rank rank-sometimes">たまに</span> | アークタンジェント（逆正接）。傾きから角度を求める。 |
    | [`std::isfinite`](numeric/cmath/isfinite.md) | <span class="rank rank-sometimes">たまに</span> | 値が有限の数（NaN でも無限大でもない）かを調べる。 |
    | [`std::tanh`](numeric/cmath/tanh.md) | <span class="rank rank-sometimes">たまに</span> | 双曲線正接（tanh）を求める。−1〜1 になだらかに収まる。 |
    | [`std::lround`](numeric/cmath/lround.md) | <span class="rank rank-sometimes">たまに</span> | 小数を四捨五入して、整数型（long）で返す。 |
    | [`std::trunc`](numeric/cmath/trunc.md) | <span class="rank rank-rare">知ってるだけ</span> | 小数部を捨てる（0 に向かって切り捨てる）。 |
    | [`std::log2`](numeric/cmath/log2.md) | <span class="rank rank-rare">知ってるだけ</span> | 底が 2 の対数を求める。 |
    | [`std::log10`](numeric/cmath/log10.md) | <span class="rank rank-rare">知ってるだけ</span> | 底が 10 の対数を求める。 |
    | [`std::cbrt`](numeric/cmath/cbrt.md) | <span class="rank rank-rare">知ってるだけ</span> | 立方根（3 乗根）を求める。 |
    | [`std::fma`](numeric/cmath/fma.md) | <span class="rank rank-rare">知ってるだけ</span> | `x * y + z` を、丸めを 1 回だけで計算する。 |
    | [`std::isinf`](numeric/cmath/isinf.md) | <span class="rank rank-rare">知ってるだけ</span> | 値が無限大かを調べる。 |
    | [`std::copysign`](numeric/cmath/copysign.md) | <span class="rank rank-rare">知ってるだけ</span> | 大きさは x、符号は y の値を作る。 |
    | [`std::signbit`](numeric/cmath/signbit.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号ビットが立っているか（負か）を調べる。 |
    | [`std::remainder`](numeric/cmath/remainder.md) | <span class="rank rank-rare">知ってるだけ</span> | 小数の余り。商を四捨五入で決めるので、負になることがある。 |
    | [`std::sinh`](numeric/cmath/sinh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線正弦（sinh）を求める。 |
    | [`std::cosh`](numeric/cmath/cosh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線余弦（cosh）を求める。 |
    | [`std::exp2`](numeric/cmath/exp2.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 の x 乗を求める。 |
    | [`std::expm1`](numeric/cmath/expm1.md) | <span class="rank rank-rare">知ってるだけ</span> | e^x − 1 を、x が 0 に近くても精度よく求める。 |
    | [`std::log1p`](numeric/cmath/log1p.md) | <span class="rank rank-rare">知ってるだけ</span> | log(1 + x) を、x が 0 に近くても精度よく求める。 |
    | [`std::fmax`](numeric/cmath/fmax.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの小数の大きいほうを返す（NaN は無視する）。 |
    | [`std::fmin`](numeric/cmath/fmin.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの小数の小さいほうを返す（NaN は無視する）。 |
    | [`std::nearbyint`](numeric/cmath/nearbyint.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の丸めモード（既定は偶数丸め）で整数値にする。 |
    | [`std::modf`](numeric/cmath/modf.md) | <span class="rank rank-rare">知ってるだけ</span> | 小数を、整数部と小数部に分ける。 |
    | [`std::ldexp`](numeric/cmath/ldexp.md) | <span class="rank rank-rare">知ってるだけ</span> | x × 2^n を求める（2 のべき乗倍）。 |
    | [`std::frexp`](numeric/cmath/frexp.md) | <span class="rank rank-rare">知ってるだけ</span> | 小数を、仮数（0.5〜1）と 2 の指数に分ける。 |

    **飽和演算（<numeric>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::add_sat`](numeric/add_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 足し算。範囲を超えたら最大・最小値に張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::sub_sat`](numeric/sub_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 引き算。範囲を超えたら最大・最小値に張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::mul_sat`](numeric/mul_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 掛け算。範囲を超えたら最大・最小値に張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::div_sat`](numeric/div_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 割り算。範囲を超える唯一の場合（最小値 ÷ −1）で張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::saturate_cast`](numeric/saturate_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数を別の整数型に変換する。範囲を超えたら張り付く。 <span class="ver ver-26">C++26</span> |

??? abstract "並行処理（34）: スレッドとデータの守り方"
    | 名前 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::jthread`](concurrency/jthread.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | スコープを抜けると自動で join する、止める合図つきのスレッド。 <span class="ver ver-20">C++20</span> |
    | [`std::stop_token`](concurrency/stop_token.md) | <span class="rank rank-sometimes">たまに</span> | — | 「止まって」の合図を受け取る側。 <span class="ver ver-20">C++20</span> |
    | [`std::thread`](concurrency/thread.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 別のスレッドで、処理を動かす。 |
    | [`std::mutex`](concurrency/mutex.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 共有のデータを同時に触れないよう、鍵で守る。 |
    | [`std::atomic`](concurrency/atomic.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-3">○</span> | 複数スレッドから、安全に読み書きできる数値・フラグ。 |
    | [`std::lock_guard`](concurrency/lock_guard.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | スコープの間だけ鍵をかけ、抜けるときに自動で開ける。 |
    | [`std::scoped_lock`](concurrency/scoped_lock.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 複数の mutex を、デッドロックしないようにまとめてかける。 <span class="ver ver-17">C++17</span> |
    | [`std::unique_lock`](concurrency/unique_lock.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 途中で開け閉めできる鍵。条件変数と一緒に使う。 |
    | [`std::async`](concurrency/async.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 関数を別スレッドで実行して、結果を future で受け取る。 |
    | [`std::future`](concurrency/future.md) | <span class="rank rank-sometimes">たまに</span> | <span class="perf perf-2">△</span> | 別のスレッドの結果を、あとで受け取る。 |
    | [`std::atomic_flag`](concurrency/atomic_flag.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 一番単純なアトミックなフラグ（立っているか、いないか）。 |
    | [`std::atomic_ref`](concurrency/atomic_ref.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 普通の変数を、一時的にアトミックに操作する。 <span class="ver ver-20">C++20</span> |
    | [`std::memory_order`](concurrency/memory_order.md) | <span class="rank rank-rare">知ってるだけ</span> | — | アトミック操作の、メモリの見え方の順序を決める指定。 |
    | [`std::stop_source`](concurrency/stop_source.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「止まって」の合図を出す側。 <span class="ver ver-20">C++20</span> |
    | [`std::stop_callback`](concurrency/stop_callback.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「止まって」の合図が来たときに、実行する処理を登録する。 <span class="ver ver-20">C++20</span> |
    | [`std::condition_variable`](concurrency/condition_variable.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 条件が満たされるまで、スレッドを眠らせて待たせる。 |
    | [`std::shared_mutex`](concurrency/shared_mutex.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 読む人は何人でも同時に、書く人は 1 人だけ、という鍵。 <span class="ver ver-17">C++17</span> |
    | [`std::shared_lock`](concurrency/shared_lock.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | `shared_mutex` を「読む側」としてロックする鍵。 |
    | [`std::recursive_mutex`](concurrency/recursive_mutex.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 同じスレッドなら何度でもロックできる鍵。 |
    | [`std::call_once`](concurrency/call_once.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 何回呼ばれても、初期化を 1 回だけ実行する。 |
    | [`std::timed_mutex`](concurrency/timed_mutex.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 時間を決めて待てる鍵。取れなければ諦められる。 |
    | [`std::lock`](concurrency/lock.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 複数の mutex を、デッドロックしないように同時にかける関数。 |
    | [`std::promise`](concurrency/promise.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 結果を、別のスレッドへ渡すための「約束」。書き込む側を自分で持つ。 |
    | [`std::shared_future`](concurrency/shared_future.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 複数の場所から、同じ結果を受け取れる future。 |
    | [`std::packaged_task`](concurrency/packaged_task.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-2">△</span> | 関数と future をセットにしたもの。自前のスレッドプールに便利。 |
    | [`std::latch`](concurrency/latch.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | カウンタが 0 になるまで待つ、1 回きりの待ち合わせ。 <span class="ver ver-20">C++20</span> |
    | [`std::counting_semaphore`](concurrency/counting_semaphore.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 同時に入れる数を制限する入場券。 <span class="ver ver-20">C++20</span> |
    | [`std::binary_semaphore`](concurrency/binary_semaphore.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 最大 1 のセマフォ。「合図」に使う。 <span class="ver ver-20">C++20</span> |
    | [`std::barrier`](concurrency/barrier.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | 全員がそろうのを待つ。何度でも繰り返し使える。 <span class="ver ver-20">C++20</span> |
    | [`std::condition_variable_any`](concurrency/condition_variable_any.md) | <span class="rank rank-rare">知ってるだけ</span> | <span class="perf perf-3">○</span> | どんな種類の鍵とも組み合わせられる条件変数。 |

    **this_thread**

    | 名前 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::this_thread::sleep_for`](concurrency/this_thread/sleep_for.md) | <span class="rank rank-sometimes">たまに</span> | — | 今のスレッドを、指定した時間だけ止める。 |
    | [`std::this_thread::sleep_until`](concurrency/this_thread/sleep_until.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 今のスレッドを、指定した時刻まで止める。 |
    | [`std::this_thread::yield`](concurrency/this_thread/yield.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 他のスレッドに、実行の順番を譲る。 |
    | [`std::this_thread::get_id`](concurrency/this_thread/get_id.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 今のスレッドの ID を取得する。 |

??? abstract "型・言語サポート（119）: イテレータの道具、関数オブジェクト、型の性質、例外"
    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::source_location`](support/source_location.md) | <span class="rank rank-sometimes">たまに</span> | 今の場所（ファイル・行・関数）を取得する。 <span class="ver ver-20">C++20</span> |
    | [`std::stacktrace`](support/stacktrace.md) | <span class="rank rank-sometimes">たまに</span> | 呼び出し履歴（スタックトレース）を取得する。 <span class="ver ver-23">C++23</span> |
    | [<iterator>（next / distance / back_inserter など）](support/iterator.md) | <span class="rank rank-sometimes">たまに</span> | イテレータを進める・距離を測る・挿入するなどの道具（`next`、`distance`、`back_inserter`）。 |
    | [<functional>（関数オブジェクト・invoke・hash など）](support/functional.md) | <span class="rank rank-sometimes">たまに</span> | 比較（`greater`）・参照渡し（`ref`）・引数の固定（`bind_front`）などの、関数の道具。 |
    | [<type_traits>（型の性質を調べる）](support/type_traits.md) | <span class="rank rank-sometimes">たまに</span> | 型の性質（整数かポインタかなど）を、コンパイル時に調べる。 |
    | [小さな便利機能（to_underlying / byte / cmp_less など）](support/utility-misc.md) | <span class="rank rank-sometimes">たまに</span> | `to_underlying`、`cmp_less`、`byte` など細かい便利道具。 <span class="ver ver-17">C++17</span> |
    | [標準の例外（<stdexcept>）](support/exceptions.md) | <span class="rank rank-sometimes">たまに</span> | 標準の例外の種類（`runtime_error`、`out_of_range` など）と使い分け。 |
    | [<version>（機能テストマクロ）](support/version.md) | <span class="rank rank-rare">知ってるだけ</span> | 「この標準ライブラリの機能が使えるか」を、`#if` で調べるためのマクロ。 <span class="ver ver-20">C++20</span> |
    | [std::generator（コルーチン）](support/generator.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンで、値を 1 つずつ作って返す（C++23）。 <span class="ver ver-23">C++23</span> |

    **ranges の基本部品**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::ranges::range`](support/ranges/range.md) | <span class="rank rank-sometimes">たまに</span> | 「範囲」であること（begin と end がある）を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::begin`](support/ranges/begin.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の先頭のイテレータを取る（配列・コンテナ・独自の範囲に対応）。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::size`](support/ranges/size.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素数を取る。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::dangling`](support/ranges/dangling.md) | <span class="rank rank-rare">知ってるだけ</span> | 「一時オブジェクトのイテレータは危険」と知らせるための印の型。 <span class="ver ver-20">C++20</span> |

    **イテレータの道具（<iterator>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::size`](support/iterator/size.md) | <span class="rank rank-often">よく使う</span> | コンテナや配列の要素数を返す（配列にも使える）。 |
    | [`std::back_inserter`](support/iterator/back_inserter.md) | <span class="rank rank-often">よく使う</span> | 代入するたびに、コンテナの末尾に push_back するイテレータ。 |
    | [`std::next`](support/iterator/next.md) | <span class="rank rank-sometimes">たまに</span> | イテレータを n 個進めた位置を返す（元は変えない）。 |
    | [`std::prev`](support/iterator/prev.md) | <span class="rank rank-sometimes">たまに</span> | イテレータを n 個戻した位置を返す（元は変えない）。 |
    | [`std::distance`](support/iterator/distance.md) | <span class="rank rank-sometimes">たまに</span> | 2 つのイテレータの間の要素数を返す。 |
    | [`std::inserter`](support/iterator/inserter.md) | <span class="rank rank-sometimes">たまに</span> | 代入するたびに、指定した位置にコンテナへ挿入するイテレータ。 |
    | [`std::advance`](support/iterator/advance.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータそのものを n 個進める（戻り値なし）。 |
    | [`std::ssize`](support/iterator/ssize.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素数を符号つきの整数で返す。 <span class="ver ver-20">C++20</span> |
    | [`std::empty`](support/iterator/empty.md) | <span class="rank rank-rare">知ってるだけ</span> | コンテナが空かを調べる（配列・initializer_list にも使える）。 |
    | [`std::data`](support/iterator/data.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭の要素へのポインターを返す（配列にも使える）。 |
    | [`std::begin`](support/iterator/begin.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭と終端のイテレータを返す（配列にも使える）。 |
    | [`std::front_inserter`](support/iterator/front_inserter.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、コンテナの先頭に push_front するイテレータ。 |
    | [`std::make_move_iterator`](support/iterator/move_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照外しするとムーブされるイテレータ。 |
    | [`std::reverse_iterator`](support/iterator/reverse_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 逆向きに進むイテレータ（rbegin / rend が返す型）。 |
    | [`std::istream_iterator`](support/iterator/istream_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力ストリームから、値を 1 つずつ読むイテレータ。 |
    | [`std::ostream_iterator`](support/iterator/ostream_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、出力ストリームへ値を書き出すイテレータ。 |

    **エラーコード（<system_error>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::error_code`](support/error_code.md) | <span class="rank rank-sometimes">たまに</span> | OS やライブラリのエラーを、値と分類で表す（例外を使わない失敗の通知）。 |
    | [`std::error_condition`](support/error_condition.md) | <span class="rank rank-rare">知ってるだけ</span> | 環境に依存しない「エラーの種類」を表す。error_code と比べる相手。 |
    | [`std::errc`](support/errc.md) | <span class="rank rank-rare">知ってるだけ</span> | 環境に依存しない、エラーの種類の名前（列挙型）。 |

    **コルーチン（<coroutine>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::coroutine_handle`](support/coroutine/coroutine_handle.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンの再開・破棄を操作する「取っ手」。 <span class="ver ver-20">C++20</span> |
    | [`std::suspend_always`](support/coroutine/suspend_always.md) | <span class="rank rank-rare">知ってるだけ</span> | 「必ず一時停止する」ことを表す待ち受け体。 <span class="ver ver-20">C++20</span> |
    | [`std::suspend_never`](support/coroutine/suspend_never.md) | <span class="rank rank-rare">知ってるだけ</span> | 「一時停止しない」ことを表す待ち受け体。 <span class="ver ver-20">C++20</span> |
    | [co_await](support/coroutine/co_await.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンを一時停止して、あとで結果を受け取って再開する演算子。 <span class="ver ver-20">C++20</span> |
    | [co_yield](support/coroutine/co_yield.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンから値を 1 つ返して一時停止し、次に呼ばれたら続きから再開する。 <span class="ver ver-20">C++20</span> |
    | [co_return](support/coroutine/co_return.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンを終了して、値を返す。 <span class="ver ver-20">C++20</span> |

    **コンセプト（<concepts>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::same_as`](support/concepts/same_as.md) | <span class="rank rank-often">よく使う</span> | 2 つの型が同じであることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::integral`](support/concepts/integral.md) | <span class="rank rank-often">よく使う</span> | 整数型であることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::floating_point`](support/concepts/floating_point.md) | <span class="rank rank-sometimes">たまに</span> | 小数型であることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::derived_from`](support/concepts/derived_from.md) | <span class="rank rank-sometimes">たまに</span> | 別のクラスの派生クラスであることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::invocable`](support/concepts/invocable.md) | <span class="rank rank-sometimes">たまに</span> | 指定した引数で呼び出せることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::convertible_to`](support/concepts/convertible_to.md) | <span class="rank rank-rare">知ってるだけ</span> | ある型から別の型へ変換できることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::predicate`](support/concepts/predicate.md) | <span class="rank rank-rare">知ってるだけ</span> | `bool` として使える結果を返す関数であることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::totally_ordered`](support/concepts/totally_ordered.md) | <span class="rank rank-rare">知ってるだけ</span> | `<`、`>`、`==` などで大小を比べられることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::copyable`](support/concepts/copyable.md) | <span class="rank rank-rare">知ってるだけ</span> | コピーできる型であることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::movable`](support/concepts/movable.md) | <span class="rank rank-rare">知ってるだけ</span> | ムーブできる型であることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::default_initializable`](support/concepts/default_initializable.md) | <span class="rank rank-rare">知ってるだけ</span> | 引数なしで作れる型であることを要求するコンセプト。 <span class="ver ver-20">C++20</span> |

    **型の性質（<type_traits>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::is_same`](support/type_traits/is_same.md) | <span class="rank rank-often">よく使う</span> | 2 つの型が同じかを、コンパイル時に調べる。 |
    | [`std::is_integral`](support/type_traits/is_integral.md) | <span class="rank rank-often">よく使う</span> | 整数型かを調べる。 |
    | [`std::is_floating_point`](support/type_traits/is_floating_point.md) | <span class="rank rank-often">よく使う</span> | 小数型（float・double・long double）かを調べる。 |
    | [`std::remove_cvref`](support/type_traits/remove_cvref.md) | <span class="rank rank-often">よく使う</span> | `const`・`volatile`・参照をすべて外した型にする。 <span class="ver ver-20">C++20</span> |
    | [`std::is_arithmetic`](support/type_traits/is_arithmetic.md) | <span class="rank rank-sometimes">たまに</span> | 算術型（整数または小数）かを調べる。 |
    | [`std::is_trivially_copyable`](support/type_traits/is_trivially_copyable.md) | <span class="rank rank-sometimes">たまに</span> | `memcpy` で安全にコピーできる型かを調べる。 |
    | [`std::is_base_of`](support/type_traits/is_base_of.md) | <span class="rank rank-sometimes">たまに</span> | ある型が、別の型の基底クラスかを調べる。 |
    | [`std::is_nothrow_move_constructible`](support/type_traits/is_nothrow_move_constructible.md) | <span class="rank rank-sometimes">たまに</span> | ムーブが例外を投げない型かを調べる。 |
    | [`std::underlying_type`](support/type_traits/underlying_type.md) | <span class="rank rank-sometimes">たまに</span> | 列挙型が内部で使っている整数型を調べる。 |
    | [`std::conditional`](support/type_traits/conditional.md) | <span class="rank rank-sometimes">たまに</span> | 条件によって、2 つの型のどちらかを選ぶ。 |
    | [`std::is_enum`](support/type_traits/is_enum.md) | <span class="rank rank-rare">知ってるだけ</span> | 列挙型（enum）かを調べる。 |
    | [`std::is_pointer`](support/type_traits/is_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインター型かを調べる。 |
    | [`std::is_const`](support/type_traits/is_const.md) | <span class="rank rank-rare">知ってるだけ</span> | `const` が付いた型かを調べる。 |
    | [`std::is_default_constructible`](support/type_traits/is_default_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 引数なしで作れる型かを調べる。 |
    | [`std::is_copy_constructible`](support/type_traits/is_copy_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | コピーして作れる型かを調べる。 |
    | [`std::is_aggregate`](support/type_traits/is_aggregate.md) | <span class="rank rank-rare">知ってるだけ</span> | 集成体（波かっこでメンバを順に初期化できる型）かを調べる。 |
    | [`std::decay`](support/type_traits/decay.md) | <span class="rank rank-rare">知ってるだけ</span> | 関数に値渡しされたときの型（参照・const を外し、配列・関数はポインターに）にする。 |
    | [`std::common_type`](support/type_traits/common_type.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の型に共通する型（どちらにも変換できる型）を調べる。 |
    | [`std::make_unsigned`](support/type_traits/make_unsigned.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号つき整数の型を、符号なしの同じ大きさの型にする。 |
    | [`std::invoke_result`](support/type_traits/invoke_result.md) | <span class="rank rank-rare">知ってるだけ</span> | 関数を呼んだときの、戻り値の型を調べる。 |

    **基本の型（<cstddef>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::size_t`](support/size_t.md) | <span class="rank rank-sometimes">たまに</span> | 大きさや個数を表す、符号なしの整数型。 |
    | [`std::nullptr_t`](support/nullptr_t.md) | <span class="rank rank-rare">知ってるだけ</span> | `nullptr` の型。 |
    | [`std::ptrdiff_t`](support/ptrdiff_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのポインターの差を表す、符号つきの整数型。 |
    | [`std::max_align_t`](support/max_align_t.md) | <span class="rank rank-rare">知ってるだけ</span> | その環境で、最も厳しい（最大の）アラインメントを持つ型。 |
    | [offsetof](support/offsetof.md) | <span class="rank rank-rare">知ってるだけ</span> | 構造体のメンバが、先頭から何バイト目にあるかを求める。 |

    **実行時の型情報（<typeinfo>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [typeid](support/typeid.md) | <span class="rank rank-rare">知ってるだけ</span> | 式や型の「実際の型」を、実行時に調べる演算子。 |
    | [`std::type_info`](support/type_info.md) | <span class="rank rank-rare">知ってるだけ</span> | 型の情報（名前・同じ型かの比較）を持つクラス。 |
    | [`std::type_index`](support/type_index.md) | <span class="rank rank-rare">知ってるだけ</span> | `type_info` を、コンテナのキーにできるようにした包み。 |

    **小さな便利機能（<utility>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::to_underlying`](support/to_underlying.md) | <span class="rank rank-often">よく使う</span> | 列挙型の値を、元の整数型に変換する。 <span class="ver ver-23">C++23</span> |
    | [`std::cmp_less`](support/cmp_less.md) | <span class="rank rank-sometimes">たまに</span> | 符号の違う整数どうしを、正しく比べる（小さいか）。 <span class="ver ver-20">C++20</span> |
    | [`std::in_range`](support/in_range.md) | <span class="rank rank-sometimes">たまに</span> | 整数の値が、ある整数型の範囲に収まるかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::byte`](support/byte.md) | <span class="rank rank-sometimes">たまに</span> | バイト（8 ビット）を表す型。整数としては扱えない。 <span class="ver ver-17">C++17</span> |
    | [`std::cmp_equal`](support/cmp_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号の違う整数どうしを、正しく比べる（等しいか）。 <span class="ver ver-20">C++20</span> |
    | [`std::to_integer`](support/to_integer.md) | <span class="rank rank-rare">知ってるだけ</span> | `std::byte` を整数に変換する。 <span class="ver ver-17">C++17</span> |
    | [`std::unreachable`](support/unreachable.md) | <span class="rank rank-rare">知ってるだけ</span> | 「ここには絶対に来ない」とコンパイラに伝える。 <span class="ver ver-23">C++23</span> |
    | [`std::as_const`](support/as_const.md) | <span class="rank rank-rare">知ってるだけ</span> | 値を const 参照として扱う。 <span class="ver ver-17">C++17</span> |

    **標準の例外**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::runtime_error`](support/exceptions/runtime_error.md) | <span class="rank rank-often">よく使う</span> | 実行してみないと分からないエラー（ファイルが無い、通信失敗など）を表す例外。 |
    | [`std::out_of_range`](support/exceptions/out_of_range.md) | <span class="rank rank-often">よく使う</span> | 範囲外の添字・キーにアクセスしたときの例外。 |
    | [`std::exception`](support/exceptions/exception.md) | <span class="rank rank-sometimes">たまに</span> | すべての標準例外の基底クラス。what() でメッセージを取れる。 |
    | [`std::invalid_argument`](support/exceptions/invalid_argument.md) | <span class="rank rank-sometimes">たまに</span> | 引数の値が不正なときの例外。 |
    | [`std::bad_alloc`](support/exceptions/bad_alloc.md) | <span class="rank rank-sometimes">たまに</span> | メモリ確保に失敗したときの例外。 |
    | [`std::bad_optional_access`](support/exceptions/bad_optional_access.md) | <span class="rank rank-sometimes">たまに</span> | 空の optional から `value()` で取り出したときの例外。 <span class="ver ver-17">C++17</span> |
    | [`std::bad_variant_access`](support/exceptions/bad_variant_access.md) | <span class="rank rank-sometimes">たまに</span> | variant が持っていない型を `get` で取り出したときの例外。 <span class="ver ver-17">C++17</span> |
    | [`std::bad_function_call`](support/exceptions/bad_function_call.md) | <span class="rank rank-sometimes">たまに</span> | 空の std::function を呼んだときの例外。 |
    | [`std::logic_error`](support/exceptions/logic_error.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラムの論理の間違い（呼び出し側のミス）を表す例外。 |
    | [`std::system_error`](support/exceptions/system_error.md) | <span class="rank rank-rare">知ってるだけ</span> | OS のエラー（error_code つき）を表す例外。 |
    | [`std::exception_ptr`](support/exceptions/exception_ptr.md) | <span class="rank rank-rare">知ってるだけ</span> | 例外を保存して、別の場所・スレッドで投げ直す。 |
    | [`std::length_error`](support/exceptions/length_error.md) | <span class="rank rank-rare">知ってるだけ</span> | 許される最大の長さを超えたときの例外。 |
    | [`std::overflow_error`](support/exceptions/overflow_error.md) | <span class="rank rank-rare">知ってるだけ</span> | 計算結果が大きすぎて、表せないことを表す例外。 |
    | [`std::bad_cast`](support/exceptions/bad_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照の `dynamic_cast` が失敗したときの例外。 |
    | [`std::format_error`](support/exceptions/format_error.md) | <span class="rank rank-rare">知ってるだけ</span> | `std::format` の書式が不正なときの例外。 <span class="ver ver-20">C++20</span> |
    | [`std::terminate`](support/exceptions/terminate.md) | <span class="rank rank-rare">知ってるだけ</span> | 処理されなかった例外などで呼ばれる、プログラムの強制終了。 |

    **比較（<compare>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [operator<=>（三方比較）](support/spaceship.md) | <span class="rank rank-often">よく使う</span> | 「小さい・等しい・大きい」を 1 回で調べる比較演算子。= default で全部の比較が生える。 <span class="ver ver-20">C++20</span> |
    | [`std::strong_ordering`](support/strong_ordering.md) | <span class="rank rank-sometimes">たまに</span> | 「等しいものは区別できない」比較結果（整数など）。less / equal / greater の 3 値。 <span class="ver ver-20">C++20</span> |
    | [`std::partial_ordering`](support/partial_ordering.md) | <span class="rank rank-sometimes">たまに</span> | 「比べられない」場合がある比較結果（NaN を含む小数）。 <span class="ver ver-20">C++20</span> |
    | [`std::weak_ordering`](support/weak_ordering.md) | <span class="rank rank-rare">知ってるだけ</span> | 「等しいが、区別はできる」場合を含む比較結果（大文字小文字を無視した比較など）。 <span class="ver ver-20">C++20</span> |

    **関数オブジェクトと呼び出し（<functional>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::less`](support/functional/less.md) | <span class="rank rank-sometimes">たまに</span> | 「小さいか」を比べる関数オブジェクト（`<` の代わり）。 |
    | [`std::greater`](support/functional/greater.md) | <span class="rank rank-sometimes">たまに</span> | 「大きいか」を比べる関数オブジェクト（`>` の代わり）。 |
    | [`std::ref`](support/functional/ref.md) | <span class="rank rank-sometimes">たまに</span> | 値を参照のまま、関数やスレッドに渡す（reference_wrapper を作る）。 |
    | [`std::bind_front`](support/functional/bind_front.md) | <span class="rank rank-sometimes">たまに</span> | 関数の先頭の引数をあらかじめ決めた、新しい関数を作る。 <span class="ver ver-20">C++20</span> |
    | [`std::equal_to`](support/functional/equal_to.md) | <span class="rank rank-rare">知ってるだけ</span> | 「等しいか」を比べる関数オブジェクト（`==` の代わり）。 |
    | [`std::plus`](support/functional/plus.md) | <span class="rank rank-rare">知ってるだけ</span> | 足し算をする関数オブジェクト（`+` の代わり）。 |
    | [`std::multiplies`](support/functional/multiplies.md) | <span class="rank rank-rare">知ってるだけ</span> | 掛け算をする関数オブジェクト（`*` の代わり）。 |
    | [`std::identity`](support/functional/identity.md) | <span class="rank rank-rare">知ってるだけ</span> | 受け取った値をそのまま返す関数オブジェクト。 <span class="ver ver-20">C++20</span> |
    | [`std::invoke`](support/functional/invoke.md) | <span class="rank rank-rare">知ってるだけ</span> | 関数・メンバ関数・メンバ変数を、同じ書き方で呼び出す。 <span class="ver ver-17">C++17</span> |
    | [`std::bind_back`](support/functional/bind_back.md) | <span class="rank rank-rare">知ってるだけ</span> | 関数の末尾の引数をあらかじめ決めた、新しい関数を作る。 <span class="ver ver-23">C++23</span> |
    | [`std::not_fn`](support/functional/not_fn.md) | <span class="rank rank-rare">知ってるだけ</span> | 条件を逆にした関数を作る。 <span class="ver ver-17">C++17</span> |
    | [`std::bind`](support/functional/bind.md) | <span class="rank rank-rare">知ってるだけ</span> | 関数の引数の一部を固定した、新しい関数を作る（古い書き方）。 |
    | [`std::mem_fn`](support/functional/mem_fn.md) | <span class="rank rank-rare">知ってるだけ</span> | メンバ関数ポインターを、普通の関数のように呼べるようにする。 |
    | [`std::reference_wrapper`](support/functional/reference_wrapper.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照を、コピー・代入できる値として持つ入れ物。 |

STL を読むための前提知識は [基礎](../basics/index.md) にまとめています。
