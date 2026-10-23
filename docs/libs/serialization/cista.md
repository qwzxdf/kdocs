---
title: cista（バイナリ・ゼロコピー）
tags:
  - 外部ライブラリ
  - シリアライズ
---

# cista（バイナリ・ゼロコピー）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17〜</span>
`#include <cista/serialization.h>`
</div>

**cista**（チスタ）は、読み込みで一切コピーしない（ゼロコピー） バイナリシリアライザです。普通のシリアライザは、ファイルのバイト列を読んで、`std::string` や `std::vector` を作り直します（メモリを確保して中身をコピーする）。cista は、保存するときに「メモリ上の形そのまま」をバイト列にしておくので、読み込みはバイト列の先頭をその型のポインタとして見るだけです。100 MB のデータでも、メモリマップ（ファイルをメモリのように見せる OS の機能）と組み合わせれば、ほぼ一瞬で使い始められます。その代わり、`std::string` や `std::vector` は使えず、cista 専用のコンテナ（`cista::offset::string`、`cista::offset::vector` など）でデータを作る必要があります。巨大なワールドデータ、ナビメッシュ、ゲームのアセットのまとめファイルなど、「大きくて、読むだけのデータを、とにかく速く読みたい」ときの最終手段です。

!!! tip "ポイント"
    - <strong>巨大で、ロード後は読むだけのデータに使う。</strong> 読み込みは「ポインタとして見るだけ」なので、データが大きいほど他との差が出る。
    - データは **`cista::offset::string` / `cista::offset::vector` など専用の型**で作る。`std::string` は使えない。
    - 保存は `cista::serialize<モード>(obj)`、読み込みは `cista::deserialize<T, モード>(buffer)`（`T*` が返る）。
    - 返ったポインタはバッファの中を指している。バッファを消すと使えない。
    - モードには `WITH_VERSION`<strong>（型のチェック）と </strong>`WITH_INTEGRITY`<strong>（チェックサム）を付けるのが基本。信用できないデータには </strong>`DEEP_CHECK`。
    - 普通のセーブデータなら、[cereal](cereal.md) や [zpp_bits](zpp-bits.md) の方が扱いやすい。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md)、[キャッシュ効率](../../basics/cache.md)、[未定義動作](../../basics/ub.md) を先に読むと、cista が何をしているか、何が危ないかが分かります。比較のために [zpp_bits](zpp-bits.md) も読んでおくのがおすすめです。

## ゼロコピーとは

普通のシリアライザと cista の読み込みを比べます。

<div class="anim" data-type="graph" data-label="普通のシリアライザと cista の読み込み">
n file ファイル 0 0
n buf バイト列 1 0
n obj 作り直した_vector_string 3 0
# 普通のシリアライザ：ファイルを読み込む
---
n file ファイル 0 0 hit
n buf バイト列 1 0 hit
n obj 作り直した_vector_string 3 0 new
l file buf hit 読む
l buf obj new 解析して作り直す
# バイト列を解析して、vector や string を新しく作る（確保とコピーが、要素ごとに起きる）
---
n file ファイル 0 1
n buf バイト列 1 1 hit
n view 先頭を_T*_として見る 3 1 hit
l file buf hit 読む_または_mmap
l buf view hit 見るだけ
# cista：バイト列の先頭を、そのままポインタとして見る。作り直しもコピーもない
</div>


cista の `cista::offset::vector` は、中身の場所を<strong>ポインタではなく「自分からの距離（オフセット）」</strong> で覚えています。保存するときに、中身を全部 1 つのバイト列の中に並べ、距離を書いておきます。読み込むときは、バイト列がメモリのどこに置かれても、距離で中身を見つけられるので、何も作り直さずにそのまま使えます。

<svg class="fig flow" viewBox="0 0 514 280" role="img" aria-label="cista：中身は、自分からの距離（オフセット）で覚える"><defs><marker id="fl17801" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">cista：中身は、自分からの距離（オフセット）で覚える</text><line x1="107.0" y1="138.0" x2="332.0" y2="83.1" stroke="currentColor" stroke-width="2" marker-end="url(#fl17801)"/><text x="219.5" y="104.6" text-anchor="middle" style="font-size:12px">name +28バイト先</text><line x1="107.0" y1="158.0" x2="336.5" y2="214.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl17801)"/><text x="221.8" y="180.0" text-anchor="middle" style="font-size:12px">items +33バイト先 3個</text><rect x="28.0" y="128.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Player</text><rect x="335.0" y="44.0" width="151" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="410.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">"Alice" （5文字）</text><rect x="339.5" y="212.0" width="142" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="410.5" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">101 | 205 | 330</text><rect x="168.0" y="128.0" width="103" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="219.5" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">level = 12</text></svg>

距離の数字は、イメージです。

## 導入

### Visual Studio で導入する（最初に読む）

Visual Studio を使っているなら、ここから読みます。ライブラリを入れる基本の手順は [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md) にまとめています。ここでは cista だけの部分を書きます。

=== "ファイルを置く"

    1. [リリースページ](https://github.com/felixguendling/cista/releases) の **`cista.h`**（全部を 1 ファイルにまとめたもの）を `third_party/cista/` に置く（その場合は `#include "cista.h"` と書く）
    2. プロジェクトのプロパティを開き（[画面つきの手順](../../vs/include-dirs.md#additional)）、構成を すべての構成、プラットフォームを x64 にする
    3. C/C++ → 全般 → 追加のインクルード ディレクトリ に、`$(SolutionDir)third_party\cista` を追加する
    4. `#include <cista/serialization.h>` と書いてビルドする

=== "vcpkg"

    1. 初回だけ、Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install cista:x64-windows
        ```

        （マニフェスト モードなら、`vcpkg.json` の `dependencies` に `"cista"` を足す）
    3. プロジェクトには何も設定せずに、`#include <cista/serialization.h>` と書けば使える

!!! note "C++ の設定"
    C++17 以上が必要です。メモリマップ（`cista::mmap`）は、Windows でもそのまま使えます。

### そのほかの方法（CMake など）

ヘッダオンリーです。C++17 以上が必要です。

=== "1 ファイル版"

    [リリースページ](https://github.com/felixguendling/cista/releases) から `cista.h`（全部を 1 ファイルにまとめたもの）をダウンロードして、プロジェクトに置きます。その場合は `#include "cista.h"` と書きます。

=== "CMake FetchContent"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      cista
      GIT_REPOSITORY https://github.com/felixguendling/cista.git
      GIT_TAG master  # 本番ではタグを固定する
      GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(cista)
    target_link_libraries(my_game PRIVATE cista)
    ```

=== "vcpkg"

    ```text
    vcpkg install cista
    ```

    ポートの名前やターゲット名は vcpkg のバージョンで変わることがあるので、`vcpkg search cista` で確認します。

## offset モードと raw モード

cista には、データの持ち方が 2 種類あります。名前空間で選びます。

| モード | 名前空間 | 中身の場所の覚え方 | 読み込み | メモリマップ（読み込み専用） |
| --- | --- | --- | --- | --- |
| **offset** | `cista::offset` | 自分からの距離 | 本当に何もしない | 使える |
| raw | `cista::raw` | 普通のポインタ | 保存時の距離をポインタに直す（バッファを書き換える） | 使えない |

- offset は、アクセスのたびに「自分の場所 + 距離」の足し算が入りますが、ほとんど気にならない差です。メモリマップと組み合わせられるので、基本は offset を使います。
- raw は、読み込んだ後のアクセスがほんの少し速くなります。普通のポインタなので、デバッガで中身を見やすいという利点もあります。

このページでは `namespace data = cista::offset;` と書いて、offset モードを使います。

## 関数一覧

| 関数・型 | 重要度 | 何をする |
| --- | --- | --- |
| [`serialize`](#serialize) | <span class="rank rank-must">必須</span> | オブジェクトをバイト列にする |
| [`deserialize`](#deserialize) | <span class="rank rank-must">必須</span> | バイト列をそのまま `T*` として使えるようにする |
| [`offset::string`](#offset_string) | <span class="rank rank-must">必須</span> | cista 用の文字列 |
| [`offset::vector`](#offset_vector) | <span class="rank rank-must">必須</span> | cista 用の可変長配列 |
| [`mode`](#mode) | <span class="rank rank-must">必須</span> | 型のチェック・チェックサムなどの設定 |
| [`offset::hash_map`](#offset_hash_map) | <span class="rank rank-often">よく使う</span> | cista 用のハッシュマップ |
| [`mmap`](#mmap) | <span class="rank rank-often">よく使う</span> | ファイルをメモリマップする |
| [`buf`](#buf) | <span class="rank rank-often">よく使う</span> | mmap などに書き込むためのバッファ |
| [`offset::hash_set`](#offset_hash_set) | <span class="rank rank-sometimes">たまに</span> | cista 用のハッシュセット |
| [`offset::unique_ptr`](#offset_unique_ptr) | <span class="rank rank-sometimes">たまに</span> | cista 用の unique_ptr |
| [`offset::ptr`](#offset_ptr) | <span class="rank rank-sometimes">たまに</span> | データの中の別の要素を指すポインタ |
| [`offset::array`](#offset_array) | <span class="rank rank-sometimes">たまに</span> | 固定長の配列 |
| [`offset::optional`](#offset_optional) | <span class="rank rank-rare">知ってるだけ</span> | 値があるかないか |
| [`offset::variant`](#offset_variant) | <span class="rank rank-rare">知ってるだけ</span> | 複数の型のどれか |
| [`cista_members`](#cista_members) | <span class="rank rank-sometimes">たまに</span> | 集成体でないクラスのメンバを教える |
| [`type_hash`](#type_hash) | <span class="rank rank-rare">知ってるだけ</span> | 型の形から計算したハッシュ値 |

## よくある使い方

```cpp
#include <print>

#include <cista/serialization.h>

namespace data = cista::offset;

// std::string / std::vector ではなく cista の型を使う
struct Player {
  data::string name;
  int level = 1;
  data::vector<int> items;
};

int main() {
  // 型のチェックとチェックサムを付ける
  constexpr auto kMode = cista::mode::WITH_VERSION | cista::mode::WITH_INTEGRITY;

  Player player;
  player.name = "Alice";
  player.level = 12;
  player.items.push_back(101);
  player.items.push_back(205);
  player.items.push_back(330);

  cista::byte_buf buffer = cista::serialize<kMode>(player);  // std::vector<std::uint8_t>

  // 作り直さない：buffer の中をそのまま Player として見る
  Player* loaded = cista::deserialize<Player, kMode>(buffer);
  std::println("{} Lv.{} アイテム {} 個", loaded->name.view(), loaded->level,
               loaded->items.size());
  for (int id : loaded->items) {
    std::println("  {}", id);
  }
}
```

```text title="実行結果"
Alice Lv.12 アイテム 3 個
  101
  205
  330
```

`loaded` は `buffer` の**中を指すポインタ**です。`delete` してはいけませんし、`buffer` を消したり、`buffer` に要素を足して中身が引っ越したりすると使えなくなります。

### メモリマップで巨大なデータを一瞬で読む

cista が本当に力を発揮するのは、メモリマップと組み合わせたときです。メモリマップを使うと、ファイルを読み込まずに「メモリにあるかのように」見せられます。実際にファイルから読まれるのはアクセスしたページ（4 KB ずつ）だけなので、1 GB のデータでも、使い始めるまでの時間はほぼゼロです。

```cpp
#include <cista/mmap.h>
#include <cista/serialization.h>

namespace data = cista::offset;

constexpr auto kMode = cista::mode::WITH_VERSION;

struct NavNode {
  float x = 0.0f;
  float y = 0.0f;
  data::vector<std::uint32_t> neighbors;  // つながっているノードの番号
};

struct NavMesh {
  data::vector<NavNode> nodes;
  data::hash_map<data::string, std::uint32_t> named_points;  // "spawn" -> ノード番号
};

// ツール側：保存する
void BuildNavMesh(const NavMesh& mesh, const char* path) {
  cista::buf file{cista::mmap{path}};  // 書き込み用にファイルをマップ
  cista::serialize<kMode>(file, mesh);
}

// ゲーム側：読み込む（ほぼ一瞬）
class NavMeshAsset {
 public:
  explicit NavMeshAsset(const char* path)
      : file_(path, cista::mmap::protection::READ),
        mesh_(cista::deserialize<NavMesh, kMode>(file_)) {}

  const NavMesh& mesh() const { return *mesh_; }

 private:
  cista::mmap file_;  // mesh_ より先に宣言する（先に作られ、後に消える）
  NavMesh* mesh_;
};
```

`NavMeshAsset` のように、バッファ（mmap）とポインタを 1 つのクラスで一緒に持つと、「バッファが先に消える」というミスを防げます。メンバは宣言した順に作られ、逆の順に消えるので、バッファを先に宣言します。

## cista のコンテナ

cista のデータには、`std::` のコンテナの代わりに、次の型を使います（`data` は `cista::offset` の別名）。

| cista の型 | 代わりになる std の型 | 備考 |
| --- | --- | --- |
| `data::string` | `std::string` | `.view()` で `std::string_view`、`.str()` で `std::string` |
| `data::vector<T>` | `std::vector<T>` | `push_back`、`size`、範囲 for など普通に使える |
| `data::hash_map<K, V>` | `std::unordered_map<K, V>` | 速いハッシュマップ（Swiss Table 方式） |
| `data::hash_set<T>` | `std::unordered_set<T>` | |
| `data::array<T, N>` | `std::array<T, N>` | |
| `data::unique_ptr<T>` | `std::unique_ptr<T>` | `data::make_unique<T>(...)` で作る |
| `data::ptr<T>` | `T*` | データの中の別の要素を指す（所有しない） |
| `data::optional<T>` | `std::optional<T>` | |
| `data::variant<T...>` | `std::variant<T...>` | |
| `data::tuple<T...>` / `data::pair<A, B>` | `std::tuple` / `std::pair` | |
| `data::bitset<N>` | `std::bitset<N>` | |
| `int`、`float`、enum、ネストした構造体 | そのまま | |

!!! warning "使えないもの"
    - `std::string`、`std::vector`、`std::map` など、**中身をヒープに持つ std の型**は使えません（ポインタの値が保存されてしまうため、コンパイルエラーか、壊れたデータになります）。
    - 仮想関数を持つクラス（vtable のポインタがあるため）。
    - 普通のポインタ `T*`（offset モードでは `data::ptr<T>` を使う）。

ゲーム本体で `std::` の型を使っているなら、保存用の構造体を別に作って変換するのが現実的です。

## データの形のチェックと安全性

cista は、読み込みのときに**何も作り直さない**ので、壊れたデータや形の違うデータを読むと、そのままでたらめなメモリを指すことになります。それを防ぐために、モードでチェックを付けます。

| モード | チェックすること | 重さ |
| --- | --- | --- |
| `WITH_VERSION` | 型の形から計算したハッシュを先頭に書き、読むときに比べる | ほぼ無し |
| `WITH_INTEGRITY` | データ全体のチェックサムを書き、読むときに計算して比べる | データの大きさに比例 |
| `DEEP_CHECK` | 中のすべての距離・大きさが、バッファの範囲内に収まっているか調べる | 重い（全体を見る） |
| `UNCHECKED` | 範囲のチェックを全部やめる | 最速。自分で作ったデータだけに |

- 自分のツールで作って、ゲームに同梱するデータ → `WITH_VERSION`（必要なら `WITH_INTEGRITY`）
- プレイヤーのパソコンに保存されるデータ（壊れる・書き換えられるかもしれない） → `WITH_VERSION | WITH_INTEGRITY | DEEP_CHECK`
- ネットワークから来るデータ → `DEEP_CHECK` は必須

チェックに失敗すると、例外（`std::exception` の子）が投げられます。

!!! danger "信用できないデータを DEEP_CHECK なしで読まない"
    cista のデータの中の「距離」は、そのまま「どこのメモリを読むか」になります。悪意のあるデータで距離が書き換えられていると、関係のないメモリを読んだり書いたりできてしまいます（セキュリティの穴になります）。

## バージョン管理

cista には、データの形を変えたときに古いデータを読む仕組みは**ありません**。`WITH_VERSION` は「形が違う」ことを検出するだけです。

cista を使うデータは、普通「ツールで作って、ゲームと一緒に配るデータ」なので、形を変えたら、ツールでデータを作り直すのが基本の運用です。

<svg class="fig flow" viewBox="0 0 900 112" role="img" aria-label="ビルド時に変換して、ゲームでは一瞬で読む"><defs><marker id="fl42607" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ビルド時に変換して、ゲームでは一瞬で読む</text><line x1="233.0" y1="64.0" x2="291.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42607)"/><line x1="485.0" y1="64.0" x2="543.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42607)"/><text x="514.0" y="58.0" text-anchor="middle" style="font-size:12px">形が変わったら作り直す</text><line x1="691.0" y1="64.0" x2="749.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl42607)"/><text x="720.0" y="58.0" text-anchor="middle" style="font-size:12px">ゲームと一緒に配る</text><rect x="28.0" y="44.0" width="202" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="129.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">元データ （JSON / YAML）</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="294.0" y="44.0" width="188" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="388.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">変換ツール （ビルド時）</text><circle cx="296.0" cy="46.0" r="10" fill="#2ea043"/><text x="296.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="546.0" y="44.0" width="142" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="617.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">cista のバイナリ</text><circle cx="548.0" cy="46.0" r="10" fill="#e5a828"/><text x="548.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="752.0" y="44.0" width="120" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="812.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ゲームで mmap</text><circle cx="754.0" cy="46.0" r="10" fill="#e5484d"/><text x="754.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

プレイヤーのセーブデータのように「形が変わっても古いデータを読みたい」ものには、cista は向いていません。[cereal](cereal.md) や [struct_pack](struct-pack.md) を使います。

## 速さの特徴

| 項目 | 特徴 |
| --- | --- |
| 読み込み | **データの大きさに関係なく**ほぼ一瞬（`WITH_INTEGRITY` や `DEEP_CHECK` を付けると、全体を見るぶん時間がかかる） |
| メモリマップ | アクセスした部分だけファイルから読まれる。起動が速い。複数のプロセスで共有もできる |
| 保存 | 普通のシリアライザと同じくらい（中身を 1 つのバッファに並べ直す） |
| アクセス | offset モードは足し算が 1 回増えるが、ほとんど差は無い |
| サイズ | メモリ上の形そのままなので、パディング（構造体の隙間）も含めて保存される。zpp_bits などより大きくなりがち |

!!! note "どのくらいのデータから意味がある？"
    数 MB くらいまでなら、[zpp_bits](zpp-bits.md) や [struct_pack](struct-pack.md) でも一瞬で読めるので、cista の扱いにくさに見合わないことが多いです。数十 MB〜数 GB のデータ（オープンワールドの地形、巨大なナビメッシュ、大量のアセットの目次）で、本当にロード時間が問題になったときに検討します。

## 関数の詳しい説明

### serialize {#serialize}

```cpp
template <mode Mode = mode::NONE, typename T>
byte_buf serialize(T const& el);

template <mode Mode = mode::NONE, typename Target, typename T>
void serialize(Target& t, T const& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Mode` | 型引数 | チェックなどの設定（[mode](#mode)） |
| `el` / `value` | `T&` | 保存するオブジェクト |
| `t` | `cista::buf<...>&` | 書き込み先（`cista::buf<cista::mmap>`、`cista::buf<std::vector<std::uint8_t>>` など） |

- **戻り値:** 1 つ目は `cista::byte_buf`（`std::vector<std::uint8_t>`）
- 中身を 1 つのバイト列に並べ、中のポインタを「距離」に直して書きます。

### deserialize {#deserialize}

```cpp
template <typename T, mode Mode = mode::NONE, typename Container>
T* deserialize(Container& c);

template <typename T, mode Mode = mode::NONE>
T* deserialize(std::uint8_t* from, std::uint8_t* to);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型引数 | 読む型 |
| `Mode` | `mode` | 保存したときと同じモード |
| `c` | `cista::byte_buf` など | バイト列（`cista::byte_buf`、`cista::mmap` など） |
| `from`, `to` | `const uint8_t*` | バイト列の先頭と終わり |

- 戻り値: バッファの中を指す `T*`。コピーではない
- 例外: モードのチェックに失敗すると例外
- 返ったポインタは `delete` しません。バッファより長く使ってはいけません。
- バッファは、型に合ったアラインメント（並びの区切り）で置かれている必要があります。`std::vector` や mmap の先頭なら大丈夫ですが、別のデータの途中に埋め込むときは注意します。

### offset::string {#offset_string}

```cpp
struct basic_string {
  basic_string(char const* s);
  basic_string& operator=(char const* s);
  std::string_view view() const;
  std::string str() const;
  char const* data() const;
  std::size_t size() const;
  bool empty() const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `std::string_view` | 中身にする文字列（コピーされる） |

- cista 用の文字列です。短い文字列（15 文字くらいまで）はヒープを使わずに中に持ちます。
- 表示や比較には `.view()` で `std::string_view` にして使います。`std::string` が欲しいときは `.str()`。

### offset::vector {#offset_vector}

```cpp
template <typename T>
struct vector {
  void push_back(T const& el);
  template <typename... Args> T& emplace_back(Args&&... args);
  void reserve(std::size_t new_size);
  void resize(std::size_t size);
  std::size_t size() const;
  T& operator[](std::size_t index);
  T* begin();
  T* end();
};
```

- `std::vector` とほぼ同じように使えます。範囲 for やアルゴリズムも使えます。
- 読み込んだデータの中の vector は、バッファの中を指しているだけです。読み込んだ後は、読むだけにするのが安全です。

### mode {#mode}

```cpp
enum class mode {
  NONE = 0,
  UNCHECKED = 1 << 0,
  WITH_VERSION = 1 << 1,
  WITH_INTEGRITY = 1 << 2,
  SERIALIZE_BIG_ENDIAN = 1 << 3,
  DEEP_CHECK = 1 << 4,
  CAST = 1 << 5,
  /* ... */
};
```

- `|` で組み合わせます（`cista::mode::WITH_VERSION | cista::mode::WITH_INTEGRITY`）。
- 保存と読み込みで同じモードを使います。違うと読めないか、壊れます。
- 各フラグの意味は [フラグ・オプション](#flags) にまとめています。

### offset::hash_map {#offset_hash_map}

```cpp
template <typename Key, typename Value>
using hash_map = /* Swiss Table 方式のハッシュマップ */;
```

- `std::unordered_map` と同じように `find`、`operator[]`、`emplace`、範囲 for が使えます。
- キーに `data::string` を使うと、`std::string_view` で探せます（文字列を作らずに探せる）。
- 読み込んだデータでも、ハッシュ表を作り直さずにそのまま検索できるのが cista の大きな利点です。

### mmap {#mmap}

```cpp
struct mmap {
  enum class protection { READ, WRITE, MODIFY };
  explicit mmap(char const* path, protection = protection::WRITE);
  std::uint8_t* data();
  std::size_t size() const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `path` | `const char*` | ファイルのパス |
| `protection` | `cista::mmap::protection` | `READ`（読むだけ）、`WRITE`（新しく書く）、`MODIFY`（今のファイルを書き換える） |

- ファイルをメモリマップします。Windows でも Linux でも同じように使えます。
- `READ` でマップしたものは書き換えられないので、`deserialize` は offset モードで使います。
- オブジェクトが消えるとマップも外れるので、読み込んだデータを使っている間は残しておきます。

### buf {#buf}

```cpp
template <typename Buf = std::vector<std::uint8_t>>
struct buf {
  explicit buf(Buf&& buf);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buf` | `cista::mmap&` | 書き込み先（`cista::mmap` など） |

- `serialize` の書き込み先として使うための入れ物です。`cista::buf file{cista::mmap{"out.bin"}};` のように使います。

### offset::hash_set {#offset_hash_set}

```cpp
template <typename T>
using hash_set = /* Swiss Table 方式のハッシュセット */;
```

- `std::unordered_set` の代わりです。「このアイテムを持っているか」などの判定に使います。

### offset::unique_ptr {#offset_unique_ptr}

```cpp
template <typename T>
struct unique_ptr;

template <typename T, typename... Args>
unique_ptr<T> make_unique(Args&&... args);
```

- `std::unique_ptr` の代わりです。中身もバイト列に一緒に保存されます。
- 継承（ポリモーフィズム）には使えません（仮想関数を持つ型は保存できないため）。

### offset::ptr {#offset_ptr}

```cpp
template <typename T>
using ptr = offset_ptr<T>;
```

- データの中の別の要素を指す、所有しないポインタです。保存するときに、指している先も同じデータの中にある必要があります。
- 「ノードが別のノードを指す」グラフのようなデータを、ID ではなくポインタのまま保存できます。指している先がデータの中に無いと、保存のときに例外になります。

### offset::array {#offset_array}

```cpp
template <typename T, std::size_t Size>
using array = /* std::array と同じ */;
```

- 固定長の配列です。`std::array` と同じように使えます。数値だけの `std::array` は、そのまま使えることもあります。

### offset::optional {#offset_optional}

```cpp
template <typename T>
struct optional;
```

- `std::optional` の代わりです。`has_value()`、`value()`、`*` が使えます。

### offset::variant {#offset_variant}

```cpp
template <typename... T>
struct variant;
```

- `std::variant` の代わりです。`cista::get<T>(v)` や `v.apply(関数)` で中身を使います。

### cista_members {#cista_members}

```cpp
auto cista_members() { return std::tie(member1, member2, ...); }
```

- 集成体でない（コンストラクタがある、など）クラスで、保存するメンバを教えるメンバ関数です。集成体なら書かなくても自動で分かります。

```cpp
class Chunk {
 public:
  Chunk() = default;
  auto cista_members() { return std::tie(x_, y_, tiles_); }

 private:
  int x_ = 0;
  int y_ = 0;
  data::vector<std::uint16_t> tiles_;
};
```

### type_hash {#type_hash}

```cpp
template <typename T>
hash_t type_hash();
```

- 戻り値: 型の形（メンバの型と順番）から計算したハッシュ値
- `WITH_VERSION` で保存されるのはこの値です。ツールとゲームで型の形がそろっているかを、ログに出して確かめるときに使えます。

## フラグ・オプション {#flags}

| モード | 意味 |
| --- | --- |
| `cista::mode::NONE` | 何もしない（デフォルト） |
| `cista::mode::WITH_VERSION` | 型のハッシュを書き、読むときに確認する |
| `cista::mode::WITH_INTEGRITY` | チェックサムを書き、読むときに確認する |
| `cista::mode::DEEP_CHECK` | 読むときに、すべての距離と大きさがバッファ内か調べる |
| `cista::mode::UNCHECKED` | 範囲のチェックをすべてやめる（最速・危険） |
| `cista::mode::SERIALIZE_BIG_ENDIAN` | ビッグエンディアンで保存する |
| `cista::mode::CAST` | チェックを何もせず、ただポインタとして見る（`deserialize` で使う） |
| `cista::mode::SKIP_VERSION` / `SKIP_INTEGRITY` | 保存されているバージョン・チェックサムを、読むときに確認しない |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| オープンワールドの地形・チャンク | mmap して、必要な部分だけページインさせる |
| 巨大なナビメッシュ・経路のグラフ | `data::ptr` でノード同士をつないだまま保存 |
| アセットの目次（名前 → ファイル内の位置） | `data::hash_map` を作り直さずに検索 |
| 大量のマスターデータ | ビルド時に変換。ゲーム起動時は mmap だけ |
| 複数プロセスで同じデータを共有 | エディタとゲームで同じファイルを mmap |

## よくあるミス

??? failure "std::string や std::vector を使う"
    `struct Player { std::string name; };` を保存すると、文字列の中身ではなくヒープのポインタの値が保存されます。cista のデータには `data::string` / `data::vector` を使います。

??? failure "バッファより長くポインタを使う"
    `deserialize` が返すポインタは、バッファの中を指しています。`cista::byte_buf` をローカル変数で作って、ポインタだけ返すと、ダングリングポインタになります。バッファとポインタは 1 つのクラスで一緒に持ちます。

??? failure "保存と読み込みでモードが違う"
    `serialize<WITH_VERSION>` で保存したものを `deserialize<T>`（モード無し）で読むと、先頭のハッシュをデータとして読んでしまいます。同じ `constexpr auto kMode` を両方で使います。

??? failure "プレイヤーのセーブデータに使う"
    cista には古い形のデータを読む仕組みがありません。ゲームをアップデートして型の形が変わると、古いセーブは読めなくなります。セーブデータには [cereal](cereal.md) や [struct_pack](struct-pack.md) を使います。

??? failure "外から来たデータを DEEP_CHECK なしで読む"
    書き換えられたデータで、関係ないメモリを読み書きされてしまいます。信用できないデータには必ず `DEEP_CHECK` を付けます。

??? failure "32 ビットと 64 ビットでデータを共有する"
    メモリ上の形そのまま保存するので、`std::size_t` などの大きさや、構造体のパディングが違う環境では読めません。ツールとゲームは同じ環境（64 ビット、同じコンパイラ）でビルドします。

## 類似ライブラリ

| ライブラリ | 違い |
| --- | --- |
| FlatBuffers | ゼロコピーで読める定番。スキーマファイルを書いてコードを生成する。他の言語でも読める。フィールドの追加にも対応 |
| Cap'n Proto | ゼロコピーの通信用形式。スキーマとコード生成が必要 |
| Boost.Interprocess | 共有メモリやメモリマップの中にコンテナを作る。オフセットポインタの考え方は同じ |
| [zpp_bits](zpp-bits.md) / [struct_pack](struct-pack.md) | 読み込みでコピーするが、普通の std の型が使えて扱いやすい |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読み込みはコピーしない（ゼロコピー）。巨大な読み込み専用データ向け
    - [x] `cista::offset` の型（`string`、`vector`、`hash_map`）でデータを作る
    - [x] `serialize<kMode>` で保存、`deserialize<T, kMode>` で `T*` を受け取る
    - [x] 返ったポインタはバッファの中。バッファと一緒に持つ
    - [x] `WITH_VERSION` を基本に、信用できないデータには `DEEP_CHECK`
    - [x] 形が変わったらデータを作り直す運用。セーブデータには使わない

## 関連ページ

- [シリアライズの概要](../../engine/serialization/index.md)
- [zpp_bits（バイナリ・速さ重視）](zpp-bits.md)
- [yalantinglibs（struct_pack）](struct-pack.md)
- [ポインタ](../../basics/pointer.md)
- [キャッシュ効率](../../basics/cache.md)
- [cista（GitHub）](https://github.com/felixguendling/cista)
- [cista 公式サイト](https://cista.rocks/)
