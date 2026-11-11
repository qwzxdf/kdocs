---
title: Sorting
tags:
  - 描画
---

# Sorting

通常のアルファ ブレンドは描く順番で結果が変わります。赤いガラスと青いガラスを重ねて、順番を間違えると手前と奥が入れ替わって見えます。深度の書き込みをしないので後から描いた物が、常に手前に重なるからです。

<strong>半透明は奥から手前へ（画家のアルゴリズム）の順に描きます</strong>。そのために、カメラからの距離で並べ替えます。このページではソートの基本、距離とビュー空間の深度の違い（実測つき）、ソートが破綻する場面、パーティクルの GPU ソート（動く HLSL）、ソートに頼らない方法を説明します。

!!! tip "ポイント"
    - 物体の中心のビュー空間の深度（前方向への射影）で、遠い順に並べるのが基本です。
    - 物体同士が入り組むとソートでは直りません（OIT が必要です）。
    - パーティクルはシステムごとまたは GPU でソートします。加算ブレンドならソートは要りません。
    - 距離が同じ物は ID などで順序を固定して、ちらつきを防ぎます。
    - 描画順は不透明、半透明（奥から手前）です。

!!! info "このページを読む前に"
    - [Alpha Blending and Sorting](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

## なぜソートが必要か {#why}

```text
赤いガラス（手前）と、青いガラス（奥）を通して、背景を見るとき:
  正しい順序:  背景 → 青（奥）→ 赤（手前）   → 赤が手前に見える
  逆の順序:    背景 → 赤（手前）→ 青（奥）   → 青が手前に見える（間違い）
```

[Blend State](blend-state.md) で見たとおり赤と青を α = 0.5 で黒に重ねると、順序で `(0.25, 0, 0.5)` と `(0.5, 0, 0.25)` に分かれます。加算や乗算なら順序に依存しないので、ソートは要りません。

<!-- fig:alpha-sort-order:begin -->

<svg class="fig illust motion" data-fig="alpha-sort-order" viewBox="0 0 780 390" role="img"><rect x="0" y="0" width="780" height="390" rx="14" fill="#ffffff"/>
<defs><marker id="arr-alpha-sort-order" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<mask id="as-mask-1-1" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
</mask>
<mask id="as-mask-1-2" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
<rect x="486" y="134" width="130" height="130" fill="#000000"/>
</mask>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">半透明は奥から手前の順に描く。順番を間違えると、透けなくなる</text>
<text x="40" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">正しい順:奥 → 中 → 手前</text>
<rect x="40" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="290" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="60" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><rect x="106" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><rect x="152" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">間違った順:手前 → 中 → 奥（深度を書く）</text>
<rect x="420" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="670" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="532" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-1)"><rect x="486" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-2)"><rect x="440" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
</g>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">左:重なりに赤・緑・青が全部透けて見える。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">右:手前が先に深度を書くので、奥の物が消えて透けない。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:alpha-sort-order:end -->

## ソートの基本 {#basic}

カメラからの距離の遠い順に並べて、描きます。

```cpp
#include <algorithm>
#include <cstdint>
#include <vector>

struct Vec3 { float x, y, z; };
static Vec3 operator-(Vec3 a, Vec3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
static float Dot(Vec3 a, Vec3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }

struct TransparentObject {
  Vec3 center;          // 代表点（中心）
  uint32_t id;          // 距離が同じときの安定なタイブレーク用
  float sort_key;       // カメラの前方向に沿った距離（ビュー空間の z）
};

// 毎フレーム: 前方向への射影をキーにして、遠い順に並べる。距離が同じなら id で決める
void SortBackToFront(std::vector<TransparentObject>& objects, Vec3 camera_position, Vec3 camera_forward) {
  for (TransparentObject& o : objects) o.sort_key = Dot(o.center - camera_position, camera_forward);
  std::sort(objects.begin(), objects.end(), [](const TransparentObject& a, const TransparentObject& b) {
    if (a.sort_key != b.sort_key) return a.sort_key > b.sort_key;   // 遠い物が先
    return a.id < b.id;                                              // フレームごとに順序が揺れない
  });
}
```

MSVC（`/W4`）でコンパイルして確かめました。キーの違いを測ります。60° の画角（16:9）に奥行き 2〜40 m で 3000 個の板（画面に平行）を、ランダムに置いて「カメラからの距離」で並べた順と「前方向の深度」で並べた順を比べました。画面に平行な板では前方向の深度の順が、見た目の前後に一致します。全ペアの約 6.2 % で順序が食い違いました。ただし、画面上で重なる近いペア（画面座標の差が 0.02 未満）だけを見ると、2995 ペアのうち食い違いは 0.3 % でした。

つまり、距離でも見た目に重なる物の順序はほぼ合います。ただし、前方向の深度のほうがカメラが回転しても順序が安定します。距離は球状に広がる物（爆発、パーティクルの群れ）に向いて、前方向の深度は平面的な板（ビルボード、ガラス板）に向きます。距離の比較だけなら平方根は不要で、2 乗のままで比べられます。

## ソートが破綻する場面 {#limits}

### 物体の内部でソートできない

1 つのメッシュ（ガラスの瓶、水槽）は三角形がばらばらの距離にあります。中心の距離だけでソートすると、1 つのメッシュの中の三角形の順序は、インデックスの順で決まって手前と奥が逆に重なることがあります。

凸な物（瓶、球）は 2 パスで描くと正しくなります。1 回目は前面をカリングして、奥の面（背面）だけを描きます。2 回目は背面をカリングして、手前の面（前面）だけを描きます。

```cpp
// （コンパイルしていない）凸な半透明の物: 裏面 → 表面の順で 2 回描く
context->RSSetState(rs_cull_front.Get());     // 表面をカリング（裏面だけ）
Draw(mesh);
context->RSSetState(rs_cull_back.Get());      // 裏面をカリング（表面だけ）
Draw(mesh);
```

そのほかに深度の事前描画で手前の面だけを深度に書いて、最前面の 1 層だけを描く方法やメッシュの三角形をソートする方法（重い）があります。

### 物体同士が交差している

2 つの大きな物体が互いに貫通していると、どちらが手前か場所によって違います。物体単位のソートが成立しません。分割するか OIT を使います。

### 大きな物体と小さな物体

大きな板（地面に広がる水面）と小さなパーティクルを中心の距離で並べると、小さな物が大きな物の手前にあるのに、先に描かれることがあります。大きな物は別のパスで先に描きます（水は、不透明の後、半透明の前、など）。

### 同じ距離

距離がほぼ同じ物はフレームごとに順序が入れ替わると、ちらつきます。上のコードのように ID を加えて、安定なタイブレークにします。

## パーティクルのソート {#particles}

パーティクルは数千〜数万個あって、毎フレーム CPU でソートすると重いです。

- システム単位でソートします。パーティクル システム（炎、煙）を 1 つの物体として並べて、システムの中は生成順のまま描きます。
- システムの中もソートします。煙のように重なりが多く見た目が重要なものだけです。
- GPU でソートします。計算シェーダーでビトニック ソートなどを使います。
- 加算ブレンド（火花、光）は順序に依存しないのでソートしません。

### GPU でのビトニック ソート

ビトニック ソートはデータ数が 2 の累乗で、並列に実行しやすいソートです。比較の組を決まった形の網で並べるので、分岐が少なく GPU に向いています。`N = 2ᵏ` 個を並べるパスの数は `k (k + 1) / 2` です。1024 個なら 55、16384 個なら 105、65536 個なら 136 です。Python で実装して 1024 個の乱数が正しく整列することとパス数が 55 であることを確かめました。

次の計算シェーダーは 512 個を 1 グループで並べる部分です。グループ共有メモリにキー（距離。遠い順にするため符号を反転）とパーティクルの番号を入れて、ビトニック ソートします。

```hlsl
StructuredBuffer<float4> g_particle_pos : register(t0);   // xyz = ワールド位置
RWStructuredBuffer<uint> g_sorted_index : register(u0);   // 並べた後のパーティクル番号（遠い順）

cbuffer SortConstants : register(b0) {
  float3 g_camera_position;
  uint g_count;               // パーティクルの数（512 の倍数に切り上げて、余りは遠い値で埋める）
  float3 g_camera_forward;
  float _pad;
};

static const uint kGroup = 512;                           // 1 グループで並べる個数
groupshared float2 s_data[kGroup];                        // x = キー（小さいほど先）、y = 番号

float2 LoadKey(uint i) {
  if (i >= g_count) return float2(1e30, (float)i);        // 余りは末尾へ
  float3 d = g_particle_pos[i].xyz - g_camera_position;
  float view_z = dot(d, g_camera_forward);                // 前方向の深度
  return float2(-view_z, (float)i);                       // 遠い順にしたいので、符号を反転して昇順に並べる
}

[numthreads(256, 1, 1)]
void BitonicSortLocalCS(uint3 gid : SV_GroupID, uint tid : SV_GroupThreadID) {
  uint base = gid.x * kGroup;
  s_data[tid] = LoadKey(base + tid);                      // 1 スレッドが 2 要素を担当
  s_data[tid + 256] = LoadKey(base + tid + 256);
  GroupMemoryBarrierWithGroupSync();

  for (uint k = 2; k <= kGroup; k <<= 1) {                // 並べる列の長さを倍々にする
    for (uint j = k >> 1; j > 0; j >>= 1) {               // 比較する要素の間隔を半分ずつ
      uint i = 2 * tid - (tid & (j - 1));                 // 各スレッドが担当する比較の、下側の要素
      uint l = i + j;                                      // 比較相手
      bool ascending = ((i & k) == 0);                     // 列ごとに、昇順と降順を交互にする
      float2 a = s_data[i];
      float2 b = s_data[l];
      if ((a.x > b.x) == ascending) { s_data[i] = b; s_data[l] = a; }   // 順序が逆なら入れ替える
      GroupMemoryBarrierWithGroupSync();
    }
  }
  g_sorted_index[base + tid] = (uint)s_data[tid].y;
  g_sorted_index[base + tid + 256] = (uint)s_data[tid + 256].y;
}
```

1 グループの 512 個は整列します。それより多いときはグループ間のマージ（残りのビトニックの段階）を別のパスで続けます。この部分はこのページでは書いていません。実用ではライブラリ（`FidelityFX Parallel Sort` など）を使う方法もあります。

!!! note "確かめた範囲"
    C++ は MSVC（`/W4`）でコンパイルして確かめました（実行はしていません）。HLSL は `fxc`（`cs_5_0`）で `BitonicSortLocalCS` をコンパイルして、エラーが出ないことを確かめました。ビトニック ソートの正しさは Python の実装（同じ網の構造）で確かめたもので、HLSL を GPU で実行した結果ではありません。距離と深度の違いの数字は Python のシミュレーションです。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="要素数ごとの、ビトニック ソートのパス数"><text x="14" y="22" class="fig-title">ビトニック ソートのパス数（k(k+1)/2、N = 2^k）</text>
<line x1="60" y1="190" x2="690" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"><rect x="110" y="141" width="80" height="49"/><rect x="240" y="95" width="80" height="95"/><rect x="370" y="68" width="80" height="122"/><rect x="500" y="40" width="80" height="150"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="150" y="135">55</text><text x="280" y="89">105</text><text x="410" y="62">136</text><text x="540" y="34">210</text>
<text x="150" y="210">1024（k=10）</text><text x="280" y="210">16384（k=14）</text><text x="410" y="210">65536（k=16）</text><text x="540" y="210">約 100 万（k=20）</text></g>
<text x="360" y="232" text-anchor="middle" style="font-size:12px">要素が 1000 倍になっても、パス数は 4 倍にならない（網の段数は対数の 2 乗で増える）</text></svg>

## ソートに頼らない方法 {#alternatives}

- 加算や乗算のブレンドは順序に依存しないので、ソートが要りません。
- OIT（順序に依存しない透明）は、ソートなしで近似または正確な結果を得ます（[OIT](../oit/index.md)）。
- アルファ テスト系は深度に書き込んで、ソートが不要です（[Alpha Testing](../alpha-test/index.md)）。

## ブレンドとソートのまとめ {#summary-table}

- ガラスと水面は通常のブレンドで、ソートが必要です。
- 炎、爆発、魔法は加算で不要です。
- 煙は通常（または乗算済み）で、必要です。
- 影の板（ブロブ）は乗算で、不要です。
- UI は通常で描画順をレイヤーで決めます。

## よくあるミス {#mistakes}

??? failure "入り組んだ半透明が前後逆に見える"
    原因は物体単位のソートでは貫通や自己重なりの順序を決められないことです。ソートの粒度を細かくするか OIT を使います。

??? failure "カメラを動かすと半透明の順序が、ちらちら入れ替わる"
    原因は距離がほぼ同じ物の順序が、フレームごとに変わることです。ID などで安定なタイブレークを加えます。

??? failure "大きな水面の上の小さなパーティクルが、水面に隠れる"
    原因は中心の距離だけで並べて、大きな物が後から描かれることです。水面は不透明の後、半透明の前に別のパスで描きます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 不透明の後に半透明を奥から手前へ描きます。
    - [x] キーは前方向の深度（ビュー空間の z）が安定です。ID でタイブレークします。
    - [x] 入り組むなら OIT です。
    - [x] パーティクルは GPU のビトニック ソート（1024 個で 55 パス）などを使います。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は自分で書いた Python のシミュレーションです。

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）
- Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Carpenter, "The A-buffer, an Antialiased Hidden Surface Method", SIGGRAPH 1984
- Batcher, "Sorting Networks and their Applications", AFIPS Spring Joint Computer Conference, 1968（ビトニック ソートの原典）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [OIT](../oit/index.md)
- [Blend State](blend-state.md)
