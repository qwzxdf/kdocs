---
title: Underwater God Rays
tags:
  - 描画
---

# Underwater God Rays

水に潜って水面を見上げると太陽の光が柱のように差し込んで見えます。波がうねるとその光の柱もゆらゆら揺れます。空気中のゴッド レイと同じ原理ですが、水中には 2 つの違いがあります。水が光を強く吸収することと水面の波が光を集めたり散らしたりすることです。

<strong>水中の光の筋は光の通り道にある粒子が光を散らして、その通り道だけが明るく見える現象です</strong>。このページでは見える理由、水中での光の向き 3 つの作り方（放射状のブラー、シャドウ マップのレイマーチ、メッシュ）、水中らしさを出す工夫を説明します。

!!! tip "ポイント"
    - 作り方は 3 つです。画面空間の放射状ブラー（安い）、シャドウ マップを使ったレイマーチ（正確）、半透明のメッシュ（最も安い）です。
    - レイマーチは視線に沿って進み各点の「太陽光が届くか」「水面でどれだけ吸収されたか」を足します。
    - 波の揺れはコースティクスで光を変調して表します。
    - 水が濁っているほど筋が見えます。澄んだ水では筋は弱くなります。
    - 太陽の光は水面で屈折するので、水中の光の向きは空気中より真下に近づきます。

!!! info "このページを読む前に"
    - [Underwater Rendering](index.md)（このセクション全体の地図と、読む順番）

## 光の筋が見える理由 {#why}

光の筋は光そのものではなく光の通り道にある粒子が光を散らして、その一部がカメラに届くことで見えます。水中にはプランクトン、泥、微生物などの細かい粒子が必ずあります。粒子のない真空では光が通っても、横から見ると何も見えません。

波は水面を細かいレンズの集まりのようにして、光を集めた所は明るく散らした所は暗くします。その模様は水中の奥まで光の柱として伸びて、波とともに動きます。これが光の筋が揺れる理由で水面の模様（コースティクス）が 3 次元に伸びたものとも言えます。

## 水中での光の向き {#direction}

太陽の光は水面で屈折して水の中へ入ります。空気の屈折率 1.0 から水の 1.33 へ入るので、光は法線（真下）の側へ曲がります。スネルの法則 `sin θ_水 = sin θ_空気 / 1.33` で向きが決まります。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="太陽の光が水面で屈折して、水中では真下に近い向きに進む"><defs><marker id="grA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">水面での屈折: 水中の光は、真下に寄る</text>
<rect x="20" y="130" width="680" height="130" fill="rgba(76,139,245,0.15)"/><line x1="20" y1="130" x2="700" y2="130" stroke="#4c8bf5" stroke-width="3"/><text x="690" y="124" text-anchor="end" style="font-size:12px">水面</text>
<line x1="360" y1="40" x2="360" y2="250" stroke="#94a3b8" stroke-dasharray="5 4"/><text x="366" y="48" style="font-size:12px">法線（真下）</text>
<line x1="180" y1="40" x2="360" y2="130" stroke="#e5aa28" stroke-width="3.5" marker-end="url(#grA)"/><text x="170" y="58" text-anchor="end" style="font-size:12px;font-weight:600">空気中: 入射角 60°</text>
<line x1="360" y1="130" x2="480" y2="236" stroke="#e5aa28" stroke-width="3.5" marker-end="url(#grA)"/><text x="490" y="222" style="font-size:12px;font-weight:600">水中: 約 40.6°</text>
<text x="360" y="150" text-anchor="middle" style="font-size:11px"> </text>
<text x="500" y="90" style="font-size:12px">低い太陽（水平線近く、90°）でも、</text><text x="500" y="108" style="font-size:12px">水中は最大で約 48.8° までしか曲がらない</text></svg>

太陽の高さが 30°（法線から 60°）なら水中の向きは `sin θ = sin 60° / 1.33 = 0.866 / 1.33 = 0.651` で、`θ ≒ 40.6°` になります。太陽が水平線ぎりぎり（入射角 90°）でも `sin θ = 1 / 1.33 = 0.752` で、`θ ≒ 48.8°` が限界です。水中の光はどんなときも真下から 48.8° の円錐の内側にしか来ません。

HLSL では `refract(-sun_dir, float3(0, 1, 0), 1.0 / 1.33)` で求めます。`sun_dir` は太陽の方向（光の来る向き）です。

## 方法 1: 放射状のブラー（画面空間） {#radial}

太陽の画面上の位置から各画素へ向かって何回か読んで、足す方法です（[Screen-Space Radial Blur](../../atmosphere/god-rays/radial-blur.md)）。水中では太陽が水面の向こうにあるので、明るい水面（波を通った太陽光）の領域を光の源のマスクとして使います。

```hlsl
Texture2D<float> g_light_mask : register(t0);        // 光の源の明るさ（水面の明るい部分。0..1）
SamplerState g_linear_clamp : register(s0);

cbuffer RadialConstants : register(b0) {
  float2 g_sun_screen;       // 太陽の画面上の UV（画面の外でもよい）
  float g_density;           // 読む範囲の広さ。0..1。例: 0.9
  float g_decay;             // 1 回進むごとの減衰。例: 0.96
  float3 g_sun_color_underwater;   // 水中の太陽の色。赤が減った青緑。例: (0.2, 0.7, 0.8)
  float g_intensity;         // 全体の強さ。例: 0.6
};
static const int kSamples = 48;

float4 RadialGodRaysPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  // 画素から太陽へ向かう 1 回分の移動量
  float2 delta = (uv - g_sun_screen) / kSamples * g_density;
  float2 sample_uv = uv;
  float illum = 0.0;
  float weight = 1.0;
  for (int i = 0; i < kSamples; ++i) {
    sample_uv -= delta;                                // 太陽の方へ 1 歩進む
    illum += g_light_mask.SampleLevel(g_linear_clamp, sample_uv, 0) * weight;
    weight *= g_decay;                                 // 遠いほど寄与を減らす
  }
  float3 god_rays = illum / kSamples * g_sun_color_underwater * g_intensity;
  return float4(god_rays, 1.0);                        // 加算ブレンドで、シーンに足す
}
```

画面全体の後処理で読み出しは 48 回だけです。1080p なら `1920 × 1080 × 48 ≒ 1 億回` で半分の解像度に落とせば 4 分の 1 です。

弱点は 2 つあります。遮蔽物（岩、船）が光を遮る正確な影が出ません。太陽が画面の外にあるときは方向が不安定になります。

## 方法 2: シャドウ マップを使ったレイマーチ {#raymarch}

各画素について視線に沿って少しずつ進みます。各点で太陽光が届いているか（影の中でないか）をシャドウ マップで調べて、足し合わせます。水面の波による光の変調（コースティクス）と水中での吸収も含められます（[Shadow Map Raymarching](../../atmosphere/god-rays/shadowmap-march.md)）。

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="視線に沿ってサンプルし、各点で影と吸収を調べる。岩の影の中の点は足さない"><defs><marker id="grB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">視線に沿ったサンプルと、各点の「光が届くか」</text>
<line x1="40" y1="60" x2="700" y2="60" stroke="#4c8bf5" stroke-width="3"/><text x="690" y="52" text-anchor="end" style="font-size:12px">水面</text>
<g stroke="#e5aa28" stroke-width="3" opacity="0.7"><line x1="150" y1="60" x2="230" y2="200"/><line x1="260" y1="60" x2="340" y2="200"/><line x1="380" y1="60" x2="460" y2="200"/><line x1="500" y1="60" x2="580" y2="200"/></g>
<path d="M300,150 L400,150 L400,210 L300,210 Z" fill="rgba(100,116,139,0.45)" stroke="#64748b"/><text x="350" y="236" text-anchor="middle" style="font-size:12px">岩（光を遮る）</text>
<line x1="60" y1="226" x2="660" y2="90" stroke="currentColor" stroke-width="2" marker-end="url(#grB)"/>
<g fill="#e5484d"><circle cx="110" cy="215" r="5" fill="#e5aa28"/><circle cx="190" cy="196" r="5" fill="#e5aa28"/><circle cx="270" cy="178" r="5" fill="#e5aa28"/><circle cx="350" cy="160" r="5" fill="#94a3b8"/><circle cx="430" cy="142" r="5" fill="#e5aa28"/><circle cx="510" cy="124" r="5" fill="#e5aa28"/><circle cx="590" cy="106" r="5" fill="#e5aa28"/></g>
<text x="60" y="246" style="font-size:12px">カメラ</text><text x="350" y="182" text-anchor="middle" style="font-size:11px;fill:#64748b">影の中: 足さない</text>
<text x="560" y="150" style="font-size:12px">黄: 光が届く点（足す）</text></svg>

```hlsl
Texture2D<float> g_shadow_map : register(t1);
SamplerComparisonState g_shadow_sampler : register(s1);
Texture2D<float> g_caustics : register(t2);            // 水面の模様（タイル化したテクスチャ。1 = 平均）
SamplerState g_wrap_sampler : register(s2);

cbuffer RaymarchConstants : register(b1) {
  float4x4 g_world_to_light;     // ワールド → ライトのクリップ空間
  float3 g_camera_position;
  float g_surface_y;             // 水面の高さ（ワールド y）
  float3 g_sun_dir_underwater;   // 水中の光の進む向き（下向き。屈折済み）
  float g_scatter;               // 散乱の強さ。例: 0.05
  float3 g_absorption;           // 色ごとの吸収（1/メートル）。例: (0.45, 0.07, 0.03)
  float g_phase_g;               // 前方散乱の偏り。例: 0.7
  float3 g_sun_color;
  float g_caustic_scale;         // 模様の大きさ（1/メートル）。例: 0.25
  float g_time;                  // 秒。模様の動き用
  float3 _pad;
};
static const int kSteps = 32;

// 前方への散乱が強い粒子を表す位相関数（Henyey-Greenstein）
float HenyeyGreenstein(float cos_theta, float g) {
  float g2 = g * g;
  return (1.0 - g2) / (4.0 * 3.14159265 * pow(1.0 + g2 - 2.0 * g * cos_theta, 1.5));
}

// 同じ位置で同じ値が出る、画面上のノイズ。サンプルの開始をずらして縞を消す
float InterleavedGradientNoise(float2 p) {
  return frac(52.9829189 * frac(dot(p, float2(0.06711056, 0.00583715))));
}

float SampleSunVisibility(float3 world_pos) {
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);
  if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;      // 足した: シャドウ マップの外は、光が届くとする
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z - 0.001);
}

float4 UnderwaterRaymarchPS(float4 pos : SV_Position, float3 world_pos : TEXCOORD0) : SV_Target {
  float3 to_pixel = world_pos - g_camera_position;
  float ray_length = length(to_pixel);
  float3 view_dir = to_pixel / ray_length;
  float step_len = ray_length / kSteps;

  // 散乱角の余弦: 光の進む向きと、粒子からカメラへ戻る向き（-view_dir）のなす角。
  // 太陽の方を見上げるとき 1 に近づいて、前方散乱で明るくなる
  float cos_theta = dot(g_sun_dir_underwater, -view_dir);
  float phase = HenyeyGreenstein(cos_theta, g_phase_g);

  float jitter = InterleavedGradientNoise(pos.xy);
  float3 in_scatter = 0.0;

  for (int i = 0; i < kSteps; ++i) {
    float travelled = (i + jitter) * step_len;         // カメラからの距離
    float3 p = g_camera_position + view_dir * travelled;

    float lit = SampleSunVisibility(p);                // 影の中なら 0
    // コースティクス: 水平面の模様を、深さ方向に伸ばして使う（2D の模様を xz で引く）
    float caustic = g_caustics.SampleLevel(g_wrap_sampler, p.xz * g_caustic_scale + g_time * 0.03, 0);

    float depth_below = max(g_surface_y - p.y, 0.0);   // 水面から、この点までの深さ
    float3 sun = g_sun_color * exp(-g_absorption * depth_below / max(-g_sun_dir_underwater.y, 0.2));
    float3 to_camera = exp(-g_absorption * travelled); // この点から、カメラまでの吸収

    in_scatter += sun * lit * caustic * to_camera * g_scatter * phase * step_len;
  }
  return float4(in_scatter, 1.0);                      // 加算でシーンに足す
}
```

各項の意味を順に見ます。`lit` は影の中かどうかです。岩の影の中の点は光が届かないので足しません。`caustic` は水面の波が作る光の濃淡です。これを掛けると光の筋が波で揺れます。

`sun` は水面からその点まで光が進む間の吸収です。光は斜めに進むので鉛直の深さ `depth_below` を光の向きの y 成分で割って、実際の道のりに直しています（`max(…, 0.2)` で、水平に近い向きの暴走を防ぐ足した処理です）。`to_camera` はその点からカメラまでの吸収です。吸収は色ごとに違うので赤が先に消えて、遠くや深い所の筋は青緑になります。

`phase` は位相関数です。水中の粒子は光の進む向きへ強く散乱します。`g_phase_g = 0.7` なら太陽の方を見上げるとき（散乱角が 0 に近いとき）に筋が特に明るくなります。散乱角の余弦は光の進む向きと `-view_dir`（粒子からカメラへ戻る向き）の内積で決まります。`view_dir` の符号を間違えると太陽と反対を見たときに明るくなります。

数字で確かめます。1080p（約 207 万画素）で 32 ステップならシャドウ マップの読み出しは約 6600 万回です。半分の解像度で計算してアップサンプルすると、約 1650 万回になります。ジッターで開始位置をずらしているので、ステップが少なくても縞が出にくく、TAA やぼかしでならせます。

## 方法 3: 光の筋のメッシュ {#mesh}

水面から水中へ向かって細長い半透明の板を置く方法です（[Light Shaft Meshes](../../atmosphere/god-rays/mesh-shafts.md)）。形は太陽の向きに沿った細長い板で、上は明るく下に向かって消えます。板を数十枚描くだけなので最も安い方法です。

```hlsl
cbuffer ShaftConstants : register(b2) {
  float4x4 g_view_proj;
  float3 g_shaft_dir;        // 光の進む向き（水中。屈折済み。下向き）
  float g_shaft_length;      // 筋の長さ（メートル）。例: 30
  float g_shaft_width;       // 筋の幅（メートル）。例: 2
  float g_shaft_time;
  float2 _pad2;
};

struct ShaftVsOut {
  float4 pos : SV_Position;
  float v : TEXCOORD0;       // 0 = 水面側、1 = 先端
  float phase : TEXCOORD1;   // 筋ごとの位相
};

// 1 枚の筋 = 4 頂点のストリップ。instance_id が、筋の水面上の位置を決める
ShaftVsOut ShaftVS(uint vertex_id : SV_VertexID, uint instance_id : SV_InstanceID,
                   float3 surface_pos : POSITION) {      // surface_pos: 筋の根元（水面上）。インスタンス データ
  float2 corner = float2(vertex_id & 1, vertex_id >> 1);   // x: 左右、y: 水面側(0)/先端(1)
  float3 side = normalize(cross(g_shaft_dir, float3(0, 1, 0)));
  float3 world = surface_pos + side * (corner.x - 0.5) * g_shaft_width + g_shaft_dir * corner.y * g_shaft_length;

  ShaftVsOut o;
  o.pos = mul(float4(world, 1.0), g_view_proj);
  o.v = corner.y;
  o.phase = frac(sin(dot(surface_pos.xz, float2(12.9898, 78.233))) * 43758.5453);
  return o;
}

float4 ShaftPS(ShaftVsOut i) : SV_Target {
  // 先端へ向かって消える。波に合わせて、明るさをゆっくり揺らす
  float fade = pow(1.0 - i.v, 2.0);
  float shimmer = 0.75 + 0.25 * sin(g_shaft_time * 1.3 + i.phase * 6.2831853);
  return float4(float3(0.3, 0.8, 0.9) * fade * shimmer * 0.4, 1.0);     // 加算ブレンド
}
```

弱点は影や遮蔽物と連動しないことです。筋は岩に当たってもそのまま下へ伸びます。板が重なる所が明るくなるのは、加算ブレンドを使っているからです。

!!! note "確かめた範囲"
    HLSL は `fxc` で `RadialGodRaysPS`、`UnderwaterRaymarchPS`、`ShaftPS`（`ps_5_0`）と `ShaftVS`（`vs_5_0`）をコンパイルして、エラーが出ないことを確かめました。位相関数の符号は本文のとおり使うときに `-cos_theta` を渡す必要があります。GPU での描画は確認していません。

## 水中らしさを出す工夫 {#tips}

- 波で揺らします。光の筋の強さをコースティクスの模様で変調します。水面の揺れがそのまま筋の揺れになります。
- 深さで消します。光は深くなるほど吸収されて浅い所だけが明るくなります。
- 青緑に着色します。赤が吸収された水中の太陽光の色で描きます。
- 粒子を漂わせます。光の筋の中に細かい粒子（マリン スノー）を置くと筋が立体的に見えます（[Other Underwater Elements](other.md)）。

太陽の高さによる見え方の違いもあります。

- 真上（正午）の筋は真下へまっすぐ伸びます。
- 低い太陽（朝夕）は水面で屈折するので、筋が水中で斜めに伸びます。
- 太陽の方を向くとまぶしく見えます。
- 曇りや夜は光の筋が出ません。

## よくあるミス {#mistakes}

??? failure "光の筋が揺れずに固定されて見える"
    原因はコースティクスで光を変調していないことです。筋の強さに水面の模様を掛けて、時間でゆっくり動かします。メッシュ方式なら筋ごとに明るさを位相をずらして揺らします。

??? failure "光の筋が、太陽と逆の方向を向くまたは斜めすぎる"
    原因は屈折する前の太陽の向きをそのまま使っていることです。水中の光は `refract(-sun_dir, float3(0, 1, 0), 1.0 / 1.33)` の向きに進みます。最大でも真下から約 48.8° までです。

??? failure "光の筋が縞模様になる"
    原因はステップ数が少ないのに、全画素が同じ位置からサンプルしていることです。`InterleavedGradientNoise` で開始位置をずらして画素ごとに変えます。残るノイズはぼかしや TAA でならします。

??? failure "遠くまで、筋がいつまでも明るい"
    原因は水面から点までの吸収か点からカメラまでの吸収のどちらかを掛けていないことです。両方を掛けます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 筋は粒子が光を散らして見えます。水面の波で揺れます。
    - [x] 水中の光は水面で屈折して、真下から最大で約 48.8° の円錐の中を通ります。
    - [x] 精度はレイマーチ、軽さはメッシュ、中間が放射状ブラーです。
    - [x] レイマーチはシャドウ、コースティクス、吸収、位相関数を掛けて足します。

## 参考 {#references}

このページは次の資料を読まずに書きました。式と HLSL は自分で書いたもので、`fxc` でのコンパイルまで確かめています。

- Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004
- Guardado, Sánchez-Crespo, "Rendering Water Caustics", GPU Gems, Chapter 2, 2004
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Wronski, "Volumetric Fog and Lighting", SIGGRAPH 2014（ボリューム ライティング）

## 関連ページ

- [Underwater Rendering](index.md)
- [God Rays](../../atmosphere/god-rays/index.md)
