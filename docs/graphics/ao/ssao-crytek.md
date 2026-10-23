---
title: Crytek SSAO
tags:
  - 描画
---

# Crytek SSAO

<strong>SSAO</strong>（Screen-Space Ambient Occlusion）は、2007 年に Crytek が『Crysis』のエンジン（CryEngine 2）で実用化した、画面の深度バッファだけで AO を近似する方式です。それまでの AO は、モデルに焼き込むか、事前計算するものでした。毎フレーム、ポストプロセスとして、動くシーンにも使える AOを、初めて現実的なコストで出したのが、この方式です。以降のスクリーン空間 AO は、すべてこの発想の延長にあります。

このページでは、原型である Crytek 方式を、仕組みから順に説明します。深度バッファから位置を復元する方法、サンプルの取り方、そしてこの方式の弱点（平らな面が灰色になる）まで扱います。

!!! tip "ポイント"
    - 入力は<strong>深度バッファだけ</strong>（法線は不要）。<strong>ポストプロセス</strong>で全画面に 1 パス。
    - 各画素で周囲の球の中にランダムなサンプル点を置く。サンプル点を画面に投影して、その画素の深度と比べ、面の奥にあれば「遮られている」と数える。
    - AO ＝ 遮られていないサンプルの割合。
    - 球を使うので平らな面でも約半分が「遮られる」。面全体が灰色になるのが弱点（次の[Hemisphere SSAO](ssao-hemisphere.md) で解決）。
    - サンプル数が少ない（16 程度）ので画素ごとにサンプルをランダムに回転し、ぼかしで消す。

## 発想

[理論](theory/index.md)のとおり、AO は「<strong>点 p の周りの遮られていない方向の割合</strong>」でした。本来はシーンにレイを飛ばして調べます。Crytek 方式は、レイを飛ばす代わりに、「p の近くの点が物体の内側にあるか」を調べます。

<svg class="fig illust" viewBox="0 0 774 300" role="img" aria-label="Crytek SSAO のサンプル">
<text x="20" y="24" class="fig-title">p の周りの球の中のサンプル点が、面の「奥」にあれば、遮られているとみなす</text>
<path d="M60,200 L330,200 L380,140 L700,140" fill="none" stroke="currentColor" stroke-width="4"/>
<polygon points="60,200 330,200 380,140 700,140 700,270 60,270" fill="rgba(150,150,150,0.25)"/>
<circle cx="260" cy="200" r="7" fill="currentColor"/><text x="244" y="224" style="font-size:12px">p</text>
<circle cx="260" cy="200" r="70" fill="none" stroke="currentColor" stroke-dasharray="5 4"/>
<g fill="#2ea043"><circle cx="230" cy="150" r="5"/><circle cx="290" cy="165" r="5"/><circle cx="250" cy="135" r="5"/><circle cx="215" cy="175" r="5"/></g>
<g fill="#e5484d"><circle cx="215" cy="225" r="5"/><circle cx="285" cy="235" r="5"/><circle cx="250" cy="245" r="5"/><circle cx="300" cy="180" r="5"/></g>
<text x="400" y="80" style="font-weight:700">緑：面の手前（空が見える）</text>
<text x="400" y="104" style="font-weight:700;fill:#e5484d">赤：面の奥（遮られている）</text>
<text x="400" y="134" style="font-size:12px">平らな面では、球の下半分が、全部「奥」になる</text>
<text x="400" y="154" style="font-size:12px">→ 何も遮るものが無くても、約 50% が「遮られた」と数えられる</text>
<text x="20" y="290" style="font-size:12px">この「球の下半分」の問題が、Crytek 方式の最大の弱点</text>
</svg>

!!! info "ここで使われる「積分」を、やさしく言うと"
    Crytek SSAO の積分は、くじ引きです。

    - 半球の全方向を、細かく調べる代わりに、球の中に、ランダムな点を 16 個ほど撒く。
    - 各点が、物の裏側に入っていれば（遮られていれば）1、そうでなければ 0 と数える。
    - 遮られた点の割合が、AO。

    点の数が少ないので、ざらざらしたノイズが出ます。これを、ぼかしで、ならします。この「ランダムに選んで、平均する」考え方を、モンテカルロ法と呼びます。

    数式を使わない、くわしい説明は [Integrals and Elevation Angles in Plain Words](theory/integral-intuition.md) です。

## 手順

実際の処理を、順番に見ていきます。

最初に、深度バッファから画素のビュー空間の位置 p を復元します。次に、半径 R の球の中に N 個のランダムなベクトルを用意します（あらかじめ作っておき、全画素で共通に使います）。このベクトルは、画素ごとにランダムに回転します。全画素で同じ向きだと、同じ模様が繰り返されて縞が出るからです。

そして、サンプル点 s = p + R·ベクトル を画面に投影して、s が画面のどの画素に映るかを求めます。その画素の深度をバッファから読み、「画面から見える面の深度」を得ます。この面が s よりも手前（深度が小さい）にあれば、s は面の奥側、つまり何かの内側にあるので「遮られている」と数えます。最後に `AO = 1 − (遮られた数 / N)` として割合を出します。

## ① 深度から位置を復元する

深度バッファの値（0〜1）から、<strong>カメラからの距離（ビュー空間の z）</strong>を求め、そこから x・y を逆算します。プロジェクション行列の式を、逆に解くだけです（[投影](../../3d/projection.md)）。

左手系・標準の Z（near → 0、far → 1）の場合、深度値 d から、ビュー空間の奥行き z は、次のとおりです。

<div class="formula">z = (near · far) / (far − d · (far − near))</div>

x・y は、NDC 座標と視野角から、次のように求めます。

<div class="formula">x = ndc_x · z · tan(fovY/2) · aspect　、　y = ndc_y · z · tan(fovY/2)</div>

```hlsl
float LinearizeDepth(float d) {
  return near_z * far_z / (far_z - d * (far_z - near_z));
}

float3 ViewPosition(float2 uv, float z) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  return float3(ndc * tan_half_fov * z, z);
}
```

| 変数 | 意味 |
| --- | --- |
| `tan_half_fov` | `float2(tan(fovY/2) * aspect, tan(fovY/2))` |
| `uv.y` の反転 | テクスチャの V は下向き、NDC の y は上向き |

!!! note "reverse-Z のとき"
    深度が 1 → 0 に反転している場合（[投影](../../3d/projection.md)）、`LinearizeDepth` の式が変わります。自分の射影行列に合わせた式を使います。

## ②③ サンプルの作り方

<strong>球の中</strong>に N 個（16 前後）のベクトルを用意します。原点の近くに多く置くと、近い遮蔽ほど強く効くので、見た目が良くなります。

```cpp
std::vector<Vector3> MakeSphereKernel(int n, std::mt19937& rng) {
  std::uniform_real_distribution<float> unit(-1.0f, 1.0f);
  std::uniform_real_distribution<float> zero_one(0.0f, 1.0f);
  std::vector<Vector3> kernel;
  while (static_cast<int>(kernel.size()) < n) {
    Vector3 v(unit(rng), unit(rng), unit(rng));
    if (v.LengthSquared() > 1.0f || v.LengthSquared() < 1e-4f) continue;
    v.Normalize();
    float t = static_cast<float>(kernel.size()) / static_cast<float>(n);
    float scale = std::lerp(0.1f, 1.0f, t * t);
    kernel.push_back(v * scale * zero_one(rng));
  }
  return kernel;
}
```

| 点 | 説明 |
| --- | --- |
| 球の内側に一様 | 立方体からランダムに取り、球の外なら捨てる（棄却法）。長さは後で揃える |
| 原点に近いサンプルを多く | `scale = lerp(0.1, 1.0, t²)` で、近いサンプルを増やす |
| サンプル数 | 8〜16。少ないほど速いがノイズが増える |

サンプル ベクトルを画素ごとにランダムに回転します。4×4 画素のランダム ベクトルのテクスチャ（`float3`、0〜1 を −1〜1 にして使う）を、画面全体に繰り返し貼ります。

```hlsl
float3 random_vec = noise_tex.Sample(wrap_sampler, uv * screen_size / 4.0).xyz * 2.0 - 1.0;
float3 ray = reflect(kernel[i].xyz, random_vec);
```

`reflect` でランダム ベクトルを軸にサンプルを鏡映します。これで画素ごとにサンプルの向きが変わります。

## ④〜⑦ 判定とコード

```hlsl
float SSAO(float2 uv) {
  float z = LinearizeDepth(depth_tex.Sample(point_sampler, uv).r);
  float3 p = ViewPosition(uv, z);
  float3 random_vec = noise_tex.Sample(wrap_sampler, uv * screen_size / 4.0).xyz * 2.0 - 1.0;

  float occlusion = 0.0;
  for (int i = 0; i < kKernelSize; ++i) {
    float3 s = p + reflect(kernel[i].xyz, random_vec) * radius;

    float4 clip = mul(float4(s, 1.0), projection);
    float2 suv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;

    float scene_z = LinearizeDepth(depth_tex.SampleLevel(point_sampler, suv, 0).r);

    float range_check = saturate(radius / abs(z - scene_z));
    occlusion += (scene_z < s.z - bias ? 1.0 : 0.0) * range_check;
  }
  return 1.0 - occlusion / kKernelSize;
}
```

| 点 | 説明 |
| --- | --- |
| `scene_z < s.z − bias` | 画面から見える面（`scene_z`）が、サンプル点（`s.z`）より手前なら、s は面の奥 ＝ 遮られている |
| `bias` | 平らな面で自分自身を遮蔽物と判定する（自己遮蔽）のを防ぐ小さな値 |
| `range_check` | p から遠く離れた面（手前にある別の物）が、p を遮っていると誤判定するのを防ぐ。深度の差が大きいほど、効きを弱める |
| `SampleLevel` | ループの中でミップを選ぶ命令（勾配が使えないため） |
| ポイント サンプル | 深度は補間せずに読む（補間すると境界で嘘の深度ができる） |

## この方式の問題点

<!-- fig:sphere-vs-hemisphere:begin -->

<svg class="fig illust motion" data-fig="sphere-vs-hemisphere" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sphere-vs-hemisphere" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">平らな面で、球のサンプルは半分が面の中に入る（灰色になる）</text>
<circle cx="210" cy="190" r="100" fill="none" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="6 4"/>
<rect x="70" y="190" width="280" height="60" fill="#cbd5e1"/>
<line x1="70" y1="190" x2="350" y2="190" stroke="#1f2937" stroke-width="3"/>
<text x="210" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">球にサンプル（Crytek）</text>
<circle cx="174.77" cy="120.17" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></circle>
<circle cx="240.19" cy="104.49" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1214;0.1217;1.0000" values="0;0;1;1"/></circle>
<circle cx="217.18" cy="163.14" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;1.0000" values="0;0;1;1"/></circle>
<circle cx="121.6" cy="191.49" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="0;0;1;1"/></circle>
<circle cx="117.5" cy="176.73" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;1.0000" values="0;0;1;1"/></circle>
<circle cx="194.9" cy="255.37" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000" values="0;0;1;1"/></circle>
<circle cx="134.76" cy="134.65" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;1.0000" values="0;0;1;1"/></circle>
<circle cx="235.49" cy="279.54" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;1.0000" values="0;0;1;1"/></circle>
<circle cx="225.42" cy="169.34" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;1.0000" values="0;0;1;1"/></circle>
<circle cx="281.69" cy="147.92" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></circle>
<circle cx="171.7" cy="253.23" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="0;0;1;1"/></circle>
<circle cx="146.15" cy="206.32" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/></circle>
<circle cx="237.78" cy="164.48" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;1.0000" values="0;0;1;1"/></circle>
<circle cx="219.55" cy="102.56" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;1.0000" values="0;0;1;1"/></circle>
<circle cx="246.08" cy="175.52" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000" values="0;0;1;1"/></circle>
<circle cx="172.83" cy="207.11" r="6" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000" values="0;0;1;1"/></circle>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0</text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1214;0.1217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1214;0.1217;0.1562;0.1565;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;0.1910;0.1913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.2257;0.2261;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;0.2605;0.2609;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;0.2953;0.2957;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;0.3301;0.3304;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;0.3649;0.3652;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4344;0.4348;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;0.5040;0.5043;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;0.5388;0.5391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;0.5736;0.5739;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;0.6083;0.6087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="210" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000" values="0;0;1;1"/></text>
<circle cx="560" cy="190" r="100" fill="none" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="6 4"/>
<rect x="420" y="190" width="280" height="60" fill="#cbd5e1"/>
<line x1="420" y1="190" x2="700" y2="190" stroke="#1f2937" stroke-width="3"/>
<text x="560" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">半球にサンプル（法線を使う）</text>
<circle cx="524.77" cy="120.17" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></circle>
<circle cx="590.19" cy="104.49" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1214;0.1217;1.0000" values="0;0;1;1"/></circle>
<circle cx="567.18" cy="163.14" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;1.0000" values="0;0;1;1"/></circle>
<circle cx="471.6" cy="188.51" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;1.0000" values="0;0;1;1"/></circle>
<circle cx="467.5" cy="176.73" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;1.0000" values="0;0;1;1"/></circle>
<circle cx="544.9" cy="124.63" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;1.0000" values="0;0;1;1"/></circle>
<circle cx="484.76" cy="134.65" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;1.0000" values="0;0;1;1"/></circle>
<circle cx="585.49" cy="100.46" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;1.0000" values="0;0;1;1"/></circle>
<circle cx="575.42" cy="169.34" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;1.0000" values="0;0;1;1"/></circle>
<circle cx="631.69" cy="147.92" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></circle>
<circle cx="521.7" cy="126.77" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="0;0;1;1"/></circle>
<circle cx="496.15" cy="173.68" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/></circle>
<circle cx="587.78" cy="164.48" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;1.0000" values="0;0;1;1"/></circle>
<circle cx="569.55" cy="102.56" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;1.0000" values="0;0;1;1"/></circle>
<circle cx="596.08" cy="175.52" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;1.0000" values="0;0;1;1"/></circle>
<circle cx="522.83" cy="172.89" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000" values="0;0;1;1"/></circle>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0</text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1214;0.1217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1214;0.1217;0.1562;0.1565;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1562;0.1565;0.1910;0.1913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1910;0.1913;0.2257;0.2261;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2257;0.2261;0.2605;0.2609;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;0.2953;0.2957;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2953;0.2957;0.3301;0.3304;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;0.3649;0.3652;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3649;0.3652;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4344;0.4348;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;0.5040;0.5043;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5040;0.5043;0.5388;0.5391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5388;0.5391;0.5736;0.5739;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5736;0.5739;0.6083;0.6087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="335" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;1.0000" values="0;0;1;1"/></text>
<text x="210" y="365" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">面の中（赤）に入った数 / 16</text>
<text x="560" y="365" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">常に 0 / 16 → 平らな面は、遮蔽なし</text>
<text x="390" y="398" text-anchor="middle" style="font-size:13px;font-weight:500;fill:#1f2937">球では、何も遮るものがなくても、約半分が「遮蔽」と数えられる</text>
</svg>

<!-- fig:sphere-vs-hemisphere:end -->

### 1. 平らな面が灰色になる

<strong>球</strong>を使うので平らな面の上の点でもサンプルの約半分が面の下に入り、「遮られた」と数えられます。何も遮るものが無いのに、AO が 0.5 程度になり、全体が灰色に見えます。

| 対処 | 説明 |
| --- | --- |
| 0.5 を差し引いて伸ばす | `ao = saturate((ao − 0.5) × 2)` のように平面の値を 1 に補正する。簡易的な対処で凸の面は補正しすぎになる |
| 半球に変える | 法線を使い、面の上側だけにサンプルを置く（[Hemisphere SSAO](ssao-hemisphere.md)） |

### 2. 法線が無いので、角の向きを区別できない

法線が無いため、凸の角（外側）と凹の角（内側）を区別できません。凸の縁にも暗い輪郭（ハロー）が出やすくなります。

### 3. ハロー

手前の物体の縁に背景が暗くなる輪が出ます。深度の差が大きい境界で、背景側の点が手前の物に遮られていると判定されるためです。`range_check` で弱められますが、完全には消えません（[アーティファクト](artifacts/index.md)）。

### 4. ノイズとバンディング

サンプル数が少ないので、ノイズか縞模様が出ます。4×4 のランダム回転 ＋ 4×4 のぼかしで消すのが定番ですが、ぼかしが物体の境界をにじませるので、深度を考慮したバイラテラル ブラーが必要です（[フィルタ](filtering/index.md)）。

## 歴史的な位置づけ

この方式は 2007 年に CryEngine 2（『Crysis』）で登場し、SIGGRAPH 2007 の講演で公開されました。それまでの AO はモデルへの焼き込みか事前計算でしたが、事前計算なしで動的なシーンに AO を付けられること、深度バッファだけで動くこと（G-Buffer に依存しない）が画期的でした。「深度から位置を復元し、近傍をサンプルする」という発想は、以降のすべての SSAO 系の基礎になりました。

そして、この方式の欠点を一つずつ直す形で、後の方式が生まれました。球を半球にする（法線の利用）、式を理論から導く（Alchemy）、地平線を直接扱う（HBAO）、深度のミップで高速化する（SAO）、コサイン重みを正確に扱う（GTAO）という順です。この順に読むと、それぞれの方式が「何を直したのか」が分かりやすくなります。

## よくあるミス

??? failure "球を使い、平らな面が灰色になる"
    法線を使って<strong>半球</strong>にします。または、0.5 を補正します。

??? failure "深度を線形補間して読み、境界で嘘の深度が出る"
    ポイント サンプリングで読みます。

??? failure "遠くの別の物体が、手前の面を暗くする"
    `range_check`（深度差による弱め）を入れます。

??? failure "同じランダム パターンを、全画素に使い、縞が出る"
    画素ごとにサンプルを回転します（4×4 のノイズ テクスチャ）。

??? failure "`bias` が小さすぎて、平らな面に縞が出る"
    `bias` を少し大きくします（0.01〜0.05 程度）。大きすぎると接地の暗さが消えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Crytek SSAO ＝ <strong>深度バッファだけで、球のサンプルを画面に投影し、面の奥にあれば遮られた、と数える</strong>
    - [x] 深度から位置を復元（ビュー空間）。ポイント サンプリングで深度を読む
    - [x] 範囲チェックとバイアスで、誤判定を減らす
    - [x] 球のため、平らな面が灰色になるのが最大の弱点 → 半球にする
    - [x] ランダム回転＋ぼかしが前提

## 参考

- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Filion, McNaughton, "StarCraft II: Effects & Techniques", SIGGRAPH 2008, Advances in Real-Time Rendering in 3D Graphics and Games（深度バッファによる、SSAO）
- Kajalin, "Screen Space Ambient Occlusion", ShaderX7, 2009
- de Vries, "SSAO", LearnOpenGL（半球カーネル・ノイズ・バイアス・範囲チェックの、実装解説）

## 関連ページ

- [Ambient Occlusion (AO)](index.md)
- [AO Theory](theory/index.md)
- [Hemisphere SSAO](ssao-hemisphere.md)
- [AO Filtering](filtering/index.md)
- [AO Artifacts](artifacts/index.md)
- [投影（プロジェクション）](../../3d/projection.md)
