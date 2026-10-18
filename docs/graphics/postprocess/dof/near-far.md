---
title: Foreground and Background
tags:
  - 描画
---

# Foreground and Background

**DOF の難しさは、「ピントの手前（前景）」と「奥（背景）」で、ぼけ方の理屈が違う**ことです。**背景のボケはピントが合った物の「後ろ」にあるので手前の物を隠さない**ですが、**前景のボケはピントが合った物の「手前」にあるのでその物の上に広がってかぶさります**。**これを分けて処理しないと、ボケた前景の輪郭がきつくなったり、ピント内の物に背景がにじんだり**します。このページでは、**前景と背景の違い・別々に処理する方法・近傍の最大 CoC（タイル）・合成・よくある破綻**を説明します。

!!! tip "ポイント"
    - <strong>背景のボケ</strong>は<strong>ピント内の物にかぶらない</strong>。<strong>前景のボケは奥の物の上に広がる</strong>。
    - <strong>CoC を符号付き</strong>で持ち（<strong>前景は負</strong>）、<strong>前景・背景を別々に処理</strong>する。
    - <strong>前景は「周りの最大 CoC」</strong>を使う（<strong>前景の輪郭の外側にまでボケが広がる</strong>ため）。<strong>タイルで高速化</strong>。
    - <strong>前景のボケは、アルファ（透け具合）つきで最後に合成</strong>する。
    - <strong>背景はピント内の物を貫通しない</strong>ように、<strong>重みを制御</strong>。
    - <strong>半解像度</strong>でも<strong>前景と背景は分けて保存</strong>する。

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
| **ボケの広がる向き** | **奥の物の周り** | **手前の物の輪郭の外へ奥にかぶさる** |
| **ピント内の物との関係** | **ピント内の物は、手前にあるので隠れない** | **ピント内の物の上に広がる** |
| **ボケた縁** | **ピント内の物の縁できっぱり切れる** | **縁がやわらかく、透ける** |

## 別々に処理する

**CoC の符号**で**前景と背景に分け**、**別々にぼかし、最後に合成**します。

| 手順 | 内容 |
| --- | --- |
| **① 前景と背景に分ける** | **CoC < 0 を前景、CoC > 0 を背景**（**ピント内（|CoC| が小さい）は、そのまま**） |
| **② 背景をぼかす** | **ピント内の物の色が混ざらないよう、重みを制御** |
| **③ 前景をぼかす** | **近傍の最大 CoC を使い、前景の外にも広げる。アルファ付き** |
| **④ 合成** | **背景 → ピント内 → 前景（アルファで上に）の順** |

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

**背景をぼかすとき**、**ピント内の物（手前にある）の色を背景のボケに混ぜてはいけません**（**ピント内の物がぼけて見えてしまう**）。

```hlsl
float BackgroundWeight(float sample_coc, float distance_in_pixels) {
  float reach = saturate(sample_coc - distance_in_pixels + 1.0);
  float is_far = saturate(sample_coc);
  return reach * is_far;
}
```

背景のぼかしのコードの要点です。`is_far` は、サンプルが背景（CoC > 0）なら有効で、前景やピント内なら 0 にします。`reach` は、そのサンプルのボケが自分まで届くかを表します。

## 前景のぼかし：近傍の最大 CoC

**前景のボケは前景の輪郭の「外側」にまで広がります**。**その位置の画素自体の CoC は 0（ピント内か背景）でも近くに前景の画素があれば、その CoC の分だけボケが届く**ので、**周りの画素の最大 CoC**を**使います**。

<!-- fig:dof-near-field:begin -->

<svg class="fig illust motion" data-fig="dof-near-field" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dof-near-field" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<filter id="nf-b0" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5.0"/>
</filter>
<filter id="nf-b1" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="10.0"/>
</filter>
<filter id="nf-b2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="16.0"/>
</filter>
<clipPath id="nf-clip-40-0"><circle cx="205" cy="200" r="52"/>
</clipPath>
<clipPath id="nf-clip-40-1"><circle cx="205" cy="200" r="52"/>
</clipPath>
<clipPath id="nf-clip-40-2"><circle cx="205" cy="200" r="52"/>
</clipPath>
<clipPath id="nf-clip-40-3"><circle cx="205" cy="200" r="52"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">前景のボケは、輪郭の外へ広がる</text>
<text x="40" y="70" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">自分の CoC だけ使う（輪郭が硬い）</text>
<rect x="40" y="90" width="330" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="50" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="80" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="110" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="140" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="170" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="200" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="230" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="260" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="290" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="320" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="350" y="90" width="14" height="220" fill="#cbd5e1"/>
<circle cx="205" cy="200" r="52" fill="#e5484d" opacity="0" clip-path="url(#nf-clip-40-0)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;1;0.27;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0.27;1;1"/></circle>
<circle cx="205" cy="200" r="52" fill="#e5484d" opacity="0" filter="url(#nf-b0)" clip-path="url(#nf-clip-40-1)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;0.73;0.75;0.3;0;0;0;0;0;0;0;0;0;0;0;0;0;0.3;0.75;0.73;0;0"/></circle>
<circle cx="205" cy="200" r="52" fill="#e5484d" opacity="0" filter="url(#nf-b1)" clip-path="url(#nf-clip-40-2)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;0;0.25;0.7;0.92;0.65;0.42;0.24;0.1;0.03;0;0.03;0.1;0.24;0.42;0.65;0.92;0.7;0.25;0;0;0"/></circle>
<circle cx="205" cy="200" r="52" fill="#e5484d" opacity="0" filter="url(#nf-b2)" clip-path="url(#nf-clip-40-3)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;0;0;0;0.08;0.35;0.58;0.76;0.9;0.97;1;0.97;0.9;0.76;0.58;0.35;0.08;0;0;0;0;0"/></circle>
<text x="410" y="70" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">周りの最大 CoC を使う（輪郭の外へ広がる）</text>
<rect x="410" y="90" width="330" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="420" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="450" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="480" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="510" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="540" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="570" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="600" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="630" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="660" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="690" y="90" width="14" height="220" fill="#cbd5e1"/>
<rect x="720" y="90" width="14" height="220" fill="#cbd5e1"/>
<circle cx="575" cy="200" r="52" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;1;0.27;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0.27;1;1"/></circle>
<circle cx="575" cy="200" r="52" fill="#e5484d" opacity="0" filter="url(#nf-b0)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;0.73;0.75;0.3;0;0;0;0;0;0;0;0;0;0;0;0;0;0.3;0.75;0.73;0;0"/></circle>
<circle cx="575" cy="200" r="52" fill="#e5484d" opacity="0" filter="url(#nf-b1)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;0;0.25;0.7;0.92;0.65;0.42;0.24;0.1;0.03;0;0.03;0.1;0.24;0.42;0.65;0.92;0.7;0.25;0;0;0"/></circle>
<circle cx="575" cy="200" r="52" fill="#e5484d" opacity="0" filter="url(#nf-b2)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1100;0.1400;0.1700;0.2000;0.2300;0.2600;0.2900;0.3200;0.3500;0.3800;0.4100;0.4400;0.4700;0.5000;0.5300;0.5600;0.5900;0.6200;0.6500;0.6800;1.0000" values="0;0;0;0;0;0.08;0.35;0.58;0.76;0.9;0.97;1;0.97;0.9;0.76;0.58;0.35;0.08;0;0;0;0;0"/></circle>
<text x="40" y="346" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ピントを背景に合わせると、手前の赤い物がボケる。左は輪郭が硬いまま。右は外にも広がる（本物のボケ）。<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:dof-near-field:end -->

### 近傍の最大 CoC（タイル）

**画面をたとえば 16×16 のタイルに分け**、**各タイルの前景の最大 CoC（最も負に大きい値）を求め**、**それを周りのタイルへ広げます**（**ダイレーション**）。

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

近傍最大 CoC のコードの要点です。前景は負の値なので、最小値が最も大きな前景の CoC になります。グループ内の最小値を共有メモリで縮約して求め、さらに、隣接 3×3 のタイルの最小値を、そのタイルの「近傍の最大 CoC」にします。

**タイルの最大 CoC が 0 のタイル**（**前景がまったくない**）は、**前景のぼかしを丸ごとスキップ**でき、**高速化**になります。

## 合成の順序

合成の順序は、背景のぼけをピント内の画像に混ぜ、ピント内はそのままにして、ぼけた前景をアルファで上に重ねる、という順です。

**半解像度**で**前景・背景を処理**する場合、**前景と背景を別の画像として保存**し、**最後にフル解像度の画像へ合成**します。

## よくある破綻と対処

| 破綻 | 原因 | 対処 |
| --- | --- | --- |
| **ピント内の物の縁に背景のボケがにじむ** | **背景のぼかしで前景・ピント内を混ぜた** | **サンプルの CoC 符号で除外** |
| **ぼけた前景の輪郭がきつい** | **前景を自分の CoC だけで処理** | **近傍の最大 CoC・アルファ合成** |
| <strong>前景と背景の境にハロ（白い縁）</strong> | **混ざり方の誤り** | **符号付きの重み・別画像で合成** |
| **ピント内の物の背後にぼけた物が突き抜けて見える** | **深度の考慮漏れ** | **背景の重みに深度の順序を反映** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **前景・背景を別バッファに** | **混ざりを防ぐ** |
| **タイルの最大 CoC** | **前景のぼかしを必要な所だけ** |
| **前景はアルファ付きで合成** | **透けるボケ** |
| **ピント内はできるだけ元の絵のまま** | **くっきりを保つ** |
| **背景の「裏側」の補完** | **前景の下に隠れた背景が見えるよう、周囲の色で補う**（高度） |

## よくあるミス

??? failure "前景のボケが、奥にしかかからず、手前の物の輪郭が切れている"
    **近傍の最大 CoC**で**前景の外へも広げる**。

??? failure "ピント内の物の周りに、背景のボケが白く縁取る"
    **背景のぼかしで前景・ピント内のサンプルを除外**。

??? failure "前景も背景も、1 枚でぼかして、境が破綻する"
    **符号で分け、別々にぼかして、合成**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>背景のボケは、ピント内の物を隠さない</strong>。<strong>前景のボケは奥にかぶさる</strong>
    - [x] <strong>CoC を符号付きで持ち、前景・背景を別々に処理</strong>
    - [x] <strong>前景は、近傍の最大 CoC（タイル）</strong>で<strong>外側へ広げる</strong>
    - [x] <strong>背景のぼかしで、ピント内・前景のサンプルを除外</strong>
    - [x] <strong>合成は、背景 → ピント内 → 前景（アルファ）</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）

## 関連ページ

- [Depth of Field (DOF)](index.md)
- [Circle of Confusion (CoC)](coc.md)
- [Gather Method](gather.md)
- [Scatter Method](scatter.md)
