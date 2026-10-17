---
title: ベイク（事前計算）
tags:
  - 最適化
---

# ベイク（事前計算）

**ベイク**（bake）は、**実行中にやると重い計算を、ビルド時やツールの実行時（オフライン）に済ませ、結果をファイルに焼き付けて（保存して）おく**ことです。**パンを焼いておく**ように、**ゲームの実行時は、焼けた結果を読むだけ**にします。**ライトマップ・ナビメッシュ・アニメーション・当たり判定のデータ・テクスチャの圧縮・シェーダー**など、**ゲーム開発の、あらゆる場面**で使われる、**最も効果の大きい最適化の 1 つ**です。このページは、**考え方・何をベイクするか・パイプラインの作り方・注意点**をまとめます。

!!! tip "ポイント"
    - ベイク ＝ <strong>「実行時にやる計算」を、「ビルド時（オフライン）」に移して、結果をファイルに保存</strong>。
    - 実行時は<strong>結果を読むだけ</strong>。<strong>起動・ロード・毎フレームの処理が、軽くなる</strong>。
    - 向くのは<strong>入力が、変わらない（静的な）もの</strong>：<strong>地形・建物・アニメーション・テクスチャ・ライトの一部</strong>。
    - 代表例：<strong>ライトマップ、ナビメッシュ、衝突データ（凸包・BVH）、アニメーションの圧縮、テクスチャ圧縮とミップ、シェーダーのコンパイル、LUT</strong>。
    - <strong>ベイクしたものは、ゲームが読みやすい形式（バイナリ）</strong>にする（<strong>そのまま `mmap` して使える形</strong>が理想）。
    - 代償：<strong>ビルド時間・ディスク容量が、増える</strong>。<strong>動的に変わるものには、使えない</strong>。<strong>元データを変えたら、焼き直す</strong>。
    - <strong>ビルド（焼き）が、遅くならない工夫</strong>：<strong>変更があったものだけ、焼き直す（差分ビルド・キャッシュ）</strong>。

## なぜ、ベイクするのか

<svg class="fig illust" viewBox="0 0 800 300" role="img" aria-label="ベイク：重い計算を、実行前に済ませて、結果を保存する"><defs><marker id="bk1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs><text x="20" y="26" class="fig-title">ベイク ＝ 重い計算を、ビルド時に「焼いて」おく。ゲーム中は、焼けたものを読むだけ</text><polygon points="90.0,102.0 138.0,126.0 90.0,150.0 42.0,126.0" fill="rgba(76,139,245,0.35)" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="42.0,126.0 90.0,150.0 90.0,198.0 42.0,174.0" fill="rgba(76,139,245,0.2)" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="90.0,150.0 138.0,126.0 138.0,174.0 90.0,198.0" fill="rgba(76,139,245,0.5)" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><rect x="30" y="196" width="120" height="26" rx="6" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-width="2"/><text x="90" y="214" text-anchor="middle" style="font-size:13px;font-weight:600">character.fbx</text><text x="90" y="252" text-anchor="middle" style="font-size:15px;font-weight:700">元データ</text><text x="90" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">人が編集する形式</text><line x1="160" y1="150" x2="232" y2="150" stroke="currentColor" stroke-width="3" marker-end="url(#bk1)"/><text x="196" y="140" text-anchor="middle" style="font-size:12px;font-weight:600">ビルド時</text><rect x="240" y="80" width="170" height="150" rx="14" fill="rgba(229,170,40,0.22)" stroke="currentColor" stroke-width="3"/><rect x="262" y="118" width="126" height="86" rx="10" fill="rgba(229,72,77,0.28)" stroke="currentColor" stroke-width="2"/><path d="M 300 190 Q 312 150 325 172 Q 332 140 345 188 Q 360 160 366 192 Z" fill="#e5484d" opacity="0.8"/><circle cx="268" cy="100" r="9" fill="none" stroke="currentColor" stroke-width="2"/><line x1="268" y1="100" x2="266" y2="93" stroke="currentColor" stroke-width="2"/><circle cx="300" cy="100" r="9" fill="none" stroke="currentColor" stroke-width="2"/><line x1="300" y1="100" x2="300" y2="93" stroke="currentColor" stroke-width="2"/><circle cx="332" cy="100" r="9" fill="none" stroke="currentColor" stroke-width="2"/><line x1="332" y1="100" x2="334" y2="93" stroke="currentColor" stroke-width="2"/><circle cx="364" cy="100" r="9" fill="none" stroke="currentColor" stroke-width="2"/><line x1="364" y1="100" x2="368" y2="93" stroke="currentColor" stroke-width="2"/><text x="325" y="252" text-anchor="middle" style="font-size:15px;font-weight:700">ベイク ツール</text><text x="325" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">数分かけて計算</text><line x1="420" y1="150" x2="492" y2="150" stroke="currentColor" stroke-width="3" marker-end="url(#bk1)"/><text x="456" y="140" text-anchor="middle" style="font-size:12px;font-weight:600">保存</text><path d="M 500 96 L 560 96 L 584 120 L 584 204 L 500 204 Z" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><path d="M 560 96 L 560 120 L 584 120" fill="none" stroke="currentColor" stroke-width="2"/><text x="542" y="156" text-anchor="middle" style="font-size:20px;font-weight:800">BIN</text><path d="M 520 180 L 534 192 L 560 166" fill="none" stroke="#2ea043" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><text x="542" y="252" text-anchor="middle" style="font-size:15px;font-weight:700">焼いたデータ</text><text x="542" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">ゲーム用のバイナリ</text><line x1="592" y1="150" x2="650" y2="150" stroke="currentColor" stroke-width="3" marker-end="url(#bk1)"/><text x="620" y="140" text-anchor="middle" style="font-size:12px;font-weight:600">読む</text><rect x="656" y="96" width="120" height="86" rx="8" fill="rgba(76,139,245,0.18)" stroke="currentColor" stroke-width="3"/><rect x="700" y="182" width="32" height="14" fill="currentColor" opacity="0.5"/><rect x="684" y="196" width="64" height="8" rx="3" fill="currentColor" opacity="0.5"/><polygon points="716.0,126.0 740.0,138.0 716.0,150.0 692.0,138.0" fill="#f6c244" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="692.0,138.0 716.0,150.0 716.0,174.0 692.0,162.0" fill="#e5484d" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><polygon points="716.0,150.0 740.0,138.0 740.0,162.0 716.0,174.0" fill="#c93a3f" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><text x="716" y="252" text-anchor="middle" style="font-size:15px;font-weight:700">ゲーム（実行時）</text><text x="716" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">ほぼ一瞬で読める</text></svg>

| 比べる | 実行時に計算 | ベイク |
| --- | --- | --- |
| **計算のタイミング** | **ゲーム中・起動時**（毎回） | <strong>ビルド時（1 回）</strong> |
| **ゲームの負荷** | **重い** | **読むだけ**で軽い |
| **品質** | **時間の制限で、簡易的** | **時間をかけて、高品質**にできる |
| **柔軟性** | **動的に変わる**ものに、対応 | **静的なものだけ** |
| **ビルド時間** | 影響なし | **増える** |

<strong>「実行時には、時間が限られている」</strong>が、<strong>「ビルド時は、何分かけてもよい」</strong>ので、<strong>高品質な計算（レイトレーシングの照明など）</strong>を、**事前にやっておけます**。

## 何をベイクするか

### グラフィックス

| 対象 | 内容 |
| --- | --- |
| **ライトマップ** | **静的な光と影を、テクスチャに焼く**。**実行時は、貼るだけ**（光の計算が、不要） |
| **ライトプローブ** | **空間の、数か所の光の情報**を焼いて、**動く物の照明に使う** |
| **反射プローブ・環境マップ** | **周囲の景色**をキューブマップに（[PBR の IBL](../3d/pbr.md)） |
| **IBL の事前計算** | **irradiance マップ・プリフィルタ マップ・BRDF LUT** |
| **ミップマップ** | **縮小版の画像を、事前に生成**（[メッシュとテクスチャ](../3d/mesh-textures.md)） |
| **テクスチャ圧縮** | **BC7・BC5 などの GPU 圧縮形式**に変換（メモリ・帯域を節約） |
| **テクスチャ アトラス** | **小さな画像を、1 枚にまとめる**（描画の切り替えを減らす） |
| **シェーダー** | **`.hlsl` を、ビルド時にコンパイル**して、`.cso` に（起動時のコンパイルを避ける） |
| **LOD** | **遠景用の、簡易モデル**を、自動生成 |
| **オクルージョン データ** | <strong>「どこから、何が見えるか」</strong>を、事前に計算 |
| **メッシュの最適化** | **頂点キャッシュの並び替え**、**頂点フォーマットの圧縮** |

### ゲームプレイ

| 対象 | 内容 |
| --- | --- |
| **ナビメッシュ** | **歩ける場所の、多角形**を、マップから**自動生成**（経路探索に使う）。**実行時の生成は、重い** |
| **経路の事前計算** | **主要な地点間の、最短経路表**（ウェイポイント） |
| **衝突データ** | <strong>三角形メッシュ → 凸包・BVH（空間分割）</strong>に変換（[3D の衝突判定](../3d/collision-3d.md)） |
| <strong>物理メッシュの「クッキング」</strong> | **物理エンジン（PhysX・Jolt など）用の形式**に変換 |
| **空間分割の構築** | **八分木・グリッド**を、静的な世界に対して、**事前に作る** |
| **視界・可視性** | <strong>PVS（Potentially Visible Set）</strong>：**各場所から見える部屋の一覧** |

### アニメーション

| 対象 | 内容 |
| --- | --- |
| **アニメーションの再サンプリング** | **フレームレートをそろえる**（ばらばらなキーフレームを、**一定間隔**に） |
| **アニメーションの圧縮** | **キーフレームの削減・量子化**（データ量を、数分の一に）（[スキニング](../3d/skinning-animation.md)） |
| **ルートモーションの抽出** | **移動量を、アニメーションから分離**して、事前に保存 |
| **ポーズの事前計算** | **ブレンドツリー・IK の結果**を、事前に焼く（簡易化） |
| **頂点アニメーション テクスチャ**（VAT） | **骨の動きを、テクスチャに焼いて**、**大量のキャラクター**を、GPU で再生（**群衆**） |
| **物理シミュレーションの焼き込み** | **布・破壊の動きを、事前に計算**し、**アニメーションとして**再生 |

### そのほか

| 対象 | 内容 |
| --- | --- |
| **フォント アトラス** | **文字の絵を、1 枚のテクスチャに**（[ImGui のフォント](../libs/imgui/fonts.md)） |
| **ルックアップ テーブル** | **ガンマ・イージング・BRDF** などの、数値表（[コンパイル時の計算](compile-time.md)も） |
| **音声** | **圧縮・ループ点の設定・ストリーミング用に分割** |
| **ローカライズ** | **文字列テーブルを、ID 付きの、バイナリに** |
| **データのシリアライズ** | **JSON → バイナリ**（[シリアライズでロードを速く](serialization-speed.md)） |
| **ハッシュ・ID の割り当て** | **文字列を、ハッシュ値に置き換えた、データ**（[文字列とハッシュ](strings-hash.md)） |

## ベイクのパイプライン（アセットパイプライン）

**元データ（人が作る）→ ベイク ツール → ゲーム用データ**、という**変換の流れ**を作ります。

```text
assets_source/                  ← 元データ（Git で管理）
  character.fbx
  stage1.json
  skin.png
        │
        ▼  アセット ビルド ツール（コマンドライン、ビルドの一部）
        │
assets_baked/（またはパッケージ）  ← ゲームが読む形式（バイナリ）
  character.mesh
  stage1.bin
  skin.dds
```

### 元データと、ゲーム用データを、分ける

| | 元データ（ソース） | ゲーム用データ（ベイク済み） |
| --- | --- | --- |
| **形式** | **編集しやすい**（FBX・PNG・JSON） | **読みやすい・軽い**（独自バイナリ・DDS） |
| **管理** | **Git で管理**（編集の履歴） | **Git に入れない**（ビルドで作る）、またはパッケージ |
| **大きさ** | 大きい・冗長 | **小さい・最適化済み** |

**ゲームは、元データを、直接読まない**ようにします（**ビルド時に変換**）。

### 差分ビルド（変更があったものだけ、焼き直す）

**全アセットを、毎回焼き直す**と、**ビルドが、とても遅く**なります。

| 方法 | 説明 |
| --- | --- |
| **更新日時の比較** | **元データが、焼いたデータより新しければ、焼き直す** |
| **内容のハッシュ** | **元データのハッシュ値が変わったときだけ**（日時より確実。**ツールのバージョンも、ハッシュに含める**） |
| **依存関係の記録** | <strong>「この出力は、この入力から作られた」</strong>を記録（**入力が変われば、出力を無効に**） |
| **キャッシュの共有** | **チームで、焼いた結果を共有**（**自分で焼かず、ダウンロード**） |

```cpp
std::string cache_key = Hash(source_file_contents) + tool_version + settings_hash;
if (Cache::Has(cache_key)) {
  return Cache::Get(cache_key);
}
Result r = Bake(source);
Cache::Put(cache_key, r);
```

<strong>「ツールのバージョン」や「設定」も、キーに含める</strong>のが、重要です（**ツールを直したのに、古い結果が使われる**のを防ぐ）。

### ビルドシステムに組み込む

| 方法 | 説明 |
| --- | --- |
| **Visual Studio のカスタム ビルド ステップ** | **プロジェクトに、ツールの実行を、登録**（ビルド時に自動実行） |
| **CMake の `add_custom_command`** | **入力ファイルが変わったときだけ、ツールを実行** |
| **専用のアセット ビルダー** | **別プロセス**で、並列に、変換（**ファイル監視**で、ホットリロード） |

```cmake
add_custom_command(
  OUTPUT ${CMAKE_BINARY_DIR}/assets/stage1.bin
  COMMAND bake_tool ${CMAKE_SOURCE_DIR}/assets/stage1.json ${CMAKE_BINARY_DIR}/assets/stage1.bin
  DEPENDS ${CMAKE_SOURCE_DIR}/assets/stage1.json bake_tool
)
```

**`DEPENDS`** で、**入力が変わったときだけ**、再実行されます（[CMake](../vs/cmake.md)）。

## ベイクした結果の、形式

**ゲームが、できるだけ速く読める形**にします。

| 方針 | 説明 |
| --- | --- |
| **バイナリ形式** | **テキスト（JSON）の解析は、遅い**。**バイナリは、そのまま読める** |
| **メモリ上の形そのまま** | **ファイルを読み込んだメモリを、そのまま、構造体として使う**（**パースなし・コピーなし**）（[シリアライズ](serialization-speed.md)、[cista](../libs/serialization/cista.md)） |
| **ヘッダ ＋ データの塊** | **ヘッダに、各データの、位置・大きさ**。**必要な部分だけ、読める** |
| **GPU が読める形** | **頂点バッファ・テクスチャ**は、**そのまま GPU へ転送**できる形（DDS・頂点配列）に |
| **ポインタでなく、オフセット・インデックス** | **ファイルを、どこに読み込んでも、有効**（[ポインタをインデックスに](data-layout.md)） |
| **アライメントを、そろえる** | **構造体の境界**を、守る |
| **バージョン番号** | **形式を変えたとき**、**古いファイルを検出**して、**焼き直しを促す** |

### 簡単な例：ベイクして、読む

```cpp
struct BakedHeader {
  uint32_t magic = 0x4D455348;
  uint32_t version = 1;
  uint32_t vertex_count = 0;
  uint32_t index_count = 0;
};

void BakeMesh(const SourceMesh& src, const std::string& path) {
  std::vector<Vertex> vertices = Optimize(src.vertices);
  std::vector<uint32_t> indices = OptimizeCache(src.indices);

  BakedHeader h;
  h.vertex_count = static_cast<uint32_t>(vertices.size());
  h.index_count = static_cast<uint32_t>(indices.size());

  std::ofstream out(path, std::ios::binary);
  out.write(reinterpret_cast<const char*>(&h), sizeof(h));
  out.write(reinterpret_cast<const char*>(vertices.data()), vertices.size() * sizeof(Vertex));
  out.write(reinterpret_cast<const char*>(indices.data()), indices.size() * sizeof(uint32_t));
}

LoadedMesh LoadMesh(std::span<const std::byte> file) {
  const BakedHeader* h = reinterpret_cast<const BakedHeader*>(file.data());
  if (h->magic != 0x4D455348 || h->version != 1) throw std::runtime_error("bad file");

  const Vertex* vertices = reinterpret_cast<const Vertex*>(file.data() + sizeof(BakedHeader));
  const uint32_t* indices = reinterpret_cast<const uint32_t*>(vertices + h->vertex_count);
  return {vertices, h->vertex_count, indices, h->index_count};
}
```

| 点 | 説明 |
| --- | --- |
| **`magic`** | **ファイルの種類を確認**する、目印の数字 |
| **`version`** | **形式が変わったか**を検出 |
| **ベイク側で、最適化** | **頂点キャッシュの並び替え**などを、**ツールで**行う |
| **読む側は、解析なし** | **ファイルの、メモリ上のバイト列を、そのまま構造体として見る** |

!!! warning "エンディアンとパディング"
    **別の環境のツールで焼く**と、**構造体のパディング・エンディアン**が違って、**読めません**。**同じコンパイラ・同じ環境**、または**固定幅の整数・`static_assert(sizeof(...))`** で、形を**固定**します（[データ構造の配置](data-layout.md)）。

## ベイクの例

### ナビメッシュ

| 手順 | 内容 |
| --- | --- |
| **入力** | **ステージの、静的なメッシュ**（床・壁） |
| **ベイク** | **歩ける場所を、多角形に分割**し、**隣り合う多角形の関係**を記録（**Recast** などのライブラリが、定番） |
| **出力** | **ナビメッシュのバイナリ** |
| **実行時** | **読み込んで、A* で経路探索**（生成はしない） |

### 衝突データ（物理メッシュのクッキング）

| 手順 | 内容 |
| --- | --- |
| **入力** | <strong>見た目のメッシュ（数万ポリゴン）</strong> |
| **ベイク** | **簡略化した衝突用メッシュ**・**凸包の分解**・**BVH の構築** |
| **出力** | **物理エンジンが読む形式** |
| **実行時** | **読み込むだけで、すぐ衝突判定に使える**（[Jolt](../libs/jolt/shapes.md)） |

### アニメーションの圧縮

| 手順 | 内容 |
| --- | --- |
| **入力** | **全フレームの、全骨の、位置・回転・スケール** |
| **ベイク** | **変化の少ない骨・フレームを削除**、**回転を、小さな型に量子化**（4 つの `float` → 数バイト） |
| **出力** | **数分の一の、サイズ**の、アニメーション |
| **実行時** | **復元（デコード）して、再生** |

### シェーダー

**`.hlsl` を、ゲームの起動時にコンパイルする**と、**起動が遅く**なります。**ビルド時に、`fxc` / `dxc`** で、<strong>`.cso`（コンパイル済み）</strong>にしておきます。

```text
shader.hlsl → (dxc / fxc、ビルド時) → shader.cso → ゲームが読み込んで CreateVertexShader
```

**Visual Studio は、`.hlsl` をプロジェクトに追加するだけで、ビルド時にコンパイル**してくれます（プロパティの「HLSL コンパイラ」）。

### ライトマップ

**静的な光と影を、時間をかけて計算し、テクスチャに焼きます**。**実行時は、ライトマップのテクスチャを、貼るだけ**で、**リアルタイムの影・間接光の計算が不要**になります。

| 利点 | 欠点 |
| --- | --- |
| **実行時のコストが、ほぼゼロ**・**高品質**（時間をかけた、間接光） | **光源や、物体が動くと、使えない**（**静的な物だけ**） |
| | **ライトマップのテクスチャが、メモリを使う** |
| | **ライトを変えたら、焼き直し**（時間がかかる） |

**動くキャラクター**には、**ライトプローブ**（空間の、光の情報）を併用します。

## 実行時に計算するか、ベイクするか

| 判断 | ベイク | 実行時 |
| --- | --- | --- |
| **入力が、変わらない** | ✓ | |
| **入力が、ゲーム中に変わる**（プレイヤーが壊す・動かす） | | ✓ |
| **計算が、重い** | ✓ | |
| **結果が、小さい** | ✓ | |
| **結果が、巨大**（ディスク・メモリを圧迫） | | ✓（または、一部だけ） |
| **ゲーム中の、柔軟性が必要**（時間帯で光が変わる） | 組み合わせ（複数をベイク、補間） | ✓ |

**折衷案**：**複数の状態をベイクしておき、実行時に補間する**（昼と夜のライトマップを、混ぜる）。**動的な部分だけ、実行時に計算**し、**静的な部分は、ベイクの結果を使う**。

## ベイクの注意点

| 注意 | 説明 |
| --- | --- |
| **元データを変えたら、焼き直す** | **古い焼き済みデータが、残る**と、**見た目が、おかしくなる**。**差分ビルド**で、確実に更新 |
| **ツールのバージョン・設定** | **変えたら、全部、焼き直し**（キャッシュのキーに含める） |
| **ビルド時間が、増える** | **差分ビルド・並列実行・キャッシュの共有**で、緩和 |
| **ディスク容量** | **焼いたデータが、大きく**なる（ライトマップ・プローブ）。**圧縮**する |
| **イテレーション（試行）が、遅くなる** | **エディタで、少し変えて確かめたいのに、毎回焼く**のは、つらい。**開発中は、簡易ベイク・実行時計算に切り替えられる**ようにする |
| **プラットフォームごとの違い** | **PC とコンソール**で、**テクスチャ圧縮形式**などが違う。**プラットフォーム別に、焼く** |
| **ベイク結果の検証** | **焼いたものが、正しいか**を、**自動テスト・目視**で確認 |
| **バージョン管理** | **ベイク済みデータを、Git に入れない**（大きく、再生成できる）。**パッケージで配布** |

## よくあるミス

??? failure "実行時に、毎回同じ計算をしている"
    **入力が変わらない**なら、**ベイク**できないか考えます（**プロファイラーで、重い処理を探す**）。

??? failure "元データを変えたのに、焼いた結果が、古いまま"
    **差分ビルドの条件**（入力のハッシュ）を、確認します。**ツールのバージョンも、キー**に含めます。

??? failure "ベイクを、全アセットを毎回やって、ビルドが非常に遅い"
    **変更があったものだけ**、焼き直します。**キャッシュを、チームで共有**します。

??? failure "焼いたデータの形式を変えたのに、古いファイルを読んで、クラッシュする"
    **バージョン番号**を持たせ、**古い形式を検出**して、**エラーにする**（または焼き直し）。

??? failure "動的に変わるものを、ベイクして、見た目が合わない"
    **ベイクは、静的なものだけ**です。**動的な部分は、実行時**に。

??? failure "ベイク結果が巨大になり、ロードが、かえって遅くなる"
    **圧縮**・**必要な部分だけを焼く**・**ストリーミング**を検討します（[ロード時間](loading.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ベイク ＝ 重い計算を、ビルド時に済ませて、結果を保存</strong>。<strong>実行時は、読むだけ</strong>
    - [x] 代表例：<strong>ライトマップ・ナビメッシュ・衝突データ・アニメ圧縮・テクスチャ圧縮・シェーダー</strong>
    - [x] <strong>元データ（編集用）と、ゲーム用データ（ベイク済み）を、分ける</strong>
    - [x] <strong>差分ビルド（入力とツールのハッシュ）</strong>で、<strong>変更したものだけ焼き直す</strong>
    - [x] 形式は<strong>バイナリ・そのまま読める・バージョン番号付き</strong>
    - [x] <strong>静的なものだけ</strong>。<strong>動くものは、実行時に（または、補間）</strong>

## 関連ページ

- [最適化の進め方](index.md)
- [コンパイル時の計算（constexpr）](compile-time.md)
- [シリアライズでロードを速く](serialization-speed.md)
- [ロード時間・起動時間](loading.md)
- [データ構造の配置](data-layout.md)
- [PBR（物理ベースレンダリング）](../3d/pbr.md)
- [スキニングとアニメーション](../3d/skinning-animation.md)
- [3D の衝突判定](../3d/collision-3d.md)
- [CMake で使う](../vs/cmake.md)
