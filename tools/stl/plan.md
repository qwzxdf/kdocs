# STL 拡充の計画（作業用。サイトには出ない）

C++23 の標準ライブラリで、まだページがないもの、1 ページに押し込まれているものの一覧。
`[x]` は完了、`[ ]` は未着手。上から順に進める。

## 方針

- 1 ページ = 1 つのクラス / 関数。`a / b` のタイトルは基本ダメ。
- 例外（1 ページにまとめてよいもの）:
  - 述語版・個数版が同じ名前の別形（`find` と `find_if`、`copy` と `copy_n`、`for_each` と `for_each_n`）は同じページの別見出しにする。
  - 形がまったく同じで名前だけが違う一族（`cmp_less` など 6 個、`less` / `greater` などの比較関数オブジェクト）は 1 ページ。
  - 定数・マクロの一覧（`<numbers>`、`<climits>`）。
- 各ページの先頭の front matter に `summary:`（一言で）と `group:`（index の小見出し）を書く。index は `tools/stl/gen_index.py` が作る。
- ページの形は `docs/_template.md`。関数は 1 つずつ見出し、引数表・戻り値・計算量・例。

## A. 1 ページにまとまっているものを分ける

### containers
- [ ] multimap / multiset → `multimap.md`、`multiset.md`

### algorithms
- [ ] any_of / all_of / none_of → 3 ページ
- [ ] min / max / minmax → 3 ページ
- [ ] min_element / max_element → `min_element`、`max_element`、`minmax_element`
- [ ] equal / mismatch → 2 ページ
- [ ] search / adjacent_find / is_sorted → `search`、`search_n`、`adjacent_find`、`is_sorted`、`is_sorted_until`
- [ ] copy / fill / iota など → `copy`、`move`、`fill`、`generate`、`iota`、`swap_ranges`、`transform`
- [ ] reverse / rotate → 2 ページ
- [ ] partial_sort / nth_element → 2 ページ
- [ ] shuffle / sample → 2 ページ
- [ ] lower_bound / binary_search → `lower_bound`、`upper_bound`、`binary_search`、`equal_range`
- [ ] accumulate / fold_left → `accumulate`、`fold_left`
- [ ] heap → `make_heap`、`push_heap`、`pop_heap`、`sort_heap`、`is_heap`
- [ ] set_operations → `set_union`、`set_intersection`、`set_difference`、`set_symmetric_difference`、`includes`、`merge`
- [ ] erase_if / erase → 2 ページ
- [ ] partition → `partition`、`stable_partition`、`partition_copy`、`partition_point`、`is_partitioned`
- [ ] views（24 見出し） → `algorithms/views/` に 1 view 1 ページ

### utilities
- [ ] pair / tuple → 2 ページ
- [ ] shared_ptr / weak_ptr → 2 ページ
- [ ] move / forward → 2 ページ
- [ ] format / print → `format`、`print`（`println` を含む）
- [ ] chrono（全部入り） → `utilities/chrono/` に分ける
- [ ] random（全部入り） → `utilities/random/` に分ける

### concurrency
- [ ] mutex / lock_guard → `mutex`、`lock_guard`、`unique_lock`、`scoped_lock`、`recursive_mutex`、`timed_mutex`、`shared_mutex`、`shared_lock`、`call_once`
- [ ] thread / jthread → 2 ページ + `stop_token`
- [ ] async / future → `async`、`future`、`promise`、`packaged_task`、`shared_future`
- [ ] セマフォ・ラッチ・バリア → `counting_semaphore`、`binary_semaphore`、`latch`、`barrier`
- [ ] atomic → `atomic`、`atomic_flag`、`atomic_ref`、`memory_order`

### io
- [ ] ifstream / ofstream → `ifstream`、`ofstream`、`fstream`
- [ ] cout / cin → `cout`、`cin`、`cerr`
- [ ] stringstream → `stringstream`、`istringstream`、`ostringstream`
- [ ] from_chars / to_chars → 2 ページ
- [ ] filesystem（33 見出し） → `io/filesystem/` に分ける
- [ ] regex → `regex`、`regex_match`、`regex_search`、`regex_replace`、`smatch`

### memory
- [ ] pmr → `memory_resource`、`monotonic_buffer_resource`、`unsynchronized_pool_resource`、`synchronized_pool_resource`、`polymorphic_allocator`、`new_delete_resource`
- [ ] cstring（14 見出し） → 関数ごと
- [ ] malloc / free → `malloc`、`free`、`calloc`、`realloc`、`aligned_alloc`
- [ ] new_delete → `new`、`delete`、配置 new、`construct_at`、`destroy_at`

### numeric
- [ ] cmath（27 見出し） → 関数ごと
- [ ] bit（14 見出し） → 関数ごと
- [ ] numeric（gcd / lcm / midpoint…） → 関数ごと

### support
- [ ] functional → `bind_front`、`bind`、`ref`、`invoke`、`not_fn`、`mem_fn`、`less` ほか
- [ ] iterator → `next`、`prev`、`advance`、`distance`、`back_inserter`、`front_inserter`、`inserter`、`reverse_iterator`、`move_iterator`、`istream_iterator`、`ostream_iterator`
- [ ] type_traits → テーマごと
- [ ] utility-misc → `to_underlying`、`cmp_less` ほか、`byte`、`exchange`、`as_const`、`unreachable`
- [ ] exceptions → 例外クラスごと
- [ ] source_location / stacktrace → 2 ページ

## B. まだページがないもの（新規）

### containers
- [ ] unordered_multimap、unordered_multiset、flat_multimap、flat_multiset
- [ ] vector<bool>、initializer_list、valarray、inplace_vector（C++26）
- [ ] basic_string（wstring / u8string など）、char_traits
- [ ] extents、layout_right、layout_left、layout_stride

### algorithms
- [ ] find_end、find_first_of、find_last、contains、starts_with、ends_with
- [ ] lexicographical_compare、is_permutation、next_permutation、prev_permutation
- [ ] copy_backward、move_backward、remove_copy、replace_copy、unique_copy、reverse_copy、rotate_copy、shift_left / shift_right
- [ ] partial_sort_copy、inplace_merge、is_heap_until
- [ ] 実行ポリシー（`std::execution`）

### utilities
- [ ] make_unique、make_shared、enable_shared_from_this、owner_less、out_ptr、inout_ptr
- [ ] unexpected、bad_expected_access、nullopt、in_place、monostate、visit、holds_alternative、get_if、get
- [ ] tuple まわり: make_tuple、tie、apply、make_from_tuple、tuple_cat、forward_as_tuple、make_pair、ignore、tuple_size / tuple_element、piecewise_construct
- [ ] swap、exchange、as_const、addressof、declval、identity、integer_sequence
- [ ] ratio、complex

### support
- [ ] compare（strong_ordering ほか、`<=>`）
- [ ] concepts（same_as ほか）
- [ ] コルーチン（coroutine_handle、suspend_always）
- [ ] type_info / typeid / type_index
- [ ] nullptr_t、size_t / ptrdiff_t、max_align_t、offsetof、launder
- [ ] system_error（error_code、error_condition、errc）
- [ ] `<new>`（bad_alloc、nothrow、set_new_handler）
- [ ] `<climits>` / `<cfloat>` のマクロ
- [ ] `<version>`（機能テストマクロ）
- [ ] `<stdfloat>`（float16_t など）
- [ ] reference_wrapper、move_only_function

### numeric
- [ ] reduce、transform_reduce、partial_sum、adjacent_difference、inclusive_scan、exclusive_scan、inner_product、add_sat など飽和演算
- [ ] `<cstdlib>`（abs、rand、atoi、strtol、exit、abort、getenv、qsort、bsearch、div）
- [ ] `<cctype>`（isalpha、isdigit、toupper など）
- [ ] `<cfenv>`

### io
- [ ] iomanip（setw、setprecision、setfill など）、ios_base とフラグ
- [ ] ostream、istream、streambuf、syncstream、spanstream
- [ ] `<cstdio>`（printf、fopen など）、`<ctime>`、locale
- [ ] `<cassert>`（assert）、`<cerrno>`、`<csignal>`、`<cstdarg>`、`<csetjmp>`

## C. index と周辺

- [ ] `tools/stl/gen_index.py` で `stl/index.md` を作り直す（件数・重要度・速さ・一言で）
- [ ] 各フォルダの `.pages`
- [ ] 他のページから分けたページへのリンク（アンカー）を直す
