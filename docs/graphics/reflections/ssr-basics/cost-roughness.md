---
title: Cost and Roughness
tags:
  - 描画
---

# Cost and Roughness

SSR は画素ごとにレイを進めるので、画面が大きいほど歩数が多いほど重くなります。反射がはっきり見える画素にだけ使えば十分なのに、全画素に同じ数のレイを飛ばすと予算の大半をほとんど見えない反射に使うことになります。もう 1 つの困りごとは粗さです。粗い面の反射はぼやけるべきですが、レイ 1 本で取れるのは鏡の反射だけです。このページではコストを「画素数 × 本数 × 歩数」で見積もり減らす工夫（半解像度、除外、タイル分類）を HLSL で書き粗さの簡易対応（結果をミップでぼかす）が、どこまで通用するかを数字で確かめます。

!!! tip "ポイント"
    - 深度の読み込みは最大で 画素数 × レイの本数 × 歩数 回。1920 × 1080、1 本、32 歩なら約 6,640 万回。半解像度なら 1/4 の約 1,660 万回になる。
    - 粗い面は反射がぼやけるが、ローブの幅は粗さの 2 乗（α = 粗さ²）で急に広がる。粗さ 0.3 で半角約 10°、0.5 で約 28°、1.0 で 90°。
    - 結果のミップによるぼかしは、レイが長いほど粗いほど高いミップを引く。ただし上限があり粗さ 0.5 で長さ 20 m なら画面の大きさを超える。
    - 見えない反射はトレースしない。この例では粗さ 0.7 超の除外だけで、画素の約 48 % を省けた。
    - 本格的な粗さは確率的に複数のレイを飛ばす[Stochastic SSR](../ssr-stochastic.md)で扱う。

!!! info "このページを読む前に"
    - [SSR Basics](index.md)（このセクション全体の地図と読む順番）

## 読んだ資料 {#sources}

- Stachowiak, Uludag, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）、Uludag の "Hi-Z Screen-Space Cone-Traced Reflections"（GPU Pro 5）、Walter らの "Microfacet Models for Refraction through Rough Surfaces"（2007）、Heitz の "Sampling the GGX Distribution of Visible Normals"（2018）は、このページの執筆では読んでいません。
- GGX の反射ローブの幅は GGX の分布関数 D(h) から、このページで導出しました（次の節）。数値は C++ で導出した式の通りに出しています。
- 材質の分布、除外のしきい値（0.7、0.01）、深度の重み（40）は説明のために決めた値で、特定のエンジンの値ではありません。
- 旧版にあった「レイマーチ 0.5〜2 ms」などの時間は、出典がないため削除しました。このページは時間ではなく読み込みの回数で見積もります。

HLSL は `fxc`（`ps_5_0` と `cs_5_0`）でコンパイルして確かめました。C++ は MSVC で実行しました。

## コストの見積もり {#cost}

SSR の時間のほとんどはレイマーチの深度の読み込みです。1 歩が深度テクスチャの 1 回の読み込みなので、最大の回数は次の式で出ます。

`読み込み回数 = 画素数 × レイの本数 × 歩数`

1920 × 1080 は 2,073,600 画素です。1 本、32 歩なら最大 6,636 万回、半解像度（518,400 画素）なら 1,659 万回で、ちょうど 4 分の 1 です。粗い面のぼけをレイ 4 本で取るならフル解像度で 2.65 億回、半解像度で 6,636 万回になります。**半解像度で 4 本飛ばしても、フル解像度で 1 本飛ばすのと同じ回数です。**

実際の時間は、GPU、キャッシュ、Hi-Z（[Hi-Z SSR](../ssr-hiz.md)）で何歩に減るかで変わるため、このページでは時間を書きません。比べたいときは自分の環境で画素数・本数・歩数を変えて、時間を測ります。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="最大の深度読み込み回数(百万回/フレーム、1920×1080、最大 32 歩)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">最大の深度読み込み回数(百万回/フレーム、1920×1080、最大 32 歩)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">150</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">300</text><rect x="104.5" y="156.8" width="43.0" height="33.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="126.0" y="152.8" text-anchor="middle" font-size="10" fill="currentColor">66.4</text><text x="127.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">フル 1本</text><rect x="239.5" y="181.7" width="43.0" height="8.3" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="261.0" y="177.7" text-anchor="middle" font-size="10" fill="currentColor">16.6</text><text x="262.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">半 1本</text><rect x="374.5" y="57.3" width="43.0" height="132.7" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="396.0" y="53.30000000000001" text-anchor="middle" font-size="10" fill="currentColor">265.4</text><text x="397.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">フル 4本</text><rect x="509.5" y="156.8" width="43.0" height="33.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="531.0" y="152.8" text-anchor="middle" font-size="10" fill="currentColor">66.4</text><text x="532.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">半 4本</text></svg>

## 画素を減らす {#reduce}

### 見えない反射を除外する {#skip}

反射がほとんど見えない画素はトレースしません。粗さが大きい面と反射率の低い面です。

```hlsl
```hlsl
// ================= ② 画素を除外する =================

// 反射がほぼ見えない画素。非金属の F0 は約 0.04、金属は 1 に近い。
bool ShouldSkipSsr(float roughness, float metallic) {
  float f0_scale = lerp(0.04, 1.0, metallic);
  float visible = f0_scale * (1.0 - roughness);          // 反射の見えやすさの目安（足した式）
  return roughness > g_skip_roughness || visible < 0.01;
}
```
```

`f0_scale` は垂直に見たときの反射率 F0 の目安です。非金属は約 0.04（4 %）、金属は 1 に近い値です。`visible` は F0 に `(1 - roughness)` を掛けた見えやすさの目安で、このページが決めた式です。しきい値 0.01 は反射が 1 % を下回ると、見えにくいという意味の一例です。

非金属（金属度 0）では `0.04 × (1 - r) < 0.01` を `r` について解くと `r > 0.75` です。つまり、非金属では 2 番目の条件は粗さのしきい値 0.7 とほぼ同じで、あまり効きません。**2 番目の条件が効くのは、中間の金属度の面だけ**です。

材質の分布の一例で割合を数えました。画素の 60 % が粗さ 0.3〜1 の非金属、10 % が粗さ 0.1〜0.7 の金属、30 % が粗さ 0.6〜1 の非金属とすると、粗さ > 0.7 だけで 48.2 %、`visible` だけで 40.2 %、どちらかなら 48.2 % を除外できました。実際のシーンの割合は材質の分布で大きく変わるので、自分のシーンで数えてください。

### タイルで分類する {#tile}

画素ごとに分岐しても同じ warp（wave）の中に除外する画素としない画素が混ざると結局、全員が待たされます。そこで、8 × 8 のタイルで分類して、要るタイルだけをあとからトレースします。

```hlsl
```hlsl
// ================= ③ タイル分類 =================

RWStructuredBuffer<uint> g_tile_list : register(u0);   // SSR が要るタイルの番号
RWByteAddressBuffer g_tile_count : register(u1);       // 要るタイルの数（間接ディスパッチの引数に使う）
groupshared uint s_need;

[numthreads(8, 8, 1)]
void ClassifyTilesCS(uint3 gid : SV_GroupID, uint3 dtid : SV_DispatchThreadID, uint gindex : SV_GroupIndex) {
  if (gindex == 0) s_need = 0;
  GroupMemoryBarrierWithGroupSync();
  float2 mat = g_gbuffer_mat.Load(int3(dtid.xy, 0));
  if (!ShouldSkipSsr(mat.x, mat.y)) InterlockedOr(s_need, 1);   // 1 画素でも要るなら、タイル全体を要るとする
  GroupMemoryBarrierWithGroupSync();
  if (gindex == 0 && s_need != 0) {
    uint slot;
    g_tile_count.InterlockedAdd(0, 1, slot);              // 要るタイルを 1 つ追加
    g_tile_list[slot] = (gid.y << 16) | gid.x;            // タイルの座標を詰める
  }
}
```
```

`s_need` はタイル内で共有する旗です。1 画素でも SSR が要るなら 1 にします（`InterlockedOr`）。`GroupMemoryBarrierWithGroupSync()` を旗を立てる前後に置いて、立て終わってから読みます。これを省くと旗を立てる前に読んで、要るタイルを落とします。

最後に、代表のスレッドが要るタイルの座標を `g_tile_list` に詰め個数を `g_tile_count` に足します。`g_tile_count` は間接ディスパッチの引数に使えます。トレースのパスは要るタイルだけを `DispatchIndirect` で起動します。除外された画素の多いシーンほど効果が大きくなります。

### 半解像度でトレースする {#half}

トレースを半分の解像度（画素数 1/4）で行い結果をフル解像度に戻します。ただ拡大すると物の境界で隣の物の当たりを拾います。深度で重みづけして混ぜます（バイラテラル）。

```hlsl
```hlsl
// ================= ④ 半解像度 → フル解像度 =================

// フル解像度の画素 p に対して、半解像度の 4 画素を深度の近さで重みづけして混ぜる。
// 混ぜるのは「当たった UV（rg）とレイの長さ（b）」。色ではなく当たりの情報を混ぜ色はこのあとフル解像度で引く。
float4 UpsampleHit(uint2 p) {
  float center_depth = g_depth_full.Load(int3(p, 0));
  float2 hp = (float2(p) + 0.5) * 0.5 - 0.5;             // 半解像度の座標系での位置（画素の中心を合わせる）
  int2 base = (int2)floor(hp);                           // 左上の半解像度画素
  float2 f = hp - base;                                  // 4 画素の中での位置（0〜1）
  float3 sum = 0;
  float hit_sum = 0, wsum = 0;
  [unroll] for (int i = 0; i < 4; ++i) {
    int2 o = int2(i & 1, i >> 1);
    int2 q = max(base + o, 0);                           // 画面の端は 0 に丸める
    float d = g_depth_half.Load(int3(q, 0));
    float wb = lerp(1.0 - f.x, f.x, (float)o.x) * lerp(1.0 - f.y, f.y, (float)o.y);   // 双線形の重み
    float wd = 1.0 / (1.0 + 40.0 * abs(d - center_depth) / max(center_depth, 0.1));   // 深度の差が大きいほど小さく（40 は足した値）
    float4 h = g_hit_half.Load(int3(q, 0));
    float w = wb * wd * h.a;                             // 外れた画素は寄与しない
    sum += h.rgb * w;
    hit_sum += h.a * wb * wd;                            // 「当たった割合」用（外れも分母に入れる）
    wsum += w;
  }
  float all_w = 0;                                       // 外れを含む重みの合計（当たり率の分母）
  [unroll] for (int j = 0; j < 4; ++j) {
    int2 o = int2(j & 1, j >> 1);
    int2 q = max(base + o, 0);
    float d = g_depth_half.Load(int3(q, 0));
    all_w += lerp(1.0 - f.x, f.x, (float)o.x) * lerp(1.0 - f.y, f.y, (float)o.y)
           / (1.0 + 40.0 * abs(d - center_depth) / max(center_depth, 0.1));
  }
  float hit_rate = hit_sum / max(all_w, 1e-4);           // 0〜1。外れが多いほど小さい
  return wsum > 1e-4 ? float4(sum / wsum, hit_rate) : float4(0, 0, 0, 0);
}
```
```

混ぜるのは色ではなく「当たった UV とレイの長さ」です。色はフル解像度の画素の位置で引き直すので、境界で色が滲みません。`hp` はフル解像度の画素中心を半解像度の座標系に直した位置で `-0.5` は、画素の中心を合わせる補正です。これを忘れると結果が半画素ずれます。

重みは双線形の重み `wb` に深度の近さの重み `wd` を掛けます。`wd` はフル解像度の深度と半解像度の深度の差が大きいほど小さくなります（係数 40 は説明のための値）。外れた画素（`h.a` が 0）は `w` を 0 にして、UV の平均に混ぜません。ただし、「当たり率」の分母には入れます。外れが多い境界では当たり率が下がり後のプローブへの切り替えが効きます。

## 粗さに対応する {#roughness}

### 反射ローブの幅 {#lobe}

粗い面の反射がぼやけるのは反射方向が、法線の周りの微小な面（マイクロファセット）の向きによって、ばらつくからです。GGX の分布 `D(h)` ではハーフベクトル h の方向の累積確率 `u` と角度 θh の関係が、次の形になります。

`tan²θh = α² · u / (1 − u)`

`cos θh` で重みづけした D を立体角で積分して、解いた式です（このページでの導出）。α は粗さの 2 乗です（`α = roughness²`）。反射方向の角度はハーフベクトルの角度の 2 倍です。`u = 0.5`（光の半分がこの角の内側に入る）なら `tan θh = α` で、反射の半角は `2 atan(α)` になります。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="GGX の反射ローブの半角(度)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">GGX の反射ローブの半角(度)</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="171.5" text-anchor="end" font-size="10" fill="currentColor">45</text><text x="54" y="129.0" text-anchor="end" font-size="10" fill="currentColor">90</text><text x="54" y="86.5" text-anchor="end" font-size="10" fill="currentColor">135</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">180</text><text x="60.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="168.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0.2</text><text x="276.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0.4</text><text x="384.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0.6</text><text x="492.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">0.8</text><text x="600.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">1</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">粗さ(知覚的)</text><polyline points="60.0,210.0 87.0,209.7 114.0,208.9 141.0,207.6 168.0,205.7 195.0,203.2 222.0,200.3 249.0,196.8 276.0,192.8 303.0,188.4 330.0,183.5 357.0,178.2 384.0,172.6 411.0,166.7 438.0,160.7 465.0,154.5 492.0,148.4 519.0,142.3 546.0,136.3 573.0,130.5 600.0,125.0" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">50 % が入る角</text><polyline points="60.0,210.0 87.0,209.2 114.0,206.8 141.0,202.7 168.0,197.1 195.0,189.9 222.0,181.5 249.0,171.9 276.0,161.6 303.0,150.9 330.0,140.4 357.0,130.2 384.0,120.8 411.0,112.3 438.0,104.6 465.0,97.9 492.0,92.0 519.0,86.8 546.0,82.3 573.0,78.3 600.0,74.8" fill="none" stroke="#4c8bf5" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">90 % が入る角</text><polyline points="60.0,210.0 87.0,207.3 114.0,199.3 141.0,186.2 168.0,169.0 195.0,149.8 222.0,131.0 249.0,114.4 276.0,100.7 303.0,89.9 330.0,81.4 357.0,74.7 384.0,69.5 411.0,65.3 438.0,61.9 465.0,59.1 492.0,56.9 519.0,55.0 546.0,53.4 573.0,52.0 600.0,50.8" fill="none" stroke="#e5aa28" stroke-width="2.4"/><line x1="470" y1="80" x2="496" y2="80" stroke="#e5aa28" stroke-width="2.4"/><text x="502" y="84" text-anchor="start" font-size="11" fill="currentColor">99 % が入る角</text></svg>

C++ で出した値を読みます。粗さ 0.1 の半角は 1.15°（50 %）、粗さ 0.3 で 10.29°、0.5 で 28.07°、0.7 で 52.21°、1.0 で 90° です。**粗さの 2 乗で効くので、粗さ 0.3 まではほぼ鏡で、0.5 を超えると急に広がります。** 90 % が入る角で見ると、粗さ 0.3 で 30.2°、0.5 で 73.7° とさらに広くなります。裾が長い分布なので 99 % の角は粗さ 0.3 で 83.7° まで広がります。

ミップで近似するときは 50 % の半角を使います。90 % を使うとぼかしが広すぎて、ミップの上限に張りつきます。

### 結果をミップでぼかす {#mip}

レイは 1 本だけ飛ばして当たった画素の色を粗さに応じたミップで読みます。反射する物が遠いほどぼけが大きくなる現実の見え方もレイの長さに応じて円錐を太くすれば、近似できます。

```hlsl
```hlsl
// ================= ① 粗さ → ミップ =================

// GGX の反射ローブの「半分の光が入る半角」（中央値）。ハーフベクトルの角 θh は tan θh = α·sqrt(u/(1-u))（u = 累積確率）。
// u = 0.5 なら tan θh = α、反射方向の角は 2θh。α = 粗さ²（知覚的な粗さから）。90% を使うと広すぎてミップが上限に張りつく（[2] 参照）。
float RoughnessToHalfAngle(float roughness) {
  float alpha = roughness * roughness;
  return 2.0 * atan(alpha);                               // ラジアン。粗さ 0 で 0、1 で π/2
}

// 反射円錐の太さ（当たった位置での幅 [m]）→ ミップ。
float ConeToMip(float ray_length, float roughness, float hit_depth) {
  float half_angle = RoughnessToHalfAngle(roughness);
  float footprint = 2.0 * ray_length * tan(min(half_angle, 1.5));            // 円錐の直径 [m]（tan の発散を避けて 1.5 rad で打ち切る。足した処理）
  float pixel_world = 2.0 * hit_depth * g_tan_half_fov_y / g_full_size.y;    // 当たった深度での 1 画素の幅 [m]
  float footprint_px = footprint / max(pixel_world, 1e-5);                   // 円錐の太さ [画素]
  return clamp(log2(max(footprint_px, 1.0)), 0.0, g_max_mip);                // 1 画素以下ならミップ 0
}

float3 ResolveReflection(float2 hit_uv, float ray_length, float hit_depth, float roughness) {
  float mip = ConeToMip(ray_length, roughness, hit_depth);
  return g_lit_scene_mips.SampleLevel(g_linear_clamp, hit_uv, mip).rgb;     // 3 重線形補間でミップ間も滑らか
}
```
```

`RoughnessToHalfAngle` は上の `2 atan(α)` です。`ConeToMip` はレイの長さ `ray_length` で円錐の直径を求め（`2 × 長さ × tan 半角`）、当たった深度での 1 画素の幅で割って、画素数にし `log2` でミップに直します。`tan` は半角が π/2 に近づくと発散するので、1.5 rad で打ち切ります（足した処理）。

数字で見ます。1080p、垂直画角 60°、当たった深度 10 m では 1 画素の幅が 1.07 cm です。粗さ 0.3 でレイの長さが 5 m なら円錐の直径は 1.8 m（約 170 画素）で、ミップは 7.4 です。粗さ 0.5 で 20 m なら直径は 21 m（約 2000 画素）で、ミップは 10.96 です。1920 × 1080 のミップ列は、ミップ 10 で 2 × 1 画素になるためこれは、**画面全体を平均した色**とほぼ同じです。

ここからこの方法の限界が分かります。ミップは正方形の箱形のぼかしで、GGX の裾の長い分布を再現できません。画面外や遮蔽された部分の色はミップにも含まれません。粗さが 0.5 を超えるあたりから、ぼけの形が現実の反射と合わなくなります。だから、粗い面は SSR をやめてプローブに任せます。

### プローブへ切り替える {#probe}

粗さが一定を超えたら SSR をやめて、反射プローブの色に切り替えます。急に切り替えると粗さの境で縞が出るので、幅を持たせて混ぜます。

```hlsl
```hlsl
// ================= ⑤ プローブとの混ぜ =================

float3 BlendWithProbe(float3 ssr_color, float ssr_hit, float3 probe_color, float roughness) {
  float rough_fade = saturate((roughness - g_fade_start) / max(g_skip_roughness - g_fade_start, 1e-3));   // 0.5 → 0.7 で 0 → 1
  float use_probe = max(rough_fade, 1.0 - ssr_hit);      // 粗い、または当たらなかった画素はプローブ
  return lerp(ssr_color, probe_color, use_probe);
}

// ================= 画素シェーダー =================

float4 ResolvePS(float4 pos : SV_Position) : SV_Target {
  uint2 p = (uint2)pos.xy;
  float2 mat = g_gbuffer_mat.Load(int3(p, 0));
  float3 probe = g_probe_reflection.Load(int3(p, 0)).rgb;
  if (ShouldSkipSsr(mat.x, mat.y)) return float4(probe, 1.0);       // トレースしていない画素
  float4 h = UpsampleHit(p);                                         // rg = 当たった UV、b = レイの長さ a = 当たり率
  float hit_depth = g_depth_full.Load(int3(p, 0));
  float3 ssr = ResolveReflection(h.rg, h.b, hit_depth, mat.x);
  return float4(BlendWithProbe(ssr, h.a, probe, mat.x), 1.0);
}
```
```

`rough_fade` は粗さが `g_fade_start`（例: 0.5）から `g_skip_roughness`（例: 0.7）の間で、0 から 1 に上がる重みです。トレースが外れた画素（`ssr_hit` が 0 に近い）は、粗さに関係なくプローブを使います。`max` で両方の条件の大きいほうを取るので、どちらか一方でも満たせばプローブに寄ります。

## 数字を出した C++ {#experiment}

ここまでの数字は次の C++ で出しました。

```cpp
```cpp
// SSR のコストと粗さの数字を出す。① GGX 反射ローブの幅 ② 円錐 → ミップ ③ 画素数 x 本数 x 歩数 ④ 除外できる画素の割合
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <random>

constexpr double kPi = 3.14159265358979323846;

int main() {
  // ---- ① GGX の反射ローブ: ハーフベクトルの角 θh の累積確率 u → tan θh = α sqrt(u/(1-u))、反射方向の角は 2θh ----
  std::printf("[1] GGX reflection lobe half-angle (degrees), alpha = roughness^2\n");
  std::printf("rough  alpha   50%%     90%%     99%%\n");
  for (double r : {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0}) {
    double a = r * r;                                        // 知覚的な粗さ → α
    auto ang = [&](double u) { return 2 * std::atan(a * std::sqrt(u / (1 - u))) * 180 / kPi; };   // 反射方向の角 [度]
    std::printf("%.1f   %.4f  %6.2f  %6.2f  %6.2f\n", r, a, ang(0.5), ang(0.9), ang(0.99));
  }

  // ---- ② 反射円錐の太さ → ミップ（HLSL の ConeToMip と同じ式、50% の半角を使う）----
  std::printf("\n[2] mip level from the cone (1080p, vertical fov 60 deg, hit depth 10 m)\n");
  double pixel_world = 2 * 10.0 * std::tan(30 * kPi / 180) / 1080;   // 当たった深度 10 m での 1 画素の幅 [m]
  std::printf("pixel width at 10 m = %.5f m\n", pixel_world);
  std::printf("rough  ray_len  cone_width[m]  footprint[px]  mip\n");
  for (double r : {0.2, 0.3, 0.5}) {
    for (double len : {1.0, 5.0, 20.0}) {                    // レイの長さ [m]
      double half = 2 * std::atan(r * r);                    // 50% の半角 [rad]（HLSL の RoughnessToHalfAngle）
      double fp = 2 * len * std::tan(std::min(half, 1.5));   // 円錐の直径 [m]
      double px = fp / pixel_world;
      std::printf("%.1f   %5.1f    %8.3f       %8.1f       %.2f\n", r, len, fp, px, std::log2(std::max(px, 1.0)));
    }
  }

  // ---- ③ 画素数 x 本数 x 歩数 ----
  std::printf("\n[3] depth reads per frame at 1920x1080 (rays=1, steps=32 max)\n");
  double full = 1920.0 * 1080;
  std::printf("full res   : %.0f pixels -> %.1f M reads max\n", full, full * 32 / 1e6);
  std::printf("half res   : %.0f pixels -> %.1f M reads max (1/4)\n", full / 4, full / 4 * 32 / 1e6);
  std::printf("full, 4 rays (rough surfaces): %.1f M reads max\n", full * 4 * 32 / 1e6);
  std::printf("half, 4 rays                 : %.1f M reads max\n", full / 4 * 4 * 32 / 1e6);

  // ---- ④ 除外できる画素の割合（材質の分布は一例）----
  // 一例: 60% は非金属で粗さ 0.3〜1、10% は金属で粗さ 0.1〜0.7、30% は非金属で粗さ 0.6〜1
  std::mt19937 rng(7);
  std::uniform_real_distribution<double> u(0, 1);
  long skip_a = 0, skip_b = 0, skip_either = 0, n = 2000000;
  for (long i = 0; i < n; ++i) {
    double c = u(rng), r, m;
    if (c < 0.6) { r = 0.3 + 0.7 * u(rng); m = 0; }
    else if (c < 0.7) { r = 0.1 + 0.6 * u(rng); m = 1; }
    else { r = 0.6 + 0.4 * u(rng); m = 0; }
    bool a = r > 0.7;                                        // 粗さのしきい値
    bool b = (0.04 + 0.96 * m) * (1 - r) < 0.01;             // 見えやすさの目安
    skip_a += a; skip_b += b; skip_either += (a || b);
  }
  std::printf("\n[4] skipped pixels in an example material mix\n");
  std::printf("rough > 0.7 only            : %.1f %%\n", 100.0 * skip_a / n);
  std::printf("f0*(1-rough) < 0.01 only    : %.1f %%\n", 100.0 * skip_b / n);
  std::printf("either                      : %.1f %%\n", 100.0 * skip_either / n);
  std::printf("non-metal threshold of the 2nd rule: rough > %.3f\n", 1 - 0.01 / 0.04);
  return 0;
}
```
```

```text title="実行結果"
[1] GGX reflection lobe half-angle (degrees), alpha = roughness^2
rough  alpha   50%     90%     99%
0.1   0.0100    1.15    3.44   11.36
0.2   0.0400    4.58   13.69   43.40
0.3   0.0900   10.29   30.22   83.69
0.4   0.1600   18.18   51.28  115.73
0.5   0.2500   28.07   73.74  136.20
0.6   0.3600   39.60   94.41  148.80
0.7   0.4900   52.21  111.55  156.82
0.8   0.6400   65.24  124.98  162.15
1.0   1.0000   90.00  143.13  168.52
```

```text title="実行結果（続き）"
[2] mip level from the cone (1080p, vertical fov 60 deg, hit depth 10 m)
pixel width at 10 m = 0.01069 m
rough  ray_len  cone_width[m]  footprint[px]  mip
0.2     1.0       0.160           15.0       3.91
0.2     5.0       0.801           74.9       6.23
0.2    20.0       3.205          299.8       8.23
0.3     1.0       0.363           33.9       5.09
0.3     5.0       1.815          169.7       7.41
0.3    20.0       7.259          678.9       9.41
0.5     1.0       1.067           99.8       6.64
0.5     5.0       5.333          498.8       8.96
0.5    20.0      21.333         1995.3       10.96
```

```text title="実行結果（続き）"
[3] depth reads per frame at 1920x1080 (rays=1, steps=32 max)
```

## よくあるミス {#mistakes}

??? failure "粗い面にも鏡のようにくっきりした反射が出る"
    粗さに応じたぼかしがない。結果のミップを粗さとレイの長さから選ぶ。粗さ 0.5 以上はプローブへ切り替える。

??? failure "半解像度の境界で、反射が隣の物にはみ出す"
    戻すときに深度の重みを付けていない。双線形だけで混ぜると境界の外の当たりを拾う。深度が近い画素だけを混ぜる。

??? failure "タイル分類で、反射が要るタイルが落ちる"
    旗を立てる前に読んでいる。`GroupMemoryBarrierWithGroupSync()` を旗を立てる前後に置く。

??? failure "粗さの境目で、反射に縞が出る"
    SSR とプローブを粗さのしきい値で切り替えている。しきい値の前後に幅を持たせて、混ぜる。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 深度の読み込みは、最大で 画素数 × 本数 × 歩数。半解像度で 1/4 にできる。
    - [x] 粗い面と反射率の低い面は、トレースしない。タイルで分類すると warp の無駄が出ない。
    - [x] 反射ローブの半角は 2 atan(粗さ²)。粗さ 0.3 までは鏡に近く、0.5 を超えると急に広がる。
    - [x] ミップによるぼかしは、粗さ 0.5 あたりが限界。粗い面はプローブに任せる。

## 参考 {#references}

- Tomasz Stachowiak, Yasin Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games. 読んでいない。
- Yasin Uludag, "Hi-Z Screen-Space Cone-Traced Reflections", GPU Pro 5, CRC Press, 2014. 読んでいない。
- Bruce Walter, Stephen R. Marschner, Hongsong Li, Kenneth E. Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007. 読んでいない。GGX の分布関数 D(h) の式として参照した。
- Eric Heitz, "Sampling the GGX Distribution of Visible Normals", Journal of Computer Graphics Techniques 7(4), 2018. 読んでいない。
- 反射ローブの幅の式、除外のしきい値、半解像度の重みはこのページで決めたもの。数値は C++ の実験結果。

## 関連ページ {#related}

- [SSR Basics](index.md)
- [Stochastic SSR](../ssr-stochastic.md)
- [Hi-Z SSR](../ssr-hiz.md)
- [Color Lookup and Fading](color-fade.md)
