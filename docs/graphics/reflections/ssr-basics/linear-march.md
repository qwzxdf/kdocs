---
title: Linear Marching
tags:
  - 描画
---

# Linear Marching

<strong>SSR の中心は、「反射レイを画面上で進めて、深度と比べる」処理</strong>です。<strong>一定の歩幅で進めるのが「線形マーチ」</strong>で、歩幅が大きいと、薄い物を飛び越え、小さいと、遅くなります。当たりが見つかった後は、二分探索で精密化すると、少ないステップでも、きれいに当たります。このページでは、レイの進め方・歩幅の決め方・当たりの精密化を説明します。

!!! tip "ポイント"
    - レイを画面空間（2D）で進め、各点でレイの深度とバッファの深度を比べる。
    - レイの深度 ＞ バッファの深度になったら、当たり候補。
    - 歩幅が大きいと、薄い物を飛び越える。小さいと、ステップ数が増える。
    - 当たり候補の前後で二分探索すると、少ないステップで、精密になる。
    - より良いやり方は、Hi-Z トレース（[Hi-Z SSR](../ssr-hiz.md)）。

## レイの進め方
### 方法 1：ビュー空間の線形マーチ

<strong>ビュー空間</strong>で<strong>一定の長さ</strong>ずつレイを進め、各点を画面に投影して深度を比べます。

```hlsl
float3 pos = origin_vs;
for (int i = 0; i < kMaxSteps; ++i) {
  pos += dir_vs * step_length;
  float4 clip = mul(float4(pos, 1.0), projection);
  float2 uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
  float scene_z = LinearDepth(uv);
  if (pos.z > scene_z && pos.z < scene_z + thickness) { hit = true; break; }
}
```

線形マーチには、3 つの課題があります。第 1 は、ステップ長の選択です。長いと薄い物を飛び越し、短いとステップ数が増えて重くなります。第 2 は、画面上の歩幅が不均一なことです。ビュー空間で一定の長さは、画面では遠いほど短く、近いほど長くなり、無駄や取りこぼしを生みます。第 3 は、画面外に出た後も進み続けることで、これは無駄な計算になります。

### 方法 2：画面空間の DDA（推奨）

<strong>画面上で、1 ピクセルずつ</strong>進みます。<strong>全ての画素を、1 回ずつ確認</strong>でき、取りこぼしがなく、無駄もありません。McGuire と Mara の方法（「Efficient GPU Screen-Space Ray Tracing」、JCGT 2014）が、標準です。

<strong>透視投影では画面上の直線がビュー空間の直線に対応します</strong>。ただし、<strong>奥行きの補間</strong>は、<strong>`1/z`（または `Q/w`）</strong>で行う必要があります（透視補正）。

| 量 | 補間方法 |
| --- | --- |
| <strong>画面座標 (x, y)</strong> | 線形（DDA で、1 ピクセルずつ） |
| `k = 1/w`（`w` ＝ ビュー空間の `z`） | 線形 |
| `Q = P_view × k` | 線形 |
| レイの奥行き `z` | `z = Q.z / k` |


この「`1/z` が画面上で線形」という性質を使うことが、McGuire と Mara（2014）の手法の中核です。奥行きを画面上の位置で直接補間すると、レイが斜めに傾いたときに、奥行きが大きくずれて、当たり判定がおかしくなります。

この「`1/z` が画面上で線形」という性質を使うことが、McGuire と Mara（2014）の手法の中核です。奥行きを画面上の位置で直接補間すると、レイが斜めに傾いたときに、奥行きが大きくずれて、当たり判定がおかしくなります。

```hlsl
bool TraceSSR(float3 origin_vs, float3 dir_vs, float2 jitter,
              out float2 hit_pixel, out float3 hit_vs) {
  float ray_length = (origin_vs.z + dir_vs.z * max_distance < near_z)
      ? (near_z - origin_vs.z) / dir_vs.z : max_distance;
  float3 end_vs = origin_vs + dir_vs * ray_length;
```

レイを、画面の線分にするための、準備です。レイが、近クリップ面より手前（カメラの後ろ）に、出る場合は、近クリップ面で、切ります。そうしないと、投影した終点が、画面の外の、おかしな位置になります。

```hlsl
  float4 h0 = mul(float4(origin_vs, 1.0), projection);
  float4 h1 = mul(float4(end_vs, 1.0), projection);
  float k0 = 1.0 / h0.w;
  float k1 = 1.0 / h1.w;
  float3 q0 = origin_vs * k0;
  float3 q1 = end_vs * k1;
  float2 p0 = (h0.xy * k0 * float2(0.5, -0.5) + 0.5) * screen_size;
  float2 p1 = (h1.xy * k1 * float2(0.5, -0.5) + 0.5) * screen_size;
```

始点と終点を、クリップ空間へ、投影します。`k = 1/w` と、`q = 位置 × k` を、持っておくのが、要点です。この 2 つは、画面空間で、線形に、補間できるので、透視補正を、正しく、行えます。`p0`、`p1` は、画素単位の、画面座標です。

```hlsl
  float2 delta = p1 - p0;
  bool permute = abs(delta.x) < abs(delta.y);
  if (permute) {
    delta = delta.yx; p0 = p0.yx; p1 = p1.yx;
  }
```

線分が、縦に長いとき（`|dy| > |dx|`）は、x と y を、入れ替えます（`permute`）。こうすると、常に、x を 1 画素ずつ進める形にでき、ループが、単純になります（DDA の、準備です）。

```hlsl
  float step_dir = sign(delta.x);
  float inv_dx = step_dir / delta.x;
  float2 dp = float2(step_dir, delta.y * inv_dx) * stride;
  float3 dq = (q1 - q0) * inv_dx * stride;
  float dk = (k1 - k0) * inv_dx * stride;
```

x を、1 画素進めるごとの、y・`q`・`k` の増分を、求めます。`stride` は、何画素ずつ進むか（1 なら、全画素）で、大きくすると、速いが、取りこぼします。

```hlsl
  float2 p = p0 + dp * jitter.x;
  float3 q = q0 + dq * jitter.x;
  float k = k0 + dk * jitter.x;
```

開始位置を、ジッターで、少しずらします。画素ごとに、ずらし方を、変えると、規則的な、縞が、ノイズに、変わり、TAA や、ぼかしで、消せます。

```hlsl
  float prev_z_max = origin_vs.z;
  for (int i = 0; i < kMaxSteps && p.x * step_dir <= p1.x * step_dir; ++i) {
    p += dp; q += dq; k += dk;

    float ray_z_min = prev_z_max;
    float ray_z_max = (dq.z * 0.5 + q.z) / (dk * 0.5 + k);
    prev_z_max = ray_z_max;
    if (ray_z_min > ray_z_max) { float t = ray_z_min; ray_z_min = ray_z_max; ray_z_max = t; }
```

1 歩ごとに、レイの、この区間の、深度の範囲 `[ray_z_min, ray_z_max]` を、求めます。区間の終端の深度は、`q.z / k` で、取り出します。前の区間の終端を、今の区間の始端にして、つなぎ目の、隙間を、なくします。

```hlsl
    hit_pixel = permute ? p.yx : p;
    float scene_z = LinearDepth(hit_pixel);

    if (ray_z_max >= scene_z && ray_z_min <= scene_z + thickness) {
      hit_vs = q * (1.0 / k);
      return true;
    }
  }
```

この画素の、実際の深度 `scene_z` と、レイの区間を、比べます。レイの区間が、`[scene_z, scene_z + thickness]` と、重なれば、当たりです。当たったら、`q / k` で、ビュー空間の位置に、戻して、返します。ステップを使い切るか、線分の終点に、達したら、外れです（[Thickness](thickness.md)）。

```hlsl
  return false;
}
```

| 点 | 説明 |
| --- | --- |
| 近クリップ面の処理 | レイがカメラの後ろ（`z < near`）に出ないよう、近クリップ面で切る |
| `permute` | x と y のうち、変化が大きい方を主軸にする（DDA の歩幅を 1 にするため） |
| `stride` | 歩幅（ピクセル）。1 より大きくすると速いが、薄い物を飛び越す。ジッターで縞を消す |
| `ray_z_min/max` | 1 ステップの間のレイの奥行きの範囲。画素の深度との区間の重なりで判定 |
| `ray_z_max >= scene_z` | レイが面の奥に達した（左手系・+Z が前なので奥ほど z が大きい） |
| `ray_z_min <= scene_z + thickness` | レイが面から厚みの範囲内にある（はるか後ろではない） |

<!-- fig:ssr-march:begin -->

<svg class="fig illust motion" data-fig="ssr-march" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ssr-march" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">SSR:反射した向きへ少しずつ進み、深度バッファの物にぶつかるまで探す</text>
<line x1="40" y1="270" x2="740" y2="270" stroke="#1f2937" stroke-width="4"/>
<rect x="40" y="270" width="700" height="50" fill="#dbeafe" opacity="0.6"/>
<text x="46" y="300" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">鏡のような床</text>
<rect x="500" y="150" width="80" height="120" fill="#e5484d" stroke="#7f1d1d" stroke-width="2"/>
<circle cx="70" cy="170" r="9" fill="#1f2937"/>
<text x="60" y="154" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">カメラ</text>
<line x1="70" y1="170" x2="70" y2="170" stroke="#1f2937" stroke-width="2.5" stroke-dasharray="6 4"><animate attributeName="x2" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.0455;0.1182;1.0000" values="70;70;300;300"/><animate attributeName="y2" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.0455;0.1182;1.0000" values="170;170;270;270"/></line>
<circle cx="300" cy="270" r="6" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="280" y="296" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">この床のピクセル</text>
<line x1="300" y1="270" x2="323.84" y2="259.63" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1451;0.1455;1.0000" values="0;0;1;1"/></line>
<circle cx="323.84" cy="259.63" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1451;0.1455;1.0000" values="0;0;1;1"/></circle>
<line x1="323.84" y1="259.63" x2="347.69" y2="249.27" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1833;0.1836;1.0000" values="0;0;1;1"/></line>
<circle cx="347.69" cy="249.27" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1833;0.1836;1.0000" values="0;0;1;1"/></circle>
<line x1="347.69" y1="249.27" x2="371.53" y2="238.9" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2215;0.2218;1.0000" values="0;0;1;1"/></line>
<circle cx="371.53" cy="238.9" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2215;0.2218;1.0000" values="0;0;1;1"/></circle>
<line x1="371.53" y1="238.9" x2="395.38" y2="228.53" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2596;0.2600;1.0000" values="0;0;1;1"/></line>
<circle cx="395.38" cy="228.53" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2596;0.2600;1.0000" values="0;0;1;1"/></circle>
<line x1="395.38" y1="228.53" x2="419.22" y2="218.17" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2978;0.2982;1.0000" values="0;0;1;1"/></line>
<circle cx="419.22" cy="218.17" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2978;0.2982;1.0000" values="0;0;1;1"/></circle>
<line x1="419.22" y1="218.17" x2="443.06" y2="207.8" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3360;0.3364;1.0000" values="0;0;1;1"/></line>
<circle cx="443.06" cy="207.8" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3360;0.3364;1.0000" values="0;0;1;1"/></circle>
<line x1="443.06" y1="207.8" x2="466.91" y2="197.43" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3742;0.3745;1.0000" values="0;0;1;1"/></line>
<circle cx="466.91" cy="197.43" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3742;0.3745;1.0000" values="0;0;1;1"/></circle>
<line x1="466.91" y1="197.43" x2="490.75" y2="187.06" stroke="#2ea043" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4124;0.4127;1.0000" values="0;0;1;1"/></line>
<circle cx="490.75" cy="187.06" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4124;0.4127;1.0000" values="0;0;1;1"/></circle>
<line x1="490.75" y1="187.06" x2="514.59" y2="176.7" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4505;0.4509;1.0000" values="0;0;1;1"/></line>
<circle cx="514.59" cy="176.7" r="9" fill="#e5484d" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4505;0.4509;1.0000" values="0;0;1;1"/></circle>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 1:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1451;0.1455;0.1833;0.1836;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 2:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1833;0.1836;0.2215;0.2218;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 3:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2215;0.2218;0.2596;0.2600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 4:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2596;0.2600;0.2978;0.2982;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 5:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.2978;0.2982;0.3360;0.3364;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 6:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3360;0.3364;0.3742;0.3745;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 7:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.3742;0.3745;0.4124;0.4127;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 8:まだ手前（何もない）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4124;0.4127;0.4505;0.4509;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ステップ 9:物にぶつかった！<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4505;0.4509;1.0000;1.0000" values="0;0;1;1;0"/></text>
<rect x="290" y="276" width="20" height="12" fill="#e5484d" stroke="#1f2937" opacity="0"><animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.5142;0.5145;1.0000" values="0;0;1;1"/></rect>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">① カメラから床のピクセルへ視線が届く<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1360;0.1364;1.0000" values="1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">② 反射した向きへ、一定の間隔で進みながら、物があるか調べる<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.1360;0.1364;0.4869;0.4873;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">③ ぶつかった所の色を、床に映す（床のピクセルが赤くなる）<animate attributeName="opacity" dur="11s" repeatCount="indefinite" keyTimes="0.0000;0.4869;0.4873;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ssr-march:end -->

## 当たりの精密化
<strong>歩幅が 1 より大きい</strong>と、<strong>当たりの位置が粗く</strong>（歩幅分のずれ）なります。当たった後に区間を二分探索で精密化します。

```hlsl
float2 RefineHit(float2 p_before, float2 p_after, int steps) {
  float2 lo = p_before;
  float2 hi = p_after;
  for (int i = 0; i < steps; ++i) {
    float2 mid = (lo + hi) * 0.5;
    if (RayIsBehindSurface(mid)) hi = mid; else lo = mid;
  }
  return hi;
}
```

<strong>2〜5 回</strong>の二分探索で、<strong>歩幅の誤差がほぼ無くなります</strong>。

## 線形マーチ：画面空間で、レイを、辿る

<strong>最も、単純な、SSR</strong> は、<strong>反射レイを、画面空間で、一定の歩幅で、辿り</strong>、各点で、深度バッファと、比べる方法です（線形マーチ）。当たりを、見つけるまで、繰り返します。

```text
画面上の、線分（始点 → 終点）を、N 区間に、分ける。各区間で:
   レイ上の点の、深度 と、その画素の、深度バッファの値 を、比べる
   レイの方が、奥（面の、裏）に、入った → 交差
```

## 実装

```hlsl
// 線形マーチ: 画面空間で、レイを、一定の歩幅で、進める。戻り値: 当たった uv（当たらなければ、-1）。
float2 LinearMarch(float3 origin_vs, float3 dir_vs, float2 pixel) {
  // 始点・終点を、クリップ空間→ uv へ（前のページと同じ）。
  float3 end_vs = origin_vs + dir_vs * g_max_distance;
  float4 s = mul(float4(origin_vs, 1.0), g_proj);
  float4 e = mul(float4(end_vs, 1.0), g_proj);
  float2 start_uv = s.xy / s.w * float2(0.5, -0.5) + 0.5;
  float2 end_uv = e.xy / e.w * float2(0.5, -0.5) + 0.5;
  float start_inv_w = 1.0 / s.w;                                          // 1/w（透視補正のため）
  float end_inv_w = 1.0 / e.w;
```

<strong>始点と終点</strong>を、<strong>uv に、投影</strong>します。`1/w` を、覚えておくのは、透視投影の、補間（画面空間で、直線的に、補間しても、奥行きは、直線的でない）を、正しく、行うためです。

```hlsl
  const int kSteps = 32;
  float jitter = InterleavedGradientNoise(pixel) * 0.5;                   // 開始位置を、ずらして、縞を、減らす
  for (int i = 1; i <= kSteps; ++i) {
    float t = (i + jitter) / kSteps;                                        // 線分上の、位置（0〜1）。画面空間で、等間隔
    float2 uv = lerp(start_uv, end_uv, t);                                  // 画面上の位置
    if (any(uv < 0.0) || any(uv > 1.0)) return -1.0;                        // 画面の外に出た → 当たらない
```

<strong>画面空間で、等間隔</strong>に、進みます。<strong>画面の外</strong>に、出たら、情報が、無いので、打ち切ります。

```hlsl
    // レイ上の点の、深度（ビュー空間の距離）。1/w を、画面空間で線形補間して、逆数を取る（透視補正）。
    float inv_w = lerp(start_inv_w, end_inv_w, t);
    float ray_depth = 1.0 / inv_w;                                          // レイ上の点の、ビュー空間での、深度（正の距離）

    float scene_depth = LinearizeDepth(g_depth.SampleLevel(g_point_clamp, uv, 0));   // その画素の、実際の深度

    float diff = ray_depth - scene_depth;
    if (diff > 0.0 && diff < g_thickness) return uv;                        // レイが、面の「裏」に入った（厚み以内）→ 当たり
  }
  return -1.0;                                                              // 当たらなかった
}
```

<strong>レイ上の、点の、深度</strong>は、<strong>`1 / w` を、画面空間で、線形補間し</strong>、その逆数を、取ると、正しい値です（透視補正）。画面の深度と、比べ、レイが、面より、奥に、入って、かつ、厚み以内なら、当たりです。

## 線形マーチの、問題

### ① 細い物を、すり抜ける

<strong>歩幅が、粗い</strong>と、<strong>細い物</strong>（フェンス、手すり）の、上を、飛び越えて、当たりを、見逃します。

```text
ステップ:  ●     ●     ●     ●     ●          ← 粗い歩幅
                  ┃ 細い物
                 ●が、物の、手前と奥に、またがって、当たりを、検出できない（厚みの範囲を、飛び越える）
```

| 対策 | 内容 |
| --- | --- |
| 歩幅を、細かく | ステップ数を、増やす。重い |
| 厚みを、大きく | すり抜けは、減るが、偽の当たり（物の、手前の面に、誤って当たる）が、増える（[Thickness](thickness.md)） |
| 二分探索で、洗練 | 当たりを、見つけた後、直前の、ステップと、の間で、二分探索し、正確な、交点を、求める |
| Hi-Z | 階層的な深度で、空の部分を、大きく、飛ばし、細かい所は、細かく（[Hi-Z SSR](../ssr-hiz.md)） |

### ② 二分探索で、交点を、洗練する

<strong>当たった、ステップ</strong>の、<strong>1 つ前</strong>（まだ、当たっていない）と、当たったステップの、間に、真の、交点が、あります。二分探索で、絞り込みます。

```hlsl
// 当たった t_hit と、その 1 つ前 t_prev の間を、二分探索して、正確な交点を求める。
float lo = t_prev, hi = t_hit;
for (int k = 0; k < 6; ++k) {                                               // 6 回で、歩幅の 1/64 の精度
  float mid = 0.5 * (lo + hi);
  float2 uv_mid = lerp(start_uv, end_uv, mid);
  float ray_d = 1.0 / lerp(start_inv_w, end_inv_w, mid);
  float scene_d = LinearizeDepth(g_depth.SampleLevel(g_point_clamp, uv_mid, 0));
  if (ray_d > scene_d) hi = mid; else lo = mid;                              // レイが、面の裏なら、手前へ。そうでなければ、奥へ
}
float2 hit_uv = lerp(start_uv, end_uv, hi);
```

<strong>6 回の、二分探索</strong>で、<strong>歩幅の、1/64</strong>の、精度に、なります。粗い歩幅でも、正確な、交点が、得られ、反射が、なめらかになります。

### ③ 画面空間で、等間隔でも、3D では、不均等

<strong>画面空間で、等間隔</strong>に、進むと、<strong>カメラに、近い所</strong>では、3D の歩幅が、小さく、遠い所では、大きくなります。遠くの物は、粗い歩幅で、すり抜けやすくなります。

| 方式 | 内容 |
| --- | --- |
| 画面空間で、等間隔 | 実装が、簡単。遠くが、粗い |
| 3D 空間で、等間隔 | 歩幅が、3D で、一定。画面上の、歩幅が、不均等（近くは、画素を、飛ばす） |
| DDA（デジタル微分解析器）で、1 画素ずつ | 画面上の、すべての画素を、1 つずつ、辿る。取りこぼしが、無い。線が、長いと、重い |

<strong>DDA</strong> は、<strong>線分が、通る、すべての画素</strong>を、辿るので、取りこぼしが、ありません（McGuire と Mara、2014）。画面上の、線分が、長いと、ステップが、非常に、多くなるので、最大のステップ数を、制限します。

## 速さの、目安

| 設定 | コスト |
| --- | --- |
| 線形マーチ 16 ステップ + 二分探索 | 約 0.5 ms（1080p、半解像度） |
| 線形マーチ 32 ステップ + 二分探索 | 約 1 ms |
| Hi-Z（[Hi-Z SSR](../ssr-hiz.md)） | 同品質で、数倍速い |

## よくあるミス

??? failure "薄い柵や線が、反射に映らない"
    <strong>歩幅を小さく</strong>するか、<strong>Hi-Z トレース</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 画面空間でレイを進め、深度を比べる
    - [x] 当たりを見つけたら、二分探索で精密化

## 参考

- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014
- Stachowiak, Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Frostbite の SSR）
- Uludag, "Hi-Z Screen-Space Cone-Traced Reflections", GPU Pro 5, 2014
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）

## 関連ページ

- [SSR Basics](index.md)
- [Thickness](thickness.md)
- [Hi-Z SSR](../ssr-hiz.md)
