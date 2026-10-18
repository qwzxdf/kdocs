---
title: Thin Translucency
tags:
  - 描画
---

# Thin Translucency

太陽や強い光を背にして耳や指を見ると、<strong>赤く透けて見えます</strong>。肌が薄い所では光が肌の<strong>反対側の面から入り</strong>、内部を通り抜けてこちら側へ出てくるためです。これが薄い部位の透過（thin translucency）です。SSS の画面空間のぼかしやLUTは、「光が当たった面の近くの広がり」しか扱えずこの裏から来る光は表せません。このページでは Jimenez らの "Real-Time Realistic Skin Translucency"（2010）に沿って、「裏から入った光の量」をシャドウ マップから求める方法を説明します。

!!! tip "ポイント"
    - 耳・鼻・指・唇のように薄い所は、反対側から入った光が透けて見える。
    - 透けた光の量は肌を通る距離（厚み）で決まる。厚いほど光は弱く赤い。
    - 厚みはシャドウ マップで測る。光から見た手前の面までの深さと今の点の深さの差。
    - 厚みから透過率への変換は、拡散プロファイルを厚みの関数にした形（ガウスの和）。
    - 裏側の法線を使って、透過光の向きを決める。表面の光は別に計算する。

## 何が起きているか

肌の内部で光は散乱しながら進み少しずつ吸収されます。薄い部位では反対側から入った光が、<strong>吸収されきる前に</strong>こちら側の表面にたどり着けます。吸収されやすさは色で違います。赤は吸収されにくく緑や青は吸収されやすいので、通り抜けた光は <strong>赤みを帯びます</strong>。耳を光に透かすと赤橙色に見えるのは、そのためです。

必要な計算は「点 P に裏側から入った光が、肌の中を通って P まで届く量」です。この量は <strong>光が肌の中を通った距離 s</strong>（厚み）で決まります。

* 厚みが小さい（薄い）→ 光が強く届く。
* 厚みが大きい（厚い）→ 光は弱く、赤だけが残る。

したがって各点 P で光の方向に沿った<strong>肌の厚み s</strong>を知る必要があります。

## シャドウ マップで厚みを測る

厚みを知る方法として <strong>シャドウ マップ</strong>が利用できます。シャドウ マップは光から見た最も手前の面までの距離を保存しています。

点 P が光に照らされていない側（影の側）にあるとします。光から見て P の前に光に近い側の肌の面があります。シャドウ マップに保存された距離 d₁（光から、手前の面まで）と P の光からの距離 d₂ の差が、<strong>光が肌の中を通った距離</strong>、つまり厚みになります。

<div class="formula">s = d₂ − d₁　（光から見た P の距離 − シャドウ マップの距離）</div>

d₁ と d₂ はシャドウ マップをサンプルするときの光空間の座標から得られます。この方法はほぼ追加コスト無しで、シャドウ マップの 1 回の読み込みで済みます。

```hlsl
float Thickness(float3 world_pos, float3 normal) {
  float3 offset_pos = world_pos - normal * kNormalOffset;
  float4 light_pos = mul(float4(offset_pos, 1.0), light_view_projection);
  float2 uv = light_pos.xy / light_pos.w * float2(0.5, -0.5) + 0.5;
  float d1 = shadow_depth_tex.SampleLevel(point_clamp, uv, 0).r;
  float d2 = light_pos.z / light_pos.w;
  return abs(LinearizeLightDepth(d2) - LinearizeLightDepth(d1));
}
```

`kNormalOffset` は P を法線の逆向き（肌の内側）に少しずらすための値です。P が表面ちょうどにあるとシャドウ マップの値と区別できず自己影のノイズが出るからです。

<!-- fig:thin-transmit:begin -->

<svg class="fig illust motion" data-fig="thin-transmit" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-thin-transmit" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">薄い物の透過光: 耳や葉が、後ろからの光で、赤く(緑に)透ける</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">耳の断面(厚さの違うところ)を、後ろから照らす。色ごとに「厚さに応じて」光が減る(ベールの法則)</text>
<rect x="30" y="96" width="392.0" height="196.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 厚さ(濃い = 厚い)</text>
<rect x="30.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="86.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="100.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="114.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="128.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="142.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="156.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="170.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="184.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="198.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="212.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="226.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="240.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="254.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="268.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="282.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="296.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="310.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="324.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="338.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="352.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="366.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="380.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="96.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="86.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="100.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="114.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="128.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#eff2f5"/></rect>
<rect x="142.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d7dbe1"/></rect>
<rect x="156.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c8cdd4"/></rect>
<rect x="170.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#bec3cb"/></rect>
<rect x="184.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b6bdc5"/></rect>
<rect x="198.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b1b8c1"/></rect>
<rect x="212.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#afb6bf"/></rect>
<rect x="226.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#afb6bf"/></rect>
<rect x="240.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b1b8c1"/></rect>
<rect x="254.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b6bdc5"/></rect>
<rect x="268.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#bec3cb"/></rect>
<rect x="282.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c8cdd4"/></rect>
<rect x="296.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d7dbe1"/></rect>
<rect x="310.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#eff2f5"/></rect>
<rect x="324.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="338.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="352.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="366.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="380.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="110.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="86.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="100.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#e0e3e8"/></rect>
<rect x="114.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c7ccd3"/></rect>
<rect x="128.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bbc4"/></rect>
<rect x="142.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a7afb9"/></rect>
<rect x="156.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca4b0"/></rect>
<rect x="170.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="184.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8e97a4"/></rect>
<rect x="198.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8a94a1"/></rect>
<rect x="212.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#88929f"/></rect>
<rect x="226.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#88929f"/></rect>
<rect x="240.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8a94a1"/></rect>
<rect x="254.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8e97a4"/></rect>
<rect x="268.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="282.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca4b0"/></rect>
<rect x="296.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a7afb9"/></rect>
<rect x="310.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bbc4"/></rect>
<rect x="324.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c7ccd3"/></rect>
<rect x="338.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#e0e3e8"/></rect>
<rect x="352.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="366.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="380.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="124.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f4f6f9"/></rect>
<rect x="86.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cdd2d8"/></rect>
<rect x="100.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bcc5"/></rect>
<rect x="114.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a3abb5"/></rect>
<rect x="128.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="142.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#89929f"/></rect>
<rect x="156.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8998"/></rect>
<rect x="170.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#788291"/></rect>
<rect x="184.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#727d8d"/></rect>
<rect x="198.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6f7a8a"/></rect>
<rect x="212.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6d7889"/></rect>
<rect x="226.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6d7889"/></rect>
<rect x="240.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6f7a8a"/></rect>
<rect x="254.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#727d8d"/></rect>
<rect x="268.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#788291"/></rect>
<rect x="282.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8998"/></rect>
<rect x="296.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#89929f"/></rect>
<rect x="310.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="324.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a3abb5"/></rect>
<rect x="338.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bcc5"/></rect>
<rect x="352.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cdd2d8"/></rect>
<rect x="366.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f4f6f9"/></rect>
<rect x="380.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="138.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f3f6f8"/></rect>
<rect x="72.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd6"/></rect>
<rect x="86.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b0b7c1"/></rect>
<rect x="100.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca5b0"/></rect>
<rect x="114.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8c96a3"/></rect>
<rect x="128.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8997"/></rect>
<rect x="142.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#747f8e"/></rect>
<rect x="156.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7787"/></rect>
<rect x="170.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#647081"/></rect>
<rect x="184.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5f6b7d"/></rect>
<rect x="198.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5c687a"/></rect>
<rect x="212.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5a6779"/></rect>
<rect x="226.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5a6779"/></rect>
<rect x="240.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5c687a"/></rect>
<rect x="254.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5f6b7d"/></rect>
<rect x="268.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#647081"/></rect>
<rect x="282.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7787"/></rect>
<rect x="296.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#747f8e"/></rect>
<rect x="310.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8997"/></rect>
<rect x="324.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8c96a3"/></rect>
<rect x="338.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca5b0"/></rect>
<rect x="352.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b0b7c1"/></rect>
<rect x="366.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd6"/></rect>
<rect x="380.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f3f6f8"/></rect>
<rect x="394.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="152.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d5d9df"/></rect>
<rect x="72.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b7bdc6"/></rect>
<rect x="86.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a0a8b3"/></rect>
<rect x="100.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8d97a4"/></rect>
<rect x="114.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7e8897"/></rect>
<rect x="128.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#717d8c"/></rect>
<rect x="142.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#677383"/></rect>
<rect x="156.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5e6b7c"/></rect>
<rect x="170.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="184.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#536073"/></rect>
<rect x="198.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4f5d70"/></rect>
<rect x="212.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4e5b6f"/></rect>
<rect x="226.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4e5b6f"/></rect>
<rect x="240.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4f5d70"/></rect>
<rect x="254.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#536073"/></rect>
<rect x="268.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="282.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5e6b7c"/></rect>
<rect x="296.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#677383"/></rect>
<rect x="310.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#717d8c"/></rect>
<rect x="324.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7e8897"/></rect>
<rect x="338.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8d97a4"/></rect>
<rect x="352.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a0a8b3"/></rect>
<rect x="366.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b7bdc6"/></rect>
<rect x="380.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d5d9df"/></rect>
<rect x="394.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="166.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd5"/></rect>
<rect x="72.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#aeb5be"/></rect>
<rect x="86.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#98a1ac"/></rect>
<rect x="100.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#86909e"/></rect>
<rect x="114.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#778291"/></rect>
<rect x="128.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7687"/></rect>
<rect x="142.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#616d7e"/></rect>
<rect x="156.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="170.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#525f72"/></rect>
<rect x="184.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4d5a6e"/></rect>
<rect x="198.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4a576b"/></rect>
<rect x="212.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#48566a"/></rect>
<rect x="226.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#48566a"/></rect>
<rect x="240.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4a576b"/></rect>
<rect x="254.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4d5a6e"/></rect>
<rect x="268.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#525f72"/></rect>
<rect x="282.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="296.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#616d7e"/></rect>
<rect x="310.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7687"/></rect>
<rect x="324.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#778291"/></rect>
<rect x="338.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#86909e"/></rect>
<rect x="352.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#98a1ac"/></rect>
<rect x="366.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#aeb5be"/></rect>
<rect x="380.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd5"/></rect>
<rect x="394.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="180.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd5"/></rect>
<rect x="72.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#aeb5be"/></rect>
<rect x="86.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#98a1ac"/></rect>
<rect x="100.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#86909e"/></rect>
<rect x="114.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#778291"/></rect>
<rect x="128.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7687"/></rect>
<rect x="142.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#616d7e"/></rect>
<rect x="156.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="170.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#525f72"/></rect>
<rect x="184.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4d5a6e"/></rect>
<rect x="198.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4a576b"/></rect>
<rect x="212.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#48566a"/></rect>
<rect x="226.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#48566a"/></rect>
<rect x="240.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4a576b"/></rect>
<rect x="254.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4d5a6e"/></rect>
<rect x="268.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#525f72"/></rect>
<rect x="282.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="296.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#616d7e"/></rect>
<rect x="310.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7687"/></rect>
<rect x="324.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#778291"/></rect>
<rect x="338.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#86909e"/></rect>
<rect x="352.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#98a1ac"/></rect>
<rect x="366.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#aeb5be"/></rect>
<rect x="380.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd5"/></rect>
<rect x="394.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="194.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d5d9df"/></rect>
<rect x="72.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b7bdc6"/></rect>
<rect x="86.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a0a8b3"/></rect>
<rect x="100.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8d97a4"/></rect>
<rect x="114.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7e8897"/></rect>
<rect x="128.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#717d8c"/></rect>
<rect x="142.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#677383"/></rect>
<rect x="156.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5e6b7c"/></rect>
<rect x="170.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="184.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#536073"/></rect>
<rect x="198.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4f5d70"/></rect>
<rect x="212.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4e5b6f"/></rect>
<rect x="226.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4e5b6f"/></rect>
<rect x="240.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#4f5d70"/></rect>
<rect x="254.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#536073"/></rect>
<rect x="268.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#586577"/></rect>
<rect x="282.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5e6b7c"/></rect>
<rect x="296.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#677383"/></rect>
<rect x="310.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#717d8c"/></rect>
<rect x="324.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7e8897"/></rect>
<rect x="338.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8d97a4"/></rect>
<rect x="352.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a0a8b3"/></rect>
<rect x="366.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b7bdc6"/></rect>
<rect x="380.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d5d9df"/></rect>
<rect x="394.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="208.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f3f6f8"/></rect>
<rect x="72.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd6"/></rect>
<rect x="86.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b0b7c1"/></rect>
<rect x="100.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca5b0"/></rect>
<rect x="114.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8c96a3"/></rect>
<rect x="128.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8997"/></rect>
<rect x="142.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#747f8e"/></rect>
<rect x="156.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7787"/></rect>
<rect x="170.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#647081"/></rect>
<rect x="184.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5f6b7d"/></rect>
<rect x="198.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5c687a"/></rect>
<rect x="212.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5a6779"/></rect>
<rect x="226.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5a6779"/></rect>
<rect x="240.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5c687a"/></rect>
<rect x="254.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#5f6b7d"/></rect>
<rect x="268.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#647081"/></rect>
<rect x="282.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6b7787"/></rect>
<rect x="296.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#747f8e"/></rect>
<rect x="310.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8997"/></rect>
<rect x="324.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8c96a3"/></rect>
<rect x="338.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca5b0"/></rect>
<rect x="352.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b0b7c1"/></rect>
<rect x="366.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cacfd6"/></rect>
<rect x="380.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f3f6f8"/></rect>
<rect x="394.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="222.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f4f6f9"/></rect>
<rect x="86.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cdd2d8"/></rect>
<rect x="100.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bcc5"/></rect>
<rect x="114.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a3abb5"/></rect>
<rect x="128.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="142.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#89929f"/></rect>
<rect x="156.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8998"/></rect>
<rect x="170.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#788291"/></rect>
<rect x="184.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#727d8d"/></rect>
<rect x="198.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6f7a8a"/></rect>
<rect x="212.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6d7889"/></rect>
<rect x="226.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6d7889"/></rect>
<rect x="240.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#6f7a8a"/></rect>
<rect x="254.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#727d8d"/></rect>
<rect x="268.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#788291"/></rect>
<rect x="282.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#7f8998"/></rect>
<rect x="296.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#89929f"/></rect>
<rect x="310.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="324.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a3abb5"/></rect>
<rect x="338.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bcc5"/></rect>
<rect x="352.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#cdd2d8"/></rect>
<rect x="366.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#f4f6f9"/></rect>
<rect x="380.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="236.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="86.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="100.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#e0e3e8"/></rect>
<rect x="114.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c7ccd3"/></rect>
<rect x="128.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bbc4"/></rect>
<rect x="142.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a7afb9"/></rect>
<rect x="156.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca4b0"/></rect>
<rect x="170.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="184.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8e97a4"/></rect>
<rect x="198.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8a94a1"/></rect>
<rect x="212.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#88929f"/></rect>
<rect x="226.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#88929f"/></rect>
<rect x="240.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8a94a1"/></rect>
<rect x="254.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#8e97a4"/></rect>
<rect x="268.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#949da9"/></rect>
<rect x="282.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#9ca4b0"/></rect>
<rect x="296.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#a7afb9"/></rect>
<rect x="310.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b5bbc4"/></rect>
<rect x="324.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c7ccd3"/></rect>
<rect x="338.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#e0e3e8"/></rect>
<rect x="352.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="366.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="380.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="250.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="86.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="100.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="114.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="128.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#eff2f5"/></rect>
<rect x="142.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d7dbe1"/></rect>
<rect x="156.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c8cdd4"/></rect>
<rect x="170.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#bec3cb"/></rect>
<rect x="184.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b6bdc5"/></rect>
<rect x="198.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b1b8c1"/></rect>
<rect x="212.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#afb6bf"/></rect>
<rect x="226.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#afb6bf"/></rect>
<rect x="240.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b1b8c1"/></rect>
<rect x="254.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#b6bdc5"/></rect>
<rect x="268.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#bec3cb"/></rect>
<rect x="282.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#c8cdd4"/></rect>
<rect x="296.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#d7dbe1"/></rect>
<rect x="310.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0233" values="#f8fafc;#eff2f5"/></rect>
<rect x="324.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="338.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="352.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="366.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="380.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="264.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="30.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="44.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="58.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="72.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="86.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="100.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="114.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="128.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="142.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="156.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="170.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="184.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="198.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="212.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="226.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="240.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="254.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="268.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="282.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="296.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="310.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="324.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="338.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="352.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="366.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="380.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="394.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="408.0" y="278.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="462.0" y="96" width="392.0" height="196.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="462.0" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">② 後ろから光を当てたときの色</text>
<rect x="462.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="518.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="532.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="546.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="560.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="574.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="588.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="602.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="616.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="630.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="644.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="658.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="672.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="686.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="700.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="714.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="728.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="742.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="756.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="770.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="784.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="798.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="812.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="96.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="518.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="532.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="546.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="560.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#ffffca"/></rect>
<rect x="574.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#fea850"/></rect>
<rect x="588.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#e17e2d"/></rect>
<rect x="602.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#cf671e"/></rect>
<rect x="616.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#c35917"/></rect>
<rect x="630.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#bb5213"/></rect>
<rect x="644.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#b84e11"/></rect>
<rect x="658.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#b84e11"/></rect>
<rect x="672.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#bb5213"/></rect>
<rect x="686.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#c35917"/></rect>
<rect x="700.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#cf671e"/></rect>
<rect x="714.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#e17e2d"/></rect>
<rect x="728.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#fea850"/></rect>
<rect x="742.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#ffffca"/></rect>
<rect x="756.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="770.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="784.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="798.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="812.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="110.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="518.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="532.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#ffc670"/></rect>
<rect x="546.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#df7b2b"/></rect>
<rect x="560.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#c15716"/></rect>
<rect x="574.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#ac430d"/></rect>
<rect x="588.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#9e3708"/></rect>
<rect x="602.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#942f06"/></rect>
<rect x="616.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#8d2a05"/></rect>
<rect x="630.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#882704"/></rect>
<rect x="644.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#862504"/></rect>
<rect x="658.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#862504"/></rect>
<rect x="672.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#882704"/></rect>
<rect x="686.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#8d2a05"/></rect>
<rect x="700.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#942f06"/></rect>
<rect x="714.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#9e3708"/></rect>
<rect x="728.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#ac430d"/></rect>
<rect x="742.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#c15716"/></rect>
<rect x="756.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#df7b2b"/></rect>
<rect x="770.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#ffc670"/></rect>
<rect x="784.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="798.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="812.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="124.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fffff2"/></rect>
<rect x="518.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#ea8b37"/></rect>
<rect x="532.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#c25816"/></rect>
<rect x="546.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#a73e0b"/></rect>
<rect x="560.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#942f06"/></rect>
<rect x="574.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#872504"/></rect>
<rect x="588.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#7d1f03"/></rect>
<rect x="602.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#761b02"/></rect>
<rect x="616.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#711802"/></rect>
<rect x="630.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#6d1701"/></rect>
<rect x="644.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#6c1601"/></rect>
<rect x="658.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#6c1601"/></rect>
<rect x="672.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#6d1701"/></rect>
<rect x="686.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#711802"/></rect>
<rect x="700.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#761b02"/></rect>
<rect x="714.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#7d1f03"/></rect>
<rect x="728.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#872504"/></rect>
<rect x="742.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#942f06"/></rect>
<rect x="756.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#a73e0b"/></rect>
<rect x="770.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#c25816"/></rect>
<rect x="784.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#ea8b37"/></rect>
<rect x="798.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#fffff2"/></rect>
<rect x="812.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="138.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#ffffeb"/></rect>
<rect x="504.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#e48330"/></rect>
<rect x="518.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#ba5012"/></rect>
<rect x="532.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#9e3709"/></rect>
<rect x="546.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#8b2805"/></rect>
<rect x="560.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#7d1f03"/></rect>
<rect x="574.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#721902"/></rect>
<rect x="588.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#6a1501"/></rect>
<rect x="602.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#641301"/></rect>
<rect x="616.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#601101"/></rect>
<rect x="630.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#5e1001"/></rect>
<rect x="644.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#5c0f01"/></rect>
<rect x="658.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#5c0f01"/></rect>
<rect x="672.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#5e1001"/></rect>
<rect x="686.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#601101"/></rect>
<rect x="700.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#641301"/></rect>
<rect x="714.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#6a1501"/></rect>
<rect x="728.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#721902"/></rect>
<rect x="742.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#7d1f03"/></rect>
<rect x="756.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#8b2805"/></rect>
<rect x="770.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#9e3709"/></rect>
<rect x="784.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#ba5012"/></rect>
<rect x="798.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#e48330"/></rect>
<rect x="812.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#0f172a;#ffffeb"/></rect>
<rect x="826.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="152.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#f9a049"/></rect>
<rect x="504.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#c35a17"/></rect>
<rect x="518.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#a33b0a"/></rect>
<rect x="532.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#8c2905"/></rect>
<rect x="546.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#7c1f03"/></rect>
<rect x="560.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#701802"/></rect>
<rect x="574.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#671401"/></rect>
<rect x="588.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#601101"/></rect>
<rect x="602.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#5b0f01"/></rect>
<rect x="616.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#570d01"/></rect>
<rect x="630.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#550d00"/></rect>
<rect x="644.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#540c00"/></rect>
<rect x="658.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#540c00"/></rect>
<rect x="672.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#550d00"/></rect>
<rect x="686.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#570d01"/></rect>
<rect x="700.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#5b0f01"/></rect>
<rect x="714.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#601101"/></rect>
<rect x="728.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#671401"/></rect>
<rect x="742.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#701802"/></rect>
<rect x="756.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#7c1f03"/></rect>
<rect x="770.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#8c2905"/></rect>
<rect x="784.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#a33b0a"/></rect>
<rect x="798.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#c35a17"/></rect>
<rect x="812.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#0f172a;#f9a049"/></rect>
<rect x="826.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="166.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#e48230"/></rect>
<rect x="504.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#b64c11"/></rect>
<rect x="518.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#993207"/></rect>
<rect x="532.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#842404"/></rect>
<rect x="546.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#751b02"/></rect>
<rect x="560.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#6a1501"/></rect>
<rect x="574.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#621101"/></rect>
<rect x="588.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#5b0f01"/></rect>
<rect x="602.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#560d00"/></rect>
<rect x="616.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#530c00"/></rect>
<rect x="630.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#510b00"/></rect>
<rect x="644.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#500b00"/></rect>
<rect x="658.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#500b00"/></rect>
<rect x="672.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#510b00"/></rect>
<rect x="686.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#530c00"/></rect>
<rect x="700.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#560d00"/></rect>
<rect x="714.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#5b0f01"/></rect>
<rect x="728.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#621101"/></rect>
<rect x="742.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#6a1501"/></rect>
<rect x="756.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#751b02"/></rect>
<rect x="770.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#842404"/></rect>
<rect x="784.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#993207"/></rect>
<rect x="798.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#b64c11"/></rect>
<rect x="812.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#0f172a;#e48230"/></rect>
<rect x="826.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="180.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#e48230"/></rect>
<rect x="504.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#b64c11"/></rect>
<rect x="518.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#993207"/></rect>
<rect x="532.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#842404"/></rect>
<rect x="546.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#751b02"/></rect>
<rect x="560.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#6a1501"/></rect>
<rect x="574.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#621101"/></rect>
<rect x="588.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#5b0f01"/></rect>
<rect x="602.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#560d00"/></rect>
<rect x="616.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#530c00"/></rect>
<rect x="630.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#510b00"/></rect>
<rect x="644.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#500b00"/></rect>
<rect x="658.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#500b00"/></rect>
<rect x="672.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#510b00"/></rect>
<rect x="686.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#530c00"/></rect>
<rect x="700.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#560d00"/></rect>
<rect x="714.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#5b0f01"/></rect>
<rect x="728.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#621101"/></rect>
<rect x="742.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#6a1501"/></rect>
<rect x="756.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#751b02"/></rect>
<rect x="770.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#842404"/></rect>
<rect x="784.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#993207"/></rect>
<rect x="798.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#b64c11"/></rect>
<rect x="812.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#0f172a;#e48230"/></rect>
<rect x="826.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="194.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#f9a049"/></rect>
<rect x="504.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#c35a17"/></rect>
<rect x="518.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#a33b0a"/></rect>
<rect x="532.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#8c2905"/></rect>
<rect x="546.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#7c1f03"/></rect>
<rect x="560.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#701802"/></rect>
<rect x="574.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#671401"/></rect>
<rect x="588.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#601101"/></rect>
<rect x="602.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#5b0f01"/></rect>
<rect x="616.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#570d01"/></rect>
<rect x="630.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#550d00"/></rect>
<rect x="644.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#540c00"/></rect>
<rect x="658.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#540c00"/></rect>
<rect x="672.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#550d00"/></rect>
<rect x="686.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#570d01"/></rect>
<rect x="700.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#5b0f01"/></rect>
<rect x="714.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#601101"/></rect>
<rect x="728.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#671401"/></rect>
<rect x="742.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#701802"/></rect>
<rect x="756.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#7c1f03"/></rect>
<rect x="770.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#8c2905"/></rect>
<rect x="784.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#a33b0a"/></rect>
<rect x="798.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#c35a17"/></rect>
<rect x="812.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#0f172a;#f9a049"/></rect>
<rect x="826.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="208.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#ffffeb"/></rect>
<rect x="504.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#e48330"/></rect>
<rect x="518.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#ba5012"/></rect>
<rect x="532.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#9e3709"/></rect>
<rect x="546.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#8b2805"/></rect>
<rect x="560.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#7d1f03"/></rect>
<rect x="574.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#721902"/></rect>
<rect x="588.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#6a1501"/></rect>
<rect x="602.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#641301"/></rect>
<rect x="616.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#601101"/></rect>
<rect x="630.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#5e1001"/></rect>
<rect x="644.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#5c0f01"/></rect>
<rect x="658.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#5c0f01"/></rect>
<rect x="672.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#5e1001"/></rect>
<rect x="686.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#601101"/></rect>
<rect x="700.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#641301"/></rect>
<rect x="714.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#6a1501"/></rect>
<rect x="728.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#721902"/></rect>
<rect x="742.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#7d1f03"/></rect>
<rect x="756.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#8b2805"/></rect>
<rect x="770.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#9e3709"/></rect>
<rect x="784.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#ba5012"/></rect>
<rect x="798.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#e48330"/></rect>
<rect x="812.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#0f172a;#ffffeb"/></rect>
<rect x="826.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="222.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fffff2"/></rect>
<rect x="518.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#ea8b37"/></rect>
<rect x="532.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#c25816"/></rect>
<rect x="546.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#a73e0b"/></rect>
<rect x="560.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#942f06"/></rect>
<rect x="574.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#872504"/></rect>
<rect x="588.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#7d1f03"/></rect>
<rect x="602.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#761b02"/></rect>
<rect x="616.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#711802"/></rect>
<rect x="630.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#6d1701"/></rect>
<rect x="644.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#6c1601"/></rect>
<rect x="658.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#6c1601"/></rect>
<rect x="672.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#6d1701"/></rect>
<rect x="686.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#711802"/></rect>
<rect x="700.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#761b02"/></rect>
<rect x="714.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#7d1f03"/></rect>
<rect x="728.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#872504"/></rect>
<rect x="742.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#942f06"/></rect>
<rect x="756.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#a73e0b"/></rect>
<rect x="770.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#c25816"/></rect>
<rect x="784.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#ea8b37"/></rect>
<rect x="798.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#fffff2"/></rect>
<rect x="812.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="236.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="518.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="532.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#ffc670"/></rect>
<rect x="546.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#df7b2b"/></rect>
<rect x="560.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#c15716"/></rect>
<rect x="574.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#ac430d"/></rect>
<rect x="588.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#9e3708"/></rect>
<rect x="602.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#942f06"/></rect>
<rect x="616.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#8d2a05"/></rect>
<rect x="630.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#882704"/></rect>
<rect x="644.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#862504"/></rect>
<rect x="658.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#862504"/></rect>
<rect x="672.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#882704"/></rect>
<rect x="686.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#8d2a05"/></rect>
<rect x="700.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#942f06"/></rect>
<rect x="714.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#9e3708"/></rect>
<rect x="728.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#ac430d"/></rect>
<rect x="742.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#c15716"/></rect>
<rect x="756.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#df7b2b"/></rect>
<rect x="770.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#ffc670"/></rect>
<rect x="784.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="798.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="812.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="250.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="518.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="532.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="546.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="560.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#ffffca"/></rect>
<rect x="574.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#fea850"/></rect>
<rect x="588.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#e17e2d"/></rect>
<rect x="602.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#cf671e"/></rect>
<rect x="616.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#c35917"/></rect>
<rect x="630.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#bb5213"/></rect>
<rect x="644.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#b84e11"/></rect>
<rect x="658.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#b84e11"/></rect>
<rect x="672.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#bb5213"/></rect>
<rect x="686.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#c35917"/></rect>
<rect x="700.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#cf671e"/></rect>
<rect x="714.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#e17e2d"/></rect>
<rect x="728.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#fea850"/></rect>
<rect x="742.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#ffffca"/></rect>
<rect x="756.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="770.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="784.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="798.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="812.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="264.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="462.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="476.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="490.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="504.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="518.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="532.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="546.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="560.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="574.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="588.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="602.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="616.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="630.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="644.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="658.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="672.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="686.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="700.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="714.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="728.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="742.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="756.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="770.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="784.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="798.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="812.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="826.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="840.0" y="278.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="30" y="316" width="440" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="306" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">③ 中央の行での、色ごとに通り抜ける光の割合</text>
<path d="M79.63,364.39 L94.44,379.57 L109.26,389.3 L124.07,396.12 L138.89,401.1 L153.7,404.83 L168.52,407.65 L183.33,409.76 L198.15,411.33 L212.96,412.43 L227.78,413.13 L242.59,413.48 L257.41,413.48 L272.22,413.13 L287.04,412.43 L301.85,411.33 L316.67,409.76 L331.48,407.65 L346.3,404.83 L361.11,401.1 L375.93,396.12 L390.74,389.3 L405.56,379.57 L420.37,364.39" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1663;0.1665;1.0000" values="0;0;1;1"/></path>
<text x="455" y="417.47696620936614" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">R<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1663;0.1665;1.0000" values="0;0;1;1"/></text>
<path d="M79.63,394.65 L94.44,413.3 L109.26,422.37 L124.07,427.47 L138.89,430.57 L153.7,432.57 L168.52,433.9 L183.33,434.8 L198.15,435.42 L212.96,435.82 L227.78,436.07 L242.59,436.19 L257.41,436.19 L272.22,436.07 L287.04,435.82 L301.85,435.42 L316.67,434.8 L331.48,433.9 L346.3,432.57 L361.11,430.57 L375.93,427.47 L390.74,422.37 L405.56,413.3 L420.37,394.65" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2035;0.2037;1.0000" values="0;0;1;1"/></path>
<text x="455" y="440.18749640081273" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">G<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2035;0.2037;1.0000" values="0;0;1;1"/></text>
<path d="M79.63,421.3 L94.44,433.52 L109.26,437.17 L124.07,438.57 L138.89,439.19 L153.7,439.5 L168.52,439.66 L183.33,439.75 L198.15,439.81 L212.96,439.84 L227.78,439.86 L242.59,439.87 L257.41,439.87 L272.22,439.86 L287.04,439.84 L301.85,439.81 L316.67,439.75 L331.48,439.66 L346.3,439.5 L361.11,439.19 L375.93,438.57 L390.74,437.17 L405.56,433.52 L420.37,421.3" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2407;0.2409;1.0000" values="0;0;1;1"/></path>
<text x="455" y="443.86786196641987" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">B<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2407;0.2409;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2873;0.2874;1.0000" values="0;0;1;1"/><rect x="490" y="330" width="440" height="136" rx="12" fill="#faf5ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="506" y="354" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">ふちの薄い所(厚さ 1.1): R 55% / G 24% / B 6%</text>
<text x="506" y="377" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">真ん中の厚い所(厚さ 2.6): R 24% / G 3% / B 0%</text>
<text x="506" y="400" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">厚いほど、青 → 緑 → 赤の順に光が減り、赤が残る</text>
<text x="506" y="422" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">(ゲームでは、厚さを、事前に焼いた画像で持つ)</text>
</g>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">耳のように薄い所は、後ろの光が、肉を通り抜けてくる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">各画素の厚さから、色ごとの光の減り方を計算する<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.1477;0.1479;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">青はすぐ消え、赤が最後まで残る<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1477;0.1479;0.2873;0.2874;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ふちは明るく、真ん中は暗い赤。これが、耳が赤く透ける理由<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2873;0.2874;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:thin-transmit:end -->

## 厚みから透過光へ

厚み s から透過する光の量を計算します。これは <strong>拡散プロファイルを厚みの関数にしたもの</strong>です。肌の内部を距離 s だけ光が通り抜けたときどれだけ光が残るかを表します。Jimenez らはこれを拡散プロファイル R(r) の近似に使うガウスの和で、そのまま表せることを示しました。

<div class="formula">T(s) = Σᵢ wᵢ · exp(−s² / vᵢ)</div>

w_i と v_i は[Diffusion Profiles](diffusion-profile.md) のガウスの和と同じ重みと分散です。RGB ごとに別の重みを持つので、厚みが増えるにつれて青、緑の順に消え赤が残ります。ガウスの 6 項をそのまま使うと重いので、肌の透過に効く広い分散のガウス 3〜4 項に絞るのが一般的です。

```hlsl
float3 Transmittance(float s) {
  float s2 = s * s;
  return float3(0.233, 0.455, 0.649) * exp(-s2 / 0.0064) +
         float3(0.100, 0.336, 0.344) * exp(-s2 / 0.0484) +
         float3(0.118, 0.198, 0.000) * exp(-s2 / 0.187) +
         float3(0.113, 0.007, 0.007) * exp(-s2 / 0.567) +
         float3(0.358, 0.004, 0.000) * exp(-s2 / 1.99) +
         float3(0.078, 0.000, 0.000) * exp(-s2 / 7.41);
}
```

厚みの単位は mm です。シャドウ マップから得た距離が m 単位なら変換が必要です。

## 最終的な組み立て

透過した光を肌の色に反映して、拡散反射に足します。

```hlsl
float3 TransmittedLight(float3 world_pos, float3 normal, float3 light_dir, float3 light_color, float3 albedo) {
  float s = Thickness(world_pos, normal) * kMetersToMillimeters;
  float3 t = Transmittance(s);
  float back_lit = saturate(dot(-normal, light_dir));
  return t * back_lit * albedo * light_color;
}
```

`back_lit` は光が裏側から当たっているか（法線の裏が光を向くか）の係数です。表側が光を向いている場合は通常の拡散反射に任せて、`back_lit` で透過の寄与を 0 にします。反対に表側が影の側のときだけ透過が効きます。

## より良いやり方

厚みを求める方法にはいくつかの改良があります。

<strong>法線の向きに応じた補正</strong>。光が斜めに当たると実際に肌の中を通る距離は、垂直に通る距離より長くなります。厚み s を光と法線のなす角（`N·L`）で補正すると、斜めの場合の過剰な透過を抑えられます。

<strong>厚みマップ</strong>。シャドウ マップが使えない場合やシャドウを描かないライトに対しては、事前に計算した<strong>厚みマップ</strong>（キャラクターの UV に焼いたテクスチャ）を使います。耳や鼻、指で厚みが小さく頭の中心部で大きくなるようにキャラクターを作るときにベイクします。実行時の計算はマップを 1 回引くだけで済みシャドウ マップに依らない分、安定します。

<strong>画面空間のぼかしと併用</strong>。透過光は表面の光と同じ散乱を受けるので、透過光の結果も SSS のぼかしの対象に含めると、自然になじみます。

## よくあるミス

??? failure "耳が光の側でも赤く透けて、不自然"
    透過は <strong>表側が影の側（光が裏から当たる）</strong>のときだけ。`dot(-N, L)` で重みを掛けて <strong>光が表から当たるときは 0</strong> にする。

??? failure "透過がノイズだらけでちらつく"
    P が表面ちょうどにあると、シャドウ マップと比べたときに自己影が出る。<strong>法線の逆向きに少しずらして</strong>サンプルする。<strong>シャドウ マップを PCF やぼかしで滑らかに</strong>サンプルする。

??? failure "厚みの単位が合わず透過が強すぎる・弱すぎる"
    ガウスの分散は <strong>mm²</strong>。距離を <strong>mm に変換</strong>してから入れる。

??? failure "厚い頭の中央まで、光が透けて見える"
    ガウスの広い項を入れすぎている。<strong>s が大きいときに T が十分小さくなる</strong>ように項を絞る。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 薄い部位は<strong>裏から入った光が透ける</strong>。赤みを帯びる
    - [x] 厚みは<strong>シャドウ マップの距離の差</strong>で測る
    - [x] 透過率は<strong>ガウスの和 T(s) = Σ w exp(−s²/v)</strong>。厚いほど赤だけが残る
    - [x] 表が影の側のときだけ効かせる。厚みマップで代用もできる

## 参考

- Jimenez, Whelan, Sundstedt, Gutierrez, "Real-Time Realistic Skin Translucency"（IEEE Computer Graphics and Applications, 2010）
- d'Eon, Luebke, "Advanced Techniques for Realistic Real-Time Skin Rendering"（GPU Gems 3, 2007）

## 関連ページ

- [Skin Overview](index.md)
- [Diffusion Profiles](diffusion-profile.md)
- [Separable SSS](screen-space-sss.md)
- [Shadow Map Basics](../../shadows/shadow-map-basics/index.md)
