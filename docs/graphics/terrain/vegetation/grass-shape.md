---
title: Grass Shape
tags:
  - 描画
---

# Grass Shape

草原を描くには 1 平方メートルに数百本の草を生やす必要があります。1 本を 3 枚の三角形で作っても、100 万本なら 300 万三角形です。草は数が桁違いに多いので 1 本あたりの三角形の数がそのまま負荷を決めます。少ない頂点でそれらしく見せる工夫が要ります。

<strong>草は細長い板を少数の三角形で作るのが基本</strong>です。十字に交差させた板に絵を貼る古典的な方法から、1 本ずつ曲げた帯をシェーダーで組み立てる方法まであります。このページでは草の形の選び方、帯 1 本の頂点の決め方、描き方、見え方の工夫、色の付け方を説明します。

!!! tip "ポイント"
    - 遠くは十字板かビルボード、近くは 1 本ずつの帯にして、距離で切り替えます。
    - 帯は根元から先端へ段に分けて、幅を細く位置を前へ曲げます。曲がりは `t²` のような曲線にすると、草らしくなります。
    - 頂点バッファを持たず `SV_VertexID` とインスタンスのパラメーターから頂点シェーダーで組み立てられます。
    - 帯は真横から見ると厚みが 0 になるので、視線に応じて幅を広げます。両面を描きます。
    - 根元の色を地面の色に合わせると、境目が消えます。根元が暗いと AO の代わりにもなります。

!!! info "このページを読む前に"
    - [Vegetation](index.md)（このセクション全体の地図と読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 草の形を選ぶ {#shapes}

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="草の 4 つの形。クロス板、房、1 本ずつの帯、ビルボード"><text x="14" y="22" class="fig-title">草の形と三角形の数（1 本あたり）</text>
<g fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"><rect x="30" y="60" width="26" height="90"/><rect x="43" y="60" width="26" height="90" transform="rotate(0)" opacity="0.5"/><path d="M200,150 L226,150 L214,66 Z"/><path d="M218,150 L244,150 L226,60 Z" opacity="0.6"/><path d="M236,150 L262,150 L244,70 Z" opacity="0.4"/><path d="M390,150 L408,150 L412,120 L400,70 L396,92 L392,120 Z" /><rect x="570" y="70" width="60" height="80"/></g>
<g fill="none" stroke="#94a3b8" stroke-width="1.5"><path d="M30,150 L69,150"/></g>
<text x="50" y="180" text-anchor="middle" style="font-size:13px;font-weight:600">クロス板</text><text x="50" y="200" text-anchor="middle" style="font-size:12px">4 枚（十字 2 枚）</text><text x="50" y="218" text-anchor="middle" style="font-size:12px">絵を貼る</text>
<text x="226" y="180" text-anchor="middle" style="font-size:13px;font-weight:600">房</text><text x="226" y="200" text-anchor="middle" style="font-size:12px">6〜10 枚</text><text x="226" y="218" text-anchor="middle" style="font-size:12px">3〜5 本を扇形に</text>
<text x="400" y="180" text-anchor="middle" style="font-size:13px;font-weight:600">1 本ずつの帯</text><text x="400" y="200" text-anchor="middle" style="font-size:12px">3〜14 枚</text><text x="400" y="218" text-anchor="middle" style="font-size:12px">1 本ごとに曲がる</text>
<text x="600" y="180" text-anchor="middle" style="font-size:13px;font-weight:600">ビルボード</text><text x="600" y="200" text-anchor="middle" style="font-size:12px">2 枚</text><text x="600" y="218" text-anchor="middle" style="font-size:12px">遠景用。動かない</text>
<text x="360" y="244" text-anchor="middle" style="font-size:12px">近づくほど右から左へ、本数を減らして形を細かくしていく</text></svg>

### クロス板

草の絵を貼った板を 2 枚、十字に交差させます。1 本ではなく草むらの 1 房を 1 つの板で表すので、三角形は 4 枚で済みます。横から見ると板だと分かるのが欠点で、風でも先端のあたりだけを揺らします。実装が簡単で古典的な方法です。

### 房

3〜5 本の葉の板を扇形に並べます。三角形は 6〜10 枚です。近景でもまずまず草に見えます。房全体が 1 つの単位で揺れます。

### 1 本ずつの帯

細長い三角形の帯を 3〜7 段で 1 本ずつ作ります。三角形は 3〜14 枚です。1 本ごとに曲げたり揺らしたりでき近くで見ても 1 本ずつ見えます。インスタンスごとに高さ曲がり色を変えると、自然になります。距離に応じて段の少ない帯に切り替えます。

### ビルボード

常にカメラを向く 2 枚の三角形です。遠景の草原の塊に使います。回転しても形が崩れませんが動きは付けられません。

## 帯 1 本のメッシュ {#blade}

帯は根元から先端へ向かう細い板です。n 段に分けて各段に左右の 2 頂点を置き先端に 1 頂点だけ置きます。頂点数は `2n + 1`、三角形は `2n − 1` です。

<svg class="fig flow" viewBox="0 0 720 300" role="img" aria-label="5 段の帯の頂点の並びと、横から見た曲がり"><defs><marker id="gsA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">帯の頂点（5 段）と、横から見た曲がり</text>
<path d="M120,260 L220,260 L212,212 L128,212 Z M128,212 L212,212 L204,164 L136,164 Z M136,164 L204,164 L196,116 L144,116 Z M144,116 L196,116 L188,68 L152,68 Z M152,68 L188,68 L170,40 Z" fill="rgba(76,139,245,0.18)" stroke="#4c8bf5" stroke-width="2"/>
<g style="font-size:11px"><text x="108" y="264" text-anchor="end">0</text><text x="228" y="264">1</text><text x="116" y="216" text-anchor="end">2</text><text x="220" y="216">3</text><text x="124" y="168" text-anchor="end">4</text><text x="212" y="168">5</text><text x="132" y="120" text-anchor="end">6</text><text x="204" y="120">7</text><text x="140" y="72" text-anchor="end">8</text><text x="196" y="72">9</text><text x="170" y="34" text-anchor="middle">10（先端）</text></g>
<text x="170" y="286" text-anchor="middle" style="font-size:12px">vertex_id: 段 = id / 2、左右 = id &amp; 1</text>
<path d="M420,260 C430,170 470,110 560,60" fill="none" stroke="#e5aa28" stroke-width="4"/><line x1="420" y1="260" x2="420" y2="50" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="400" y1="260" x2="640" y2="260" stroke="currentColor" stroke-width="1.5"/>
<line x1="420" y1="260" x2="560" y2="60" stroke="#94a3b8" stroke-dasharray="2 4"/>
<text x="428" y="290" style="font-size:12px">根元（動かない）</text><text x="565" y="56" style="font-size:12px;font-weight:600">先端ほど前へ倒れる</text><text x="440" y="150" style="font-size:12px">オフセット ∝ t²</text></svg>

段数は距離で変えます。段が増えるほど曲がりがなめらかになります。

- 1 段: 頂点 3、三角形 1。遠景で三角形 1 枚の葉になります。
- 3 段: 頂点 7、三角形 5。中景です。
- 5 段: 頂点 11、三角形 9。近景です。
- 7 段: 頂点 15、三角形 13。最近景で曲がりがなめらかです。

遠景では三角形 1 枚でも画面上で細い線にしか見えません。距離に応じて段数が違うインスタンスの描画へ切り替えます。

## 頂点シェーダーで組み立てる {#procedural}

帯の頂点は頂点バッファに持たず頂点シェーダーが計算できます。`SV_VertexID` から段と左右を取り出して、インスタンスごとのパラメーター（位置、向き高さ曲がり）から位置を決めます。頂点バッファもインデックス バッファも不要で、頂点数の違う LOD も `DrawInstanced` の頂点数を変えるだけで描き分けられます。

まず、定数とインスタンスのデータです。

```hlsl
static const uint kSegments = 5;                 // 段数。vertices_per_blade = 2 * kSegments + 1

struct Blade {
  float3 base;        // 根元のワールド位置
  float yaw;          // 帯の向き（ラジアン）。地面の上の回転
  float height;       // 高さ（メートル）
  float width;        // 根元の幅（メートル）。例: 0.05
  float bend;         // 曲がり 0..1。先端が前へ倒れる割合
  float random01;     // 0..1 の乱数。色のばらつき用（決定的に作る）
};

StructuredBuffer<Blade> g_blades : register(t0);

cbuffer FrameConstants : register(b0) {
  float4x4 g_view_proj;
  float3 g_camera_pos;
  float g_thicken;           // 真横から見たときの幅の増やし方。例: 0.04
};

struct VsOut {
  float4 pos : SV_Position;
  float3 normal : NORMAL;
  float t : TEXCOORD0;       // 根元 0、先端 1
  float random01 : TEXCOORD1;
  float3 world_pos : TEXCOORD2;
};
```

次に、帯の頂点の位置です。

```hlsl
VsOut BladeVS(uint vertex_id : SV_VertexID, uint instance_id : SV_InstanceID) {
  Blade b = g_blades[instance_id];

  // 頂点番号から、段 (level) と、左右 (side) を取り出す。最後の 1 つが先端
  bool is_tip = (vertex_id == 2 * kSegments);
  uint level = is_tip ? kSegments : vertex_id / 2;
  float side = is_tip ? 0.0 : ((vertex_id & 1) ? 1.0 : -1.0);
  float t = float(level) / kSegments;

  // 幅は、根元で太く、先端で 0。1 - t² だと、先端近くで急に細くなる
  float w = b.width * (1.0 - t * t);

  // 曲がり: 先端ほど前へ倒れる（t² に比例）。根元は動かない
  float forward = b.bend * t * t * b.height * 0.6;
  // 倒れた分だけ、高さを縮める（帯の長さをおおよそ保つ）
  float up = b.height * (t - 0.5 * b.bend * b.bend * t * t * t);

  // 帯の局所座標。x = 幅方向、y = 上、z = 前
  float3 local_pos = float3(side * w * 0.5, up, forward);

  // 向き（yaw）で、地面の上を回す
  float s, c;
  sincos(b.yaw, s, c);
  float3 right = float3(c, 0, -s);                 // 帯の幅方向
  float3 fwd = float3(s, 0, c);                    // 帯が倒れる前方
  float3 world_pos = b.base + right * local_pos.x + float3(0, 1, 0) * local_pos.y + fwd * local_pos.z;

  // 法線: 帯の面の向き。曲がるほど上を向く
  float3 normal = normalize(cross(right, float3(0, 1, 0) * 1.0 + fwd * (2.0 * b.bend * t * 0.6)));

  // 真横から見ても消えないように、視線に応じて幅を少し広げる
  float3 view_dir = normalize(g_camera_pos - world_pos);
  float side_on = 1.0 - abs(dot(view_dir, normal));     // 真横ほど 1
  world_pos += right * side * side_on * g_thicken * (1.0 - t);

  VsOut o;
  o.pos = mul(float4(world_pos, 1.0), g_view_proj);
  o.normal = normal;
  o.t = t;
  o.random01 = b.random01;
  o.world_pos = world_pos;
  return o;
}
```

`level` は頂点番号を 2 で割った段で、`side` は偶数が左、奇数が右です。先端の頂点は左右がなく `w` も 0 になって、1 点に収束します。

`forward` が曲がりの本体です。`t²` にすると根元（t = 0）では傾きが 0 で、先端へ向かって傾きが大きくなります。根元がまっすぐ立って先端だけがしなる草の形です。`t` に比例させる（直線）と全体が斜めに倒れるだけで、草に見えません。

`up` の補正は倒れた分だけ高さを縮めて、帯の長さが `height` からあまり変わらないようにしています。厳密な弧長の保存ではありません。足りなければベジェ曲線で制御点を置いて、曲線の上に頂点を並べる方法もあります。

`side_on` は視線と帯の法線のなす角から決まります。真横から見ると `dot` が 0 になって、`side_on` が 1 になり幅が `g_thicken` ぶん広がります。真正面では 0 で何もしません。全部をカメラに向けると不自然なので、広げる量を小さくとどめます。

C++ 側は頂点バッファなしで描きます。帯は左右の頂点を交互に並べるので、三角形ストリップで表せます。

```cpp
// 頂点バッファなしで描く（コンパイルしていない）。頂点数は 2 * 段数 + 1。
context->IASetInputLayout(nullptr);
context->IASetVertexBuffers(0, 0, nullptr, nullptr, nullptr);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLESTRIP);
const UINT vertices_per_blade = 2 * kSegments + 1;
context->DrawInstanced(vertices_per_blade, instance_count, 0, 0);
```

ストリップは「左、右、左、右、…、先端」の順に並べると `2n − 1` 枚の三角形になります。

## 色と陰影 {#color}

草の見た目の半分は色のばらつきと根元の暗さで決まります。

```hlsl
Texture2D<float4> g_terrain_albedo : register(t1);     // 地形のカラー マップ
SamplerState g_linear_clamp : register(s0);

cbuffer ColorConstants : register(b1) {
  float2 g_terrain_origin;      // 地形の左下（ワールド xz）
  float g_terrain_size;         // 地形の 1 辺（メートル）
  float _pad;
  float3 g_light_dir;           // 光の来る向き（正規化済み）
};

float4 BladePS(VsOut i, bool is_front : SV_IsFrontFace) : SV_Target {
  // 根元の位置の地形の色を拾って、少し暗くする（地面との馴染み、AO の代わり）
  float2 terrain_uv = (i.world_pos.xz - g_terrain_origin) / g_terrain_size;
  float3 root_color = g_terrain_albedo.SampleLevel(g_linear_clamp, terrain_uv, 0).rgb * 0.5;

  // 先端は明るい緑。根元から先端へ、高さ t で補間する
  float3 tip_color = lerp(root_color, float3(0.55, 0.75, 0.25), 0.8);
  float3 albedo = lerp(root_color, tip_color, i.t);
  // 1 本ずつのばらつき（明るさを ±10 % ずらす）
  albedo *= 0.9 + 0.2 * i.random01;

  // 両面を描くので、裏面では法線を反転する
  float3 n = is_front ? i.normal : -i.normal;
  float diffuse = saturate(dot(n, g_light_dir)) * 0.7 + 0.3;     // 0.3 は環境光の下駄
  return float4(albedo * diffuse, 1.0);
}
```

根元の色は立っている地形の色から取ります。草の根元と地面が同じ色になって、境目が見えなくなります。根元を暗く先端を明るくすると、草の密集の中の影を表せて AO を別に計算する必要が減ります。ばらつきはインスタンスの乱数から作ります。乱数をフレームごとに変えると、色がちらつきます。位置などから決定的に作ります。

帯の裏面を描くためにラスタライザーのカリングを切ります（`D3D11_CULL_NONE`）。裏面の法線はピクセル シェーダーで `SV_IsFrontFace` を使って反転します。

!!! note "確かめた範囲"
    HLSL は `fxc`（`vs_5_0` と `ps_5_0`）でコンパイルして、エラーが出ないことを確かめました。C++ はコンパイルしていません。GPU で描画した結果は確認していません。

## 近年の実装例 {#modern}

Wohllaib の GDC 2021 の発表（『Ghost of Tsushima』の草）は、1 本ずつの葉を GPU で曲線として扱い LOD ごとに頂点数を変えて数百万本を描く方法として知られています。このページでは発表を読んでいないので、内容の解説はしていません。このページの「頂点シェーダーで組み立てる」節は、同じ考え方（1 本ずつを曲線として扱い距離で段数を変える）を自分の式で書いたものです。

## よくあるミス {#mistakes}

??? failure "草が横から見ると板に見える"
    原因は板が 1 枚か向きが 1 方向にそろっていることです。クロス板は複数枚を交差させます。帯はインスタンスごとに向き（`yaw`）をばらけさせて、幅を視線に応じて少し広げます。

??? failure "帯が真横から見ると消えるまたは点滅する"
    原因は帯が厚みのない板なので、視線と平行になると画面上の幅が 0 になることです。`side_on` で幅を広げます。遠くでは幅が 1 ピクセルを切るとエイリアシングで消えるので、画面上の最小幅を保つように `width` を大きくします。

??? failure "裏側が真っ黒、または見えない"
    原因は裏面がカリングされているか裏面の法線が逆向きのままで、ライティングが 0 になっていることです。カリングを無効にしてピクセル シェーダーで `is_front` を見て法線を反転します。

??? failure "全部の草が同じ色・同じ向きで、コピーしたように見える"
    原因はインスタンスのばらつき（向き高さ曲がり色）が 1 つもないことです。位置のハッシュなどから決定的な乱数を作って、4 つとも少しずつずらします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 草は数が多いので、1 本あたりの三角形の数を距離で減らします。
    - [x] 帯は `2n + 1` 頂点で、曲がりを `t²` にすると草らしくなります。
    - [x] 頂点バッファなしで、`SV_VertexID` とインスタンスから組み立てられます。
    - [x] 両面を描いて、真横から見たときの幅を広げます。
    - [x] 根元の色を地面に合わせて、暗くします。

## 参考 {#references}

このページは次の資料を読まずに書きました。式と HLSL は自分で書いたもので、`fxc` でのコンパイルまで確かめています。

- Pelzer, "Rendering Countless Blades of Waving Grass", GPU Gems, Chapter 7, 2004（草の板ポリ、風、クロス ブレンド）
- Wohllaib, "Procedural Grass in Ghost of Tsushima", Game Developers Conference 2021
- Boulanger, Pattanaik, Bouatouch, "Rendering Grass in Real Time with Dynamic Lighting", IEEE Computer Graphics and Applications, Vol. 29, No. 1, 2009
- Sousa, "Vegetation Procedural Animation and Shading in Crysis", GPU Gems 3, Chapter 16, 2007

## 関連ページ

- [Vegetation](index.md)
- [Wind](wind.md)
