---
title: Virtual Texturing
tags:
  - 描画
---

# Virtual Texturing

<strong>広大な地形に、一意なテクスチャを貼るには、巨大なテクスチャが必要</strong>です。<strong>必要な部分だけを、メモリに読み込む「仮想テクスチャ」</strong>で、実現します。このページでは、仮想テクスチャの考え方を説明します。

!!! tip "ポイント"
    - 巨大なテクスチャを、小さなタイルに分ける。
    - 見えているタイルだけ、メモリに載せる。
    - ページ テーブルで、仮想アドレスを引く。
    - 複雑だが、広大な地形では強力。

## 仮想テクスチャ
<strong>地形全体に固有のテクスチャを描きたい</strong>（<strong>手描きの道・足跡・建物の跡</strong>）とき、<strong>巨大なテクスチャ（例：128K×128K）</strong>が必要になりますがメモリに全部は載せられません。仮想テクスチャ（Sparse Virtual Texture）は、見える部分を必要な解像度でタイル単位に読み込みます。

| 要素 | 内容 |
| --- | --- |
| タイル | テクスチャを、128×128 などのページに分割 |
| フィードバック パス | 画面の各ピクセルがどのページ・ミップを必要とするかを書き出す |
| ページ テーブル | 仮想アドレスから、物理テクスチャ（キャッシュ）の位置へ |
| キャッシュ | 物理テクスチャに読み込んだタイルを置く（LRU で入れ替え） |
| 読み込み | 足りないタイルをディスクから読み、必要なら生成 |

<strong>ランタイム仮想テクスチャ（RVT）</strong>は、<strong>スプラットのブレンド結果を、タイルとしてキャッシュ</strong>します。<strong>毎ピクセルのスプラット計算が、キャッシュの読み出し 1 回になり</strong>、描画が軽くなります。

ランタイム仮想テクスチャ（RVT）の利点は、ピクセルごとの合成を省略できること、地形全体の巨大な固有テクスチャを持てること、デカールを焼き込めることです。欠点は、仕組みが複雑なことと、フィードバックの遅延で一瞬ぼやける（ポップイン）こと、メモリの管理が必要なことです。

## 解きたい問題

広い地形に、場所ごとに違う模様（手描きの道、建物の跡、境目の汚れ）を貼りたいとします。地形が 8 km 四方で、1 m を 4 画素にすると、32,000 × 32,000 画素です。1 画素 4 バイトなら、<strong>4 GB</strong> になります。さらに、近づくと、もっと細かい解像度が欲しくなります。

| 方法 | 問題 |
| --- | --- |
| 全部をメモリに載せる | VRAM が、足りない |
| 繰り返しのテクスチャ（タイル）を使う | 場所ごとの、固有の模様を、描けない |
| 低解像度で、全体を覆う | 近づくと、ぼやける |

仮想テクスチャ（Virtual Texture、VT）は、<strong>巨大なテクスチャを、小さなタイル（ページ）に切って、いま見えている部分だけを、メモリに置く</strong>方式です。CPU の、仮想メモリと、まったく同じ考え方です。

| CPU の仮想メモリ | 仮想テクスチャ |
| --- | --- |
| 仮想アドレス | テクスチャ座標（UV） |
| ページ（4 KB など） | タイル（128×128 画素など） |
| ページ テーブル | ページ テーブル（間接参照のテクスチャ） |
| 物理メモリ | 物理テクスチャ（タイルを置くキャッシュ） |
| ページ フォールト | 足りないタイルの要求 |

## 3 つの部品

### ① フィードバック パス

画面の各画素が、<strong>どのタイルの、どのミップが必要か</strong>を調べます。専用の、小さな解像度（画面の 1/8 など）の描画で、タイルの番号を書き出します。

```hlsl
// フィードバック: 画素ごとに、必要なタイルの番号を書き出す。
float4 FeedbackPS(PSInput input) : SV_Target {
  float2 uv = input.virtual_uv * virtual_size;          // 仮想テクスチャ上の画素座標
  // ミップ レベルを、画素の微分から求める
  float2 dx = ddx(uv);
  float2 dy = ddy(uv);
  float mip = max(0.0, 0.5 * log2(max(dot(dx, dx), dot(dy, dy))) + mip_bias);
  mip = min(floor(mip), max_mip);

  uint2 page = uint2(uv / (tile_size * exp2(mip)));     // このミップでの、タイル番号
  // R, G = タイルの X, Y、B = ミップ、A = 有効フラグ
  return float4(page.x & 255, page.y & 255, mip, 255) / 255.0;
}
```

書き出した画像は、<strong>CPU に読み戻して</strong>（ステージング テクスチャ経由）、重複を除き、「必要なタイルの一覧」を作ります。

```cpp
// 1〜2 フレーム前の結果を読む（GPU を待たせないため、遅延させる）。
context->CopyResource(staging_texture.Get(), feedback_texture.Get());
// 数フレーム後に、Map で読む
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(old_staging.Get(), 0, D3D11_MAP_READ, 0, &mapped);
// 画素を走査して、必要なタイルの集合を作る
context->Unmap(old_staging.Get(), 0);
```

### ② 物理テクスチャ（キャッシュ）

読み込んだタイルを、置く場所です。1 枚の大きなテクスチャを、<strong>タイル大のスロット</strong>に、分けて使います。

| 項目 | 内容 |
| --- | --- |
| 大きさ | 例：4096×4096 画素 ＝ 128×128 画素のタイル、1,024 枚 |
| 入れ替え | 足りなくなったら、最近使われていないタイル（LRU）を、捨てて、新しいタイルを入れる |
| タイルの内容 | ディスクから読んで展開する、または、その場で生成する（スプラットを合成して作る、など） |

タイルを、物理テクスチャに書き込むときは、`UpdateSubresource` や、タイルを描いた小さなレンダー ターゲットから、`CopySubresourceRegion` します。

### ③ ページ テーブル（間接参照）

「仮想の UV」から、「物理テクスチャの、どの位置か」を引く表です。<strong>テクスチャ自体で表現します</strong>（1 画素 ＝ 1 タイル）。

```hlsl
Texture2D<float4> g_page_table : register(t0);   // 各画素が、1 つのタイル。RG = 物理スロットの位置、B = ミップ
Texture2D g_physical : register(t1);             // 物理テクスチャ（タイルのキャッシュ）

float4 SampleVirtual(float2 virtual_uv) {
  // ① ページ テーブルを、点サンプリングで引く（補間しない）
  uint2 table_pos = uint2(virtual_uv * page_table_size);
  float4 entry = g_page_table.Load(int3(table_pos, 0));

  // ② 物理テクスチャ上の、タイルの位置と、タイル内のオフセットを計算する
  float2 tile_pos = entry.xy * 255.0;                    // 物理スロット（タイル単位）
  float scale = exp2(entry.z * 255.0);                   // そのタイルのミップの大きさ
  float2 in_tile = frac(virtual_uv * page_table_size * scale);  // タイルの中の、0〜1 の位置

  // ③ 境界を、少し内側に寄せる（隣のタイルの色が、混ざるのを防ぐ）
  float2 padded = (in_tile * (tile_size - 2 * border) + border) / tile_size_with_border;
  float2 physical_uv = (tile_pos + padded) / physical_tile_count;
  return g_physical.SampleGrad(g_linear_clamp, physical_uv, ddx(virtual_uv * ...), ddy(virtual_uv * ...));
}
```

### 境界の問題（枠）

<strong>バイリニアやトライリニア補間は、隣の画素を読みます。</strong> タイルの端では、隣のタイルが、物理テクスチャの、全然違う場所にあるので、<strong>別のタイルの色が混ざって、継ぎ目の線が見えます</strong>。

対策は、各タイルに、<strong>周りの画素を、数画素ぶん、一緒に持たせる（ボーダー）</strong>ことです。たとえば、128×128 のタイルに、4 画素の枠を付けて、136×136 を、1 スロットとします。異方性フィルタリングを使うなら、枠も、大きく（4 画素以上）します。

## 動き全体の流れ

```text
毎フレーム:
  ① フィードバック パス  → 必要なタイルの一覧を、作る（数フレーム遅れて、CPU に届く）
  ② ストリーミング       → 足りないタイルを、ディスクから読む／その場で生成する
  ③ 物理テクスチャを更新 → タイルを、スロットに、書き込む
  ④ ページ テーブルを更新 → 仮想の位置と、物理スロットを、結びつける
  ⑤ 通常の描画           → SampleVirtual で、テクスチャを引く
```

タイルが、まだ届いていない間は、<strong>粗いミップの、常駐しているタイルで、代用</strong>します。そうすると、画面は、一瞬ぼやけますが、真っ黒や、抜けにはなりません。タイルが届くと、鮮明になります。

!!! note "最も粗いミップは、常に、メモリに置く"
    必ず読み込み済みの、<strong>最も粗い階層</strong>（たとえば、全体が 1 枚のタイルに収まるミップ）を、常駐させておきます。ページ テーブルは、タイルが、まだ無いとき、この常駐したタイルを指します。

## 論文と、実装の例

| 資料 | 内容 |
| --- | --- |
| Barrett、GDC 2008「Sparse Virtual Textures」 | 仮想テクスチャの、基本構成を、整理した発表。ページ テーブルに、アルゴリズムを、シェーダーで書く例 |
| van Waveren、SIGGRAPH 2009 | id Tech 5（RAGE）の実装。ページ テーブルの、更新方法や、圧縮、ストリーミング |
| Mittring、SIGGRAPH 2008 | CryEngine での、仮想テクスチャの、応用（地形、キャラクター） |

id Tech 5 は、<strong>ゲーム全体の地形テクスチャを、固有の絵として</strong>描いて、巨大な仮想テクスチャに入れました。アーティストは、場所ごとに、好きな絵を描けます。代わりに、ディスク容量が、大きくなります。

## ランタイム仮想テクスチャ（RVT）

近年の実装では、<strong>ディスクから、タイルを読む代わりに、その場で、タイルを生成する</strong>方式があります。タイルの中身は、<strong>地形のスプラットと、高さブレンド、デカールを、ブレンドした結果</strong>です。

| 項目 | 内容 |
| --- | --- |
| 生成 | 必要なタイルが、要求されたとき、そのタイルの範囲だけ、地形の素材を、ブレンドして、物理テクスチャに描く |
| 利点 | 画素ごとの、素材の合成（数層ぶんの読み込み）が、描画時に、1 回の読み込みで済む。デカールも、タイルに焼き込める |
| 欠点 | タイルを作る間は、負荷が、かかる。キャッシュが、足りないと、毎フレーム、作り直しが起きる |
| 向く場面 | 素材の層が多い地形。デカールが多い場面。カメラが、ゆっくり動く場面 |

スプラット（[Splat Weights](weights.md)）の合成は、近景では、1 画素に、数十回のテクスチャ読み込みを、必要とします。RVT は、この処理を、<strong>「タイルを作るときの、1 回だけ」</strong>に、してしまいます。

## 他の方法との比較

| 方式 | 固有の模様 | メモリ | 実装の難しさ |
| --- | --- | --- | --- |
| タイルの繰り返し ＋ スプラット | 素材の組み合わせだけ | 少ない | 易しい |
| 巨大な 1 枚のテクスチャ | 自由 | 巨大 | 易しいが、メモリが足りない |
| 仮想テクスチャ | 自由 | キャッシュの分だけ | 難しい（ページ テーブル、フィードバック、境界、ストリーミング） |
| DirectX 11.2 の Tiled Resources | 自由（ハードウェア対応） | キャッシュの分だけ | やや難しい（ハードウェアが、ページ テーブルの役割を果たす） |

DirectX 11.2 以降の <strong>Tiled Resources</strong>（リザーブド リソース）は、ハードウェアが、<strong>仮想テクスチャの、ページ テーブルを、担当します</strong>。シェーダーの中で、`SampleVirtual` のような、間接参照を書く手間が、なくなります。ただし、対応する GPU と、Windows の組み合わせが、必要です。

## よくあるミス

??? failure "近づいた時、テクスチャがぼやけて、後から鮮明になる"
    <strong>先読み</strong>を<strong>強める</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 必要なタイルだけ、メモリに載せる

## 参考

- Barrett, "Sparse Virtual Textures", Game Developers Conference 2008
- van Waveren, "id Tech 5 Challenges: From Texture Virtualization to Massive Parallelization", SIGGRAPH 2009, Beyond Programmable Shading
- Mittring, "Advanced Virtual Texture Topics", SIGGRAPH 2008, Advances in Real-Time Rendering in 3D Graphics and Games
- Microsoft Learn, "Tiled resources"（Direct3D 11.2 の、ハードウェアによる仮想テクスチャ）

## 関連ページ

- [Terrain Texturing](index.md)
- [Terrain Decals and Roads](decals.md)
