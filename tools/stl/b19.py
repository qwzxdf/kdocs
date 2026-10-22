"""バッチ 19: 既存のクラスのページに足りないメンバ関数の節を足す（members.py の一覧を元にする）。"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mk import STL, add_secs, fn  # noqa: E402
import members  # noqa: E402

IDS = {"operator=": "op_assign", "operator==": "op_eq", "operator<=>": "op_cmp", "operator[]": "op_index", "operator*": "op_deref", "operator->": "op_arrow",
       "operator()": "op_call", "operator_bool": "op_bool", "operator&=": "op_and_assign", "operator|=": "op_or_assign", "operator^=": "op_xor_assign",
       "operator<<=": "op_shl_assign", "operator>>=": "op_shr_assign", "operator++": "op_inc", "operator--": "op_dec", "operator+": "op_plus", "operator+=": "op_plus_assign",
       "operator~": "op_not", "operator<<": "op_shl", "operator>>": "op_shr", "operator&": "op_and", "operator|": "op_or", "operator^": "op_xor"}
HEAD = {"operator_bool": "explicit operator bool"}

# {C} = クラス名
GEN = {
    "begin": ("iterator begin() noexcept;\nconst_iterator begin() const noexcept;", "先頭の要素を指すイテレータ。空なら `end()` と同じ。", "定数"),
    "end": ("iterator end() noexcept;\nconst_iterator end() const noexcept;", "終端（最後の要素の次）を指すイテレータ。この位置は読めません。", "定数"),
    "cbegin": ("const_iterator cbegin() const noexcept;", "先頭の要素を指す const イテレータ。要素を書き換えられないので、読むだけの走査で使います。", "定数"),
    "cend": ("const_iterator cend() const noexcept;", "終端（最後の要素の次）を指す const イテレータ。", "定数"),
    "rbegin": ("reverse_iterator rbegin() noexcept;", "逆順の先頭（最後の要素）を指すイテレータ。後ろから前へ走査するときに使います。", "定数"),
    "crbegin": ("const_reverse_iterator crbegin() const noexcept;", "逆順の先頭（最後の要素）を指す const イテレータ。", "定数"),
    "rend": ("reverse_iterator rend() noexcept;", "逆順の終端（先頭の手前）を指すイテレータ。", "定数"),
    "crend": ("const_reverse_iterator crend() const noexcept;", "逆順の終端（先頭の手前）を指す const イテレータ。", "定数"),
    "empty": ("[[nodiscard]] bool empty() const noexcept;", "要素が 1 つもなければ `true`。`size() == 0` より意図が伝わります。", "定数"),
    "size": ("size_type size() const noexcept;", "要素の数。", "定数"),
    "clear": ("void clear() noexcept;", "全ての要素を削除します。メモリは返さないことがあります。", "O(要素数)"),
    "max_size": ("size_type max_size() const noexcept;", "理論上、入れられる最大の要素数。実装の上限で、実際にそれだけ確保できるとは限りません。", "定数"),
    "get_allocator": ("allocator_type get_allocator() const noexcept;", "使っているアロケータのコピー。", "定数"),
    "swap": ("void swap({C}& other) noexcept;", "中身を `other` と入れ替えます。要素のコピーやムーブはせず、内部のポインタを入れ替えるだけなので速いです。", "定数"),
    "operator=": ("{C}& operator=(const {C}& other);\n{C}& operator=({C}&& other) noexcept;", "コピー代入とムーブ代入。ムーブ代入は、中身の所有権を移すだけで、要素をコピーしません。", "コピーは O(要素数)、ムーブは定数"),
    "operator==": ("bool operator==(const {C}& a, const {C}& b);", "要素の数が同じで、各要素が順に等しければ `true`。", "O(要素数)"),
    "operator<=>": ("auto operator<=>(const {C}& a, const {C}& b);", "要素を先頭から順に比べる、辞書順の三方比較（C++20）。`<`・`>`・`<=`・`>=` も使えるようになります。", "O(要素数)"),
    "assign": ("void assign(size_type n, const T& value);\ntemplate <class InputIt>\nvoid assign(InputIt first, InputIt last);\nvoid assign(std::initializer_list<T> il);", "中身を全部捨てて、新しい要素で置き換えます。", "O(要素数)"),
    "assign_range": ("template <ranges::input_range R>\nvoid assign_range(R&& rg);", "範囲の要素で、中身を置き換えます（C++23）。", "O(要素数)"),
    "insert_range": ("template <ranges::input_range R>\niterator insert_range(const_iterator pos, R&& rg);", "範囲の要素を、`pos` の位置に挿入します（C++23）。", "O(挿入数 + 移動する要素数)"),
    "append_range": ("template <ranges::input_range R>\nvoid append_range(R&& rg);", "範囲の要素を、末尾に追加します（C++23）。`insert(end(), ...)` より意図が伝わります。", "O(追加数)"),
    "prepend_range": ("template <ranges::input_range R>\nvoid prepend_range(R&& rg);", "範囲の要素を、先頭に追加します（C++23）。", "O(追加数)"),
    "replace_with_range": ("template <ranges::input_range R>\nbasic_string& replace_with_range(const_iterator i1, const_iterator i2, R&& rg);", "指定した範囲を、別の範囲の要素で置き換えます（C++23）。", "O(長さ)"),
    "resize_and_overwrite": ("template <class Operation>\nvoid resize_and_overwrite(size_type n, Operation op);", "文字数を `n` にしてから、`op(buf, n)` に先頭のポインタを渡して書き込ませます。初期化の無駄を省けます（C++23）。C の API が書き込む領域を用意するのに向きます。", "O(n)"),
    "resize": ("void resize(size_type n);\nvoid resize(size_type n, const T& value);", "要素数を `n` にします。増えるぶんは、既定値（または `value`）で埋め、減るぶんは末尾から削除します。", "O(差)"),
    "emplace": ("template <class... Args>\niterator emplace(Args&&... args);", "引数から、その場で要素を作って挿入します。コピーやムーブを避けられます。", "O(log n)（順序つき）、平均 O(1)（unordered）"),
    "emplace_hint": ("template <class... Args>\niterator emplace_hint(const_iterator hint, Args&&... args);", "挿入される位置のヒント（直前の位置）を渡して、その場で要素を作ります。ヒントが合っていれば、償却定数で挿入できます。", "ヒントが正しければ償却定数"),
    "extract": ("node_type extract(const_iterator pos);\nnode_type extract(const key_type& key);", "要素をコピーやムーブなしで、ノードごと取り出します（C++17）。取り出したノードは、キーを書き換えたり、別のコンテナに `insert` したりできます。", "O(log n)（順序つき）、平均 O(1)（unordered）"),
    "merge": ("template <class C2>\nvoid merge({C}<..., C2>& source);", "別のコンテナの要素を、ノードごとこちらへ移します（C++17）。キーが重複するものは、移動元に残ります。", "O(移動する要素数 × log n)"),
    "key_comp": ("key_compare key_comp() const;", "キーの比較に使っている関数オブジェクトのコピー。", "定数"),
    "value_comp": ("value_compare value_comp() const;", "要素（キーと値のペア）の比較に使っている関数オブジェクトのコピー。", "定数"),
    "count": ("size_type count(const key_type& key) const;", "指定したキーの要素の数を返します。重複を許すコンテナで意味があります。", "O(log n + 個数)、平均 O(個数)（unordered）"),
    "find": ("iterator find(const key_type& key);\nconst_iterator find(const key_type& key) const;", "指定したキーの要素を探し、見つかればそのイテレータ、なければ `end()` を返します。", "O(log n)、平均 O(1)（unordered）"),
    "contains": ("bool contains(const key_type& key) const;", "指定したキーの要素があれば `true`（C++20）。`find(...) != end()` を短く書けます。", "O(log n)、平均 O(1)（unordered）"),
    "equal_range": ("std::pair<iterator, iterator> equal_range(const key_type& key);", "指定したキーに等しい要素の範囲（`[first, last)`）を返します。", "O(log n)、平均 O(個数)（unordered）"),
    "swap_c": ("", "", ""),
    "bucket_count": ("size_type bucket_count() const noexcept;", "バケット（要素を振り分ける箱）の数。", "定数"),
    "max_bucket_count": ("size_type max_bucket_count() const noexcept;", "バケットの数の上限。", "定数"),
    "bucket_size": ("size_type bucket_size(size_type n) const;", "n 番目のバケットに入っている要素の数。偏りの確認に使います。", "O(要素数)"),
    "bucket": ("size_type bucket(const key_type& key) const;", "キーが入るバケットの番号。", "定数"),
    "load_factor": ("float load_factor() const noexcept;", "平均の負荷（要素数 ÷ バケット数）。1 に近づくと、衝突が増えて遅くなります。", "定数"),
    "max_load_factor": ("float max_load_factor() const noexcept;\nvoid max_load_factor(float ml);", "負荷の上限。これを超えると、自動でバケットを増やします（リハッシュ）。", "定数"),
    "rehash": ("void rehash(size_type count);", "バケットの数を `count` 以上にして、全ての要素を再配置します。", "平均 O(要素数)"),
    "reserve": ("void reserve(size_type count);", "`count` 個の要素が入っても、リハッシュが起きないようにバケットを用意します。", "平均 O(要素数)"),
    "hash_function": ("hasher hash_function() const;", "キーのハッシュ値を作る関数オブジェクトのコピー。", "定数"),
    "key_eq": ("key_equal key_eq() const;", "キーの等しさを判定する関数オブジェクトのコピー。", "定数"),
    "cbefore_begin": ("const_iterator cbefore_begin() const noexcept;", "先頭の手前を指す const イテレータ。`insert_after` の基点になります。", "定数"),
    "insert_range_after": ("template <ranges::input_range R>\niterator insert_range_after(const_iterator pos, R&& rg);", "範囲の要素を、`pos` の次に挿入します（C++23）。", "O(挿入数)"),
    "unique": ("size_type unique();\ntemplate <class BinaryPred>\nsize_type unique(BinaryPred pred);", "隣り合う同じ要素を 1 つにまとめます（整列済みのリストで重複を消す）。", "O(要素数)"),
    "operator&=": ("{C}& operator&=(const {C}& rhs) noexcept;", "ビットごとの AND を、自分に代入します。", "O(ビット数 / ワード長)"),
    "operator|=": ("{C}& operator|=(const {C}& rhs) noexcept;", "ビットごとの OR を、自分に代入します。", "O(ビット数 / ワード長)"),
    "operator^=": ("{C}& operator^=(const {C}& rhs) noexcept;", "ビットごとの XOR を、自分に代入します。", "O(ビット数 / ワード長)"),
    "operator<<=": ("{C}& operator<<=(size_t pos) noexcept;", "`pos` ビット左へずらして、自分に代入します。あふれたビットは捨てられます。", "O(ビット数 / ワード長)"),
    "operator>>=": ("{C}& operator>>=(size_t pos) noexcept;", "`pos` ビット右へずらして、自分に代入します。", "O(ビット数 / ワード長)"),
    "length": ("size_type length() const noexcept;", "文字数（`size()` と同じ）。", "定数"),
    "compare": ("int compare(basic_string_view sv) const noexcept;", "辞書順で比べて、小さければ負、等しければ 0、大きければ正を返します。", "O(長さ)"),
    "find_last_of": ("size_type find_last_of(basic_string_view chars, size_type pos = npos) const noexcept;", "`chars` のどれかの文字が、最後に現れる位置を探します。なければ `npos`。", "O(長さ × chars の長さ)"),
    "find_last_not_of": ("size_type find_last_not_of(basic_string_view chars, size_type pos = npos) const noexcept;", "`chars` に含まれない文字が、最後に現れる位置を探します。末尾の空白を取り除く位置を探すときに便利です。", "O(長さ × chars の長さ)"),
    "native_handle": ("native_handle_type native_handle();", "OS 固有のハンドル（`pthread_t` や `HANDLE`）を返します。標準にない機能（優先度の設定など）を使うときの出口です。", "定数"),
}

# 呼び出し順の都合で、個別の説明（クラスごと）
SPEC = {
    ("containers/vector.md", "operator[]"): None,
    ("concurrency/thread.md", "get_id"): ("std::thread::id get_id() const noexcept;", "スレッドの ID。実行中でなければ（`joinable()` が偽なら）、どのスレッドも指さない既定の ID を返します。ログに出して、どのスレッドか確かめるのに使えます。", "定数"),
    ("concurrency/thread.md", "swap"): ("void swap(thread& other) noexcept;", "2 つの `thread` オブジェクトが管理するスレッドを入れ替えます。", "定数"),
    ("concurrency/thread.md", "operator="): ("thread& operator=(thread&& other) noexcept;", "ムーブ代入。コピーはできません。自分が実行中のスレッドを持っている（`joinable()` が真）状態で代入すると、`std::terminate` になります。", "定数"),
    ("concurrency/jthread.md", "detach"): ("void detach();", "スレッドを切り離して、独立に動かします。`join` も `request_stop` もできなくなるので、`jthread` では普通は使いません。", "定数"),
    ("concurrency/jthread.md", "joinable"): ("[[nodiscard]] bool joinable() const noexcept;", "スレッドが実行中（まだ `join` されていない）なら `true`。", "定数"),
    ("concurrency/jthread.md", "get_id"): ("id get_id() const noexcept;", "スレッドの ID。", "定数"),
    ("concurrency/jthread.md", "hardware_concurrency"): ("static unsigned hardware_concurrency() noexcept;", "同時に動かせるスレッド数の目安（CPU のコア数など）。分からなければ 0 を返します。", "定数"),
    ("concurrency/jthread.md", "swap"): ("void swap(jthread& other) noexcept;", "2 つの `jthread` を入れ替えます。", "定数"),
    ("concurrency/jthread.md", "request_stop"): ("bool request_stop() noexcept;", "スレッドに、停止を要求します。スレッド関数が受け取った `stop_token` で確かめて、自分で終了します。デストラクタでも、自動で呼ばれます。", "定数"),
    ("concurrency/jthread.md", "get_stop_source"): ("stop_source get_stop_source() noexcept;", "このスレッドの停止要求を管理する `stop_source` を返します。", "定数"),
    ("concurrency/jthread.md", "get_stop_token"): ("stop_token get_stop_token() const noexcept;", "このスレッドの停止要求を確認する `stop_token` を返します。", "定数"),
    ("concurrency/jthread.md", "operator="): ("jthread& operator=(jthread&& other) noexcept;", "ムーブ代入。自分が実行中なら、先に停止を要求して、`join` します。", "スレッドの終了まで待つ"),
    ("concurrency/atomic.md", "is_always_lock_free"): ("static constexpr bool is_always_lock_free;", "この型の `atomic` が、常にロックなしで動くなら `true`（コンパイル時の定数）。`is_lock_free()` は実行時に調べますが、こちらは型で決まります。", "コンパイル時"),
    ("concurrency/future.md", "wait_until"): ("template <class Clock, class Duration>\nfuture_status wait_until(const std::chrono::time_point<Clock, Duration>& abs_time) const;", "指定した時刻まで、結果が出るのを待ちます。結果が出たか、時間切れかを `future_status` で返します。", "最大で指定時刻まで"),
    ("concurrency/future.md", "share"): ("std::shared_future<T> share() noexcept;", "`future` を `shared_future` に変換します。変換後の元の `future` は無効（`valid()` が偽）になります。結果を複数のスレッドで読みたいときに使います。", "定数"),
    ("concurrency/promise.md", "get_future"): ("std::future<T> get_future();", "この `promise` と結びついた `future` を返します。**1 回だけ**呼べます。2 回呼ぶと `future_error` です。", "定数"),
    ("concurrency/promise.md", "set_value"): ("void set_value(const T& value);\nvoid set_value(T&& value);", "結果の値を設定します。待っている `future::get()` が、これで戻ります。2 回設定すると `future_error` です。", "定数"),
    ("concurrency/promise.md", "set_exception"): ("void set_exception(std::exception_ptr p);", "値の代わりに、例外を設定します。`future::get()` がこの例外を投げ直します。", "定数"),
    ("concurrency/promise.md", "set_value_at_thread_exit"): ("void set_value_at_thread_exit(const T& value);", "値を設定しますが、結果が見えるようになるのは、スレッドが完全に終わってからです（`thread_local` の後始末のあと）。", "定数"),
    ("concurrency/promise.md", "set_exception_at_thread_exit"): ("void set_exception_at_thread_exit(std::exception_ptr p);", "例外を設定しますが、結果が見えるようになるのは、スレッドが完全に終わってからです。", "定数"),
    ("concurrency/promise.md", "swap"): ("void swap(promise& other) noexcept;", "2 つの `promise` を入れ替えます。", "定数"),
    ("concurrency/packaged_task.md", "operator()"): ("void operator()(Args... args);", "関数を呼んで、結果を `future` に設定します。例外が出たら、それが `future` に設定されます。", "関数による"),
    ("concurrency/packaged_task.md", "get_future"): ("std::future<R> get_future();", "結果を受け取る `future` を返します。**1 回だけ**呼べます。", "定数"),
    ("concurrency/packaged_task.md", "valid"): ("bool valid() const noexcept;", "関数を持っていれば `true`。", "定数"),
    ("concurrency/packaged_task.md", "make_ready_at_thread_exit"): ("void make_ready_at_thread_exit(Args... args);", "関数を呼びますが、結果が見えるようになるのは、スレッドが完全に終わってからです。", "関数による"),
    ("concurrency/packaged_task.md", "reset"): ("void reset();", "状態を捨てて、同じ関数で新しい状態を作ります。もう一度 `operator()` を呼べるようになります。", "定数"),
    ("concurrency/packaged_task.md", "swap"): ("void swap(packaged_task& other) noexcept;", "2 つの `packaged_task` を入れ替えます。", "定数"),
    ("concurrency/shared_future.md", "get"): ("const T& get() const;", "結果への参照を返します。結果が出るまで待ち、**何回呼んでも**同じ結果を返します（`future::get` は 1 回だけ）。", "結果が出るまで待つ"),
    ("concurrency/shared_future.md", "valid"): ("bool valid() const noexcept;", "結果を受け取れる状態なら `true`。", "定数"),
    ("concurrency/shared_future.md", "wait"): ("void wait() const;", "結果が出るまで待ちます。", "結果が出るまで待つ"),
    ("concurrency/shared_future.md", "wait_for"): ("template <class Rep, class Period>\nfuture_status wait_for(const std::chrono::duration<Rep, Period>& rel_time) const;", "指定した時間まで、結果が出るのを待ちます。", "最大で指定時間"),
    ("concurrency/shared_future.md", "wait_until"): ("template <class Clock, class Duration>\nfuture_status wait_until(const std::chrono::time_point<Clock, Duration>& abs_time) const;", "指定した時刻まで、結果が出るのを待ちます。", "最大で指定時刻まで"),
    ("concurrency/mutex.md", "native_handle"): None,
    ("concurrency/binary_semaphore.md", "acquire"): ("void acquire();", "カウンタが 0 より大きくなるまで待ち、1 減らします。", "待つ時間による"),
    ("concurrency/binary_semaphore.md", "try_acquire"): ("bool try_acquire() noexcept;", "待たずに、取得を試みます。取れたら `true`。", "定数"),
    ("concurrency/binary_semaphore.md", "try_acquire_for"): ("template <class Rep, class Period>\nbool try_acquire_for(const std::chrono::duration<Rep, Period>& rel_time);", "指定した時間まで待って、取得を試みます。取れたら `true`。", "最大で指定時間"),
    ("concurrency/binary_semaphore.md", "try_acquire_until"): ("template <class Clock, class Duration>\nbool try_acquire_until(const std::chrono::time_point<Clock, Duration>& abs_time);", "指定した時刻まで待って、取得を試みます。取れたら `true`。", "最大で指定時刻まで"),
    ("concurrency/binary_semaphore.md", "release"): ("void release(ptrdiff_t update = 1);", "カウンタを増やして、待っているスレッドを起こします。", "定数"),
    ("concurrency/binary_semaphore.md", "max"): ("static constexpr ptrdiff_t max() noexcept;", "カウンタの最大値（`binary_semaphore` では 1）。", "定数"),
    ("concurrency/counting_semaphore.md", "try_acquire_for"): ("template <class Rep, class Period>\nbool try_acquire_for(const std::chrono::duration<Rep, Period>& rel_time);", "指定した時間まで待って、取得を試みます。取れたら `true`。", "最大で指定時間"),
    ("concurrency/counting_semaphore.md", "try_acquire_until"): ("template <class Clock, class Duration>\nbool try_acquire_until(const std::chrono::time_point<Clock, Duration>& abs_time);", "指定した時刻まで待って、取得を試みます。取れたら `true`。", "最大で指定時刻まで"),
    ("concurrency/counting_semaphore.md", "max"): ("static constexpr ptrdiff_t max() noexcept;", "カウンタの最大値。", "定数"),
    ("concurrency/latch.md", "try_wait"): ("bool try_wait() const noexcept;", "待たずに、カウンタが 0 になっているか調べます。0 なら `true`。", "定数"),
    ("concurrency/barrier.md", "max"): ("static constexpr ptrdiff_t max() noexcept;", "カウンタの最大値。", "定数"),
    ("concurrency/atomic_flag.md", "test_and_set"): ("bool test_and_set(std::memory_order order = std::memory_order_seq_cst) noexcept;", "旗を立てて、立てる前の状態を返します。スピンロックの基本部品です。", "定数"),
    ("concurrency/atomic_flag.md", "clear"): ("void clear(std::memory_order order = std::memory_order_seq_cst) noexcept;", "旗を下ろします。", "定数"),
    ("concurrency/atomic_flag.md", "test"): ("bool test(std::memory_order order = std::memory_order_seq_cst) const noexcept;", "旗が立っているかを調べます（旗は変えません）。C++20。", "定数"),
    ("concurrency/atomic_flag.md", "wait"): ("void wait(bool old, std::memory_order order = std::memory_order_seq_cst) const noexcept;", "旗が `old` と等しい間、待ちます。C++20。", "待つ時間による"),
    ("concurrency/atomic_flag.md", "notify_one"): ("void notify_one() noexcept;", "`wait` で待っているスレッドを 1 つ起こします。C++20。", "定数"),
    ("concurrency/atomic_flag.md", "notify_all"): ("void notify_all() noexcept;", "`wait` で待っているスレッドを全部起こします。C++20。", "定数"),
    ("concurrency/stop_source.md", "request_stop"): ("bool request_stop() noexcept;", "停止を要求します。最初に要求した呼び出しなら `true`。同じ状態を共有する `stop_token` から、`stop_requested()` が真になります。", "定数"),
    ("concurrency/stop_source.md", "stop_requested"): ("[[nodiscard]] bool stop_requested() const noexcept;", "停止が要求されていれば `true`。", "定数"),
    ("concurrency/stop_source.md", "stop_possible"): ("[[nodiscard]] bool stop_possible() const noexcept;", "停止を要求できる状態を持っていれば `true`（`nostopstate` で作ったものは `false`）。", "定数"),
    ("concurrency/stop_source.md", "get_token"): ("[[nodiscard]] stop_token get_token() const noexcept;", "停止の要求を確認するための `stop_token` を返します。", "定数"),
    ("concurrency/stop_source.md", "swap"): ("void swap(stop_source& other) noexcept;", "2 つの `stop_source` を入れ替えます。", "定数"),
    ("concurrency/stop_token.md", "stop_requested"): ("[[nodiscard]] bool stop_requested() const noexcept;", "停止が要求されていれば `true`。ワーカースレッドのループ条件で確かめます。", "定数"),
    ("concurrency/stop_token.md", "stop_possible"): ("[[nodiscard]] bool stop_possible() const noexcept;", "停止が要求されうる状態なら `true`。", "定数"),
    ("concurrency/stop_token.md", "swap"): ("void swap(stop_token& other) noexcept;", "2 つの `stop_token` を入れ替えます。", "定数"),
    ("concurrency/shared_mutex.md", "lock"): ("void lock();", "書き込み用に、独占的にロックします。ほかのスレッドは、読み取りも書き込みもできません。", "待つ時間による"),
    ("concurrency/shared_mutex.md", "try_lock"): ("bool try_lock();", "待たずに、独占ロックを試みます。取れたら `true`。", "定数"),
    ("concurrency/shared_mutex.md", "unlock"): ("void unlock();", "独占ロックを解除します。", "定数"),
    ("concurrency/shared_mutex.md", "lock_shared"): ("void lock_shared();", "読み取り用に、共有ロックします。複数のスレッドが同時に取れますが、独占ロックとは両立しません。", "待つ時間による"),
    ("concurrency/shared_mutex.md", "try_lock_shared"): ("bool try_lock_shared();", "待たずに、共有ロックを試みます。取れたら `true`。", "定数"),
    ("concurrency/shared_mutex.md", "unlock_shared"): ("void unlock_shared();", "共有ロックを解除します。", "定数"),
    ("concurrency/timed_mutex.md", "try_lock_until"): ("template <class Clock, class Duration>\nbool try_lock_until(const std::chrono::time_point<Clock, Duration>& abs_time);", "指定した時刻まで待って、ロックを試みます。取れたら `true`。", "最大で指定時刻まで"),
    ("concurrency/timed_mutex.md", "unlock"): ("void unlock();", "ロックを解除します。", "定数"),
    ("concurrency/recursive_mutex.md", "lock"): ("void lock();", "ロックします。すでに自分が持っていれば、回数を増やして成功します。", "待つ時間による"),
    ("concurrency/recursive_mutex.md", "try_lock"): ("bool try_lock() noexcept;", "待たずに、ロックを試みます。", "定数"),
    ("concurrency/recursive_mutex.md", "unlock"): ("void unlock();", "ロックの回数を 1 減らします。0 になったら、本当に解除します。", "定数"),
    ("concurrency/unique_lock.md", "try_lock"): ("bool try_lock();", "待たずに、ミューテックスのロックを試みます。取れたら `true`。", "定数"),
    ("concurrency/unique_lock.md", "try_lock_for"): ("template <class Rep, class Period>\nbool try_lock_for(const std::chrono::duration<Rep, Period>& rel_time);", "指定した時間まで待って、ロックを試みます。", "最大で指定時間"),
    ("concurrency/unique_lock.md", "try_lock_until"): ("template <class Clock, class Duration>\nbool try_lock_until(const std::chrono::time_point<Clock, Duration>& abs_time);", "指定した時刻まで待って、ロックを試みます。", "最大で指定時刻まで"),
    ("concurrency/unique_lock.md", "unlock"): ("void unlock();", "ロックを解除します。スコープの途中で、早めに解除したいときに使います。", "定数"),
    ("concurrency/unique_lock.md", "swap"): ("void swap(unique_lock& other) noexcept;", "2 つの `unique_lock` を入れ替えます。", "定数"),
    ("concurrency/unique_lock.md", "release"): ("mutex_type* release() noexcept;", "ミューテックスとの関連を切り離し、そのポインタを返します。解除はしないので、以降は自分で `unlock` します。", "定数"),
    ("concurrency/unique_lock.md", "mutex"): ("mutex_type* mutex() const noexcept;", "管理しているミューテックスへのポインタ。", "定数"),
    ("concurrency/unique_lock.md", "owns_lock"): ("bool owns_lock() const noexcept;", "ロックを持っていれば `true`。`defer_lock` や `try_to_lock` で作ったときに確かめます。", "定数"),
    ("concurrency/unique_lock.md", "operator_bool"): ("explicit operator bool() const noexcept;", "`owns_lock()` と同じです。", "定数"),
    ("concurrency/shared_lock.md", "try_lock"): ("bool try_lock();", "待たずに、共有ロックを試みます。取れたら `true`。", "定数"),
    ("concurrency/shared_lock.md", "try_lock_for"): ("template <class Rep, class Period>\nbool try_lock_for(const std::chrono::duration<Rep, Period>& rel_time);", "指定した時間まで待って、共有ロックを試みます。", "最大で指定時間"),
    ("concurrency/shared_lock.md", "try_lock_until"): ("template <class Clock, class Duration>\nbool try_lock_until(const std::chrono::time_point<Clock, Duration>& abs_time);", "指定した時刻まで待って、共有ロックを試みます。", "最大で指定時刻まで"),
    ("concurrency/shared_lock.md", "unlock"): ("void unlock();", "共有ロックを解除します。", "定数"),
    ("concurrency/shared_lock.md", "swap"): ("void swap(shared_lock& other) noexcept;", "2 つの `shared_lock` を入れ替えます。", "定数"),
    ("concurrency/shared_lock.md", "release"): ("mutex_type* release() noexcept;", "ミューテックスとの関連を切り離し、そのポインタを返します。", "定数"),
    ("concurrency/shared_lock.md", "mutex"): ("mutex_type* mutex() const noexcept;", "管理しているミューテックスへのポインタ。", "定数"),
    ("concurrency/shared_lock.md", "owns_lock"): ("bool owns_lock() const noexcept;", "共有ロックを持っていれば `true`。", "定数"),
    ("concurrency/shared_lock.md", "operator_bool"): ("explicit operator bool() const noexcept;", "`owns_lock()` と同じです。", "定数"),
    ("concurrency/atomic_ref.md", "load"): ("T load(std::memory_order order = std::memory_order_seq_cst) const noexcept;", "参照している変数の値を、アトミックに読みます。", "定数"),
    ("concurrency/atomic_ref.md", "store"): ("void store(T desired, std::memory_order order = std::memory_order_seq_cst) const noexcept;", "参照している変数に、アトミックに値を書きます。", "定数"),
    ("concurrency/atomic_ref.md", "exchange"): ("T exchange(T desired, std::memory_order order = std::memory_order_seq_cst) const noexcept;", "値を書き換えて、書き換える前の値を返します。", "定数"),
    ("concurrency/atomic_ref.md", "compare_exchange_weak"): ("bool compare_exchange_weak(T& expected, T desired) const noexcept;", "現在の値が `expected` と等しければ `desired` に書き換えます。見かけ上の失敗が起きることがあり、ループで使います。", "定数"),
    ("concurrency/atomic_ref.md", "compare_exchange_strong"): ("bool compare_exchange_strong(T& expected, T desired) const noexcept;", "現在の値が `expected` と等しければ `desired` に書き換えます。見かけ上の失敗は起きません。", "定数"),
    ("concurrency/atomic_ref.md", "fetch_add"): ("T fetch_add(T arg, std::memory_order order = std::memory_order_seq_cst) const noexcept;", "加算して、加算前の値を返します。", "定数"),
    ("concurrency/atomic_ref.md", "fetch_sub"): ("T fetch_sub(T arg, std::memory_order order = std::memory_order_seq_cst) const noexcept;", "減算して、減算前の値を返します。", "定数"),
    ("concurrency/atomic_ref.md", "is_lock_free"): ("bool is_lock_free() const noexcept;", "ロックなしで動くなら `true`。", "定数"),
    ("concurrency/atomic_ref.md", "wait"): ("void wait(T old, std::memory_order order = std::memory_order_seq_cst) const noexcept;", "値が `old` と等しい間、待ちます。", "待つ時間による"),
    ("concurrency/atomic_ref.md", "notify_one"): ("void notify_one() const noexcept;", "`wait` で待っているスレッドを 1 つ起こします。", "定数"),
    ("concurrency/atomic_ref.md", "notify_all"): ("void notify_all() const noexcept;", "`wait` で待っているスレッドを全部起こします。", "定数"),
    ("utilities/function.md", "target_type"): ("const std::type_info& target_type() const noexcept;", "中に入っている呼び出し可能なものの型情報（`typeid`）。空なら `typeid(void)`。", "定数"),
    ("utilities/function.md", "operator="): ("function& operator=(function&& other);\nfunction& operator=(const function& other);\ntemplate <class F> function& operator=(F&& f);\nfunction& operator=(std::nullptr_t) noexcept;", "ほかの `function`・関数・ラムダなどを代入します。`nullptr` を代入すると空になります。", "中身による"),
    ("utilities/any.md", "swap"): ("void swap(any& other) noexcept;", "中身を入れ替えます。", "定数"),
    ("utilities/any.md", "operator="): ("any& operator=(const any& rhs);\nany& operator=(any&& rhs) noexcept;\ntemplate <class T> any& operator=(T&& value);", "別の `any` または値を代入します。中の型は、代入した値の型に変わります。", "中身による"),
    ("utilities/pair.md", "operator="): ("pair& operator=(const pair& other);\npair& operator=(pair&& other) noexcept(...);", "`first` と `second` をそれぞれ代入します。", "要素による"),
    ("utilities/pair.md", "operator=="): ("template <class T1, class T2>\nbool operator==(const pair<T1, T2>& a, const pair<T1, T2>& b);", "`first` と `second` が両方等しければ `true`。", "要素による"),
    ("utilities/pair.md", "operator<=>"): ("template <class T1, class T2>\nauto operator<=>(const pair<T1, T2>& a, const pair<T1, T2>& b);", "まず `first` を比べ、等しければ `second` を比べる辞書順の三方比較（C++20）。", "要素による"),
    ("utilities/variant.md", "swap"): ("void swap(variant& other);", "中身を入れ替えます。型が違えば、それぞれが相手の型に変わります。", "中身による"),
    ("utilities/variant.md", "operator="): ("variant& operator=(const variant& rhs);\nvariant& operator=(variant&& rhs);\ntemplate <class T> variant& operator=(T&& t);", "別の `variant` または値を代入します。値を代入するときは、`T` に最も合う選択肢が選ばれます。", "中身による"),
    ("utilities/variant.md", "operator=="): ("template <class... Types>\nbool operator==(const variant<Types...>& a, const variant<Types...>& b);", "同じ選択肢で、値が等しければ `true`。選択肢が違えば `false`。", "中身による"),
    ("utilities/expected.md", "emplace"): ("template <class... Args>\nT& emplace(Args&&... args) noexcept;", "今の中身を捨てて、引数から値をその場で作り直します（成功の状態になります）。", "定数 + 構築"),
    ("utilities/expected.md", "swap"): ("void swap(expected& other);", "中身を入れ替えます。", "中身による"),
    ("utilities/expected.md", "operator="): ("expected& operator=(const expected& rhs);\nexpected& operator=(expected&& rhs);\ntemplate <class U = T> expected& operator=(U&& v);", "別の `expected` または値を代入します。", "中身による"),
    ("utilities/expected.md", "operator=="): ("template <class T2, class E2>\nbool operator==(const expected& x, const expected<T2, E2>& y);", "どちらも成功なら値を、どちらも失敗ならエラーを比べます。成功と失敗の比較は `false`。", "中身による"),
    ("utilities/unique_ptr.md", "operator="): ("unique_ptr& operator=(unique_ptr&& r) noexcept;\nunique_ptr& operator=(std::nullptr_t) noexcept;", "所有権をムーブで受け取ります（コピーはできません）。それまで持っていたものは解放されます。`nullptr` を代入すると、解放して空になります。", "定数 + 解放"),
    ("utilities/shared_ptr.md", "operator[]"): ("element_type& operator[](std::ptrdiff_t idx) const;", "配列用の `shared_ptr<T[]>` の、`idx` 番目の要素への参照（C++17）。", "定数"),
    ("utilities/shared_ptr.md", "swap"): ("void swap(shared_ptr& r) noexcept;", "管理しているオブジェクトと参照カウントを、入れ替えます。", "定数"),
    ("utilities/shared_ptr.md", "owner_before"): ("template <class Y>\nbool owner_before(const shared_ptr<Y>& other) const noexcept;", "管理しているオブジェクトの「持ち主」（制御ブロック）の順序で比べます。`weak_ptr` をキーにした `map` で使います。", "定数"),
    ("utilities/shared_ptr.md", "owner_hash"): ("std::size_t owner_hash() const noexcept;", "持ち主（制御ブロック）に対するハッシュ値（C++26）。", "定数"),
    ("utilities/shared_ptr.md", "owner_equal"): ("template <class Y>\nbool owner_equal(const shared_ptr<Y>& other) const noexcept;", "同じ持ち主（制御ブロック）かどうか（C++26）。", "定数"),
    ("utilities/shared_ptr.md", "operator="): ("shared_ptr& operator=(const shared_ptr& r) noexcept;\nshared_ptr& operator=(shared_ptr&& r) noexcept;", "コピー代入で参照カウントが 1 増え、それまで持っていたものの参照カウントが 1 減ります。ムーブ代入では、所有権を移すだけです。", "定数"),
    ("utilities/weak_ptr.md", "use_count"): ("long use_count() const noexcept;", "管理しているオブジェクトを共有している `shared_ptr` の数。期限切れなら 0。", "定数"),
    ("utilities/weak_ptr.md", "reset"): ("void reset() noexcept;", "何も指さない状態にします。", "定数"),
    ("utilities/weak_ptr.md", "swap"): ("void swap(weak_ptr& r) noexcept;", "2 つの `weak_ptr` を入れ替えます。", "定数"),
    ("utilities/weak_ptr.md", "owner_before"): ("template <class Y>\nbool owner_before(const weak_ptr<Y>& other) const noexcept;", "持ち主（制御ブロック）の順序で比べます。`weak_ptr` をキーにした `map` で使います。", "定数"),
    ("utilities/weak_ptr.md", "owner_hash"): ("std::size_t owner_hash() const noexcept;", "持ち主（制御ブロック）に対するハッシュ値（C++26）。", "定数"),
    ("utilities/weak_ptr.md", "owner_equal"): ("template <class Y>\nbool owner_equal(const weak_ptr<Y>& other) const noexcept;", "同じ持ち主かどうか（C++26）。", "定数"),
    ("utilities/weak_ptr.md", "operator="): ("weak_ptr& operator=(const weak_ptr& r) noexcept;\nweak_ptr& operator=(const shared_ptr<T>& r) noexcept;", "`weak_ptr` または `shared_ptr` から代入します。参照カウントは増えません（弱い参照）。", "定数"),
    ("io/ifstream.md", "ignore"): ("istream& ignore(streamsize count = 1, int_type delim = EOF);", "最大 `count` 文字を読み飛ばします。`delim` に当たったら、それも読んで止まります。入力のあとに残った改行を捨てるのに使います。", "O(count)"),
    ("io/ifstream.md", "peek"): ("int_type peek();", "次の 1 文字を、読み進めずにのぞきます。終端なら `EOF`。", "定数"),
    ("io/ifstream.md", "unget"): ("istream& unget();", "直前に読んだ 1 文字を戻して、もう一度読めるようにします。", "定数"),
    ("io/ifstream.md", "putback"): ("istream& putback(char_type ch);", "指定した文字を、読み直せるように戻します。", "定数"),
    ("io/ifstream.md", "fail"): ("bool fail() const;", "読み込みに失敗した（`failbit` か `badbit`）なら `true`。形式が合わない入力のときも真になります。", "定数"),
    ("io/ifstream.md", "bad"): ("bool bad() const;", "回復できない深刻なエラー（`badbit`）があれば `true`。", "定数"),
    ("io/ifstream.md", "good"): ("bool good() const;", "エラーがなく、終端でもなければ `true`。", "定数"),
    ("io/ifstream.md", "readsome"): ("streamsize readsome(char_type* s, streamsize n);", "バッファに**すでにある**文字だけを、待たずに読みます。", "O(n)"),
    ("io/ifstream.md", "sync"): ("int sync();", "入力バッファを同期します。", "実装による"),
    ("io/ofstream.md", "put"): ("ostream& put(char_type ch);", "1 文字を、書式なしで書き込みます。", "定数"),
    ("io/ofstream.md", "eof"): ("bool eof() const;", "終端に達していれば `true`。", "定数"),
    ("io/ofstream.md", "fail"): ("bool fail() const;", "書き込みに失敗した（`failbit` か `badbit`）なら `true`。", "定数"),
    ("io/ofstream.md", "bad"): ("bool bad() const;", "回復できない深刻なエラー（`badbit`）があれば `true`。ディスクがいっぱいのときなどです。", "定数"),
    ("io/ofstream.md", "good"): ("bool good() const;", "エラーがなければ `true`。", "定数"),
    ("containers/bitset.md", "operator<<="): None,
    ("containers/string_view.md", ""): None,
}
EXTRA_CLASS = {"unordered_multimap.md": "unordered_multimap", "unordered_multiset.md": "unordered_multiset"}


def class_of(page):
    return Path(page).stem


def build(page, name):
    cls = class_of(page)
    spec = SPEC.get((page, name))
    if spec is None:
        spec = GEN.get(name)
        if spec is None:
            return None
    sig, desc, cx = spec
    sig = sig.replace("{C}", cls)
    ver = None
    if "C++23" in desc and "（C++23）" in desc:
        ver = ("23", "C++23")
    elif "C++26" in desc and "（C++26）" in desc:
        ver = ("26", "C++26")
    elif "C++20" in desc and ("（C++20）" in desc or "。C++20。" in desc):
        ver = ("20", "C++20")
    elif "C++17" in desc and "（C++17）" in desc:
        ver = ("17", "C++17")
    desc = re.sub(r"（C\+\+(17|20|23|26)）", "", desc).replace("。C++20。", "。")
    heading = HEAD.get(name, name)
    ids = IDS.get(name, re.sub(r"[^\w]+", "_", name).strip("_"))
    if page == "concurrency/thread.md" and name in ("get_id", "join"):
        ids = "thread_" + name
    return fn(heading, sig, None, "", cx, None, notes=desc, ver=ver, ids=ids)


def run(only=()):
    unhandled = []
    for page, names in members.MEMBERS.items():
        if only and not any(o in page for o in only):
            continue
        p = STL / page
        if not p.exists():
            continue
        hs, ids = members.headings(p)
        for n in names.split():
            if members.has(n, hs, ids):
                continue
            sec = build(page, n)
            if sec is None:
                unhandled.append((page, n))
                continue
            add_secs(page, sec)
    for u in unhandled:
        print("UNHANDLED", u)
    return unhandled


if __name__ == "__main__":
    run(sys.argv[1:])
