"""標準ライブラリの名前の一覧と、docs/stl のページを突き合わせて、ページが無いものを出す（作業用）。

使い方: python tools/stl/inventory.py [ヘッダ名 ...]
ページがある = ファイル名・title・見出し・{#id} のどれかにその名前がある。
"""
import glob
import re
import sys

INV = {
"algorithm": "all_of any_of none_of for_each for_each_n count count_if mismatch find find_if find_if_not find_end find_first_of adjacent_find search search_n copy copy_if copy_n copy_backward move move_backward fill fill_n transform generate generate_n remove remove_if remove_copy remove_copy_if replace replace_if replace_copy replace_copy_if swap swap_ranges iter_swap reverse reverse_copy rotate rotate_copy shift_left shift_right shuffle sample unique unique_copy is_partitioned partition partition_copy stable_partition partition_point is_sorted is_sorted_until sort partial_sort partial_sort_copy stable_sort nth_element lower_bound upper_bound binary_search equal_range merge inplace_merge includes set_difference set_intersection set_symmetric_difference set_union is_heap is_heap_until make_heap push_heap pop_heap sort_heap max max_element min min_element minmax minmax_element clamp equal lexicographical_compare lexicographical_compare_three_way is_permutation next_permutation prev_permutation contains contains_subrange starts_with ends_with find_last find_last_if find_last_if_not fold_left fold_right fold_left_first fold_right_last fold_left_with_iter fold_left_first_with_iter",
"numeric": "iota accumulate reduce transform_reduce inner_product adjacent_difference partial_sum inclusive_scan exclusive_scan transform_inclusive_scan transform_exclusive_scan gcd lcm midpoint add_sat sub_sat mul_sat div_sat saturate_cast",
"memory": "unique_ptr shared_ptr weak_ptr make_unique make_shared make_unique_for_overwrite make_shared_for_overwrite allocate_shared enable_shared_from_this bad_weak_ptr owner_less owner_hash owner_equal default_delete allocator allocator_traits allocator_arg uses_allocator make_obj_using_allocator pointer_traits to_address addressof align assume_aligned get_deleter static_pointer_cast dynamic_pointer_cast const_pointer_cast reinterpret_pointer_cast construct_at destroy destroy_at destroy_n uninitialized_copy uninitialized_copy_n uninitialized_fill uninitialized_fill_n uninitialized_move uninitialized_move_n uninitialized_default_construct uninitialized_default_construct_n uninitialized_value_construct uninitialized_value_construct_n out_ptr inout_ptr start_lifetime_as",
"memory_resource": "memory_resource polymorphic_allocator monotonic_buffer_resource unsynchronized_pool_resource synchronized_pool_resource pool_options new_delete_resource null_memory_resource get_default_resource set_default_resource",
"scoped_allocator": "scoped_allocator_adaptor",
"utility": "pair make_pair swap exchange forward forward_like move move_if_noexcept declval as_const to_underlying unreachable cmp_equal cmp_not_equal cmp_less cmp_greater cmp_less_equal cmp_greater_equal in_range integer_sequence index_sequence make_integer_sequence make_index_sequence index_sequence_for piecewise_construct in_place in_place_type in_place_index tuple_size tuple_element",
"tuple": "tuple make_tuple tie forward_as_tuple tuple_cat apply make_from_tuple ignore get",
"optional": "optional nullopt bad_optional_access make_optional",
"variant": "variant visit holds_alternative get_if variant_size variant_alternative variant_npos bad_variant_access monostate",
"any": "any any_cast make_any bad_any_cast",
"expected": "expected unexpected unexpect bad_expected_access",
"bitset": "bitset",
"functional": "function move_only_function copyable_function function_ref bind bind_front bind_back placeholders is_bind_expression is_placeholder ref cref reference_wrapper invoke invoke_r not_fn mem_fn plus minus multiplies divides modulus negate equal_to not_equal_to greater less greater_equal less_equal logical_and logical_or logical_not bit_and bit_or bit_xor bit_not identity hash default_searcher boyer_moore_searcher boyer_moore_horspool_searcher bad_function_call unwrap_reference unwrap_ref_decay",
"chrono": "duration time_point system_clock steady_clock high_resolution_clock utc_clock tai_clock gps_clock file_clock clock_cast nanoseconds microseconds milliseconds seconds minutes hours days weeks months years duration_cast time_point_cast floor ceil round abs treat_as_floating_point duration_values day month year weekday weekday_indexed weekday_last month_day month_day_last month_weekday month_weekday_last year_month year_month_day year_month_day_last year_month_weekday year_month_weekday_last hh_mm_ss is_am is_pm make12 make24 sys_time sys_seconds sys_days local_time local_seconds local_days utc_time time_zone zoned_time time_zone_link tzdb tzdb_list get_tzdb locate_zone current_zone sys_info local_info nonexistent_local_time ambiguous_local_time leap_second get_leap_second_info file_time last_spec parse from_stream to_stream",
"ctime": "time clock difftime mktime strftime localtime gmtime asctime ctime timespec timespec_get tm clock_t time_t CLOCKS_PER_SEC",
"random": "random_device mt19937 mt19937_64 minstd_rand0 minstd_rand ranlux24 ranlux48 ranlux24_base ranlux48_base knuth_b default_random_engine linear_congruential_engine mersenne_twister_engine subtract_with_carry_engine discard_block_engine independent_bits_engine shuffle_order_engine seed_seq uniform_int_distribution uniform_real_distribution bernoulli_distribution binomial_distribution negative_binomial_distribution geometric_distribution poisson_distribution exponential_distribution gamma_distribution weibull_distribution extreme_value_distribution normal_distribution lognormal_distribution chi_squared_distribution cauchy_distribution fisher_f_distribution student_t_distribution discrete_distribution piecewise_constant_distribution piecewise_linear_distribution generate_canonical",
"ratio": "ratio ratio_add ratio_subtract ratio_multiply ratio_divide ratio_equal ratio_not_equal ratio_less ratio_less_equal ratio_greater ratio_greater_equal nano micro milli centi deci deca hecto kilo mega giga tera peta exa",
"complex": "complex real imag abs arg norm conj proj polar",
"string": "basic_string string wstring u8string u16string u32string char_traits stoi stol stoll stoul stoull stof stod stold to_string to_wstring getline",
"string_view": "basic_string_view string_view wstring_view u8string_view u16string_view u32string_view",
"cstring": "memcpy memmove memset memcmp memchr strcpy strncpy strcat strncat strcmp strncmp strchr strrchr strstr strlen strspn strcspn strpbrk strtok strcoll strxfrm strerror",
"cstdlib": "abs labs llabs div ldiv lldiv rand srand atoi atol atoll atof strtol strtoll strtoul strtoull strtof strtod strtold exit quick_exit abort atexit at_quick_exit getenv system malloc calloc realloc free aligned_alloc qsort bsearch EXIT_SUCCESS EXIT_FAILURE RAND_MAX mblen mbtowc wctomb mbstowcs wcstombs",
"cctype": "isalnum isalpha islower isupper isdigit isxdigit iscntrl isgraph isspace isblank isprint ispunct tolower toupper",
"cwctype": "iswalnum iswalpha iswlower iswupper iswdigit iswxdigit iswcntrl iswgraph iswspace iswblank iswprint iswpunct towlower towupper",
"cuchar": "mbrtoc8 c8rtomb mbrtoc16 c16rtomb mbrtoc32 c32rtomb",
"cmath": "abs fabs fmod remainder remquo fma fmax fmin fdim nan exp exp2 expm1 log log10 log2 log1p pow sqrt cbrt hypot sin cos tan asin acos atan atan2 sinh cosh tanh asinh acosh atanh erf erfc tgamma lgamma ceil floor trunc round lround llround nearbyint rint lrint llrint frexp ldexp modf scalbn scalbln ilogb logb nextafter nexttoward copysign fpclassify isfinite isinf isnan isnormal signbit isgreater isgreaterequal isless islessequal islessgreater isunordered lerp assoc_laguerre assoc_legendre beta comp_ellint_1 comp_ellint_2 comp_ellint_3 cyl_bessel_i cyl_bessel_j cyl_bessel_k cyl_neumann ellint_1 ellint_2 ellint_3 expint hermite laguerre legendre riemann_zeta sph_bessel sph_legendre sph_neumann HUGE_VAL INFINITY NAN math_errhandling",
"cfenv": "feclearexcept fetestexcept feraiseexcept fegetexceptflag fesetexceptflag fegetround fesetround fegetenv fesetenv feholdexcept feupdateenv",
"bit": "bit_cast byteswap has_single_bit bit_ceil bit_floor bit_width rotl rotr countl_zero countl_one countr_zero countr_one popcount endian",
"limits": "numeric_limits float_round_style float_denorm_style",
"climits": "CHAR_BIT INT_MAX INT_MIN UINT_MAX LONG_MAX LLONG_MAX SIZE_MAX CHAR_MAX SCHAR_MAX SHRT_MAX",
"cfloat": "FLT_EPSILON DBL_EPSILON FLT_MAX DBL_MAX FLT_MIN DBL_MIN FLT_DIG DBL_DIG FLT_MANT_DIG DBL_MANT_DIG FLT_EVAL_METHOD DECIMAL_DIG FLT_ROUNDS FLT_RADIX",
"cstdint": "int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t int_fast8_t int_least8_t intmax_t intptr_t uintmax_t uintptr_t",
"cstddef": "size_t ptrdiff_t nullptr_t max_align_t byte offsetof to_integer",
"numbers": "e log2e log10e pi inv_pi inv_sqrtpi ln2 ln10 sqrt2 sqrt3 inv_sqrt3 egamma phi",
"stdfloat": "float16_t float32_t float64_t float128_t bfloat16_t",
"cinttypes": "imaxabs imaxdiv strtoimax strtoumax",
"iterator": "iterator_traits input_iterator_tag output_iterator_tag forward_iterator_tag bidirectional_iterator_tag random_access_iterator_tag contiguous_iterator_tag advance distance next prev begin end cbegin cend rbegin rend crbegin crend size ssize empty data reverse_iterator make_reverse_iterator move_iterator make_move_iterator move_sentinel back_insert_iterator front_insert_iterator insert_iterator back_inserter front_inserter inserter istream_iterator ostream_iterator istreambuf_iterator ostreambuf_iterator counted_iterator default_sentinel unreachable_sentinel common_iterator basic_const_iterator make_const_iterator projected iter_value_t iter_reference_t iter_difference_t iter_move",
"ranges": "range viewable_range borrowed_range sized_range contiguous_range common_range input_range output_range forward_range bidirectional_range random_access_range view range_value_t range_reference_t range_difference_t range_size_t iterator_t sentinel_t subrange dangling borrowed_iterator_t enable_borrowed_range enable_view view_interface ref_view owning_view all all_t empty_view single_view iota_view repeat_view istream_view basic_istream_view filter_view transform_view take_view take_while_view drop_view drop_while_view join_view join_with_view lazy_split_view split_view counted common_view reverse_view as_const_view as_rvalue_view elements_view keys_view values_view zip_view zip_transform_view adjacent_view adjacent_transform_view slide_view chunk_view chunk_by_view stride_view cartesian_product_view enumerate_view concat_view cache_latest_view to_input generator from_range to range_adaptor_closure",
"concepts": "same_as derived_from convertible_to common_reference_with common_with integral signed_integral unsigned_integral floating_point assignable_from swappable swappable_with destructible constructible_from default_initializable move_constructible copy_constructible movable copyable semiregular regular equality_comparable equality_comparable_with totally_ordered totally_ordered_with invocable regular_invocable predicate relation equivalence_relation strict_weak_order sortable permutable mergeable indirectly_comparable input_iterator output_iterator forward_iterator bidirectional_iterator random_access_iterator contiguous_iterator input_or_output_iterator sentinel_for sized_sentinel_for incrementable weakly_incrementable indirectly_readable indirectly_writable indirectly_movable indirectly_copyable indirectly_swappable indirectly_unary_invocable indirectly_regular_unary_invocable indirect_unary_predicate indirect_binary_predicate indirect_equivalence_relation indirect_strict_weak_order",
"type_traits": "integral_constant bool_constant true_type false_type is_void is_null_pointer is_integral is_floating_point is_array is_enum is_union is_class is_function is_pointer is_lvalue_reference is_rvalue_reference is_member_object_pointer is_member_function_pointer is_fundamental is_arithmetic is_scalar is_object is_compound is_reference is_member_pointer is_const is_volatile is_trivial is_trivially_copyable is_standard_layout is_pod is_empty is_polymorphic is_abstract is_final is_aggregate is_implicit_lifetime is_signed is_unsigned is_bounded_array is_unbounded_array is_scoped_enum is_constructible is_trivially_constructible is_nothrow_constructible is_default_constructible is_copy_constructible is_move_constructible is_assignable is_copy_assignable is_move_assignable is_destructible is_trivially_destructible is_nothrow_destructible is_swappable is_swappable_with is_nothrow_swappable has_virtual_destructor has_unique_object_representations is_layout_compatible is_pointer_interconvertible_base_of alignment_of rank extent is_same is_base_of is_convertible is_nothrow_convertible is_invocable is_invocable_r is_nothrow_invocable is_corresponding_member is_within_lifetime remove_cv remove_const remove_volatile add_cv add_const add_volatile remove_reference add_lvalue_reference add_rvalue_reference make_signed make_unsigned remove_extent remove_all_extents remove_pointer add_pointer aligned_storage aligned_union decay remove_cvref enable_if disjunction conjunction negation conditional common_type common_reference underlying_type invoke_result type_identity void_t is_constant_evaluated reference_constructs_from_temporary reference_converts_from_temporary",
"exception": "exception bad_exception nested_exception terminate set_terminate get_terminate current_exception rethrow_exception make_exception_ptr exception_ptr throw_with_nested rethrow_if_nested uncaught_exceptions",
"stdexcept": "logic_error invalid_argument domain_error length_error out_of_range runtime_error range_error overflow_error underflow_error",
"system_error": "error_code error_condition error_category system_error errc generic_category system_category make_error_code make_error_condition is_error_code_enum is_error_condition_enum io_errc iostream_category",
"new": "bad_alloc bad_array_new_length nothrow set_new_handler get_new_handler launder align_val_t hardware_destructive_interference_size hardware_constructive_interference_size",
"typeinfo": "type_info bad_cast bad_typeid typeid type_index",
"compare": "strong_ordering weak_ordering partial_ordering common_comparison_category compare_three_way compare_three_way_result three_way_comparable three_way_comparable_with strong_order weak_order partial_order compare_strong_order_fallback compare_weak_order_fallback compare_partial_order_fallback is_eq is_neq is_lt is_lteq is_gt is_gteq",
"misc": "initializer_list source_location stacktrace stacktrace_entry basic_stacktrace coroutine_handle coroutine_traits suspend_always suspend_never noop_coroutine contract_violation text_encoding generator",
"containers": "vector array deque list forward_list set multiset map multimap unordered_set unordered_multiset unordered_map unordered_multimap flat_map flat_multimap flat_set flat_multiset stack queue priority_queue span dynamic_extent as_bytes as_writable_bytes mdspan extents dextents layout_left layout_right layout_stride default_accessor aligned_accessor submdspan strided_slice full_extent valarray slice gslice mask_array indirect_array inplace_vector hive to_array",
"thread": "thread jthread sleep_for sleep_until yield get_id hardware_concurrency",
"mutex": "mutex recursive_mutex timed_mutex recursive_timed_mutex shared_mutex shared_timed_mutex lock_guard unique_lock scoped_lock shared_lock lock try_lock call_once once_flag defer_lock try_to_lock adopt_lock",
"condition_variable": "condition_variable condition_variable_any notify_all_at_thread_exit cv_status",
"future": "future shared_future promise packaged_task async launch future_status future_error future_errc",
"atomic": "atomic atomic_ref atomic_flag memory_order atomic_thread_fence atomic_signal_fence kill_dependency atomic_init atomic_is_lock_free atomic_wait atomic_notify_one atomic_notify_all atomic_fetch_add atomic_fetch_sub atomic_load_explicit atomic_store_explicit atomic_flag_test_and_set atomic_flag_clear",
"sync": "counting_semaphore binary_semaphore latch barrier stop_token stop_source stop_callback nostopstate never_stop_token",
"execution": "seq par par_unseq unseq is_execution_policy",
"rcu": "rcu_obj_base rcu_domain rcu_default_domain rcu_synchronize rcu_barrier rcu_retire hazard_pointer hazard_pointer_obj_base make_hazard_pointer",
"io_stream": "cin cout cerr clog wcin wcout wcerr wclog osyncstream syncbuf ios_base basic_ios ios fmtflags iostate openmode seekdir streamsize streampos streamoff fpos boolalpha showbase showpoint showpos skipws unitbuf uppercase dec hex oct fixed scientific hexfloat defaultfloat internal left right badbit eofbit failbit goodbit good eof fail bad rdstate clear setstate exceptions imbue getloc iword pword sync_with_stdio",
"istream_ostream": "istream basic_istream iostream basic_iostream wistream get getline read readsome ignore peek unget putback gcount tellg seekg sync ws ostream basic_ostream wostream put write flush endl ends tellp seekp emit_on_flush flush_emit",
"streambuf": "streambuf basic_streambuf filebuf stringbuf sgetc sputc rdbuf in_avail pubsync pubseekoff pubsetbuf",
"iomanip": "setw setprecision setfill setbase setiosflags resetiosflags get_money put_money get_time put_time quoted",
"sstream_fstream": "stringstream istringstream ostringstream wstringstream fstream ifstream ofstream wfstream spanstream ispanstream ospanstream spanbuf",
"cstdio": "printf fprintf sprintf snprintf vprintf vfprintf vsprintf vsnprintf scanf fscanf sscanf fopen freopen fclose fflush setbuf setvbuf fread fwrite fgetc getc getchar fgets fputc putc putchar fputs puts ungetc ftell fgetpos fseek fsetpos rewind clearerr feof ferror perror remove rename tmpfile tmpnam FILE stdin stdout stderr EOF BUFSIZ SEEK_SET",
"cwchar": "wprintf fwprintf swprintf wscanf fgetwc fputwc fgetws fputws wcslen wcscpy wcscmp wmemcpy wcstol btowc wctob mbrlen mbrtowc wcrtomb mbsrtowcs wcsrtombs mbstate_t wint_t WEOF",
"regex": "basic_regex regex wregex regex_match regex_search regex_replace regex_iterator sregex_iterator cregex_iterator regex_token_iterator sregex_token_iterator match_results smatch cmatch wsmatch wcmatch sub_match ssub_match csub_match regex_error regex_traits regex_constants syntax_option_type match_flag_type",
"locale": "locale facet codecvt ctype num_get num_put numpunct collate time_get time_put money_get money_put moneypunct messages use_facet has_facet codecvt_utf8 setlocale localeconv lconv",
"filesystem": "path directory_entry directory_iterator recursive_directory_iterator file_status file_type perms perm_options copy_options directory_options space_info file_time_type filesystem_error absolute canonical weakly_canonical relative proximate copy copy_file copy_symlink create_directory create_directories create_hard_link create_symlink create_directory_symlink current_path equivalent exists file_size hard_link_count last_write_time permissions read_symlink remove remove_all rename resize_file space status symlink_status temp_directory_path is_block_file is_character_file is_directory is_empty is_fifo is_other is_regular_file is_socket is_symlink status_known u8path",
"print_format": "print println vprint_unicode vprint_nonunicode format format_to format_to_n formatted_size vformat vformat_to formatter format_error format_parse_context format_context basic_format_string format_string wformat_string make_format_args make_wformat_args basic_format_arg basic_format_args visit_format_arg range_formatter format_kind range_format formattable runtime_format",
"charconv": "to_chars from_chars to_chars_result from_chars_result chars_format",
"c_misc": "assert errno signal raise sig_atomic_t va_list va_start va_arg va_end va_copy setjmp longjmp jmp_buf",
}


def collect():
    names = set()
    for f in glob.glob("docs/stl/**/*.md", recursive=True):
        t = open(f, encoding="utf8").read()
        names.add(f.replace("\\", "/").rsplit("/", 1)[1][:-3])
        for m in re.finditer(r"^#{1,4} (.*)$", t, re.M):
            for w in re.findall(r"[A-Za-z_][A-Za-z_0-9]*(?:::[A-Za-z_][A-Za-z_0-9]*)*", m.group(1)):
                names.add(w)
                names.add(w.split("::")[-1])
        m = re.search(r"^title:\s*(.*)$", t, re.M)
        if m:
            names.update(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", m.group(1)))
        names.update(re.findall(r"\{#([A-Za-z_0-9\-]+)", t))
    return names


if __name__ == "__main__":
    names = collect()
    only = sys.argv[1:]
    total = 0
    for hdr, syms in INV.items():
        if only and hdr not in only:
            continue
        miss = [s for s in syms.split() if s not in names]
        if miss:
            total += len(miss)
            print(f"[{hdr}] ({len(miss)}): {' '.join(miss)}")
    print("合計", total)
