using System;
using System.Collections.Generic;
using System.Linq;

namespace KCppAssist.Vcpkg
{
    /// <summary>おすすめの 1 件。Rank は 1 から(小さいほど、ゲーム制作で入れる機会が多い)。</summary>
    internal sealed class Featured
    {
        public int Rank;
        public string Name;
        public string Category;      // 分野の日本語名(L.T で訳す)
        public string Ja;            // 日本語の説明(1 文)
        public string En;            // 英語の説明
    }

    /// <summary>
    /// ゲーム制作でよく使う vcpkg のパッケージを、入れる機会が多い順に並べたもの。最初の画面に出す。
    /// 順番は人気の統計ではなく、「ゲームを作る学生が、プロジェクトに入れる機会が多そうか」で決めた(DirectX を使う前提で、DirectX 系を上に置いた)。
    /// 説明は自分の言葉で書いた。名前は vcpkg search で確かめてある(tools の確認スクリプト参照)。
    /// </summary>
    internal static class VcpkgCatalog
    {
        public const string CatRender = "描画・DirectX";
        public const string CatWindow = "ウィンドウ・入力・フレームワーク";
        public const string CatUi = "UI・デバッグ表示";
        public const string CatAudio = "音";
        public const string CatPhysics = "物理・ナビゲーション";
        public const string CatData = "データ・保存";
        public const string CatAsset = "モデル・画像・フォント";
        public const string CatCore = "基盤・ユーティリティ";
        public const string CatScript = "スクリプト・ECS";
        public const string CatNet = "ネットワーク";
        public const string CatTest = "テスト・計測";
        public const string CatPack = "圧縮・暗号・文字コード";

        public static readonly string[] Categories =
        {
            CatRender, CatWindow, CatUi, CatAudio, CatPhysics, CatData, CatAsset, CatCore, CatScript, CatNet, CatTest, CatPack,
        };

        // 名前|分野|日本語の説明|英語の説明。上にあるほど順位が高い
        private const string Table = @"
imgui|UI・デバッグ表示|ゲームの中に、デバッグ用のウィンドウやエディタを手軽に作れる即時モードの UI。まず入れる 1 つ。|Immediate-mode UI for in-game debug windows and editors. Usually the first thing to add.
directxtk|描画・DirectX|DirectX 11 の補助クラス集。SimpleMath、SpriteBatch、モデル、入力、音がそろう。|Helper classes for DirectX 11: SimpleMath, SpriteBatch, models, input and audio.
directxtk12|描画・DirectX|DirectX 12 バージョンの補助クラス集。リソースのアップロードやスプライト描画を楽にする。|The DirectX 12 counterpart: resource upload, sprite drawing and more.
nlohmann-json|データ・保存|C++ らしい書き方で読み書きできる JSON ライブラリ。設定やセーブデータの定番。|JSON for modern C++. The usual choice for settings and save data.
glaze|データ・保存|構造体をそのまま JSON や バイナリに読み書きできる、コンパイル時に動くシリアライズ ライブラリ。リフレクション風に書ける。|Compile-time serialization of structs to and from JSON and binary, with reflection-like usage.
spdlog|基盤・ユーティリティ|速いログ出力ライブラリ。ファイル・コンソール・VS の出力欄に書き分けられる。|Fast logging to files, the console and the VS output window.
stb|モデル・画像・フォント|画像の読み込み（stb_image）やフォントの描画など、1 ファイルで使える小道具集。|Single-file helpers: image loading (stb_image), font rasterizing and more.
joltphysics|物理・ナビゲーション|剛体の物理と衝突判定。マルチスレッドで速く、最近のゲームでの採用例も多い。|Rigid-body physics and collision. Multithreaded and fast, used by recent games.
assimp|モデル・画像・フォント|FBX や OBJ など、さまざまな 3D モデルの形式を読み込む。|Loads many 3D model formats such as FBX and OBJ.
miniaudio|音|音の再生と録音を、1 つのヘッダーで済ませられる。ミキサーや 3D 音響もある。|Audio playback and capture in a single header, with mixing and 3D audio.
sdl3|ウィンドウ・入力・フレームワーク|ウィンドウ・入力・ゲームパッド・音を、複数の OS で同じように扱う土台。|Windowing, input, gamepads and audio across platforms.
entt|スクリプト・ECS|ECS（エンティティ・コンポーネント・システム）の定番。速く、ヘッダーだけで使える。|A fast header-only ECS (entity-component-system) library.
glm|描画・DirectX|ベクトルと行列の数学ライブラリ。シェーダーの GLSL に似た書き方ができる。|Vector and matrix math with GLSL-like syntax.
tracy|テスト・計測|フレームの内訳を、リアルタイムに見られるプロファイラー。重い所の特定に使う。|A real-time frame profiler for finding what makes frames slow.
fastgltf|モデル・画像・フォント|glTF 2.0 を速く読み込む。メモリの扱いがよく、大きなシーンに向く。|A fast glTF 2.0 loader with careful memory use.
directx-headers|描画・DirectX|DirectX 12 の公式ヘッダー。d3dx12 などの補助ヘッダーも含む。|The official DirectX 12 headers, including d3dx12 helpers.
directx12-agility|描画・DirectX|DirectX 12 Agility SDK。OS の更新を待たずに、新しい DirectX 12 の機能を使える。|DirectX 12 Agility SDK: new D3D12 features without waiting for an OS update.
directx-dxc|描画・DirectX|DirectX Shader Compiler。SM6 以降の HLSL を、コンパイルする。|DirectX Shader Compiler for Shader Model 6+ HLSL.
lua|スクリプト・ECS|軽くて埋め込みやすいスクリプト言語。ゲームのロジックやモッドに使う。|A small embeddable scripting language for gameplay logic and mods.
sol2|スクリプト・ECS|C++ と Lua を、少ない記述でつなぐ。|Binds C++ and Lua with little code.
box2d|物理・ナビゲーション|2D の物理エンジン。横スクロールやパズルなど、2D ゲームの定番。|The standard 2D physics engine for platformers and puzzle games.
openal-soft|音|3D 音響に強い音のライブラリ。位置による音の変化を、簡単に作れる。|A 3D positional audio library.
freetype|モデル・画像・フォント|フォントを読み込んで、文字を画像にする。文字の描画の土台。|Loads fonts and rasterizes glyphs. The base of text rendering.
meshoptimizer|モデル・画像・フォント|メッシュを軽く・速くするための最適化と圧縮。LOD の生成もできる。|Mesh optimization and compression, including LOD generation.
recastnavigation|物理・ナビゲーション|ナビゲーション メッシュを作って、経路探索に使う。敵の移動に向く。|Builds navigation meshes for pathfinding, e.g. enemy movement.
cereal|データ・保存|構造体をそのまま保存・復元するシリアライズ ライブラリ。JSON やバイナリに対応する。|Header-only serialization to JSON, XML and binary.
yaml-cpp|データ・保存|YAML の読み書き。人が読める設定やシーンのファイルに向く。|YAML parser and emitter for human-readable configs and scenes.
tomlplusplus|データ・保存|TOML の設定ファイルを読み書きする。コメントを書ける設定に向く。|Reads and writes TOML config files.
simdjson|データ・保存|非常に速い JSON パーサー。大きなデータを読み込むときに差が出る。|An extremely fast JSON parser for large data.
rapidjson|データ・保存|速くて小さい JSON ライブラリ。メモリの使い方を細かく制御できる。|A fast JSON library with fine control over memory.
tinyxml2|データ・保存|小さくて分かりやすい XML パーサー。|A small, simple XML parser.
pugixml|データ・保存|XPath が使える軽い XML パーサー。|A light XML parser with XPath.
gtest|テスト・計測|Google のテスト フレームワーク。モックも使える。|Google Test, with mocking.
catch2|テスト・計測|テストを書きやすい、C++ らしいテスト フレームワーク。|A test framework with a friendly syntax.
doctest|テスト・計測|ヘッダー 1 つで軽く動くテスト フレームワーク。|A light single-header test framework.
benchmark|テスト・計測|Google のマイクロベンチマーク。関数の速さを数字で比べる。|Google Benchmark for timing small pieces of code.
mimalloc|基盤・ユーティリティ|速くて断片化しにくいメモリ アロケーター。new / delete を置き換える。|A fast general-purpose allocator that can replace new/delete.
taskflow|基盤・ユーティリティ|タスクの依存関係を書いて、並列に動かす。ジョブ システムの代わりに使える。|Parallel task graphs; a ready-made job system.
concurrentqueue|基盤・ユーティリティ|スレッド間で受け渡す、ロックしない速いキュー。|A fast lock-free multi-producer queue.
enet|ネットワーク|UDP の上で、信頼できる通信と通常の通信を使い分けられる。ゲームの通信向け。|Reliable UDP networking designed for games.
asio|ネットワーク|TCP / UDP の非同期通信。通信を自作するときの土台。|Asynchronous TCP/UDP networking.
curl|ネットワーク|HTTP などで、データを取得・送信する。ランキングやアップデートの確認に使う。|Transfers data over HTTP and more, e.g. leaderboards or update checks.
zlib|圧縮・暗号・文字コード|定番の圧縮ライブラリ。多くのライブラリが、内部で使っている。|The standard compression library, used inside many others.
lz4|圧縮・暗号・文字コード|圧縮と展開が非常に速い。ロード時間を短くしたいときに向く。|Extremely fast compression for short load times.
zstd|圧縮・暗号・文字コード|圧縮率と速さのバランスがよい。アセットのパック向き。|Balanced ratio and speed; good for asset packs.
libpng|モデル・画像・フォント|PNG の読み書き。|Reads and writes PNG images.
libjpeg-turbo|モデル・画像・フォント|JPEG の読み書きを、SIMD で高速にする。|SIMD-accelerated JPEG codec.
libwebp|モデル・画像・フォント|WebP 形式の画像を読み書きする。|Reads and writes WebP images.
ktx|モデル・画像・フォント|GPU 向けのテクスチャ形式（KTX）を扱う。|Handles the KTX GPU texture format.
basisu|モデル・画像・フォント|GPU に合わせて変換できる、圧縮テクスチャ形式。配布サイズを小さくできる。|A supercompressed texture format that transcodes to GPU formats.
openexr|モデル・画像・フォント|HDR 画像（EXR）の読み書き。環境マップやライトマップに使う。|HDR image (EXR) I/O for environment and light maps.
implot|UI・デバッグ表示|ImGui の中にグラフを描く。フレームタイムの表示などに使う。|Plots inside ImGui, e.g. frame-time graphs.
imguizmo|UI・デバッグ表示|ImGui の上で、3D の移動・回転・拡大のギズモを出す。エディタ作りに使う。|3D translate/rotate/scale gizmos for editors.
glfw3|ウィンドウ・入力・フレームワーク|ウィンドウと入力だけを扱う軽いライブラリ。OpenGL・Vulkan 向け。|A light window and input library for OpenGL and Vulkan.
sdl3-image|ウィンドウ・入力・フレームワーク|SDL で、さまざまな画像形式を読み込む。|Loads many image formats for SDL.
sdl3-ttf|ウィンドウ・入力・フレームワーク|SDL で、TrueType フォントの文字を描く。|Renders TrueType text for SDL.
flecs|スクリプト・ECS|機能が豊富な ECS。クエリや階層、システムの順序を細かく指定できる。|A feature-rich ECS with queries, hierarchies and system ordering.
bullet3|物理・ナビゲーション|昔からある物理エンジン。剛体のほか、布や車両もある。|A long-standing physics engine with soft bodies and vehicles.
tinygltf|モデル・画像・フォント|ヘッダーだけで使える glTF ローダー。|A header-only glTF loader.
tinyobjloader|モデル・画像・フォント|OBJ ファイルだけを、軽く読み込む。|A tiny Wavefront OBJ loader.
magic-enum|基盤・ユーティリティ|enum の値を、文字列に変換したり、文字列から戻したりする。|Converts between enum values and strings.
fmt|基盤・ユーティリティ|書式つき文字列の作成。C++20 の std::format のもとになったライブラリ。|Formatting library that std::format is based on.
boost|基盤・ユーティリティ|C++ の定番ライブラリ集。small_vector や static_vector、asio、filesystem など、標準にない部品が多い。全部入りで大きいので、必要な部品だけ (boost-container など) を入れる手もある。|The classic C++ library collection: small_vector, static_vector, asio and more. It is large, so you can add single parts (e.g. boost-container) instead.
abseil|基盤・ユーティリティ|Google の基盤ライブラリ。InlinedVector、FixedArray、flat_hash_map など、速いコンテナーと文字列の道具がそろう。|Google's foundation library: InlinedVector, FixedArray, flat_hash_map and other fast containers and string utilities.
etl|基盤・ユーティリティ|動的確保をしない、固定容量の vector や string など。サイズが決まっているデータを、ヒープなしで扱える。|Fixed-capacity vector, string and more that never allocate from the heap.
range-v3|基盤・ユーティリティ|C++20 の ranges のもとになったライブラリ。C++20 より前の機能も使える。|The library std::ranges is based on, with extra features.
unordered-dense|基盤・ユーティリティ|std::unordered_map より速く、メモリも少ないハッシュ マップ。|A hash map faster and smaller than std::unordered_map.
robin-hood-hashing|基盤・ユーティリティ|速いハッシュ マップ。unordered-dense の前から使われている。|A fast hash map predating unordered-dense.
d3d12-memory-allocator|描画・DirectX|DirectX 12 のメモリ確保を、まとめて面倒を見てくれる。|Manages DirectX 12 memory allocation (D3D12MA).
directxmath|描画・DirectX|DirectX の SIMD 数学ライブラリ。SimpleMath のもとになっている。|DirectX's SIMD math library; SimpleMath is built on it.
glslang|描画・DirectX|GLSL を SPIR-V にコンパイルする。Vulkan 向け。|Compiles GLSL to SPIR-V for Vulkan.
spirv-cross|描画・DirectX|SPIR-V を、HLSL や GLSL などに変換する。|Converts SPIR-V back to HLSL, GLSL and others.
shaderc|描画・DirectX|Vulkan 向けのシェーダー コンパイラー。|A shader compiler collection for Vulkan.
msdfgen|モデル・画像・フォント|拡大してもくっきりする、距離フィールドのフォントを作る。|Generates multi-channel signed distance fields for crisp text.
harfbuzz|モデル・画像・フォント|文字を並べる（シェーピング）。アラビア語や日本語の組版に必要。|Text shaping for complex scripts.
icu|圧縮・暗号・文字コード|Unicode と地域設定の定番。文字コード変換や並べ替え。|The standard Unicode and localization library.
sqlite3|データ・保存|ファイル 1 つで動く SQL データベース。大量のセーブや設定の管理に向く。|A single-file SQL database.
protobuf|データ・保存|Google のシリアライズ形式。サイズが小さく、通信やセーブに向く。|Google's compact serialization format.
flatbuffers|データ・保存|読み込み時に変換しないで使えるシリアライズ。ゼロコピーで速い。|Zero-copy serialization for fast loading.
eigen3|基盤・ユーティリティ|大きな行列や線形代数の計算。物理やアニメーションの計算に使う。|Linear algebra for larger matrices and solvers.
openssl|圧縮・暗号・文字コード|暗号と TLS の定番。HTTPS の通信に必要。|Cryptography and TLS.
libsodium|圧縮・暗号・文字コード|使いやすい暗号ライブラリ。間違いにくい設計。|An easy-to-use crypto library.
backward-cpp|テスト・計測|クラッシュしたとき、スタック トレースを読みやすく出す。|Pretty stack traces on crashes.
sentry-native|テスト・計測|クラッシュの報告を集めるサービスと連携する。|Crash reporting integration for Sentry.
angelscript|スクリプト・ECS|C++ に似た書き方のスクリプト言語。|A C++-like scripting language.
wren|スクリプト・ECS|小さくて速い、クラスのあるスクリプト言語。|A small, fast class-based scripting language.
raylib|ウィンドウ・入力・フレームワーク|ゲーム作りを学ぶための、分かりやすいフレームワーク。|A simple framework for learning game programming.
sfml|ウィンドウ・入力・フレームワーク|2D ゲーム向けのマルチメディア ライブラリ。|A multimedia library popular for 2D games.
bgfx|描画・DirectX|複数の描画 API を、同じコードで使える描画ライブラリ。|A rendering library that abstracts DirectX, Vulkan and OpenGL.
libvorbis|音|Ogg Vorbis の音声を読み込む。BGM 向け。|Decodes Ogg Vorbis audio, good for music.
opus|音|通話にも使われる、低遅延の音声コーデック。|A low-latency audio codec used for voice chat.
libogg|音|Ogg コンテナ。Vorbis や Opus を使うときに必要になる。|The Ogg container needed by Vorbis and Opus.
minimp3|音|MP3 を読み込む、ヘッダー 1 つのライブラリ。|A single-header MP3 decoder.
nanovg|UI・デバッグ表示|アンチエイリアスつきのベクター描画。UI の図形に使う。|Antialiased vector drawing for UI shapes.
lunasvg|UI・デバッグ表示|SVG を、画像にして描く。アイコン用。|Renders SVG to images, handy for icons.
nuklear|UI・デバッグ表示|ImGui に似た、C 言語の即時モード UI。|A C immediate-mode UI similar to ImGui.
gsl-lite|基盤・ユーティリティ|C++ Core Guidelines の補助型（span など）。|C++ Core Guidelines support types such as span.
wg21-sg14|基盤・ユーティリティ|ゲーム向けの C++ 標準化グループ SG14 が提案した部品集。|Components proposed by the games-oriented C++ study group SG14.
stduuid|基盤・ユーティリティ|UUID（一意な ID）を作る。アセットの ID に使う。|Generates UUIDs, handy for asset IDs.
utfcpp|圧縮・暗号・文字コード|UTF-8 / 16 / 32 の変換。|UTF-8/16/32 conversions.
rttr|基盤・ユーティリティ|実行時にクラスのメンバーを調べる、リフレクション。エディタ作りに向く。|Run-time reflection, useful for editors.
plog|基盤・ユーティリティ|軽くて簡単なログ ライブラリ。|A light, simple logging library.
nanobench|テスト・計測|1 ファイルで使える、小さなベンチマーク。|A single-header micro benchmark.
readerwriterqueue|基盤・ユーティリティ|1 つのスレッドから 1 つのスレッドへ渡す、ロックしないキュー。|A lock-free single-producer single-consumer queue.
vulkan-headers|描画・DirectX|Vulkan のヘッダー。|Vulkan headers.
volk|描画・DirectX|Vulkan の関数を、実行時に読み込むローダー。|A Vulkan meta loader.
vulkan-memory-allocator|描画・DirectX|Vulkan のメモリ確保を、まとめて面倒を見てくれる。|Manages Vulkan memory allocation (VMA).
physx|物理・ナビゲーション|NVIDIA の物理エンジン。大規模なゲームでの実績がある。|NVIDIA's physics engine, proven in large games.
openxr-loader|描画・DirectX|VR / AR の標準 API OpenXR のローダー。|The OpenXR loader for VR/AR.
cpr|ネットワーク|curl を、書きやすく包んだ HTTP ライブラリ。|A friendly HTTP wrapper around curl.
libuv|ネットワーク|非同期の入出力。Node.js の土台でもある。|Asynchronous I/O, the base of Node.js.
cgltf|モデル・画像・フォント|C 言語の、ヘッダー 1 つの glTF ローダー。|A single-file C glTF loader.
glad|描画・DirectX|OpenGL の関数を読み込むローダーを、生成する。|Generates OpenGL function loaders.
lodepng|モデル・画像・フォント|1 ファイルで使える PNG の読み書き。|A single-file PNG codec.
tinyexr|モデル・画像・フォント|EXR 画像を、軽く読み書きする。|A light EXR reader and writer.
sdl2|ウィンドウ・入力・フレームワーク|SDL の 2 番目のバージョン。情報が多く、まだ広く使われている。|The older, widely documented SDL 2.
pybind11|スクリプト・ECS|C++ と Python をつなぐ。ツールやエディタの拡張に使う。|Binds C++ and Python for tooling.
";

        private static List<Featured> _all;

        public static IReadOnlyList<Featured> All
        {
            get
            {
                if (_all != null) return _all;
                var list = new List<Featured>();
                int rank = 0;
                foreach (string raw in Table.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    string[] f = raw.Split('|');
                    if (f.Length < 4) continue;
                    list.Add(new Featured { Rank = ++rank, Name = f[0].Trim(), Category = f[1].Trim(), Ja = f[2].Trim(), En = f[3].Trim() });
                }
                _all = list;
                return list;
            }
        }

        public static Featured Find(string name)
        {
            return All.FirstOrDefault(f => string.Equals(f.Name, name, StringComparison.OrdinalIgnoreCase));
        }
    }
}
