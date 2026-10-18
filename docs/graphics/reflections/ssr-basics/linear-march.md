---
title: Linear Marching
tags:
  - 描画
---

# Linear Marching

**SSR の中心は、「反射レイを画面上で進めて、深度と比べる」処理**です。**一定の歩幅で進めるのが「線形マーチ」**で、**歩幅が大きいと、薄い物を飛び越え、小さいと、遅くなります**。**当たりが見つかった後は、二分探索で精密化**すると、**少ないステップでも、きれいに当たります**。このページでは、**レイの進め方・歩幅の決め方・当たりの精密化**を説明します。

!!! tip "ポイント"
    - **レイを画面空間（2D）で進め、各点でレイの深度とバッファの深度を比べる**。
    - **レイの深度 ＞ バッファの深度になったら、当たり候補**。
    - **歩幅が大きいと、薄い物を飛び越える**。**小さいと、ステップ数が増える**。
    - **当たり候補の前後で二分探索すると、少ないステップで、精密になる**。
    - **より良いやり方は、Hi-Z トレース**（[階層 Z](../ssr-hiz.md)）。

## Advancing the Ray {#レイの進め方}
### Method 1: Linear March in View Space {#方法-1ビュー空間の線形マーチ}

**ビュー空間**で**一定の長さ**ずつレイを進め、**各点を画面に投影**して深度を比べます。

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

### Method 2: Screen-Space DDA (Recommended) {#方法-2画面空間の-dda推奨}

**画面上で、1 ピクセルずつ**進みます。**全ての画素を、1 回ずつ確認**でき、**取りこぼしがなく**、**無駄もありません**。McGuire と Mara の方法（「Efficient GPU Screen-Space Ray Tracing」、JCGT 2014）が、標準です。

**透視投影では画面上の直線がビュー空間の直線に対応します**。ただし、**奥行きの補間**は、<strong>`1/z`（または `Q/w`）</strong>で行う必要があります（透視補正）。

| 量 | 補間方法 |
| --- | --- |
| <strong>画面座標 (x, y)</strong> | **線形**（DDA で、1 ピクセルずつ） |
| **`k = 1/w`**（`w` ＝ ビュー空間の `z`） | **線形** |
| **`Q = P_view × k`** | **線形** |
| **レイの奥行き `z`** | `z = Q.z / k` |


この「`1/z` が画面上で線形」という性質を使うことが、McGuire と Mara（2014）の手法の中核です。奥行きを画面上の位置で直接補間すると、レイが斜めに傾いたときに、奥行きが大きくずれて、当たり判定がおかしくなります。

この「`1/z` が画面上で線形」という性質を使うことが、McGuire と Mara（2014）の手法の中核です。奥行きを画面上の位置で直接補間すると、レイが斜めに傾いたときに、奥行きが大きくずれて、当たり判定がおかしくなります。

```hlsl
bool TraceSSR(float3 origin_vs, float3 dir_vs, float2 jitter,
              out float2 hit_pixel, out float3 hit_vs) {
  float ray_length = (origin_vs.z + dir_vs.z * max_distance < near_z)
      ? (near_z - origin_vs.z) / dir_vs.z : max_distance;
  float3 end_vs = origin_vs + dir_vs * ray_length;

  float4 h0 = mul(float4(origin_vs, 1.0), projection);
  float4 h1 = mul(float4(end_vs, 1.0), projection);
  float k0 = 1.0 / h0.w;
  float k1 = 1.0 / h1.w;
  float3 q0 = origin_vs * k0;
  float3 q1 = end_vs * k1;
  float2 p0 = (h0.xy * k0 * float2(0.5, -0.5) + 0.5) * screen_size;
  float2 p1 = (h1.xy * k1 * float2(0.5, -0.5) + 0.5) * screen_size;

  float2 delta = p1 - p0;
  bool permute = abs(delta.x) < abs(delta.y);
  if (permute) {
    delta = delta.yx; p0 = p0.yx; p1 = p1.yx;
  }

  float step_dir = sign(delta.x);
  float inv_dx = step_dir / delta.x;
  float2 dp = float2(step_dir, delta.y * inv_dx) * stride;
  float3 dq = (q1 - q0) * inv_dx * stride;
  float dk = (k1 - k0) * inv_dx * stride;

  float2 p = p0 + dp * jitter.x;
  float3 q = q0 + dq * jitter.x;
  float k = k0 + dk * jitter.x;

  float prev_z_max = origin_vs.z;
  for (int i = 0; i < kMaxSteps && p.x * step_dir <= p1.x * step_dir; ++i) {
    p += dp; q += dq; k += dk;

    float ray_z_min = prev_z_max;
    float ray_z_max = (dq.z * 0.5 + q.z) / (dk * 0.5 + k);
    prev_z_max = ray_z_max;
    if (ray_z_min > ray_z_max) { float t = ray_z_min; ray_z_min = ray_z_max; ray_z_max = t; }

    hit_pixel = permute ? p.yx : p;
    float scene_z = LinearDepth(hit_pixel);

    if (ray_z_max >= scene_z && ray_z_min <= scene_z + thickness) {
      hit_vs = q * (1.0 / k);
      return true;
    }
  }
  return false;
}
```

| 点 | 説明 |
| --- | --- |
| **近クリップ面の処理** | レイが**カメラの後ろ**（`z < near`）に出ないよう、**近クリップ面で切る** |
| **`permute`** | **x と y のうち、変化が大きい方**を主軸にする（DDA の歩幅を 1 にするため） |
| **`stride`** | **歩幅**（ピクセル）。1 より大きくすると速いが、**薄い物を飛び越す**。**ジッター**で縞を消す |
| **`ray_z_min/max`** | **1 ステップの間のレイの奥行きの範囲**。画素の深度との**区間の重なり**で判定 |
| **`ray_z_max >= scene_z`** | レイが面の**奥**に達した（左手系・+Z が前なので奥ほど z が大きい） |
| **`ray_z_min <= scene_z + thickness`** | レイが面から**厚みの範囲内**にある（はるか後ろではない） |

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

## Refining the Hit {#当たりの精密化}
**歩幅が 1 より大きい**と、**当たりの位置が粗く**（歩幅分のずれ）なります。**当たった後**に**区間を二分探索**で精密化します。

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

**2〜5 回**の二分探索で、**歩幅の誤差がほぼ無くなります**。

## Common Mistakes {#よくあるミス}

??? failure "薄い柵や線が、反射に映らない"
    **歩幅を小さく**するか、**Hi-Z トレース**にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **画面空間でレイを進め、深度を比べる**
    - [x] **当たりを見つけたら、二分探索で精密化**

## References {#参考}

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [SSR Basics](index.md)
- [厚み](thickness.md)
- [階層 Z（Hi-Z）](../ssr-hiz.md)
