---
title: 錯乱円（CoC）
tags:
  - 描画
---

# 錯乱円（CoC）

<strong>錯乱円（Circle of Confusion、CoC）</strong>は、<strong>ピントが合っていない点が、センサー上に作る「円」</strong>です。**この円の大きさがそのままボケの大きさ**になります。**DOF の最初の仕事は、画面の各画素について、この CoC を求めること**です。このページでは、**光学的な仕組み・薄いレンズの式・CoC のグラフ・ピクセルへの換算・符号の意味・物理ベースとアーティスト向けの簡易式**を説明します。

!!! tip "ポイント"
    - ピントが合った点は<strong>センサー上で 1 点</strong>、<strong>ずれた点は円（CoC）</strong>になる。
    - <strong>CoC の大きさ</strong>は<strong>絞り（F 値）・焦点距離・ピント距離・被写体の距離</strong>で決まる。
    - <strong>絞りを開く・望遠にする・被写体に近づく</strong>と<strong>ボケが大きくなる</strong>。
    - <strong>背景は無限遠で CoC が飽和</strong>する。<strong>前景は近づくほど急に大きくなる</strong>。
    - <strong>符号付きで持つ</strong>：<strong>前景（ピントより手前）は負、背景は正</strong>。
    - <strong>画素数に換算し、最大値でクランプ</strong>する（<strong>コストの上限</strong>）。
    - <strong>線形な深度</strong>（ビュー空間の z）を使う。

## 光学の仕組み

**レンズはある距離の点をセンサー上の 1 点に集めます**（**ピントが合う距離**）。**それより近い点・遠い点はセンサーの前や後ろで像を結び、センサー上では広がった円**になります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="錯乱円の仕組み">
<text x="20" y="26" class="fig-title">ピント面にない点は、センサー上で円になる</text>
<line x1="60" y1="130" x2="730" y2="130" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/>
<line x1="330" y1="60" x2="330" y2="200" stroke="currentColor" stroke-width="4"/><text x="300" y="52" style="font-size:12px">レンズ</text>
<circle cx="80" cy="130" r="6" fill="#e5aa28" stroke="currentColor" stroke-width="2"/><text x="40" y="156" style="font-size:12px">被写体（ピント外）</text>
<line x1="80" y1="130" x2="330" y2="82" stroke="currentColor"/><line x1="80" y1="130" x2="330" y2="178" stroke="currentColor"/>
<line x1="330" y1="82" x2="560" y2="130" stroke="currentColor"/><line x1="330" y1="178" x2="560" y2="130" stroke="currentColor"/>
<circle cx="560" cy="130" r="4" fill="currentColor"/><text x="520" y="150" style="font-size:12px">像を結ぶ点</text>
<line x1="650" y1="70" x2="650" y2="190" stroke="currentColor" stroke-width="3"/><text x="620" y="62" style="font-size:12px">センサー</text>
<line x1="330" y1="82" x2="650" y2="104" stroke="currentColor" stroke-dasharray="2 3" opacity="0.6"/><line x1="330" y1="178" x2="650" y2="156" stroke="currentColor" stroke-dasharray="2 3" opacity="0.6"/>
<line x1="662" y1="104" x2="662" y2="156" stroke="#e5484d" stroke-width="3"/><text x="672" y="134" style="font-size:12px;fill:#e5484d;font-weight:700">CoC</text>
<text x="300" y="232" style="font-size:12px">像を結ぶ点がセンサーの手前 → センサー上では光が広がる</text>
</svg>

## 薄いレンズの式から

**薄いレンズの式**から、**CoC の直径**（**センサー上の長さ**）が**導けます**。

<div class="formula">CoC = A · |S₂ − S₁| / S₂ · f / (S₁ − f)　（A = f / N）</div>

| 記号 | 意味 | 例 |
| --- | --- | --- |
| **f** | **焦点距離** | **50 mm** |
| **N** | **F 値**（小さいほど開放） | **1.8** |
| **A = f / N** | **絞りの口径** | **約 27.8 mm** |
| **S₁** | **ピントを合わせた距離** | **3 m** |
| **S₂** | **被写体の距離** | **ピント面からの距離次第** |

| 要因 | ボケの大きさ |
| --- | --- |
| <strong>絞りを開く（N を小さく）</strong> | **大きくなる** |
| <strong>焦点距離を長く（望遠）</strong> | **大きくなる** |
| **被写体を近づける** | **大きくなる** |
| **ピント面から離れる** | **大きくなる**（**背景は無限遠で頭打ち**） |

<!-- fig:coc-graph:begin -->
<!-- fig:coc-graph:end -->

## CoC のグラフの形

**被写体の距離 S₂ を横軸**にすると、**CoC は次の形**になります。

- **S₂ = S₁（ピント面）で 0**。
- **手前（S₂ < S₁）に行くと急に大きくなる**（**前景のボケは近いほど極端**）。
- **奥（S₂ > S₁）に行くと緩やかに大きくなり、無限遠で一定の値に近づく**。

**したがって、前景は大きくぼけ、背景はある大きさで頭打ち**になります。

## HLSL

```hlsl
cbuffer DofConstants : register(b0) {
  float focal_length;
  float f_number;
  float focus_distance;
  float sensor_height;
  float image_height_in_pixels;
  float max_coc_in_pixels;
  float2 padding;
};

float CircleOfConfusion(float linear_depth) {
  float aperture = focal_length / f_number;
  float coc = aperture * abs(linear_depth - focus_distance) / linear_depth
            * focal_length / (focus_distance - focal_length);
  return coc;
}

float SignedCocPixels(float linear_depth) {
  float coc = CircleOfConfusion(linear_depth);
  float pixels = coc / sensor_height * image_height_in_pixels;
  float sign_value = linear_depth < focus_distance ? -1.0 : 1.0;
  return sign_value * min(pixels, max_coc_in_pixels);
}
```

| 点 | 説明 |
| --- | --- |
| **`linear_depth`** | **カメラからの線形な距離**（ビュー空間の z）。**深度バッファの非線形な値は使えない** |
| **符号** | **前景は負、背景は正**。**前景と背景を別々に扱うため** |
| **センサー高さで割って画素数へ** | **ミリメートルの CoC を、画像の画素数に換算** |
| **`max_coc_in_pixels`** | <strong>ボケの最大半径（画素）</strong>。**コストの上限**（20〜50 画素） |

**単位をそろえる**ことが**大切**です（**焦点距離・距離・センサー高さをすべてミリメートルかメートル**に）。

## アーティスト向けの簡易式

**物理式はパラメータの意味が直感的でない**ことがあります。<strong>「ピント距離・ピントが合う幅・ぼかしの強さ」</strong>だけで**決める簡易式**も**よく使われます**。

```hlsl
float SimpleCoc(float linear_depth, float focus, float range, float scale) {
  float d = linear_depth - focus;
  float t = saturate(abs(d) / range);
  return sign(d) * t * scale;
}
```

| パラメータ | 内容 |
| --- | --- |
| **`focus`** | **ピント距離** |
| **`range`** | **ピントが「十分に合って見える」幅**（**この幅で最大のボケに達する**） |
| **`scale`** | <strong>ぼかしの最大強さ（画素）</strong> |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **物理式を使い、カメラのパラメータをそのまま出す** | **シネマ カメラのように、F 値・焦点距離で直感的に** |
| **ピント距離を注視点から自動で決める** | **画面中心の深度を読んで、ピント距離を追従**（**オートフォーカス**） |
| **ピントの移動をなめらかに** | **ピント距離を指数的に追従させる**（[自動露出](../tonemapping/auto-exposure.md)と同じ考え方） |
| **CoC を専用のバッファに保存** | <strong>カラーのアルファに入れる（FP16）</strong>と、**読み込みが 1 回で済む** |
| **最大 CoC でクランプ** | **コストの上限を保証** |
| **半解像度で処理** | **CoC も半解像度で扱い、コストを 1/4** |

## よくあるミス

??? failure "非線形の深度バッファの値を、そのまま CoC の計算に使う"
    **ビュー空間の線形な z に直してから**使う。

??? failure "単位がバラバラで、ボケの大きさが極端になる"
    **焦点距離・距離・センサー高さの単位をそろえる**。

??? failure "前景と背景の符号を持たず、前景のボケが背景扱いになる"
    **符号付きで持ち、前景・背景を別に処理**する（[前景と背景](near-far.md)）。

??? failure "ピント距離が、画面中心の深度に追従せず、ガクガク動く"
    **ピント距離を時間で滑らかに追従**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CoC ＝ <strong>ピント外の点が、センサー上に作る円</strong>。<strong>大きさ ＝ ボケの大きさ</strong>
    - [x] <strong>`CoC = A·|S₂−S₁|/S₂·f/(S₁−f)`</strong>。<strong>絞りを開く・望遠・近づくと大きい</strong>
    - [x] <strong>前景は急に、背景は頭打ち</strong>。<strong>符号付きで持つ</strong>
    - [x] <strong>画素数に換算し、最大値でクランプ</strong>
    - [x] <strong>線形な深度</strong>を使う。<strong>単位をそろえる</strong>

## 参考

- Potmesil & Chakravarty, "A Lens and Aperture Camera Model for Synthetic Image Generation"（SIGGRAPH 1981）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Wikipedia, "Circle of confusion"

## 関連ページ

- [被写界深度（DOF）](index.md)
- [ギャザー方式](gather.md)
- [前景と背景](near-far.md)
- [露出](../tonemapping/exposure.md)
