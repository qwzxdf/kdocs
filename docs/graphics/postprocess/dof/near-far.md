---
title: Foreground and Background
tags:
  - 描画
---

# Foreground and Background

被写界深度（DOF）を後処理で作るとき最初に思いつくのは、CoC（錯乱円。ボケの大きさ）に応じて画面全体を 1 枚でぼかすことです。ところが、これをやるとピントの合った人物の輪郭に背景のボケがにじんだり手前の物のボケた輪郭が妙にくっきりしたりします。

<strong>DOF の難しさはピントの手前（前景）と奥（背景）で、ボケ方の理屈が違うことです</strong>。背景のボケはピントが合った物の後ろにあるので、手前の物を隠しません。前景のボケはピントが合った物の手前にあるので、その物の上に広がってかぶさります。このページでは前景と背景の違い CoC の符号と数字、別々に処理する方法、近傍の最大 CoC（タイル）、合成、よくある破綻を説明します。

!!! tip "ポイント"
    - 背景のボケはピント内の物にかぶりません。前景のボケは奥の物の上に広がります。
    - CoC を符号付きで持ち（前景は負）、前景と背景を別々に処理します。
    - 前景は周りの最大 CoC を使います。前景の輪郭の外側にまでボケが広がるからです。タイルで高速化します。
    - 前景のボケはアルファ（透け具合）つきで最後に合成します。
    - 背景はピント内の物の色を混ぜないようにサンプルの重みを制御します。
    - 半解像度でも前景と背景は分けて保存します。

!!! info "このページを読む前に"
    - [Depth of Field (DOF)](index.md)（このセクション全体の地図と、読む順番）
    - [Circle of Confusion (CoC)](coc.md)（ボケの大きさを求める式）

## 前景と背景の違い {#difference}

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

前景と背景では次の 3 点が違います。

- ボケの広がる向きが違います。背景のボケは奥の物の周りに広がります。前景のボケは手前の物の輪郭の外へ奥にかぶさるように広がります。
- ピント内の物との関係が違います。背景のボケはピント内の物が手前にあるので、隠れません。前景のボケはピント内の物の上に広がります。
- ボケた縁が違います。背景はピント内の物の縁できっぱり切れます。前景は縁がやわらかく透けます。

## CoC の符号と数字 {#coc}

前景と背景を分ける基準は符号つきの CoC です。薄いレンズの式からボケの直径を求めて、手前（ピントより近い）を負、奥を正にします。

```hlsl
Texture2D<float> g_depth : register(t0);            // 視点深度（メートル）。リニアに直したもの
Texture2D<float4> g_color : register(t1);
RWTexture2D<float4> g_color_coc : register(u0);     // RGB = 色、A = 符号つき CoC（ピクセル）

cbuffer DofConstants : register(b0) {
  float g_focus_distance;    // ピントが合う距離（メートル）。例: 2
  float g_focal_length;      // 焦点距離（メートル）。例: 0.05
  float g_aperture;          // 絞りの直径（メートル）。焦点距離 ÷ F 値。例: 0.0278（50 mm、F1.8）
  float g_pixels_per_meter_on_sensor;   // センサー上の 1 m が何ピクセルか。例: 1920 / 0.036
  float g_max_coc;           // CoC の上限（ピクセル）。例: 64
  uint2 g_size;
  float _pad;
};

// 符号つきの CoC（ピクセル）。手前は負、奥は正
float SignedCoc(float d) {
  float s = g_focus_distance;
  float coc_meters = g_aperture * g_focal_length / (s - g_focal_length) * abs(d - s) / d;
  float coc_px = coc_meters * g_pixels_per_meter_on_sensor;
  coc_px = min(coc_px, g_max_coc);                  // 上限（暴走する近距離の防止。足した処理）
  return (d < s) ? -coc_px : coc_px;
}

[numthreads(8, 8, 1)]
void CocCS(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= g_size)) return;
  float d = g_depth.Load(int3(id.xy, 0));
  g_color_coc[id.xy] = float4(g_color.Load(int3(id.xy, 0)).rgb, SignedCoc(d));
}
```

数字で確かめます。50 mm、F 1.8（絞りの直径 27.8 mm）で、距離 2 m にピントを合わせセンサー幅 36 mm を 1920 ピクセルで受けるとします。CoC（ピクセル）は 1 m の物で約 38、1.5 m で約 13、3 m で約 13、5 m で約 23、10 m で約 30 です。無限遠でも約 38 で頭打ちになります。一方、手前の 0.5 m では約 114 になります。

背景のボケは無限遠でも上限が決まっていますが、前景のボケは近づくほど際限なく大きくなります。前景が背景より大きなボケを作りやすくしかもピント内の物の上に広がるので、処理の工夫が前景で特に必要になります。

## 別々に処理する {#separate}

CoC の符号で前景と背景に分けて、別々にぼかして最後に合成します。

1. 前景と背景に分けます。CoC が負なら前景、正なら背景です。ピント内（絶対値が小さい）はそのままです。
2. 背景をぼかします。ピント内の物の色が混ざらないように重みを制御します。
3. 前景をぼかします。近傍の最大 CoC を使って、前景の外にも広げます。アルファつきです。
4. 合成します。背景、ピント内、前景（アルファで上に）の順です。

## 背景のぼかし: ピント内の物を混ぜない {#background}

背景をぼかすときピント内の物（手前にある）の色を背景のボケに混ぜてはいけません。ピント内の物がぼけて見えてしまうからです。サンプルの CoC が自分の画素まで届くかで、重みを決めます。

```hlsl
Texture2D<float4> g_color_coc_srv : register(t2);   // RGB = 色、A = 符号つき CoC
SamplerState g_point_clamp : register(s0);

static const int kRings = 3;                         // 同心円の数
static const int kSamplesPerRing = 8;

float BackgroundWeight(float sample_coc, float distance_in_pixels) {
  // そのサンプルが背景（coc > 0）で、ボケが自分まで届くとき、重みが 1
  float reach = saturate(sample_coc - distance_in_pixels + 1.0);
  float is_far = saturate(sample_coc);               // 前景やピント内は 0
  return reach * is_far;
}

float4 BackgroundBlurPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float4 center = g_color_coc_srv.SampleLevel(g_point_clamp, uv, 0);
  float radius = max(center.a, 0.0);                 // 自分の CoC（背景のみ）
  float3 sum = center.rgb;
  float weight = 1.0;
  float2 texel = 1.0 / float2(1920.0, 1080.0);       // 例: 画面のサイズ（実際は定数で渡す）

  [unroll] for (int ring = 1; ring <= kRings; ++ring) {
    float r = radius * ring / kRings;
    [unroll] for (int k = 0; k < kSamplesPerRing; ++k) {
      float angle = 6.2831853 * (k + 0.5 * ring) / kSamplesPerRing;
      float2 offset = float2(cos(angle), sin(angle)) * r;
      float4 s = g_color_coc_srv.SampleLevel(g_point_clamp, uv + offset * texel, 0);
      float w = BackgroundWeight(s.a, r);
      sum += s.rgb * w;
      weight += w;
    }
  }
  return float4(sum / weight, 1.0);
}
```

`is_far` が前景やピント内のサンプルを除外します。これでピント内の物の色が背景のボケに混ざりません。`reach` はそのサンプルのボケが自分まで届くかの目安です。

## 前景のぼかし: 近傍の最大 CoC {#foreground}

前景のボケは前景の輪郭の外側にまで広がります。その位置の画素自体の CoC が 0（ピント内か背景）でも近くに前景の画素があれば、その CoC のぶんだけボケが届きます。そこで、周りの画素の最大 CoC を使います。

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

画面をたとえば 16 × 16 のタイルに分けて、各タイルの前景の最大 CoC（最も負に大きい値）を求めて、それを周りのタイルへ広げます（ダイレーション）。1920 × 1080 なら `120 × 68` のタイルです。上の数字で前景の CoC が最大 114 ピクセルなら広げる範囲は `114 / 16 ≒ 7.1` で、7 タイル先までです。

```hlsl
Texture2D<float4> g_coc_in : register(t3);
RWTexture2D<float> g_tile_min_coc : register(u1);          // 1 タイルに 1 値（最小 = 最も大きな前景）
groupshared float s_min_coc[256];

[numthreads(16, 16, 1)]
void TileMaxCocCS(uint3 id : SV_DispatchThreadID, uint3 group_id : SV_GroupID, uint group_index : SV_GroupIndex) {
  float coc = g_coc_in.Load(int3(id.xy, 0)).a;
  s_min_coc[group_index] = coc;
  GroupMemoryBarrierWithGroupSync();
  // 共有メモリで、最小値を縮約する。前景は負なので、最小値が最も大きな前景の CoC
  for (uint stride = 128; stride > 0; stride >>= 1) {
    if (group_index < stride) s_min_coc[group_index] = min(s_min_coc[group_index], s_min_coc[group_index + stride]);
    GroupMemoryBarrierWithGroupSync();
  }
  if (group_index == 0) g_tile_min_coc[group_id.xy] = s_min_coc[0];
}

Texture2D<float> g_tile_in : register(t4);
RWTexture2D<float> g_tile_dilated : register(u2);

// 隣接 3×3 のタイルの最小値を、そのタイルの「近傍の最大 CoC」にする（ダイレーション）
[numthreads(8, 8, 1)]
void TileDilateCS(uint3 id : SV_DispatchThreadID) {
  float m = 0.0;
  [unroll] for (int y = -1; y <= 1; ++y)
    [unroll] for (int x = -1; x <= 1; ++x)
      m = min(m, g_tile_in.Load(int3(int2(id.xy) + int2(x, y), 0)));
  g_tile_dilated[id.xy] = m;
}
```

タイルの最大 CoC が 0 のタイル（前景がまったくない）は、前景のぼかしを丸ごとスキップできて、高速化になります。広げる範囲が 7 タイルなら 3×3 を何回か繰り返すか最初から広い範囲で最小値を取ります。

前景のぼかしでは近傍の最大 CoC を半径にして、周りを読み前景のサンプルの寄与から、アルファを作ります。

```hlsl
Texture2D<float> g_tile_near : register(t5);

float4 ForegroundBlurPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  uint2 tile = uint2(pos.xy) / 16;
  float near_radius = -g_tile_near.Load(int3(tile, 0));      // 近傍の最大 CoC（正の値にする）
  if (near_radius < 0.5) return float4(0, 0, 0, 0);          // 前景が近くにない → 何もしない

  float3 sum = 0.0;
  float alpha_sum = 0.0;
  float count = 0.0;
  float2 texel = 1.0 / float2(1920.0, 1080.0);
  [unroll] for (int ring = 0; ring <= kRings; ++ring) {
    float r = near_radius * ring / kRings;
    int n = (ring == 0) ? 1 : kSamplesPerRing;
    for (int k = 0; k < n; ++k) {
      float angle = 6.2831853 * (k + 0.5 * ring) / kSamplesPerRing;
      float2 offset = float2(cos(angle), sin(angle)) * r;
      float4 s = g_color_coc_srv.SampleLevel(g_point_clamp, uv + offset * texel, 0);
      // サンプルが前景（coc < 0）で、その CoC が、このサンプルの距離 r まで届くなら、寄与する
      float w = (s.a < 0.0 && (-s.a) >= r - 1.0) ? 1.0 : 0.0;
      sum += s.rgb * w;
      alpha_sum += w;
      count += 1.0;
    }
  }
  float alpha = saturate(alpha_sum / count * 2.0);           // 前景が占める割合から、透け具合を作る。2 倍は調整値
  return float4(sum / max(alpha_sum, 1.0), alpha);
}
```

前景のサンプルが多いほどアルファが 1 に近づきます。輪郭の外側では前景のサンプルが少ないので、アルファが小さくなってやわらかく透けます。

## 合成 {#composite}

合成の順序は背景のボケをピント内の画像に混ぜて、ピント内はそのままにしてぼけた前景をアルファで上に重ねるという順です。

```hlsl
float3 CompositeDof(float3 sharp, float coc, float4 far_blur, float4 near_blur) {
  float far_alpha = saturate(coc);                           // 背景のボケは、CoC が大きいほど強く混ぜる
  float3 color = lerp(sharp, far_blur.rgb, far_alpha);
  color = lerp(color, near_blur.rgb, near_blur.a);           // 前景は最後に上へ。a が透け具合
  return color;
}
```

`far_alpha = saturate(coc)` で CoC が 1 ピクセル以上なら完全に背景のボケにします。`near_blur.a` は前景のぼけた濃さで輪郭の外側は薄く透けます。最後に前景を重ねるのは前景が最も手前にあるからです。半解像度で前景と背景を処理する場合は、前景と背景を別の画像として保存して、最後にフル解像度の画像へ合成します。

!!! note "確かめた範囲"
    HLSL は `fxc` で `CocCS`、`TileMaxCocCS`、`TileDilateCS`（`cs_5_0`）と `BackgroundBlurPS`、`ForegroundBlurPS`（`ps_5_0`）をコンパイルしてエラーが出ないことを確かめました。CoC の数字は式からの手計算です。GPU での描画は確認していません。

## よくある破綻と対処 {#failures}

??? failure "ピント内の物の縁に背景のボケがにじむ"
    原因は背景のぼかしで、前景やピント内のサンプルを混ぜていることです。サンプルの CoC の符号で除外します（`BackgroundWeight` の `is_far`）。

??? failure "ぼけた前景の輪郭がきつい"
    原因は前景を自分の CoC だけで処理して、外側へ広げていないことです。近傍の最大 CoC で広げて、アルファで合成します。

??? failure "前景と背景の境に白いハロが出る"
    原因は混ざり方の誤りです。前景と背景を同じ画像でぼかして、符号を考えずに混ぜています。符号つきの重みで別の画像として合成します。

??? failure "ピント内の物の背後にぼけた物が突き抜けて見える"
    原因は深度の順序を考慮していないことです。背景のぼかしで深度の順序を重みに入れます。

??? failure "前景も背景も 1 枚でぼかして、境が破綻する"
    原因は符号で分けていないことです。符号で分けて別々にぼかして合成します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 背景のボケはピント内の物を隠しません。前景のボケは奥にかぶさります。
    - [x] CoC を符号付きで持ち前景と背景を別々に処理します。
    - [x] 前景は近傍の最大 CoC（タイル）で外側へ広げます。1920×1080 を 16×16 で区切ると 120×68 タイルです。
    - [x] 背景のぼかしで、ピント内と前景のサンプルを除外します。
    - [x] 合成は背景、ピント内、前景（アルファ）の順です。

## 参考 {#references}

このページは次の資料を読まずに書きました。CoC の式は薄いレンズの一般的な式で、数字は手計算です。ぼかしのシェーダーは仕組みを説明するために自分で書いたもので、発表の実装とは異なります。

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014
- Abadie, "A Life of a Bokeh", SIGGRAPH 2018
- Sousa, "Graphics Gems from CryENGINE 3", SIGGRAPH 2013

## 関連ページ

- [Depth of Field (DOF)](index.md)
- [Circle of Confusion (CoC)](coc.md)
- [Gather Method](gather.md)
- [Scatter Method](scatter.md)
