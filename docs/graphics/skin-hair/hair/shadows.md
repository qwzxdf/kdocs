---
title: Hair Shadows
tags:
  - 描画
---

# Hair Shadows

髪の立体感は、**自己影**で決まります。髪の束の内側は、外側の髪の毛に光を遮られて暗く、外側は明るい。この明暗の差がなければ、髪は平らなヘルメットのように見えます。ところが、髪は**細くて半透明**なので、ふつうのシャドウ マップでは、うまく影が付きません。シャドウ マップは「ある深さで光が完全に遮られるか」を 0 か 1 で決めますが、髪の影は「通り抜ける髪の毛の本数に応じて、**少しずつ暗くなる**」ものだからです。このページでは、髪の影の問題と、解決する **Deep Opacity Maps**（Yuksel と Keyser、2008）を説明します。

!!! tip "ポイント"
    - 髪の影は<strong>連続的に暗くなる</strong>（通り抜けた髪の本数に比例）。**0/1 のシャドウ マップでは足りない**。
    - **Opacity Shadow Maps**：光の方向に**層（スライス）**を切って、層ごとの**不透明度の累積**を保存。**層が多く必要でメモリが重い**。
    - **Deep Opacity Maps**：**髪の最初の面から数えて層を切る**ことで、**少ない層（3〜4）**で済む。
    - **影の濃さ** ＝ 光の方向に通り抜ける**不透明度の合計**から、**Beer の法則**で透過率を求める。
    - ストランドは<strong>ボリューム（密度の 3D 格子）</strong>で影を付ける方法もある。

## Why an Ordinary Shadow Map Is Not Enough {#普通のシャドウ-マップではなぜ足りないか}

通常のシャドウ マップは、光から見た「最も手前の面の深度」を保存します。髪にそのまま使うと、2 つの問題が出ます。

1. **髪が細く、半透明**なので、画素ごとの手前の面の深度が、ほんの 1 本の髪の毛の深度になってしまいます。その後ろにある多数の髪は、すべて「影の中」と判定され、**影が 0 か 1 の硬い値**になります。髪の層を何枚も通り抜けて徐々に暗くなる様子は、出ません。
2. シャドウ マップの解像度は有限なので、**髪の毛 1 本が、シャドウ マップの 1 テクセルより細い**ことが多く、ちらつきやノイズが出ます。

髪の影は、本質的に**ボリュームの現象**です。光が、髪が詰まった空間を進むとき、その進んだ距離に応じて、減衰します。これは、煙や雲と同じ考え方です。

## Opacity Shadow Maps

最初の解決策は、Kim と Neumann の **Opacity Shadow Maps**（2001）です。考え方は、光の方向に、髪の空間を**一定間隔の層（スライス）**に切り、層ごとに「その層より手前にある髪の不透明度の合計」を、画像に保存することです。

手順は、光から見て、層の位置を手前から奥へ進めながら、各層の位置までに積み重なった髪の不透明度を、順にレンダリングします。層が N 枚なら、N 枚の画像ができます。影を付ける点では、その点が属する層の前後の 2 枚を補間して、その点の手前にある不透明度の合計を得ます。

欠点は、**層を細かく取る必要がある**ことです。層の間隔が粗いと、層ごとの切れ目が帯（バンディング）として見えます。きれいな結果には数十枚の層が要り、メモリと描画のコストが大きくなります。

<!-- fig:deep-opacity:begin -->

<svg class="fig illust motion" data-fig="deep-opacity" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-deep-opacity" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">層を「髪の最初の面」から切ると、少ない層で足りる</text>
<rect x="50" y="90" width="320" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="210" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">固定の層（Opacity Shadow Maps）</text>
<rect x="410" y="90" width="320" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="570" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">髪の面から切る層（Deep Opacity Maps）</text>
<text x="56" y="54" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">↓ 光の向き</text>
<line x1="50" y1="120" x2="370" y2="120" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="50" y1="156" x2="370" y2="156" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="50" y1="192" x2="370" y2="192" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="50" y1="228" x2="370" y2="228" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="50" y1="264" x2="370" y2="264" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="50" y1="300" x2="370" y2="300" stroke="#e2e8f0" stroke-width="1.5"/>
<path d="M50,240.0 L58,244.46 L66,248.81 L74,252.93 L82,256.72 L90,260.09 L98,262.94 L106,265.2 L114,266.82 L122,267.76 L130,267.99 L138,267.5 L146,266.31 L154,264.45 L162,261.96 L170,258.91 L178,255.38 L186,251.46 L194,247.24 L202,242.84 L210,238.37 L218,233.93 L226,229.66 L234,225.64 L242,222.0 L250,218.81 L258,216.16 L266,214.13 L274,212.75 L282,212.07 L290,212.11 L298,212.85 L306,214.29 L314,216.39 L322,219.09 L330,222.32 L338,226.01 L346,230.05 L354,234.35 L362,238.79 L370,243.26 L370,280 L50,280 Z" fill="#7c3aed" fill-opacity="0.28"/>
<path d="M50,240.0 L58,244.46 L66,248.81 L74,252.93 L82,256.72 L90,260.09 L98,262.94 L106,265.2 L114,266.82 L122,267.76 L130,267.99 L138,267.5 L146,266.31 L154,264.45 L162,261.96 L170,258.91 L178,255.38 L186,251.46 L194,247.24 L202,242.84 L210,238.37 L218,233.93 L226,229.66 L234,225.64 L242,222.0 L250,218.81 L258,216.16 L266,214.13 L274,212.75 L282,212.07 L290,212.11 L298,212.85 L306,214.29 L314,216.39 L322,219.09 L330,222.32 L338,226.01 L346,230.05 L354,234.35 L362,238.79 L370,243.26" fill="none" stroke="#7c3aed" stroke-width="3"/>
<path d="M410,240.0 L418,244.46 L426,248.81 L434,252.93 L442,256.72 L450,260.09 L458,262.94 L466,265.2 L474,266.82 L482,267.76 L490,267.99 L498,267.5 L506,266.31 L514,264.45 L522,261.96 L530,258.91 L538,255.38 L546,251.46 L554,247.24 L562,242.84 L570,238.37 L578,233.93 L586,229.66 L594,225.64 L602,222.0 L610,218.81 L618,216.16 L626,214.13 L634,212.75 L642,212.07 L650,212.11 L658,212.85 L666,214.29 L674,216.39 L682,219.09 L690,222.32 L698,226.01 L706,230.05 L714,234.35 L722,238.79 L730,243.26 L730,280 L410,280 Z" fill="#7c3aed" fill-opacity="0.28"/>
<path d="M410,240.0 L418,244.46 L426,248.81 L434,252.93 L442,256.72 L450,260.09 L458,262.94 L466,265.2 L474,266.82 L482,267.76 L490,267.99 L498,267.5 L506,266.31 L514,264.45 L522,261.96 L530,258.91 L538,255.38 L546,251.46 L554,247.24 L562,242.84 L570,238.37 L578,233.93 L586,229.66 L594,225.64 L602,222.0 L610,218.81 L618,216.16 L626,214.13 L634,212.75 L642,212.07 L650,212.11 L658,212.85 L666,214.29 L674,216.39 L682,219.09 L690,222.32 L698,226.01 L706,230.05 L714,234.35 L722,238.79 L730,243.26" fill="none" stroke="#7c3aed" stroke-width="3"/>
<path d="M410,240.0 L418,244.46 L426,248.81 L434,252.93 L442,256.72 L450,260.09 L458,262.94 L466,265.2 L474,266.82 L482,267.76 L490,267.99 L498,267.5 L506,266.31 L514,264.45 L522,261.96 L530,258.91 L538,255.38 L546,251.46 L554,247.24 L562,242.84 L570,238.37 L578,233.93 L586,229.66 L594,225.64 L602,222.0 L610,218.81 L618,216.16 L626,214.13 L634,212.75 L642,212.07 L650,212.11 L658,212.85 L666,214.29 L674,216.39 L682,219.09 L690,222.32 L698,226.01 L706,230.05 L714,234.35 L722,238.79 L730,243.26" fill="none" stroke="#e5aa28" stroke-width="3"/>
<path d="M410,276.0 L418,280.46 L426,284.81 L434,288.93 L442,292.72 L450,296.09 L458,298.94 L466,301.2 L474,302.82 L482,303.76 L490,303.99 L498,303.5 L506,302.31 L514,300.45 L522,297.96 L530,294.91 L538,291.38 L546,287.46 L554,283.24 L562,278.84 L570,274.37 L578,269.93 L586,265.66 L594,261.64 L602,258.0 L610,254.81 L618,252.16 L626,250.13 L634,248.75 L642,248.07 L650,248.11 L658,248.85 L666,250.29 L674,252.39 L682,255.09 L690,258.32 L698,262.01 L706,266.05 L714,270.35 L722,274.79 L730,279.26" fill="none" stroke="#f59e0b" stroke-width="3"/>
<path d="M410,312.0 L418,316.46 L426,320.81 L434,324.93 L442,328.72 L450,332.09 L458,334.94 L466,337.2 L474,338.82 L482,339.76 L490,339.99 L498,339.5 L506,338.31 L514,336.45 L522,333.96 L530,330.91 L538,327.38 L546,323.46 L554,319.24 L562,314.84 L570,310.37 L578,305.93 L586,301.66 L594,297.64 L602,294.0 L610,290.81 L618,288.16 L626,286.13 L634,284.75 L642,284.07 L650,284.11 L658,284.85 L666,286.29 L674,288.39 L682,291.09 L690,294.32 L698,298.01 L706,302.05 L714,306.35 L722,310.79 L730,315.26" fill="none" stroke="#d97706" stroke-width="3"/>
<text x="60" y="350" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">層が、髪のない所にも割り当てられて、無駄が出る</text>
<text x="420" y="350" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">層の始まりが、画素ごとの髪の最初の面。3〜4 層で足りる</text>
<rect x="420" y="370" width="300" height="22" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5" rx="3"/>
<rect x="420" y="370" width="300" height="22" fill="#2563eb" rx="3"><animate attributeName="width" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1111;0.1389;0.1667;0.1944;0.2222;0.2500;0.2778;0.3056;0.3333;0.3611;0.3889;0.4167;0.4444;0.4722;0.5000;0.5278;0.5556;0.5833;0.6111;0.6389;0.6667;0.6944;0.7222;0.7500;0.7778;1.0000" values="300;300;261.46;227.87;198.6;173.08;150.85;131.47;114.58;99.86;87.03;75.85;66.11;57.61;50.21;43.76;38.14;33.24;28.97;25.25;22.01;19.18;16.71;14.57;12.7;11.06;11.06"/></rect>
<text x="50" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が通った不透明度の合計 0.0 → 届く光 100 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1108;0.1111;0.2219;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が通った不透明度の合計 0.6 → 届く光 52 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.3330;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が通った不透明度の合計 1.2 → 届く光 27 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;0.4441;0.4444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が通った不透明度の合計 1.8 → 届く光 14 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4441;0.4444;0.5553;0.5556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が通った不透明度の合計 2.4 → 届く光 7 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5553;0.5556;0.6664;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">光が通った不透明度の合計 3.0 → 届く光 4 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;0.7775;0.7778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="418" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">届く光の割合 = exp(−密度 × 合計)</text>
</svg>

<!-- fig:deep-opacity:end -->

## Deep Opacity Maps

Yuksel と Keyser の **Deep Opacity Maps**（Eurographics 2008 / I3D）は、この問題を賢い工夫で解決しました。**層の始まりの位置を、画素ごとに変える**のです。

1. **最初の深度マップ**：光から見て、髪の**最も手前の面**の深度 z₀ を、画素ごとに保存します（通常のシャドウ マップと同じ）。
2. **層の設定**：各画素について、z₀ から奥へ向かって、一定の間隔 Δ で層を切ります。第 1 層は z₀ から z₀ + Δ、第 2 層は z₀ + Δ から z₀ + 2Δ、…と続きます。層の数 K は少数（3〜4）です。
3. **不透明度の累積**：髪をもう一度描き、各フラグメントについて、その深度が属する層以降の層に、不透明度を**加算**します。1 枚の RGBA テクスチャの 4 つのチャンネルが、4 つの層に対応します。
4. **影の計算**：影を付ける点で、その点の光空間の位置を求めます。その点が、画素の z₀ から何層目に属するかを計算し、**その点より手前にある層の不透明度の合計**を読んで、補間します。

ポイントは、**層の始まりを髪の最初の面に揃える**ことです。層が髪の領域にだけ割り当てられるので、少ない層でも、髪の厚み全体を細かく表現できます。通常の Opacity Shadow Maps では、髪がない空間にも層が割り当てられ、無駄が出ていました。

```hlsl
float DeepOpacityShadow(float3 world_pos) {
  float4 light_pos = mul(float4(world_pos, 1.0), light_view_projection);
  float2 uv = light_pos.xy / light_pos.w * float2(0.5, -0.5) + 0.5;
  float z = light_pos.z / light_pos.w;

  float z0 = first_depth_tex.SampleLevel(point_clamp, uv, 0).r;
  float4 layers = opacity_layers_tex.SampleLevel(linear_clamp, uv, 0);

  float depth_in_hair = max(z - z0, 0.0) / kLayerSize;
  float accumulated = 0.0;
  accumulated += (depth_in_hair > 0.0) ? layers.x * saturate(depth_in_hair) : 0.0;
  accumulated += (depth_in_hair > 1.0) ? layers.y * saturate(depth_in_hair - 1.0) : 0.0;
  accumulated += (depth_in_hair > 2.0) ? layers.z * saturate(depth_in_hair - 2.0) : 0.0;
  accumulated += (depth_in_hair > 3.0) ? layers.w * saturate(depth_in_hair - 3.0) : 0.0;

  return exp(-kShadowDensity * accumulated);
}
```

最後の `exp(−密度 × 不透明度の合計)` は、Beer の法則です。通り抜けた髪の量が多いほど、光が指数関数的に減ります。`kShadowDensity` が影の濃さを決め、髪の密度に合わせて調整します。

## Other Methods {#他の方式}

髪の影には、ほかにもいくつか方式があります。

**Adaptive Volumetric Shadow Maps**（AVSM、Salvi ほか、2010）は、光の方向の透過率の曲線（深度に対する透過率）を、画素ごとに少数の点の折れ線で保存します。髪のように複雑な密度の分布でも、高い精度で影を表せます。保存する点の数（たとえば 8〜16）に応じてメモリを使いますが、柔軟性があります。

**ストランド用のボリューム ボクセル化**は、ストランドを描く方式で多く使われます。髪全体を囲む 3D 格子（ボクセル）を作り、各セルに、そこを通る髪の**密度**を書き込みます。影を付けるときは、点から光へ向かって、ボクセルの密度を**レイマーチ**で積分して、透過率を得ます。Unreal Engine の Groom などが、この方法を採っています。ボクセルは、髪の量が多くても一定のメモリで済み、AO や GI のような他の効果にも流用できます。

## Shadows Between Hair and Other Objects {#髪と他の物体の影}

髪の影は、髪だけで完結しません。**髪が肌に落とす影**（額や頬に前髪の影が落ちる）と、**肌や肩が髪に落とす影**もあります。髪の影用のマップ（Deep Opacity Maps など）は、肌のシェーディングでも参照して、髪が落とす影を肌に付けます。通常のシャドウ マップとは別に、**髪専用のシャドウ マップ**を持つ構成が一般的です。

髪専用の影を使うときは、通常のシャドウ マップに髪を**含めない**か、含める場合も**簡易**にします。二重に影を計算すると、髪が黒くなりすぎるためです。

## Shadow Color {#影の色}

髪の影の色は、単なる黒ではなく、髪の色を反映します。光が髪の内部を通って散乱するため、**影の中でも、髪の色がうっすら残ります**。影の濃さを `exp(−密度 × 不透明度の合計)` で求めたあと、その値を 0 まで下げず、**下限**（たとえば 0.1〜0.3）を設けて、完全な黒にならないようにします。さらに、環境光（空の光）を足して、影の中の髪が、完全に潰れないようにします。

## Cost {#コスト}

Deep Opacity Maps のコストは、髪を 2 回描くこと（最初の深度マップと、層の累積）です。髪のカードの数が多いと、頂点処理が 2 倍になります。解像度は、通常のシャドウ マップよりも低く（1024×1024 程度）ても、髪の影はぼんやりしているので足ります。層の累積は、加算ブレンドなので、描画自体は軽い処理です。髪の領域だけを描画範囲に絞ると、フィルレートを節約できます。

## Common Mistakes {#よくあるミス}

??? failure "髪の影が、ベタッと黒く、立体感がない"
    **影の濃さに下限**を設ける。**環境光を足す**。Beer の法則の**密度**を下げる。

??? failure "髪に、縞（バンディング）が出る"
    層の間隔 Δ が**大きすぎる**。**層を細かく**する、または**層の境の補間**をなめらかにする。

??? failure "髪が肌に影を落とさない"
    髪の影マップを、**肌のシェーディングでも参照**する。

??? failure "髪の影が二重に出て、黒くなりすぎる"
    通常のシャドウ マップと**髪の影を二重に掛けていないか**確認する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] 髪の影は<strong>連続的に暗くなる</strong>。**0/1 のシャドウ マップでは足りない**
    - [x] **Deep Opacity Maps**：**髪の最初の面から層を切り**、**不透明度を累積**
    - [x] 影の濃さは<strong>exp(−密度 × 不透明度の合計)</strong>（Beer の法則）
    - [x] ストランドは**ボクセル化した密度のレイマーチ**でも影を付けられる
    - [x] 髪の影は**肌にも落とす**

## References {#参考}

- Yuksel, Keyser, "Deep Opacity Maps"（Computer Graphics Forum / Eurographics 2008）
- Kim, Neumann, "Opacity Shadow Maps"（Eurographics Workshop on Rendering 2001）
- Salvi, Vidimče, Lauritzen, Lefohn, "Adaptive Volumetric Shadow Maps"（Eurographics Symposium on Rendering 2010）

## Related Pages {#関連ページ}

- [Hair Overview](index.md)
- [Hair Transparency](transparency.md)
- [Translucent Shadows](../../shadows/special-cases/translucent-shadows.md)
- [Volumetric Fog](../../atmosphere/volumetric-fog/index.md)
