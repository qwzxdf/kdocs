---
title: GPU Driven Rendering
tags:
  - 最適化
  - 3Dゲーム
---

# GPU Driven Rendering

草と岩と瓦礫を置いた広いマップで、物体を 10 万個まで増やしたとします。視界に入るのはそのうち 6,500 個ほどです。それでも CPU は 10 万個の可視判定を毎フレーム回して、見えた 6,500 個にドロー コールを 1 つずつ出します。ドロー コール 1 回が CPU で 5 マイクロ秒かかるとすると、これだけで 32 ミリ秒です。60 fps の 16.7 ミリ秒を描画命令を作るだけで使い切ります。GPU は暇なのに CPU が命令を作りきれないという状態です。

この仕事をそっくり GPU に渡す方式が GPU Driven Rendering です。物体のデータを GPU のバッファに置いたままにして、可視判定も描画命令の作成もコンピュート シェーダーで行います。CPU が毎フレーム出す命令はメッシュの種類の数（このページの例では 64 回）で済みます。

このページは D3D11 で動く最小の形を 1 行ずつ解説しながら組み立てます。流れは「常駐データ → カリング → 描画引数 → インダイレクト描画」です。数字は 10 万個のシーンを CPU 上で再現して数えました。HLSL は `fxc` を通し C++ は構文だけ確かめています。実機では動かしていません（くわしくは「確かめたこと」）。

!!! tip "ポイント"
    - 目的はカリングと描画命令の作成を CPU から GPU へ移すことです。物体が 10 倍になっても CPU の仕事はほとんど増えません。
    - 中心になる仕組みは 4 段階です。①全物体のデータを GPU に常駐させる ②コンピュート シェーダーで見える物を選ぶ ③生き残った物の描画引数を GPU が書く ④インダイレクト描画で、GPU が自分で書いた命令を実行する。
    - 見えた個数を CPU は知りません。知らないから GPU から CPU へ結果を読み戻す同期待ちが起きません。
    - D3D11 では `DrawIndexedInstancedIndirect` をメッシュの種類ごとに 1 回ずつ呼びます。複数の描画を 1 回の命令にまとめる本物のマルチ ドローは、D3D12 の `ExecuteIndirect` と Vulkan が担当します。
    - 苦手なことは材質の切り替え半透明のソート、アニメーションする頂点です。GPU Driven は CPU が限界になってから導入します。

!!! info "このページを読む前に"
    - [Draw Call](index.md)（このセクション全体の地図と読む順番）
    - [Draw Calls and Batching](draw-calls.md)（ドロー コール 1 回のコストと、まとめる方法）
    - [Culling](culling.md)（視錐台とオクルージョンの判定。ここではその判定を GPU に移す）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 1. CPU Driven のどこが詰まるか

CPU Driven では毎フレーム次の 4 つの仕事を CPU が繰り返します。

<svg class="fig illust" viewBox="0 0 800 280" role="img" aria-label="CPU Driven と GPU Driven の比べ">
<defs><marker id="gd1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">上：CPU Driven（CPU が毎フレーム全部やる）／下：GPU Driven（GPU が自分で決めて描く）</text>
<rect x="20" y="40" width="130" height="60" rx="8" fill="rgba(229,72,77,0.25)" stroke="currentColor" stroke-width="2"/><text x="85" y="66" text-anchor="middle" style="font-weight:700">CPU</text><text x="85" y="86" text-anchor="middle" style="font-size:11px">全物体を判定</text>
<line x1="156" y1="70" x2="206" y2="70" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="214" y="40" width="190" height="60" rx="8" fill="rgba(229,72,77,0.25)" stroke="currentColor" stroke-width="2"/><text x="309" y="66" text-anchor="middle" style="font-weight:700">ドロー コール × 6,528</text><text x="309" y="86" text-anchor="middle" style="font-size:11px">見えた物ごとに命令を作る</text>
<line x1="410" y1="70" x2="460" y2="70" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="468" y="40" width="130" height="60" rx="8" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="533" y="76" text-anchor="middle" style="font-weight:700">GPU が描く</text>
<text x="620" y="76" style="font-size:12px;fill:#e5484d;font-weight:700">CPU がボトルネック</text>
<rect x="20" y="150" width="190" height="90" rx="8" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/><text x="115" y="176" text-anchor="middle" style="font-weight:700">全物体のデータ</text><text x="115" y="196" text-anchor="middle" style="font-size:11px">GPU バッファに常駐</text><text x="115" y="214" text-anchor="middle" style="font-size:11px">（毎フレーム送らない）</text>
<line x1="216" y1="195" x2="262" y2="195" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="270" y="150" width="170" height="90" rx="8" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="355" y="176" text-anchor="middle" style="font-weight:700">コンピュート</text><text x="355" y="196" text-anchor="middle" style="font-size:11px">カリング</text><text x="355" y="214" text-anchor="middle" style="font-size:11px">描画引数を書く</text>
<line x1="446" y1="195" x2="492" y2="195" stroke="currentColor" stroke-width="3" marker-end="url(#gd1)"/>
<rect x="500" y="150" width="150" height="90" rx="8" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="575" y="176" text-anchor="middle" style="font-weight:700">インダイレクト</text><text x="575" y="196" text-anchor="middle" style="font-size:11px">描画（メッシュ数だけ）</text>
<text x="660" y="196" style="font-size:12px;fill:#2ea043;font-weight:700">CPU はほぼ暇</text>
</svg>

1. 物体ごとの可視判定です。10 万個ぶんの球と視錐台の 6 平面を比べると、1 フレームに 60 万回の内積になります。
2. 物体ごとの描画命令です。見えた 6,528 個にそれぞれドロー コールを出します。
3. 物体ごとの定数の転送です。ワールド行列 64 バイトを 6,528 個ぶん書くと 1 フレームに 0.42 MB、60 fps で 25 MB/s の CPU から GPU への転送になります。
4. 結果を待てないことです。GPU が出した可視判定の結果を CPU が読もうとすると、GPU の完了を待つ同期が入ります。待たないために CPU 側で自前の判定を繰り返すことになります。

ドロー コール 1 回の CPU 時間は、ドライバや状態の数で大きく変わります。ここでは 2、5、10 マイクロ秒と仮定して見積もります（実測ではありません）。

- 2 マイクロ秒なら 6,528 回で 13.1 ミリ秒です。16.7 ミリ秒の枠のほぼ 8 割で、描ける上限は 8,334 回です。
- 5 マイクロ秒なら 32.6 ミリ秒です。枠を超えて上限は 3,333 回です。
- 10 マイクロ秒なら 65.3 ミリ秒です。上限は 1,667 回で見えた 6,528 個の 4 分の 1 も描けません。

GPU Driven にすると、CPU が出す命令はメッシュの種類の数だけです。このシーンの 64 回なら同じ仮定で 0.13、0.32、0.64 ミリ秒になります。物体が 10 万個から 100 万個に増えても、CPU が出す命令は 64 回のままです。

## 2. 全体像：毎フレームの 4 段階

毎フレームの流れは次の図のとおりです。青い箱が GPU 上のバッファで、黄色い箱がコンピュート シェーダー、緑がインダイレクト描画です。

<svg class="fig flow" viewBox="0 0 820 300" role="img" aria-label="GPU Driven の毎フレームの流れ">
<defs><marker id="gd2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">毎フレームの流れ（GPU 上で完結する）</text>
<rect x="20" y="44" width="150" height="56" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="95" y="68" text-anchor="middle" style="font-weight:700">instances</text><text x="95" y="86" text-anchor="middle" style="font-size:11px">100,000 × 96 B</text>
<rect x="20" y="124" width="150" height="56" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="95" y="148" text-anchor="middle" style="font-weight:700">meshes</text><text x="95" y="166" text-anchor="middle" style="font-size:11px">64 × 16 B</text>
<rect x="20" y="214" width="150" height="56" rx="8" fill="rgba(229,170,40,0.28)" stroke="currentColor" stroke-width="2"/><text x="95" y="238" text-anchor="middle" style="font-weight:700">① counts を 0 に</text><text x="95" y="256" text-anchor="middle" style="font-size:11px">ClearUAV</text>
<line x1="176" y1="72" x2="232" y2="130" stroke="currentColor" stroke-width="2.5" marker-end="url(#gd2)"/>
<line x1="176" y1="152" x2="232" y2="150" stroke="currentColor" stroke-width="2.5" marker-end="url(#gd2)"/>
<line x1="176" y1="240" x2="232" y2="166" stroke="currentColor" stroke-width="2.5" marker-end="url(#gd2)"/>
<rect x="240" y="104" width="150" height="76" rx="8" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="315" y="130" text-anchor="middle" style="font-weight:700">② CullCS</text><text x="315" y="150" text-anchor="middle" style="font-size:11px">1 スレッド = 1 物体</text><text x="315" y="168" text-anchor="middle" style="font-size:11px">視錐台＋距離</text>
<line x1="396" y1="130" x2="450" y2="86" stroke="currentColor" stroke-width="2.5" marker-end="url(#gd2)"/>
<line x1="396" y1="154" x2="450" y2="196" stroke="currentColor" stroke-width="2.5" marker-end="url(#gd2)"/>
<rect x="458" y="56" width="140" height="56" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="528" y="80" text-anchor="middle" style="font-weight:700">visible</text><text x="528" y="98" text-anchor="middle" style="font-size:11px">見えた物の番号</text>
<rect x="458" y="170" width="140" height="56" rx="8" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="2"/><text x="528" y="194" text-anchor="middle" style="font-weight:700">counts</text><text x="528" y="212" text-anchor="middle" style="font-size:11px">メッシュごとの個数</text>
<line x1="604" y1="198" x2="650" y2="168" stroke="currentColor" stroke-width="2.5" marker-end="url(#gd2)"/>
<rect x="652" y="124" width="150" height="76" rx="8" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="727" y="150" text-anchor="middle" style="font-weight:700">③ BuildArgsCS</text><text x="727" y="170" text-anchor="middle" style="font-size:11px">描画引数 20 B × 64</text><text x="727" y="188" text-anchor="middle" style="font-size:11px">を書く</text>
<line x1="727" y1="206" x2="727" y2="240" stroke="currentColor" stroke-width="2.5" marker-end="url(#gd2)"/>
<rect x="560" y="244" width="242" height="46" rx="8" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="681" y="264" text-anchor="middle" style="font-weight:700">④ DrawIndexedInstancedIndirect × 64</text><text x="681" y="281" text-anchor="middle" style="font-size:11px">VS が visible[offset + SV_InstanceID] を読む</text>
<line x1="528" y1="116" x2="600" y2="246" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#gd2)"/>
</svg>

CPU が書く部分はほとんどありません。起動時にバッファを作り毎フレーム「カウンターを 0 にする、ディスパッチを 2 回、メッシュの数だけ描画を呼ぶ」の 3 種類を並べるだけです。ここから先は各段階を実際のコードで追います。コードは通して読める 1 つのつながりですが、解説のために意味のまとまりで区切って載せています。

## 3. データを GPU に常駐させる

GPU に置くものは 2 種類です。1 つは物体ごとのデータ（インスタンス）で、もう 1 つはメッシュの種類ごとのデータ（メッシュ表）です。まずその 2 つの構造体です。

```hlsl
// ① GPU に常駐させるインスタンス 1 個ぶん。C++ 側の構造体と、並びも大きさも一致させる(96 バイト)。
struct Instance {
  row_major float4x4 world;   // モデル → ワールド(64 バイト)
  float4 sphere;              // xyz = ワールドでの境界球の中心、w = 半径(メートル)(16 バイト)
  uint mesh_id;               // どのメッシュか(メッシュ表の添字)
  uint material_id;           // どの材質か(この最小例では使わない)
  uint2 pad;                  // 16 バイト境界にそろえる
};

// ② メッシュ 1 種類ぶんの描画に必要な値。ロード時に CPU が埋めて、以後は変えない。
struct MeshInfo {
  uint index_count;           // このメッシュのインデックス数
  uint start_index;           // 巨大なインデックス バッファの中の先頭位置
  int  base_vertex;           // 巨大な頂点バッファの中の先頭位置
  uint out_offset;            // visible_indices の中で、このメッシュに割り当てた範囲の先頭
};
```

`Instance` が 1 物体ぶんです。`world` はモデルからワールドへの行列で、HLSL の既定は列優先なので、C++ の行優先の並びに合わせて `row_major` を付けています。付け忘れると行列が転置されて、物体がまるで別の場所に飛びます。`sphere` はワールド空間での境界球で、中心と半径を 1 つの `float4` に詰めています。カリングが読むのはこの 16 バイトだけなので、判定のためにほかのメンバーまで読み込むのを避けたいときは、球だけ別のバッファに分ける設計も使えます。`mesh_id` はどのメッシュの物体かを表し、`material_id` は材質の番号です（この最小例では使いません）。最後の `pad` は全体を 96 バイトにそろえるための詰め物です。64 + 16 + 4 + 4 + 8 で 96 バイトになり 16 の倍数なので構造化バッファの要素として扱いやすくなります。C++ 側の構造体と大きさや並びが 1 バイトでもずれると、2 つ目以降の物体が壊れたデータを読みます。

10 万個なら 96 × 100,000 = 9.60 MB です。この全体を毎フレーム GPU に送るわけではありません。起動時に 1 回作って置いておき動いた物だけ `UpdateSubresource` などで部分的に書き換えます。動かない物（岩や建物）が大半のシーンでは、毎フレームの転送量が大きく減ります。

`MeshInfo` がメッシュ 1 種類ぶんです。`index_count`、`start_index`、`base_vertex` は描画の引数にそのまま渡す値です。全メッシュの頂点とインデックスを 1 つの巨大なバッファに連結しておきメッシュごとの先頭位置で区別します。`out_offset` だけは描画の引数ではなく、後のカリングで使う「このメッシュの出力範囲の先頭」です。次の節で詳しく説明します。

## 4. 出力先を先に割り当てる

カリングは見えた物の番号を `visible` というバッファに詰めます。描画はメッシュごとに 1 回なので、`visible` の中でメッシュ 0 の物は連続して並び次にメッシュ 1 の物が並んでほしいところです。ところが、何個見えるかはカリングが終わるまで分かりません。そこで、各メッシュの範囲を見えるかどうかに関係なく「そのメッシュの物体の総数」ぶん先に確保します。

<svg class="fig illust" viewBox="0 0 800 230" role="img" aria-label="visible バッファの範囲の割り当て">
<defs><marker id="gd3" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="22" class="fig-title">visible バッファ：メッシュごとの範囲は総数ぶん確保する（色が付いた所だけ使われる）</text>
<rect x="30" y="50" width="740" height="40" rx="4" fill="none" stroke="currentColor" stroke-width="2"/>
<rect x="30" y="50" width="60" height="40" fill="rgba(46,160,67,0.4)" stroke="currentColor"/><rect x="90" y="50" width="160" height="40" fill="rgba(128,128,128,0.12)" stroke="currentColor"/>
<rect x="250" y="50" width="30" height="40" fill="rgba(46,160,67,0.4)" stroke="currentColor"/><rect x="280" y="50" width="200" height="40" fill="rgba(128,128,128,0.12)" stroke="currentColor"/>
<rect x="480" y="50" width="80" height="40" fill="rgba(46,160,67,0.4)" stroke="currentColor"/><rect x="560" y="50" width="210" height="40" fill="rgba(128,128,128,0.12)" stroke="currentColor"/>
<text x="60" y="76" text-anchor="middle" style="font-size:11px">見えた</text><text x="170" y="76" text-anchor="middle" style="font-size:11px">未使用（穴）</text>
<text x="265" y="76" text-anchor="middle" style="font-size:10px">見</text><text x="380" y="76" text-anchor="middle" style="font-size:11px">未使用（穴）</text>
<text x="520" y="76" text-anchor="middle" style="font-size:11px">見えた</text><text x="665" y="76" text-anchor="middle" style="font-size:11px">未使用（穴）</text>
<line x1="30" y1="96" x2="30" y2="130" stroke="currentColor" stroke-width="1.5"/><text x="30" y="148" text-anchor="middle" style="font-size:12px">offset[0] = 0</text>
<line x1="250" y1="96" x2="250" y2="130" stroke="currentColor" stroke-width="1.5"/><text x="250" y="148" text-anchor="middle" style="font-size:12px">offset[1] = total[0]</text>
<line x1="480" y1="96" x2="480" y2="130" stroke="currentColor" stroke-width="1.5"/><text x="480" y="148" text-anchor="middle" style="font-size:12px">offset[2] = total[0] + total[1]</text>
<text x="140" y="176" text-anchor="middle" style="font-size:11px">メッシュ 0 の範囲（total[0] 個）</text>
<text x="365" y="176" text-anchor="middle" style="font-size:11px">メッシュ 1 の範囲</text>
<text x="625" y="176" text-anchor="middle" style="font-size:11px">メッシュ 2 の範囲</text>
<text x="20" y="210" style="font-size:12px">このシーン：100,000 枠のうち、使われるのは 6,528 枠（6.5%）。残り 93,472 枠（93.5%）は穴になる。</text>
</svg>

各範囲の先頭 `offset[m]` はメッシュごとの総数の累積和（前置和）です。物体の総数はロード時に分かるので、計算は 1 回で済みます。

```cpp
  // メッシュごとの出力範囲の先頭(ロード時に 1 回計算する前置和)。各範囲は総数ぶん確保するので、あふれない。
  std::vector<uint32_t> offset(M, 0);
  for (int m = 1; m < M; ++m) offset[m] = offset[m - 1] + total_per_mesh[m - 1];
```

`offset[0]` は 0 で `offset[m]` は直前までの総数の合計です。この図でメッシュ 1 の範囲はメッシュ 0 の範囲の直後から始まります。各範囲が自分の総数ぶんあるので、1 つのメッシュの見えた個数が総数を超えることはなく、隣の範囲にあふれません。

代償は穴です。見えた物は 6,528 個なのに、`visible` は 100,000 個ぶん（391 KB）確保します。穴の 93.5% はほとんど読まれないので、メモリ帯域には効きませんが確保する量としては無駄が出ます。カリングの結果を詰め直す方法（プレフィックス サム）もありますが、実装が複雑になります。まずは総数ぶん確保する方式から始めて、メモリが問題になってから詰め直しを検討します。

C++ 上で同じ手順を再現して、配置を検証しました。全メッシュの範囲の中身を調べると、範囲外の物を指す要素は 0 件でした。見えた個数のメッシュごとの合計は 6,528 で、視錐台を通った数と一致します。

## 5. コンピュート シェーダーで見える物を選ぶ

カリングが読む定数と GPU に束縛するバッファの宣言です。

```hlsl
cbuffer CullCB : register(b0) {
  float4 g_planes[6];         // 視錐台の 6 面。内側が dot(xyz, p) + w >= 0(法線は正規化済み)
  float3 g_camera_pos;        // カメラのワールド位置
  float  g_max_distance;      // これより遠い物は描かない(メートル)
  uint   g_instance_count;    // インスタンスの総数
  uint   g_mesh_count;        // メッシュの種類数
  uint2  g_pad;
};

StructuredBuffer<Instance>    g_instances    : register(t0);   // 常駐している全インスタンス
StructuredBuffer<MeshInfo>    g_meshes       : register(t1);   // メッシュ表
RWStructuredBuffer<uint>      g_counts       : register(u0);   // メッシュごとの「見えた個数」(毎フレーム 0 で始める)
RWStructuredBuffer<uint>      g_visible      : register(u1);   // 見えたインスタンス番号を、メッシュごとの範囲に詰める
RWByteAddressBuffer           g_args         : register(u2);   // DrawIndexedInstancedIndirect の引数(メッシュ 1 個 = 20 バイト)
```

`g_planes` は視錐台の 6 平面です。それぞれ `(法線.xyz, d)` で内側が `dot(法線, p) + d >= 0` になる向きに正規化して渡します。法線が正規化されていないと次の半径との比較（`< -r`）で距離の単位が狂うので、球の判定が大きくずれます。`g_camera_pos` と `g_max_distance` は距離カリング用です。`g_instance_count` と `g_mesh_count` はスレッドの範囲チェックに使います。

バッファの束縛は 5 つです。読み取りが `g_instances`（`t0`）と `g_meshes`（`t1`）で、書き込みが `g_counts`（`u0`）、`g_visible`（`u1`）、`g_args`（`u2`）です。`g_args` は `RWByteAddressBuffer` で後で見るように描画引数の 5 つの `uint` をバイト位置で書きます。

次がカリング本体です。

```hlsl
[numthreads(64, 1, 1)]
void CullCS(uint3 id : SV_DispatchThreadID) {
  if (id.x >= g_instance_count) return;                        // ディスパッチは 64 の倍数に切り上げるので、余りのスレッドを捨てる
  Instance inst = g_instances[id.x];
  float3 c = inst.sphere.xyz;
  float r = inst.sphere.w;

  [unroll] for (int i = 0; i < 6; ++i) {                       // 6 枚の面すべてについて
    if (dot(g_planes[i].xyz, c) + g_planes[i].w < -r) return;  // 球が面の外側に完全に出ていたら、見えない
  }
  if (distance(c, g_camera_pos) - r > g_max_distance) return;  // 遠すぎる物は描かない(球の手前の縁で判定)

  uint slot;
  InterlockedAdd(g_counts[inst.mesh_id], 1, slot);             // このメッシュの何番目に見えたか。slot には加算前の値が返る
  g_visible[g_meshes[inst.mesh_id].out_offset + slot] = id.x;  // メッシュの範囲の slot 番目に、インスタンス番号を書く
}
```

`numthreads(64, 1, 1)` は 1 グループに 64 スレッドを並べるという意味です。64 は多くの GPU で 1 回に動く単位（ウェーブ）の倍数なので、無駄が出にくい値です。`id.x` が物体の番号になり 10 万個なら 1,563 グループ（切り上げ）を起動します。切り上げた分のスレッドは範囲外の番号を持つので、最初の行で捨てます。この `return` を忘れるとバッファの外を読んで、結果が壊れます。

視錐台の判定は 6 平面をループで調べます。`dot(g_planes[i].xyz, c) + g_planes[i].w` は球の中心から平面までの符号つき距離です。正なら内側、負なら外側です。これが `-r` より小さいと球全体が平面の外側にあるので、見えないと判定します。半径ぶん内側にはみ出している球は残すので、判定は保守的です。画面の角の外側で平面ごとに近いだけの球は、見えないのに通過する場合があります。この誤差はカリングを軽くするための代償で、見える物が消えるよりは安全な側です。

距離の判定は `distance(c, g_camera_pos) - r > g_max_distance` です。球の中心ではなく手前の縁（中心から半径を引いた位置）で比べるので、遠くに半分はみ出す大きな物が、急に消えません。

生き残った物は自分のメッシュの何番目かを決めます。`InterlockedAdd(g_counts[inst.mesh_id], 1, slot)` は `g_counts` の値を 1 増やして、増やす前の値を `slot` に返します。多数のスレッドが同時に呼んでも各スレッドが別々の番号を受け取れます。最後に `g_visible[offset + slot] = id.x` と書いて見えた物の番号を自分のメッシュの範囲の `slot` 番目に置きます。同じメッシュの物が並ぶ順序は実行のたびに変わりますが、描画の結果には影響しません。

6 平面ぶんの判定は 1 物体に 6 回の内積です。10 万個で 60 万回の内積になりますが、GPU には小さな仕事です。カリング パスが読むデータは 9.60 MB で、書くのは見えた物の 26 KB ほどと 64 個のカウンターです。60 fps なら読み出しは 576 MB/s になり近年の GPU の帯域に比べて十分小さい量です。

## 6. 描画引数を GPU が書く

インダイレクト描画は描画の引数を CPU から渡さず GPU バッファから読みます。メッシュごとに 20 バイト（`uint` 5 つ）で、これを別のコンピュート シェーダーが書きます。カリングが全部終わってからでないと個数が確定しないので、カリングとは別のディスパッチです。

```hlsl
[numthreads(64, 1, 1)]
void BuildArgsCS(uint3 id : SV_DispatchThreadID) {
  if (id.x >= g_mesh_count) return;
  MeshInfo m = g_meshes[id.x];
  uint base = id.x * 20;                                       // 引数 5 個 × 4 バイト = 20 バイト
  g_args.Store(base + 0, m.index_count);                       // IndexCountPerInstance
  g_args.Store(base + 4, g_counts[id.x]);                      // InstanceCount: カリング後に見えた個数(0 なら何も描かれない)
  g_args.Store(base + 8, m.start_index);                       // StartIndexLocation
  g_args.Store(base + 12, asuint(m.base_vertex));              // BaseVertexLocation(符号付きなのでビットをそのまま書く)
  g_args.Store(base + 16, 0);                                  // StartInstanceLocation: 0。範囲の先頭は定数バッファで渡す
}
```

1 スレッドが 1 メッシュを担当します。`base` はこのメッシュの引数の書き込み位置で、5 つの `uint` で 20 バイトなので `id.x * 20` です。書く 5 つの値は `DrawIndexedInstancedIndirect` が読む順序と同じにします。

- `IndexCountPerInstance` はメッシュのインデックス数です。
- `InstanceCount` はカリングで見えた個数です。`g_counts[id.x]` を読むので 0 のメッシュは何も描きません。CPU はこの数を知らないままです。
- `StartIndexLocation` と `BaseVertexLocation` は巨大なバッファの中のメッシュの位置です。後者は符号付きなので `asuint` でビットをそのまま書いています。
- `StartInstanceLocation` は 0 にします。メッシュの範囲の先頭は次の節の定数バッファで頂点シェーダーに渡します。

この 20 バイトの並びを間違えると、描かれる個数や位置が壊れます。デバッグではこのバッファを読み戻して、5 つの値を順に見てください。

## 7. 頂点シェーダーが visible を読む

描画では頂点シェーダーが物体を探します。

```hlsl
cbuffer PerMeshCB : register(b1) {
  row_major float4x4 g_view_projection;   // ワールド → クリップ
  uint g_range_offset;                     // このメッシュの範囲の先頭。CPU が描画の直前に MeshInfo.out_offset を書く
  uint3 g_pad2;
};
StructuredBuffer<uint> g_visible_srv : register(t2);          // CullCS が書いた g_visible を、読み取りで見る

struct VSIn { float3 position : POSITION; float3 normal : NORMAL; };
struct VSOut { float4 position : SV_Position; float3 normal : TEXCOORD0; };

VSOut DrawVS(VSIn v, uint instance_id : SV_InstanceID) {
  // SV_InstanceID は 0 から数える(引数の StartInstanceLocation を含むかは、この例では当てにしない)。
  uint inst_index = g_visible_srv[g_range_offset + instance_id];   // 見えたインスタンスの、本当の番号
  Instance inst = g_instances[inst_index];                          // 常駐データから行列を引く
  float4 world = mul(float4(v.position, 1.0), inst.world);          // モデル → ワールド
  VSOut o;
  o.position = mul(world, g_view_projection);                       // ワールド → クリップ
  o.normal = mul(v.normal, (float3x3)inst.world);                   // 法線は回転だけ(一様なスケールを想定)
  return o;
}

float4 DrawPS(VSOut i) : SV_Target {
  float n_dot_l = saturate(dot(normalize(i.normal), normalize(float3(0.3, 1.0, -0.4))));   // 仮の固定光源
  return float4(n_dot_l.xxx * 0.8 + 0.1, 1.0);
}
```

`PerMeshCB` にビュー射影行列と `g_range_offset` を入れます。`g_range_offset` はこれから描くメッシュの範囲の先頭（`MeshInfo` の `out_offset`）で、CPU が描画の直前に書き換えます。`SV_InstanceID` は 0 から数えるインスタンス番号で、`g_visible_srv[g_range_offset + instance_id]` を引くと見えた物のうち `instance_id` 番目の本当のインスタンス番号が得られます。それで `g_instances` から行列を取り出し、頂点をワールド、クリップの順に変換します。

ここで注意が 1 つあります。引数の `StartInstanceLocation` を 0 にして範囲の先頭は定数バッファで渡す設計にしたのは、`SV_InstanceID` が `StartInstanceLocation` を含むかどうかを今回確かめていないからです。含まないことを前提にして含んでも結果が変わらない設計にしました。

法線の変換は `(float3x3)inst.world` で回転だけを使います。拡大が一様でないスケールを許す場合は、逆転置行列が必要です。ピクセル シェーダーの `DrawPS` は仮の固定光源で明るさを出すだけの最小のものです。

## 8. D3D11 の C++ を組み立てる

ここまでが GPU 側です。CPU 側はバッファを作るコードと毎フレーム呼ぶ 3 段階のコードだけです。バッファの入れ物から見ます。

```cpp
struct GpuDrivenResources {
  ComPtr<ID3D11Buffer> instances;                     // 常駐インスタンス(構造化バッファ、96 バイト × N)
  ComPtr<ID3D11ShaderResourceView> instances_srv;
  ComPtr<ID3D11Buffer> meshes;                        // メッシュ表(構造化バッファ、16 バイト × M)
  ComPtr<ID3D11ShaderResourceView> meshes_srv;
  ComPtr<ID3D11Buffer> counts;                        // メッシュごとの見えた個数(4 バイト × M)
  ComPtr<ID3D11UnorderedAccessView> counts_uav;
  ComPtr<ID3D11Buffer> visible;                       // 見えたインスタンス番号(4 バイト × N)
  ComPtr<ID3D11UnorderedAccessView> visible_uav;
  ComPtr<ID3D11ShaderResourceView> visible_srv;       // 描画では読み取りで見る(UAV と SRV に同時に束縛しない)
  ComPtr<ID3D11Buffer> args;                          // 描画引数(20 バイト × M)
  ComPtr<ID3D11UnorderedAccessView> args_uav;
  UINT instance_count = 0;
  UINT mesh_count = 0;
};
```

`GpuDrivenResources` は GPU Driven に必要なバッファとそのビューを 1 つにまとめた入れ物です。`visible` だけはカリングでは UAV で書き描画では SRV で読むので、UAV と SRV の両方を持ちます。同じバッファを同時に UAV と SRV に束縛すると、どちらかが無効になるので使う段階で切り替えます。

```cpp
static HRESULT CreateStructured(ID3D11Device* dev, UINT stride, UINT count, UINT bind, const void* init, ID3D11Buffer** out) {
  D3D11_BUFFER_DESC d = {};
  d.ByteWidth = stride * count;                                   // 全体のバイト数
  d.Usage = D3D11_USAGE_DEFAULT;                                  // GPU が読み書きする。CPU からは UpdateSubresource で更新
  d.BindFlags = bind;                                             // SRV と UAV のどちらで使うか
  d.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;            // 構造化バッファ(StructuredBuffer / RWStructuredBuffer)
  d.StructureByteStride = stride;                                 // 1 要素のバイト数。HLSL の構造体の大きさと一致させる
  D3D11_SUBRESOURCE_DATA sd = {init, 0, 0};
  return dev->CreateBuffer(&d, init ? &sd : nullptr, out);
}
```

`CreateStructured` は構造化バッファを作る共通の関数です。`ByteWidth` は全体のバイト数で `StructureByteStride` は 1 要素のバイト数です。HLSL の構造体と一致させます。`MiscFlags` の `D3D11_RESOURCE_MISC_BUFFER_STRUCTURED` が構造化バッファの印です。

```cpp
bool CreateGpuDrivenResources(ID3D11Device* dev, const void* instances, UINT n, const void* meshes, UINT m, GpuDrivenResources* r) {
  r->instance_count = n;
  r->mesh_count = m;
  if (FAILED(CreateStructured(dev, 96, n, D3D11_BIND_SHADER_RESOURCE, instances, &r->instances))) return false;
  if (FAILED(dev->CreateShaderResourceView(r->instances.Get(), nullptr, &r->instances_srv))) return false;
  if (FAILED(CreateStructured(dev, 16, m, D3D11_BIND_SHADER_RESOURCE, meshes, &r->meshes))) return false;
  if (FAILED(dev->CreateShaderResourceView(r->meshes.Get(), nullptr, &r->meshes_srv))) return false;
  if (FAILED(CreateStructured(dev, 4, m, D3D11_BIND_UNORDERED_ACCESS, nullptr, &r->counts))) return false;
  if (FAILED(dev->CreateUnorderedAccessView(r->counts.Get(), nullptr, &r->counts_uav))) return false;
  if (FAILED(CreateStructured(dev, 4, n, D3D11_BIND_UNORDERED_ACCESS | D3D11_BIND_SHADER_RESOURCE, nullptr, &r->visible))) return false;
  if (FAILED(dev->CreateUnorderedAccessView(r->visible.Get(), nullptr, &r->visible_uav))) return false;
  if (FAILED(dev->CreateShaderResourceView(r->visible.Get(), nullptr, &r->visible_srv))) return false;

  // 描画引数のバッファ: バイト アドレスで書き、かつ「インダイレクト引数」として使えるようにする。
  D3D11_BUFFER_DESC a = {};
  a.ByteWidth = 20 * m;                                            // DrawIndexedInstancedIndirect の引数は 5 つの uint = 20 バイト
  a.Usage = D3D11_USAGE_DEFAULT;
  a.BindFlags = D3D11_BIND_UNORDERED_ACCESS;
  a.MiscFlags = D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS | D3D11_RESOURCE_MISC_BUFFER_ALLOW_RAW_VIEWS;   // 引数用 + RWByteAddressBuffer 用
  if (FAILED(dev->CreateBuffer(&a, nullptr, &r->args))) return false;
  D3D11_UNORDERED_ACCESS_VIEW_DESC u = {};
  u.Format = DXGI_FORMAT_R32_TYPELESS;                             // バイト アドレスのビューはこの形式
  u.ViewDimension = D3D11_UAV_DIMENSION_BUFFER;
  u.Buffer.NumElements = 5 * m;                                    // 4 バイトの要素が 5 × M 個
  u.Buffer.Flags = D3D11_BUFFER_UAV_FLAG_RAW;
  return SUCCEEDED(dev->CreateUnorderedAccessView(r->args.Get(), &u, &r->args_uav));
}
```

起動時に呼ぶ関数です。`instances` は 96 バイト × N、`meshes` は 16 バイト × M の読み取り専用で、初期データを渡します。`counts` と `visible` は GPU が書くので初期データはありません。最後の `args` が特別で `D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS` を付けると、インダイレクト描画の引数として使えるようになります。同時にコンピュート シェーダーから書くために `BUFFER_ALLOW_RAW_VIEWS` を付けて、`RWByteAddressBuffer` として見えるように UAV を作ります。UAV の `Format` が `DXGI_FORMAT_R32_TYPELESS` で `Flags` が `RAW` なのは、バイト アドレスのビューの決まりです。

毎フレームの処理は 3 段階です。1 つずつ見ます。

```cpp
  // ① カウンターを 0 にする。前フレームの個数が残っていると、見えた個数が積み上がってしまう。
  const UINT zero[4] = {0, 0, 0, 0};
  ctx->ClearUnorderedAccessViewUint(r.counts_uav.Get(), zero);
```

最初にカウンターを 0 に戻します。これを忘れると前のフレームの個数に今のフレームの個数が足されて、`visible` が自分の範囲を飛び出します。構造化バッファの UAV に対する `ClearUnorderedAccessViewUint` の挙動は、今回は実機で確かめていません。確実に 0 にしたいときはゼロ初期化したバッファを `CopyResource` で `counts` に書く方法もあります。

```cpp
  // ② カリング。1 スレッド = 1 インスタンスなので、N を 64 で割って切り上げた数のグループを起動する。
  ID3D11ShaderResourceView* srvs[2] = {r.instances_srv.Get(), r.meshes_srv.Get()};
  ID3D11UnorderedAccessView* uavs[3] = {r.counts_uav.Get(), r.visible_uav.Get(), r.args_uav.Get()};
  ctx->CSSetShader(cull_cs, nullptr, 0);
  ctx->CSSetConstantBuffers(0, 1, &cull_cb);
  ctx->CSSetShaderResources(0, 2, srvs);
  ctx->CSSetUnorderedAccessViews(0, 3, uavs, nullptr);             // u0 = counts、u1 = visible、u2 = args
  ctx->Dispatch((r.instance_count + 63) / 64, 1, 1);
```

カリングを実行します。`CSSetShader` でカリング用のシェーダーを選び定数バッファ、読み取りの 2 つ書き込みの 3 つ（`u0` が `counts`、`u1` が `visible`、`u2` が `args`）を束縛します。`Dispatch` のグループ数は `(物体数 + 63) / 64` で切り上げです。10 万個なら 1,563 グループです。

```cpp
  // ③ 描画引数。カリングが全部終わってから(同じコンテキストの Dispatch は順に実行されるので、そのまま続けてよい)。
  ctx->CSSetShader(args_cs, nullptr, 0);
  ctx->Dispatch((r.mesh_count + 63) / 64, 1, 1);
```

同じコンテキストの `Dispatch` は順番に実行されるので、カリングが終わってから描画引数のシェーダーが動きます。ここでは `args_cs` に切り替えてメッシュの数ぶんのグループを起動しています。64 メッシュなら 1 グループです。

```cpp
  // ④ 描画の前に、コンピュートの束縛を外す。UAV のまま args や visible を読もうとすると、読み取り側が無効になる。
  ID3D11UnorderedAccessView* null_uav[3] = {nullptr, nullptr, nullptr};
  ctx->CSSetUnorderedAccessViews(0, 3, null_uav, nullptr);
  ID3D11ShaderResourceView* null_srv[2] = {nullptr, nullptr};
  ctx->CSSetShaderResources(0, 2, null_srv);

  ID3D11ShaderResourceView* vs_srvs[3] = {r.instances_srv.Get(), r.meshes_srv.Get(), r.visible_srv.Get()};
  ctx->VSSetShaderResources(0, 3, vs_srvs);                         // t0 = instances、t1 = meshes、t2 = visible
```

描画の前にコンピュートの束縛を外します。`args` と `visible` が UAV として束縛されたままだと描画で読み取りとして使えません。そのうえで、頂点シェーダーに 3 つの読み取りビューを渡します。

```cpp
  // メッシュごとに 1 回。CPU が知っているのは「メッシュの数」だけで、何個描かれるかは args の中身が決める。
  for (UINT m = 0; m < r.mesh_count; ++m) {
    set_mesh_offset(mesh_range_offsets[m]);                         // b1 の g_range_offset を書く(CPU の仕事は、これだけ)
    ctx->DrawIndexedInstancedIndirect(r.args.Get(), 20 * m);         // メッシュ m の引数は、先頭から 20 × m バイト
  }
```

最後に、メッシュごとに 1 回ずつ描きます。CPU はメッシュの数を知っているだけで、何個描かれるかは `args` の中身が決めます。1 回ごとに `set_mesh_offset` で `g_range_offset` を書き `DrawIndexedInstancedIndirect(args, 20 * m)` を呼びます。2 つ目の引数は `args` の中のメッシュ `m` の引数の位置（バイト オフセット）です。CPU 側のコストは 64 回の呼び出しと 64 回の定数更新で、見えた個数が何個になっても変わりません。

## 9. 何が改善するのか

数字で整理します。いずれも 10 万個、6,528 個が可視、メッシュ 64 種類の場合です。

- CPU の命令数は 6,528 回から 64 回に減りました。5 マイクロ秒の仮定では 32.6 ミリ秒が 0.32 ミリ秒です。
- 物体ごとの定数の転送がなくなりました。25 MB/s の転送が動いた物の更新ぶんに置き換わります。
- 同期待ちがなくなりました。可視判定の結果を CPU が読む必要がないからです。
- 判定を細かくできます。物体より小さい単位（サブメッシュや Meshlet）で判定できます（[Mesh Shader and Meshlet](mesh-shaders.md)）。
- 草や瓦礫のように数十万個の同じ物を大量に置けます。

## 10. 2 パス オクルージョン カリング

[Culling](culling.md) のオクルージョン カリングは、前のフレームの深度バッファから作った Hi-Z（深度の階層）を使います。ところが、カメラが動くと前のフレームの深度は今のフレームと合いません。壁の向こうにあった物がカメラの動きで見えるようになっても、前のフレームの深度では隠れたままに判定されて、一瞬消えます。

2 パスはこれを避ける定番の方法です。

1. パス 1 では前のフレームで見えていた物をそのまま今のフレームで描きます。
2. 今のフレームの深度から Hi-Z を作ります。
3. パス 2 ではパス 1 で描かなかった物を新しい Hi-Z で判定して、見える物だけ追加で描きます。

前のフレームで見えていた物は今もほとんど見えています。だからパス 1 で画面の大半が描けて、パス 2 に回るのは「新しく見えるようになった物」だけです。新しく見える物の割合はカメラの動きで決まります。視錐台だけの判定で数えた結果が次の図です（オクルージョンは含みません）。

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="1 フレームで新しく見える物の割合">
<text x="20" y="22" class="fig-title">1 フレームで新しく見えるようになる物の割合（視錐台のみ、10 万個、水平回転）</text>
<line x1="90" y1="40" x2="90" y2="210" stroke="currentColor" stroke-width="1.5"/><line x1="90" y1="210" x2="760" y2="210" stroke="currentColor" stroke-width="1.5"/>
<text x="84" y="214" text-anchor="end" style="font-size:11px">0%</text><text x="84" y="127" text-anchor="end" style="font-size:11px">25%</text><text x="84" y="44" text-anchor="end" style="font-size:11px">50%</text>
<rect x="130" y="205" width="60" height="5" fill="rgba(76,139,245,0.6)"/><text x="160" y="198" text-anchor="middle" style="font-size:12px">1.3%</text><text x="160" y="228" text-anchor="middle" style="font-size:11px">0.5°</text><text x="160" y="244" text-anchor="middle" style="font-size:10px">30°/s</text>
<rect x="250" y="199" width="60" height="11" fill="rgba(76,139,245,0.6)"/><text x="280" y="192" text-anchor="middle" style="font-size:12px">2.5%</text><text x="280" y="228" text-anchor="middle" style="font-size:11px">1°</text><text x="280" y="244" text-anchor="middle" style="font-size:10px">60°/s</text>
<rect x="370" y="177" width="60" height="33" fill="rgba(76,139,245,0.6)"/><text x="400" y="170" text-anchor="middle" style="font-size:12px">7.9%</text><text x="400" y="228" text-anchor="middle" style="font-size:11px">3°</text><text x="400" y="244" text-anchor="middle" style="font-size:10px">180°/s</text>
<rect x="490" y="148" width="60" height="62" fill="rgba(229,170,40,0.7)"/><text x="520" y="141" text-anchor="middle" style="font-size:12px">14.4%</text><text x="520" y="228" text-anchor="middle" style="font-size:11px">6°</text><text x="520" y="244" text-anchor="middle" style="font-size:10px">360°/s</text>
<rect x="610" y="48" width="60" height="162" fill="rgba(229,72,77,0.65)"/><text x="640" y="41" text-anchor="middle" style="font-size:12px">47.1%</text><text x="640" y="228" text-anchor="middle" style="font-size:11px">30°</text><text x="640" y="244" text-anchor="middle" style="font-size:10px">1800°/s</text>
<text x="20" y="264" style="font-size:12px">1 フレームの回転量（60 fps に直した毎秒の角速度）。前進は 10 m 進んでも 4.0%（600 m/s）と、回転よりずっと小さい。</text>
</svg>

通常のカメラ操作（1 フレームに 1 度以内、毎秒 60 度まで）なら新しく見える物は 3% 以下です。パス 2 に回る物が少ないので、ほとんどの物はパス 1 の 1 回で描けます。毎秒 360 度の素早い回転で 14.4% で、ほぼ瞬間的な 30 度の切り替えでは 47.1% になります。シーンのカット切り替えのようにほぼ全部が新しく見えるときは、パス 2 の負担が増えます。前進は 10 m 進んでも 4.0% で、回転より影響が小さくなります。この数字は一様に散らばった 10 万個の物と 60 度の画角、500 m の遠景という条件での値で、実際のシーンの配置で変わります。

## 11. 設計の課題

GPU Driven の難しさは仕組みよりも周辺の設計にあります。

- 材質とシェーダーです。1 回の描画に複数の材質が混ざるので、テクスチャを番号で引くバインドレスの設計が必要になります（[GPU Driven (D3D12)](gpu-driven-dx12/index.md)）。D3D11 ではこの最小例のようにメッシュ（と材質）の種類ごとに描画を分けるのが現実的です。
- 半透明です。ソートが必要で順番を GPU 上で整える処理が要ります。多くのゲームは不透明だけを GPU Driven にして、半透明は別のパスにします。
- 動くメッシュです。スキニングされたメッシュは頂点がフレームごとに変わるので、スキニングの結果を先にバッファへ書きます。
- デバッグです。GPU の中で完結するので RenderDoc や PIX でバッファの中身を読み戻して確認します。`counts` と `args` を見るのが最初の手がかりです。
- API の制約です。D3D11 には複数の描画を 1 回の命令にまとめるマルチ ドローがありません。D3D12 と Vulkan が本命です。
- アセットの準備です。メッシュを巨大な 1 つのバッファに連結したり Meshlet 化したりするビルド時の処理が増えます（[ベイク](../../optimize/baking.md)）。

## 12. 段階的に取り入れる

最初から全部を作る必要はありません。

1. 同じメッシュの多数のインスタンスをコンピュート シェーダーでカリングして、`DrawIndexedInstancedIndirect` で描きます。
2. 複数のメッシュに広げます。このページのコードはここまでです。
3. Hi-Z オクルージョンを足します。2 パスの形にします。
4. D3D12 / Vulkan に移して、マルチ ドローとバインドレスで、シーン全体を少ない描画で描きます。
5. 判定の単位を Meshlet にします（[Mesh Shader and Meshlet](mesh-shaders.md)）。

## 13. よくあるミス

??? failure "CPU がボトルネックでないのに導入する"
    GPU が遅いシーンに GPU Driven を入れても、速くなりません。物体が数百個なら CPU Driven のままで十分です。まず [Bottlenecks](../optimization/bottlenecks.md) で CPU と GPU のどちらが遅いかを切り分けます。

??? failure "カウンターを毎フレーム 0 に戻さない"
    `counts` に前のフレームの個数が残ると、見えた個数が積み上がり `visible` の範囲を飛び出して隣のメッシュの物を壊します。カリングの前に必ず 0 にします。

??? failure "引数の並びや大きさが違う"
    `IndexCountPerInstance`、`InstanceCount`、`StartIndexLocation`、`BaseVertexLocation`、`StartInstanceLocation` の順に 4 バイトずつ書きます。1 つずれると描かれる個数や位置が壊れます。`args` を読み戻して確かめます。

??? failure "C++ と HLSL の構造体の大きさがずれる"
    `Instance` は 96 バイトです。パディングを忘れると 2 つ目以降の物体が壊れたデータを読みます。`static_assert(sizeof(Instance) == 96)` を C++ 側に置くと安全です。

??? failure "UAV のまま描画で読もうとする"
    `args` や `visible` が UAV として束縛されたままだと読み取りが無効になり、何も描かれません。描画の前にコンピュートの束縛を外します。

??? failure "急なカメラの動きで物が消える"
    前のフレームの Hi-Z だけで判定すると、急な動きで新しく見えた物が消えます。2 パスにします。

??? failure "D3D11 でマルチ ドローを期待する"
    D3D11 には複数の描画を 1 回にまとめる命令がありません。メッシュごとの `DrawIndexedInstancedIndirect` にします。

## 確かめたこと

- C++ の数字（可視数 6,528、穴 93,472、配置の検証、新しく見える割合）は 10 万個の乱数のシーンを C++23 で再現して数えた値です。再現に使ったのは視錐台の 6 平面と球の判定だけで、GPU では動かしていません。
- 本文の HLSL は `fxc` で `CullCS` と `BuildArgsCS` を `cs_5_0`、`DrawVS` を `vs_5_0`、`DrawPS` を `ps_5_0` としてコンパイルし、エラーなしで通りました。
- D3D11 の C++ は `g++ -fsyntax-only` で構文だけ確かめました。実機では動かしていません。
- 動かして確かめていないこと：①`SV_InstanceID` が `StartInstanceLocation` を含むか ②構造化バッファの UAV に対する `ClearUnorderedAccessViewUint` の挙動 ③`DRAWINDIRECT_ARGS` と `ALLOW_RAW_VIEWS` と `UNORDERED_ACCESS` の組み合わせが、使うドライバで通ること。
- ドロー コール 1 回の CPU 時間（2、5、10 マイクロ秒）は仮定した値で、計測した値ではありません。

## 参考資料

このページの内容は D3D11 の API の知識と上で述べた再現コードを根拠にしています。次の資料は今回は読んでいません。

- Microsoft の Direct3D 11 の公式ドキュメント（`DrawIndexedInstancedIndirect`、`D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS`、`ClearUnorderedAccessViewUint`）。
- GPU Driven Rendering Pipelines の発表や、2 パス オクルージョン カリングを扱った資料。

細部の仕様はこれらの公式の文書で確かめてください。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU Driven ＝ <strong>カリングと描画命令の作成を GPU にやらせる</strong>。CPU の負担が物体数に依存しない
    - [x] 流れは「データ常駐 → CullCS が選ぶ → BuildArgsCS が引数を書く → インダイレクト描画」
    - [x] 出力範囲はメッシュごとの総数ぶんを先に割り当てる（前置和）。穴ができる代わりにあふれない
    - [x] D3D11 は `DrawIndexedInstancedIndirect` をメッシュごとに呼ぶ。マルチ ドローは D3D12 / Vulkan
    - [x] 2 パス オクルージョンで、前フレームの Hi-Z の遅れを解決する
    - [x] CPU がボトルネックのときに段階的に導入する

## 関連ページ

- [描画の最適化（詳細）](../optimization/index.md)
- [Draw Calls and Batching](draw-calls.md)
- [Culling](culling.md)
- [Mesh Shader and Meshlet](mesh-shaders.md)
- [Hi-Z and Screen-Space Tracing](../optimization/hiz.md)
- [GPU Driven (D3D12)](gpu-driven-dx12/index.md)
