---
title: Normal Offset
tags:
  - 描画
---

# Normal Offset

**深度にバイアスを足す**代わりに、**影を調べる点（受け手の位置）を、法線方向に少しずらす**方法が**法線オフセット**です。**面の傾きに自然に追従し、ピーター パンニングが出にくい**ので、**現在の標準的な手法**です。このページでは、**考え方・ずらす量の決め方・実装・注意（細い物・影の縁）**を説明します。

!!! tip "ポイント"
    - **法線オフセット ＝ 受け手の位置を、法線方向にずらしてから、光の空間へ変換する**。
    - **ずらす量は、テクセルの大きさに比例**させる。
    - **傾いた面ほど、大きくずらす**（`1 − N·L`）。
    - **ピーター パンニングが出にくい**が、**影の位置が少しずれる**。

<!-- fig:normal-offset:begin -->

<svg class="fig illust motion" data-fig="normal-offset" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-normal-offset" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">法線オフセット:受ける点を、法線方向へ少しずらしてから、深度を比べる</text>
<line x1="60" y1="280" x2="700" y2="139.2" stroke="#b8794b" stroke-width="6"/>
<line x1="60" y1="110" x2="60" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="140" y1="110" x2="140" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="220" y1="110" x2="220" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="300" y1="110" x2="300" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="380" y1="110" x2="380" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="460" y1="110" x2="460" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="540" y1="110" x2="540" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="620" y1="110" x2="620" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="700" y1="110" x2="700" y2="340" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4 3"/>
<circle cx="80" cy="275.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="80;80;80;75.27;75.27;75.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="275.6;275.6;275.6;254.11;254.11;254.11"/></circle>
<line x1="80" y1="275.6" x2="75.27" y2="254.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="120" cy="266.8" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="120;120;120;115.27;115.27;115.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="266.8;266.8;266.8;245.31;245.31;245.31"/></circle>
<line x1="120" y1="266.8" x2="115.27" y2="245.31" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="160" cy="258.0" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="160;160;160;155.27;155.27;155.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="258;258;258;236.51;236.51;236.51"/></circle>
<line x1="160" y1="258.0" x2="155.27" y2="236.51" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="200" cy="249.2" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="200;200;200;195.27;195.27;195.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="249.2;249.2;249.2;227.71;227.71;227.71"/></circle>
<line x1="200" y1="249.2" x2="195.27" y2="227.71" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="240" cy="240.4" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="240;240;240;235.27;235.27;235.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="240.4;240.4;240.4;218.91;218.91;218.91"/></circle>
<line x1="240" y1="240.4" x2="235.27" y2="218.91" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="280" cy="231.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="280;280;280;275.27;275.27;275.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="231.6;231.6;231.6;210.11;210.11;210.11"/></circle>
<line x1="280" y1="231.6" x2="275.27" y2="210.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="320" cy="222.8" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="320;320;320;315.27;315.27;315.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="222.8;222.8;222.8;201.31;201.31;201.31"/></circle>
<line x1="320" y1="222.8" x2="315.27" y2="201.31" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="360" cy="214.0" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="360;360;360;355.27;355.27;355.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="214;214;214;192.51;192.51;192.51"/></circle>
<line x1="360" y1="214.0" x2="355.27" y2="192.51" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="400" cy="205.2" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="400;400;400;395.27;395.27;395.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="205.2;205.2;205.2;183.71;183.71;183.71"/></circle>
<line x1="400" y1="205.2" x2="395.27" y2="183.71" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="440" cy="196.4" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="440;440;440;435.27;435.27;435.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="196.4;196.4;196.4;174.91;174.91;174.91"/></circle>
<line x1="440" y1="196.4" x2="435.27" y2="174.91" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="480" cy="187.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="480;480;480;475.27;475.27;475.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="187.6;187.6;187.6;166.11;166.11;166.11"/></circle>
<line x1="480" y1="187.6" x2="475.27" y2="166.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="520" cy="178.8" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="520;520;520;515.27;515.27;515.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="178.8;178.8;178.8;157.31;157.31;157.31"/></circle>
<line x1="520" y1="178.8" x2="515.27" y2="157.31" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="560" cy="170.0" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="560;560;560;555.27;555.27;555.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="170;170;170;148.51;148.51;148.51"/></circle>
<line x1="560" y1="170.0" x2="555.27" y2="148.51" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="600" cy="161.2" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="600;600;600;595.27;595.27;595.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="161.2;161.2;161.2;139.71;139.71;139.71"/></circle>
<line x1="600" y1="161.2" x2="595.27" y2="139.71" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="640" cy="152.4" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="640;640;640;635.27;635.27;635.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="152.4;152.4;152.4;130.91;130.91;130.91"/></circle>
<line x1="640" y1="152.4" x2="635.27" y2="130.91" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<circle cx="680" cy="143.6" r="6" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000" values="#2ea043;#e5484d;#e5484d;#2ea043;#2ea043"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="680;680;680;675.27;675.27;675.27"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.6000;0.8000;1.0000" values="143.6;143.6;143.6;122.11;122.11;122.11"/></circle>
<line x1="680" y1="143.6" x2="675.27" y2="122.11" stroke="#64748b" stroke-width="1.5" opacity="0.6"/>
<text x="60" y="70" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">面上の点（赤 = 自己遮蔽のアクネ、緑 = OK）。矢印は法線<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="1;1;0;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">法線方向に、ずらしていく…<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.5997;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光に近い側へ持ち上げたので、アクネが消えた<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5997;0.6000;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="380" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">深度ではなく「位置」をずらすので、傾きによらず効く。ずらしすぎると、影の位置が、わずかにずれる。</text>
</svg>

<!-- fig:normal-offset:end -->

## Fix 3: Normal Offset {#対策-3法線オフセット}
**バイアスを深度ではなく、位置**で与えます。**サンプルする点を法線方向に少しずらして**から、光の座標に変換します。

<div class="formula">P′ = P + N · offset · texel_size · (1 − N·L)</div>

| 項 | 意味 |
| --- | --- |
| **N** | 面の法線 |
| **offset** | 調整値（0.5〜2 程度） |
| **texel_size** | シャドウ マップの 1 テクセルの、ワールドでの大きさ |
| <strong>(1 − N·L)</strong> | **斜めの面ほど、大きく**ずらす |

```hlsl
float3 shadow_pos = world_pos + normal * (normal_offset * texel_world_size * (1.0 - saturate(dot(normal, light_dir))));
float4 light_clip = mul(float4(shadow_pos, 1.0), light_view_projection);
```

法線オフセットの利点は、面に沿って法線方向にずらすので、ピーター パンニングが小さいこと、斜めの面で効果が大きいこと、テクセルの大きさに比例するので、解像度の変化にも追従することです。欠点は、法線が必要なこと（丸みのある法線では角が丸くずれる）、影の位置がわずかにずれること（薄い物や細い隙間で光漏れ）、法線の読み込みと行列の乗算で計算が増えることです。

**スロープ スケール＋法線オフセット**を併用するのが、**実用上の定番**です。

## Common Mistakes {#よくあるミス}

??? failure "オフセットが大きすぎて、細い物の影が欠ける"
    **ずらす量を、テクセルの大きさ程度に抑える**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **法線方向にずらして比べる**
    - [x] **テクセル サイズに比例**。**現在の標準**

## References {#参考}

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## Related Pages {#関連ページ}

- [Shadow Bias](index.md)
- [Slope-Scale Bias](slope-scale-bias.md)
- [Receiver Plane Bias](receiver-plane-bias.md)
