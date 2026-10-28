---
title: Height at Arbitrary Positions
tags:
  - 描画
---

# Height at Arbitrary Positions

<strong>キャラクターを地面に立たせるには、任意の位置の地面の高さが必要</strong>です。格子の 4 点から補間して求めます。このページでは高さの取得方法を説明します。

!!! tip "ポイント"
    - 位置を格子の座標に変換し、周囲の 4 点を取り出す。
    - 双線形補間で高さを求める。
    - CPU 側にも高さマップを持つ。
    - 格子の三角形の分割と、補間を合わせる。

!!! info "このページを読む前に"
    - [Heightmaps and Meshes](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 任意の位置の高さを取る
<strong>キャラクターを地面に立たせる・草を置く・当たり判定</strong>には、CPU で任意の (x, z) の高さが必要です。高さマップの 4 点を双線形補間します。

```cpp
float SampleHeight(const HeightMap& map, float world_x, float world_z) {
  float u = (world_x - map.origin_x) / map.cell_size;
  float v = (world_z - map.origin_z) / map.cell_size;
  int x0 = static_cast<int>(std::floor(u));
  int z0 = static_cast<int>(std::floor(v));
  float fx = u - x0;
  float fz = v - z0;

  float h00 = map.At(x0, z0);
  float h10 = map.At(x0 + 1, z0);
  float h01 = map.At(x0, z0 + 1);
  float h11 = map.At(x0 + 1, z0 + 1);

  float h0 = h00 + (h10 - h00) * fx;
  float h1 = h01 + (h11 - h01) * fx;
  return h0 + (h1 - h0) * fz;
}
```

| 点 | 説明 |
| --- | --- |
| 双線形補間 | 4 点を補間して滑らかな高さ |
| メッシュの三角形と一致させる | 見た目のメッシュは三角形 2 枚なので、厳密には三角形に沿って補間するとずれない（足が浮く・めり込むを防ぐ） |
| GPU と同じデータ | CPU 側にも同じ高さマップを保持 |
| 範囲外 | `At` は端にクランプ |

対角線方向の三角形に沿った補間は、マス内の位置 (fx, fz) が `fx + fz < 1` かどうかで三角形を選び、その三角形上の平面の式で高さを出します。

<!-- fig:bilinear-height:begin -->

<svg class="fig illust motion" data-fig="bilinear-height" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bilinear-height" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">好きな位置の高さ: 周りの 4 つの高さを距離で混ぜる(バイリニア)。最も近い 1 点だと、階段になる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">なだらかな坂の上にキャラクターが歩く。高さマップは 1 マス = 1 m。1 マスの途中の位置で、2 つの方法の高さを比べる</text>
<rect x="30" y="96" width="900" height="260" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">歩いた線に沿った高さ</text>
<path d="M60.0,310.91 L76.8,304.84 L93.6,299.13 L110.4,293.82 L127.2,288.93 L144.0,284.5 L160.8,280.54 L177.6,277.07 L194.4,274.08 L211.2,271.57 L228.0,269.54 L244.8,267.95 L261.6,266.78 L278.4,266.01 L295.2,265.57 L312.0,265.44 L328.8,265.55 L345.6,265.87 L362.4,266.31 L379.2,266.84 L396.0,267.38 L412.8,267.88 L429.6,268.28 L446.4,268.52 L463.2,268.54 L480.0,268.29 L496.8,267.73 L513.6,266.82 L530.4,265.52 L547.2,263.8 L564.0,261.64 L580.8,259.02 L597.6,255.95 L614.4,252.41 L631.2,248.41 L648.0,243.98 L664.8,239.14 L681.6,233.9 L698.4,228.31 L715.2,222.41 L732.0,216.25 L748.8,209.87 L765.6,203.32 L782.4,196.67 L799.2,189.97 L816.0,183.27 L832.8,176.64 L849.6,170.12 L866.4,163.78 L883.2,157.66 L900.0,151.81" fill="none" stroke="#64748b" stroke-width="2.5" stroke-dasharray="6 5"/>
<path d="M60.0,310.91 L76.8,310.91 L93.6,310.91 L110.4,298.19 L127.2,298.19 L144.0,274.93 L160.8,274.93 L177.6,274.93 L194.4,274.93 L211.2,274.93 L228.0,274.93 L244.8,274.93 L261.6,274.93 L278.4,274.93 L295.2,274.93 L312.0,274.93 L328.8,266.08 L345.6,266.08 L362.4,266.08 L379.2,266.08 L396.0,266.08 L412.8,266.08 L429.6,266.08 L446.4,278.81 L463.2,278.81 L480.0,250.73 L496.8,250.73 L513.6,250.73 L530.4,263.45 L547.2,263.45 L564.0,263.45 L580.8,263.45 L597.6,263.45 L614.4,263.45 L631.2,263.45 L648.0,263.45 L664.8,210.67 L681.6,210.67 L698.4,210.67 L715.2,210.67 L732.0,210.67 L748.8,210.67 L765.6,210.67 L782.4,210.67 L799.2,210.67 L816.0,163.9 L832.8,163.9 L849.6,163.9 L866.4,151.18 L883.2,151.18 L900.0,151.18" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="1"/>
<path d="M60.0,310.91 L76.8,306.21 L93.6,301.54 L110.4,296.94 L127.2,292.46 L144.0,288.11 L160.8,283.94 L177.6,279.98 L194.4,276.24 L211.2,272.76 L228.0,269.54 L244.8,268.04 L261.6,266.84 L278.4,265.94 L295.2,265.33 L312.0,265.02 L328.8,264.99 L345.6,265.23 L362.4,265.72 L379.2,266.45 L396.0,267.38 L412.8,266.57 L429.6,265.91 L446.4,265.35 L463.2,264.88 L480.0,264.45 L496.8,264.02 L513.6,263.57 L530.4,263.04 L547.2,262.41 L564.0,261.64 L580.8,258.23 L597.6,254.62 L614.4,250.78 L631.2,246.7 L648.0,242.35 L664.8,237.72 L681.6,232.8 L698.4,227.58 L715.2,222.06 L732.0,216.25 L748.8,210.76 L765.6,204.99 L782.4,198.96 L799.2,192.71 L816.0,186.24 L832.8,179.59 L849.6,172.79 L866.4,165.87 L883.2,158.86 L900.0,151.81" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3828;0.3830;1.0000" values="0;0;1;1"/></path>
<circle cx="76" cy="120" r="6" fill="#64748b"/>
<text x="86" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">本当の高さ</text>
<circle cx="159.0" cy="120" r="6" fill="#e5484d"/>
<text x="169.0" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">最も近い 1 点</text>
<circle cx="276.2" cy="120" r="6" fill="#2ea043"/>
<text x="286.2" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">周りの 4 点を混ぜる</text>
<circle cx="60.0" cy="310.91" r="7" fill="#1f2937"><animate attributeName="cx" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0638;0.0689;0.0740;0.0791;0.0843;0.0894;0.0945;0.0996;0.1047;0.1098;0.1149;0.1200;0.1251;0.1302;0.1353;0.1404;0.1455;0.1506;0.1557;0.1609;0.1660;0.1711;0.1762;0.1813;0.1864;0.1915;0.1966;0.2017;0.2068;0.2119;0.2170;0.2221;0.2272;0.2323;0.2374;0.2426;0.2477;0.2528;0.2579;0.2630;0.2681;0.2732;0.2783;0.2834;0.2885;0.2936;0.2987;0.3038;0.3089;0.3140;0.3191;1.0000" values="60;60;76.8;93.6;110.4;127.2;144;160.8;177.6;194.4;211.2;228;244.8;261.6;278.4;295.2;312;328.8;345.6;362.4;379.2;396;412.8;429.6;446.4;463.2;480;496.8;513.6;530.4;547.2;564;580.8;597.6;614.4;631.2;648;664.8;681.6;698.4;715.2;732;748.8;765.6;782.4;799.2;816;832.8;849.6;866.4;883.2;900;900"/><animate attributeName="cy" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0638;0.0689;0.0740;0.0791;0.0843;0.0894;0.0945;0.0996;0.1047;0.1098;0.1149;0.1200;0.1251;0.1302;0.1353;0.1404;0.1455;0.1506;0.1557;0.1609;0.1660;0.1711;0.1762;0.1813;0.1864;0.1915;0.1966;0.2017;0.2068;0.2119;0.2170;0.2221;0.2272;0.2323;0.2374;0.2426;0.2477;0.2528;0.2579;0.2630;0.2681;0.2732;0.2783;0.2834;0.2885;0.2936;0.2987;0.3038;0.3089;0.3140;0.3191;1.0000" values="310.91;310.91;304.84;299.13;293.82;288.93;284.5;280.54;277.07;274.08;271.57;269.54;267.95;266.78;266.01;265.57;265.44;265.55;265.87;266.31;266.84;267.38;267.88;268.28;268.52;268.54;268.29;267.73;266.82;265.52;263.8;261.64;259.02;255.95;252.41;248.41;243.98;239.14;233.9;228.31;222.41;216.25;209.87;203.32;196.67;189.97;183.27;176.64;170.12;163.78;157.66;151.81;151.81"/></circle>
<text x="40" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">足元の高さのずれ(平均、cm):</text>
<text x="300" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="300" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.3190;0.3191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3190;0.3191;0.6381;0.6383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6381;0.6383;1.0000" values="0;0;1;1"/></text>
<text x="340" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(最近点 → バイリニア)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6807;0.6809;1.0000" values="0;0;1;1"/><rect x="40" y="420" width="880" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="444" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">ずれの平均: 最も近い 1 点 13.2 cm → バイリニア 2.5 cm</text>
<text x="56" y="468" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">最も近い 1 点だと、1 m ごとに、階段状に段差。キャラがガクガク上下する</text>
<text x="56" y="490" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">バイリニアは、4 回読むだけで、なめらか。当たり判定・接地・草の根元に使う</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">高さマップは、整数の格子点にしか、高さが無い<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">最も近い格子点の高さを使うと、階段になる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.3828;0.3830;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">周りの 4 点を距離で混ぜると、なめらかな坂になる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3828;0.3830;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bilinear-height:end -->

## 双線形補間は描画のメッシュとずれる

上の `SampleHeight` は 4 点から <strong>双線形補間</strong>で、高さを求めます。ところが、描画される地形は 格子のマスを 2 枚の三角形に分けた折れ曲がった面です。双線形補間の面は曲がった面（双曲放物面）で、三角形の平面とは違います。

| 方式 | 面の形 | 描画との一致 |
| --- | --- | --- |
| 双線形補間 | 4 点を通る、曲面 | マスの中心でずれる |
| 三角形で補間（重心座標） | 2 枚の平面 | 描画のメッシュと、完全に一致 |

ずれはわずかですが 足が地面にめり込んだり浮いたりします。特に、急な斜面や高さマップの解像度が粗い場合は目立ちます。キャラクターの足や物の接地には、メッシュと同じ三角形で補間する必要があります。

## 三角形に合わせた補間

マスを <strong>どの対角線で分けているか</strong>で、計算が変わります（[Grid Mesh](grid-mesh.md)）。

```text
対角線 A（左上 − 右下）           対角線 B（右上 − 左下）
a───b                            a───b
│╲  │                            │  ╱│
│ ╲ │                            │ ╱ │
c───d                            c───d
```

```cpp
// 三角形に合わせた高さの補間。(fx, fz) は、マスの中の位置（0〜1）。
// h00 = 左上(a), h10 = 右上(b), h01 = 左下(c), h11 = 右下(d)
float InterpolateTriangle(float h00, float h10, float h01, float h11,
                          float fx, float fz, bool diagonal_a) {
  if (diagonal_a) {
```

関数の入口です。マスの 4 隅の高さとマスの中での位置 `(fx, fz)`（0〜1）、そしてこのマスの対角線がどちらかを受け取ります。メッシュはマスを 2 枚の三角形に割っているので高さも 三角形の平面で、補間しないと見た目の地面とずれます（双一次補間だと、曲面になってメッシュと一致しません）。

```cpp
    // 対角線 a−d。a, c, d の三角形（左下側）と、a, d, b の三角形（右上側）
    if (fx <= fz) {
      // 左下側: a, c, d
      return h00 + (h11 - h01) * fx + (h01 - h00) * fz;
    } else {
      // 右上側: a, d, b
      return h00 + (h10 - h00) * fx + (h11 - h10) * fz;
    }
  } else {
```

対角線が左上 a と右下 d を結ぶときマスは左下側（a、c、d）と右上側（a、d、b）に割れます。`fx <= fz` なら点は左下側にあります。どちらも、基準の頂点の高さに 2 方向への傾きを足すだけの平面の式です。

```cpp
    // 対角線 b−c。a, c, b の三角形（左上側）と、b, c, d の三角形（右下側）
    if (fx + fz <= 1.0f) {
      // 左上側: a, c, b
      return h00 + (h10 - h00) * fx + (h01 - h00) * fz;
    } else {
      // 右下側: b, c, d
      return h11 + (h01 - h11) * (1.0f - fx) + (h10 - h11) * (1.0f - fz);
    }
  }
}
```

対角線が右上 b と左下 c を結ぶときは `fx + fz <= 1` が左上側（a、c、b）と右下側（b、c、d）の境目です。右下側は d を基準にして `1 − fx`、`1 − fz` 方向に足します。

```cpp
float SampleHeightMatchingMesh(const HeightMap& map, float world_x, float world_z) {
  const float u = (world_x - map.origin_x) / map.cell_size;
  const float v = (world_z - map.origin_z) / map.cell_size;
```

ワールド座標からマスの番号と、マスの中の位置を求めます。`u`、`v` はマス単位の座標です。マスの番号は端ではみ出さないよう、`width − 2` までに制限します（右隣の頂点も、読むため）。

```cpp
  const int x0 = std::clamp(int(std::floor(u)), 0, map.width - 2);
  const int z0 = std::clamp(int(std::floor(v)), 0, map.height - 2);
  const float fx = u - x0, fz = v - z0;
```

対角線の向きはメッシュを作ったときと、同じ規則（市松）で決めます。ここがメッシュと食い違うと高さが、半マスぶんずれます（[Grid Mesh](grid-mesh.md)）。最後に、4 隅の高さを読んで先ほどの関数に渡します。

```cpp
  const bool diagonal_a = ((x0 + z0) & 1) == 0;       // 市松の貼り方と、同じ規則
  return InterpolateTriangle(map.At(x0, z0), map.At(x0 + 1, z0),
                             map.At(x0, z0 + 1), map.At(x0 + 1, z0 + 1), fx, fz, diagonal_a);
}
```

!!! warning "対角線の規則は、メッシュとまったく同じにする"
    `diagonal_a` の判定が描画のメッシュの貼り方と、1 つでも違うとずれが残ります。規則を 1 か所の関数にまとめて、メッシュ作りと高さの補間の両方から、使います。

## 法線も同じ三角形から

高さと同じ三角形から <strong>面の法線</strong>も、求められます。足を斜面に合わせて傾けるキャラクターを斜面に沿って滑らせるときに使います。

```cpp
float3 NormalAt(const HeightMap& map, float world_x, float world_z) {
  const float e = map.cell_size;
  // 中央差分（なめらかな法線）。三角形の面の法線が欲しいなら、三角形の 3 点から、外積で求める。
  const float hl = SampleHeightMatchingMesh(map, world_x - e, world_z);
  const float hr = SampleHeightMatchingMesh(map, world_x + e, world_z);
  const float hd = SampleHeightMatchingMesh(map, world_x, world_z - e);
  const float hu = SampleHeightMatchingMesh(map, world_x, world_z + e);
  return Normalize({hl - hr, 2.0f * e, hd - hu});
}
```

## レイと地形の交差

「画面をクリックした場所の地面」「弾が地面に当たる位置」を求めるには、<strong>レイと高さ場の交差</strong>を調べます。

### ① 一定の歩幅で進む（レイマーチ）

レイに沿って少しずつ進み レイの高さが、地面の高さを下回った所を交点とします。

```cpp
bool RaycastTerrain(const HeightMap& map, float3 origin, float3 dir, float max_dist,
                    float step, float3& hit) {
  float t = 0.0f;
  float prev_diff = origin.y - SampleHeightMatchingMesh(map, origin.x, origin.z);
```

レイを地面に当てる関数です。始点が地面の上にあるか下にあるかを `diff = レイの高さ − 地面の高さ` で、持ちます。

```cpp
  while (t < max_dist) {
    t += step;
    const float3 p = origin + dir * t;
    const float diff = p.y - SampleHeightMatchingMesh(map, p.x, p.z);
    if (diff < 0.0f && prev_diff >= 0.0f) {
```

一定の歩幅 `step` で進みます。`diff` が正から負に変わった瞬間が地面に入ったときです。

```cpp
      // 地面の下に入った。直前の位置との間で、二分探索して、交点を絞り込む。
      float lo = t - step, hi = t;
      for (int i = 0; i < 8; ++i) {
        const float mid = 0.5f * (lo + hi);
        const float3 q = origin + dir * mid;
        if (q.y - SampleHeightMatchingMesh(map, q.x, q.z) < 0.0f) hi = mid; else lo = mid;
      }
```

入った区間（直前の位置と今の位置）の間で、二分探索して交点を絞ります。8 回で歩幅の 256 分の 1 の、精度になります。歩幅が大きいと細い尾根を飛び越えるので地形の、起伏に合わせて歩幅を決めます。

```cpp
      hit = origin + dir * hi;
      return true;
    }
    prev_diff = diff;
  }
  return false;
}
```

歩幅が大きいと 細い尾根を飛び越えて、取りこぼします。小さいと遅くなります。歩幅は格子の間隔の半分以下が目安です。

### ② マスを 1 つずつ進む（DDA）

Amanatides と Woo（1987）の方法で、レイが通る マスだけを 1 つずつたどり、各マスでレイと 2 枚の三角形の交差を調べます。取りこぼしがなく長いレイでも、調べるマスの数は距離に比例するだけです。

| 方式 | 取りこぼし | 速さ | 実装 |
| --- | --- | --- | --- |
| 一定の歩幅 | 出ることがある | 歩幅が小さいと遅い | 簡単 |
| マスを 1 つずつ（DDA） | ない | 速い | やや複雑 |
| 四分木の最大高さで枝刈り | ない | 長いレイで、特に速い | 複雑（最大高さのミップが必要） |

長距離（狙撃、視線チェック）では 最大高さのミップ（[Heightmap LOD (Mips)](../lod/height-mip.md)）で、「このブロックの上をレイが通過するか」を先に判定して 大きく飛ばすと、速くなります。

## 物理エンジンの高さ場

物理エンジンも地形の当たり判定に使える<strong>高さ場（heightfield）の形状</strong>を持っています（PhysX、Jolt など）。

| 項目 | 内容 |
| --- | --- |
| データ | 高さの配列（描画の高さマップと、同じ値を渡す） |
| 三角形の分け方 | エンジンごとに、決まっている。描画と合わせる（合わせられなければ、わずかなずれを許容する） |
| 更新 | 地形を変形したら、高さ場の該当範囲を更新する |
| 穴 | 洞窟の入口などの穴は、材質の ID に穴を表す値を持たせて、表現する（エンジンによる） |

物理エンジンが独自の補間を使う場合、自分で同じ補間を実装して見た目を合わせるのが無難です。

## 範囲外と穴

| 場合 | 扱い |
| --- | --- |
| 地形の外 | `clamp` で端の高さをそのまま使う。または、「地面がない」を返す |
| 穴（洞窟の入口） | 穴の画素は `NaN` や、特別な値で表す。高さの補間で穴の境目が混ざらないように、4 点のどれかが穴ならその三角形は、穴として扱う |
| チャンクの境界 | 隣のチャンクを読み込んでいない間は境界の画素を両側が同じ値で持つ（[Chunking](chunks.md)） |

## よくあるミス

??? failure "キャラクターが地面にめり込む・浮く"
    <strong>描画と同じ補間方法</strong>で高さを求める。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 4 点を補間して、高さを求める

## 参考

- Amanatides, Woo, "A Fast Voxel Traversal Algorithm for Ray Tracing", Eurographics 1987（グリッドを 1 マスずつ進む DDA）
- Ericson, "Real-Time Collision Detection", Morgan Kaufmann, 2004（レイと三角形、グリッドの走査）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）
- Jolt Physics, "HeightFieldShape" ドキュメント（物理エンジンでの、高さ場の扱い）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [Chunking](chunks.md)
