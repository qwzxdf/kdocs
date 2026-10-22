# STL

C++23 の標準ライブラリをゲーム制作でよく使う順にまとめています。見出しをクリックすると一覧が開きます。

迷ったら [コンテナの選び方](../basics/container-chart.md) も見てください。

??? abstract "コンテナ（61）: データをまとめて持つ入れ物"
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
    | [`std::to_array`](containers/to_array.md) | <span class="rank rank-sometimes">たまに</span> | — | 配列リテラルや C の配列から、std::array を作る。 <span class="ver ver-20">C++20</span> |
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
    | [`std::aligned_accessor`](containers/aligned_accessor.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 要素が指定した境界に並ぶことを保証する mdspan のアクセサ。 <span class="ver ver-26">C++26</span> |
    | [`std::default_accessor`](containers/default_accessor.md) | <span class="rank rank-rare">知ってるだけ</span> | — | mdspan の要素への標準のアクセス方法（ふつうのポインタ）。 <span class="ver ver-23">C++23</span> |
    | [`std::dextents`](containers/dextents.md) | <span class="rank rank-rare">知ってるだけ</span> | — | すべての次元が実行時に決まる extents の別名。 <span class="ver ver-23">C++23</span> |
    | [`std::dynamic_extent`](containers/dynamic_extent.md) | <span class="rank rank-rare">知ってるだけ</span> | — | span や mdspan で「要素数が実行時に決まる」ことを表す定数。 <span class="ver ver-20">C++20</span> |
    | [`std::full_extent`](containers/full_extent.md) | <span class="rank rank-rare">知ってるだけ</span> | — | submdspan で「この次元は全部」を表す目印。 <span class="ver ver-26">C++26</span> |
    | [`std::gslice`](containers/gslice.md) | <span class="rank rank-rare">知ってるだけ</span> | — | valarray から、多次元の添字（開始位置・各次元の個数・各次元の間隔）で要素を選ぶ。 |
    | [`std::hive`](containers/hive.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 要素を挿入・削除しても、他の要素の位置が変わらない順序なしコンテナ。 <span class="ver ver-26">C++26</span> |
    | [`std::indirect_array`](containers/indirect_array.md) | <span class="rank rank-rare">知ってるだけ</span> | — | valarray から、添字の配列で選んだ要素への参照。 |
    | [`std::mask_array`](containers/mask_array.md) | <span class="rank rank-rare">知ってるだけ</span> | — | valarray から、bool の配列（マスク）で選んだ要素への参照。 |
    | [`std::slice`](containers/slice.md) | <span class="rank rank-rare">知ってるだけ</span> | — | valarray から、開始位置・個数・間隔で要素を選ぶ。 |
    | [`std::stol`](containers/stol.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 文字列を long に変換する（失敗すると例外）。 |
    | [`std::stold`](containers/stold.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 文字列を long double に変換する（失敗すると例外）。 |
    | [`std::stoul`](containers/stoul.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 文字列を unsigned long に変換する（失敗すると例外）。 |
    | [`std::stoull`](containers/stoull.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 文字列を unsigned long long に変換する（失敗すると例外）。 |
    | [`std::strided_slice`](containers/strided_slice.md) | <span class="rank rank-rare">知ってるだけ</span> | — | submdspan で「開始位置・長さ・間隔」を指定する範囲。 <span class="ver ver-26">C++26</span> |
    | [`std::submdspan`](containers/submdspan.md) | <span class="rank rank-rare">知ってるだけ</span> | — | mdspan の一部（行・列・範囲）を取り出して、新しい mdspan にする。 <span class="ver ver-26">C++26</span> |
    | [`std::to_wstring`](containers/to_wstring.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 数値を wstring に変換する。 |
    | [`std::u16string`](containers/u16string.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `char16_t` を文字の型にもつ文字列。 |
    | [`std::u32string`](containers/u32string.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `char32_t` を文字の型にもつ文字列。 |
    | [`std::u8string`](containers/u8string.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `char8_t` を文字の型にもつ文字列。 <span class="ver ver-20">C++20</span> |
    | [`std::wstring`](containers/wstring.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `wchar_t` を文字の型にもつ文字列。 |

    **文字列と数値の変換**

    | コンテナ | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::to_string`](containers/to_string.md) | <span class="rank rank-often">よく使う</span> | — | 数値を文字列にする。 |
    | [`std::stoi`](containers/stoi.md) | <span class="rank rank-often">よく使う</span> | — | 文字列を int に変換する（失敗すると例外）。 |
    | [`std::stof`](containers/stof.md) | <span class="rank rank-often">よく使う</span> | — | 文字列を float に変換する（失敗すると例外）。 |
    | [`std::stod`](containers/stod.md) | <span class="rank rank-sometimes">たまに</span> | — | 文字列を double に変換する（失敗すると例外）。 |
    | [`std::stoll`](containers/stoll.md) | <span class="rank rank-sometimes">たまに</span> | — | 文字列を long long に変換する（失敗すると例外）。 |

??? abstract "アルゴリズム（140）: 並べ替え・検索・変換"
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
    | [`std::execution::par_unseq`](algorithms/par_unseq.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数のスレッドで、しかもベクトル化も許して実行するポリシー。 <span class="ver ver-17">C++17</span> |
    | [`std::execution::seq`](algorithms/seq.md) | <span class="rank rank-rare">知ってるだけ</span> | 並列化せず、順番に実行するポリシー。 <span class="ver ver-17">C++17</span> |
    | [`std::execution::unseq`](algorithms/unseq.md) | <span class="rank rank-rare">知ってるだけ</span> | 1 つのスレッドの中で、ベクトル化（SIMD）を許して実行するポリシー。 <span class="ver ver-20">C++20</span> |
    | [`std::is_execution_policy`](algorithms/is_execution_policy.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が実行ポリシーかを調べる型特性。 <span class="ver ver-17">C++17</span> |
    | [`std::lexicographical_compare_three_way`](algorithms/lexicographical_compare_three_way.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの範囲を辞書順に比べて、順序（strong_ordering など）を返す。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::fold_left_first_with_iter`](algorithms/fold_left_first_with_iter.md) | <span class="rank rank-rare">知ってるだけ</span> | 初期値なしで左から畳み込み、結果と読んだ位置を返す。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::fold_left_with_iter`](algorithms/fold_left_with_iter.md) | <span class="rank rank-rare">知ってるだけ</span> | 左から畳み込み、結果と「どこまで読んだか」の両方を返す。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::fold_right_last`](algorithms/fold_right_last.md) | <span class="rank rank-rare">知ってるだけ</span> | 初期値なしで、範囲を右から畳み込む。 <span class="ver ver-23">C++23</span> |
    | [`std::replace_copy_if`](algorithms/replace_copy_if.md) | <span class="rank rank-rare">知ってるだけ</span> | 条件に合う要素だけ置き換えながら、別の場所へコピーする。 |
    | [`std::transform_exclusive_scan`](algorithms/transform_exclusive_scan.md) | <span class="rank rank-rare">知ってるだけ</span> | 各要素を変換してから、先頭からの累積を作る（その位置を含まない）。 <span class="ver ver-17">C++17</span> |
    | [`std::transform_inclusive_scan`](algorithms/transform_inclusive_scan.md) | <span class="rank rank-rare">知ってるだけ</span> | 各要素を変換してから、先頭からの累積を作る（その位置を含む）。 <span class="ver ver-17">C++17</span> |

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
    | [views::cache_latest](algorithms/views/cache_latest.md) | <span class="rank rank-rare">知ってるだけ</span> | 直前に計算した要素を覚えておく view。 <span class="ver ver-26">C++26</span> |
    | [views::concat](algorithms/views/concat.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の範囲を、1 本につなげて見せる view。 <span class="ver ver-26">C++26</span> |

??? abstract "ユーティリティ（204）: optional, unique_ptr, format などの便利な部品"
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
    | [`std::make_optional`](utilities/make_optional.md) | <span class="rank rank-sometimes">たまに</span> | — | 値から optional を作る（型を書かなくてよい）。 <span class="ver ver-17">C++17</span> |
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
    | [`std::bad_any_cast`](utilities/bad_any_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | any_cast で、入っている型と違う型を取り出したときの例外。 <span class="ver ver-17">C++17</span> |
    | [`std::basic_format_arg`](utilities/basic_format_arg.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式化の引数 1 つぶんを表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::basic_format_args`](utilities/basic_format_args.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式化の引数のリストを表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::basic_format_string`](utilities/basic_format_string.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式文字列を、コンパイル時に検査して保持する型。 <span class="ver ver-20">C++20</span> |
    | [`std::basic_string_view`](utilities/basic_string_view.md) | <span class="rank rank-rare">知ってるだけ</span> | — | string_view / wstring_view などの元になる、文字の型を選べるテンプレート。 <span class="ver ver-17">C++17</span> |
    | [`std::const_pointer_cast`](utilities/const_pointer_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | shared_ptr の指す先から const を外す（持ち主は共有）。 |
    | [`std::discard_block_engine`](utilities/random/discard_block_engine.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 別のエンジンの出力を、ブロックごとに間引くアダプタ（`ranlux24` の元）。 |
    | [`std::format_context`](utilities/format_context.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式化の出力先と引数を持つクラス（自作の formatter の format で受け取る）。 <span class="ver ver-20">C++20</span> |
    | [`std::format_kind`](utilities/format_kind.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 範囲の書式化の種類（sequence・map・set など）を表す変数。 <span class="ver ver-23">C++23</span> |
    | [`std::format_parse_context`](utilities/format_parse_context.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式文字列の解析の途中状態を持つクラス（自作の formatter の parse で受け取る）。 <span class="ver ver-20">C++20</span> |
    | [`std::format_string`](utilities/format_string.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式文字列を、コンパイル時に検査する型（char 版の別名）。 <span class="ver ver-20">C++20</span> |
    | [`std::formattable`](utilities/formattable.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 型が `std::format` で書式化できることを要求するコンセプト。 <span class="ver ver-23">C++23</span> |
    | [`std::forward_like`](utilities/forward_like.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 別の式の値カテゴリ（左辺値 / 右辺値、const）を、メンバにも引き継いで転送する。 <span class="ver ver-23">C++23</span> |
    | [`std::in_place_index`](utilities/in_place_index.md) | <span class="rank rank-rare">知ってるだけ</span> | — | variant に、番号を指定してその場で作らせる目印。 <span class="ver ver-17">C++17</span> |
    | [`std::in_place_type`](utilities/in_place_type.md) | <span class="rank rank-rare">知ってるだけ</span> | — | variant / any / optional に、型を指定してその場で作らせる目印。 <span class="ver ver-17">C++17</span> |
    | [`std::independent_bits_engine`](utilities/random/independent_bits_engine.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 別のエンジンの出力から、指定したビット数の乱数を作るアダプタ。 |
    | [`std::index_sequence`](utilities/index_sequence.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 0, 1, 2, … の番号の並びを、型で表す。 |
    | [`std::index_sequence_for`](utilities/index_sequence_for.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 型のパックの個数ぶんの index_sequence を作る。 |
    | [`std::linear_congruential_engine`](utilities/random/linear_congruential_engine.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 線形合同法の乱数エンジンのテンプレート（`minstd_rand` の元）。 |
    | [`std::make_format_args`](utilities/make_format_args.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 引数を、書式化用の引数リストにまとめる。 <span class="ver ver-20">C++20</span> |
    | [`std::make_index_sequence`](utilities/make_index_sequence.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 0 から N-1 までの index_sequence を作る。 |
    | [`std::make_integer_sequence`](utilities/make_integer_sequence.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 0 から N-1 までの integer_sequence を、整数型を選んで作る。 |
    | [`std::make_wformat_args`](utilities/make_wformat_args.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 引数を、wchar_t 用の書式化引数リストにまとめる。 <span class="ver ver-20">C++20</span> |
    | [`std::mersenne_twister_engine`](utilities/random/mersenne_twister_engine.md) | <span class="rank rank-rare">知ってるだけ</span> | — | メルセンヌ・ツイスタの乱数エンジンのテンプレート（`mt19937` の元）。 |
    | [`std::minstd_rand0`](utilities/random/minstd_rand0.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 古典的な線形合同法の乱数エンジン（軽いが品質は低め）。 |
    | [`std::mt19937_64`](utilities/random/mt19937_64.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 64 ビット版のメルセンヌ・ツイスタ（高品質な乱数エンジン）。 |
    | [`std::range_format`](utilities/range_format.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 範囲の書式化の種類を表す列挙型。 <span class="ver ver-23">C++23</span> |
    | [`std::range_formatter`](utilities/range_formatter.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 範囲（vector など）を書式化する formatter の部品。 <span class="ver ver-23">C++23</span> |
    | [`std::ranlux24_base`](utilities/random/ranlux24_base.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ranlux24 の土台になる、キャリーつき引き算法のエンジン。 |
    | [`std::ranlux48_base`](utilities/random/ranlux48_base.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ranlux48 の土台になる、キャリーつき引き算法のエンジン。 |
    | [`std::reinterpret_pointer_cast`](utilities/reinterpret_pointer_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | shared_ptr の指す先を、reinterpret_cast で別の型に見せる（持ち主は共有）。 <span class="ver ver-17">C++17</span> |
    | [`std::runtime_format`](utilities/runtime_format.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 実行時の文字列を、書式文字列として `format` に渡す。 <span class="ver ver-26">C++26</span> |
    | [`std::shuffle_order_engine`](utilities/random/shuffle_order_engine.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 別のエンジンの出力の順番を入れ替えるアダプタ（`knuth_b` の元）。 |
    | [`std::static_pointer_cast`](utilities/static_pointer_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | shared_ptr の指す先を、static_cast で別の型に変える（持ち主は共有）。 |
    | [`std::subtract_with_carry_engine`](utilities/random/subtract_with_carry_engine.md) | <span class="rank rank-rare">知ってるだけ</span> | — | キャリーつき引き算法の乱数エンジンのテンプレート（`ranlux24_base` の元）。 |
    | [`std::u16string_view`](utilities/u16string_view.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `char16_t` を文字の型にもつ、文字列を借りて見るだけの型。 <span class="ver ver-17">C++17</span> |
    | [`std::u32string_view`](utilities/u32string_view.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `char32_t` を文字の型にもつ、文字列を借りて見るだけの型。 <span class="ver ver-17">C++17</span> |
    | [`std::u8string_view`](utilities/u8string_view.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `char8_t` を文字の型にもつ、文字列を借りて見るだけの型。 <span class="ver ver-20">C++20</span> |
    | [`std::unexpect`](utilities/unexpect.md) | <span class="rank rank-rare">知ってるだけ</span> | — | expected に、エラー側をその場で作らせる目印。 <span class="ver ver-23">C++23</span> |
    | [`std::variant_alternative`](utilities/variant_alternative.md) | <span class="rank rank-rare">知ってるだけ</span> | — | variant の N 番目の選択肢の型を取り出す。 <span class="ver ver-17">C++17</span> |
    | [`std::variant_npos`](utilities/variant_npos.md) | <span class="rank rank-rare">知ってるだけ</span> | — | variant が値を持たない状態を表す、index() の値。 <span class="ver ver-17">C++17</span> |
    | [`std::vformat_to`](utilities/vformat_to.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 実行時の書式文字列で、出力イテレータに書式化して出力する。 <span class="ver ver-20">C++20</span> |
    | [`std::visit_format_arg`](utilities/visit_format_arg.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式化の引数 1 つの中身を、型に応じて取り出す。 <span class="ver ver-20">C++20</span> |
    | [`std::vprint_nonunicode`](utilities/vprint_nonunicode.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 実行時の書式文字列で、Unicode 変換なしで出力する。 <span class="ver ver-23">C++23</span> |
    | [`std::vprint_unicode`](utilities/vprint_unicode.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 実行時の書式文字列で、Unicode 対応の出力をする。 <span class="ver ver-23">C++23</span> |
    | [`std::wformat_string`](utilities/wformat_string.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式文字列を、コンパイル時に検査する型（wchar_t 版の別名）。 <span class="ver ver-20">C++20</span> |
    | [`std::wstring_view`](utilities/wstring_view.md) | <span class="rank rank-rare">知ってるだけ</span> | — | `wchar_t` を文字の型にもつ、文字列を借りて見るだけの型。 <span class="ver ver-17">C++17</span> |

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
    | [`std::chrono::milliseconds`](utilities/chrono/milliseconds.md) | <span class="rank rank-sometimes">たまに</span> | — | ミリ秒（1000 分の 1 秒）を数える duration の別名。 |
    | [`std::chrono::seconds`](utilities/chrono/seconds.md) | <span class="rank rank-sometimes">たまに</span> | — | 秒を数える duration の別名。 |
    | [`std::chrono::high_resolution_clock`](utilities/chrono/high_resolution_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 最も細かい時計（実体は環境しだい）。使わず steady_clock を使う。 |
    | [`std::chrono::floor`](utilities/chrono/floor.md) | <span class="rank rank-rare">知ってるだけ</span> | — | duration（または time_point）を、別の単位に丸める（切り捨て・切り上げ・四捨五入）。 <span class="ver ver-17">C++17</span> |
    | [`std::chrono::year_month_day`](utilities/chrono/year_month_day.md) | <span class="rank rank-rare">知ってるだけ</span> | — | カレンダーの日付（年・月・日）。曜日や日数の計算もできる。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::hh_mm_ss`](utilities/chrono/hh_mm_ss.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 経過時間を「時・分・秒」に分解する。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::zoned_time`](utilities/chrono/zoned_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | タイムゾーンつきの日時。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::file_clock`](utilities/chrono/file_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ファイルの更新日時に使われる時計。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::ambiguous_local_time`](utilities/chrono/ambiguous_local_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 夏時間の終わりで 2 回ある（曖昧な）ローカル時刻を変換したときの例外。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::clock_cast`](utilities/chrono/clock_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 時計どうしの時点を、別の時計の時点に変換する。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::current_zone`](utilities/chrono/current_zone.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 今の環境のタイムゾーンを取得する。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::day`](utilities/chrono/day.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 月の中の日（1〜31）を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::days`](utilities/chrono/days.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 日を数える duration の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::duration_values`](utilities/chrono/duration_values.md) | <span class="rank rank-rare">知ってるだけ</span> | — | duration の rep について、0・最小・最大を返す。 |
    | [`std::chrono::file_time`](utilities/chrono/file_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | file_clock の時点を表す別名（単位を選べる）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::from_stream`](utilities/chrono/from_stream.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ストリームから書式に従って chrono の型を読み込む。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::get_leap_second_info`](utilities/chrono/get_leap_second_info.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ある UTC の時点が、うるう秒の中か、それまでに何秒入ったかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::get_tzdb`](utilities/chrono/get_tzdb.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 現在のタイムゾーンデータベースを取得する。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::gps_clock`](utilities/chrono/gps_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | GPS の時刻に合わせた時計。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::hours`](utilities/chrono/hours.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 時間を数える duration の別名。 |
    | [`std::chrono::is_am`](utilities/chrono/is_am.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 24 時間制の時刻が午前かを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::is_pm`](utilities/chrono/is_pm.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 24 時間制の時刻が午後かを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::last_spec`](utilities/chrono/last_spec.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「最後」を表す定数 `std::chrono::last` の型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::leap_second`](utilities/chrono/leap_second.md) | <span class="rank rank-rare">知ってるだけ</span> | — | うるう秒の挿入日と値を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::local_days`](utilities/chrono/local_days.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ローカル時刻を、日の単位で表す別名（地域のカレンダーの日付）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::local_info`](utilities/chrono/local_info.md) | <span class="rank rank-rare">知ってるだけ</span> | — | あるローカル時刻の時差情報（曖昧・存在しない場合も表す）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::local_seconds`](utilities/chrono/local_seconds.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ローカル時刻を、秒の単位で表す別名。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::local_time`](utilities/chrono/local_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | タイムゾーンのない、地域の時刻を表す別名。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::locate_zone`](utilities/chrono/locate_zone.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 名前から time_zone を取得する。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::make12`](utilities/chrono/make12.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 24 時間制の時を、12 時間制の時（1〜12）に直す。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::make24`](utilities/chrono/make24.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 12 時間制の時を、24 時間制の時（0〜23）に直す。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::microseconds`](utilities/chrono/microseconds.md) | <span class="rank rank-rare">知ってるだけ</span> | — | マイクロ秒（100 万分の 1 秒）を数える duration の別名。 |
    | [`std::chrono::minutes`](utilities/chrono/minutes.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 分を数える duration の別名。 |
    | [`std::chrono::month`](utilities/chrono/month.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 月（1〜12）を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::month_day`](utilities/chrono/month_day.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 月と日の組（誕生日のような、年を問わない日付）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::month_day_last`](utilities/chrono/month_day_last.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「その月の最終日」を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::month_weekday`](utilities/chrono/month_weekday.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「その月の第 n 曜日」を表す型（年を問わない）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::month_weekday_last`](utilities/chrono/month_weekday_last.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「その月の最後の曜日」を表す型（年を問わない）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::months`](utilities/chrono/months.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 月（平均の長さ）を数える duration の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::nanoseconds`](utilities/chrono/nanoseconds.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ナノ秒（10 億分の 1 秒）を数える duration の別名。 |
    | [`std::chrono::nonexistent_local_time`](utilities/chrono/nonexistent_local_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 夏時間の切り替えで存在しないローカル時刻を変換したときの例外。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::parse`](utilities/chrono/parse.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 文字列を書式に従って読み込み、chrono の型にするための入力マニピュレータ。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::sys_days`](utilities/chrono/sys_days.md) | <span class="rank rank-rare">知ってるだけ</span> | — | system_clock の時点を、日の単位で表す別名（カレンダーの日付）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::sys_info`](utilities/chrono/sys_info.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ある UTC の時点での、時差・夏時間・略称の情報。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::sys_seconds`](utilities/chrono/sys_seconds.md) | <span class="rank rank-rare">知ってるだけ</span> | — | system_clock の時点を、秒の単位で表す別名。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::sys_time`](utilities/chrono/sys_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | system_clock の時点を表す別名（単位を選べる）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::tai_clock`](utilities/chrono/tai_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | うるう秒を含まず、連続して進む国際原子時（TAI）の時計。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::time_point_cast`](utilities/chrono/time_point_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | — | time_point の単位を、別の単位に変換する（切り捨て）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::time_zone`](utilities/chrono/time_zone.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 1 つのタイムゾーン（例: Asia/Tokyo）を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::time_zone_link`](utilities/chrono/time_zone_link.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 別名のタイムゾーン（古い名前から新しい名前への対応）を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::to_stream`](utilities/chrono/to_stream.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 書式に従って chrono の型をストリームに書き出す。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::treat_as_floating_point`](utilities/chrono/treat_as_floating_point.md) | <span class="rank rank-rare">知ってるだけ</span> | — | duration の中身（rep）を、小数として扱うかの特性。 |
    | [`std::chrono::tzdb`](utilities/chrono/tzdb.md) | <span class="rank rank-rare">知ってるだけ</span> | — | タイムゾーンのデータベース（IANA）を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::tzdb_list`](utilities/chrono/tzdb_list.md) | <span class="rank rank-rare">知ってるだけ</span> | — | tzdb の更新履歴（世代ごとの一覧）を管理する型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::utc_clock`](utilities/chrono/utc_clock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | うるう秒を数に入れた、協定世界時（UTC）の時計。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::utc_time`](utilities/chrono/utc_time.md) | <span class="rank rank-rare">知ってるだけ</span> | — | utc_clock の時点を表す別名（単位を選べる）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::weekday`](utilities/chrono/weekday.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 曜日を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::weekday_indexed`](utilities/chrono/weekday_indexed.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「第 n の曜日」を表す型（第 2 月曜日など）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::weekday_last`](utilities/chrono/weekday_last.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「最後の曜日」を表す型（最終金曜日など）。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::weeks`](utilities/chrono/weeks.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 週を数える duration の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::year`](utilities/chrono/year.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 年を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::year_month`](utilities/chrono/year_month.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 年と月の組。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::year_month_day_last`](utilities/chrono/year_month_day_last.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「その年のその月の最終日」を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::year_month_weekday`](utilities/chrono/year_month_weekday.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「その年のその月の第 n 曜日」を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::year_month_weekday_last`](utilities/chrono/year_month_weekday_last.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「その年のその月の最後の曜日」を表す型。 <span class="ver ver-20">C++20</span> |
    | [`std::chrono::years`](utilities/chrono/years.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 年（平均の長さ）を数える duration の別名。 <span class="ver ver-20">C++20</span> |

??? abstract "メモリ（78）: 確保の仕組み、アロケータ、C 由来の関数"
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
    | [`std::allocator_arg`](memory/allocator_arg.md) | <span class="rank rank-rare">知ってるだけ</span> | 「次の引数はアロケータ」と示す目印。 |
    | [`std::assume_aligned`](memory/assume_aligned.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタが N バイト境界にあると、コンパイラに約束する。 <span class="ver ver-20">C++20</span> |
    | [`std::hardware_constructive_interference_size`](memory/hardware_constructive_interference_size.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じキャッシュラインに載せたいデータの、大きさの上限。 <span class="ver ver-17">C++17</span> |
    | [`std::make_obj_using_allocator`](memory/make_obj_using_allocator.md) | <span class="rank rank-rare">知ってるだけ</span> | アロケータを渡しながら、オブジェクトを作る。 <span class="ver ver-20">C++20</span> |
    | [`std::owner_equal`](memory/owner_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | shared_ptr / weak_ptr が、同じ持ち主（制御ブロック）かを比べる。 <span class="ver ver-26">C++26</span> |
    | [`std::owner_hash`](memory/owner_hash.md) | <span class="rank rank-rare">知ってるだけ</span> | shared_ptr / weak_ptr を、持ち主（制御ブロック）で数えたハッシュ値を作る。 <span class="ver ver-26">C++26</span> |
    | [`std::pmr::pool_options`](memory/pmr/pool_options.md) | <span class="rank rank-rare">知ってるだけ</span> | プールのメモリリソースの、ブロックの大きさと数の設定。 <span class="ver ver-17">C++17</span> |
    | [`std::pointer_traits`](memory/pointer_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタ（生ポインタやスマートポインタ）の性質を、同じ書き方で調べる。 |
    | [`std::scoped_allocator_adaptor`](memory/scoped_allocator_adaptor.md) | <span class="rank rank-rare">知ってるだけ</span> | 入れ子のコンテナの全体に、同じアロケータを渡してくれる。 |
    | [`std::start_lifetime_as`](memory/start_lifetime_as.md) | <span class="rank rank-rare">知ってるだけ</span> | バイト列を、そのままの値で指定した型のオブジェクトとして使い始める。 <span class="ver ver-23">C++23</span> |
    | [`std::strcoll`](memory/cstring/strcoll.md) | <span class="rank rank-rare">知ってるだけ</span> | ロケールの規則で、2 つの文字列を比べる。 |
    | [`std::strcspn`](memory/cstring/strcspn.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭から、指定した文字を含まない部分の長さを返す。 |
    | [`std::strerror`](memory/cstring/strerror.md) | <span class="rank rank-rare">知ってるだけ</span> | エラー番号（errno）を、説明の文字列にする。 |
    | [`std::strncat`](memory/cstring/strncat.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の末尾に、最大 n 文字を連結する。 |
    | [`std::strpbrk`](memory/cstring/strpbrk.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の中から、指定した文字のどれかが最初に現れる位置を探す。 |
    | [`std::strrchr`](memory/cstring/strrchr.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の中から、指定した文字が最後に現れる位置を探す。 |
    | [`std::strspn`](memory/cstring/strspn.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭から、指定した文字だけが続く長さを返す。 |
    | [`std::strtok`](memory/cstring/strtok.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を、区切り文字で分割して 1 つずつ取り出す。 |
    | [`std::strxfrm`](memory/cstring/strxfrm.md) | <span class="rank rank-rare">知ってるだけ</span> | ロケールの規則での比較用に、文字列を変換する。 |
    | [`std::uses_allocator`](memory/uses_allocator.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が、指定したアロケータを受け取れるかを調べる型特性。 |

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
    | [`std::bad_array_new_length`](memory/new_delete/bad_array_new_length.md) | <span class="rank rank-rare">知ってるだけ</span> | 配列の new で、要素数が不正だったときの例外。 |
    | [`std::destroy`](memory/new_delete/destroy.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲のオブジェクトのデストラクタを呼ぶ（メモリは返さない）。 <span class="ver ver-17">C++17</span> |
    | [`std::destroy_n`](memory/new_delete/destroy_n.md) | <span class="rank rank-rare">知ってるだけ</span> | 先頭から n 個のオブジェクトのデストラクタを呼ぶ。 <span class="ver ver-17">C++17</span> |
    | [`std::get_new_handler`](memory/new_delete/get_new_handler.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在設定されている new ハンドラを取得する。 |
    | [`std::uninitialized_default_construct`](memory/new_delete/uninitialized_default_construct.md) | <span class="rank rank-rare">知ってるだけ</span> | 未初期化のメモリに、デフォルト初期化でオブジェクトを作る。 <span class="ver ver-17">C++17</span> |
    | [`std::uninitialized_fill`](memory/new_delete/uninitialized_fill.md) | <span class="rank rank-rare">知ってるだけ</span> | 未初期化のメモリの範囲を、同じ値のコピーで埋める。 |
    | [`std::uninitialized_move`](memory/new_delete/uninitialized_move.md) | <span class="rank rank-rare">知ってるだけ</span> | 未初期化のメモリに、範囲の要素をムーブして作る。 <span class="ver ver-17">C++17</span> |
    | [`std::uninitialized_value_construct`](memory/new_delete/uninitialized_value_construct.md) | <span class="rank rank-rare">知ってるだけ</span> | 未初期化のメモリに、値初期化でオブジェクトを作る。 <span class="ver ver-17">C++17</span> |

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

??? abstract "入出力・文字列（266）: ファイル、パス、文字列と数値の変換"
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
    | [`std::scientific`](io/scientific.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数を指数表記（`1.5e+03`）で出す。 |
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
    | [`<cuchar>`](io/cuchar.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字と UTF-8 / 16 / 32 の変換をする C 由来の関数群。 |
    | [`<cwchar>`](io/cwchar.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字（`wchar_t`）の C 由来の関数群。 |
    | [setjmp / longjmp](io/csetjmp.md) | <span class="rank rank-rare">知ってるだけ</span> | 離れた場所へ一気に戻る（C 由来・C++ では危険）。 |
    | [`std::codecvt`](io/codecvt.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字コードの変換を行う、ロケールの部品。 |
    | [BUFSIZ](io/cstdio/bufsiz.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準のバッファの大きさ（バイト）。 |
    | [CLOCKS_PER_SEC](io/ctime/clocks_per_sec.md) | <span class="rank rank-rare">知ってるだけ</span> | clock() の値を、秒に直すための 1 秒あたりのカウント数。 |
    | [EOF](io/cstdio/eof.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの終端またはエラーを表す定数（負の整数）。 |
    | [FILE](io/cstdio/file.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルを表す型。 |
    | [SEEK_CUR](io/cstdio/seek_cur.md) | <span class="rank rank-rare">知ってるだけ</span> | `fseek` の基準：現在位置。 |
    | [SEEK_END](io/cstdio/seek_end.md) | <span class="rank rank-rare">知ってるだけ</span> | `fseek` の基準：ファイルの末尾。 |
    | [SEEK_SET](io/cstdio/seek_set.md) | <span class="rank rank-rare">知ってるだけ</span> | `fseek` の基準：ファイルの先頭。 |
    | [WEOF](io/cwchar/weof.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字の終端またはエラーを表す定数。 |
    | [jmp_buf](io/jmp_buf.md) | <span class="rank rank-rare">知ってるだけ</span> | setjmp が保存した、実行位置の情報を入れる型。 |
    | [`std::asctime`](io/ctime/asctime.md) | <span class="rank rank-rare">知ってるだけ</span> | tm を、決まった形の文字列にする。 |
    | [`std::basic_ios`](io/basic_ios.md) | <span class="rank rank-rare">知ってるだけ</span> | すべてのストリームの土台。状態の確認（good / fail / bad）とロケールの設定を持つ。 |
    | [`std::basic_iostream`](io/basic_iostream.md) | <span class="rank rank-rare">知ってるだけ</span> | 読み書き両用のストリームの元になるテンプレート（`iostream` の元）。 |
    | [`std::basic_istream`](io/basic_istream.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力ストリームの元になるテンプレート（`istream` の元）。 |
    | [`std::basic_ostream`](io/basic_ostream.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力ストリームの元になるテンプレート（`ostream` の元）。 |
    | [`std::basic_regex`](io/regex/basic_regex.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現を保持するクラスの、元になるテンプレート（`regex` の元）。 |
    | [`std::basic_streambuf`](io/basic_streambuf.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームバッファの元になるテンプレート（`streambuf` の元）。 |
    | [`std::btowc`](io/cwchar/btowc.md) | <span class="rank rank-rare">知ってるだけ</span> | 1 バイトの文字を、ワイド文字に変換する。 |
    | [`std::chars_format`](io/chars_format.md) | <span class="rank rank-rare">知ってるだけ</span> | to_chars / from_chars で浮動小数点の書式（固定・指数・16 進）を選ぶ列挙型。 <span class="ver ver-17">C++17</span> |
    | [`std::clearerr`](io/cstdio/clearerr.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルのエラー状態と終端状態をクリアする。 |
    | [`std::clock_t`](io/ctime/clock_t.md) | <span class="rank rank-rare">知ってるだけ</span> | プロセッサ時間（clock の戻り値）を表す型。 |
    | [`std::cmatch`](io/regex/cmatch.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列用の match_results。 |
    | [`std::codecvt`](io/locale/codecvt.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字コードの変換を担当するファセット。 |
    | [`std::codecvt_utf8`](io/locale/codecvt_utf8.md) | <span class="rank rank-rare">知ってるだけ</span> | UTF-8 と、UCS-2 / UTF-32 を変換するファセット（非推奨）。 |
    | [`std::collate`](io/locale/collate.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の照合（辞書順の比較）を担当するファセット。 |
    | [`std::cregex_iterator`](io/regex/cregex_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列から、正規表現に一致する部分を順に取り出すイテレータ。 |
    | [`std::csub_match`](io/regex/csub_match.md) | <span class="rank rank-rare">知ってるだけ</span> | C 文字列用の sub_match。 |
    | [`std::ctime`](io/ctime/ctime.md) | <span class="rank rank-rare">知ってるだけ</span> | time_t を、ローカル時刻の決まった形の文字列にする。 |
    | [`std::ctype`](io/locale/ctype.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字の分類（数字か、英字か）と、大文字小文字の変換を担当するファセット。 |
    | [`std::dec`](io/dec.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数を 10 進数で出力・入力する（既定）。 |
    | [`std::defaultfloat`](io/defaultfloat.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点数の出力を、既定の形式に戻す。 |
    | [`std::difftime`](io/ctime/difftime.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの time_t の差を、秒（double）で返す。 |
    | [`std::emit_on_flush`](io/emit_on_flush.md) | <span class="rank rank-rare">知ってるだけ</span> | osyncstream で、フラッシュのたびに出力を確定する設定にする。 <span class="ver ver-20">C++20</span> |
    | [`std::ends`](io/ends.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列の終端（`'\0'`）を出力する。 |
    | [`std::facet`](io/locale/facet.md) | <span class="rank rank-rare">知ってるだけ</span> | ロケールを構成する、部品（ファセット）の基底クラス。 |
    | [`std::fclose`](io/cstdio/fclose.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルを閉じる。 |
    | [`std::feof`](io/cstdio/feof.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの終端に達したかを調べる。 |
    | [`std::ferror`](io/cstdio/ferror.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの読み書きでエラーが起きたかを調べる。 |
    | [`std::fflush`](io/cstdio/fflush.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力バッファの内容を、いまファイルに書き出す。 |
    | [`std::fgetc`](io/cstdio/fgetc.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルから 1 文字を読む。 |
    | [`std::fgetpos`](io/cstdio/fgetpos.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの現在位置を、保存する。 |
    | [`std::fgetwc`](io/cwchar/fgetwc.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルからワイド文字を 1 文字読む。 |
    | [`std::fgetws`](io/cwchar/fgetws.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルからワイド文字列を 1 行読む。 |
    | [`std::filebuf`](io/filebuf.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルへの読み書きを担当するストリームバッファ。 |
    | [`std::flush_emit`](io/flush_emit.md) | <span class="rank rank-rare">知ってるだけ</span> | osyncstream の出力を確定して、フラッシュする。 <span class="ver ver-20">C++20</span> |
    | [`std::fprintf`](io/cstdio/fprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式を指定して、ファイルに出力する。 |
    | [`std::fputc`](io/cstdio/fputc.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルに 1 文字を書く。 |
    | [`std::fputs`](io/cstdio/fputs.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルに文字列を書く（改行は付かない）。 |
    | [`std::fputwc`](io/cwchar/fputwc.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルにワイド文字を 1 文字書く。 |
    | [`std::fputws`](io/cwchar/fputws.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルにワイド文字列を書く。 |
    | [`std::freopen`](io/cstdio/freopen.md) | <span class="rank rank-rare">知ってるだけ</span> | 開いているファイル（stdout など）を、別のファイルに付け替える。 |
    | [`std::from_chars_result`](io/from_chars_result.md) | <span class="rank rank-rare">知ってるだけ</span> | from_chars の結果（読み終えた位置とエラー）を表す構造体。 <span class="ver ver-17">C++17</span> |
    | [`std::fscanf`](io/cstdio/fscanf.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルから、書式を指定して読み込む。 |
    | [`std::fseek`](io/cstdio/fseek.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの読み書き位置を動かす。 |
    | [`std::fsetpos`](io/cstdio/fsetpos.md) | <span class="rank rank-rare">知ってるだけ</span> | `fgetpos` で保存した位置に、読み書き位置を戻す。 |
    | [`std::ftell`](io/cstdio/ftell.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの現在位置を返す。 |
    | [`std::fwprintf`](io/cwchar/fwprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式を指定して、ワイド文字でファイルに出力する。 |
    | [`std::get_money`](io/get_money.md) | <span class="rank rank-rare">知ってるだけ</span> | 金額を、ロケールの形式で入力する。 |
    | [`std::get_time`](io/get_time.md) | <span class="rank rank-rare">知ってるだけ</span> | 日時を、書式を指定して読み込む。 |
    | [`std::getc`](io/cstdio/getc.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルから 1 文字を読む（`fgetc` と同じ）。 |
    | [`std::getchar`](io/cstdio/getchar.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準入力から 1 文字を読む。 |
    | [`std::has_facet`](io/locale/has_facet.md) | <span class="rank rank-rare">知ってるだけ</span> | ロケールが、指定したファセット（部品）を持っているかを調べる。 |
    | [`std::hexfloat`](io/hexfloat.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点数を、16 進の指数表記で出力する。 |
    | [`std::internal`](io/internal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号や接頭辞を左に、数字を右に寄せる（間を埋める）。 |
    | [`std::iostream`](io/iostream.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力も出力もできるストリームのクラス。 |
    | [`std::ispanstream`](io/ispanstream.md) | <span class="rank rank-rare">知ってるだけ</span> | `span` の上にあるメモリから、読み込むストリーム。 <span class="ver ver-23">C++23</span> |
    | [`std::lconv`](io/locale/lconv.md) | <span class="rank rank-rare">知ってるだけ</span> | 数値と通貨の書式情報をまとめた構造体。 |
    | [`std::left`](io/left.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力を、幅の中で左寄せにする。 |
    | [`std::localeconv`](io/locale/localeconv.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在のロケールの数値・通貨の書式情報を取得する。 |
    | [`std::localtime`](io/ctime/localtime.md) | <span class="rank rank-rare">知ってるだけ</span> | time_t を、ローカル時刻の tm に変換する。 |
    | [`std::match_flag_type`](io/regex/match_flag_type.md) | <span class="rank rank-rare">知ってるだけ</span> | 一致や置換の動作を指定するビットマスク型。 |
    | [`std::match_results`](io/regex/match_results.md) | <span class="rank rank-rare">知ってるだけ</span> | 一致の結果（全体とグループ）を保持するクラスの、元になるテンプレート。 |
    | [`std::mbrlen`](io/cwchar/mbrlen.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字 1 文字のバイト数を返す（途中状態つき）。 |
    | [`std::mbrtowc`](io/cwchar/mbrtowc.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字を、ワイド文字に変換する（途中状態つき）。 |
    | [`std::mbsrtowcs`](io/cwchar/mbsrtowcs.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字列を、ワイド文字列に変換する（途中状態つき）。 |
    | [`std::mbstate_t`](io/cwchar/mbstate_t.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字の変換の途中状態を入れる型。 |
    | [`std::messages`](io/locale/messages.md) | <span class="rank rank-rare">知ってるだけ</span> | メッセージ（翻訳された文字列）をカタログから取り出すファセット。 |
    | [`std::mktime`](io/ctime/mktime.md) | <span class="rank rank-rare">知ってるだけ</span> | tm（年月日時分秒）を time_t に変換する（ローカル時刻として）。 |
    | [`std::money_get`](io/locale/money_get.md) | <span class="rank rank-rare">知ってるだけ</span> | 金額を、ロケールの通貨の書式から読み込むファセット。 |
    | [`std::money_put`](io/locale/money_put.md) | <span class="rank rank-rare">知ってるだけ</span> | 金額を、ロケールの通貨の書式で書き出すファセット。 |
    | [`std::moneypunct`](io/locale/moneypunct.md) | <span class="rank rank-rare">知ってるだけ</span> | 通貨の書式（記号・桁区切り・小数点以下の桁数）を担当するファセット。 |
    | [`std::num_get`](io/locale/num_get.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列から数値を読み込む処理を担当するファセット。 |
    | [`std::num_put`](io/locale/num_put.md) | <span class="rank rank-rare">知ってるだけ</span> | 数値を文字列に書き出す処理を担当するファセット。 |
    | [`std::numpunct`](io/locale/numpunct.md) | <span class="rank rank-rare">知ってるだけ</span> | 数値の書式（小数点・桁区切り）を担当するファセット。 |
    | [`std::oct`](io/oct.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数を 8 進数で出力・入力する。 |
    | [`std::ospanstream`](io/ospanstream.md) | <span class="rank rank-rare">知ってるだけ</span> | `span` の上にあるメモリに、書き込むストリーム。 <span class="ver ver-23">C++23</span> |
    | [`std::perror`](io/cstdio/perror.md) | <span class="rank rank-rare">知ってるだけ</span> | `errno` の内容を、説明つきで標準エラー出力に出す。 |
    | [`std::put_money`](io/put_money.md) | <span class="rank rank-rare">知ってるだけ</span> | 金額を、ロケールの形式で出力する。 |
    | [`std::put_time`](io/put_time.md) | <span class="rank rank-rare">知ってるだけ</span> | 日時（`tm`）を、書式を指定して出力する。 |
    | [`std::putc`](io/cstdio/putc.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルに 1 文字を書く（`fputc` と同じ）。 |
    | [`std::putchar`](io/cstdio/putchar.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準出力に 1 文字を書く。 |
    | [`std::puts`](io/cstdio/puts.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準出力に文字列と改行を書く。 |
    | [`std::quoted`](io/quoted.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を、引用符で囲んで出力・入力する。 |
    | [`std::raise`](io/raise.md) | <span class="rank rank-rare">知ってるだけ</span> | 自分自身にシグナルを送る。 |
    | [`std::regex_constants`](io/regex/regex_constants.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現のオプションとエラーコードをまとめた名前空間。 |
    | [`std::regex_error`](io/regex/regex_error.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現のパターンが不正なときに投げられる例外。 |
    | [`std::regex_iterator`](io/regex/regex_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列から、正規表現に一致する部分を、順に取り出すイテレータ。 |
    | [`std::regex_token_iterator`](io/regex/regex_token_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を、正規表現で分割して（または一致を取り出して）、順に返すイテレータ。 |
    | [`std::regex_traits`](io/regex/regex_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字の分類や変換の規則をまとめた、正規表現の部品。 |
    | [`std::resetiosflags`](io/resetiosflags.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式フラグを、まとめて解除する。 |
    | [`std::rewind`](io/cstdio/rewind.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの読み書き位置を、先頭に戻す。 |
    | [`std::right`](io/right.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力を、幅の中で右寄せにする（既定）。 |
    | [`std::scanf`](io/cstdio/scanf.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準入力から、書式を指定して読み込む。 |
    | [`std::setbase`](io/setbase.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数の基数（8・10・16）を設定する。 |
    | [`std::setbuf`](io/cstdio/setbuf.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルのバッファを、自分で指定した配列にする（または無効にする）。 |
    | [`std::setiosflags`](io/setiosflags.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式フラグを、まとめて設定する。 |
    | [`std::setlocale`](io/locale/setlocale.md) | <span class="rank rank-rare">知ってるだけ</span> | C のロケールを設定・取得する。 |
    | [`std::setvbuf`](io/cstdio/setvbuf.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルのバッファの方式（全部・行・なし）と大きさを設定する。 |
    | [`std::showbase`](io/showbase.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数の出力に、進数の接頭辞（`0x` や `0`）を付ける。 |
    | [`std::showpoint`](io/showpoint.md) | <span class="rank rank-rare">知ってるだけ</span> | 小数の出力に、小数点と末尾の 0 を必ず付ける。 |
    | [`std::showpos`](io/showpos.md) | <span class="rank rank-rare">知ってるだけ</span> | 正の数の出力に、`+` を付ける。 |
    | [`std::sig_atomic_t`](io/sig_atomic_t.md) | <span class="rank rank-rare">知ってるだけ</span> | シグナルハンドラの中で、安全に読み書きできる整数型。 |
    | [`std::skipws`](io/skipws.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力で、先頭の空白を読み飛ばす（既定でオン）。 |
    | [`std::snprintf`](io/cstdio/snprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式を指定して、大きさを決めた文字配列に書き込む（あふれない）。 |
    | [`std::spanbuf`](io/spanbuf.md) | <span class="rank rank-rare">知ってるだけ</span> | `span` の上にあるメモリを使うストリームバッファ。 <span class="ver ver-23">C++23</span> |
    | [`std::sprintf`](io/cstdio/sprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式を指定して、文字配列に書き込む。 |
    | [`std::sregex_token_iterator`](io/regex/sregex_token_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | string 用の regex_token_iterator。 |
    | [`std::sscanf`](io/cstdio/sscanf.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列から、書式を指定して読み込む。 |
    | [`std::ssub_match`](io/regex/ssub_match.md) | <span class="rank rank-rare">知ってるだけ</span> | string 用の sub_match。 |
    | [`std::stderr`](io/cstdio/stderr.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準エラー出力を表す FILE*。 |
    | [`std::stdin`](io/cstdio/stdin.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準入力を表す FILE*。 |
    | [`std::stdout`](io/cstdio/stdout.md) | <span class="rank rank-rare">知ってるだけ</span> | 標準出力を表す FILE*。 |
    | [`std::stringbuf`](io/stringbuf.md) | <span class="rank rank-rare">知ってるだけ</span> | メモリ上の文字列への読み書きを担当するストリームバッファ。 |
    | [`std::sub_match`](io/regex/sub_match.md) | <span class="rank rank-rare">知ってるだけ</span> | 一致したグループ 1 つぶんを表すクラス。 |
    | [`std::swprintf`](io/cwchar/swprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式を指定して、ワイド文字の配列に書き込む。 |
    | [`std::syntax_option_type`](io/regex/syntax_option_type.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規表現の構文やオプションを指定するビットマスク型。 |
    | [`std::time_get`](io/locale/time_get.md) | <span class="rank rank-rare">知ってるだけ</span> | 日時を、書式に従って文字列から読み込むファセット。 |
    | [`std::time_put`](io/locale/time_put.md) | <span class="rank rank-rare">知ってるだけ</span> | 日時を、書式に従って文字列に書き出すファセット。 |
    | [`std::time_t`](io/ctime/time_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 時刻（エポックからの秒数）を表す型。 |
    | [`std::timespec`](io/ctime/timespec.md) | <span class="rank rank-rare">知ってるだけ</span> | 秒とナノ秒の組を表す構造体。 <span class="ver ver-17">C++17</span> |
    | [`std::timespec_get`](io/ctime/timespec_get.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の時刻を、秒とナノ秒の組（timespec）で取得する。 <span class="ver ver-17">C++17</span> |
    | [`std::tm`](io/ctime/tm.md) | <span class="rank rank-rare">知ってるだけ</span> | 年月日時分秒を分けて持つ構造体。 |
    | [`std::tmpfile`](io/cstdio/tmpfile.md) | <span class="rank rank-rare">知ってるだけ</span> | 自動で消える一時ファイルを作る。 |
    | [`std::tmpnam`](io/cstdio/tmpnam.md) | <span class="rank rank-rare">知ってるだけ</span> | 一時ファイルに使える名前を作る（非推奨）。 |
    | [`std::to_chars_result`](io/to_chars_result.md) | <span class="rank rank-rare">知ってるだけ</span> | to_chars の結果（書き込み終えた位置とエラー）を表す構造体。 <span class="ver ver-17">C++17</span> |
    | [`std::ungetc`](io/cstdio/ungetc.md) | <span class="rank rank-rare">知ってるだけ</span> | 読んだ文字を 1 文字、ファイルに戻す。 |
    | [`std::unitbuf`](io/unitbuf.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力のたびに、バッファをフラッシュする。 |
    | [`std::uppercase`](io/uppercase.md) | <span class="rank rank-rare">知ってるだけ</span> | 16 進数や指数表記の英字を、大文字で出力する。 |
    | [`std::use_facet`](io/locale/use_facet.md) | <span class="rank rank-rare">知ってるだけ</span> | ロケールから、ファセット（部品）を取り出す。 |
    | [`std::vfprintf`](io/cstdio/vfprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数のリスト（va_list）を使って、ファイルに出力する。 |
    | [`std::vprintf`](io/cstdio/vprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数のリスト（va_list）を使って、標準出力に出力する。 |
    | [`std::vsnprintf`](io/cstdio/vsnprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数のリスト（va_list）を使って、大きさを指定して文字配列に書き込む。 |
    | [`std::vsprintf`](io/cstdio/vsprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数のリスト（va_list）を使って、文字配列に書き込む。 |
    | [`std::wcmatch`](io/regex/wcmatch.md) | <span class="rank rank-rare">知ってるだけ</span> | wchar_t の C 文字列用の match_results。 |
    | [`std::wcrtomb`](io/cwchar/wcrtomb.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字を、マルチバイト文字に変換する（途中状態つき）。 |
    | [`std::wcscmp`](io/cwchar/wcscmp.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのワイド文字列を比べる。 |
    | [`std::wcscpy`](io/cwchar/wcscpy.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字列をコピーする。 |
    | [`std::wcsrtombs`](io/cwchar/wcsrtombs.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字列を、マルチバイト文字列に変換する（途中状態つき）。 |
    | [`std::wcstol`](io/cwchar/wcstol.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字列を long に変換する。 |
    | [`std::wctob`](io/cwchar/wctob.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字を、1 バイトの文字に変換する。 |
    | [`std::wfstream`](io/wfstream.md) | <span class="rank rank-rare">知ってるだけ</span> | `wchar_t` のファイルストリーム。 |
    | [`std::wint_t`](io/cwchar/wint_t.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字と WEOF を入れられる整数型。 |
    | [`std::wistream`](io/wistream.md) | <span class="rank rank-rare">知ってるだけ</span> | `wchar_t` の入力ストリーム。 |
    | [`std::wmemcpy`](io/cwchar/wmemcpy.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字の配列を、指定した個数だけコピーする。 |
    | [`std::wostream`](io/wostream.md) | <span class="rank rank-rare">知ってるだけ</span> | `wchar_t` の出力ストリーム。 |
    | [`std::wprintf`](io/cwchar/wprintf.md) | <span class="rank rank-rare">知ってるだけ</span> | 書式を指定して、ワイド文字で標準出力に出す。 |
    | [`std::wregex`](io/regex/wregex.md) | <span class="rank rank-rare">知ってるだけ</span> | `wchar_t` 用の正規表現。 |
    | [`std::ws`](io/ws.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力で、空白（スペース・改行・タブ）を読み飛ばす。 |
    | [`std::wscanf`](io/cwchar/wscanf.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字で、標準入力から書式を指定して読み込む。 |
    | [`std::wsmatch`](io/regex/wsmatch.md) | <span class="rank rank-rare">知ってるだけ</span> | wstring 用の match_results。 |
    | [`std::wstringstream`](io/wstringstream.md) | <span class="rank rank-rare">知ってるだけ</span> | `wchar_t` の文字列ストリーム。 |
    | [va_arg](io/va_arg.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数から、次の引数を指定した型で取り出す。 |
    | [va_copy](io/va_copy.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数の読み取り状態をコピーする。 |
    | [va_end](io/va_end.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数の読み取りを終える。 |
    | [va_start](io/va_start.md) | <span class="rank rank-rare">知ってるだけ</span> | 可変引数の読み取りを始める。 |

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
    | [`std::filesystem::copy_symlink`](io/filesystem/copy_symlink.md) | <span class="rank rank-rare">知ってるだけ</span> | シンボリックリンクを、リンクのままコピーする。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::create_directory_symlink`](io/filesystem/create_directory_symlink.md) | <span class="rank rank-rare">知ってるだけ</span> | フォルダへのシンボリックリンクを作る。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::create_hard_link`](io/filesystem/create_hard_link.md) | <span class="rank rank-rare">知ってるだけ</span> | ハードリンク（同じ実体への別の名前）を作る。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::file_status`](io/filesystem/file_status.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの種類と権限を持つクラス。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::file_time_type`](io/filesystem/file_time_type.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの更新時刻を表す型。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::hard_link_count`](io/filesystem/hard_link_count.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルのハードリンクの数を返す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_block_file`](io/filesystem/is_block_file.md) | <span class="rank rank-rare">知ってるだけ</span> | パスがブロックデバイスかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_character_file`](io/filesystem/is_character_file.md) | <span class="rank rank-rare">知ってるだけ</span> | パスがキャラクタデバイスかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_fifo`](io/filesystem/is_fifo.md) | <span class="rank rank-rare">知ってるだけ</span> | パスが名前つきパイプ（FIFO）かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_other`](io/filesystem/is_other.md) | <span class="rank rank-rare">知ってるだけ</span> | パスが通常ファイル・フォルダ・シンボリックリンク以外かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_socket`](io/filesystem/is_socket.md) | <span class="rank rank-rare">知ってるだけ</span> | パスがソケットかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::is_symlink`](io/filesystem/is_symlink.md) | <span class="rank rank-rare">知ってるだけ</span> | パスがシンボリックリンクかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::perm_options`](io/filesystem/perm_options.md) | <span class="rank rank-rare">知ってるだけ</span> | permissions で権限をどう変更するか（置き換え・追加・削除）を指定する。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::perms`](io/filesystem/perms.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの権限（読み・書き・実行）を表すビットマスク型。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::proximate`](io/filesystem/proximate.md) | <span class="rank rank-rare">知ってるだけ</span> | 基準のパスから見た相対パスを返す（作れなければ元のパス）。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::read_symlink`](io/filesystem/read_symlink.md) | <span class="rank rank-rare">知ってるだけ</span> | シンボリックリンクが指すパスを返す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::space_info`](io/filesystem/space_info.md) | <span class="rank rank-rare">知ってるだけ</span> | ディスクの容量と空き容量を持つ構造体。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::status_known`](io/filesystem/status_known.md) | <span class="rank rank-rare">知ってるだけ</span> | ファイルの状態を取得できたかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::symlink_status`](io/filesystem/symlink_status.md) | <span class="rank rank-rare">知ってるだけ</span> | シンボリックリンクをたどらずに、そのファイル自身の状態を返す。 <span class="ver ver-17">C++17</span> |
    | [`std::filesystem::u8path`](io/filesystem/u8path.md) | <span class="rank rank-rare">知ってるだけ</span> | UTF-8 の文字列から path を作る（非推奨）。 <span class="ver ver-17">C++17</span> |

    **時刻（<ctime>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::time`](io/ctime/time.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在時刻を、1970 年からの秒数で取得する（C 由来）。 |
    | [`std::clock`](io/ctime/clock.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラムが使った CPU 時間を取得する（C 由来）。 |
    | [`std::strftime`](io/ctime/strftime.md) | <span class="rank rank-rare">知ってるだけ</span> | 日時を、書式に従った文字列にする（C 由来）。 |
    | [`std::gmtime`](io/ctime/gmtime.md) | <span class="rank rank-rare">知ってるだけ</span> | 秒数を、UTC の年月日時分秒に分解する（C 由来）。 |

??? abstract "数値（244）: 数学関数、定数、整数型、ビット操作"
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
    | [`std::linalg`](numeric/linalg.md) | <span class="rank rank-rare">知ってるだけ</span> | 行列とベクトルの基本演算を、標準で提供する（C++26）。 <span class="ver ver-26">C++26</span> |
    | [EXIT_FAILURE](numeric/cstdlib/exit_failure.md) | <span class="rank rank-rare">知ってるだけ</span> | 失敗を表す終了コードのマクロ。 |
    | [EXIT_SUCCESS](numeric/cstdlib/exit_success.md) | <span class="rank rank-rare">知ってるだけ</span> | 成功を表す終了コードのマクロ。 |
    | [RAND_MAX](numeric/cstdlib/rand_max.md) | <span class="rank rank-rare">知ってるだけ</span> | rand() が返す最大値のマクロ。 |
    | [`std::arg`](numeric/complex/arg.md) | <span class="rank rank-rare">知ってるだけ</span> | 複素数の偏角（実軸からの角度）をラジアンで返す。 |
    | [`std::at_quick_exit`](numeric/cstdlib/at_quick_exit.md) | <span class="rank rank-rare">知ってるだけ</span> | quick_exit() で終了するときに呼ぶ関数を登録する。 |
    | [`std::atexit`](numeric/cstdlib/atexit.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラム終了時に呼ぶ関数を登録する。 |
    | [`std::atof`](numeric/cstdlib/atof.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を double に変換する。 |
    | [`std::atol`](numeric/cstdlib/atol.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を long に変換する。 |
    | [`std::atoll`](numeric/cstdlib/atoll.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を long long に変換する。 |
    | [`std::c16rtomb`](numeric/cuchar/c16rtomb.md) | <span class="rank rank-rare">知ってるだけ</span> | c16 → mb：UTF-16 のコード単位（`char16_t`）を、ロケールのマルチバイト文字列に変換します。 |
    | [`std::c32rtomb`](numeric/cuchar/c32rtomb.md) | <span class="rank rank-rare">知ってるだけ</span> | c32 → mb：UTF-32（コードポイント、`char32_t`）を、ロケールのマルチバイト文字列に変換します。 |
    | [`std::c8rtomb`](numeric/cuchar/c8rtomb.md) | <span class="rank rank-rare">知ってるだけ</span> | c8 → mb：UTF-8 のコード単位（`char8_t`）を、ロケールのマルチバイト文字列に変換します。 <span class="ver ver-20">C++20</span> |
    | [`std::centi`](numeric/ratio/centi.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「centi」（100 分の 1）を表す `ratio` の別名。 |
    | [`std::conj`](numeric/complex/conj.md) | <span class="rank rank-rare">知ってるだけ</span> | 共役複素数（虚部の符号を反転したもの）を返す。 |
    | [`std::deca`](numeric/ratio/deca.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「deca」（10 倍）を表す `ratio` の別名。 |
    | [`std::deci`](numeric/ratio/deci.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「deci」（10 分の 1）を表す `ratio` の別名。 |
    | [`std::exa`](numeric/ratio/exa.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「exa」（100 京倍）を表す `ratio` の別名。 |
    | [`std::giga`](numeric/ratio/giga.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「giga」（10 億倍）を表す `ratio` の別名。 |
    | [`std::hecto`](numeric/ratio/hecto.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「hecto」（100 倍）を表す `ratio` の別名。 |
    | [`std::imag`](numeric/complex/imag.md) | <span class="rank rank-rare">知ってるだけ</span> | 複素数の虚部を取り出す。 |
    | [`std::imaxabs`](numeric/cinttypes/imaxabs.md) | <span class="rank rank-rare">知ってるだけ</span> | `intmax_t` の絶対値を返す。 |
    | [`std::imaxdiv`](numeric/cinttypes/imaxdiv.md) | <span class="rank rank-rare">知ってるだけ</span> | `intmax_t` の割り算で、商と余りをいっしょに返す。 |
    | [`std::isalnum`](numeric/cctype/isalnum.md) | <span class="rank rank-rare">知ってるだけ</span> | 英字か数字かを調べる。 |
    | [`std::isblank`](numeric/cctype/isblank.md) | <span class="rank rank-rare">知ってるだけ</span> | 空白かタブかを調べる。 |
    | [`std::iscntrl`](numeric/cctype/iscntrl.md) | <span class="rank rank-rare">知ってるだけ</span> | 制御文字かを調べる。 |
    | [`std::isgraph`](numeric/cctype/isgraph.md) | <span class="rank rank-rare">知ってるだけ</span> | 空白以外の表示できる文字かを調べる。 |
    | [`std::islower`](numeric/cctype/islower.md) | <span class="rank rank-rare">知ってるだけ</span> | 英小文字かを調べる。 |
    | [`std::isprint`](numeric/cctype/isprint.md) | <span class="rank rank-rare">知ってるだけ</span> | 表示できる文字（空白を含む）かを調べる。 |
    | [`std::ispunct`](numeric/cctype/ispunct.md) | <span class="rank rank-rare">知ってるだけ</span> | 句読点・記号かを調べる。 |
    | [`std::isupper`](numeric/cctype/isupper.md) | <span class="rank rank-rare">知ってるだけ</span> | 英大文字かを調べる。 |
    | [`std::isxdigit`](numeric/cctype/isxdigit.md) | <span class="rank rank-rare">知ってるだけ</span> | 16 進数の数字（0〜9, a〜f, A〜F）かを調べる。 |
    | [`std::kilo`](numeric/ratio/kilo.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「kilo」（1000 倍）を表す `ratio` の別名。 |
    | [`std::labs`](numeric/cstdlib/labs.md) | <span class="rank rank-rare">知ってるだけ</span> | long の絶対値を返す。 |
    | [`std::ldiv`](numeric/cstdlib/ldiv.md) | <span class="rank rank-rare">知ってるだけ</span> | long の割り算で、商と余りをいっしょに返す。 |
    | [`std::llabs`](numeric/cstdlib/llabs.md) | <span class="rank rank-rare">知ってるだけ</span> | long long の絶対値を返す。 |
    | [`std::lldiv`](numeric/cstdlib/lldiv.md) | <span class="rank rank-rare">知ってるだけ</span> | long long の割り算で、商と余りをいっしょに返す。 |
    | [`std::mblen`](numeric/cstdlib/mblen.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字の 1 文字目のバイト数を返す。 |
    | [`std::mbrtoc16`](numeric/cuchar/mbrtoc16.md) | <span class="rank rank-rare">知ってるだけ</span> | mb → c16：ロケールのマルチバイト文字列 1 文字を UTF-16 のコード単位（`char16_t`）に変換します。 |
    | [`std::mbrtoc32`](numeric/cuchar/mbrtoc32.md) | <span class="rank rank-rare">知ってるだけ</span> | mb → c32：ロケールのマルチバイト文字列 1 文字を UTF-32（コードポイント、`char32_t`）に変換します。 |
    | [`std::mbrtoc8`](numeric/cuchar/mbrtoc8.md) | <span class="rank rank-rare">知ってるだけ</span> | mb → c8：ロケールのマルチバイト文字列 1 文字を UTF-8 のコード単位（`char8_t`）に変換します。 <span class="ver ver-20">C++20</span> |
    | [`std::mbstowcs`](numeric/cstdlib/mbstowcs.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字列を wchar_t の文字列に変換する。 |
    | [`std::mbtowc`](numeric/cstdlib/mbtowc.md) | <span class="rank rank-rare">知ってるだけ</span> | マルチバイト文字 1 文字を wchar_t に変換する。 |
    | [`std::mega`](numeric/ratio/mega.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「mega」（100 万倍）を表す `ratio` の別名。 |
    | [`std::micro`](numeric/ratio/micro.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「micro」（100 万分の 1）を表す `ratio` の別名。 |
    | [`std::milli`](numeric/ratio/milli.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「milli」（1000 分の 1）を表す `ratio` の別名。 |
    | [`std::nano`](numeric/ratio/nano.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「nano」（10 億分の 1）を表す `ratio` の別名。 |
    | [`std::norm`](numeric/complex/norm.md) | <span class="rank rank-rare">知ってるだけ</span> | 複素数の大きさの 2 乗を返す。 |
    | [`std::peta`](numeric/ratio/peta.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「peta」（1000 兆倍）を表す `ratio` の別名。 |
    | [`std::polar`](numeric/complex/polar.md) | <span class="rank rank-rare">知ってるだけ</span> | 大きさと角度から複素数を作る。 |
    | [`std::proj`](numeric/complex/proj.md) | <span class="rank rank-rare">知ってるだけ</span> | 複素数をリーマン球面への射影に直す（無限大の扱いをそろえる）。 |
    | [`std::quick_exit`](numeric/cstdlib/quick_exit.md) | <span class="rank rank-rare">知ってるだけ</span> | 後始末を最小限にして、プログラムを終了する。 |
    | [`std::ratio_add`](numeric/ratio/ratio_add.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` の足し算を、コンパイル時に計算して `ratio` で返す。 |
    | [`std::ratio_divide`](numeric/ratio/ratio_divide.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` の割り算を、コンパイル時に計算して `ratio` で返す。 |
    | [`std::ratio_equal`](numeric/ratio/ratio_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` を `==` で比べる（コンパイル時）。 |
    | [`std::ratio_greater`](numeric/ratio/ratio_greater.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` を `>` で比べる（コンパイル時）。 |
    | [`std::ratio_greater_equal`](numeric/ratio/ratio_greater_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` を `>=` で比べる（コンパイル時）。 |
    | [`std::ratio_less`](numeric/ratio/ratio_less.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` を `<` で比べる（コンパイル時）。 |
    | [`std::ratio_less_equal`](numeric/ratio/ratio_less_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` を `<=` で比べる（コンパイル時）。 |
    | [`std::ratio_multiply`](numeric/ratio/ratio_multiply.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` のかけ算を、コンパイル時に計算して `ratio` で返す。 |
    | [`std::ratio_not_equal`](numeric/ratio/ratio_not_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` を `!=` で比べる（コンパイル時）。 |
    | [`std::ratio_subtract`](numeric/ratio/ratio_subtract.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの `ratio` の引き算を、コンパイル時に計算して `ratio` で返す。 |
    | [`std::real`](numeric/complex/real.md) | <span class="rank rank-rare">知ってるだけ</span> | 複素数の実部を取り出す。 |
    | [`std::srand`](numeric/cstdlib/srand.md) | <span class="rank rank-rare">知ってるだけ</span> | rand() の乱数の並びを、シードで初期化する。 |
    | [`std::strtod`](numeric/cstdlib/strtod.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を double に変換する（読み終えた位置が分かる）。 |
    | [`std::strtof`](numeric/cstdlib/strtof.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を float に変換する（読み終えた位置が分かる）。 |
    | [`std::strtoimax`](numeric/cinttypes/strtoimax.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を `intmax_t` に変換する。 |
    | [`std::strtold`](numeric/cstdlib/strtold.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を long double に変換する（読み終えた位置が分かる）。 |
    | [`std::strtoll`](numeric/cstdlib/strtoll.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を long long に変換する（進数を指定でき、読み終えた位置が分かる）。 |
    | [`std::strtoul`](numeric/cstdlib/strtoul.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を unsigned long に変換する（進数を指定でき、読み終えた位置が分かる）。 |
    | [`std::strtoull`](numeric/cstdlib/strtoull.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を unsigned long long に変換する（進数を指定でき、読み終えた位置が分かる）。 |
    | [`std::strtoumax`](numeric/cinttypes/strtoumax.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字列を `uintmax_t` に変換する。 |
    | [`std::system`](numeric/cstdlib/system.md) | <span class="rank rank-rare">知ってるだけ</span> | OS のコマンドを実行する。 |
    | [`std::tera`](numeric/ratio/tera.md) | <span class="rank rank-rare">知ってるだけ</span> | SI 接頭辞「tera」（1 兆倍）を表す `ratio` の別名。 |
    | [`std::wcstombs`](numeric/cstdlib/wcstombs.md) | <span class="rank rank-rare">知ってるだけ</span> | wchar_t の文字列をマルチバイト文字列に変換する。 |
    | [`std::wctomb`](numeric/cstdlib/wctomb.md) | <span class="rank rank-rare">知ってるだけ</span> | wchar_t 1 文字をマルチバイト文字に変換する。 |

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

    **<cwctype> のワイド文字の判定・変換**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::iswalnum`](numeric/cwctype/iswalnum.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が英数字かを調べる。 |
    | [`std::iswalpha`](numeric/cwctype/iswalpha.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が英字かを調べる。 |
    | [`std::iswblank`](numeric/cwctype/iswblank.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が空白かタブかを調べる。 |
    | [`std::iswcntrl`](numeric/cwctype/iswcntrl.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が制御文字かを調べる。 |
    | [`std::iswdigit`](numeric/cwctype/iswdigit.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が数字かを調べる。 |
    | [`std::iswgraph`](numeric/cwctype/iswgraph.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が空白以外の表示できる文字かを調べる。 |
    | [`std::iswlower`](numeric/cwctype/iswlower.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が小文字かを調べる。 |
    | [`std::iswprint`](numeric/cwctype/iswprint.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が表示できる文字かを調べる。 |
    | [`std::iswpunct`](numeric/cwctype/iswpunct.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が記号かを調べる。 |
    | [`std::iswspace`](numeric/cwctype/iswspace.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が空白類かを調べる。 |
    | [`std::iswupper`](numeric/cwctype/iswupper.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が大文字かを調べる。 |
    | [`std::iswxdigit`](numeric/cwctype/iswxdigit.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字が 16 進数の数字かを調べる。 |
    | [`std::towlower`](numeric/cwctype/towlower.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字を小文字にする。 |
    | [`std::towupper`](numeric/cwctype/towupper.md) | <span class="rank rank-rare">知ってるだけ</span> | ワイド文字を大文字にする。 |

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
    | [`std::fabs`](numeric/cmath/fabs.md) | <span class="rank rank-sometimes">たまに</span> | 浮動小数点の絶対値を返す。 |
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
    | [HUGE_VAL](numeric/cmath/huge_val.md) | <span class="rank rank-rare">知ってるだけ</span> | double の無限大を表すマクロ。 |
    | [INFINITY](numeric/cmath/infinity.md) | <span class="rank rank-rare">知ってるだけ</span> | float の無限大を表すマクロ。 |
    | [NAN](numeric/cmath/nan_macro.md) | <span class="rank rank-rare">知ってるだけ</span> | float の NaN（非数）を表すマクロ。 |
    | [math_errhandling](numeric/cmath/math_errhandling.md) | <span class="rank rank-rare">知ってるだけ</span> | 数学関数のエラーの知らせ方を表すマクロ。 |
    | [`std::acosh`](numeric/cmath/acosh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線逆余弦（cosh の逆関数）を返す。 |
    | [`std::asinh`](numeric/cmath/asinh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線逆正弦（sinh の逆関数）を返す。 |
    | [`std::assoc_laguerre`](numeric/cmath/assoc_laguerre.md) | <span class="rank rank-rare">知ってるだけ</span> | ラゲール陪多項式を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::assoc_legendre`](numeric/cmath/assoc_legendre.md) | <span class="rank rank-rare">知ってるだけ</span> | ルジャンドル陪関数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::atanh`](numeric/cmath/atanh.md) | <span class="rank rank-rare">知ってるだけ</span> | 双曲線逆正接（tanh の逆関数）を返す。 |
    | [`std::beta`](numeric/cmath/beta.md) | <span class="rank rank-rare">知ってるだけ</span> | ベータ関数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::comp_ellint_1`](numeric/cmath/comp_ellint_1.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::comp_ellint_2`](numeric/cmath/comp_ellint_2.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 2 種完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::comp_ellint_3`](numeric/cmath/comp_ellint_3.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 3 種完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::cyl_bessel_i`](numeric/cmath/cyl_bessel_i.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種変形ベッセル関数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::cyl_bessel_j`](numeric/cmath/cyl_bessel_j.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種ベッセル関数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::cyl_bessel_k`](numeric/cmath/cyl_bessel_k.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 2 種変形ベッセル関数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::cyl_neumann`](numeric/cmath/cyl_neumann.md) | <span class="rank rank-rare">知ってるだけ</span> | ノイマン関数（第 2 種ベッセル関数）を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::ellint_1`](numeric/cmath/ellint_1.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 1 種不完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::ellint_2`](numeric/cmath/ellint_2.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 2 種不完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::ellint_3`](numeric/cmath/ellint_3.md) | <span class="rank rank-rare">知ってるだけ</span> | 第 3 種不完全楕円積分を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::erf`](numeric/cmath/erf.md) | <span class="rank rank-rare">知ってるだけ</span> | 誤差関数（正規分布の積分に関係する関数）を返す。 |
    | [`std::erfc`](numeric/cmath/erfc.md) | <span class="rank rank-rare">知ってるだけ</span> | 相補誤差関数（1 − erf）を返す。 |
    | [`std::expint`](numeric/cmath/expint.md) | <span class="rank rank-rare">知ってるだけ</span> | 指数積分 Ei(x) を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::fdim`](numeric/cmath/fdim.md) | <span class="rank rank-rare">知ってるだけ</span> | x − y が正ならその値、そうでなければ 0 を返す。 |
    | [`std::fpclassify`](numeric/cmath/fpclassify.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点数の種類（0・正規数・NaN など）を判定する。 |
    | [`std::hermite`](numeric/cmath/hermite.md) | <span class="rank rank-rare">知ってるだけ</span> | エルミート多項式を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::ilogb`](numeric/cmath/ilogb.md) | <span class="rank rank-rare">知ってるだけ</span> | x の指数部（2 を底とした対数の整数部分）を int で返す。 |
    | [`std::isgreater`](numeric/cmath/isgreater.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y より大きいか）。NaN でも例外を出さない。 |
    | [`std::isgreaterequal`](numeric/cmath/isgreaterequal.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y 以上か）。NaN でも例外を出さない。 |
    | [`std::isless`](numeric/cmath/isless.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y より小さいか）。NaN でも例外を出さない。 |
    | [`std::islessequal`](numeric/cmath/islessequal.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y 以下か）。NaN でも例外を出さない。 |
    | [`std::islessgreater`](numeric/cmath/islessgreater.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（x が y より小さいか大きいか（等しくも非順序でもない））。NaN でも例外を出さない。 |
    | [`std::isnormal`](numeric/cmath/isnormal.md) | <span class="rank rank-rare">知ってるだけ</span> | 正規数（0・無限大・NaN・非正規数以外）かを判定する。 |
    | [`std::isunordered`](numeric/cmath/isunordered.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点を比べる（どちらかが NaN で、大小を比べられないか）。NaN でも例外を出さない。 |
    | [`std::laguerre`](numeric/cmath/laguerre.md) | <span class="rank rank-rare">知ってるだけ</span> | ラゲール多項式を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::legendre`](numeric/cmath/legendre.md) | <span class="rank rank-rare">知ってるだけ</span> | ルジャンドル多項式を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::lgamma`](numeric/cmath/lgamma.md) | <span class="rank rank-rare">知ってるだけ</span> | ガンマ関数の自然対数を返す。 |
    | [`std::llrint`](numeric/cmath/llrint.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の丸めモードで整数に丸める（long long で返す）。 |
    | [`std::llround`](numeric/cmath/llround.md) | <span class="rank rank-rare">知ってるだけ</span> | 四捨五入して long long にする。 |
    | [`std::logb`](numeric/cmath/logb.md) | <span class="rank rank-rare">知ってるだけ</span> | x の指数部を、浮動小数点で返す。 |
    | [`std::lrint`](numeric/cmath/lrint.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の丸めモードで整数に丸める（long で返す）。 |
    | [`std::nan`](numeric/cmath/nan.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した文字列に対応する NaN（非数）を返す。 |
    | [`std::nextafter`](numeric/cmath/nextafter.md) | <span class="rank rank-rare">知ってるだけ</span> | x の次に表せる浮動小数点数を返す（y の方向へ）。 |
    | [`std::nexttoward`](numeric/cmath/nexttoward.md) | <span class="rank rank-rare">知ってるだけ</span> | x の次に表せる値を返す（向かう先が long double）。 |
    | [`std::remquo`](numeric/cmath/remquo.md) | <span class="rank rank-rare">知ってるだけ</span> | 割り算の余りと、商の下位ビットをいっしょに返す。 |
    | [`std::riemann_zeta`](numeric/cmath/riemann_zeta.md) | <span class="rank rank-rare">知ってるだけ</span> | リーマンのゼータ関数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::rint`](numeric/cmath/rint.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の丸めモードで整数に丸める（結果は小数）。 |
    | [`std::scalbln`](numeric/cmath/scalbln.md) | <span class="rank rank-rare">知ってるだけ</span> | x × 2ⁿ を計算する（指数が long）。 |
    | [`std::scalbn`](numeric/cmath/scalbn.md) | <span class="rank rank-rare">知ってるだけ</span> | x × 2ⁿ を、乗算を使わずに計算する。 |
    | [`std::sph_bessel`](numeric/cmath/sph_bessel.md) | <span class="rank rank-rare">知ってるだけ</span> | 球ベッセル関数（第 1 種）を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::sph_legendre`](numeric/cmath/sph_legendre.md) | <span class="rank rank-rare">知ってるだけ</span> | 球面調和関数の θ 部分を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::sph_neumann`](numeric/cmath/sph_neumann.md) | <span class="rank rank-rare">知ってるだけ</span> | 球ノイマン関数を求める。 <span class="ver ver-17">C++17</span> |
    | [`std::tgamma`](numeric/cmath/tgamma.md) | <span class="rank rank-rare">知ってるだけ</span> | ガンマ関数（階乗の一般化）を返す。 |

    **浮動小数点環境（<cfenv>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::feclearexcept`](numeric/feclearexcept.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点例外のフラグをクリアする。 |
    | [`std::fegetenv`](numeric/fegetenv.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点環境（フラグと丸めモード）を丸ごと保存する。 |
    | [`std::fegetexceptflag`](numeric/fegetexceptflag.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点例外のフラグの状態を保存する。 |
    | [`std::fegetround`](numeric/fegetround.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在の浮動小数点の丸めモードを調べる。 |
    | [`std::feholdexcept`](numeric/feholdexcept.md) | <span class="rank rank-rare">知ってるだけ</span> | 環境を保存し、例外フラグをクリアして、例外を止めるモードに入る。 |
    | [`std::feraiseexcept`](numeric/feraiseexcept.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点例外を、意図して発生させる。 |
    | [`std::fesetenv`](numeric/fesetenv.md) | <span class="rank rank-rare">知ってるだけ</span> | 保存しておいた浮動小数点環境を復元する。 |
    | [`std::fesetexceptflag`](numeric/fesetexceptflag.md) | <span class="rank rank-rare">知ってるだけ</span> | 保存しておいた浮動小数点例外のフラグを復元する。 |
    | [`std::fetestexcept`](numeric/fetestexcept.md) | <span class="rank rank-rare">知ってるだけ</span> | 浮動小数点例外のフラグを調べる。 |
    | [`std::feupdateenv`](numeric/feupdateenv.md) | <span class="rank rank-rare">知ってるだけ</span> | 保存した環境を復元し、保留中の例外を再び発生させる。 |

    **飽和演算（<numeric>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::add_sat`](numeric/add_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 足し算。範囲を超えたら最大・最小値に張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::sub_sat`](numeric/sub_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 引き算。範囲を超えたら最大・最小値に張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::mul_sat`](numeric/mul_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 掛け算。範囲を超えたら最大・最小値に張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::div_sat`](numeric/div_sat.md) | <span class="rank rank-rare">知ってるだけ</span> | 割り算。範囲を超える唯一の場合（最小値 ÷ −1）で張り付く。 <span class="ver ver-26">C++26</span> |
    | [`std::saturate_cast`](numeric/saturate_cast.md) | <span class="rank rank-rare">知ってるだけ</span> | 整数を別の整数型に変換する。範囲を超えたら張り付く。 <span class="ver ver-26">C++26</span> |

??? abstract "並行処理（71）: スレッドとデータの守り方"
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
    | [`std::launch`](concurrency/launch.md) | <span class="rank rank-sometimes">たまに</span> | — | async の実行方法（別スレッドか、遅延か）を選ぶ列挙型。 |
    | [`std::once_flag`](concurrency/once_flag.md) | <span class="rank rank-sometimes">たまに</span> | — | call_once で「1 回だけ実行」を管理するための旗。 |
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
    | [`std::adopt_lock`](concurrency/adopt_lock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 「すでにロック済みのミューテックスを引き取る」と伝える目印。 |
    | [`std::atomic_fetch_add`](concurrency/atomic_fetch_add.md) | <span class="rank rank-rare">知ってるだけ</span> | — | アトミックに加算し、加算前の値を返す。 |
    | [`std::atomic_fetch_sub`](concurrency/atomic_fetch_sub.md) | <span class="rank rank-rare">知ってるだけ</span> | — | アトミックに減算し、減算前の値を返す。 |
    | [`std::atomic_flag_clear`](concurrency/atomic_flag_clear.md) | <span class="rank rank-rare">知ってるだけ</span> | — | atomic_flag を下ろす。 |
    | [`std::atomic_flag_test_and_set`](concurrency/atomic_flag_test_and_set.md) | <span class="rank rank-rare">知ってるだけ</span> | — | atomic_flag を立て、立てる前の状態を返す。 |
    | [`std::atomic_init`](concurrency/atomic_init.md) | <span class="rank rank-rare">知ってるだけ</span> | — | atomic を初期化する（まだ他のスレッドが触っていないとき）。 |
    | [`std::atomic_is_lock_free`](concurrency/atomic_is_lock_free.md) | <span class="rank rank-rare">知ってるだけ</span> | — | atomic の操作が、ロックなしで行えるかを調べる。 |
    | [`std::atomic_load_explicit`](concurrency/atomic_load_explicit.md) | <span class="rank rank-rare">知ってるだけ</span> | — | メモリ順序を指定して、アトミックに値を読む。 |
    | [`std::atomic_notify_all`](concurrency/atomic_notify_all.md) | <span class="rank rank-rare">知ってるだけ</span> | — | atomic_wait で待っているスレッドを全部起こす。 <span class="ver ver-20">C++20</span> |
    | [`std::atomic_notify_one`](concurrency/atomic_notify_one.md) | <span class="rank rank-rare">知ってるだけ</span> | — | atomic_wait で待っているスレッドを 1 つ起こす。 <span class="ver ver-20">C++20</span> |
    | [`std::atomic_signal_fence`](concurrency/atomic_signal_fence.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 同じスレッドの中の、シグナルハンドラとの間の順序を強制する柵。 |
    | [`std::atomic_store_explicit`](concurrency/atomic_store_explicit.md) | <span class="rank rank-rare">知ってるだけ</span> | — | メモリ順序を指定して、アトミックに値を書く。 |
    | [`std::atomic_thread_fence`](concurrency/atomic_thread_fence.md) | <span class="rank rank-rare">知ってるだけ</span> | — | スレッド間のメモリ順序を、変数なしで強制する柵（フェンス）。 |
    | [`std::atomic_wait`](concurrency/atomic_wait.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 値が変わるまで、アトミックに待つ。 <span class="ver ver-20">C++20</span> |
    | [`std::cv_status`](concurrency/cv_status.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 条件変数の待機が、通知で終わったか、時間切れで終わったかを表す列挙型。 |
    | [`std::defer_lock`](concurrency/defer_lock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | unique_lock に「まだロックしない」と伝える目印。 |
    | [`std::future_errc`](concurrency/future_errc.md) | <span class="rank rank-rare">知ってるだけ</span> | — | future_error の原因を表す列挙型。 |
    | [`std::future_error`](concurrency/future_error.md) | <span class="rank rank-rare">知ってるだけ</span> | — | future / promise の使い方を間違えたときの例外。 |
    | [`std::future_status`](concurrency/future_status.md) | <span class="rank rank-rare">知ってるだけ</span> | — | future の待機の結果（準備完了・時間切れ・遅延）を表す列挙型。 |
    | [`std::hazard_pointer`](concurrency/hazard_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 別のスレッドが使用中のオブジェクトを「使っている」と宣言する印。 <span class="ver ver-26">C++26</span> |
    | [`std::hazard_pointer_obj_base`](concurrency/hazard_pointer_obj_base.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ハザードポインタで守るオブジェクトが継承する基底クラス。 <span class="ver ver-26">C++26</span> |
    | [`std::kill_dependency`](concurrency/kill_dependency.md) | <span class="rank rank-rare">知ってるだけ</span> | — | メモリ順序の依存関係をここで断ち切る。 |
    | [`std::make_hazard_pointer`](concurrency/make_hazard_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | — | ハザードポインタを作る。 <span class="ver ver-26">C++26</span> |
    | [`std::never_stop_token`](concurrency/never_stop_token.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 停止が絶対に要求されない stop_token。 <span class="ver ver-26">C++26</span> |
    | [`std::nostopstate`](concurrency/nostopstate.md) | <span class="rank rank-rare">知ってるだけ</span> | — | stop_source を、停止の状態を持たない形で作る目印。 <span class="ver ver-20">C++20</span> |
    | [`std::notify_all_at_thread_exit`](concurrency/notify_all_at_thread_exit.md) | <span class="rank rank-rare">知ってるだけ</span> | — | スレッドが完全に終わった（後始末も済んだ）あとで、条件変数に通知する。 |
    | [`std::rcu_barrier`](concurrency/rcu_barrier.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 予約された破棄が、すべて終わるまで待つ。 <span class="ver ver-26">C++26</span> |
    | [`std::rcu_default_domain`](concurrency/rcu_default_domain.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 標準の RCU ドメインを返す関数。 <span class="ver ver-26">C++26</span> |
    | [`std::rcu_domain`](concurrency/rcu_domain.md) | <span class="rank rank-rare">知ってるだけ</span> | — | RCU の管理単位（ドメイン）を表す型。 <span class="ver ver-26">C++26</span> |
    | [`std::rcu_obj_base`](concurrency/rcu_obj_base.md) | <span class="rank rank-rare">知ってるだけ</span> | — | RCU で保護するオブジェクトが継承する基底クラス。 <span class="ver ver-26">C++26</span> |
    | [`std::rcu_retire`](concurrency/rcu_retire.md) | <span class="rank rank-rare">知ってるだけ</span> | — | オブジェクトの破棄を、読み取りが終わってからの予約にする。 <span class="ver ver-26">C++26</span> |
    | [`std::rcu_synchronize`](concurrency/rcu_synchronize.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 読み取り中のスレッドがいなくなるまで待つ。 <span class="ver ver-26">C++26</span> |
    | [`std::recursive_timed_mutex`](concurrency/recursive_timed_mutex.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 同じスレッドで何度でもロックでき、時間切れも指定できるミューテックス。 |
    | [`std::shared_timed_mutex`](concurrency/shared_timed_mutex.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 読み取りは同時に、書き込みは 1 つだけで、時間切れも指定できるミューテックス。 |
    | [`std::try_to_lock`](concurrency/try_to_lock.md) | <span class="rank rank-rare">知ってるだけ</span> | — | unique_lock に「ロックを試すだけ。取れなければ待たない」と伝える目印。 |

    **this_thread**

    | 名前 | 重要度 | 速さ | 一言で |
    | --- | --- | --- | --- |
    | [`std::this_thread::sleep_for`](concurrency/this_thread/sleep_for.md) | <span class="rank rank-sometimes">たまに</span> | — | 今のスレッドを、指定した時間だけ止める。 |
    | [`std::this_thread::sleep_until`](concurrency/this_thread/sleep_until.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 今のスレッドを、指定した時刻まで止める。 |
    | [`std::this_thread::yield`](concurrency/this_thread/yield.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 他のスレッドに、実行の順番を譲る。 |
    | [`std::this_thread::get_id`](concurrency/this_thread/get_id.md) | <span class="rank rank-rare">知ってるだけ</span> | — | 今のスレッドの ID を取得する。 |

??? abstract "型・言語サポート（376）: イテレータの道具、関数オブジェクト、型の性質、例外"
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
    | [`std::ranges::elements_of`](support/ranges/elements_of.md) | <span class="rank rank-rare">知ってるだけ</span> | ジェネレーターの中で、別のレンジを丸ごと `co_yield` する（C++23）。 <span class="ver ver-23">C++23</span> |
    | [`std::basic_stacktrace`](support/basic_stacktrace.md) | <span class="rank rank-rare">知ってるだけ</span> | stacktrace の元になる、アロケータを選べるテンプレート。 <span class="ver ver-23">C++23</span> |
    | [`std::contracts::contract_violation`](support/contract_violation.md) | <span class="rank rank-rare">知ってるだけ</span> | 契約（事前条件・事後条件）の違反の情報を表す型。 <span class="ver ver-26">C++26</span> |
    | [`std::from_range`](support/ranges/from_range.md) | <span class="rank rank-rare">知ってるだけ</span> | コンテナのコンストラクタに「範囲から作る」と伝える目印。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::bidirectional_range`](support/ranges/bidirectional_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 前後どちらにも進める範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::borrowed_iterator_t`](support/ranges/borrowed_iterator_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲のイテレータの型（借りられない範囲なら dangling）を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::borrowed_range`](support/ranges/borrowed_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 元の範囲より長生きするイテレータを返せる範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::common_range`](support/ranges/common_range.md) | <span class="rank rank-rare">知ってるだけ</span> | begin と end が同じ型の範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::contiguous_range`](support/ranges/contiguous_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素がメモリ上で連続して並ぶ範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::enable_borrowed_range`](support/ranges/enable_borrowed_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 自分の型を borrowed_range として扱ってよいと宣言する変数テンプレート。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::enable_view`](support/ranges/enable_view.md) | <span class="rank rank-rare">知ってるだけ</span> | 自分の型を view として扱ってよいと宣言する変数テンプレート。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::forward_range`](support/ranges/forward_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 何度でも先頭から読み直せる範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::input_range`](support/ranges/input_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力として一度だけ読める範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::iterator_t`](support/ranges/iterator_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲のイテレータの型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::output_range`](support/ranges/output_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 書き込める範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::random_access_range`](support/ranges/random_access_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 添字で好きな位置へ飛べる範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::range_adaptor_closure`](support/ranges/range_adaptor_closure.md) | <span class="rank rank-rare">知ってるだけ</span> | 自作のパイプ対応アダプタを作るための土台。 <span class="ver ver-23">C++23</span> |
    | [`std::ranges::range_difference_t`](support/ranges/range_difference_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲のイテレータの差の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::range_reference_t`](support/ranges/range_reference_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素の参照の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::range_size_t`](support/ranges/range_size_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素数の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::range_value_t`](support/ranges/range_value_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の要素の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::sentinel_t`](support/ranges/sentinel_t.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲の終端（sentinel）の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::sized_range`](support/ranges/sized_range.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素数を定数時間で返せる範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::view_interface`](support/ranges/view_interface.md) | <span class="rank rank-rare">知ってるだけ</span> | begin と end だけ書けば、empty() や front() などを足してくれる view の土台。 <span class="ver ver-20">C++20</span> |
    | [`std::ranges::viewable_range`](support/ranges/viewable_range.md) | <span class="rank rank-rare">知ってるだけ</span> | view に変換できる範囲を要求するコンセプト。 <span class="ver ver-20">C++20</span> |
    | [`std::stacktrace_entry`](support/stacktrace_entry.md) | <span class="rank rank-rare">知ってるだけ</span> | スタックトレースの 1 行（関数 1 つぶん）を表す型。 <span class="ver ver-23">C++23</span> |
    | [`std::text_encoding`](support/text_encoding.md) | <span class="rank rank-rare">知ってるだけ</span> | 文字エンコーディング（UTF-8 など）の名前を表す型。 <span class="ver ver-26">C++26</span> |
    | [`std::views::all_t`](support/ranges/all_t.md) | <span class="rank rank-rare">知ってるだけ</span> | views::all が返す view の型。 <span class="ver ver-20">C++20</span> |
    | [`std::views::to_input`](support/ranges/to_input.md) | <span class="rank rank-rare">知ってるだけ</span> | 範囲を、入力範囲（1 回だけ読める）として見せる view。 <span class="ver ver-26">C++26</span> |

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
    | [`std::back_insert_iterator`](support/iterator/back_insert_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、コンテナの末尾へ push_back するイテレータ。 |
    | [`std::basic_const_iterator`](support/iterator/basic_const_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を const として見せるイテレータのアダプタ。 <span class="ver ver-23">C++23</span> |
    | [`std::bidirectional_iterator_tag`](support/iterator/bidirectional_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 双方向イテレータ（前後どちらにも進める）を表すタグの型。 |
    | [`std::common_iterator`](support/iterator/common_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータと sentinel（終端）を、1 つの型にまとめる。 <span class="ver ver-20">C++20</span> |
    | [`std::contiguous_iterator_tag`](support/iterator/contiguous_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 連続イテレータ（メモリ上で連続した要素を指す）を表すタグの型。 <span class="ver ver-20">C++20</span> |
    | [`std::counted_iterator`](support/iterator/counted_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 残りの個数を数えながら進むイテレータ。 <span class="ver ver-20">C++20</span> |
    | [`std::crbegin`](support/iterator/crbegin.md) | <span class="rank rank-rare">知ってるだけ</span> | const の逆順イテレータで、末尾の要素を指す。 |
    | [`std::crend`](support/iterator/crend.md) | <span class="rank rank-rare">知ってるだけ</span> | const の逆順イテレータで、先頭の手前を指す。 |
    | [`std::default_sentinel`](support/iterator/default_sentinel.md) | <span class="rank rank-rare">知ってるだけ</span> | counted_iterator などの終端を表す目印の定数。 <span class="ver ver-20">C++20</span> |
    | [`std::forward_iterator_tag`](support/iterator/forward_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 前方イテレータ（何度でも読み返せる（一方向））を表すタグの型。 |
    | [`std::front_insert_iterator`](support/iterator/front_insert_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、コンテナの先頭へ push_front するイテレータ。 |
    | [`std::input_iterator_tag`](support/iterator/input_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 入力イテレータ（1 回だけ読み進められる）を表すタグの型。 |
    | [`std::insert_iterator`](support/iterator/insert_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入するたびに、コンテナの指定位置へ insert するイテレータ。 |
    | [`std::istreambuf_iterator`](support/iterator/istreambuf_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームバッファから、1 文字ずつ生で読むイテレータ。 |
    | [`std::iter_difference_t`](support/iterator/iter_difference_t.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータの差の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::iter_move`](support/iterator/iter_move.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータが指す要素を、右辺値として取り出す。 <span class="ver ver-20">C++20</span> |
    | [`std::iter_reference_t`](support/iterator/iter_reference_t.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータの `*it` の型（参照）を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::iter_value_t`](support/iterator/iter_value_t.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータが指す値の型を取り出す型の別名。 <span class="ver ver-20">C++20</span> |
    | [`std::iterator_traits`](support/iterator/iterator_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータの性質（要素の型、種類など）を取り出す。 |
    | [`std::make_const_iterator`](support/iterator/make_const_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータを、要素が const として見えるイテレータに変換する。 <span class="ver ver-23">C++23</span> |
    | [`std::make_reverse_iterator`](support/iterator/make_reverse_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータから reverse_iterator を作る。 |
    | [`std::move_sentinel`](support/iterator/move_sentinel.md) | <span class="rank rank-rare">知ってるだけ</span> | move_iterator と組み合わせる、ムーブ用の終端。 <span class="ver ver-20">C++20</span> |
    | [`std::ostreambuf_iterator`](support/iterator/ostreambuf_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | ストリームバッファへ、1 文字ずつ生で書くイテレータ。 |
    | [`std::output_iterator_tag`](support/iterator/output_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | 出力イテレータ（書き込みながら進められる）を表すタグの型。 |
    | [`std::projected`](support/iterator/projected.md) | <span class="rank rank-rare">知ってるだけ</span> | プロジェクション（変換）を通した値を、アルゴリズムに見せるための型。 <span class="ver ver-20">C++20</span> |
    | [`std::random_access_iterator_tag`](support/iterator/random_access_iterator_tag.md) | <span class="rank rank-rare">知ってるだけ</span> | ランダムアクセスイテレータ（添字で好きな位置へ飛べる）を表すタグの型。 |
    | [`std::unreachable_sentinel`](support/iterator/unreachable_sentinel.md) | <span class="rank rank-rare">知ってるだけ</span> | 「終わりには絶対に届かない」と約束する終端。 <span class="ver ver-20">C++20</span> |

    **エラーコード（<system_error>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::error_code`](support/error_code.md) | <span class="rank rank-sometimes">たまに</span> | OS やライブラリのエラーを、値と分類で表す（例外を使わない失敗の通知）。 |
    | [`std::error_condition`](support/error_condition.md) | <span class="rank rank-rare">知ってるだけ</span> | 環境に依存しない「エラーの種類」を表す。error_code と比べる相手。 |
    | [`std::errc`](support/errc.md) | <span class="rank rank-rare">知ってるだけ</span> | 環境に依存しない、エラーの種類の名前（列挙型）。 |
    | [`std::error_category`](support/error_category.md) | <span class="rank rank-rare">知ってるだけ</span> | エラーコードの種類（分類）を表す基底クラス。 |
    | [`std::generic_category`](support/generic_category.md) | <span class="rank rank-rare">知ってるだけ</span> | OS に依存しない標準のエラー（`errc`）の分類を表す error_category を返す。 |
    | [`std::io_errc`](support/io_errc.md) | <span class="rank rank-rare">知ってるだけ</span> | 入出力ストリームのエラーを表す列挙型。 |
    | [`std::iostream_category`](support/iostream_category.md) | <span class="rank rank-rare">知ってるだけ</span> | 入出力ストリームのエラー（`io_errc`）の分類を表す error_category を返す。 |
    | [`std::is_error_code_enum`](support/is_error_code_enum.md) | <span class="rank rank-rare">知ってるだけ</span> | 自作の列挙型を、error_code に暗黙変換できるようにする特性。 |
    | [`std::is_error_condition_enum`](support/is_error_condition_enum.md) | <span class="rank rank-rare">知ってるだけ</span> | 自作の列挙型を、error_condition に暗黙変換できるようにする特性。 |
    | [`std::make_error_code`](support/make_error_code.md) | <span class="rank rank-rare">知ってるだけ</span> | errc などの列挙値から、error_code を作る。 |
    | [`std::make_error_condition`](support/make_error_condition.md) | <span class="rank rank-rare">知ってるだけ</span> | errc などの列挙値から、error_condition を作る。 |
    | [`std::system_category`](support/system_category.md) | <span class="rank rank-rare">知ってるだけ</span> | OS 固有のエラー（Windows の `GetLastError`、POSIX の `errno`）の分類を表す error_category を返す。 |

    **コルーチン（<coroutine>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [`std::coroutine_handle`](support/coroutine/coroutine_handle.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンの再開・破棄を操作する「取っ手」。 <span class="ver ver-20">C++20</span> |
    | [`std::suspend_always`](support/coroutine/suspend_always.md) | <span class="rank rank-rare">知ってるだけ</span> | 「必ず一時停止する」ことを表す待ち受け体。 <span class="ver ver-20">C++20</span> |
    | [`std::suspend_never`](support/coroutine/suspend_never.md) | <span class="rank rank-rare">知ってるだけ</span> | 「一時停止しない」ことを表す待ち受け体。 <span class="ver ver-20">C++20</span> |
    | [co_await](support/coroutine/co_await.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンを一時停止して、あとで結果を受け取って再開する演算子。 <span class="ver ver-20">C++20</span> |
    | [co_yield](support/coroutine/co_yield.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンから値を 1 つ返して一時停止し、次に呼ばれたら続きから再開する。 <span class="ver ver-20">C++20</span> |
    | [co_return](support/coroutine/co_return.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンを終了して、値を返す。 <span class="ver ver-20">C++20</span> |
    | [`std::coroutine_traits`](support/coroutine/coroutine_traits.md) | <span class="rank rank-rare">知ってるだけ</span> | コルーチンの戻り値の型から、promise_type を取り出す特性。 <span class="ver ver-20">C++20</span> |
    | [`std::noop_coroutine`](support/coroutine/noop_coroutine.md) | <span class="rank rank-rare">知ってるだけ</span> | 何もしないコルーチンのハンドルを返す。 <span class="ver ver-20">C++20</span> |

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
    | [`std::assignable_from`](support/concepts/assignable_from.md) | <span class="rank rank-rare">知ってるだけ</span> | 左辺の型に、右辺の値を代入できることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::bidirectional_iterator`](support/concepts/bidirectional_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 前後どちらにも進めるイテレータを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::common_reference_with`](support/concepts/common_reference_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型が、共通の参照型を持つことを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::common_with`](support/concepts/common_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型が、共通の型を持つことを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::constructible_from`](support/concepts/constructible_from.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数から構築できる型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::contiguous_iterator`](support/concepts/contiguous_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素がメモリ上で連続して並ぶことを保証するイテレータを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::copy_constructible`](support/concepts/copy_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | コピーして構築できる型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::destructible`](support/concepts/destructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 破棄できる型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::equality_comparable`](support/concepts/equality_comparable.md) | <span class="rank rank-rare">知ってるだけ</span> | `==` と `!=` で比べられる型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::equality_comparable_with`](support/concepts/equality_comparable_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの異なる型を `==` で比べられることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::equivalence_relation`](support/concepts/equivalence_relation.md) | <span class="rank rank-rare">知ってるだけ</span> | 同値関係（反射・対称・推移）となる二項関係を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::forward_iterator`](support/concepts/forward_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 何度でも読み返せて、一方向に進むイテレータを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::incrementable`](support/concepts/incrementable.md) | <span class="rank rank-rare">知ってるだけ</span> | `++` で進められ、何度でも同じ範囲を走査できる型を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirect_binary_predicate`](support/concepts/indirect_binary_predicate.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのイテレータが指す値で、2 引数の述語を呼べることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirect_equivalence_relation`](support/concepts/indirect_equivalence_relation.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのイテレータが指す値で、同値関係を呼べることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirect_strict_weak_order`](support/concepts/indirect_strict_weak_order.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのイテレータが指す値で、厳密な弱順序を呼べることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirect_unary_predicate`](support/concepts/indirect_unary_predicate.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータが指す値で、1 引数の述語を呼べることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_comparable`](support/concepts/indirectly_comparable.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのイテレータが指す要素を、比較関数で比べられることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_copyable`](support/concepts/indirectly_copyable.md) | <span class="rank rank-rare">知ってるだけ</span> | あるイテレータから別のイテレータへ、要素をコピーできることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_movable`](support/concepts/indirectly_movable.md) | <span class="rank rank-rare">知ってるだけ</span> | あるイテレータから別のイテレータへ、要素をムーブできることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_readable`](support/concepts/indirectly_readable.md) | <span class="rank rank-rare">知ってるだけ</span> | `*it` で値を読み取れる型を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_regular_unary_invocable`](support/concepts/indirectly_regular_unary_invocable.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータが指す値で、副作用なく 1 引数の関数を呼べることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_swappable`](support/concepts/indirectly_swappable.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのイテレータが指す要素を、入れ替えられることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_unary_invocable`](support/concepts/indirectly_unary_invocable.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータが指す値で、1 引数の関数を呼べることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::indirectly_writable`](support/concepts/indirectly_writable.md) | <span class="rank rank-rare">知ってるだけ</span> | `*it = value` で値を書き込める型を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::input_iterator`](support/concepts/input_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を読みながら進められるイテレータを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::input_or_output_iterator`](support/concepts/input_or_output_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータとして最低限の操作ができることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::mergeable`](support/concepts/mergeable.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの整列済み範囲を併合できるイテレータの組を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::move_constructible`](support/concepts/move_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | ムーブして構築できる型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::output_iterator`](support/concepts/output_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した型の値を書き込めるイテレータを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::permutable`](support/concepts/permutable.md) | <span class="rank rank-rare">知ってるだけ</span> | 要素を並べ替えられるイテレータを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::random_access_iterator`](support/concepts/random_access_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 添字で好きな位置へ飛べるイテレータを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::regular`](support/concepts/regular.md) | <span class="rank rank-rare">知ってるだけ</span> | 値のように扱える型（コピー・既定構築・比較）を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::regular_invocable`](support/concepts/regular_invocable.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じ引数で何度呼んでも、同じ結果になる呼び出し可能な型を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::relation`](support/concepts/relation.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの値を比べる二項関係（真偽を返す関数）を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::semiregular`](support/concepts/semiregular.md) | <span class="rank rank-rare">知ってるだけ</span> | コピーでき、既定構築できる型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::sentinel_for`](support/concepts/sentinel_for.md) | <span class="rank rank-rare">知ってるだけ</span> | あるイテレータの終端として使える型を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::signed_integral`](support/concepts/signed_integral.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きの整数型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::sized_sentinel_for`](support/concepts/sized_sentinel_for.md) | <span class="rank rank-rare">知ってるだけ</span> | イテレータとの差（距離）を定数時間で求められる終端を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::sortable`](support/concepts/sortable.md) | <span class="rank rank-rare">知ってるだけ</span> | 並べ替えられるイテレータ（ランダムアクセスと入れ替えと比較）を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::strict_weak_order`](support/concepts/strict_weak_order.md) | <span class="rank rank-rare">知ってるだけ</span> | 厳密な弱順序（`sort` に使える比較）となる二項関係を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::swappable`](support/concepts/swappable.md) | <span class="rank rank-rare">知ってるだけ</span> | `swap` で入れ替えられる型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::swappable_with`](support/concepts/swappable_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型の値を、たがいに `swap` できることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::totally_ordered_with`](support/concepts/totally_ordered_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの異なる型を `<` などで比べられることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::unsigned_integral`](support/concepts/unsigned_integral.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号なしの整数型であることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::weakly_incrementable`](support/concepts/weakly_incrementable.md) | <span class="rank rank-rare">知ってるだけ</span> | `++` で進めるイテレータの最低限の条件を要求する。 <span class="ver ver-20">C++20</span> |

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
    | [`std::enable_if`](support/type_traits/enable_if.md) | <span class="rank rank-sometimes">たまに</span> | 条件が真のときだけ、型を存在させる（SFINAE のための道具）。 |
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
    | [`std::add_const`](support/type_traits/add_const.md) | <span class="rank rank-rare">知ってるだけ</span> | `const` を付け足す。 |
    | [`std::add_cv`](support/type_traits/add_cv.md) | <span class="rank rank-rare">知ってるだけ</span> | `const volatile` を付け足す。 |
    | [`std::add_lvalue_reference`](support/type_traits/add_lvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 左辺値参照を付け足す。 |
    | [`std::add_pointer`](support/type_traits/add_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタを付け足す。 |
    | [`std::add_rvalue_reference`](support/type_traits/add_rvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 右辺値参照を付け足す。 |
    | [`std::add_volatile`](support/type_traits/add_volatile.md) | <span class="rank rank-rare">知ってるだけ</span> | `volatile` を付け足す。 |
    | [`std::aligned_storage`](support/type_traits/aligned_storage.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した大きさと境界の、生のメモリ領域の型。 |
    | [`std::aligned_union`](support/type_traits/aligned_union.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の型のどれでも入れられる、生のメモリ領域の型。 |
    | [`std::alignment_of`](support/type_traits/alignment_of.md) | <span class="rank rank-rare">知ってるだけ</span> | 型のアライメント（配置できる境界のバイト数）を調べる。 |
    | [`std::bool_constant`](support/type_traits/bool_constant.md) | <span class="rank rank-rare">知ってるだけ</span> | `bool` のコンパイル時の定数を、型として表す。 |
    | [`std::common_reference`](support/type_traits/common_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の型が共有できる、共通の参照型を求める。 <span class="ver ver-20">C++20</span> |
    | [`std::conjunction`](support/type_traits/conjunction.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の条件がすべて真かを調べる（短絡評価）。 <span class="ver ver-17">C++17</span> |
    | [`std::disjunction`](support/type_traits/disjunction.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の条件のどれかが真かを調べる（短絡評価）。 <span class="ver ver-17">C++17</span> |
    | [`std::false_type`](support/type_traits/false_type.md) | <span class="rank rank-rare">知ってるだけ</span> | `false` を表すコンパイル時の定数の型。 |
    | [`std::has_unique_object_representations`](support/type_traits/has_unique_object_representations.md) | <span class="rank rank-rare">知ってるだけ</span> | 同じ値なら必ず同じビット列になる型かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::has_virtual_destructor`](support/type_traits/has_virtual_destructor.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が仮想デストラクタを持つかを調べる。 |
    | [`std::integral_constant`](support/type_traits/integral_constant.md) | <span class="rank rank-rare">知ってるだけ</span> | コンパイル時の定数を、型として表す。 |
    | [`std::is_abstract`](support/type_traits/is_abstract.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が抽象クラス（純粋仮想関数を持つ）かを調べる。 |
    | [`std::is_array`](support/type_traits/is_array.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が配列かを調べる。 |
    | [`std::is_assignable`](support/type_traits/is_assignable.md) | <span class="rank rank-rare">知ってるだけ</span> | 代入できる型の組かを調べる。 |
    | [`std::is_bounded_array`](support/type_traits/is_bounded_array.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が要素数の決まった配列かを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_class`](support/type_traits/is_class.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がクラス（struct を含む）かを調べる。 |
    | [`std::is_compound`](support/type_traits/is_compound.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が複合型（基本型以外）かを調べる。 |
    | [`std::is_constant_evaluated`](support/type_traits/is_constant_evaluated.md) | <span class="rank rank-rare">知ってるだけ</span> | いま、コンパイル時に評価されているかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_constructible`](support/type_traits/is_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で構築できる型かを調べる。 |
    | [`std::is_convertible`](support/type_traits/is_convertible.md) | <span class="rank rank-rare">知ってるだけ</span> | 型 `From` から `To` へ暗黙に変換できるかを調べる。 |
    | [`std::is_copy_assignable`](support/type_traits/is_copy_assignable.md) | <span class="rank rank-rare">知ってるだけ</span> | コピー代入できる型かを調べる。 |
    | [`std::is_corresponding_member`](support/type_traits/is_corresponding_member.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのメンバが、2 つの構造体の対応する位置にあるかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_destructible`](support/type_traits/is_destructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 破棄できる型かを調べる。 |
    | [`std::is_final`](support/type_traits/is_final.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `final`（継承できない）かを調べる。 |
    | [`std::is_function`](support/type_traits/is_function.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が関数の型かを調べる。 |
    | [`std::is_fundamental`](support/type_traits/is_fundamental.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が基本型（算術型・`void`・`nullptr_t`）かを調べる。 |
    | [`std::is_implicit_lifetime`](support/type_traits/is_implicit_lifetime.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が「暗黙的に寿命を始められる」型かを調べる。 <span class="ver ver-23">C++23</span> |
    | [`std::is_invocable`](support/type_traits/is_invocable.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で呼び出せる型かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::is_invocable_r`](support/type_traits/is_invocable_r.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で呼び出せ、結果を `R` に変換できる型かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::is_layout_compatible`](support/type_traits/is_layout_compatible.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型のメモリ配置が互換かを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_lvalue_reference`](support/type_traits/is_lvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が左辺値参照かを調べる。 |
    | [`std::is_member_function_pointer`](support/type_traits/is_member_function_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がメンバ関数へのポインタかを調べる。 |
    | [`std::is_member_object_pointer`](support/type_traits/is_member_object_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がメンバ変数へのポインタかを調べる。 |
    | [`std::is_member_pointer`](support/type_traits/is_member_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がメンバへのポインタかを調べる。 |
    | [`std::is_move_assignable`](support/type_traits/is_move_assignable.md) | <span class="rank rank-rare">知ってるだけ</span> | ムーブ代入できる型かを調べる。 |
    | [`std::is_move_constructible`](support/type_traits/is_move_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | ムーブして構築できる型かを調べる。 |
    | [`std::is_nothrow_constructible`](support/type_traits/is_nothrow_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で、例外を投げずに構築できる型かを調べる。 |
    | [`std::is_nothrow_convertible`](support/type_traits/is_nothrow_convertible.md) | <span class="rank rank-rare">知ってるだけ</span> | 暗黙の変換が例外を投げないかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_nothrow_destructible`](support/type_traits/is_nothrow_destructible.md) | <span class="rank rank-rare">知ってるだけ</span> | デストラクタが例外を投げない型かを調べる。 |
    | [`std::is_nothrow_invocable`](support/type_traits/is_nothrow_invocable.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で、例外を投げずに呼び出せるかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::is_nothrow_swappable`](support/type_traits/is_nothrow_swappable.md) | <span class="rank rank-rare">知ってるだけ</span> | `swap` が例外を投げない型かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::is_null_pointer`](support/type_traits/is_null_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `std::nullptr_t` かを調べる。 |
    | [`std::is_object`](support/type_traits/is_object.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がオブジェクト型（関数・参照・`void` 以外）かを調べる。 |
    | [`std::is_pod`](support/type_traits/is_pod.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が POD（トリビアルかつ標準レイアウト）かを調べる。 |
    | [`std::is_pointer_interconvertible_base_of`](support/type_traits/is_pointer_interconvertible_base_of.md) | <span class="rank rank-rare">知ってるだけ</span> | 基底クラスのポインタと派生クラスのポインタを、相互に変換できるかを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_polymorphic`](support/type_traits/is_polymorphic.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が仮想関数を持つ（多態的な）かを調べる。 |
    | [`std::is_reference`](support/type_traits/is_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が参照（左辺値でも右辺値でも）かを調べる。 |
    | [`std::is_rvalue_reference`](support/type_traits/is_rvalue_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が右辺値参照かを調べる。 |
    | [`std::is_scalar`](support/type_traits/is_scalar.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がスカラー型（算術型・列挙・ポインタなど）かを調べる。 |
    | [`std::is_scoped_enum`](support/type_traits/is_scoped_enum.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がスコープ付き列挙型（`enum class`）かを調べる。 <span class="ver ver-23">C++23</span> |
    | [`std::is_standard_layout`](support/type_traits/is_standard_layout.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が標準レイアウト（C 言語と互換のメモリ配置）かを調べる。 |
    | [`std::is_swappable`](support/type_traits/is_swappable.md) | <span class="rank rank-rare">知ってるだけ</span> | `swap` で入れ替えられる型かを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::is_swappable_with`](support/type_traits/is_swappable_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型の値を、たがいに `swap` できるかを調べる。 <span class="ver ver-17">C++17</span> |
    | [`std::is_trivial`](support/type_traits/is_trivial.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がトリビアル（自明な構築・コピー・破棄ができる）かを調べる。 |
    | [`std::is_trivially_constructible`](support/type_traits/is_trivially_constructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 指定した引数で、自明に（特別な処理なしで）構築できる型かを調べる。 |
    | [`std::is_trivially_destructible`](support/type_traits/is_trivially_destructible.md) | <span class="rank rank-rare">知ってるだけ</span> | 破棄が自明（何もしなくてよい）な型かを調べる。 |
    | [`std::is_unbounded_array`](support/type_traits/is_unbounded_array.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が要素数の決まっていない配列かを調べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_union`](support/type_traits/is_union.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が共用体（union）かを調べる。 |
    | [`std::is_unsigned`](support/type_traits/is_unsigned.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が符号なしの算術型かを調べる。 |
    | [`std::is_void`](support/type_traits/is_void.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `void` かを調べる。 |
    | [`std::is_volatile`](support/type_traits/is_volatile.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が `volatile` 修飾されているかを調べる。 |
    | [`std::is_within_lifetime`](support/type_traits/is_within_lifetime.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタが指すオブジェクトが、いま寿命の中にあるかを調べる。 <span class="ver ver-26">C++26</span> |
    | [`std::make_signed`](support/type_traits/make_signed.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号なしの整数型を、同じ大きさの符号付きにする。 |
    | [`std::negation`](support/type_traits/negation.md) | <span class="rank rank-rare">知ってるだけ</span> | 型特性の結果を反転する。 <span class="ver ver-17">C++17</span> |
    | [`std::reference_constructs_from_temporary`](support/type_traits/reference_constructs_from_temporary.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照が、一時オブジェクトを作って束縛されるかを調べる。 <span class="ver ver-23">C++23</span> |
    | [`std::reference_converts_from_temporary`](support/type_traits/reference_converts_from_temporary.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照が、暗黙の変換で一時オブジェクトに束縛されるかを調べる。 <span class="ver ver-23">C++23</span> |
    | [`std::remove_all_extents`](support/type_traits/remove_all_extents.md) | <span class="rank rank-rare">知ってるだけ</span> | 配列の全部の次元を取り除く。 |
    | [`std::remove_const`](support/type_traits/remove_const.md) | <span class="rank rank-rare">知ってるだけ</span> | `const` を取り除く。 |
    | [`std::remove_cv`](support/type_traits/remove_cv.md) | <span class="rank rank-rare">知ってるだけ</span> | `const` と `volatile` を取り除く。 |
    | [`std::remove_extent`](support/type_traits/remove_extent.md) | <span class="rank rank-rare">知ってるだけ</span> | 配列の最初の次元を取り除く。 |
    | [`std::remove_pointer`](support/type_traits/remove_pointer.md) | <span class="rank rank-rare">知ってるだけ</span> | ポインタを取り除く。 |
    | [`std::remove_reference`](support/type_traits/remove_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | 参照を取り除く。 |
    | [`std::remove_volatile`](support/type_traits/remove_volatile.md) | <span class="rank rank-rare">知ってるだけ</span> | `volatile` を取り除く。 |
    | [`std::true_type`](support/type_traits/true_type.md) | <span class="rank rank-rare">知ってるだけ</span> | `true` を表すコンパイル時の定数の型。 |
    | [`std::type_identity`](support/type_traits/type_identity.md) | <span class="rank rank-rare">知ってるだけ</span> | 何もしない型変換（テンプレート引数の推論を止めるのに使う）。 <span class="ver ver-20">C++20</span> |
    | [`std::void_t`](support/type_traits/void_t.md) | <span class="rank rank-rare">知ってるだけ</span> | どんな型を渡しても `void` になる別名（検出イディオム用）。 <span class="ver ver-17">C++17</span> |

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
    | [`std::cmp_greater`](support/cmp_greater.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を、安全に `>` で比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::cmp_greater_equal`](support/cmp_greater_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を、安全に `>=` で比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::cmp_less_equal`](support/cmp_less_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を、安全に `<=` で比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::cmp_not_equal`](support/cmp_not_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | 符号付きと符号なしの整数を、安全に `!=` で比べる。 <span class="ver ver-20">C++20</span> |

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
    | [`std::bad_exception`](support/exceptions/bad_exception.md) | <span class="rank rank-rare">知ってるだけ</span> | 予期しない例外を表す例外クラス。 |
    | [`std::bad_typeid`](support/exceptions/bad_typeid.md) | <span class="rank rank-rare">知ってるだけ</span> | ヌルの多態型ポインタに typeid を使ったときの例外。 |
    | [`std::bad_weak_ptr`](support/exceptions/bad_weak_ptr.md) | <span class="rank rank-rare">知ってるだけ</span> | 期限切れの weak_ptr から shared_ptr を作ろうとしたときの例外。 |
    | [`std::current_exception`](support/exceptions/current_exception.md) | <span class="rank rank-rare">知ってるだけ</span> | いま処理中の例外を、exception_ptr として取り出す。 |
    | [`std::domain_error`](support/exceptions/domain_error.md) | <span class="rank rank-rare">知ってるだけ</span> | 関数の定義域の外の引数を表す例外。 |
    | [`std::get_terminate`](support/exceptions/get_terminate.md) | <span class="rank rank-rare">知ってるだけ</span> | 現在設定されている terminate ハンドラを取得する。 |
    | [`std::make_exception_ptr`](support/exceptions/make_exception_ptr.md) | <span class="rank rank-rare">知ってるだけ</span> | 例外オブジェクトから、exception_ptr を作る。 |
    | [`std::nested_exception`](support/exceptions/nested_exception.md) | <span class="rank rank-rare">知ってるだけ</span> | 別の例外を中に抱えられる例外の土台。 |
    | [`std::range_error`](support/exceptions/range_error.md) | <span class="rank rank-rare">知ってるだけ</span> | 計算の結果が、表せる範囲を超えたことを表す例外。 |
    | [`std::rethrow_exception`](support/exceptions/rethrow_exception.md) | <span class="rank rank-rare">知ってるだけ</span> | 保存した exception_ptr の例外を、もう一度投げる。 |
    | [`std::rethrow_if_nested`](support/exceptions/rethrow_if_nested.md) | <span class="rank rank-rare">知ってるだけ</span> | 包まれた例外があれば、それを取り出して投げ直す。 |
    | [`std::set_terminate`](support/exceptions/set_terminate.md) | <span class="rank rank-rare">知ってるだけ</span> | プログラムが異常終了する直前に呼ばれる関数を設定する。 |
    | [`std::throw_with_nested`](support/exceptions/throw_with_nested.md) | <span class="rank rank-rare">知ってるだけ</span> | いま処理中の例外を包んだ上で、新しい例外を投げる。 |
    | [`std::uncaught_exceptions`](support/exceptions/uncaught_exceptions.md) | <span class="rank rank-rare">知ってるだけ</span> | いま処理中（スタックを巻き戻している最中）の例外の数を返す。 <span class="ver ver-17">C++17</span> |
    | [`std::underflow_error`](support/exceptions/underflow_error.md) | <span class="rank rank-rare">知ってるだけ</span> | 計算の結果が小さすぎて表せないことを表す例外。 |

    **比較（<compare>）**

    | 名前 | 重要度 | 一言で |
    | --- | --- | --- |
    | [operator<=>（三方比較）](support/spaceship.md) | <span class="rank rank-often">よく使う</span> | 「小さい・等しい・大きい」を 1 回で調べる比較演算子。= default で全部の比較が生える。 <span class="ver ver-20">C++20</span> |
    | [`std::strong_ordering`](support/strong_ordering.md) | <span class="rank rank-sometimes">たまに</span> | 「等しいものは区別できない」比較結果（整数など）。less / equal / greater の 3 値。 <span class="ver ver-20">C++20</span> |
    | [`std::partial_ordering`](support/partial_ordering.md) | <span class="rank rank-sometimes">たまに</span> | 「比べられない」場合がある比較結果（NaN を含む小数）。 <span class="ver ver-20">C++20</span> |
    | [`std::weak_ordering`](support/weak_ordering.md) | <span class="rank rank-rare">知ってるだけ</span> | 「等しいが、区別はできる」場合を含む比較結果（大文字小文字を無視した比較など）。 <span class="ver ver-20">C++20</span> |
    | [`std::common_comparison_category`](support/common_comparison_category.md) | <span class="rank rank-rare">知ってるだけ</span> | 複数の順序型から、全部を含む共通の順序型を求める。 <span class="ver ver-20">C++20</span> |
    | [`std::compare_partial_order_fallback`](support/compare_partial_order_fallback.md) | <span class="rank rank-rare">知ってるだけ</span> | `<=>` が無い型も、`==` と `<` で `partial_ordering` として比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::compare_strong_order_fallback`](support/compare_strong_order_fallback.md) | <span class="rank rank-rare">知ってるだけ</span> | `<=>` が無い型も、`==` と `<` で `strong_ordering` として比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::compare_three_way`](support/compare_three_way.md) | <span class="rank rank-rare">知ってるだけ</span> | `<=>` を関数オブジェクトにしたもの。 <span class="ver ver-20">C++20</span> |
    | [`std::compare_three_way_result`](support/compare_three_way_result.md) | <span class="rank rank-rare">知ってるだけ</span> | `<=>` の戻り値の型を求める。 <span class="ver ver-20">C++20</span> |
    | [`std::compare_weak_order_fallback`](support/compare_weak_order_fallback.md) | <span class="rank rank-rare">知ってるだけ</span> | `<=>` が無い型も、`==` と `<` で `weak_ordering` として比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::is_eq`](support/is_eq.md) | <span class="rank rank-rare">知ってるだけ</span> | 順序型の結果が「等しい」かを `bool` で返す。 <span class="ver ver-20">C++20</span> |
    | [`std::is_gt`](support/is_gt.md) | <span class="rank rank-rare">知ってるだけ</span> | 順序型の結果が「大きい」かを `bool` で返す。 <span class="ver ver-20">C++20</span> |
    | [`std::is_gteq`](support/is_gteq.md) | <span class="rank rank-rare">知ってるだけ</span> | 順序型の結果が「以上」かを `bool` で返す。 <span class="ver ver-20">C++20</span> |
    | [`std::is_lt`](support/is_lt.md) | <span class="rank rank-rare">知ってるだけ</span> | 順序型の結果が「小さい」かを `bool` で返す。 <span class="ver ver-20">C++20</span> |
    | [`std::is_lteq`](support/is_lteq.md) | <span class="rank rank-rare">知ってるだけ</span> | 順序型の結果が「以下」かを `bool` で返す。 <span class="ver ver-20">C++20</span> |
    | [`std::is_neq`](support/is_neq.md) | <span class="rank rank-rare">知ってるだけ</span> | 順序型の結果が「等しくない」かを `bool` で返す。 <span class="ver ver-20">C++20</span> |
    | [`std::partial_order`](support/partial_order.md) | <span class="rank rank-rare">知ってるだけ</span> | 半順序（比べられない場合がある）で比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::strong_order`](support/strong_order.md) | <span class="rank rank-rare">知ってるだけ</span> | 強い順序（等しいものは区別できない）で比べる。 <span class="ver ver-20">C++20</span> |
    | [`std::three_way_comparable`](support/three_way_comparable.md) | <span class="rank rank-rare">知ってるだけ</span> | `<=>` と、`==`・`<` などで比べられる型を要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::three_way_comparable_with`](support/three_way_comparable_with.md) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの型を `<=>` で比べられることを要求する。 <span class="ver ver-20">C++20</span> |
    | [`std::weak_order`](support/weak_order.md) | <span class="rank rank-rare">知ってるだけ</span> | 弱い順序（等しいものを同一視する）で比べる。 <span class="ver ver-20">C++20</span> |

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
    | [`std::bit_and`](support/functional/bit_and.md) | <span class="rank rank-rare">知ってるだけ</span> | `a & b`（ビットごとの AND）を表す関数オブジェクト。 |
    | [`std::bit_not`](support/functional/bit_not.md) | <span class="rank rank-rare">知ってるだけ</span> | `~a`（ビット反転）を表す関数オブジェクト。 |
    | [`std::bit_or`](support/functional/bit_or.md) | <span class="rank rank-rare">知ってるだけ</span> | `a \| b`（ビットごとの OR）を表す関数オブジェクト。 |
    | [`std::bit_xor`](support/functional/bit_xor.md) | <span class="rank rank-rare">知ってるだけ</span> | `a ^ b`（ビットごとの XOR）を表す関数オブジェクト。 |
    | [`std::boyer_moore_horspool_searcher`](support/functional/boyer_moore_horspool_searcher.md) | <span class="rank rank-rare">知ってるだけ</span> | ボイヤー・ムーア・ホースプール法で部分列を探す検索のオブジェクト。 <span class="ver ver-17">C++17</span> |
    | [`std::boyer_moore_searcher`](support/functional/boyer_moore_searcher.md) | <span class="rank rank-rare">知ってるだけ</span> | 長い列の中から部分列を速く探す検索のオブジェクト（ボイヤー・ムーア法）。 <span class="ver ver-17">C++17</span> |
    | [`std::copyable_function`](support/functional/copyable_function.md) | <span class="rank rank-rare">知ってるだけ</span> | コピーできる、const や noexcept も指定できる関数のラッパー。 <span class="ver ver-26">C++26</span> |
    | [`std::default_searcher`](support/functional/default_searcher.md) | <span class="rank rank-rare">知ってるだけ</span> | `std::search` に渡せる、素朴な部分列検索のオブジェクト。 <span class="ver ver-17">C++17</span> |
    | [`std::divides`](support/functional/divides.md) | <span class="rank rank-rare">知ってるだけ</span> | `a / b` を表す関数オブジェクト。 |
    | [`std::function_ref`](support/functional/function_ref.md) | <span class="rank rank-rare">知ってるだけ</span> | 呼び出せるものを借りて参照するだけの、軽い関数ラッパー。 <span class="ver ver-26">C++26</span> |
    | [`std::greater_equal`](support/functional/greater_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | `a >= b` を表す関数オブジェクト。 |
    | [`std::invoke_r`](support/functional/invoke_r.md) | <span class="rank rank-rare">知ってるだけ</span> | 呼び出しの結果を、指定した戻り値の型に変換して返す。 <span class="ver ver-23">C++23</span> |
    | [`std::is_bind_expression`](support/functional/is_bind_expression.md) | <span class="rank rank-rare">知ってるだけ</span> | 型が bind の式かどうかを調べる型特性。 <span class="ver ver-17">C++17</span> |
    | [`std::is_placeholder`](support/functional/is_placeholder.md) | <span class="rank rank-rare">知ってるだけ</span> | 型がプレースホルダー（_1 など）か、何番かを調べる型特性。 <span class="ver ver-17">C++17</span> |
    | [`std::less_equal`](support/functional/less_equal.md) | <span class="rank rank-rare">知ってるだけ</span> | `a <= b` を表す関数オブジェクト。 |
    | [`std::logical_and`](support/functional/logical_and.md) | <span class="rank rank-rare">知ってるだけ</span> | `a && b` を表す関数オブジェクト。 |
    | [`std::logical_not`](support/functional/logical_not.md) | <span class="rank rank-rare">知ってるだけ</span> | `!a` を表す関数オブジェクト。 |
    | [`std::logical_or`](support/functional/logical_or.md) | <span class="rank rank-rare">知ってるだけ</span> | `a \|\| b` を表す関数オブジェクト。 |
    | [`std::minus`](support/functional/minus.md) | <span class="rank rank-rare">知ってるだけ</span> | `a - b` を表す関数オブジェクト。 |
    | [`std::modulus`](support/functional/modulus.md) | <span class="rank rank-rare">知ってるだけ</span> | `a % b`（余り）を表す関数オブジェクト。 |
    | [`std::negate`](support/functional/negate.md) | <span class="rank rank-rare">知ってるだけ</span> | `-a`（符号の反転）を表す関数オブジェクト。 |
    | [`std::not_equal_to`](support/functional/not_equal_to.md) | <span class="rank rank-rare">知ってるだけ</span> | `a != b` を表す関数オブジェクト。 |
    | [`std::placeholders`](support/functional/placeholders.md) | <span class="rank rank-rare">知ってるだけ</span> | bind の引数の位置を表す _1, _2, … の名前空間。 |
    | [`std::unwrap_ref_decay`](support/functional/unwrap_ref_decay.md) | <span class="rank rank-rare">知ってるだけ</span> | decay してから、reference_wrapper を参照に戻す型変換。 <span class="ver ver-20">C++20</span> |
    | [`std::unwrap_reference`](support/functional/unwrap_reference.md) | <span class="rank rank-rare">知ってるだけ</span> | reference_wrapper を、ふつうの参照の型に戻す型変換。 <span class="ver ver-20">C++20</span> |

STL を読むための前提知識は [基礎](../basics/index.md) にまとめています。
