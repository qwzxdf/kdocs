"""クラスのメンバ関数の一覧と、ページの見出しを突き合わせて、節が無いものを出す（作業用）。

使い方: python tools/stl/members.py [ページ名 ...]
"""
import re
import sys
from pathlib import Path

STL = Path(__file__).resolve().parents[2] / "docs" / "stl"

SEQ_COMMON = "begin cbegin end cend rbegin crbegin rend crend empty size max_size clear get_allocator swap"
SETLIKE = "insert emplace emplace_hint erase swap extract merge count find contains equal_range lower_bound upper_bound begin cbegin end cend rbegin crbegin rend crend empty size max_size clear key_comp value_comp get_allocator"
UNORD = "insert emplace emplace_hint erase swap extract merge count find contains equal_range begin cbegin end cend empty size max_size clear bucket_count max_bucket_count bucket_size bucket load_factor max_load_factor rehash reserve hash_function key_eq get_allocator"

MEMBERS = {
    "containers/vector.md": "assign assign_range at operator[] front back data reserve capacity shrink_to_fit insert insert_range emplace erase push_back emplace_back append_range pop_back resize operator= operator== operator<=> " + SEQ_COMMON,
    "containers/string.md": "assign assign_range at operator[] front back data c_str length reserve capacity shrink_to_fit insert insert_range erase push_back pop_back append append_range operator+= operator+ compare starts_with ends_with contains replace replace_with_range copy substr find rfind find_first_of find_last_of find_first_not_of find_last_not_of resize resize_and_overwrite operator= operator== operator<=> " + SEQ_COMMON,
    "containers/deque.md": "assign assign_range at operator[] front back shrink_to_fit insert insert_range emplace erase push_back emplace_back append_range pop_back push_front emplace_front prepend_range pop_front resize operator= operator== operator<=> " + SEQ_COMMON,
    "containers/list.md": "assign assign_range front back insert insert_range emplace erase push_back emplace_back append_range pop_back push_front emplace_front prepend_range pop_front resize splice remove remove_if reverse unique sort merge operator= operator== operator<=> " + SEQ_COMMON,
    "containers/forward_list.md": "assign assign_range front before_begin cbefore_begin insert_after emplace_after insert_range_after erase_after push_front emplace_front prepend_range pop_front resize splice_after remove remove_if reverse unique sort merge operator= operator== operator<=> begin cbegin end cend empty max_size clear get_allocator swap",
    "containers/array.md": "at operator[] front back data fill operator== operator<=> begin cbegin end cend rbegin crbegin rend crend empty size max_size swap",
    "containers/bitset.md": "set reset flip test all any none count size to_ulong to_ullong to_string operator[] operator&= operator|= operator^= operator~ operator<<= operator>>= operator<< operator>> operator& operator| operator^ operator==",
    "containers/map.md": "at operator[] insert insert_or_assign try_emplace " + SETLIKE + " operator= operator== operator<=>",
    "containers/multimap.md": SETLIKE + " operator= operator== operator<=>",
    "containers/set.md": SETLIKE + " operator= operator== operator<=>",
    "containers/multiset.md": SETLIKE + " operator= operator== operator<=>",
    "containers/unordered_map.md": "at operator[] insert_or_assign try_emplace " + UNORD + " operator= operator==",
    "containers/unordered_multimap.md": UNORD + " operator= operator==",
    "containers/unordered_set.md": UNORD + " operator= operator==",
    "containers/unordered_multiset.md": UNORD + " operator= operator==",
    "containers/stack.md": "top push emplace push_range pop empty size swap operator== operator<=>",
    "containers/queue.md": "front back push emplace push_range pop empty size swap operator== operator<=>",
    "containers/priority_queue.md": "top push emplace push_range pop empty size swap",
    "containers/span.md": "first last subspan size size_bytes empty operator[] at front back data begin cend rbegin rend end cbegin crbegin crend",
    "utilities/string_view.md": "remove_prefix remove_suffix swap copy substr compare starts_with ends_with contains find rfind find_first_of find_last_of find_first_not_of find_last_not_of data size length max_size empty operator[] at front back begin cbegin end cend rbegin crbegin rend crend operator== operator<=>",
    "utilities/optional.md": "operator_bool has_value value value_or operator* operator-> emplace reset swap and_then transform or_else operator= operator==",
    "utilities/variant.md": "index valueless_by_exception emplace swap operator= operator==",
    "utilities/expected.md": "has_value value error value_or error_or operator* operator-> operator_bool emplace swap and_then or_else transform transform_error operator= operator==",
    "utilities/unique_ptr.md": "get get_deleter release reset swap operator_bool operator* operator-> operator[] operator=",
    "utilities/shared_ptr.md": "get operator* operator-> operator[] use_count operator_bool reset swap owner_before owner_hash owner_equal operator=",
    "utilities/weak_ptr.md": "lock expired use_count reset swap owner_before owner_hash owner_equal operator=",
    "utilities/function.md": "operator() operator_bool swap target target_type assign operator=",
    "utilities/any.md": "has_value type reset emplace swap operator=",
    "utilities/pair.md": "swap operator= operator== operator<=>",
    "concurrency/thread.md": "join detach joinable get_id native_handle hardware_concurrency swap operator=",
    "concurrency/jthread.md": "join detach joinable get_id native_handle hardware_concurrency swap request_stop get_stop_source get_stop_token operator=",
    "concurrency/mutex.md": "lock try_lock unlock native_handle",
    "concurrency/atomic.md": "load store exchange compare_exchange_weak compare_exchange_strong fetch_add fetch_sub fetch_and fetch_or fetch_xor wait notify_one notify_all is_lock_free is_always_lock_free operator++ operator-- operator=",
    "concurrency/condition_variable.md": "wait wait_for wait_until notify_one notify_all native_handle",
    "concurrency/future.md": "get valid wait wait_for wait_until share",
    "concurrency/promise.md": "get_future set_value set_exception set_value_at_thread_exit set_exception_at_thread_exit swap",
    "concurrency/packaged_task.md": "operator() get_future valid make_ready_at_thread_exit reset swap",
    "concurrency/shared_future.md": "get valid wait wait_for wait_until",
    "concurrency/unique_lock.md": "lock try_lock try_lock_for try_lock_until unlock swap release mutex owns_lock operator_bool",
    "concurrency/shared_lock.md": "lock try_lock try_lock_for try_lock_until unlock swap release mutex owns_lock operator_bool",
    "concurrency/lock_guard.md": "",
    "concurrency/shared_mutex.md": "lock try_lock unlock lock_shared try_lock_shared unlock_shared native_handle",
    "concurrency/timed_mutex.md": "lock try_lock try_lock_for try_lock_until unlock native_handle",
    "concurrency/recursive_mutex.md": "lock try_lock unlock native_handle",
    "concurrency/counting_semaphore.md": "acquire try_acquire try_acquire_for try_acquire_until release max",
    "concurrency/binary_semaphore.md": "acquire try_acquire try_acquire_for try_acquire_until release max",
    "concurrency/latch.md": "count_down try_wait wait arrive_and_wait",
    "concurrency/barrier.md": "arrive wait arrive_and_wait arrive_and_drop max",
    "concurrency/atomic_flag.md": "test_and_set clear test wait notify_one notify_all",
    "concurrency/atomic_ref.md": "load store exchange compare_exchange_weak compare_exchange_strong fetch_add fetch_sub is_lock_free wait notify_one notify_all",
    "concurrency/stop_source.md": "request_stop stop_requested stop_possible get_token swap",
    "concurrency/stop_token.md": "stop_requested stop_possible swap",
    "io/ifstream.md": "open close is_open read get getline ignore peek unget putback gcount seekg tellg eof fail bad good rdbuf operator_bool readsome sync",
    "io/ofstream.md": "open close is_open write put flush seekp tellp rdbuf eof fail bad good operator_bool",
}

# 見出しとの対応のための表記ゆれ
ALIAS = {"operator_bool": ["operator bool", "explicit operator bool"], "operator[]": ["operator[]"], "std::get": ["std::get"]}


def headings(path):
    t = path.read_text(encoding="utf-8")
    out = []
    for h in re.findall(r"^#{3,4} (.*)$", t, re.M):
        h = re.sub(r"<span[^>]*>.*?</span>", "", h)
        h = re.sub(r"\{#.*", "", h).strip()
        out.append(h)
    ids = re.findall(r"\{#([\w\-]+)", t)
    return out, ids


def tokens(h):
    return re.findall(r"operator\s*(?:bool|T|\(\)|\[\]|<=>|->|[^\s\w]+)?|\w+", h)


def has(name, hs, ids):
    cands = ALIAS.get(name, [name])
    for h in hs:
        toks = [re.sub(r"\s+", " ", t) for t in tokens(h)]
        for c in cands:
            if c in toks:
                return True
    return name in ids or name.replace("operator", "").strip() in ids


if __name__ == "__main__":
    only = sys.argv[1:]
    total = 0
    for page, names in MEMBERS.items():
        if only and not any(o in page for o in only):
            continue
        p = STL / page
        if not p.exists():
            print("NO PAGE", page)
            continue
        hs, ids = headings(p)
        miss = [n for n in names.split() if not has(n, hs, ids)]
        if miss:
            total += len(miss)
            print(f"{page} ({len(miss)}): {' '.join(miss)}")
    print("合計", total)
