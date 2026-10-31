---
title: Foreground and Background
tags:
  - 描画
---

# Foreground and Background

<strong>DOF の難しさは、「ピントの手前（前景）」と「奥（背景）」で、ぼけ方の理屈が違う</strong>ことです。背景のボケはピントが合った物の「後ろ」にあるので手前の物を隠さないですが、前景のボケはピントが合った物の「手前」にあるのでその物の上に広がってかぶさります。これを分けて処理しないと、ボケた前景の輪郭がきつくなったり、ピント内の物に背景がにじんだりします。このページでは、前景と背景の違い・別々に処理する方法・近傍の最大 CoC（タイル）・合成・よくある破綻を説明します。

!!! tip "ポイント"
    - <strong>背景のボケ</strong>は<strong>ピント内の物にかぶらない</strong>。前景のボケは奥の物の上に広がる。
    - CoC を符号付きで持ち（前景は負）、前景・背景を別々に処理する。
    - 前景は「周りの最大 CoC」を使う（前景の輪郭の外側にまでボケが広がるため）。タイルで高速化。
    - 前景のボケは、アルファ（透け具合）つきで最後に合成する。
    - 背景はピント内の物を貫通しないように、重みを制御。
    - 半解像度でも前景と背景は分けて保存する。

!!! info "このページを読む前に"
    - [Depth of Field (DOF)](index.md)（このセクション全体の地図と、読む順番）

## 前景と背景の違い

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="前景と背景のボケ">
<text x="20" y="26" class="fig-title">ぼけた前景は奥へ広がる、ぼけた背景は手前の物を隠さない</text>
<g transform="translate(40,56)">
<text x="0" y="-10" style="font-size:13px;font-weight:700">背景がぼける</text>
<rect x="0" y="0" width="300" height="130" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="150" cy="65" r="22" fill="#2563eb"/>
<circle cx="100" cy="40" r="26" fill="#e5484d" fill-opacity="0.45"/>
<circle cx="220" cy="90" r="30" fill="#e5aa28" fill-opacity="0.45"/>
<text x="0" y="152" style="font-size:12px">ピント内（青）は輪郭がくっきり、</text><text x="0" y="170" style="font-size:12px">ボケた背景は後ろに広がる</text>
</g>
<g transform="translate(420,56)">
<text x="0" y="-10" style="font-size:13px;font-weight:700">前景がぼける</text>
<rect x="0" y="0" width="300" height="130" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="150" cy="65" r="22" fill="#2563eb"/>
<circle cx="130" cy="60" r="52" fill="#e5484d" fill-opacity="0.3"/>
<text x="0" y="152" style="font-size:12px">ぼけた前景は、ピント内の物の上に</text><text x="0" y="170" style="font-size:12px">かぶさって広がる（透けて見える）</text>
</g>
</svg>

| 項目 | 背景 | 前景 |
| --- | --- | --- |
| ボケの広がる向き | 奥の物の周り | 手前の物の輪郭の外へ奥にかぶさる |
| ピント内の物との関係 | ピント内の物は、手前にあるので隠れない | ピント内の物の上に広がる |
| ボケた縁 | ピント内の物の縁できっぱり切れる | 縁がやわらかく、透ける |

## 別々に処理する

<strong>CoC の符号</strong>で前景と背景に分け、別々にぼかし、最後に合成します。

| 手順 | 内容 |
| --- | --- |
| ① 前景と背景に分ける | CoC < 0 を前景、CoC > 0 を背景（ピント内（|CoC| が小さい）は、そのまま） |
| ② 背景をぼかす | ピント内の物の色が混ざらないよう、重みを制御 |
| ③ 前景をぼかす | 近傍の最大 CoC を使い、前景の外にも広げる。アルファ付き |
| ④ 合成 | 背景 → ピント内 → 前景（アルファで上に）の順 |

```hlsl
float3 CompositeDof(float3 sharp, float4 far_blur, float4 near_blur, float coc) {
  float far_alpha = saturate(coc);
  float3 color = lerp(sharp, far_blur.rgb, far_alpha);
  color = lerp(color, near_blur.rgb, near_blur.a);
  return color;
}
```

合成のコードの要点です。`far_alpha = saturate(coc)` で、背景のボケは CoC が大きいほど強く混ぜます。`near_blur.a` は前景のぼけた濃さで、ぼけた輪郭の外側は薄く透けます。最後に前景を重ねるのは、前景が最も手前にあるからです。

## 背景のぼかし：ピント内の物を貫通させない

<strong>背景をぼかすとき</strong>、ピント内の物（手前にある）の色を背景のボケに混ぜてはいけません（ピント内の物がぼけて見えてしまう）。

```hlsl
float BackgroundWeight(float sample_coc, float distance_in_pixels) {
  float reach = saturate(sample_coc - distance_in_pixels + 1.0);
  float is_far = saturate(sample_coc);
  return reach * is_far;
}
```

背景のぼかしのコードの要点です。`is_far` は、サンプルが背景（CoC > 0）なら有効で、前景やピント内なら 0 にします。`reach` は、そのサンプルのボケが自分まで届くかを表します。

## 前景のぼかし：近傍の最大 CoC

<strong>前景のボケは前景の輪郭の「外側」にまで広がります</strong>。その位置の画素自体の CoC は 0（ピント内か背景）でも近くに前景の画素があれば、その CoC の分だけボケが届くので、周りの画素の最大 CoCを使います。

<!-- fig:dof-near-field:begin -->

<svg class="fig illust motion" data-fig="dof-near-field" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dof-near-field" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">手前のぼけ: 手前の物は、ぼけが、後ろのピントの合った所へはみ出す。後ろの画素のぼけ(0)だけでは足りない</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素。中央の手前の物(幅 8、CoC 5)がピントの合った背景に重なる。ぼけの広がりを 2 つの方法で比べる</text>
<text x="60.0" y="104" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">入力</text>
<rect x="60.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="78.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="96.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="114.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="132.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="150.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="168.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="186.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="204.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="222.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="240.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="258.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="276.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="294.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="312.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="330.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="348.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="366.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="384.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="402.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="420.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="438.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="456.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="474.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="492.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="510.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="528.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="546.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e64033"/></rect>
<rect x="564.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="582.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="600.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="618.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="636.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="654.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="672.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="690.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="708.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="726.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="744.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="762.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="780.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="798.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="816.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="834.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="852.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="870.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="888.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="906.0" y="108.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="60.0" y="108" width="864.0" height="18.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="164" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">画素自身のぼけだけで集める</text>
<rect x="60.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="78.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0689" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="96.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="114.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0733" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="132.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="150.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0778" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="168.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="186.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0822" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="204.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="222.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="240.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="258.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="276.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="294.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="312.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="330.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="348.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="366.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="384.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="402.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1089" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="420.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#e08b8a"/></rect>
<rect x="438.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1133" values="#e5e7eb;#e17c79"/></rect>
<rect x="456.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1156" values="#e5e7eb;#e26d67"/></rect>
<rect x="474.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1178" values="#e5e7eb;#e26d67"/></rect>
<rect x="492.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#e26d67"/></rect>
<rect x="510.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1222" values="#e5e7eb;#e26d67"/></rect>
<rect x="528.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#e5e7eb;#e17c79"/></rect>
<rect x="546.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1267" values="#e5e7eb;#e08b8a"/></rect>
<rect x="564.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="582.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="600.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="618.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1356" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="636.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="654.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1400" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="672.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1422" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="690.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1444" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="708.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="726.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1489" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="744.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1511" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="762.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1533" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="780.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1556" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="798.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1578" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="816.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="834.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1622" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="852.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1644" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="870.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1667" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="888.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1689" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="906.0" y="168.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1711" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="60.0" y="168" width="864.0" height="18.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="224" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">手前のぼけを周りへ広げてから集める</text>
<rect x="60.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2533" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="78.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2556" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="96.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2578" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="114.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2600" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="132.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2622" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="150.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2644" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="168.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2667" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="186.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2689" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="204.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="222.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2733" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="240.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="258.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2778" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="276.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="294.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2822" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="312.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="330.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2867" values="#e5e7eb;#dad6e1"/></rect>
<rect x="348.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#dbc7cf"/></rect>
<rect x="366.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2911" values="#e5e7eb;#dcb8be"/></rect>
<rect x="384.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#dda9ad"/></rect>
<rect x="402.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2956" values="#e5e7eb;#df9a9b"/></rect>
<rect x="420.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#e08b8a"/></rect>
<rect x="438.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3000" values="#e5e7eb;#e17c79"/></rect>
<rect x="456.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#e5e7eb;#e26d67"/></rect>
<rect x="474.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3044" values="#e5e7eb;#e26d67"/></rect>
<rect x="492.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3067" values="#e5e7eb;#e26d67"/></rect>
<rect x="510.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3089" values="#e5e7eb;#e26d67"/></rect>
<rect x="528.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3111" values="#e5e7eb;#e17c79"/></rect>
<rect x="546.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3133" values="#e5e7eb;#e08b8a"/></rect>
<rect x="564.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3156" values="#e5e7eb;#df9a9b"/></rect>
<rect x="582.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3178" values="#e5e7eb;#dda9ad"/></rect>
<rect x="600.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3200" values="#e5e7eb;#dcb8be"/></rect>
<rect x="618.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3222" values="#e5e7eb;#dbc7cf"/></rect>
<rect x="636.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3244" values="#e5e7eb;#dad6e1"/></rect>
<rect x="654.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3267" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="672.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3289" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="690.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3311" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="708.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="726.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3356" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="744.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3378" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="762.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3400" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="780.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3422" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="798.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="816.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3467" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="834.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3489" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="852.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3511" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="870.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="888.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="906.0" y="228.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3578" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="60.0" y="228" width="864.0" height="18.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="284" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">正解(手前の物を円盤でぼかす)</text>
<rect x="60.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="78.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="96.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="114.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="132.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="150.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="168.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="186.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="204.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="222.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="240.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="258.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="276.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="294.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="312.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="330.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dad6e1"/></rect>
<rect x="348.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dbc7cf"/></rect>
<rect x="366.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dcb8be"/></rect>
<rect x="384.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dda9ad"/></rect>
<rect x="402.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#df9a9b"/></rect>
<rect x="420.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e08b8a"/></rect>
<rect x="438.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e17c79"/></rect>
<rect x="456.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e26d67"/></rect>
<rect x="474.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e26d67"/></rect>
<rect x="492.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e26d67"/></rect>
<rect x="510.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e26d67"/></rect>
<rect x="528.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e17c79"/></rect>
<rect x="546.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e08b8a"/></rect>
<rect x="564.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#df9a9b"/></rect>
<rect x="582.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dda9ad"/></rect>
<rect x="600.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dcb8be"/></rect>
<rect x="618.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dbc7cf"/></rect>
<rect x="636.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dad6e1"/></rect>
<rect x="654.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="672.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="690.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="708.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="726.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="744.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="762.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="780.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="798.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="816.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="834.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="852.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="870.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="888.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="906.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d9e6f2"/></rect>
<rect x="60.0" y="288" width="864.0" height="18.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="354" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">手前の物の外へぼけがはみ出した幅(画素):</text>
<text x="430" y="358" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;1.0000" values="1;1;0;0"/></text>
<text x="430" y="358" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;0.3643;0.3644;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="358" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">18<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3643;0.3644;1.0000" values="0;0;1;1"/></text>
<text x="480" y="358" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">(正解は 18)</text>
<rect x="30" y="392" width="900" height="90" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="382" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">正解とのずれ(平均)</text>
<text x="50" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">画素自身だけ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4620;0.4622;1.0000" values="0;0;1;1"/></text>
<text x="50" y="464" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">0.037<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4620;0.4622;1.0000" values="0;0;1;1"/></text>
<text x="490" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">広げてから集める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5154;0.5156;1.0000" values="0;0;1;1"/></text>
<text x="490" y="464" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043" opacity="0">0.000<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5154;0.5156;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">手前の物は、ぼけると、後ろの背景の上にはみ出して見える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">背景の画素は、自分のぼけが 0 なので、はみ出しが再現できない(輪郭がくっきり残る)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2532;0.2533;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">手前の CoC を周りへ広げると、はみ出しが再現できる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2532;0.2533;0.4620;0.4622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">はみ出しの幅が正解に近づく<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4620;0.4622;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:dof-near-field:end -->

### 近傍の最大 CoC（タイル）

画面をたとえば 16×16 のタイルに分け、各タイルの前景の最大 CoC（最も負に大きい値）を求め、それを周りのタイルへ広げます（ダイレーション）。

```hlsl
[numthreads(16, 16, 1)]
void TileMaxCoc(uint3 id : SV_DispatchThreadID, uint3 group_id : SV_GroupID, uint group_index : SV_GroupIndex) {
  float coc = color_coc.Load(int3(id.xy, 0)).a;
  s_min_coc[group_index] = coc;
  GroupMemoryBarrierWithGroupSync();
  for (uint stride = 128; stride > 0; stride >>= 1) {
    if (group_index < stride) s_min_coc[group_index] = min(s_min_coc[group_index], s_min_coc[group_index + stride]);
    GroupMemoryBarrierWithGroupSync();
  }
  if (group_index == 0) tile_max_near[group_id.xy] = s_min_coc[0];
}
```

近傍最大 CoC のコードの要点です。前景は負の値なので、最小値が最も大きな前景の CoC になります。グループ内の最小値を共有メモリで縮約して求め、さらに、隣接 3×3 のタイルの最小値をそのタイルの「近傍の最大 CoC」にします。

タイルの最大 CoC が 0 のタイル（前景がまったくない）は、前景のぼかしを丸ごとスキップでき、高速化になります。

## 合成の順序

合成の順序は、背景のぼけをピント内の画像に混ぜ、ピント内はそのままにして、ぼけた前景をアルファで上に重ねる、という順です。

<strong>半解像度</strong>で前景・背景を処理する場合、前景と背景を別の画像として保存し、最後にフル解像度の画像へ合成します。

## よくある破綻と対処

| 破綻 | 原因 | 対処 |
| --- | --- | --- |
| ピント内の物の縁に背景のボケがにじむ | 背景のぼかしで前景・ピント内を混ぜた | サンプルの CoC 符号で除外 |
| ぼけた前景の輪郭がきつい | 前景を自分の CoC だけで処理 | 近傍の最大 CoC・アルファ合成 |
| <strong>前景と背景の境にハロ（白い縁）</strong> | 混ざり方の誤り | 符号付きの重み・別画像で合成 |
| ピント内の物の背後にぼけた物が突き抜けて見える | 深度の考慮漏れ | 背景の重みに深度の順序を反映 |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 前景・背景を別バッファに | 混ざりを防ぐ |
| タイルの最大 CoC | 前景のぼかしを必要な所だけ |
| 前景はアルファ付きで合成 | 透けるボケ |
| ピント内はできるだけ元の絵のまま | くっきりを保つ |
| 背景の「裏側」の補完 | 前景の下に隠れた背景が見えるよう、周囲の色で補う（高度） |

## よくあるミス

??? failure "前景のボケが奥にしかかからず、手前の物の輪郭が切れている"
    <strong>近傍の最大 CoC</strong>で前景の外へも広げる。

??? failure "ピント内の物の周りに、背景のボケが白く縁取る"
    背景のぼかしで前景・ピント内のサンプルを除外。

??? failure "前景も背景も、1 枚でぼかして、境が破綻する"
    符号で分け、別々にぼかして、合成する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>背景のボケは、ピント内の物を隠さない</strong>。前景のボケは奥にかぶさる
    - [x] CoC を符号付きで持ち、前景・背景を別々に処理
    - [x] 前景は、近傍の最大 CoC（タイル）で外側へ広げる
    - [x] 背景のぼかしで、ピント内・前景のサンプルを除外
    - [x] 合成は、背景 → ピント内 → 前景（アルファ）

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）

## 関連ページ

- [Depth of Field (DOF)](index.md)
- [Circle of Confusion (CoC)](coc.md)
- [Gather Method](gather.md)
- [Scatter Method](scatter.md)
