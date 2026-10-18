---
title: Height at Arbitrary Positions
tags:
  - 描画
---

# Height at Arbitrary Positions

**キャラクターを地面に立たせるには、任意の位置の地面の高さが必要**です。**格子の 4 点から補間**して**求めます**。このページでは、**高さの取得方法**を説明します。

!!! tip "ポイント"
    - **位置を格子の座標に変換**し、**周囲の 4 点を取り出す**。
    - **双線形補間で、高さを求める**。
    - **CPU 側にも、高さマップを持つ**。
    - **格子の三角形の分割と、補間を合わせる**。

## 任意の位置の高さを取る
**キャラクターを地面に立たせる・草を置く・当たり判定**には、**CPU で任意の (x, z) の高さ**が**必要**です。**高さマップの 4 点を、双線形補間**します。

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
| **双線形補間** | **4 点を補間**して**滑らかな高さ** |
| **メッシュの三角形と一致させる** | **見た目のメッシュは三角形 2 枚**なので、**厳密には三角形に沿って補間する**と**ずれない**（**足が浮く・めり込む**を防ぐ） |
| **GPU と同じデータ** | **CPU 側にも同じ高さマップを保持** |
| **範囲外** | **`At` は端にクランプ** |

**対角線方向の三角形に沿った補間**は、**マス内の位置 (fx, fz) が `fx + fz < 1` かどうか**で**三角形を選び**、**その三角形上の平面の式**で**高さを出します**。

<!-- fig:bilinear-height:begin -->

<svg class="fig illust motion" data-fig="bilinear-height" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bilinear-height" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">好きな位置の高さ: 周りの 4 つの高さを、距離で混ぜる(バイリニア)。最も近い 1 点だと、階段になる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">なだらかな坂の上に、キャラクターが歩く。高さマップは 1 マス = 1 m。1 マスの途中の位置で、2 つの方法の高さを比べる</text>
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
<text x="56" y="468" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">最も近い 1 点だと、1 m ごとに、階段状に段差。キャラが、ガクガク上下する</text>
<text x="56" y="490" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">バイリニアは、4 回読むだけで、なめらか。当たり判定・接地・草の根元に、使う</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">高さマップは、整数の格子点にしか、高さが無い<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">最も近い格子点の高さを使うと、階段になる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.3828;0.3830;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">周りの 4 点を、距離で混ぜると、なめらかな坂になる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3828;0.3830;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bilinear-height:end -->

## よくあるミス

??? failure "キャラクターが、地面にめり込む・浮く"
    **描画と同じ補間方法**で**高さを求める**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **4 点を補間して、高さを求める**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [Chunking](chunks.md)
