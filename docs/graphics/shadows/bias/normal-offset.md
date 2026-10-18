---
title: Normal Offset
tags:
  - 描画
---

# Normal Offset

<strong>深度にバイアスを足す</strong>代わりに、<strong>影を調べる点（受け手の位置）を、法線方向に少しずらす</strong>方法が法線オフセットです。面の傾きに自然に追従しピーター パンニングが出にくいので、現在の標準的な手法です。このページでは考え方・ずらす量の決め方・実装・注意（細い物・影の縁）を説明します。

!!! tip "ポイント"
    - 法線オフセット ＝ 受け手の位置を、法線方向にずらしてから光の空間へ変換する。
    - ずらす量はテクセルの大きさに比例させる。
    - 傾いた面ほど大きくずらす（`1 − N·L`）。
    - ピーター パンニングが出にくいが、影の位置が少しずれる。

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

## 対策 3：法線オフセット
<strong>バイアスを深度ではなく位置</strong>で与えます。<strong>サンプルする点を法線方向に少しずらして</strong>から、光の座標に変換します。

<div class="formula">P′ = P + N · offset · texel_size · (1 − N·L)</div>

| 項 | 意味 |
| --- | --- |
| N | 面の法線 |
| offset | 調整値（0.5〜2 程度） |
| texel_size | シャドウ マップの 1 テクセルの、ワールドでの大きさ |
| <strong>(1 − N·L)</strong> | 斜めの面ほど、大きくずらす |

```hlsl
float3 shadow_pos = world_pos + normal * (normal_offset * texel_world_size * (1.0 - saturate(dot(normal, light_dir))));
float4 light_clip = mul(float4(shadow_pos, 1.0), light_view_projection);
```

法線オフセットの利点は面に沿って法線方向にずらすので、ピーター パンニングが小さいこと、斜めの面で効果が大きいことテクセルの大きさに比例するので、解像度の変化にも追従することです。欠点は法線が必要なこと（丸みのある法線では角が丸くずれる）、影の位置がわずかにずれること（薄い物や細い隙間で光漏れ）、法線の読み込みと行列の乗算で計算が増えることです。

<strong>スロープ スケール＋法線オフセット</strong>を併用するのが、<strong>実用上の定番</strong>です。

## 法線オフセットとは

<strong>深度を引く</strong>代わりに <strong>画素の位置そのもの</strong>を、面の法線の向きに少しずらしてから、シャドウ マップを引きます。面の少し上（表面の外側）の点を、調べることになるので自分自身の面と、交差しません。

```text
              光
              ↓
 ──────────●─────────  地面（P）
            ↑ 法線の向きに、少し持ち上げる
           ●             P' = P + N × offset  ← この点で、シャドウ マップを引く
```

<strong>深度の値はいじらず</strong>、<strong>位置を動かす</strong>のでバイアスの、副作用（影が浮く）が小さくなります。

## 実装

```hlsl
float ShadowFactorNormalOffset(float3 world_pos, float3 world_normal, float3 light_dir, float offset_scale) {
  // 面が、光に対して、斜めなほど、大きくずらす（斜めの面ほど、自己影が、出やすいため）。
  float cos_theta = saturate(dot(world_normal, -light_dir));
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  float3 offset = world_normal * (sin_theta * offset_scale);

  // 位置を、法線方向に、ずらしてから、光の座標に変換する。
  float4 p = mul(float4(world_pos + offset, 1.0), g_shadow_matrix);
  float3 coord = p.xyz / p.w;
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy, coord.z);
}
```

| 要素 | 内容 |
| --- | --- |
| `offset_scale` | ずらす距離。シャドウ マップの 1 画素の、ワールドでの大きさの 1〜3 倍が、目安 |
| `sin_theta` | 光に正面（`sin = 0`）なら、ずらさない。斜め（`sin` が大きい）ほど大きくずらす |

### ずらす距離の決め方

シャドウ マップの 1 画素が、ワールドで <strong>どのくらいの大きさか</strong>を、基準にします。

```cpp
// 太陽（正射影）のとき、1 画素の、ワールドでの大きさ（メートル）。
float texel_world_size = (2.0f * radius) / shadow_map_resolution;
// 法線オフセットの距離は、その 1〜3 倍。
float normal_offset = texel_world_size * 2.0f;
```

<strong>解像度が粗い</strong>（遠いカスケード）ほど、1 画素が大きいので <strong>オフセットも、大きく</strong>します。カスケードごとに `texel_world_size` を計算します。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | ピーター パンニングが、少ない（深度を動かさないので影が物から、離れにくい） |
| 長所 | 斜めの面でも自己影を、抑えられる（傾きに応じてずらすため） |
| 長所 | ワールドの距離で、指定できる（直感的。カスケードごとにスケールしやすい） |
| 短所 | 法線が必要（シャドウを引く、メイン パスで法線を持っている必要がある） |
| 短所 | 影がわずかにずれる（位置を、動かすので）。物の縁・角で影が欠けることがある |
| 短所 | 法線が滑らか（頂点法線の、補間）でないと面の境目で影が、段差になる。ノーマル マップは使わずジオメトリの法線を、使う |

### 角（エッジ）での問題

<strong>物の角</strong>で法線方向にずらすと、<strong>隣の面の影の内部</strong>に入ってしまうことがあります。ずらす距離が大きすぎると角の影が、欠けます。

| 対策 | 内容 |
| --- | --- |
| ずらす距離を控えめに | 1 画素の、1〜2 倍にとどめる |
| 補間した法線（頂点法線）を使う | 面法線ではなく、頂点法線を補間して使う（角で法線が、滑らかに変わる） |
| 定数バイアスと併用 | 法線オフセットで、大部分を抑え残りを小さな定数バイアスで、補う |

## 他のバイアスとの組み合わせ

<strong>実用的な組み合わせ</strong>は次のとおりです。

```text
① 法線オフセット（斜めの面の、自己影を、抑える。ワールド距離で、指定）
② + 小さな定数バイアス（深度の精度の誤差を、補う）
③ + ハードウェアの、傾き依存バイアス（シャドウ パスで、ごく小さく）
```

| 役割 | 方式 |
| --- | --- |
| 斜めの面（射影エイリアシング） | 法線オフセット |
| 深度の量子化誤差 | 小さな、定数バイアス |
| 三角形ごとの微調整 | 傾き依存（ごく小さく） |

どれも <strong>大きく</strong>すると副作用が、出るので <strong>小さな値を組み合わせる</strong>のが、コツです。

## よくあるミス

??? failure "オフセットが大きすぎて、細い物の影が欠ける"
    <strong>ずらす量をテクセルの大きさ程度に抑える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 法線方向にずらして比べる
    - [x] テクセル サイズに比例。現在の標準

## 参考

- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Shadow Bias](index.md)
- [Slope-Scale Bias](slope-scale-bias.md)
- [Receiver Plane Bias](receiver-plane-bias.md)
