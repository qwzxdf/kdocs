---
title: カラー グレーディング
tags:
  - 描画
---

# カラー グレーディング

**映画・写真**では<strong>撮影した映像の色を後から調整（グレーディング）</strong>して、**作品の雰囲気**（暖かい・冷たい・くすんだ・鮮やか）を**作ります**。**ゲームでも同様**に**トーンマップの後（または前）に、色の調整**をかけて、**絵作りの最終仕上げ**をします。**調整の手段**は**ホワイト バランス・コントラスト・彩度・リフト/ガンマ/ゲイン**などですが、**これらをすべて 1 つの 3D LUT（ルックアップ テーブル）に焼き込む**と**安く、自由な色変換**ができます。

!!! tip "ポイント"
    - <strong>グレーディング ＝ 色の変換</strong>（RGB → RGB）。<strong>雰囲気づくり</strong>が目的。
    - <strong>基本操作</strong>：<strong>露出・ホワイト バランス・コントラスト・彩度・リフト/ガンマ/ゲイン・カラー バランス</strong>。
    - <strong>3D LUT</strong>：<strong>色の変換を、3D テクスチャに事前計算</strong>。<strong>実行時は、1 回サンプルするだけ</strong>。
    - <strong>LUT の入力は、トーンマップ後の LDR（または対数空間）</strong>。<strong>解像度は 32³ 程度</strong>で十分。
    - <strong>DCC ツールで、Neutral LUT にグレーディングを施して書き出す</strong>と、<strong>画像編集ソフトで色を作れる</strong>。
    - <strong>ゾーンごと・時間帯ごとの LUT を、補間</strong>して<strong>雰囲気を切り替え</strong>られる。

## 基本的な色調整

| 操作 | 内容 |
| --- | --- |
| <strong>露出（Exposure）</strong> | **全体の明るさ**（EV で、2 倍ずつ） |
| **ホワイト バランス** | <strong>色温度（暖色〜寒色）・色合い（緑〜マゼンタ）</strong>。**光源の色を白に補正する** |
| **コントラスト** | **明暗の差**。**中間の灰色（ピボット）を中心に広げる・縮める** |
| <strong>彩度（Saturation）</strong> | **色の鮮やかさ**。**0 でモノクロ** |
| **リフト / ガンマ / ゲイン** | <strong>暗部（リフト）・中間（ガンマ）・明部（ゲイン）</strong>を**別々に調整**（色相・明るさ） |
| <strong>カラー バランス（シャドウ / ミッド / ハイライト）</strong> | **明るさの領域ごとに色味を足す**（**シネマの定番：影に青緑、ハイライトにオレンジ**） |

### コントラスト・彩度

```hlsl
float3 ApplyContrast(float3 color, float contrast, float pivot) {
  return (color - pivot) * contrast + pivot;
}

float3 ApplySaturation(float3 color, float saturation) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return lerp(float3(luma, luma, luma), color, saturation);
}
```

| 点 | 説明 |
| --- | --- |
| **`pivot`** | **コントラストの中心**（<strong>中間の灰色、約 0.18（リニア）</strong>または <strong>0.5（ガンマ空間）</strong>）。**この値は変わらず、明暗が広がる** |
| **彩度の `lerp`** | **輝度（モノクロ）と元の色の間を補間**。**`saturation > 1` で、鮮やか** |

### リフト / ガンマ / ゲイン

**ASC CDL**（Color Decision List）に**準じた**、**スロープ・オフセット・パワー**の**形式**でも**表現**されます。

```hlsl
float3 LiftGammaGain(float3 color, float3 lift, float3 gamma, float3 gain) {
  color = color * gain + lift;
  color = max(color, 0.0);
  return pow(color, 1.0 / gamma);
}
```

| 項目 | 影響する範囲 |
| --- | --- |
| <strong>ゲイン（Gain）</strong> | **全体に掛ける**。**特に明部**に**強く効く**（**傾き**） |
| <strong>リフト（Lift）</strong> | **全体に足す**。**特に暗部**に**強く効く**（**黒の持ち上げ**） |
| <strong>ガンマ（Gamma）</strong> | **べき乗**。**中間調**の**明るさ**を**変える** |

### ホワイト バランス

**色温度**（ケルビン、K）から、**光源の色を推定し、補正**します。**簡易的な実装**では、**LMS 色空間**で**ゲイン**を**調整**します。

```hlsl
float3 WhiteBalance(float3 color, float temperature, float tint) {
  float t1 = temperature / 0.6;
  float t2 = tint / 0.6;
  float x = 0.31271 - t1 * (t1 < 0.0 ? 0.1 : 0.05);
  float y = 2.87 * x - 3.0 * x * x - 0.27509 + t2 * 0.05;
  float3 xyz = float3(x / y, 1.0, (1.0 - x - y) / y);
  float3 lms = mul(kXyzToLms, xyz);
  float3 white_lms = mul(kXyzToLms, float3(0.95047, 1.0, 1.08883));
  float3 balance = white_lms / lms;
  float3 color_lms = mul(kRgbToLms, color);
  return mul(kLmsToRgb, color_lms * balance);
}
```

**`kXyzToLms`・`kRgbToLms`・`kLmsToRgb`**は、**色空間変換の 3×3 行列**です。<strong>温度を上げると暖色（黄〜オレンジ）、下げると寒色（青）</strong>に**補正**します。

## 3D LUT

**上記の調整を画素ごとに毎フレーム計算**するのは、<strong>無駄（全て、色→色の関数）</strong>です。**入力の色（R, G, B）を、3 軸とする 3D テクスチャ**に、**あらかじめ、変換後の色を書き込んで**おけば、**実行時は画素の色で引くだけ**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="3D LUT">
<text x="20" y="24" class="fig-title">色（R, G, B）を座標にして、3D テクスチャから変換後の色を引く</text>
<g stroke="currentColor" stroke-width="2" fill="none"><polygon points="80,110 200,110 200,200 80,200" fill="rgba(76,139,245,0.12)"/><polygon points="80,110 130,70 250,70 200,110" fill="rgba(76,139,245,0.2)"/><polygon points="200,110 250,70 250,160 200,200" fill="rgba(76,139,245,0.28)"/></g>
<text x="60" y="224" style="font-size:12px">32×32×32 の格子（各セルに、変換後の RGB）</text>
<text x="270" y="190" style="font-size:12px">R →</text><text x="40" y="130" style="font-size:12px">G ↑</text><text x="120" y="60" style="font-size:12px">B（奥）</text>
<text x="400" y="90" style="font-size:13px">入力色 (r, g, b) → 3D テクスチャ座標</text><text x="400" y="120" style="font-size:13px">トライリニア補間で、変換後の色を取得</text>
<text x="400" y="160" style="font-size:12px">1 回のサンプルで、何段階もの色調整を、まとめて適用できる</text>
</svg>

### LUT の作成（コンピュート）

**N³ の各格子点**に対し、**その座標（RGB）を入力**として、**色調整を順に適用**し、**結果を書き込みます**。

```hlsl
RWTexture3D<float4> lut : register(u0);

cbuffer LutConstants : register(b0) {
  float lut_size;
  float contrast;
  float saturation;
  float temperature;
  float tint;
  float3 lift;
  float3 gamma;
  float3 gain;
};

[numthreads(8, 8, 8)]
void BuildLut(uint3 id : SV_DispatchThreadID) {
  if (any(id >= (uint)lut_size)) return;

  float3 color = float3(id) / (lut_size - 1.0);
  color = WhiteBalance(color, temperature, tint);
  color = ApplyContrast(color, contrast, 0.5);
  color = LiftGammaGain(color, lift, gamma, gain);
  color = ApplySaturation(color, saturation);
  lut[id] = float4(saturate(color), 1.0);
}
```

| 点 | 説明 |
| --- | --- |
| **`float3(id) / (lut_size - 1)`** | **格子点の座標を、0〜1 の色**に**変換** |
| **`RWTexture3D`** | **3D テクスチャに書く**（フォーマット：`R10G10B10A2_UNORM`・`R16G16B16A16_FLOAT` など） |
| **作成のタイミング** | **パラメータが変わったときだけ**（毎フレームは不要）。<strong>または毎フレーム（32³ なら、極小コスト）</strong> |

### 画素への適用

```hlsl
float3 ApplyLut(float3 color, Texture3D<float4> lut_texture, SamplerState linear_clamp,
                float lut_size) {
  float3 uvw = saturate(color) * ((lut_size - 1.0) / lut_size) + (0.5 / lut_size);
  return lut_texture.SampleLevel(linear_clamp, uvw, 0).rgb;
}
```

| 点 | 説明 |
| --- | --- |
| **`(lut_size - 1) / lut_size`、`0.5 / lut_size`** | **テクセルの中心**に**合わせる補正**。**端の色がずれない** |
| **クランプ サンプラー** | **範囲外に出ない** |
| **バイリニア（トライリニア）補間** | **格子点の間を線形補間**。**32³ でも滑らか** |

### 解像度

| サイズ | 特徴 |
| --- | --- |
| **16³** | **粗い**（簡易） |
| **32³** | **標準**（**多くのゲーム**） |
| **64³** | **高精度**（**暗部の細かいグラデーション**） |

**線形な色空間のまま**、**LUT の入力**にすると、**暗部が少数の格子点**に**集中**して、**バンディング**が出ます。**入力を対数（ログ）空間**や**ガンマ空間**に**変換してから、LUT を引く**と**格子点が知覚的に均等**になります。

```hlsl
float3 LinearToLogC(float3 x) {
  const float a = 5.555556;
  const float b = 0.047996;
  const float c = 0.244161;
  const float d = 0.386036;
  return c * log10(a * x + b) + d;
}
```

**ARRI LogC**などの**ログ曲線**で、**HDR の広い範囲を、0〜1 に圧縮して、LUT を引きます**。**ACES の AP1 ＋ ACEScc** などの**色空間**も**同様**です。

## 外部ツールでのグレーディング

**DCC ツール**（Photoshop・DaVinci Resolve など）で**グレーディング**し、**LUT として書き出して**、**ゲームに取り込む**ワークフローです。

| 手順 | 内容 |
| --- | --- |
| **① Neutral LUT を出力** | **変換なしの LUT 画像**（**色がそのまま格子に並んだ画像**）を、**ゲームから書き出す** |
| **② スクリーンショットに適用** | **ゲーム画面のスクリーンショットと、Neutral LUT を、ツールに並べて**開く |
| **③ グレーディング** | **スクリーンショットを見ながら、色調整**。**同じ調整が、Neutral LUT にも反映される**（**調整レイヤーを両方に適用**） |
| **④ 書き出し** | **グレーディング後の LUT 画像**を**保存** |
| **⑤ ゲームに取り込む** | **2D の「ストリップ」画像を、3D テクスチャに変換** |

**Neutral LUT の 2D 配置**（**32 枚の 32×32 スライスを、横一列に並べた 1024×32 の画像**）が**標準**です。

```hlsl
float3 ApplyLut2D(float3 color, Texture2D<float4> lut_strip, SamplerState linear_clamp) {
  const float size = 32.0;
  float3 scaled = saturate(color) * (size - 1.0);
  float slice = scaled.b;
  float slice0 = floor(slice);
  float slice1 = min(slice0 + 1.0, size - 1.0);
  float blend = slice - slice0;

  float2 uv0 = float2((slice0 * size + scaled.r + 0.5) / (size * size), (scaled.g + 0.5) / size);
  float2 uv1 = float2((slice1 * size + scaled.r + 0.5) / (size * size), (scaled.g + 0.5) / size);
  float3 c0 = lut_strip.SampleLevel(linear_clamp, uv0, 0).rgb;
  float3 c1 = lut_strip.SampleLevel(linear_clamp, uv1, 0).rgb;
  return lerp(c0, c1, blend);
}
```

| 点 | 説明 |
| --- | --- |
| **B をスライス番号** | **青の値で、32 枚のスライスから選ぶ** |
| **2 枚のスライスを補間** | **B 方向は自分で補間**（**2D テクスチャでは、ハードウェア補間が効かない**） |
| **3D テクスチャが使える場合** | **直接 3D サンプル**で**簡単**。**2D は互換性のため** |

## ゾーンごと・時間帯ごとの LUT

<strong>場面（洞窟・屋外・戦闘中）</strong>で、**LUT を切り替える**と、**雰囲気**を**演出**できます。**LUT 間を補間**して**滑らかに遷移**させます。

```hlsl
float3 graded_a = ApplyLut(color, lut_a, linear_clamp, lut_size);
float3 graded_b = ApplyLut(color, lut_b, linear_clamp, lut_size);
float3 graded = lerp(graded_a, graded_b, blend_factor);
```

| 方式 | 内容 |
| --- | --- |
| **LUT 同士を画素で補間** | **2 回サンプルして `lerp`**。**簡単** |
| **LUT 自体を事前に補間** | **LUT 作成のコンピュートで、2 つの LUT を混ぜて、新しい LUT**を作る（**画素ごとのコストが 1 回のサンプルのまま**） |
| **ボリュームでブレンド** | **ポスト プロセス ボリューム**に**入った度合い**で**補間** |

## トーンマップとの関係

| 順序 | 内容 |
| --- | --- |
| <strong>トーンマップ → LUT（LDR）</strong> | **LUT の入力が、0〜1 の LDR**。**簡単**。**HDR の範囲は、LUT では使えない** |
| **LUT（HDR・ログ空間）→ トーンマップ** | **HDR のまま、ログ空間で LUT**。**映画的**。**LUT の精度要求が高い** |
| **トーンマップを LUT に統合** | **トーンマップ ＋ グレーディングを、1 つの HDR 用 LUT に焼き込む**（**Unreal Engine の方式**） |

**どれを選ぶ**かは、<strong>「トーンマップの特性を、LUT で自由に変えたいか」</strong>で**決まります**。

## よくあるミス

??? failure "LUT の端で、色がずれる（0.5 テクセルの補正がない）"
    **`* (size - 1) / size + 0.5 / size`** で**中心**に**合わせる**。

??? failure "リニアの色を、そのまま LUT に入れて、暗部がバンディングする"
    **入力をログ空間・ガンマ空間に**変換してから**引く**。

??? failure "LUT を、sRGB のテクスチャとして読んで、色が二重にガンマ補正される"
    <strong>LUT はリニア（UNORM）</strong>として**読む**（**sRGB フラグを付けない**）。

??? failure "グレーディングを、トーンマップの前の HDR（リニア）で、LDR の LUT で行う"
    **LDR の LUT は、トーンマップ後**に。

??? failure "Neutral LUT と、実際の LUT の並び（R/G/B の軸）がずれて、色がおかしい"
    **軸の並び・スライスの向き**を**揃える**（**エクスポート・インポート**で**確認**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] グレーディング ＝ <strong>色の変換で、雰囲気を作る</strong>。<strong>ホワイト バランス・コントラスト・彩度・リフト/ガンマ/ゲイン</strong>
    - [x] <strong>3D LUT</strong> ＝ <strong>色（RGB）を座標に変換後の色を保存した 3D テクスチャ</strong>。<strong>実行時は 1 回のサンプル</strong>
    - [x] <strong>32³</strong> が<strong>標準</strong>。<strong>ログ空間の入力</strong>で<strong>暗部のバンディング</strong>を<strong>防ぐ</strong>。<strong>テクセル中心の補正</strong>を<strong>忘れない</strong>
    - [x] <strong>Neutral LUT ＋ 画像編集ツール</strong>で<strong>アーティストが色を作れる</strong>
    - [x] <strong>LUT 同士の補間</strong>で<strong>ゾーン・時間帯の雰囲気切り替え</strong>

## 参考

- Hable, "Real-Time Color Grading"／"Filmic Worlds"
- Selan, "Using Lookup Tables to Accelerate Color Transformations"（GPU Gems 2）
- ASC, "ASC CDL"（Color Decision List）
- Epic Games, "Color Grading"（Unreal Engine ドキュメント）

## 関連ページ

- [ポストプロセス](index.md)
- [トーンマッピングと露出](tonemapping.md)
- [レンズ効果](lens-effects.md)
