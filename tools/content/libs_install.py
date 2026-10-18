import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

# 外部ライブラリは docs/libs。pg の根は docs/graphics なので、相対で指す。
L = "../libs/"

# ---------------------------------------------------------------- tinygltf
pg.Add(L + "tinygltf/install.md", '''
## 動作確認：glTF を 1 つ読んでみる

導入できたかは、<strong>小さなプログラム</strong>で確かめます。`.glb` ファイル（なんでもよい。[Khronos のサンプル](https://github.com/KhronosGroup/glTF-Sample-Assets)など）を 1 つ用意します。

```cpp
// gltf_loader.cpp: tinygltf の実装は、このファイルだけに入れる。
#define TINYGLTF_IMPLEMENTATION
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "tiny_gltf.h"

#include <print>
#include <string>

int main() {
  tinygltf::TinyGLTF loader;
  tinygltf::Model model;
  std::string err;
  std::string warn;

  // .glb（バイナリ）を読む。.gltf（テキスト）なら LoadASCIIFromFile。
  const bool ok = loader.LoadBinaryFromFile(&model, &err, &warn, "model.glb");
  if (!warn.empty()) std::println("警告: {}", warn);
  if (!err.empty()) std::println("エラー: {}", err);
  if (!ok) return 1;

  std::println("メッシュ: {} 個、マテリアル: {} 個、テクスチャ: {} 枚", model.meshes.size(), model.materials.size(),
               model.textures.size());
}
```

数が出れば、導入は成功です。`LoadBinaryFromFile` は、成功で `true` を返し、失敗の理由は `err` に入ります。<strong>必ず、`err` と `warn` を表示</strong>します（ファイルが見つからない、拡張子が違う、などが、ここに出ます）。

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2005`（関数が、すでに定義されている） | `TINYGLTF_IMPLEMENTATION` を、複数の `.cpp` に書いた | 専用の `.cpp` 1 つだけに書く |
| `LNK2019`（未解決の外部シンボル）。`tinygltf::TinyGLTF::LoadBinaryFromFile` など | 実装を、どの `.cpp` にも書いていない | `TINYGLTF_IMPLEMENTATION` を書いた `.cpp` を、プロジェクトに追加 |
| `C1083`（`json.hpp` を開けない） | `json.hpp`（nlohmann/json）が、見つからない | `third_party/tinygltf/` に置く。または、vcpkg の nlohmann-json を使う |
| `stb_image` の、二重定義 | プロジェクトが、すでに `STB_IMAGE_IMPLEMENTATION` を、持っている | `TINYGLTF_NO_STB_IMAGE` を定義し、自分の `stb_image` を使う（画像の読み込みを、自分で行う） |
| `C2589`、`C2059`（`min` や `max` 周辺） | `<windows.h>` の、マクロとの衝突 | `NOMINMAX` を定義 |
| `C4996`（非推奨の関数） | 古い C の関数 | `_CRT_SECURE_NO_WARNINGS` を定義するか、警告を、個別に無効化 |

## CMake で使う

vcpkg で入れた場合の、CMake の書き方です。

```cmake
find_package(tinygltf CONFIG REQUIRED)
target_link_libraries(MyGame PRIVATE tinygltf::tinygltf)
```

ヘッダーのみのライブラリですが、`TINYGLTF_IMPLEMENTATION` を書いた `.cpp` が、必要な点は、同じです。

## バージョンを固定する

glTF のライブラリは、バージョンで、挙動や API が変わります。<strong>再現性のあるビルド</strong>のために、バージョンを固定します。

| 方法 | 内容 |
| --- | --- |
| ファイルを置く | リポジトリに、ヘッダーを、そのまま、コミットする（バージョンが、固定される） |
| vcpkg（マニフェスト） | `vcpkg.json` の `builtin-baseline` に、vcpkg の、コミット ハッシュを書く |
| FetchContent | `GIT_TAG` に、タグ（`v2.9.x`）、またはコミット ハッシュを書く |
''', before="## 関連ページ")

# ---------------------------------------------------------------- ufbx
pg.Add(L + "ufbx/install.md", '''
## 動作確認：FBX を 1 つ読んでみる

`.fbx` ファイルを 1 つ用意して、次のプログラムで、読めるかを確かめます。

```cpp
#include <print>

#include "ufbx.h"

int main() {
  ufbx_load_opts opts = {};                                        // 既定の設定（すべて 0）
  ufbx_error error;
  ufbx_scene* scene = ufbx_load_file("model.fbx", &opts, &error);
  if (!scene) {
    std::println("読み込みに失敗: {}", error.description.data);    // 理由が、文字列で入る
    return 1;
  }

  std::println("メッシュ: {} 個、ノード: {} 個、マテリアル: {} 個", scene->meshes.count, scene->nodes.count,
               scene->materials.count);

  ufbx_free_scene(scene);                                           // 使い終わったら、必ず、解放する
}
```

`ufbx_load_file` は、失敗すると `nullptr` を返し、理由が `error.description` に入ります。<strong>戻り値の確認が、必須</strong>です。読めたシーンは、`ufbx_free_scene` で、解放します（`ComPtr` のような、自動解放は、ないので、`std::unique_ptr` に、カスタム デリーターを、付けると、安全です）。

```cpp
// 解放を、自動にする。
struct SceneDeleter { void operator()(ufbx_scene* s) const { ufbx_free_scene(s); } };
using ScenePtr = std::unique_ptr<ufbx_scene, SceneDeleter>;
```

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `C1010`（プリコンパイル済みヘッダーを、探している間に、ファイルの終わり） | `ufbx.c` に、プリコンパイル済みヘッダー（`pch.h`）の設定が、掛かっている | `ufbx.c` のプロパティで、<strong>プリコンパイル済みヘッダー → 使用しない</strong> |
| `LNK2019`（`ufbx_load_file` が未解決） | `ufbx.c` を、プロジェクトに、追加していない | ソリューション エクスプローラーで、`ufbx.c` を追加 |
| `ufbx.c` が、C++ としてコンパイルされて、大量のエラー | ファイルのプロパティで、コンパイル言語が、C++ に、なっている | <strong>C/C++ → 詳細設定 → コンパイル言語</strong>を、「既定」（`.c` は C として）にする |
| `C4244` などの、警告が大量 | ufbx の、内部コード | `ufbx.c` だけ、警告レベルを下げる（`/W3`）。自分のコードには、影響しない |
| 読み込みが遅い（Debug） | ufbx は、最適化が、効かないと遅い | Debug でも、`ufbx.c` だけ、最適化（`/O2`）を、有効にする |

## ビルドの、時間を抑える

`ufbx.c` は、1 ファイルで、数万行あるので、<strong>変更しないファイル</strong>です。プロジェクトを、整理するときは、`ufbx.c` を、静的ライブラリに、分けるか、プリコンパイルを、避けて、再ビルドの対象から外します（[ビルド時間の最適化](../../optimize/build-time.md)）。
''', before="## 関連ページ")

# ---------------------------------------------------------------- jolt install
pg.Add(L + "jolt/install.md", '''
## 動作確認：Jolt を初期化してみる

導入できたかは、<strong>初期化と後始末だけ</strong>の、小さなプログラムで、確かめます。

```cpp
#include <Jolt/Jolt.h>

#include <Jolt/Core/Factory.h>
#include <Jolt/Core/Memory.h>
#include <Jolt/RegisterTypes.h>

#include <print>

JPH_SUPPRESS_WARNINGS                                      // Jolt のヘッダーが出す、警告を、抑える

int main() {
  JPH::RegisterDefaultAllocator();                         // メモリ確保の関数を、登録（最初に 1 回）
  JPH::Factory::sInstance = new JPH::Factory();            // 型の登録に、必要な、ファクトリー
  JPH::RegisterTypes();                                    // Jolt の、標準の型（形状、制約など）を、登録

  std::println("Jolt を、初期化できました");

  JPH::UnregisterTypes();                                  // 後始末（逆の順序）
  delete JPH::Factory::sInstance;
  JPH::Factory::sInstance = nullptr;
}
```

この 3 つ（アロケーターの登録、ファクトリー、型の登録）は、<strong>Jolt を、何かに使う前に、必ず 1 回</strong>行う、決まりの手順です。メッセージが出て、クラッシュしなければ、導入は、成功です（[世界の初期化と更新](system.md)）。

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2038`（`_ITERATOR_DEBUG_LEVEL` の、不一致） | `Jolt.lib` を、Release で作ったのに、自分のプロジェクトが Debug（または、逆） | Debug と Release の、両方で、`Jolt.lib` を作り、構成ごとに、正しいほうを、リンクする |
| `LNK2038`（`RuntimeLibrary` の、不一致） | `/MD` と `/MT` の、取り違え | Jolt のビルドと、自分のプロジェクトで、ランタイム ライブラリを、そろえる（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)） |
| 実行時に、原因の分からない、クラッシュ | `JPH_DEBUG_RENDERER` などの、定義が、ライブラリと、自分のプロジェクトで、違う | 定義を、ライブラリのビルドと、そろえる。CMake の `Jolt` ターゲットを、使えば、自動で、そろう |
| `LNK2019`（`JPH::…` が、未解決） | `Jolt.lib` を、リンクしていない | 追加の依存ファイルに `Jolt.lib` |
| `C1083`（`Jolt/Jolt.h` を、開けない） | インクルード ディレクトリが、違う | `Jolt` フォルダーの、<strong>親</strong>を、指定する（`JoltPhysics` のルート） |
| `C4324` などの、警告が大量 | Jolt の、アラインメント指定 | `JPH_SUPPRESS_WARNINGS` を、`#include` の後に書く |

## C++ の、設定

Jolt は、C++17 以降が、必要です。プロジェクトの、<strong>C++ 言語標準</strong>を、`/std:c++17` 以上（このサイトでは `/std:c++latest`）にします（[C++23 を使えるようにする設定](../../vs/terms/index.md)）。

| 設定 | 値 |
| --- | --- |
| C++ 言語標準 | `/std:c++17` 以上 |
| 浮動小数点モデル | `/fp:precise`（既定）。`/fp:fast` は、再現性を、壊すことがある |
| 例外 | 無効でも、有効でも、動く（Jolt は、例外を使わない）。ライブラリと、そろえる |
| RTTI | Jolt は、独自の、型情報を使うので、不要 |

## バージョンを固定する

物理演算は、バージョンで、<strong>挙動の細部</strong>（接触の、解決の順序、数値の、誤差）が変わります。リプレイや、ネットワークの、同期（決定論）を、使うなら、バージョンを、固定します。

| 方法 | 内容 |
| --- | --- |
| Git のタグ | `v5.3.0` など、タグを、指定して、`git checkout` する |
| vcpkg（マニフェスト） | `vcpkg.json` の `builtin-baseline` で、固定 |
| FetchContent | `GIT_TAG` に、タグ（またはコミット ハッシュ） |
''', before="## 関連ページ")

# ---------------------------------------------------------------- imgui install
pg.Add(L + "imgui/install.md", '''
## 動作確認：コンパイルとリンクの確認

導入できたかを、まず、<strong>ImGui の、バージョンを、表示する</strong>だけで、確かめます。画面に、何かを出す前に、リンクの段階で、問題がないかを、見られます。

```cpp
#include <print>

#include "imgui.h"

int main() {
  IMGUI_CHECKVERSION();                                    // ヘッダーと、ライブラリの、バージョンが、合っているかを確認
  ImGuiContext* context = ImGui::CreateContext();
  std::println("Dear ImGui {}", ImGui::GetVersion());      // 例: 1.91.x
  ImGui::DestroyContext(context);
}
```

`IMGUI_CHECKVERSION()` は、<strong>ヘッダーと、コンパイルした `.cpp` の、バージョンが、食い違っていないか</strong>を、実行時に、確かめます（食い違うと、アサートで止まる）。バージョンが、表示されれば、ImGui 本体の導入は、成功です。次に、バックエンド（DX11、Win32）を、足して、画面に、出します（[仕組みと最小のコード](basics.md)）。

## 追加するファイル

ソースを入れる場合、プロジェクトに、次のファイルを、追加します。

| 区分 | ファイル | 役割 |
| --- | --- | --- |
| 本体 | `imgui.cpp`、`imgui_draw.cpp`、`imgui_tables.cpp`、`imgui_widgets.cpp` | ImGui の中核 |
| バックエンド（Windows） | `imgui_impl_win32.cpp` | ウィンドウ、入力 |
| バックエンド（DX11） | `imgui_impl_dx11.cpp` | 描画 |
| バックエンド（DX12） | `imgui_impl_dx12.cpp` | 描画（DX12 のとき） |
| デモ（任意） | `imgui_demo.cpp` | `ImGui::ShowDemoWindow()` が使える。使い方を、学ぶのに、便利 |

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2019`（`ImGui::…` が未解決） | `imgui.cpp` などを、プロジェクトに、追加していない | 上の表のファイルを、全部、追加する |
| `LNK2019`（`ImGui_ImplWin32_…` が未解決） | バックエンドの `.cpp` を追加していない | `imgui_impl_win32.cpp` と `imgui_impl_dx11.cpp` を追加 |
| `C1083`（`imgui_impl_win32.h` を開けない） | バックエンドは、`backends/` フォルダーにある | インクルード ディレクトリに、`backends` も、追加 |
| `IM_ASSERT` で止まる（起動時） | `IMGUI_CHECKVERSION` の食い違い、または、`CreateContext` の前に、ImGui の関数を呼んだ | ヘッダーと `.cpp` を、同じバージョンにする。`CreateContext` を、最初に呼ぶ |
| 日本語が、`???` になる | 既定のフォントに、日本語が、入っていない | 日本語フォントを、読み込む（[フォント](fonts.md)） |

## バージョンの、注意

ImGui は、バージョンが、上がると、<strong>バックエンドの、API が、変わる</strong>ことがあります。本体（`imgui.cpp`）と、バックエンド（`imgui_impl_*.cpp`）は、<strong>同じバージョン</strong>の、組み合わせで使います。別々の場所から、取得すると、食い違いやすいので、同じ、リポジトリ（同じタグ）から、まとめて、取得します。
''', before="## 関連ページ")

# ---------------------------------------------------------------- fastgltf
pg.Add(L + "fastgltf/install.md", '''
## 動作確認の、チェックリスト

fastgltf は、バージョンで、API が、変わるので、動作確認の、コードは、[クイックスタート](quickstart.md) の、バージョンに合わせた、ものを使います。導入の段階では、次の 5 つを、確かめます。

| 確認 | 見るところ |
| --- | --- |
| ① C++ 標準 | プロジェクトの、C++ 言語標準が、`/std:c++17` 以上 |
| ② ヘッダーが、見える | `#include <fastgltf/core.hpp>` が、通る |
| ③ ライブラリが、リンクされる | `fastgltf.lib`（と、simdjson）が、リンクに含まれる。vcpkg か CMake なら、自動 |
| ④ ランタイムが、そろう | fastgltf の、ビルドと、自分のプロジェクトで、`/MD` か `/MT` が、同じ |
| ⑤ 1 つのファイルを、読める | `.glb` を、1 つ、読んで、メッシュの数を、表示（クイックスタート） |

## よくあるエラー（導入編）

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2019`（`fastgltf::…` が未解決） | ライブラリを、リンクしていない | CMake なら `target_link_libraries(… fastgltf::fastgltf)`、手動なら、`fastgltf.lib` と `simdjson.lib` |
| `C1083`（`fastgltf/core.hpp` を、開けない） | インクルード ディレクトリの、設定が違う | `include` フォルダーの、パスを、追加 |
| C++ の、構文エラーが、大量に出る | C++ の標準が、古い | `/std:c++17` 以上に |
| `LNK2038`（ランタイムの、不一致） | `/MD` と `/MT` の、取り違え | そろえる（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)） |
| 古い記事の、コードが、動かない | fastgltf の、API が、バージョンで、変わった | 導入した、バージョンの、ドキュメントと、サンプルを、見る |

## バージョンを固定する

fastgltf は、更新が、活発で、<strong>API が、予告なく、変わる</strong>ことがあります。タグ（またはコミット）を、固定します。

| 方法 | 内容 |
| --- | --- |
| vcpkg（マニフェスト） | `vcpkg.json` の `builtin-baseline` で固定 |
| FetchContent | `GIT_TAG` に、タグを書く |
| ソースを入れる | リポジトリに、コミットする |
''', before="## 関連ページ")
print("ok")
