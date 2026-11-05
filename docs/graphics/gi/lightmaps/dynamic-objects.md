---
title: Specular and Dynamic Objects
tags:
  - 描画
---

# Specular and Dynamic Objects

焼いたライトマップの壁の前をキャラクターが歩く場面を考えます。壁は焼き込みの間接光で柔らかく照らされているのに、キャラクターにはライトマップがありません。直接光だけで照らすとキャラクターだけが背景から浮きます。そこで、動く物体には空間に置いた「プローブ」から間接光を渡します。また、ライトマップが持つのは拡散の間接光だけで、つるつるした面の映り込みは別の手段が要ります。このページでは Valve の Source Engine の Ambient Cube を中心に、動く物体の間接光の作り方とその表現の精度をコメント付きの HLSL と数字で説明します。

!!! tip "ポイント"
    - ライトマップは拡散の間接光だけを持つ。鏡面は反射プローブや SSR が担当する。
    - 動く物体には放射照度ボリュームの Ambient Cube（6 色）を、法線の二乗で重み付けして渡す。評価は 6〜11 命令ほどで足りる。
    - Ambient Cube は SH L1（4 係数）より保存量が多いが、評価は軽い。精度は環境しだいで SH L2（9 係数）には及ばない。
    - プローブの間隔は粗くてよい（Valve は 4 × 4 × 8 フィート）。ただし、最寄りの 1 点を使うと光が飛ぶので、補間するか時間で平均する。
    - 静的な背景と動く物の明るさが合うようにライトマップと同じベイクの結果からプローブを作る。

!!! info "このページを読む前に"
    - [Lightmaps](index.md)（このセクション全体の地図と読む順番）
    - [Probe GI](../probes/index.md)（ライト プローブの考え方）

## 読んだ資料 {#sources}

- Jason Mitchell, Gary McTaggart, Chris Green, "Shading in Valve's Source Engine", SIGGRAPH 2006 Advanced Real-Time Rendering in 3D Graphics and Games Course, 第 8 章。8.1〜8.5 の冒頭（モデルの照明まで）を読みました。8.5 の HDR とカラー補正、その後の節は読んでいません。
- Greger ほか "The Irradiance Volume"（1998）と、Iwanicki の "Lighting Technology of The Last of Us"（2013）は、読んでいません（後者は取得できませんでした）。

Valve の資料に書かれているのは、Ambient Cube の評価ルーチン、放射照度ボリュームの間隔と最寄りの 1 点の選択、時間平均、局所ライトの扱い Half Lambert です。トライリニア補間、局所ライトを Ambient Cube へ足す式、SH との精度比較はこのページで足したものです。

## ライトマップに無いもの {#missing}

### 鏡面 {#specular}

ライトマップが保存するのは拡散の間接光だけです。鏡面反射は視線に依存するので、1 つの値としてテクスチャに焼けません（[Diffuse and Specular](../theory/diffuse-specular.md)）。ライトマップだけにするとつるつるした面が周りを映さず違和感が出ます。

鏡面は反射プローブや SSR が担当します（[Reflection Probes](../../reflections/probes/index.md)）。Valve の Source も世界の鏡面にキューブ マップを使います。レベル デザイナーが手でサンプル点を置きそこからエンジン自身で HDR のキューブ マップをレンダリングして、レベルのデータとして持ちます。鏡面が要る面は最寄りの点のキューブ マップを使うか手で 1 つ割り当てます。

### 動く物体 {#dynamic}

ライトマップはメッシュの表面（UV2）に焼き込むので、動く物体には使えません。動く物体は位置が変わるたびに受ける間接光が変わります。そこで、空間の点に間接光を保存したプローブから、周りの間接光を受け取ります。静的な背景はライトマップ、動く物はプローブ、というのが標準の組み合わせです。

## Valve の方式：Ambient Cube と放射照度ボリューム {#valve}

### Ambient Cube {#ambient-cube}

Valve はキャラクターを世界になじませるために方向のある環境光を使います。事前計算した放射照度のサンプルを空間に敷き詰めます（Greger の放射照度ボリューム）。サンプルは低解像度の「立方体の放射照度環境マップ」で、6 つの色（+x、−x、+y、−y、+z、−z）を持ちます。直接光の寄与は含まず間接光（バウンス光）だけなので、Ambient Cube と呼びます。

<svg class="fig flow" viewBox="0 0 720 232" role="img" aria-label="Ambient Cube の評価"><defs><marker id="do-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">Ambient Cube: 6 面の色を、法線の二乗で重み付けして足す</text><rect x="130" y="70" width="140" height="140" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><circle cx="270" cy="140" r="8" fill="#e5aa28"/><text x="284" y="144" text-anchor="start" font-size="11" fill="currentColor">+x</text><circle cx="130" cy="140" r="8" fill="#4c8bf5"/><text x="116" y="144" text-anchor="end" font-size="11" fill="currentColor">-x</text><circle cx="200" cy="70" r="8" fill="#4caf7a"/><text x="200" y="56" text-anchor="middle" font-size="11" fill="currentColor">+y</text><circle cx="200" cy="210" r="8" fill="#e05a4f"/><text x="200" y="234" text-anchor="middle" font-size="11" fill="currentColor">-y</text><line x1="200" y1="140" x2="254.0" y2="68.0" stroke="currentColor" stroke-width="2" marker-end="url(#do-a)"/><text x="262.0" y="68.0" text-anchor="start" font-size="11" fill="currentColor">n = (0.6, 0.8)</text><text x="400" y="80" text-anchor="start" font-size="12" fill="currentColor">重み: nx² = 0.36(+x の色)</text><text x="400" y="102" text-anchor="start" font-size="12" fill="currentColor">      ny² = 0.64(+y の色)</text><text x="400" y="130" text-anchor="start" font-size="12" fill="currentColor">色 = 0.36 × (+x) + 0.64 × (+y)</text><text x="400" y="162" text-anchor="start" font-size="11" fill="currentColor">nx² + ny² + nz² = 1 なので、重みの合計は 1</text><text x="400" y="184" text-anchor="start" font-size="11" fill="currentColor">(3 次元では、z も同様に ± の 2 色から選ぶ)</text></svg>

評価は法線の各成分の二乗で 6 色を重み付けして足すだけです。`nx² + ny² + nz² = 1` なので重みの合計は 1 になります。Valve のリストでは頂点シェーダーで 6 命令、画素シェーダーで 11 命令です。

```hlsl
// 動く物体の間接光: Valve の Ambient Cube（Source Engine、Half-Life 2）を中心にした、完成形。
//   ① Ambient Cube の評価（6 色を、法線の二乗で重み付け）
//   ② 放射照度ボリュームの読み方（Valve は最寄りの 1 点。ここでは、補間する版も書く）
//   ③ 局所ライトを Ambient Cube に足す、Half Lambert
//   ④ 時間方向の平滑（ボリュームの切り替わりで光が飛ぶのを抑える）
//   ⑤ 比較のための SH L2（9 係数）の評価
// 資料: Mitchell, McTaggart, Green, "Shading in Valve's Source Engine", SIGGRAPH 2006 Course 8 章。
// Valve が書いているのは、①の評価ルーチン、最寄りの 1 点を選ぶこと、時間平均、局所ライトを足すこと、Half Lambert。
// ②の補間、③の足し方の式、⑤は、このページが足したもの。

cbuffer DynObjCB : register(b0) {
  float3 g_volume_origin;        // 放射照度ボリュームの最小角 [m]
  float g_pad0;
  float3 g_volume_inv_size;      // 1 / ボリュームの大きさ [1/m]
  float g_pad1;
  float3 g_light_dir[2];         // 局所の主なライト 2 つの向き（物体へ向かう逆。ライトへ向かう単位ベクトル）
  float3 g_light_color[2];       // その色 × 強さ
  float g_ambient_boost;         // 主人公だけ、環境光を強める倍率（Valve のヒューリスティック。1 = そのまま）
  float g_smooth_blend;          // 時間平滑の、新しい値の重み（0.1 なら 10 % ずつ追う）
  float2 g_pad2;
};

// ボリュームは、6 つの面ごとに 1 枚の 3D テクスチャ（+x, -x, +y, -y, +z, -z の順）。R11G11B10 などで持つ。
Texture3D<float4> g_ambient_cube_volume[6] : register(t0);
SamplerState g_linear_clamp : register(s0);

// ================= ① Ambient Cube の評価 =================

// Valve のルーチンと同じ式。6 色 cube[0..5] = (+x, -x, +y, -y, +z, -z)。
// 法線の各成分の二乗が、その軸の「正か負か」の面の重みになる。nx² + ny² + nz² = 1 なので、重みの合計は 1。
float3 AmbientCube(float3 cube[6], float3 n) {
  float3 n2 = n * n;                                          // 二乗が重み
  int3 neg = (n < 0.0) ? 1 : 0;                               // 負の側なら 1（-x の面を選ぶ）
  return n2.x * cube[neg.x] + n2.y * cube[neg.y + 2] + n2.z * cube[neg.z + 4];
}
```

6 色の保存量は SH L2（9 色）より少ないです。Valve は SH に置き換えれば忠実度を上げられると認めたうえで、当時の画素シェーダー 2.x の定数レジスタが 32 本しかなかったこと（ps_3_0 では 224 本）を、選択の背景に挙げています。

### 放射照度ボリューム {#volume}

Ambient Cube のサンプルは、3D の空間構造に並べます。階層にはせず 4 × 4 × 8 フィート（約 1.22 × 1.22 × 2.44 m）の粗い間隔です。間接光は空間でゆっくり変わるので、速い参照があればよく極端な精度は要らない、という理由です。

動く物体を描くときは物体の重心にいちばん近いサンプルを選び空間のフィルターはかけません。そのため、物体の動きにつれて方向のある環境光が急に切り替わることがあります。Valve は環境光と局所ライトの情報を時間で平均して、光の飛びが目立たないようにしています。主人公のような重要な物体は直接光に環境光が埋もれて硬く見えないよう環境光を、直接光に応じて経験的に強めます。

C++ で見積もると 100 m × 100 m × 20 m の範囲は、この間隔で 83 × 83 × 9 ＝ 62,001 点です。1 点が 6 面 × R11G11B10（4 バイト）なら 1.42 MiB です。50 m × 50 m の範囲なら 0.36 MiB です。

```hlsl
// ================= ② ボリュームの読み =================

// ワールド位置から、6 面の色をトライリニアで読む。Valve は最寄りの 1 点をそのまま使う（補間しない）が、
// 動く物体が移動すると、そのたびに光が段階的に飛ぶ。トライリニアにすれば連続に変わる。
void SampleVolume(float3 world, out float3 cube[6]) {
  float3 uvw = (world - g_volume_origin) * g_volume_inv_size;   // 0〜1 のボリューム座標
  [unroll] for (int i = 0; i < 6; ++i) {
    cube[i] = g_ambient_cube_volume[i].SampleLevel(g_linear_clamp, uvw, 0).rgb;
  }
}
```

```hlsl
// ================= ④ 時間平滑 =================

// 物体ごとの Ambient Cube を、前のフレームの値と混ぜる。1 つの物体につき 6 つの色を、バッファに持つ。
RWStructuredBuffer<float3> g_object_cubes : register(u0);     // [物体の番号 * 6 + 面]
StructuredBuffer<float3> g_object_positions : register(t8);   // 物体の位置

[numthreads(64, 1, 1)]
void SmoothCubesCS(uint3 id : SV_DispatchThreadID) {
  uint object_index = id.x;
  float3 cube[6];
  SampleVolume(g_object_positions[object_index], cube);       // 今の位置の値
  [unroll] for (int i = 0; i < 6; ++i) {
    float3 previous = g_object_cubes[object_index * 6 + i];
    g_object_cubes[object_index * 6 + i] = lerp(previous, cube[i], g_smooth_blend);   // 指数移動平均
  }
}
```

最寄りの 1 点の代わりにこのコードはトライリニア補間で 6 面を読みます。物体が動いても連続に変わり光が飛びません。3D テクスチャを 6 枚に分けているのは、面ごとに補間するためです。時間平滑（`SmoothCubesCS`）は補間で足りない場合の保険で、指数移動平均で光の変化を遅らせます。

### 局所ライト {#local}

Ambient Cube は間接光だけです。局所のライトからの直接光は別に足します。Valve の対象ハードウェアでは画素シェーダー 2.0 で最大 2 つの局所ライトを、画素ごとか頂点ごとに計算します。重要な 2 つを超えるライトは非局所とみなし、Ambient Cube に混ぜます。より新しいハードウェアでは 2 つのライトに Phong の鏡面項（Fresnel 付き）も足します。

局所ライトの拡散には Half Lambert を使います。`dot(n, l)` を 0.5 倍して 0.5 を足し、二乗します。-1〜1 の値が 0〜1 になりライトの裏側でも形が保たれます。物理的ではありませんが実装が簡単で、知覚の効果が大きいと書かれています。

Ambient Cube に局所ライトを足す式は、資料にありません。上のコード（`AddLightToCube`）は 6 面に `色 × max(±軸・l, 0)` を足す私の近似です。軸の方向ではそのライトの正しいランバート値と一致し、軸の間では近似になります。

```hlsl
// ================= ③ 局所ライト =================

// Half Lambert: dot を 0.5 倍して 0.5 を足し、二乗する。-1〜1 の dot を 0〜1 にして、裏側も形を保つ（Valve、非物理）。
float HalfLambert(float3 n, float3 l) {
  float h = dot(n, l) * 0.5 + 0.5;
  return h * h;
}

// 3 番目以降の局所ライトを、Ambient Cube に足す（Valve: 2 つを超えるライトは、環境光に混ぜる）。
// 方向 l（ライトへ向かう）と色 c のライトを、6 面に分ける。面 ±axis には c × max(±axis・l, 0) を足す。
// 軸の方向では、その軸の法線のランバートの値と一致する。軸の間では近似になる。
void AddLightToCube(inout float3 cube[6], float3 l, float3 c) {
  cube[0] += c * max( l.x, 0.0);
  cube[1] += c * max(-l.x, 0.0);
  cube[2] += c * max( l.y, 0.0);
  cube[3] += c * max(-l.y, 0.0);
  cube[4] += c * max( l.z, 0.0);
  cube[5] += c * max(-l.z, 0.0);
}
```

## 完成形：画素シェーダーと比較用 SH {#complete}

```hlsl
// ================= ⑤ 比較：SH L2 の放射照度 =================

// 9 個の SH 係数 sh[0..8]（放射輝度の射影）から、法線 n の放射照度を求める。
// 基底 × 余弦ローブの畳み込み係数（L0 = π、L1 = 2π/3、L2 = π/4）をあらかじめ掛けておくと、
// 評価は基底との内積だけになる。ここでは、掛けていない係数を受け取る。
float3 IrradianceFromSH9(float3 sh[9], float3 n) {
  const float pi = 3.14159265;
  float3 e = sh[0] * (0.282095 * pi);
  e += sh[1] * (0.488603 * n.y * 2.0 * pi / 3.0);
  e += sh[2] * (0.488603 * n.z * 2.0 * pi / 3.0);
  e += sh[3] * (0.488603 * n.x * 2.0 * pi / 3.0);
  e += sh[4] * (1.092548 * n.x * n.y * pi / 4.0);
  e += sh[5] * (1.092548 * n.y * n.z * pi / 4.0);
  e += sh[6] * (0.315392 * (3.0 * n.z * n.z - 1.0) * pi / 4.0);
  e += sh[7] * (1.092548 * n.x * n.z * pi / 4.0);
  e += sh[8] * (0.546274 * (n.x * n.x - n.y * n.y) * pi / 4.0);
  return max(e, 0.0);                                          // L2 まででも負になりうるので、0 で切る
}

// ================= 画素シェーダー =================

Texture2D<float4> g_albedo_tex : register(t9);

struct PSInput {
  float4 position : SV_Position;
  float3 world_position : TEXCOORD0;
  float3 world_normal : NORMAL;
  float2 uv : TEXCOORD1;
};

float4 DynamicObjectPS(PSInput input) : SV_Target {
  float3 n = normalize(input.world_normal);
  float3 albedo = g_albedo_tex.Sample(g_linear_clamp, input.uv).rgb;

  // 1. 放射照度ボリュームから、この位置の Ambient Cube を読む（ライトマップと同じベイクの結果）。
  float3 cube[6];
  SampleVolume(input.world_position, cube);

  // 2. 主人公などの重要な物体は、環境光を強める。直接光に環境光が埋もれて、硬く見えるのを避ける（Valve のヒューリスティック）。
  [unroll] for (int i = 0; i < 6; ++i) cube[i] *= g_ambient_boost;

  // 3. 局所ライトの 2 つは、Half Lambert で直接足す。3 つ目以降を使うなら、AddLightToCube で cube に足す。
  float3 direct = 0;
  [unroll] for (int j = 0; j < 2; ++j) {
    direct += g_light_color[j] * HalfLambert(n, g_light_dir[j]);
  }

  // 4. 間接光（拡散）= アルベド/π × 放射照度。Ambient Cube が返すのは放射照度（余弦で積分済み）。
  float3 indirect = albedo / 3.14159265 * AmbientCube(cube, n);

  return float4(albedo * direct / 3.14159265 + indirect, 1.0);
}

// ================= 検証用の入口（ここまでの関数を、すべてコンパイルに通すため）=================

cbuffer ShCB : register(b1) {
  float4 g_sh[9];                // SH L2 の係数（rgb）。比較表示用
  float3 g_extra_dir;            // 3 つ目のライトの向き
  float g_pad3;
  float3 g_extra_color;
  float g_pad4;
};

float4 ShComparePS(PSInput input) : SV_Target {
  float3 n = normalize(input.world_normal);
  float3 sh[9];
  [unroll] for (int i = 0; i < 9; ++i) sh[i] = g_sh[i].rgb;
  float3 cube[6];
  SampleVolume(input.world_position, cube);
  AddLightToCube(cube, normalize(g_extra_dir), g_extra_color);   // 3 つ目のライトを Ambient Cube に足す
  // 左半分は SH L2、右半分は Ambient Cube を表示して、見比べる。
  float3 e = (input.position.x < 960.0) ? IrradianceFromSH9(sh, n) : AmbientCube(cube, n);
  return float4(e, 1.0);
}
```

画素シェーダー `DynamicObjectPS` はボリュームから Ambient Cube を読み主人公なら環境光を強め、局所ライト 2 つを Half Lambert で足し、間接光はアルベド/π × 放射照度で加えます。`IrradianceFromSH9` は次の節の比較で使う SH L2 の評価で、L0 = π、L1 = 2π/3、L2 = π/4 の畳み込み係数を掛けます。

## 表現の精度：Ambient Cube と SH {#accuracy}

Ambient Cube と SH のどちらが、環境の放射照度をどれだけ正確に再現するかを C++ で数えました。環境の放射輝度 L(ω) を決め正解の放射照度（コサイン重みの半球積分）を 3000 方向の法線で求め、3 つの近似との RMS 誤差を平均の放射照度で割った値で比べます。

<svg class="fig flow" viewBox="0 0 680 224" role="img" aria-label="Ambient Cube と SH の誤差"><defs><marker id="do-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">放射照度の RMS 誤差(平均値に対する割合)。青: Ambient Cube(6)、黄: SH L1(4)、灰: SH L2(9)</text><line x1="50" y1="184" x2="610" y2="184" stroke="#94a3b8"/><rect x="80" y="127.0" width="38" height="57.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="99" y="122.953125" text-anchor="middle" font-size="10" fill="currentColor">0.122</text><rect x="122" y="184.0" width="38" height="1.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="141" y="180.0" text-anchor="middle" font-size="10" fill="currentColor">0.000</text><rect x="164" y="184.0" width="38" height="1.0" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="183" y="180.0" text-anchor="middle" font-size="10" fill="currentColor">0.000</text><text x="140" y="200" text-anchor="middle" font-size="11" fill="currentColor">空と地面</text><rect x="260" y="45.4" width="38" height="138.6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="279" y="41.390625" text-anchor="middle" font-size="10" fill="currentColor">0.296</text><rect x="302" y="70.2" width="38" height="113.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="321" y="66.18750000000001" text-anchor="middle" font-size="10" fill="currentColor">0.243</text><rect x="344" y="165.8" width="38" height="18.2" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="363" y="161.8125" text-anchor="middle" font-size="10" fill="currentColor">0.039</text><text x="320" y="200" text-anchor="middle" font-size="11" fill="currentColor">太陽 + 環境光</text><rect x="440" y="108.4" width="38" height="75.6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="459" y="104.390625" text-anchor="middle" font-size="10" fill="currentColor">0.161</text><rect x="482" y="126.2" width="38" height="57.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="501" y="122.25" text-anchor="middle" font-size="10" fill="currentColor">0.123</text><rect x="524" y="179.9" width="38" height="4.1" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="543" y="175.921875" text-anchor="middle" font-size="10" fill="currentColor">0.009</text><text x="500" y="200" text-anchor="middle" font-size="11" fill="currentColor">片側が明るい部屋</text></svg>

- 空と地面（上が 1.0、下が 0.2）: SH L1 と L2 は、上下の差が y の 1 次関数なので、誤差 0（0.0000）。Ambient Cube は 0.122。
- 太陽 + 環境光（鋭い方向光を含む）: Ambient Cube が 0.296、SH L1 が 0.243、SH L2 が 0.039。
- 片側（+x）が明るい部屋: Ambient Cube が 0.161、SH L1 が 0.123、SH L2 が 0.009。

SH L1 は 4 係数だけで、Ambient Cube の 6 色より精度が高いです。ただし、SH L1 は負の放射照度が出ることがあります（リンギング）。Ambient Cube は 6 色がどれも非負で、重みも非負なので結果が負になりません。鋭い方向光があるときはどちらも L2 に大きく及ばないことが分かります。

SH L2 は 9 係数 × 3 色 ＝ 27 個の float で、Ambient Cube（18 個）の 1.5 倍です。評価も SH のほうが重いが、2006 年と違って今は定数レジスタの制限が緩いです。精度を取るか保存量と評価の軽さを取るかの選択になります。

## 背景への影響 {#feedback}

動く物体は周りの光を受けるだけでなく、周りに影を落とし光を反射します。ライトマップは焼き込み済みで、動く物体を知らないのでこれを反映できません。

- 動く物の影（直接光の影）: 実行時のシャドウ マップ（[Shadows](../../shadows/index.md)）。ミックス ライト（直接光は実行時）なら自然に出る。
- 動く物の接地の暗さ（AO）: AO（[AO](../../ao/index.md)）、ブロブ影（[Blob and Planar Projected Shadows](../../shadows/special-cases/blob-planar.md)）、コンタクト シャドウ（[Contact Shadows](../../shadows/contact-shadows.md)）。
- 動く物体からの反射光（赤い服が壁を赤くする）: 反映されない。SSGI、DDGI、動的なプローブで近似する。

## 静的と動的の見た目の差を小さくする {#match}

ライトマップ（高品質、焼き込み）とプローブ（低周波、補間）の品質の差が目立ちます。キャラクターが壁の前に立つとキャラクターの陰影だけがのっぺり見えます。

- プローブをベイクの結果から作る: ライトマップと同じ光源、同じバウンス数。
- プローブを動く物が通る場所に密に置く: 壁の近くでは差が出やすい。
- 接地の暗さを足す: AO とコンタクト シャドウ。
- 主人公は環境光を強める（Valve）かキャラクターの近くに追従する弱いフィル ライトを置く。

## 数字を出す C++ {#cpp}

Ambient Cube と SH の精度比較、保存量、ボリュームの大きさを数えた C++ です。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。HLSL は `fxc`（ps_5_0、cs_5_0）でコンパイルして確かめました。実行して絵は確かめていません。

```cpp
// 動く物体の間接光の表現を比べる。環境の放射輝度 L(ω) から、法線 n の放射照度 E(n) を、
//   (a) 正解（コサイン重みの半球積分）
//   (b) Valve の Ambient Cube（6 方向の E を保存し、n の二乗で重み付け）
//   (c) SH L1（4 係数）  (d) SH L2（9 係数）
// で出して、誤差を比べる。環境は 3 種類（空と地面、太陽 + 環境光、片側の壁が明るい部屋）。
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <functional>
#include <vector>

namespace {
constexpr double kPi = 3.14159265358979323846;
struct V3 { double x, y, z; };
double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
V3 Norm(V3 a) { const double l = std::sqrt(Dot(a, a)); return {a.x / l, a.y / l, a.z / l}; }

// フィボナッチ螺旋で、球面にほぼ一様な点を n 個置く。
std::vector<V3> SpherePoints(int n) {
  std::vector<V3> p(n);
  const double golden = kPi * (3.0 - std::sqrt(5.0));
  for (int i = 0; i < n; ++i) {
    const double y = 1.0 - 2.0 * (i + 0.5) / n;
    const double r = std::sqrt(1.0 - y * y);
    p[i] = {r * std::cos(golden * i), y, r * std::sin(golden * i)};
  }
  return p;
}

// 実数球面調和の基底 (L2 まで)。順番: 00, 1-1, 10, 11, 2-2, 2-1, 20, 21, 22。
std::array<double, 9> ShBasis(V3 d) {
  return {0.282095,
          0.488603 * d.y, 0.488603 * d.z, 0.488603 * d.x,
          1.092548 * d.x * d.y, 1.092548 * d.y * d.z, 0.315392 * (3.0 * d.z * d.z - 1.0),
          1.092548 * d.x * d.z, 0.546274 * (d.x * d.x - d.y * d.y)};
}
// 放射照度への畳み込み係数（ランバートの余弦ローブ）: L0 = π、L1 = 2π/3、L2 = π/4。
const double kBand[9] = {kPi, 2 * kPi / 3, 2 * kPi / 3, 2 * kPi / 3, kPi / 4, kPi / 4, kPi / 4, kPi / 4, kPi / 4};
}  // namespace

int main() {
  const auto dirs = SpherePoints(200000);                    // 積分用
  const auto normals = SpherePoints(3000);                   // 評価用の法線
  const double w = 4.0 * kPi / dirs.size();                  // 1 点あたりの立体角

  const V3 sun = Norm({0.5, 0.7, 0.5});
  struct Env { const char* name; std::function<double(V3)> L; };
  const Env envs[] = {
      {"空と地面 (上 1.0 / 下 0.2)", [](V3 d) { return d.y > 0 ? 1.0 : 0.2; }},
      {"太陽 + 環境光 (0.2 + 8 exp(-20(1-cos)))", [&](V3 d) { return 0.2 + 8.0 * std::exp(-20.0 * (1.0 - Dot(d, sun))); }},
      {"片側が明るい部屋 (+x 側 1.0 / ほか 0.15)", [](V3 d) { return d.x > 0.5 ? 1.0 : 0.15; }}};

  std::printf("環境                                      平均E    Ambient Cube(6)   SH L1(4)    SH L2(9)   (RMS 誤差 / 平均E)\n");
  for (const Env& env : envs) {
    // 正解の放射照度。
    auto exact = [&](V3 n) {
      double e = 0;
      for (const V3& d : dirs) e += env.L(d) * std::max(0.0, Dot(n, d)) * w;
      return e;
    };
    // Ambient Cube: 6 軸方向の E を保存する。
    std::array<double, 6> cube;
    const V3 axes[6] = {{1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};
    for (int i = 0; i < 6; ++i) cube[i] = exact(axes[i]);
    // SH: L(ω) を 9 係数に射影する。
    std::array<double, 9> sh{};
    for (const V3& d : dirs) {
      const auto y = ShBasis(d);
      const double l = env.L(d);
      for (int i = 0; i < 9; ++i) sh[i] += l * y[i] * w;
    }

    double se_cube = 0, se_l1 = 0, se_l2 = 0, mean = 0;
    for (const V3& n : normals) {
      const double e = exact(n);
      // Ambient Cube の評価: n² で、各軸の正負の面を重み付けして足す。
      const double ac = n.x * n.x * cube[n.x < 0] + n.y * n.y * cube[2 + (n.y < 0)] + n.z * n.z * cube[4 + (n.z < 0)];
      // SH の放射照度: Σ band(i) × 係数(i) × 基底(n)。L1 は 4 項、L2 は 9 項。
      const auto yn = ShBasis(n);
      double e1 = 0, e2 = 0;
      for (int i = 0; i < 9; ++i) {
        const double t = kBand[i] * sh[i] * yn[i];
        e2 += t;
        if (i < 4) e1 += t;
      }
      se_cube += (ac - e) * (ac - e);
      se_l1 += (e1 - e) * (e1 - e);
      se_l2 += (e2 - e) * (e2 - e);
      mean += e;
    }
    const double inv = 1.0 / normals.size();
    mean *= inv;
    std::printf("%-42s %6.3f   %10.4f       %8.4f   %8.4f\n", env.name, mean, std::sqrt(se_cube * inv) / mean,
                std::sqrt(se_l1 * inv) / mean, std::sqrt(se_l2 * inv) / mean);
  }

  std::printf("\n保存量（RGB 3 チャンネル、1 サンプルあたりの float 数）: Ambient Cube %d、SH L1 %d、SH L2 %d\n", 6 * 3,
              4 * 3, 9 * 3);
  // Valve の irradiance volume: 4 x 4 x 8 フィート = 1.22 x 1.22 x 2.44 m。
  const double dx = 4 * 0.3048, dz = 8 * 0.3048;
  std::printf("Valve の間隔 (4' x 4' x 8') = %.2f x %.2f x %.2f m\n", dx, dx, dz);
  for (double size : {50.0, 100.0}) {
    const double nx = std::ceil(size / dx), nz = std::ceil(20.0 / dz);
    const double samples = nx * nx * nz;
    std::printf("%3.0f m x %3.0f m x 20 m の範囲: %.0f x %.0f x %.0f = %.0f 点。R11G11B10 (4 B) x 6 面で %.2f MiB\n", size,
                size, nx, nx, nz, samples, samples * 6 * 4 / 1048576.0);
  }
  return 0;
}
```

```text title="実行結果"
環境                                      平均E    Ambient Cube(6)   SH L1(4)    SH L2(9)   (RMS 誤差 / 平均E)
空と地面 (上 1.0 / 下 0.2)            1.885       0.1217         0.0000     0.0000
太陽 + 環境光 (0.2 + 8 exp(-20(1-cos)))  1.257       0.2957         0.2428     0.0388
片側が明るい部屋 (+x 側 1.0 / ほか 0.15)  1.139       0.1613         0.1232     0.0087
```

```text title="実行結果（続き）"
保存量（RGB 3 チャンネル、1 サンプルあたりの float 数）: Ambient Cube 18、SH L1 12、SH L2 27
Valve の間隔 (4' x 4' x 8') = 1.22 x 1.22 x 2.44 m
 50 m x  50 m x 20 m の範囲: 42 x 42 x 9 = 15876 点。R11G11B10 (4 B) x 6 面で 0.36 MiB
100 m x 100 m x 20 m の範囲: 83 x 83 x 9 = 62001 点。R11G11B10 (4 B) x 6 面で 1.42 MiB
```

## よくあるミス

??? failure "動く物体だけ背景と明るさが合わない"
    プローブがライトマップと別のベイクから作られている。同じ光源、同じバウンス数でベイクしたプローブを使い動く物体が通る場所に置く。

??? failure "動く物体が、移動中に明るさが飛ぶ"
    最寄りの 1 点を使っている。トライリニア補間にするか時間で平均する。

??? failure "壁の向こうの明るさがプローブに混ざる"
    プローブが壁をまたいで補間されている。壁の両側のプローブは別々に扱う（可視性を見て重みを下げる）。

??? failure "SH で、背中側が真っ黒になる"
    L1 のリンギングで、放射照度が負になっている。負は 0 に切るか Ambient Cube に切り替える。

??? failure "鏡面がライトマップだけで、つるつるの面が何も映さない"
    ライトマップは拡散だけ。反射プローブや SSR を足す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 鏡面は反射の手法で、動く物体はプローブで。
    - [x] Ambient Cube は 6 色。法線の二乗で重み付けして足す。
    - [x] 精度は SH L2 が高い。保存量と評価は Ambient Cube が軽い。
    - [x] 最寄りの 1 点は光が飛ぶ。補間するか時間で平均する。
    - [x] プローブはライトマップと同じベイクから作る。

## 参考

- Jason Mitchell, Gary McTaggart, Chris Green, "Shading in Valve's Source Engine", SIGGRAPH 2006, Advanced Real-Time Rendering in 3D Graphics and Games Course, Chapter 8, 2006.（8.1〜8.5 の冒頭まで読んだ。HDR 以降は読んでいない）
- Gene Greger, Peter Shirley, Philip Hubbard, Donald Greenberg, "The Irradiance Volume", IEEE Computer Graphics and Applications 18(2), 1998.（読んでいない）
- Michał Iwanicki, "Lighting Technology of The Last of Us", SIGGRAPH 2013, Advances in Real-Time Rendering in Games（取得できず、読んでいない。アンビエント ダイスの話）
- Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001（SH の畳み込み係数の元。読んでいない。係数は一般的な値）

## 関連ページ

- [Lightmaps](index.md)
- [Probe GI](../probes/index.md)
- [Reflections](../../reflections/index.md)
- [Diffuse and Specular](../theory/diffuse-specular.md)
