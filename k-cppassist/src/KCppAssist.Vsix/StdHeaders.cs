using System;
using System.Collections.Generic;

namespace KCppAssist
{
    /// <summary>標準ライブラリ・Windows・DirectX の名前から、足すヘッダーを引く固定の表。VS に依存しない。</summary>
    internal static class StdHeaders
    {
        private static readonly Dictionary<string, string> Map = Build();

        // 前の文字が合えば、そのヘッダーとみなす名前
        private static readonly KeyValuePair<string, string>[] Prefixes =
        {
            new KeyValuePair<string, string>("ID3D12", "<d3d12.h>"),
            new KeyValuePair<string, string>("D3D12_", "<d3d12.h>"),
            new KeyValuePair<string, string>("IDXGI", "<dxgi1_6.h>"),
            new KeyValuePair<string, string>("DXGI_", "<dxgi1_6.h>"),
        };

        /// <summary>名前(std::vector、ComPtr、UINT など)の表のヘッダー(「&lt;vector&gt;」の形)。なければ null。</summary>
        public static string Lookup(string name)
        {
            string h;
            if (Map.TryGetValue(name, out h)) return h;
            int k = name.LastIndexOf("::", StringComparison.Ordinal);
            string last = k < 0 ? name : name.Substring(k + 2);
            if (k >= 0 && !name.StartsWith("DirectX::", StringComparison.Ordinal)) return null;
            if (k >= 0 && Map.TryGetValue(last, out h)) return h;
            foreach (var p in Prefixes)
                if (last.StartsWith(p.Key, StringComparison.Ordinal) && last.Length > p.Key.Length) return p.Value;
            return null;
        }

        private static Dictionary<string, string> Build()
        {
            var m = new Dictionary<string, string>(StringComparer.Ordinal);
            Action<string, string> add = (header, names) =>
            {
                foreach (string n in names.Split(' '))
                    if (n.Length > 0) m[n] = header;
            };
            Action<string, string> std = (header, names) =>
            {
                foreach (string n in names.Split(' '))
                    if (n.Length > 0) m["std::" + n] = header;
            };

            std("<string>", "string wstring u8string u16string u32string to_string to_wstring stoi stol stoll stof stod getline char_traits");
            std("<string_view>", "string_view wstring_view");
            std("<vector>", "vector");
            std("<array>", "array");
            std("<map>", "map multimap");
            std("<unordered_map>", "unordered_map unordered_multimap");
            std("<set>", "set multiset");
            std("<unordered_set>", "unordered_set unordered_multiset");
            std("<deque>", "deque");
            std("<list>", "list");
            std("<forward_list>", "forward_list");
            std("<queue>", "queue priority_queue");
            std("<stack>", "stack");
            std("<utility>", "pair move forward swap exchange make_pair declval");
            std("<tuple>", "tuple make_tuple tie get apply");
            std("<memory>", "unique_ptr shared_ptr weak_ptr make_unique make_shared enable_shared_from_this allocator");
            std("<functional>", "function bind ref cref reference_wrapper hash less greater equal_to");
            std("<optional>", "optional nullopt make_optional");
            std("<variant>", "variant visit holds_alternative monostate");
            std("<any>", "any any_cast");
            std("<atomic>", "atomic atomic_bool atomic_int memory_order");
            std("<mutex>", "mutex recursive_mutex lock_guard unique_lock scoped_lock once_flag call_once");
            std("<shared_mutex>", "shared_mutex shared_lock");
            std("<condition_variable>", "condition_variable");
            std("<thread>", "thread this_thread");
            std("<future>", "future promise async packaged_task shared_future");
            std("<chrono>", "chrono");
            std("<algorithm>", "sort stable_sort find find_if find_if_not copy copy_if fill reverse unique remove remove_if transform for_each any_of all_of none_of count count_if clamp min max minmax lower_bound upper_bound binary_search equal max_element min_element rotate shuffle");
            std("<numeric>", "accumulate iota reduce partial_sum inner_product");
            std("<iostream>", "cout cerr cin clog endl ostream istream");
            std("<sstream>", "stringstream ostringstream istringstream");
            std("<fstream>", "ifstream ofstream fstream");
            std("<iomanip>", "setw setprecision setfill");
            std("<filesystem>", "filesystem");
            std("<span>", "span");
            std("<bitset>", "bitset");
            std("<limits>", "numeric_limits");
            std("<stdexcept>", "runtime_error logic_error out_of_range invalid_argument length_error domain_error range_error overflow_error");
            std("<exception>", "exception exception_ptr current_exception rethrow_exception terminate");
            std("<initializer_list>", "initializer_list");
            std("<format>", "format");
            std("<regex>", "regex smatch regex_match regex_search regex_replace");
            std("<numbers>", "numbers");
            std("<random>", "mt19937 mt19937_64 random_device uniform_int_distribution uniform_real_distribution normal_distribution");
            std("<type_traits>", "is_same is_same_v enable_if enable_if_t conditional conditional_t remove_reference remove_reference_t decay decay_t is_integral is_floating_point is_base_of underlying_type underlying_type_t");
            std("<new>", "nothrow bad_alloc");
            std("<typeinfo>", "type_info");
            std("<cstddef>", "size_t ptrdiff_t nullptr_t byte max_align_t");
            std("<cstdint>", "int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t intptr_t uintptr_t");
            std("<cstring>", "memcpy memset memcmp memmove strlen strcmp strncmp strcpy strncpy strcat strchr strstr");
            std("<cmath>", "sqrt sin cos tan asin acos atan atan2 pow floor ceil round fabs abs fmod exp log log2 log10 isnan isinf trunc");
            std("<cstdio>", "printf snprintf sprintf fprintf fopen fclose fread fwrite fputs puts FILE");
            std("<cstdlib>", "malloc free calloc realloc exit abort atoi atof rand srand getenv system qsort");

            // 「std::」なしで書かれるもの
            add("<cstdint>", "int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t intptr_t uintptr_t");
            add("<cstddef>", "size_t ptrdiff_t");
            add("<cstring>", "memcpy memset memcmp memmove strlen strcmp strncmp strcpy strncpy strcat strchr strstr");
            add("<cstdio>", "printf snprintf sprintf fprintf fopen fclose fread fwrite fputs puts FILE");
            add("<cstdlib>", "malloc free calloc realloc exit abort atoi atof rand srand getenv qsort");
            add("<cmath>", "sqrtf sinf cosf tanf atan2f powf floorf ceilf fabsf fmodf");

            // Windows
            add("<Windows.h>", "UINT UINT8 UINT16 UINT32 UINT64 INT8 INT16 INT32 INT64 DWORD WORD BYTE BOOL BOOLEAN HRESULT HWND HINSTANCE HMODULE HANDLE HDC HICON HCURSOR LPARAM WPARAM LRESULT LPCWSTR LPCSTR LPWSTR LPSTR WCHAR TCHAR LPVOID LPCVOID SIZE_T LONG ULONG LONGLONG ULONGLONG RECT POINT MSG WNDCLASSEXW OVERLAPPED SECURITY_ATTRIBUTES CRITICAL_SECTION LARGE_INTEGER FILETIME SYSTEMTIME");
            add("<wrl/client.h>", "ComPtr Microsoft::WRL::ComPtr");
            m["Microsoft::WRL::ComPtr"] = "<wrl/client.h>";
            add("<DirectXMath.h>", "XMFLOAT2 XMFLOAT3 XMFLOAT4 XMFLOAT3X3 XMFLOAT4X3 XMFLOAT4X4 XMINT2 XMINT3 XMINT4 XMUINT2 XMUINT3 XMUINT4 XMVECTOR XMMATRIX FXMVECTOR CXMVECTOR GXMVECTOR HXMVECTOR FXMMATRIX CXMMATRIX XMVectorSet XMMatrixIdentity XMLoadFloat3 XMLoadFloat4 XMLoadFloat4x4 XMStoreFloat3 XMStoreFloat4 XMStoreFloat4x4");
            add("<DirectXCollision.h>", "BoundingBox BoundingSphere BoundingFrustum BoundingOrientedBox");
            add("<d3dcompiler.h>", "D3DCompile D3DReflect");
            return m;
        }
    }
}
