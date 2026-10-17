---
title: 屈折とガラス
tags:
  - 描画
---

# 屈折とガラス

**ガラスや水**は、**ただ透けて見える**だけでなく、<strong>向こう側の景色が歪んで見えます（屈折）</strong>。<strong>角度によって、反射が強まり（フレネル）</strong>、**厚いガラスは色が付き**、**表面には、周囲の景色が映ります**。このページでは、**屈折の原理（スネルの法則）・画面空間での屈折の実装（背景のコピー）・フレネル・厚みによる色（ビア＝ランバートの法則）・色収差・薄いガラスと厚いガラスの違い**を説明します。

!!! tip "ポイント"
    - <strong>屈折</strong> ＝ <strong>光が、媒質の境目で、曲がる</strong>。<strong>スネルの法則</strong>：<strong>n₁ sinθ₁ ＝ n₂ sinθ₂</strong>。
    - HLSL の<strong>`refract(I, N, eta)`</strong> が、<strong>屈折ベクトル</strong>を返す。<strong>eta ＝ n₁ / n₂</strong>。
    - <strong>画面空間の屈折</strong>：<strong>不透明を描いた画像をコピー</strong>し、<strong>歪んだ位置を読んで</strong>、<strong>背景として使う</strong>。
    - <strong>フレネル</strong>：<strong>浅い角度ほど反射が強く、屈折（透過）が弱くなる</strong>（<strong>Schlick の近似</strong>）。
    - <strong>厚み</strong>で色が付く：<strong>透過率 ＝ exp(−吸収係数 × 厚み)</strong>（ビア＝ランバート）。
    - <strong>画面空間の屈折は、屈折物の後ろにある半透明が写らない・画面外が取れない</strong>という限界がある。

## 屈折の原理

**光が、空気からガラスや水へ入るとき、境目で曲がります**。<strong>曲がり方は、媒質ごとの「屈折率」</strong>で決まります。

| 媒質 | 屈折率（n） |
| --- | --- |
| **真空・空気** | **1.00** |
| **水** | **1.33** |
| **ガラス** | **約 1.5** |
| **ダイヤモンド** | **約 2.4** |

### スネルの法則

<div class="formula">n₁ · sin θ₁ = n₂ · sin θ₂</div>

| 記号 | 意味 |
| --- | --- |
| **n₁・n₂** | **入る側・出る側の媒質の屈折率** |
| **θ₁** | **入射角**（面の法線と、入る光のなす角） |
| **θ₂** | **屈折角**（面の法線と、曲がった光のなす角） |

**空気（1.0）から水（1.33）へ入る**と、**屈折率が大きい側へ入る**ので、**法線に近づく向きに曲がります**。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="屈折">
<text x="20" y="24" class="fig-title">光は、屈折率の大きい媒質へ入ると、法線に近づく向きに曲がる</text>
<rect x="40" y="140" width="700" height="110" fill="rgba(76,139,245,0.18)"/>
<line x1="40" y1="140" x2="740" y2="140" stroke="currentColor" stroke-width="3"/>
<line x1="390" y1="60" x2="390" y2="230" stroke="currentColor" stroke-dasharray="4 4" stroke-opacity="0.6"/><text x="396" y="70" style="font-size:12px">法線</text>
<line x1="230" y1="50" x2="390" y2="140" stroke="#e5aa28" stroke-width="3"/><text x="230" y="44" style="font-size:12px;fill:#e5aa28">入射光</text>
<line x1="390" y1="140" x2="480" y2="236" stroke="#4c8bf5" stroke-width="3"/><text x="486" y="236" style="font-size:12px;fill:#4c8bf5">屈折光</text>
<line x1="390" y1="140" x2="520" y2="70" stroke="currentColor" stroke-width="2" stroke-opacity="0.5" stroke-dasharray="3 3"/><text x="524" y="68" style="font-size:12px">反射光（フレネルで強さが変わる）</text>
<text x="60" y="120" style="font-size:12px">空気（n = 1.0）</text><text x="60" y="270" style="font-size:12px">ガラスや水（n = 1.33〜1.5）</text>
<path d="M 390 105 A 35 35 0 0 0 366 112" fill="none" stroke="#e5aa28" stroke-width="2"/><text x="352" y="100" style="font-size:12px;fill:#e5aa28">θ₁</text>
<path d="M 390 175 A 35 35 0 0 0 407 170" fill="none" stroke="#4c8bf5" stroke-width="2"/><text x="406" y="196" style="font-size:12px;fill:#4c8bf5">θ₂（θ₁ より小さい）</text>
</svg>

### HLSL の refract

**HLSL の組み込み関数 `refract`** が、**屈折した向き**を返します。

```hlsl
float3 refracted = refract(incident, normal, eta);
```

| 引数 | 内容 |
| --- | --- |
| **`incident`** | **入射する光の向き**（**正規化**済み。**光が進む向き**＝視線方向） |
| **`normal`** | **面の法線**（**入る側を向く**） |
| **`eta`** | **屈折率の比 `n₁ / n₂`**（**空気 → 水なら 1.0 / 1.33**） |
| **戻り値** | **屈折した向き**。**全反射**（臨界角を超える）なら、**`(0, 0, 0)`** |

**視線方向**（カメラから面へ向かう向き）を `incident` に渡します。**反射は `reflect(incident, normal)`** で得られます。

## 画面空間の屈折

**屈折した光線を、本当に追跡する**（レイトレ）のは重いので、**ゲームでは、画面の画像を「背景」として、歪めて読む**方法が**標準**です。

### 手順

| 手順 | 内容 |
| --- | --- |
| **① 不透明を描く** | **不透明な物を、すべて描画** |
| **② 画像をコピー** | **この時点の画面（HDR カラー）を、別のテクスチャ（`scene_color_copy`）にコピー** |
| **③ 半透明を描く** | **ガラスの面で、`scene_color_copy` を、歪んだ UV で読み、背景とする** |

**なぜコピーが要るか**：**ガラスを描くレンダー ターゲットを、同時にテクスチャとして読めない**（**読み書きの競合**）ためです。

### UV の歪ませ方

**法線の XY 成分（ビュー空間）に応じて、UV をずらす**のが**簡易**です。

```hlsl
float2 screen_uv = input.position.xy / screen_size;
float3 view_normal = mul(world_normal, (float3x3)view_matrix);
float2 offset = view_normal.xy * refraction_strength;
float3 background = scene_color_copy.Sample(linear_clamp, screen_uv + offset).rgb;
```

| 点 | 説明 |
| --- | --- |
| **`view_normal.xy`** | **法線が、画面の左右・上下にどれだけ傾いているか** |
| **`refraction_strength`** | **歪みの強さ**（**屈折率・厚み**に合わせて調整。**0.02〜0.1**） |
| **`linear_clamp`** | **端でクランプ**（**画面外を読まない**） |

**より物理的**には、**`refract` で屈折ベクトルを求め、そのベクトルを使って、「背景の画面位置」を決める**方法もあります。

```hlsl
float3 view_dir = normalize(world_position - camera_position);
float3 refracted = refract(view_dir, world_normal, 1.0 / 1.5);
float3 sample_world = world_position + refracted * thickness;
float4 clip = mul(float4(sample_world, 1.0), view_projection);
float2 refract_uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
float3 background = scene_color_copy.Sample(linear_clamp, refract_uv).rgb;
```

| 点 | 説明 |
| --- | --- |
| **`thickness`** | **ガラスの厚み**（**屈折した光が進む距離の見積もり**）。**固定値・テクスチャ・深度差** |
| **`sample_world`** | **屈折光が、ガラスを出たあたりのワールド位置** |
| **`refract_uv`** | **その位置を、画面に投影した UV**。**ここの背景を読む** |

## 屈折の境界の問題

**画面空間の屈折には、典型的な破綻**があります。

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **前景の物が、屈折で背景に混ざる** | **ガラスより手前にある不透明物の画素**を、**屈折で読んでしまう** | **読んだ位置の深度が、ガラスより手前なら、屈折せず元の位置を読む** |
| **画面外を読む** | **歪んだ UV が、画面の外に出る** | **クランプ・端でフェード・歪みを弱める** |
| **後ろの半透明が写らない** | **コピーは、不透明のみ** | **半透明のソート順で、コピーを取り直す**（コスト大）・**割り切る** |
| **ガラスの後ろのガラス** | **屈折物どうしが重なる** | **1 層のみ対応**と割り切る・**レイトレ** |

### 前景の混入を避ける

```hlsl
float refracted_depth = LinearDepth(depth_texture.Sample(point_clamp, refract_uv).r);
float glass_depth = LinearDepth(input.position.z);
if (refracted_depth < glass_depth) {
  refract_uv = screen_uv;
}
float3 background = scene_color_copy.Sample(linear_clamp, refract_uv).rgb;
```

**屈折先の深度が、ガラスより手前**（＝**ガラスの前の物**を読んでしまう）なら、**屈折をやめて**、**元の位置**を**読みます**。

## フレネル

**浅い角度**（面すれすれ）で見るほど、**反射が強く、透過（屈折）が弱く**なります。**水面を、真上から見ると底が見え、遠くを見ると空が映る**のは、**フレネル**です。

**Schlick の近似**：

<div class="formula">F = F₀ + (1 − F₀) · (1 − cos θ)⁵　　F₀ = ((n₁ − n₂) / (n₁ + n₂))²</div>

| 記号 | 意味 |
| --- | --- |
| **F₀** | **真正面から見たときの反射率**（**ガラス・水は約 0.02〜0.04**） |
| **cos θ** | **視線と法線の内積** |
| **F** | **反射率**（0〜1）。**透過は `1 − F`** |

```hlsl
float Fresnel(float cos_theta, float f0) {
  return f0 + (1.0 - f0) * pow(1.0 - saturate(cos_theta), 5.0);
}

float f = Fresnel(dot(normal, -view_dir), 0.04);
float3 color = lerp(refracted_background, reflection, f);
```

| 点 | 説明 |
| --- | --- |
| **`F₀ = 0.04`** | **非金属（ガラス・水・プラスチック）の標準値** |
| **`lerp(屈折, 反射, F)`** | **F が大きいほど、反射が強く**なる |
| **反射の色** | **環境マップ・SSR・プローブ**（[反射](../reflections/index.md)） |

## 厚みと色（ビア＝ランバートの法則）

**色付きガラスや水は、厚いほど、光が吸収されて色が濃く**なります。

<div class="formula">T = exp(−σ · d)　（T：透過率、σ：吸収係数（RGB）、d：厚み）</div>

| 記号 | 意味 |
| --- | --- |
| <strong>σ（シグマ）</strong> | **単位長さあたりの吸収**（**色ごと**）。**水は赤を強く吸収**（σ_r が大きい） |
| **d** | **光が媒質の中を進む距離**（厚み） |
| **T** | **透過する光の割合**（RGB） |

```hlsl
float3 absorption = float3(0.4, 0.1, 0.05);
float3 transmittance = exp(-absorption * thickness);
float3 tinted_background = background * transmittance;
```

| 点 | 説明 |
| --- | --- |
| **`absorption`** | <strong>吸収係数（RGB）</strong>。**水なら、赤を強く、青を弱く**吸収し、**青緑に見える** |
| **`thickness`** | **厚み**。**ガラスなら、ほぼ一定**。<strong>水なら、水深（深度差）</strong> |
| **`exp(-σd)`** | **厚いほど、急に暗く・濃く** |

**水深**（水面から底までの距離）は、**不透明の深度と、水面の深度の差**から**求められます**（[水](../water/index.md)）。

## 色収差（分散）

**波長ごとに屈折率が少し違う**ので、**ガラスの縁で、色がずれて見えます**（**プリズムの虹**）。**R・G・B で、屈折の強さを少しずつ変えて、3 回サンプル**します。

```hlsl
float3 background;
background.r = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.00).r;
background.g = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.03).g;
background.b = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.06).b;
```

**わずか（数%）の差**で**十分**です。**宝石・水晶・厚いガラス**で**効果的**です。

## 薄いガラスと厚いガラス

| 種類 | 例 | 屈折 | 表現 |
| --- | --- | --- | --- |
| <strong>薄いガラス（板）</strong> | **窓・ガラス戸** | **ほぼ無視**（**入口と出口で相殺**） | <strong>透過 ＋ 反射（フレネル）</strong> のみ |
| **厚いガラス・水** | **瓶・水槽・宝石** | **目立つ** | **屈折 ＋ 厚みの色 ＋ 反射** |
| **曇りガラス** | **すりガラス** | **ぼやける** | **背景を、ミップや大きなブラーで読む**（粗さに応じて） |

**窓ガラス**は、**屈折を省いて、単純な半透明**にすれば**十分**です。

### 曇りガラス（粗い屈折）

**粗い面ほど、背景がぼやけて見える**ので、<strong>背景コピーのミップ（ブラー済み）</strong>を、**粗さに応じて**読みます。

```hlsl
float mip = roughness * kMaxMip;
float3 background = scene_color_mips.SampleLevel(linear_clamp, refract_uv, mip).rgb;
```

**背景のコピーに、ミップ チェーンを作って**おく（[ブルームのダウンサンプル](../postprocess/bloom/index.md)と同様）。

## 実装の全体像

```hlsl
float4 PSGlass(VsOutput input) : SV_Target {
  float3 n = normalize(input.normal);
  float3 v = normalize(camera_position - input.world_position);
  float2 screen_uv = input.position.xy / screen_size;

  float3 refracted = refract(-v, n, 1.0 / ior);
  float2 uv = ScreenUvFromWorld(input.world_position + refracted * thickness);
  uv = ValidateUv(uv, screen_uv, input.position.z);

  float3 background = scene_color_copy.SampleLevel(linear_clamp, uv, roughness * kMaxMip).rgb;
  background *= exp(-absorption * thickness);

  float3 reflection = SampleEnvironment(reflect(-v, n), roughness);
  float fresnel = Fresnel(saturate(dot(n, v)), 0.04);
  float3 color = lerp(background, reflection, fresnel);
  return float4(color, 1.0);
}
```

**出力アルファは 1**（**背景を、自分で混ぜている**ため）。<strong>ブレンドは、不要（上書き）</strong>です。

## 屈折のコストと限界

| 項目 | 内容 |
| --- | --- |
| **背景のコピー** | **フル解像度の HDR カラー 1 枚**（**帯域**） |
| **半透明の重なり** | **コピーは不透明のみ**。**重なるガラスは、別途** |
| **画面空間の限界** | **画面外・裏側の物は、屈折で写らない** |
| **レイトレの屈折** | **正確**（画面外・多重屈折も OK）。**HW RT が必要**（[RT 反射](../reflections/rt-reflections/index.md)） |

## よくあるミス

??? failure "屈折先に、ガラスより手前の物が混ざる"
    **屈折先の深度を比べて、手前なら元の UV を使う**。

??? failure "屈折の UV が画面外に出て、端がおかしい"
    **クランプ サンプラー**・**端でフェード**。

??? failure "ガラスを描いたレンダー ターゲットを、そのまま背景として読む"
    **不透明を描いた後に、コピー**を取って、**コピーを読む**。

??? failure "薄い窓ガラスに、強い屈折をかけて、不自然に歪む"
    **薄いガラスは、屈折を省く**（透過 ＋ 反射のみ）。

??? failure "フレネルを省いて、ガラスが常に同じ透明度で、作り物に見える"
    **Schlick のフレネル**で、**反射と透過を混ぜる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 屈折 ＝ <strong>媒質の境目で光が曲がる</strong>（<strong>スネルの法則</strong>）。<strong>`refract(I, N, eta)`</strong>（eta ＝ n₁/n₂）
    - [x] <strong>画面空間の屈折</strong> ＝ <strong>不透明の画像をコピーして、歪んだ UV で読む</strong>
    - [x] <strong>前景の混入・画面外・後ろの半透明</strong>に<strong>限界</strong>。<strong>深度比較・クランプ</strong>で対処
    - [x] <strong>フレネル（Schlick）</strong>で<strong>反射と透過を混ぜる</strong>。<strong>厚みで色が付く（exp(−σd)）</strong>
    - [x] <strong>薄いガラスは屈折を省く</strong>。<strong>曇りガラスは、背景のミップを粗さで読む</strong>

## 参考

- Snell's law／Fresnel equations（物理の基礎）
- Schlick, "An Inexpensive BRDF Model for Physically-based Rendering"（1994）
- Microsoft, "refract (HLSL)"

## 関連ページ

- [半透明](index.md)
- [ブレンドとソート](blending-sorting.md)
- [反射](../reflections/index.md)
- [水](../water/index.md)
- [PBR](../../3d/pbr.md)
