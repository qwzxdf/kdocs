---
title: Chunking
tags:
  - 描画
---

# Chunking

16 km 四方の地形を 1 枚のメッシュにすると、1 m 刻みの格子で 2.56 億の頂点になり画面に映らない大部分も毎フレーム処理することになります。そこで地形を区画（チャンク）に分け見えるものだけを描き遠いものは粗くし、離れすぎたものはメモリから外します。このページではチャンクの大きさをどう決めるか見えるチャンクを探す視錐台カリングの実測、同じ格子メッシュをインスタンスで共有する描き方、高さをテクスチャ配列に持つ方法、プレイヤーの周りだけを読み込むストリーミング、境界の継ぎ目を扱います。数字は C++ で数え最後に頂点シェーダーとインスタンスの描画、ストリーミングのコードをまとめます。

数字は C++（`g++ -std=c++23 -Wall -Wextra`）で数えました。視錐台の平面は自分で導いた式で、地形の高さはダミーの関数です。HLSL は `fxc`（`vs_5_0` / `ps_5_0`）に通し、D3D11 のコードは `g++ -fsyntax-only`（mingw の `<d3d11.h>`）で構文を確かめただけで、描画した結果は確かめていません。末尾の資料は今回は読んでいません。

!!! tip "ポイント"
    - チャンクを 64 m 四方（64 セル、頂点は 65×65）にすると、16 km の世界で 250 × 250 = 62,500 個です。三角形は 1 個あたり 8192、インデックスは 24,576 個（16 ビットで 48.0 KiB）です。
    - 視錐台に入るのは、遠方 2000 m で 1110 個（1.78%）です。全探索の 62,500 回に対して、四分木は 1913 回の判定で同じ結果を出します。
    - 隣と重なる境界の画素を持つ代償は、64 セルで 3.15%、16 セルで 12.89% の記憶領域です。重ねておけば隣のチャンクを読み込まなくても境界が合います。
    - 読み込みと解放の半径を同じにすると、境界を往復しただけで 100 フレームに 104 回の読み込みが起きます。解放の半径を 1 つ大きくすると 6 回に減ります。

!!! info "このページを読む前に"
    - [Heightmaps and Meshes](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## チャンクの大きさ {#size}

### 小さすぎても大きすぎても困る {#tradeoff}

チャンクが小さいほどカリングは細かくなり見えない部分を無駄に描きません。その代わりチャンクの数が増え判定と描画の発行が増えます。大きいとチャンクの数は少ない代わりに画面の隅に少し入っているだけの巨大なチャンクを丸ごと描きます。16 km の世界で格子の幅を一辺の長さ（1 m 刻み）として数えました。

<svg class="fig flow" viewBox="0 0 680 300" role="img" aria-label="チャンクの大きさ"><defs><marker id="f1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">チャンクの大きさと数</text><line x1="80" y1="250" x2="560" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="80" y1="250" x2="80" y2="60" stroke="currentColor" stroke-width="1.5"/><polyline fill="none" stroke="#e5484d" stroke-width="2.5" points="80.0,71.9 200.0,107.6 320.0,143.4 440.0,179.1 560.0,215.3"/><polyline fill="none" stroke="#4c8bf5" stroke-width="2.5" points="80.0,207.9 200.0,172.1 320.0,136.4 440.0,100.6 560.0,64.9"/><circle cx="80.0" cy="71.9" r="4" fill="#e5484d"/><text x="86.0" y="63.875" text-anchor="start" style="font-size:11px;font-weight:700">1,000,000</text><circle cx="80.0" cy="207.9" r="4" fill="#4c8bf5"/><text x="86.0" y="223.88709606706004" text-anchor="start" style="font-size:11px;font-weight:700">512</text><circle cx="200.0" cy="107.6" r="4" fill="#e5484d"/><text x="206.0" y="99.62231198509778" text-anchor="start" style="font-size:11px;font-weight:700">250,000</text><circle cx="200.0" cy="172.1" r="4" fill="#4c8bf5"/><text x="206.0" y="188.13978408196226" text-anchor="start" style="font-size:11px;font-weight:700">2,048</text><circle cx="320.0" cy="143.4" r="4" fill="#e5484d"/><text x="326.0" y="135.36962397019556" text-anchor="start" style="font-size:11px;font-weight:700">62,500</text><circle cx="320.0" cy="136.4" r="4" fill="#4c8bf5"/><text x="326.0" y="152.39247209686454" text-anchor="start" style="font-size:11px;font-weight:700">8,192</text><circle cx="440.0" cy="179.1" r="4" fill="#e5484d"/><text x="446.0" y="171.11693595529334" text-anchor="start" style="font-size:11px;font-weight:700">15,625</text><circle cx="440.0" cy="100.6" r="4" fill="#4c8bf5"/><text x="446.0" y="116.64516011176676" text-anchor="start" style="font-size:11px;font-weight:700">32,768</text><circle cx="560.0" cy="215.3" r="4" fill="#e5484d"/><text x="566.0" y="207.27848687208234" text-anchor="start" style="font-size:11px;font-weight:700">3,844</text><circle cx="560.0" cy="64.9" r="4" fill="#4c8bf5"/><text x="566.0" y="80.89784812666898" text-anchor="start" style="font-size:11px;font-weight:700">131,072</text><text x="80.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">16</text><text x="200.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">32</text><text x="320.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">64</text><text x="440.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">128</text><text x="560.0" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">256</text><text x="320.0" y="288" text-anchor="middle" style="font-size:12px;font-weight:400">チャンクの一辺(m)。格子は 1 m 刻み(N = 一辺)で、16 km の世界</text><text x="84" y="52" text-anchor="start" style="font-size:12px;font-weight:400">赤: 世界のチャンク数  青: 1 チャンクの三角形数(対数軸)</text></svg>

- 16 m（N = 16）: チャンクは 1,000,000 個、三角形は 512、インデックスは 1536 個（3.0 KiB）
- 32 m: 250,000 個、2048 三角形（12.0 KiB）
- 64 m: 62,500 個、8192 三角形（48.0 KiB）
- 128 m: 15,625 個、32,768 三角形（192.0 KiB）
- 256 m: 3,844 個、131,072 三角形（1536.0 KiB。頂点が 66,049 個で 16 ビットに収まらないので、32 ビットのインデックス）

64 m の格子は 4225 頂点で、16 ビットのインデックス（上限 65,536）に収まります。128 m でも 16,641 頂点で収まりますが、256 m では 66,049 頂点になり 32 ビットが必要になります。インデックス バッファの大きさが 2 倍になり転送と読み出しの帯域も増えます。ここから 64 m か 128 m、頂点にして 65×65 から 129×129 が実用的な目安になります。

目安は 1 つのチャンクが画面上で数百から数千三角形に見えることです。それより小さいチャンクを個別の描画命令で大量に出すのは、割に合いません。

### 数の見積もり {#count}

16 km の世界でチャンクが 64 m なら 250 × 250 = 62,500 個です。カメラの周りの視錐台に入るのは、この一部です。62,500 個を毎フレーム全部調べるのは無駄なので、四分木で大きな範囲をまとめて捨てます（[CDLOD](../lod/cdlod.md) の四分木）。次の節で視錐台と四分木の実測を示します。

## チャンクが持つもの {#data}

チャンクは格子上の位置と高さの最小・最大、AABB、いまの LOD、読み込み済みかを持ちます。AABB はチャンクの原点から一辺だけ広げた箱で、高さは最小から最大までです。

```cpp
struct TerrainChunk {
  int grid_x, grid_z;            // チャンクの格子上の位置
  float min_height, max_height;  // 高さの最小・最大(AABB のため)
  BoundingBox bounds;            // ワールド座標の AABB
};

BoundingBox ChunkBounds(const TerrainChunk& c, float chunk_size) {
  const float x0 = c.grid_x * chunk_size, z0 = c.grid_z * chunk_size;
  return {{x0, c.min_height, z0}, {x0 + chunk_size, c.max_height, z0 + chunk_size}};
}
```

高さの最小・最大はチャンクごとに事前に求めておく必要があります。山の中のチャンクと谷のチャンクでは AABB の縦の長さが大きく違います。最小と最大が不正確だとカリングで見えるはずの山が消えることがあります。今回の数え方ではチャンクの 9 × 9 点で高さを見積もりましたが、実際は高さマップの全画素から求めます。点の間にある山頂を見落とすと AABB が小さすぎて、山頂だけが突然消えます。

## 視錐台カリング {#culling}

### 視錐台の平面と p 頂点テスト {#planes}

視錐台は 6 枚の平面で表します。法線を内向きにそろえておくと内側の点は `n · p + d ≥ 0` を満たします。カメラの向き `f`、右 `r`、上 `u` と水平 FOV `h`、垂直 FOV `v` から左右上下の平面は次のように作れます（自分で導いた式です）。

- 左: 法線 = `r cos(h/2) + f sin(h/2)`、カメラの位置を通る
- 右: `−r cos(h/2) + f sin(h/2)`
- 上: `−u cos(v/2) + f sin(v/2)`
- 下: `u cos(v/2) + f sin(v/2)`
- 近: 法線 = `f`、遠: 法線 = `−f`

前方向（`f`）の点は `f · n = sin(h/2) > 0` で内側、左の端の方向の点は 0 で平面上にあります。この確認をしておくと法線の向きを取り違えにくいです。

AABB と平面の判定は 8 個の頂点を全部調べずに**平面ごとに 1 つの頂点だけ**で済みます。平面の法線の向きに最も進んだ頂点（positive vertex）が外側なら、AABB は完全に外です。

```cpp
bool Visible(const Frustum& fr, const BoundingBox& box) {
  for (const Plane& pl : fr.planes) {
    const Float3 p = {pl.n.x >= 0 ? box.max.x : box.min.x, pl.n.y >= 0 ? box.max.y : box.min.y,
                      pl.n.z >= 0 ? box.max.z : box.min.z};   // 法線の向きに最も進んだ頂点
    if (Dot(pl.n, p) + pl.d < 0) return false;                // 完全に外側
  }
  return true;
}
```

視錐台の角の少し外側にはみ出た AABB が「見える」と判定されることはありますが、描いても画面に出ないだけで問題ありません。見えるものを消すより見えないものを描いてしまうほうが安全です。

### 実測 {#culling-numbers}

世界は 16 km、チャンクは 64 m（250 × 250 = 62,500）、カメラは中央、水平 FOV は 90°、アスペクト比は 16:9 で、遠方の距離と向きを変えて数えました。四分木は 256 × 256 のチャンクを覆う根から、4 分割していきます。

<svg class="fig flow" viewBox="0 0 680 300" role="img" aria-label="カリングの回数"><defs><marker id="f2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">カリングの回数</text><line x1="80" y1="250" x2="560" y2="250" stroke="currentColor" stroke-width="1.5"/><line x1="80" y1="250" x2="80" y2="60" stroke="currentColor" stroke-width="1.5"/><rect x="110" y="231.9" width="50" height="18.1" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="135" y="225.95" text-anchor="middle" style="font-size:11px;font-weight:700">665</text><rect x="166" y="242.0" width="50" height="8.0" fill="rgba(229,170,40,0.45)" stroke="currentColor"/><text x="191" y="236.02" text-anchor="middle" style="font-size:11px;font-weight:700">294</text><text x="163" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">far 1000 m</text><rect x="260" y="198.1" width="50" height="51.9" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="285" y="192.0757142857143" text-anchor="middle" style="font-size:11px;font-weight:700">1913</text><rect x="316" y="219.9" width="50" height="30.1" fill="rgba(229,170,40,0.45)" stroke="currentColor"/><text x="341" y="213.87142857142857" text-anchor="middle" style="font-size:11px;font-weight:700">1110</text><text x="313" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">far 2000 m</text><rect x="410" y="85.4" width="50" height="164.6" fill="rgba(76,139,245,0.45)" stroke="currentColor"/><text x="435" y="79.37857142857143" text-anchor="middle" style="font-size:11px;font-weight:700">6065</text><rect x="466" y="137.4" width="50" height="112.6" fill="rgba(229,170,40,0.45)" stroke="currentColor"/><text x="491" y="131.4114285714286" text-anchor="middle" style="font-size:11px;font-weight:700">4148</text><text x="463" y="268" text-anchor="middle" style="font-size:11px;font-weight:400">far 4000 m</text><text x="550" y="73.57142857142858" text-anchor="end" style="font-size:12px;font-weight:400">全探索は 62,500 回(枠外)</text><text x="90" y="52" text-anchor="start" style="font-size:12px;font-weight:400">青: 四分木の AABB 判定の回数  黄: 見えるチャンク数</text><text x="72" y="254.0" text-anchor="end" style="font-size:11px;font-weight:400">0</text><text x="72" y="199.71428571428572" text-anchor="end" style="font-size:11px;font-weight:400">2000</text><text x="72" y="145.42857142857144" text-anchor="end" style="font-size:11px;font-weight:400">4000</text><text x="72" y="91.14285714285714" text-anchor="end" style="font-size:11px;font-weight:400">6000</text></svg>

- 遠方 1000 m: 見えるのは 294 個（0.47%）、四分木の判定は 665 回（向き 45° では 315 個、641 回）
- 2000 m: 1110 個（1.78%）、1913 回（1118 個、1765 回）
- 4000 m: 4148 個（6.64%）、6065 回（4176 個、6045 回）

四分木の結果は全探索の結果と完全に一致しました（コードの `assert` で確認）。全探索は常に 62,500 回ですが、四分木は遠方 2000 m で 1913 回で済みます。遠方が長くなるほど見えるチャンクが増え 4000 m では 6065 回と、全探索の約 1/10 です。それでも見えるチャンクの数（4148 個）より判定が多いのは、途中の節（見えるチャンクを含む中間の箱）も調べるからです。

地形の遠方を長く取ると見えるチャンクが 2 乗に近い勢いで増えます。1000 m から 2000 m で 3.8 倍、2000 m から 4000 m で 3.7 倍です。遠くのチャンクは LOD で粗くして三角形の数を抑えます（[LOD](../lod/index.md)）。

## 描画：インスタンスでまとめる {#instancing}

### 格子メッシュは 1 つだけ {#shared-mesh}

見えるチャンクは同じ格子メッシュを位置だけ変えて描きます。65×65 の格子はインデックスが 48.0 KiB です。チャンクごとに別々のメッシュを持つと 300 個で 14.1 MiB、1000 個で 46.9 MiB、3000 個で 140.6 MiB になりますが、共有すれば 48.0 KiB のままです。チャンクごとに違うのは位置、高さテクスチャのスライス、LOD でこれをインスタンス データとして渡します。

インスタンス データは原点の xz、一辺、LOD、スライスの 5 個の `float`（20 バイト）です。1000 個で 19.53 KiB、3000 個で 58.59 KiB を毎フレーム書き換えます。

| 方法 | 描画命令 | 特徴 |
| --- | --- | --- |
| 1 チャンク = 1 描画命令 | チャンクの数 | 簡単。数百個なら問題ない |
| インスタンシング | 1 回（または LOD ごと） | CPU の仕事が最小 |

LOD ごとに頂点数の違う格子を使うなら LOD ごとに 1 回ずつ描きます。この例の頂点シェーダーでは同じ 65×65 の格子のまま LOD ごとに頂点が指すテクセルの間隔を 2 倍、4 倍にして粗くします（間隔は `1 << level`）。

### 高さデータの持ち方 {#height-storage}

チャンクごとの高さをどこに置くかは次の 4 つの方法があります。

- 世界全体で 1 枚の巨大なテクスチャ: 単純ですが、巨大な地形ではメモリに収まりません。
- チャンクごとに別のテクスチャ: ストリーミングは簡単です。描画命令ごとにテクスチャを切り替える必要があります。
- テクスチャ配列: 同じ大きさの高さマップを配列のスライスにして、スライスの番号をインスタンスに持たせます。1 回の描画命令で全チャンクを描けます。
- アトラス（カメラの周りのチャンクだけを窓として持つ）: クリップマップと近い発想です（[Geometry Clipmaps](../lod/clipmap.md)）。

テクスチャ配列はインスタンシングと相性が良く、よく使われます。D3D11 のテクスチャ配列のスライス数には上限があります（フィーチャー レベル 11 で 2048）。読み込み半径 16 チャンクで保持するのは 1089 個で、これを超えない範囲に収まります。

## ストリーミング {#streaming}

### 保持する範囲 {#budget}

世界がメモリより大きいときはプレイヤーの周りのチャンクだけをメモリに置きます。読み込み半径 `r` チャンクなら保持するのは `(2r + 1)²` 個です。高さを R16 の 65×65（8450 バイト）としたとき次のようになります（法線やテクスチャは含みません）。

- `r = 4`: 81 個、0.65 MiB、見える距離は約 256 m
- `r = 8`: 289 個、2.33 MiB、約 512 m
- `r = 12`: 625 個、5.04 MiB、約 768 m
- `r = 16`: 1089 個、8.78 MiB、約 1024 m

1 チャンク分動くと新しく読むのは 1 辺分の `2r + 1` 個です。`r = 8` なら 17 個です。プレイヤーが 5 m/s で歩くと 64 m のチャンクの境界を越えるのは 12.80 秒に 1 回、10 m/s で 6.40 秒に 1 回、50 m/s の乗り物なら 1.28 秒に 1 回です。乗り物の速さだと約 1.3 秒の間に 17 個の高さマップを読み込む必要があります。読み込みは非同期にして 1 フレームあたりの個数を制限します。そうしないと読み込みの瞬間にフレーム時間が跳ね上がります。

### 先読みと解放 {#hysteresis}

範囲は次の 3 つの状態に分けます。

- 描画範囲: 高さデータがメモリに読み込み済みです。
- 先読み範囲（描画範囲の少し外）: これから使うので、非同期で読み込み中です。
- それ以外: メモリから解放します。

読み込む半径と解放する半径を同じにすると、プレイヤーが境界の近くを行き来したときに読み込みと解放が繰り返されます。1 次元でチャンク番号が 10 と 11 を毎フレーム往復する場合を 100 フレーム数えました（読み込み半径 2）。

<svg class="fig flow" viewBox="0 0 760 450" role="img" aria-label="ヒステリシス"><defs><marker id="f3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">読み込みと解放の半径</text><text x="20" y="22" text-anchor="start" style="font-size:14px;font-weight:700">プレイヤー(星)の周りのチャンク。読み込み半径 2、解放半径 4</text><rect x="30" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="76" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="112" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="148" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="184" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="220" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="256" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="292" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="328" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="364" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="30" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="148" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="184" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="220" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="256" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="292" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="66" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="148" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="184" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="220" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="256" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="292" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="102" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="148" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="184" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="220" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="256" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="292" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="138" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="148" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="184" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="220" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="256" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="292" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="174" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="148" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="184" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="220" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="256" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="292" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="210" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="148" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="184" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="220" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="256" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="292" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="246" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="148" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="184" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="220" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="256" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="292" width="36" height="36" fill="rgba(76,139,245,0.40)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="282" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="148" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="184" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="220" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="256" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="292" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="318" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="76" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="112" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="148" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="184" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="220" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="256" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="292" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="328" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="364" width="36" height="36" fill="rgba(229,170,40,0.30)" stroke="currentColor" stroke-width="0.6"/><rect x="354" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="40" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="76" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="112" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="148" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="184" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="220" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="256" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="292" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="328" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="364" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><rect x="390" y="400" width="36" height="36" fill="rgba(150,150,150,0.10)" stroke="currentColor" stroke-width="0.6"/><text x="228.0" y="246.0" text-anchor="middle" font-size="22" fill="currentColor">★</text><rect x="446" y="60" width="18" height="18" fill="rgba(76,139,245,0.40)" stroke="currentColor"/><text x="474" y="74" text-anchor="start" style="font-size:12px;font-weight:400">読み込み済み(d ≤ 2)</text><rect x="446" y="90" width="18" height="18" fill="rgba(229,170,40,0.30)" stroke="currentColor"/><text x="474" y="104" text-anchor="start" style="font-size:12px;font-weight:400">まだ保持(2 &lt; d ≤ 4)</text><rect x="446" y="120" width="18" height="18" fill="rgba(150,150,150,0.10)" stroke="currentColor"/><text x="474" y="134" text-anchor="start" style="font-size:12px;font-weight:400">解放済み(d &gt; 4)</text><text x="446" y="170" text-anchor="start" style="font-size:12px;font-weight:400">境界を往復しても、黄色の帯が</text><text x="446" y="190" text-anchor="start" style="font-size:12px;font-weight:400">のりしろになり、読み込みと</text><text x="446" y="210" text-anchor="start" style="font-size:12px;font-weight:400">解放が繰り返されない</text></svg>

- 解放半径 2: 読み込み 104 回、解放 99 回
- 解放半径 3: 読み込み 6 回、解放 0 回
- 解放半径 4: 6 回、0 回

解放半径を 1 つ大きくするだけで、往復の間の読み込みがなくなります。最初の 6 回は最初に範囲を埋める読み込みです。

## チャンクの継ぎ目 {#seams}

### 境界の画素を重ねる {#overlap}

隣り合うチャンクの境界の高さが違うと隙間ができます。対策は境界の画素を両方のチャンクに重複して保存することです。N セルのチャンクは `N × N` ではなく `(N+1) × (N+1)` 画素の高さマップを持ち隣のチャンクを読み込まなくても境界が合います。代償は `(N+1)² / N²` 倍の記憶領域です。N = 16 で 12.89%、32 で 6.35%、64 で 3.15%、128 で 1.57%、256 で 0.78% です。チャンクが小さいほど重複の割合が大きくなります。

### 半テクセルのずれ {#half-texel}

`(N+1)` 画素の高さマップを頂点 `i`（0 から N）から UV で引くとき `uv = i / N` と書くと、ずれます。テクセル座標は `uv × (N+1) − 0.5` なので `i = 0` で −0.5、`i = N` で N + 0.5 を指します（N = 16 でも 64 でも同じ）。線形補間では境界で隣のテクセルと半分ずつ混ざり高さがわずかにずれます。正しい UV は `(i + 0.5) / (N+1)` です。

頂点シェーダーで `Load` を使い整数のテクセル座標で読めば、この問題は起きません。この例のシェーダーも `Load` を使っています。

### LOD が違うとき {#lod-seam}

隣のチャンクの LOD が違うと境界の頂点の位置が合わず亀裂ができます。モーフィングやスカートで隠します（[Cracks and Seams](../lod/cracks.md)）。法線は隣のチャンクの高さを読めば連続します（重ねた画素を使えば、隣を読み込まずに済みます）。

## コード：頂点シェーダー {#shader}

ここからコードを数行ずつ見ます。最初は定数と高さのテクスチャ配列です。

```hlsl
cbuffer TerrainCB : register(b0) {
  float4x4 gViewProj;      // ビュー × 射影
  float    gGridCells;     // 格子のセル数 N。例: 64（頂点は 65 × 65）
  float    gHeightBase;    // 高さの最小値(m)。UNORM の 0 に対応
  float    gHeightRange;   // 高さの幅(m)。UNORM の 1 に対応（base + range が最大）
  float    gPad;           // 詰め物
};

// 各チャンクの高さ。65 × 65 の R16_UNORM を、チャンクごとに 1 スライスに入れる（隣と重なる境界の画素も持つ）。
Texture2DArray<float> gHeightArray : register(t0);
```

`gGridCells` は格子のセル数 N、`gHeightBase` と `gHeightRange` は UNORM（0 から 1）の高さを m に戻す定数です。高さを 16 ビットの UNORM に入れるので、高さの範囲全体を 65,536 段階に分けて持ちます。範囲が 1000 m なら刻みは約 1.5 cm です。

頂点の入出力です。

```hlsl
struct VsIn {
  float2 grid     : POSITION;   // 頂点の格子座標（0〜N の整数。メッシュは全チャンクで共有）
  float2 origin   : CHUNK_ORIGIN;  // インスタンス: チャンクのワールド上の原点 xz (m)
  float  size     : CHUNK_SIZE;    // インスタンス: チャンクの一辺 (m)
  float  level    : CHUNK_LEVEL;   // インスタンス: LOD（0 が最も細かい。1 つ上がるごとに頂点間隔が 2 倍）
  float  slice    : CHUNK_SLICE;   // インスタンス: 高さテクスチャ配列のスライス番号
};

struct VsOut {
  float4 pos    : SV_Position;
  float3 normal : NORMAL;
  float3 world  : TEXCOORD0;
};
```

`grid` は全チャンクで共有する格子の座標です。`origin`、`size`、`level`、`slice` はインスタンスごとのデータで、入力レイアウトで「インスタンス単位」に指定します。

高さを整数で読む関数です。

```hlsl
// 高さを整数座標で読む。Load なので補間もサンプラーも要らず、半テクセルのずれが起きない。
float LoadHeight(int2 texel, uint slice, int n) {
  texel = clamp(texel, 0, n);                                          // 配列の外へ出ないよう、端でクランプ（足した）
  return gHeightArray.Load(int4(texel, slice, 0)) * gHeightRange + gHeightBase;  // 0〜1 を m に戻す
}
```

`Load` は補間もサンプラーも使わないので、半テクセルのずれが起きません。`clamp` は足した処理で法線を求めるために隣を読むときに配列の外へ出るのを防ぎます。

頂点シェーダーの本体です。

```hlsl
VsOut TerrainChunkVS(VsIn i) {
  const int n = (int)gGridCells;                                       // セル数
  const int stride = 1 << (int)i.level;                                // LOD ごとの頂点の間隔（テクセル数）。level 0 で 1
  const int2 texel = (int2)(i.grid) * stride;                          // この頂点が指す高さテクセル。LOD が粗いほど飛び飛び
  const uint slice = (uint)i.slice;

  const float h = LoadHeight(texel, slice, n);                         // 頂点の高さ
  // 法線は、隣の高さの差から。間隔 stride × セルの大きさ(m) の中心差分。
  const float cell = i.size / gGridCells;                              // 1 セルの長さ (m)
  const float hx = LoadHeight(texel + int2(stride, 0), slice, n) - LoadHeight(texel - int2(stride, 0), slice, n);  // x 方向の高さの差
  const float hz = LoadHeight(texel + int2(0, stride), slice, n) - LoadHeight(texel - int2(0, stride), slice, n);  // z 方向の高さの差
  const float run = 2.0 * cell * stride;                               // 差を取った 2 点の水平距離
  const float3 normal = normalize(float3(-hx / run, 1.0, -hz / run));  // 勾配から作る法線（上向き）

  VsOut o;
  const float2 xz = i.origin + (float2)texel * cell;                   // ワールドの xz
  o.world = float3(xz.x, h, xz.y);
  o.pos = mul(float4(o.world, 1.0), gViewProj);
  o.normal = normal;
  return o;
}
```

`stride` は LOD ごとの頂点の間隔で、LOD が 1 つ上がるごとに 2 倍になります。同じ格子の頂点が飛び飛びのテクセルを指すので、頂点の数は変わらずに地形の細かさが粗くなります（描かない頂点は縮退するわけではなく、三角形が大きくなるわけでもありません。頂点の数を減らしたいなら LOD ごとに別の格子を使います）。法線は中心差分で求めます。2 点の水平距離は `2 × cell × stride` で高さの差を割ると勾配になります。

ピクセル シェーダーは法線と余弦だけの簡単なものです。

```hlsl
float4 TerrainChunkPS(VsOut i) : SV_Target {
  const float3 sun = normalize(float3(0.4, 0.8, 0.3));                 // 仮の太陽の向き（太陽へ向かう）
  const float n_dot_l = saturate(dot(normalize(i.normal), sun));       // 余弦
  return float4(float3(0.35, 0.5, 0.25) * (0.2 + 0.8 * n_dot_l), 1);   // 緑の地面に、簡単な拡散光
}
```

## コード：インスタンスの描画とストリーミング {#cpp}

インスタンス データを詰めて、1 回の描画命令で描きます。

```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <vector>

#include <d3d11.h>

// 1 チャンク分のインスタンス データ。HLSL の VsIn（CHUNK_*）と同じ並び。32 バイトではなく 20 バイト(float 5 個)。
struct ChunkInstance {
  float origin_x, origin_z;  // チャンクの原点 (m)
  float size;                // 一辺 (m)
  float level;               // LOD
  float slice;               // 高さテクスチャ配列のスライス
};

struct Chunk {
  int grid_x, grid_z;  // 格子上の位置
  int lod = 0;
  int slice = -1;      // スライスを持っていれば 0 以上
  bool loaded = false;
  bool loading = false;
};

// 見えるチャンクをインスタンス バッファに詰めて、1 回の描画で描く。LOD ごとに頂点数の違う格子を使うなら、LOD ごとに呼ぶ。
void DrawChunks(ID3D11DeviceContext* context, ID3D11Buffer* instance_buffer, UINT index_count,
                const std::vector<const Chunk*>& visible, float chunk_size) {
  if (visible.empty()) return;                                 // 0 個のインスタンスを描かない
  D3D11_MAPPED_SUBRESOURCE mapped = {};
  // WRITE_DISCARD: 前フレームの内容を捨てて新しく書く。GPU が使っている最中でも待たされない。
  if (FAILED(context->Map(instance_buffer, 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped))) return;
  auto* dst = static_cast<ChunkInstance*>(mapped.pData);
  for (size_t i = 0; i < visible.size(); ++i) {
    const Chunk& c = *visible[i];
    dst[i] = {c.grid_x * chunk_size, c.grid_z * chunk_size, chunk_size, static_cast<float>(c.lod), static_cast<float>(c.slice)};
  }
  context->Unmap(instance_buffer, 0);
  // 同じ格子メッシュを、visible.size() 個の位置で描く。頂点バッファの 0 番に格子、1 番にこのバッファを割り当て済みとする。
  context->DrawIndexedInstanced(index_count, static_cast<UINT>(visible.size()), 0, 0, 0);
}

// プレイヤーの周りのチャンクを読み込み、離れたものを解放する。解放の半径は読み込みの半径より大きく取る(ヒステリシス)。
void UpdateStreaming(std::vector<Chunk>& chunks, float player_x, float player_z, float chunk_size, int load_radius,
                     int unload_radius, void (*request_load)(Chunk&), void (*unload)(Chunk&)) {
  const int px = static_cast<int>(std::floor(player_x / chunk_size));  // プレイヤーのいるチャンク
  const int pz = static_cast<int>(std::floor(player_z / chunk_size));
  for (Chunk& c : chunks) {
    const int d = std::max(std::abs(c.grid_x - px), std::abs(c.grid_z - pz));  // チェビシェフ距離(正方形の範囲)
    if (d <= load_radius && !c.loaded && !c.loading) request_load(c);  // 非同期の読み込みを要求
    if (d > unload_radius && c.loaded) unload(c);                      // 読み込み半径より外で解放(行き来で往復しない)
  }
}
```

`D3D11_MAP_WRITE_DISCARD` は前フレームの内容を捨てて新しく書くので、GPU が使っている最中でも待たされません。`visible` が空のときは 0 個のインスタンスを描かないように戻ります。

ストリーミングです。

```cpp
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <vector>

#include <d3d11.h>

// 1 チャンク分のインスタンス データ。HLSL の VsIn（CHUNK_*）と同じ並び。32 バイトではなく 20 バイト(float 5 個)。
struct ChunkInstance {
  float origin_x, origin_z;  // チャンクの原点 (m)
  float size;                // 一辺 (m)
  float level;               // LOD
  float slice;               // 高さテクスチャ配列のスライス
};

struct Chunk {
  int grid_x, grid_z;  // 格子上の位置
  int lod = 0;
  int slice = -1;      // スライスを持っていれば 0 以上
  bool loaded = false;
  bool loading = false;
};

// 見えるチャンクをインスタンス バッファに詰めて、1 回の描画で描く。LOD ごとに頂点数の違う格子を使うなら、LOD ごとに呼ぶ。
void DrawChunks(ID3D11DeviceContext* context, ID3D11Buffer* instance_buffer, UINT index_count,
                const std::vector<const Chunk*>& visible, float chunk_size) {
  if (visible.empty()) return;                                 // 0 個のインスタンスを描かない
  D3D11_MAPPED_SUBRESOURCE mapped = {};
  // WRITE_DISCARD: 前フレームの内容を捨てて新しく書く。GPU が使っている最中でも待たされない。
  if (FAILED(context->Map(instance_buffer, 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped))) return;
  auto* dst = static_cast<ChunkInstance*>(mapped.pData);
  for (size_t i = 0; i < visible.size(); ++i) {
    const Chunk& c = *visible[i];
    dst[i] = {c.grid_x * chunk_size, c.grid_z * chunk_size, chunk_size, static_cast<float>(c.lod), static_cast<float>(c.slice)};
  }
  context->Unmap(instance_buffer, 0);
  // 同じ格子メッシュを、visible.size() 個の位置で描く。頂点バッファの 0 番に格子、1 番にこのバッファを割り当て済みとする。
  context->DrawIndexedInstanced(index_count, static_cast<UINT>(visible.size()), 0, 0, 0);
}

// プレイヤーの周りのチャンクを読み込み、離れたものを解放する。解放の半径は読み込みの半径より大きく取る(ヒステリシス)。
void UpdateStreaming(std::vector<Chunk>& chunks, float player_x, float player_z, float chunk_size, int load_radius,
                     int unload_radius, void (*request_load)(Chunk&), void (*unload)(Chunk&)) {
  const int px = static_cast<int>(std::floor(player_x / chunk_size));  // プレイヤーのいるチャンク
  const int pz = static_cast<int>(std::floor(player_z / chunk_size));
  for (Chunk& c : chunks) {
    const int d = std::max(std::abs(c.grid_x - px), std::abs(c.grid_z - pz));  // チェビシェフ距離(正方形の範囲)
    if (d <= load_radius && !c.loaded && !c.loading) request_load(c);  // 非同期の読み込みを要求
    if (d > unload_radius && c.loaded) unload(c);                      // 読み込み半径より外で解放(行き来で往復しない)
  }
}
```

距離はチェビシェフ距離（x と z の差の大きい方）で、正方形の範囲になります。`d <= load_radius` で読み込みを要求し `d > unload_radius` で解放します。解放半径を読み込み半径より大きくするのが、ヒステリシスです。

## 動く図：ストリーミング {#anim}

<!-- fig:chunk-stream:begin -->
<svg class="fig illust motion" data-fig="chunk-stream" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-chunk-stream" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">チャンクのストリーミング: カメラが動くと、近いチャンクを読み込み、遠いチャンクを捨てる。メモリは一定</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">20×8 のチャンクの世界。カメラの半径 2.5 チャンク以内を読み込む。カメラを右へ 8 チャンク動かして、読み込み・解放の数を数える</text>
<rect x="50.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="120.0" width="560.0" height="224.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0.5"><line x1="78.0" y1="120.0" x2="78.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="106.0" y1="120.0" x2="106.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="134.0" y1="120.0" x2="134.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="162.0" y1="120.0" x2="162.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="190.0" y1="120.0" x2="190.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="218.0" y1="120.0" x2="218.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="246.0" y1="120.0" x2="246.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="274.0" y1="120.0" x2="274.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="302.0" y1="120.0" x2="302.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="330.0" y1="120.0" x2="330.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="358.0" y1="120.0" x2="358.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="386.0" y1="120.0" x2="386.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="414.0" y1="120.0" x2="414.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="442.0" y1="120.0" x2="442.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="470.0" y1="120.0" x2="470.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="498.0" y1="120.0" x2="498.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="526.0" y1="120.0" x2="526.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="554.0" y1="120.0" x2="554.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="582.0" y1="120.0" x2="582.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="148.0" x2="610.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="176.0" x2="610.0" y2="176.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="204.0" x2="610.0" y2="204.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="232.0" x2="610.0" y2="232.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="260.0" x2="610.0" y2="260.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="288.0" x2="610.0" y2="288.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="316.0" x2="610.0" y2="316.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="50.0" y="120.0" width="560.0" height="224.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<circle cx="134.0" cy="232.0" r="9" fill="#1f2937"><animate attributeName="cx" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1064;0.1574;0.2000;0.2511;0.2936;0.3447;0.3872;0.4383;0.4809;0.5319;0.5745;0.6255;0.6681;0.7191;0.7617;0.8128;1.0000" values="134;134;162;162;190;190;218;218;246;246;274;274;302;302;330;330;358;358"/></circle>
<text x="40" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">読み込んだ数(累計):</text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1573;0.1574;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1573;0.1574;0.2509;0.2511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2509;0.2511;0.3445;0.3447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3445;0.3447;0.4381;0.4383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4383;0.5317;0.5319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5317;0.5319;0.6254;0.6255;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6254;0.6255;0.7190;0.7191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7190;0.7191;0.8126;0.8128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">32<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8126;0.8128;1.0000" values="0;0;1;1"/></text>
<text x="40" y="430" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">捨てた数(累計):</text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1573;0.1574;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1573;0.1574;0.2509;0.2511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2509;0.2511;0.3445;0.3447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3445;0.3447;0.4381;0.4383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4383;0.5317;0.5319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5317;0.5319;0.6254;0.6255;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6254;0.6255;0.7190;0.7191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7190;0.7191;0.8126;0.8128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">32<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8126;0.8128;1.0000" values="0;0;1;1"/></text>
<text x="40" y="462" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">いま、メモリにあるチャンク:</text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1573;0.1574;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1573;0.1574;0.2509;0.2511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2509;0.2511;0.3445;0.3447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3445;0.3447;0.4381;0.4383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4383;0.5317;0.5319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5317;0.5319;0.6254;0.6255;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6254;0.6255;0.7190;0.7191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7190;0.7191;0.8126;0.8128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8126;0.8128;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8849;0.8851;1.0000" values="0;0;1;1"/><rect x="480" y="392" width="450" height="100" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="416" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">メモリのチャンクは 16〜16 個で、ほぼ一定</text>
<text x="496" y="439" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">1 歩あたり、新しく 4〜4、捨てる 4〜4</text>
<text x="496" y="461" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">世界がどれだけ広くても、必要なメモリは、半径で決まる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">広い世界を全部は持てない<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラの周りだけ持つ。動いた分だけ、読み込み・解放する<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.9062;0.9064;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">読み込みは、1 フレームに 1 つずつ、などに分けて、ガクつきを防ぐ<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.9062;0.9064;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>
<!-- fig:chunk-stream:end -->

## よくあるミス {#mistakes}

??? failure "区画の境目に隙間が見える"
    原因は境界の頂点の高さが、隣のチャンクと違うことです。境界の画素を重複して保存し両側で同じ値を使います。LOD が違うならスカートかモーフィングで隠します。

??? failure "山頂が突然消える"
    原因はチャンクの高さの最大が小さすぎて、AABB が山頂を含んでいないことです。最小・最大は高さマップの全画素から求めます。サンプルした数点で決めると点の間の山頂を見落とします。

??? failure "境界を行き来すると、読み込みが止まらない"
    原因は読み込みの半径と解放の半径が同じことです。往復するだけで読み込みと解放が毎フレーム起きます。解放半径を 1 つ以上大きくします。

??? failure "境界で高さが半テクセルずれる"
    原因は `uv = i / N` で高さマップを引いていることです。`(N+1)` 画素のマップでは `(i + 0.5) / (N+1)` が正しい UV です。`Load` で整数座標を使うと避けられます。

??? failure "速く動くと読み込みの瞬間にフレームが跳ねる"
    原因は読み込みを 1 フレームに全部実行していることです。50 m/s で境界を越えると、17 個を一度に読みます。非同期にして 1 フレームあたりの個数を制限します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] チャンクは 64 m（65×65 頂点）か 128 m が目安。256 m は頂点が 66,049 個で 32 ビットのインデックスが要る
    - [x] 視錐台カリングは p 頂点テスト。四分木なら遠方 2000 m で 1913 回の判定（全探索は 62,500 回）
    - [x] 格子メッシュは 1 つを共有し、位置・LOD・スライスをインスタンスで渡す
    - [x] 境界の画素を重ねる代償は 64 セルで 3.15%。高さは `Load` で整数座標を使う
    - [x] 解放の半径は読み込みの半径より大きく取る

## C++ で数えたもの {#numbers}

```cpp
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
#include <numbers>
#include <vector>

struct Float3 { float x, y, z; };
struct BoundingBox { Float3 min, max; };           // ワールド座標の AABB
struct Plane { Float3 n; float d; };                // 内側が n·p + d >= 0
struct Frustum { Plane planes[6]; };                // 近、遠、左、右、上、下

float Dot(Float3 a, Float3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
Float3 Normalize(Float3 v) { const float l = std::sqrt(Dot(v, v)); return {v.x / l, v.y / l, v.z / l}; }
Float3 Add(Float3 a, Float3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
Float3 Scale(Float3 a, float s) { return {a.x * s, a.y * s, a.z * s}; }

// 地形の高さ(ダミー)。なだらかな起伏。単位 m。
float TerrainHeight(float x, float z) {
  return 120.0f * std::sin(x / 900.0f) * std::cos(z / 700.0f) + 40.0f * std::sin(x / 170.0f + z / 230.0f);
}

struct TerrainChunk {
  int grid_x, grid_z;            // チャンクの格子上の位置
  float min_height, max_height;  // 高さの最小・最大(AABB のため)
  BoundingBox bounds;            // ワールド座標の AABB
};

// チャンクの AABB。チャンクの原点 (grid * size) から size 四方、高さは min..max。
BoundingBox ChunkBounds(const TerrainChunk& c, float chunk_size) {
  const float x0 = c.grid_x * chunk_size, z0 = c.grid_z * chunk_size;
  return {{x0, c.min_height, z0}, {x0 + chunk_size, c.max_height, z0 + chunk_size}};
}

// カメラ(位置 pos、水平方向の向き yaw、水平 FOV、アスペクト比)から視錐台の 6 平面を作る。法線は内向き。
// 導出: 左の平面は、前方向と右方向を (sin(h/2), cos(h/2)) で混ぜた向きが法線になる。
Frustum MakeFrustum(Float3 pos, float yaw, float hfov, float aspect, float near_z, float far_z) {
  const Float3 f = {std::sin(yaw), 0.0f, std::cos(yaw)};        // 前(+Z が yaw = 0)
  const Float3 r = {std::cos(yaw), 0.0f, -std::sin(yaw)};       // 右
  const Float3 u = {0.0f, 1.0f, 0.0f};                          // 上
  const float vfov = 2.0f * std::atan(std::tan(hfov / 2.0f) / aspect);
  const float sh = std::sin(hfov / 2.0f), ch = std::cos(hfov / 2.0f);
  const float sv = std::sin(vfov / 2.0f), cv = std::cos(vfov / 2.0f);
  auto make = [&](Float3 n) { n = Normalize(n); return Plane{n, -Dot(n, pos)}; };  // pos を通る平面
  Frustum fr;
  fr.planes[0] = Plane{f, -Dot(f, pos) - near_z};                                   // 近
  fr.planes[1] = Plane{Scale(f, -1.0f), Dot(f, pos) + far_z};                       // 遠
  fr.planes[2] = make(Add(Scale(r, ch), Scale(f, sh)));                             // 左
  fr.planes[3] = make(Add(Scale(r, -ch), Scale(f, sh)));                            // 右
  fr.planes[4] = make(Add(Scale(u, -cv), Scale(f, sv)));                            // 上
  fr.planes[5] = make(Add(Scale(u, cv), Scale(f, sv)));                             // 下
  return fr;
}

// AABB と 6 枚の平面の判定(p 頂点テスト)。平面の法線に最も進んだ頂点が外側なら、完全に外。
bool Visible(const Frustum& fr, const BoundingBox& box) {
  for (const Plane& pl : fr.planes) {
    const Float3 p = {pl.n.x >= 0 ? box.max.x : box.min.x, pl.n.y >= 0 ? box.max.y : box.min.y,
                      pl.n.z >= 0 ? box.max.z : box.min.z};
    if (Dot(pl.n, p) + pl.d < 0) return false;  // 完全に外側
  }
  return true;
}

// 四分木。葉は 1 チャンク。節の AABB は含むチャンクの AABB の和。
struct QuadNode {
  BoundingBox box;
  int x0, z0, size;  // 含むチャンクの範囲(格子)
};

int g_tests = 0;                                  // 数えるための、AABB 判定の回数
void CullQuad(const std::vector<TerrainChunk>& chunks, int n, const Frustum& fr, const QuadNode& node,
              std::vector<int>& out, float chunk_size) {
  ++g_tests;
  if (!Visible(fr, node.box)) return;              // 節ごと捨てる
  if (node.size == 1) { out.push_back(node.z0 * n + node.x0); return; }
  const int h = node.size / 2;
  for (int dz = 0; dz < 2; ++dz) {
    for (int dx = 0; dx < 2; ++dx) {
      QuadNode c{{}, node.x0 + dx * h, node.z0 + dz * h, h};
      if (c.x0 >= n || c.z0 >= n) continue;         // 世界の外
      // 子の AABB を求める(ここでは毎回、含むチャンクから作る。実際は事前に作って持つ)。
      float mn = 1e9f, mx = -1e9f;
      for (int z = c.z0; z < std::min(c.z0 + h, n); ++z)
        for (int x = c.x0; x < std::min(c.x0 + h, n); ++x) {
          mn = std::min(mn, chunks[static_cast<size_t>(z) * n + x].min_height);
          mx = std::max(mx, chunks[static_cast<size_t>(z) * n + x].max_height);
        }
      c.box = {{c.x0 * chunk_size, mn, c.z0 * chunk_size},
               {std::min(c.x0 + h, n) * chunk_size, mx, std::min(c.z0 + h, n) * chunk_size}};
      CullQuad(chunks, n, fr, c, out, chunk_size);
    }
  }
}

int main() {
  const double kPi = std::numbers::pi;
  // 1. チャンクの大きさと、頂点・三角形・インデックスの数。格子の幅 N セル、頂点 (N+1)^2、三角形 2 N^2。
  std::printf("-- chunk mesh size\n");
  for (int n : {16, 32, 64, 128, 256}) {
    const long verts = static_cast<long>(n + 1) * (n + 1);
    const long tris = 2L * n * n;
    const long indices = 6L * n * n;
    std::printf("N = %3d: %6ld verts, %6ld tris, %7ld indices (%s, %6.1f KiB), overlap storage (N+1)^2/N^2 = %.4f\n", n, verts, tris,
                indices, verts <= 65536 ? "16-bit" : "32-bit", indices * (verts <= 65536 ? 2.0 : 4.0) / 1024.0,
                static_cast<double>(verts) / (static_cast<double>(n) * n));
  }

  // 2. 世界 16 km、チャンクの大きさごとのチャンク数。
  std::printf("-- chunk count for a 16 km world\n");
  for (int size : {16, 32, 64, 128, 256}) {
    const int cnt = 16000 / size;
    std::printf("chunk %3d m: %4d x %4d = %7d chunks\n", size, cnt, cnt, cnt * cnt);
  }

  // 3. 視錐台カリングの実測。世界 16 km、チャンク 64 m (250 x 250 = 62500)。カメラは中央、水平 FOV 90 度、16:9。
  const float chunk_size = 64.0f;
  const int n = 250;
  std::vector<TerrainChunk> chunks(static_cast<size_t>(n) * n);
  for (int z = 0; z < n; ++z) {
    for (int x = 0; x < n; ++x) {
      TerrainChunk& c = chunks[static_cast<size_t>(z) * n + x];
      c.grid_x = x; c.grid_z = z;
      float mn = 1e9f, mx = -1e9f;
      for (int j = 0; j <= 8; ++j)                                        // 9 x 9 点で高さの最小・最大を見積もる
        for (int i = 0; i <= 8; ++i) {
          const float h = TerrainHeight(x * chunk_size + i * chunk_size / 8, z * chunk_size + j * chunk_size / 8);
          mn = std::min(mn, h); mx = std::max(mx, h);
        }
      c.min_height = mn; c.max_height = mx;
      c.bounds = ChunkBounds(c, chunk_size);
    }
  }
  std::printf("-- frustum culling (62500 chunks, hfov 90, 16:9)\n");
  const Float3 cam = {8000.0f, 150.0f, 8000.0f};
  for (float far_z : {1000.0f, 2000.0f, 4000.0f}) {
    for (float yaw_deg : {0.0f, 45.0f}) {
      const Frustum fr = MakeFrustum(cam, yaw_deg * static_cast<float>(kPi) / 180.0f, static_cast<float>(kPi) / 2.0f, 16.0f / 9.0f, 0.5f, far_z);
      int flat = 0;
      for (const TerrainChunk& c : chunks) flat += Visible(fr, c.bounds) ? 1 : 0;       // 全部を調べる
      std::vector<int> quad;
      g_tests = 0;
      const QuadNode root{{{0, -1e9f, 0}, {256 * chunk_size, 1e9f, 256 * chunk_size}}, 0, 0, 256};
      CullQuad(chunks, n, fr, root, quad, chunk_size);
      assert(static_cast<int>(quad.size()) == flat);                                      // 四分木の結果は全探索と同じはず
      std::printf("far %4.0f m, yaw %2.0f: visible %5d chunks (%.2f%%), flat tests 62500, quadtree tests %5d\n", far_z, yaw_deg, flat,
                  flat * 100.0 / 62500.0, g_tests);
    }
  }

  // 4. ストリーミングの量。読み込み半径 r チャンクのとき、保持するチャンクは (2r+1)^2。1 チャンク分動くと、新しく読むのは 2r+1 個。
  std::printf("-- streaming budget (chunk 64 m, R16 65x65 height = 8450 bytes)\n");
  for (int r : {4, 8, 12, 16}) {
    const int held = (2 * r + 1) * (2 * r + 1);
    std::printf("r = %2d: holds %4d chunks = %6.2f MiB of heights, %2d new per chunk step, view distance ~%d m\n", r, held,
                held * 8450.0 / 1048576.0, 2 * r + 1, r * 64);
  }
  for (double speed : {5.0, 10.0, 50.0}) {
    std::printf("speed %4.0f m/s: crosses a chunk boundary every %5.2f s\n", speed, 64.0 / speed);
  }

  // 5. ヒステリシス。プレイヤーが境界の近くを往復するとき、読み込み半径 = 解放半径だと毎回読み込み・解放が起きる。
  //    1 次元で数える。チャンク番号 px が 10 と 11 を毎フレーム往復、読み込み半径 2。
  std::printf("-- hysteresis (1D, oscillating across a chunk boundary for 100 frames)\n");
  for (int unload_radius : {2, 3, 4}) {
    std::vector<bool> loaded(40, false);
    int loads = 0, unloads = 0;
    for (int frame = 0; frame < 100; ++frame) {
      const int px = (frame % 2 == 0) ? 10 : 11;                        // 往復
      for (int c = 0; c < 40; ++c) {
        const int d = std::abs(c - px);
        if (d <= 2 && !loaded[c]) { loaded[c] = true; ++loads; }       // 読み込み半径 2 以内を読む
        if (d > unload_radius && loaded[c]) { loaded[c] = false; ++unloads; }
      }
    }
    std::printf("load radius 2, unload radius %d: loads %3d, unloads %3d\n", unload_radius, loads, unloads);
  }

  // 6. 境界の半テクセル。(N+1) 画素の高さマップを、頂点 i (0..N) から UV で引く。正しい UV は (i + 0.5) / (N+1)。
  //    誤って i / N とすると、テクセル座標 = uv * (N+1) - 0.5 が頂点の整数位置からずれる。
  std::printf("-- half-texel error when sampling an (N+1) height map with uv = i / N\n");
  for (int nn : {16, 64}) {
    for (int i : {0, nn / 2, nn}) {
      const double wrong_texel = static_cast<double>(i) / nn * (nn + 1) - 0.5;   // 誤った UV が指すテクセル座標
      std::printf("N = %2d, vertex %2d: samples texel %7.3f (want %2d), error %+.3f texel\n", nn, i, wrong_texel, i, wrong_texel - i);
    }
  }

  // 7. インスタンス データ。1 インスタンス 20 バイト(float2 origin, size, level, slice)。
  std::printf("-- instancing upload and shared mesh\n");
  for (int count : {300, 1000, 3000}) {
    std::printf("%4d instances: %6.2f KiB per frame; separate meshes would be %7.1f MiB (65x65 mesh = 48 KiB each)\n", count,
                count * 20.0 / 1024.0, count * 48.0 / 1024.0);
  }
}
```

```text title="実行結果"
-- chunk mesh size
N =  16:    289 verts,    512 tris,    1536 indices (16-bit,    3.0 KiB), overlap storage (N+1)^2/N^2 = 1.1289
N =  32:   1089 verts,   2048 tris,    6144 indices (16-bit,   12.0 KiB), overlap storage (N+1)^2/N^2 = 1.0635
N =  64:   4225 verts,   8192 tris,   24576 indices (16-bit,   48.0 KiB), overlap storage (N+1)^2/N^2 = 1.0315
N = 128:  16641 verts,  32768 tris,   98304 indices (16-bit,  192.0 KiB), overlap storage (N+1)^2/N^2 = 1.0157
N = 256:  66049 verts, 131072 tris,  393216 indices (32-bit, 1536.0 KiB), overlap storage (N+1)^2/N^2 = 1.0078
-- chunk count for a 16 km world
chunk  16 m: 1000 x 1000 = 1000000 chunks
chunk  32 m:  500 x  500 =  250000 chunks
chunk  64 m:  250 x  250 =   62500 chunks
chunk 128 m:  125 x  125 =   15625 chunks
chunk 256 m:   62 x   62 =    3844 chunks
-- frustum culling (62500 chunks, hfov 90, 16:9)
far 1000 m, yaw  0: visible   294 chunks (0.47%), flat tests 62500, quadtree tests   665
far 1000 m, yaw 45: visible   315 chunks (0.50%), flat tests 62500, quadtree tests   641
far 2000 m, yaw  0: visible  1110 chunks (1.78%), flat tests 62500, quadtree tests  1913
far 2000 m, yaw 45: visible  1118 chunks (1.79%), flat tests 62500, quadtree tests  1765
far 4000 m, yaw  0: visible  4148 chunks (6.64%), flat tests 62500, quadtree tests  6065
far 4000 m, yaw 45: visible  4176 chunks (6.68%), flat tests 62500, quadtree tests  6045
-- streaming budget (chunk 64 m, R16 65x65 height = 8450 bytes)
r =  4: holds   81 chunks =   0.65 MiB of heights,  9 new per chunk step, view distance ~256 m
r =  8: holds  289 chunks =   2.33 MiB of heights, 17 new per chunk step, view distance ~512 m
r = 12: holds  625 chunks =   5.04 MiB of heights, 25 new per chunk step, view distance ~768 m
r = 16: holds 1089 chunks =   8.78 MiB of heights, 33 new per chunk step, view distance ~1024 m
speed    5 m/s: crosses a chunk boundary every 12.80 s
speed   10 m/s: crosses a chunk boundary every  6.40 s
speed   50 m/s: crosses a chunk boundary every  1.28 s
-- hysteresis (1D, oscillating across a chunk boundary for 100 frames)
load radius 2, unload radius 2: loads 104, unloads  99
load radius 2, unload radius 3: loads   6, unloads   0
load radius 2, unload radius 4: loads   6, unloads   0
-- half-texel error when sampling an (N+1) height map with uv = i / N
N = 16, vertex  0: samples texel  -0.500 (want  0), error -0.500 texel
N = 16, vertex  8: samples texel   8.000 (want  8), error +0.000 texel
N = 16, vertex 16: samples texel  16.500 (want 16), error +0.500 texel
N = 64, vertex  0: samples texel  -0.500 (want  0), error -0.500 texel
N = 64, vertex 32: samples texel  32.000 (want 32), error +0.000 texel
N = 64, vertex 64: samples texel  64.500 (want 64), error +0.500 texel
-- instancing upload and shared mesh
 300 instances:   5.86 KiB per frame; separate meshes would be    14.1 MiB (65x65 mesh = 48 KiB each)
1000 instances:  19.53 KiB per frame; separate meshes would be    46.9 MiB (65x65 mesh = 48 KiB each)
3000 instances:  58.59 KiB per frame; separate meshes would be   140.6 MiB (65x65 mesh = 48 KiB each)
```

## 参考資料 {#references}

このページの数字は C++ で数え直したものです。視錐台の平面の式は自分で導いたものです。以下の資料は**今回は読んでいません**。

- Thatcher Ulrich, "Rendering Massive Terrains Using Chunked Level of Detail Control", SIGGRAPH 2002 Course Notes
- Filip Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）
- Gil Gribb, Klaus Hartmann, "Fast Extraction of Viewing Frustum Planes from the World-View-Projection Matrix", 2001（視錐台の平面を行列から取り出す）

## 関連ページ {#related}

- [Heightmaps and Meshes](index.md)
- [LOD](../lod/index.md)
- [CDLOD](../lod/cdlod.md)
- [Cracks and Seams](../lod/cracks.md)
