using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace KErrorLog
{
    /// <summary>
    /// 「宣言されていない名前」のエラーから、足りない #include を言い当てる。
    /// 'vector': 宣言されていない識別子です → #include &lt;vector&gt;
    /// </summary>
    public static class IncludeAdvisor
    {
        public sealed class Suggestion
        {
            public string Name = "";
            public string Header = "";
            public string Display = "";
        }

        private static readonly Dictionary<string, string> Table = new Dictionary<string, string>(StringComparer.Ordinal);

        private static readonly HashSet<string> Codes = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "C2065", "C3861", "C2039", "C2061", "C2146", "C3646", "C2653", "C2504", "C2027", "C2079", "C2143", "C2977", "C2955", "C7568"
        };

        // 自分で付けた名前と区別がつかない短い語は、「std::」が付いているときだけ当てる
        private static readonly HashSet<string> Ambiguous = new HashSet<string>(StringComparer.Ordinal)
        {
            "get", "begin", "end", "size", "empty", "data", "count", "find", "remove", "replace", "equal", "search", "merge", "copy", "fill",
            "swap", "time", "signal", "raise", "system", "exit", "abs", "log", "exp", "pow", "hash", "less", "greater", "plus", "minus", "ref",
            "next", "prev", "distance", "tm", "clock", "apply", "visit", "unique", "generate", "mismatch", "format", "print", "println", "Colors",
            "locale", "move", "forward", "bind", "seconds", "duration", "barrier", "latch", "ranges", "views", "exception",
            "terminate", "launch", "min", "max", "round", "floor", "ceil", "sort", "reverse", "rotate", "partition", "iota", "reduce", "yield",
            "tie", "byte"
        };

        private static readonly Regex Quoted = new Regex(@"['‘`](?<n>[^'’]+)['’]", RegexOptions.Compiled);

        static IncludeAdvisor()
        {
            Add("<vector>", "vector");
            Add("<string>", "string", "wstring", "u8string", "u16string", "u32string", "basic_string", "to_string", "stoi", "stol", "stoll", "stof", "stod", "getline", "char_traits");
            Add("<string_view>", "string_view", "wstring_view", "basic_string_view");
            Add("<map>", "map", "multimap");
            Add("<unordered_map>", "unordered_map", "unordered_multimap");
            Add("<set>", "set", "multiset");
            Add("<unordered_set>", "unordered_set", "unordered_multiset");
            Add("<list>", "list");
            Add("<forward_list>", "forward_list");
            Add("<deque>", "deque");
            Add("<queue>", "queue", "priority_queue");
            Add("<stack>", "stack");
            Add("<array>", "array");
            Add("<span>", "span");
            Add("<bitset>", "bitset");
            Add("<tuple>", "tuple", "make_tuple", "tie", "get", "tuple_size", "apply");
            Add("<optional>", "optional", "nullopt", "make_optional", "bad_optional_access");
            Add("<variant>", "variant", "visit", "monostate", "holds_alternative", "get_if");
            Add("<any>", "any", "any_cast");
            Add("<memory>", "unique_ptr", "shared_ptr", "weak_ptr", "make_unique", "make_shared", "allocator", "enable_shared_from_this",
                "static_pointer_cast", "dynamic_pointer_cast", "default_delete", "addressof", "construct_at", "destroy_at", "uninitialized_copy");
            Add("<memory_resource>", "pmr", "memory_resource", "polymorphic_allocator", "monotonic_buffer_resource", "synchronized_pool_resource");
            Add("<functional>", "function", "bind", "ref", "cref", "hash", "less", "greater", "equal_to", "plus", "minus", "multiplies", "invoke", "mem_fn", "reference_wrapper", "bind_front", "move_only_function");
            Add("<utility>", "pair", "make_pair", "move", "forward", "swap", "exchange", "declval", "index_sequence", "make_index_sequence", "integer_sequence", "as_const", "in_place");
            Add("<algorithm>", "sort", "stable_sort", "find", "find_if", "find_if_not", "min", "max", "minmax", "clamp", "transform", "for_each", "remove", "remove_if", "reverse",
                "unique", "copy", "copy_if", "fill", "count", "count_if", "all_of", "any_of", "none_of", "binary_search", "lower_bound", "upper_bound", "equal_range", "min_element",
                "max_element", "rotate", "shuffle", "partition", "nth_element", "swap_ranges", "replace", "replace_if", "generate", "is_sorted", "merge", "adjacent_find", "search", "mismatch", "equal", "fill_n", "copy_n");
            Add("<numeric>", "accumulate", "iota", "reduce", "transform_reduce", "inner_product", "partial_sum", "adjacent_difference", "gcd", "lcm", "midpoint", "lerp");
            Add("<iterator>", "back_inserter", "front_inserter", "inserter", "begin", "end", "next", "prev", "advance", "distance", "iterator_traits", "make_move_iterator", "istream_iterator", "ostream_iterator", "reverse_iterator", "size", "empty", "data");
            Add("<ranges>", "ranges", "views");
            Add("<iostream>", "cout", "cin", "cerr", "clog", "endl", "wcout", "wcin", "flush", "ios_base");
            Add("<istream>", "istream", "basic_istream");
            Add("<ostream>", "ostream", "basic_ostream");
            Add("<sstream>", "stringstream", "ostringstream", "istringstream", "stringbuf");
            Add("<fstream>", "ifstream", "ofstream", "fstream", "wifstream", "wofstream", "filebuf");
            Add("<iomanip>", "setw", "setprecision", "setfill", "setbase", "fixed", "scientific", "hex", "dec", "put_time", "quoted");
            Add("<filesystem>", "filesystem");
            Add("<chrono>", "chrono", "steady_clock", "system_clock", "high_resolution_clock", "milliseconds", "microseconds", "nanoseconds", "seconds", "duration", "time_point", "duration_cast");
            Add("<thread>", "thread", "jthread", "this_thread", "sleep_for", "sleep_until", "yield", "hardware_concurrency");
            Add("<mutex>", "mutex", "recursive_mutex", "timed_mutex", "lock_guard", "unique_lock", "scoped_lock", "once_flag", "call_once", "try_lock");
            Add("<shared_mutex>", "shared_mutex", "shared_lock", "shared_timed_mutex");
            Add("<condition_variable>", "condition_variable", "condition_variable_any", "cv_status");
            Add("<atomic>", "atomic", "atomic_flag", "memory_order", "atomic_thread_fence", "atomic_int", "atomic_bool", "atomic_ref");
            Add("<future>", "future", "promise", "async", "packaged_task", "shared_future", "launch");
            Add("<semaphore>", "counting_semaphore", "binary_semaphore");
            Add("<latch>", "latch");
            Add("<barrier>", "barrier");
            Add("<stop_token>", "stop_token", "stop_source", "stop_callback");
            Add("<random>", "mt19937", "mt19937_64", "random_device", "uniform_int_distribution", "uniform_real_distribution", "normal_distribution", "default_random_engine", "bernoulli_distribution", "seed_seq", "discrete_distribution");
            Add("<limits>", "numeric_limits");
            Add("<type_traits>", "is_same", "is_same_v", "enable_if", "enable_if_t", "decay", "decay_t", "remove_reference", "remove_reference_t", "is_integral", "is_floating_point", "conditional", "conditional_t",
                "is_base_of", "is_convertible", "remove_cv", "remove_const", "underlying_type", "is_trivially_copyable", "is_enum", "void_t", "true_type", "false_type", "integral_constant", "invoke_result", "is_pointer", "is_arithmetic");
            Add("<concepts>", "same_as", "integral", "floating_point", "convertible_to", "derived_from", "invocable", "regular_invocable", "totally_ordered", "equality_comparable", "copyable", "movable", "default_initializable", "signed_integral", "unsigned_integral");
            Add("<exception>", "exception", "terminate", "current_exception", "rethrow_exception", "exception_ptr", "uncaught_exceptions");
            Add("<stdexcept>", "runtime_error", "logic_error", "invalid_argument", "out_of_range", "length_error", "domain_error", "range_error", "overflow_error", "underflow_error");
            Add("<typeinfo>", "type_info", "bad_cast");
            Add("<typeindex>", "type_index");
            Add("<new>", "bad_alloc", "nothrow", "align_val_t", "launder", "hardware_destructive_interference_size");
            Add("<initializer_list>", "initializer_list");
            Add("<compare>", "strong_ordering", "weak_ordering", "partial_ordering");
            Add("<source_location>", "source_location");
            Add("<format>", "format", "format_to", "formatter", "vformat", "format_error");
            Add("<print>", "print", "println");
            Add("<bit>", "bit_cast", "popcount", "countl_zero", "countr_zero", "has_single_bit", "bit_ceil", "bit_floor", "byteswap", "endian", "rotl", "rotr");
            Add("<numbers>", "numbers");
            Add("<cstdint>", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "int8_t", "int16_t", "int32_t", "int64_t", "uintptr_t", "intptr_t", "uint_fast32_t", "int_fast32_t", "intmax_t", "uintmax_t");
            Add("<cstddef>", "size_t", "ptrdiff_t", "nullptr_t", "byte", "max_align_t", "offsetof");
            Add("<cstdio>", "printf", "fprintf", "sprintf", "snprintf", "puts", "fopen", "fclose", "fread", "fwrite", "fgets", "scanf", "sscanf", "FILE", "stdout", "stderr", "fseek", "ftell", "fflush");
            Add("<cstdlib>", "malloc", "free", "calloc", "realloc", "rand", "srand", "atoi", "atof", "exit", "abort", "getenv", "qsort", "strtol", "strtod", "EXIT_SUCCESS", "EXIT_FAILURE", "system", "atexit");
            Add("<cstring>", "memcpy", "memset", "memmove", "memcmp", "strlen", "strcpy", "strncpy", "strcmp", "strncmp", "strcat", "strchr", "strstr", "strerror", "memchr");
            Add("<cmath>", "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "pow", "exp", "log", "log2", "log10", "floor", "ceil", "round", "fabs", "fmod", "abs", "trunc", "hypot", "cbrt", "isnan", "isinf", "isfinite", "sinh", "cosh", "tanh", "copysign", "lround", "fma");
            Add("<cassert>", "assert");
            Add("<cctype>", "isalpha", "isdigit", "isspace", "isalnum", "toupper", "tolower", "isupper", "islower", "ispunct", "isxdigit");
            Add("<cwchar>", "wcslen", "wprintf", "wcscpy", "wcscmp", "wmemcpy");
            Add("<ctime>", "time_t", "clock", "time", "localtime", "strftime", "difftime", "tm");
            Add("<cstdarg>", "va_list", "va_start", "va_end", "va_arg");
            Add("<climits>", "INT_MAX", "INT_MIN", "UINT_MAX", "LONG_MAX", "CHAR_BIT", "SIZE_MAX");
            Add("<cfloat>", "FLT_MAX", "FLT_MIN", "DBL_MAX", "DBL_MIN", "FLT_EPSILON", "DBL_EPSILON");
            Add("<locale>", "locale", "wstring_convert", "codecvt_utf8");
            Add("<csignal>", "signal", "raise", "SIGINT", "SIGTERM");

            // Windows / DirectX
            Add("<windows.h>", "HWND", "HINSTANCE", "HRESULT", "DWORD", "WORD", "BYTE", "LPARAM", "WPARAM", "LRESULT", "UINT", "BOOL", "HANDLE", "HDC", "HMODULE", "LPCWSTR", "LPCSTR", "LPWSTR", "LPSTR",
                "WNDCLASSEX", "WNDCLASS", "MSG", "RECT", "POINT", "CALLBACK", "WINAPI", "WinMain", "wWinMain", "CreateWindowEx", "CreateWindowExW", "DefWindowProc", "PostQuitMessage", "GetModuleHandle",
                "Sleep", "OutputDebugString", "OutputDebugStringA", "OutputDebugStringW", "GetLastError", "CloseHandle", "CreateFile", "ReadFile", "WriteFile", "QueryPerformanceCounter", "QueryPerformanceFrequency",
                "SUCCEEDED", "FAILED", "S_OK", "E_FAIL", "INFINITE", "MAX_PATH", "LoadLibrary", "GetProcAddress", "FreeLibrary", "CRITICAL_SECTION", "SYSTEMTIME", "GetTickCount", "GetTickCount64", "VK_ESCAPE", "WM_DESTROY", "WM_PAINT", "WM_SIZE", "WM_CLOSE", "MessageBox");
            Add("<wrl/client.h>", "ComPtr", "Microsoft::WRL::ComPtr");
            Add("<DirectXMath.h>", "XMFLOAT2", "XMFLOAT3", "XMFLOAT4", "XMFLOAT4X4", "XMFLOAT3X3", "XMMATRIX", "XMVECTOR", "XMVectorSet", "XMMatrixIdentity", "XMLoadFloat3", "XMStoreFloat3", "XM_PI", "XMConvertToRadians", "XMVECTORF32", "XMMatrixMultiply", "XMLoadFloat4x4", "XMStoreFloat4x4");
            Add("<DirectXColors.h>", "Colors");
            Add("<DirectXCollision.h>", "BoundingBox", "BoundingSphere", "BoundingFrustum", "BoundingOrientedBox");
            Add("<d3d11.h>", "ID3D11Device", "ID3D11DeviceContext", "ID3D11Buffer", "ID3D11Texture2D", "ID3D11RenderTargetView", "ID3D11DepthStencilView", "ID3D11ShaderResourceView", "D3D11_VIEWPORT",
                "D3D11_BUFFER_DESC", "D3D11_TEXTURE2D_DESC", "D3D11CreateDevice", "D3D11_INPUT_ELEMENT_DESC", "ID3D11VertexShader", "ID3D11PixelShader", "ID3D11InputLayout", "ID3D11SamplerState", "D3D_FEATURE_LEVEL", "D3D_FEATURE_LEVEL_11_0");
            Add("<d3d12.h>", "ID3D12Device", "ID3D12CommandQueue", "ID3D12CommandAllocator", "ID3D12GraphicsCommandList", "ID3D12Resource", "ID3D12Fence", "ID3D12DescriptorHeap", "ID3D12PipelineState", "ID3D12RootSignature",
                "D3D12_COMMAND_QUEUE_DESC", "D3D12_RESOURCE_DESC", "D3D12_HEAP_PROPERTIES", "D3D12CreateDevice", "D3D12_VIEWPORT", "D3D12_RECT", "D3D12_RESOURCE_BARRIER", "D3D12_GRAPHICS_PIPELINE_STATE_DESC");
            Add("<dxgi1_6.h>", "IDXGIFactory6", "IDXGIAdapter4", "IDXGISwapChain4", "IDXGIFactory4", "IDXGIFactory2", "IDXGISwapChain3", "IDXGISwapChain1", "IDXGIAdapter1", "DXGI_SWAP_CHAIN_DESC1", "DXGI_FORMAT", "CreateDXGIFactory1", "CreateDXGIFactory2");
            Add("<d3dcompiler.h>", "D3DCompile", "D3DCompileFromFile", "D3DReflect", "ID3DBlob", "D3DReadFileToBlob");
        }

        private static void Add(string header, params string[] names)
        {
            foreach (string n in names) Table[n] = header;
        }

        /// <summary>このエラーで足りない #include を、言い当てる。当てはまらなければ null。</summary>
        public static Suggestion Suggest(Diag d)
        {
            if (d.Sev != Sev.Error) return null;
            if (d.Code.Length > 0 && !Codes.Contains(d.Code)) return null;
            if (d.Code.Length == 0 && d.IsLinker) return null;

            var names = new List<string>();
            foreach (Match m in Quoted.Matches(d.Message)) names.Add(m.Groups["n"].Value.Trim());
            if (names.Count == 0) return null;

            // 'vector': 'std' のメンバーではありません → std::vector
            string name = names[0];
            if (names.Count >= 2 && names[1] == "std" && !name.StartsWith("std::", StringComparison.Ordinal)) name = "std::" + name;

            // 名前空間の名前だけが出る場合(C2653: 'std' はクラスまたは名前空間の名前ではありません)は、使い方が分からないので当てない
            if (name == "std") return null;

            string bare = name;
            int colon = bare.LastIndexOf("::", StringComparison.Ordinal);
            if (bare.StartsWith("std::", StringComparison.Ordinal)) bare = bare.Substring(5);
            else if (colon > 0) bare = bare.Substring(colon + 2);
            if (bare.StartsWith("pmr::", StringComparison.Ordinal)) bare = "pmr";
            if (bare.StartsWith("chrono::", StringComparison.Ordinal)) bare = "chrono";
            if (bare.StartsWith("filesystem::", StringComparison.Ordinal)) bare = "filesystem";
            if (bare.StartsWith("ranges::", StringComparison.Ordinal) || bare.StartsWith("views::", StringComparison.Ordinal)) bare = "ranges";

            if (!name.StartsWith("std::", StringComparison.Ordinal) && colon < 0 && Ambiguous.Contains(bare)) return null;

            string header;
            if (!Table.TryGetValue(bare, out header)) return null;
            return new Suggestion { Name = name, Header = header, Display = "#include " + header };
        }
    }
}
