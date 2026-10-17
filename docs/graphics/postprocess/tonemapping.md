---
title: トーンマッピングと露出
tags:
  - 描画
---

# トーンマッピングと露出

**現実の明るさ**は、**暗い部屋の 0.01 から、太陽の 100,000 まで**、**桁違いの幅**があります。**ディスプレイが出せる範囲**は、<strong>0〜1（LDR）</strong>です。**HDR で計算した光**を、**この狭い範囲に収める**のが**トーンマッピング**です。単に「割って詰める」のではなく、**暗部のディテールと明部の飽和を、見た目が自然になるよう、曲線で圧縮**します。**その前段として、「どれだけ明るく撮るか」＝露出**を決めます。

!!! tip "ポイント"
    - <strong>露出</strong> ＝ <strong>光の量にかける倍率</strong>（カメラの絞り・シャッター・ISO）。<strong>EV（露出値）</strong>で表す。
    - <strong>トーンマップ</strong> ＝ <strong>HDR → 0〜1 への、単調増加の曲線</strong>。<strong>S 字</strong>が<strong>フィルムの特性</strong>に近い。
    - <strong>Reinhard</strong>：<strong>x / (1 + x)</strong>。<strong>簡単</strong>だが<strong>低コントラスト</strong>。
    - <strong>フィルミック（Hable・ACES 近似・AgX）</strong>：<strong>S 字で締まった黒・自然な明部のロールオフ</strong>。
    - <strong>自動露出（Eye Adaptation）</strong>：<strong>平均輝度（ヒストグラム）から露出を決め、時間で滑らかに追従</strong>。
    - <strong>ガンマ（sRGB）変換はトーンマップの後</strong>。<strong>リニア空間で計算</strong>。

## 露出

**カメラ**は**絞り（F 値）・シャッター速度・ISO 感度**で**センサーに当たる光の量**を**調整**します。<strong>ゲームではこれを「1 つの倍率」</strong>にまとめます。

<div class="formula">露出後の値 = 輝度 × 2^(−EV)　（または 輝度 × exposure）</div>

| 概念 | 内容 |
| --- | --- |
| <strong>EV（Exposure Value）</strong> | **1 EV の違い ＝ 光の量が 2 倍**。**ストップ**とも呼ぶ |
| **EV100** | **ISO 100 を基準にした EV**。**物理ベースの露出**で使う |
| **露出補正** | **自動露出の結果に加える EV のずれ**（**アーティストの調整**） |

### 物理ベースの露出（EV100）

```hlsl
float ExposureFromEV100(float ev100) {
  float max_luminance = 1.2 * exp2(ev100);
  return 1.0 / max_luminance;
}
```

| 点 | 説明 |
| --- | --- |
| **`1.2 * exp2(ev100)`** | **飽和輝度（SBS 方式）<strong>。</strong>この輝度でちょうど 1 になる** |
| **典型的な EV100** | **晴天の屋外 約 15**・**曇り 約 12**・**室内 約 5〜8**・**夜景 約 0〜3** |
| **利点** | **ライトの単位（ルクス・カンデラ）を、物理値**で**揃える**と**シーンが明るさに依存せず一貫**して見える |

## トーンマッピングの曲線

<strong>露出を掛けた HDR の値 `x`（0〜∞）</strong>を、**0〜1 に写す関数**です。

### 単純なクランプ

`min(x, 1)`：<strong>1 を超えた部分が真っ白に潰れる（飽和）</strong>。**明部のディテールが失われ**、<strong>色が白に偏る（色相が壊れる）</strong>ため、**実用には不向き**です。

### Reinhard

<div class="formula">c = x / (1 + x)</div>

```hlsl
float3 Reinhard(float3 x) {
  return x / (1.0 + x);
}
```

| 性質 | 内容 |
| --- | --- |
| **単調増加** | **∞ に近づくほど 1 に漸近**（**飽和しない**） |
| **低コントラスト** | **中間も圧縮される**ので**全体が白っぽく・眠い** |
| **拡張版** | **`x (1 + x / L_w²) / (1 + x)`**。**白点 `L_w`** を決めて、**そこを 1 にする** |

### フィルミック（Hable / Uncharted 2）

**S 字カーブ**で<strong>暗部を締め（黒を沈め）</strong>、**明部をなだらかにロールオフ**します。

```hlsl
float3 HableCurve(float3 x) {
  const float a = 0.15;
  const float b = 0.50;
  const float c = 0.10;
  const float d = 0.20;
  const float e = 0.02;
  const float f = 0.30;
  return ((x * (a * x + c * b) + d * e) / (x * (a * x + b) + d * f)) - e / f;
}

float3 HableTonemap(float3 color) {
  const float white_point = 11.2;
  return HableCurve(color * 2.0) / HableCurve(white_point);
}
```

| 点 | 説明 |
| --- | --- |
| **`a〜f`** | **カーブの形を決める係数**（**肩の強さ・直線部・つま先**） |
| **`white_point`** | **1 に対応する入力値**（**白点**） |
| **S 字** | <strong>暗部（つま先）</strong>で**立ち上がりを抑え**、**中間（直線部）でコントラスト**、**明部（肩）で、滑らかに飽和** |

### ACES（近似）

**ACES**（Academy Color Encoding System）は、**映画業界の標準的な色管理**で、**トーンマップの参照曲線**が**ゲームで広く使われます**。**フィット（近似）式**が**手軽**です。

```hlsl
float3 ACESFilm(float3 x) {
  const float a = 2.51;
  const float b = 0.03;
  const float c = 2.43;
  const float d = 0.59;
  const float e = 0.14;
  return saturate((x * (a * x + b)) / (x * (c * x + d) + e));
}
```

| 性質 | 内容 |
| --- | --- |
| **コントラスト** | **強め**。**黒が締まり、鮮やか** |
| **色相の変化** | **明るい彩度の高い色が白に向かってシフト**（**フィルムのような、ハイライトの色飛び**）。**好みが分かれる** |
| **注意** | **近似式は本来の ACES（RRT+ODT）の簡略化**で**厳密には異なる** |

### AgX・Tony McMapface・Khronos PBR Neutral

**近年の色相が破綻しにくいトーンマップ**です。

| 方式 | 特徴 |
| --- | --- |
| **AgX**（Blender 標準など） | **ハイライトの色相のずれ・不自然な彩度を抑えた**、**中立寄りのフィルミック** |
| **Tony McMapface** | **3D LUT ベース**。**ブルーム・グレーディングとの相性が良い** |
| **Khronos PBR Neutral** | **商品の色をできるだけ忠実に**（**E コマース向け**） |

**どれを選ぶか**は、**作品の画作り**で決めます。**ゲームの標準的な選択肢**：<strong>ACES 近似・AgX・独自のフィルミック（LUT）</strong>。

## 曲線の比較

| 方式 | 暗部 | 中間 | 明部 | 色相 | 用途 |
| --- | --- | --- | --- | --- | --- |
| **クランプ** | そのまま | そのまま | **潰れる** | **壊れる** | 非推奨 |
| **Reinhard** | 持ち上がる | 低コントラスト | 滑らか | 保つ | **簡易** |
| **Hable** | **締まる** | **コントラスト** | 滑らか | ○ | **標準的** |
| **ACES 近似** | **締まる** | **強いコントラスト** | 滑らか（白へシフト） | **やや変化** | **標準的** |
| **AgX** | 締まる | 中立 | **滑らか・色相安定** | **良い** | **近年人気** |

## 輝度とトーンマップ：色相の保ち方

**R・G・B に別々にカーブを適用**すると、**彩度の高い明るい色**で**色相がずれ**ます（**例：オレンジが黄色に**）。**輝度（明るさ）にだけカーブを適用**し、**色の比率を保つ**方法もあります。

```hlsl
float Luminance(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

float3 TonemapLuminance(float3 color) {
  float l = Luminance(color);
  float mapped = Reinhard(float3(l, l, l)).x;
  return color * (mapped / max(l, 1e-4));
}
```

| 方式 | 内容 |
| --- | --- |
| **チャンネルごと** | **フィルムの特性に近く**、**ハイライトが白へ向かう**。**色飛びを意図的な表現**として使う |
| **輝度ベース** | **色相を保つ**が**非常に明るい彩度の高い色が、飽和しすぎる**ことがある |
| **ハイブリッド** | **両者を混ぜる**（**ACES・AgX は内部で彩度・色相の調整**を行う） |

## 自動露出（Eye Adaptation）

**暗い所から明るい所に出る**と、**目が慣れるまでまぶしい**です。**画面の平均的な明るさ**から**露出を自動で決め**、**時間をかけて追従**させます。

### 平均輝度

**画面の輝度の対数平均**（**幾何平均**）が**標準**です（**明るい点に引きずられにくい**）。

<div class="formula">L_avg = exp( (1/N) · Σ log(L + ε) )</div>

| 方式 | 内容 |
| --- | --- |
| <strong>ミップ チェーン（縮小）</strong> | **`log(L)` を、1×1 まで縮小**して**平均** |
| **ヒストグラム** | **輝度を数十〜256 のビン**に分けて**数え**、**暗い・明るい外れ値を除いた**範囲の平均を取る（**頑健**） |
| **中心重み** | **画面の中心を重視**して**平均** |

### 輝度ヒストグラム（コンピュート）

```hlsl
#define HISTOGRAM_BINS 256

RWStructuredBuffer<uint> histogram : register(u0);
Texture2D<float4> hdr_color : register(t0);

cbuffer HistogramConstants : register(b0) {
  uint2 size;
  float min_log_luminance;
  float inverse_log_luminance_range;
};

groupshared uint s_histogram[HISTOGRAM_BINS];

uint LuminanceToBin(float luminance) {
  if (luminance < 0.001) return 0;
  float log_luminance = saturate((log2(luminance) - min_log_luminance) * inverse_log_luminance_range);
  return uint(log_luminance * 254.0 + 1.0);
}

[numthreads(16, 16, 1)]
void HistogramMain(uint3 id : SV_DispatchThreadID, uint group_index : SV_GroupIndex) {
  s_histogram[group_index] = 0;
  GroupMemoryBarrierWithGroupSync();

  if (all(id.xy < size)) {
    float3 color = hdr_color.Load(int3(id.xy, 0)).rgb;
    uint bin = LuminanceToBin(Luminance(color));
    InterlockedAdd(s_histogram[bin], 1);
  }
  GroupMemoryBarrierWithGroupSync();

  InterlockedAdd(histogram[group_index], s_histogram[group_index]);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`s_histogram`（共有メモリ）</strong> | **グループ内でまず集計**し、**最後にグローバルへ足す**（**グローバルの原子操作を、減らす**） |
| **`log2` 空間のビン** | **輝度を対数で等間隔**に分ける（**人間の知覚に合う**） |
| **ビン 0** | **ほぼ黒**の画素を**除外**するための専用ビン |

**ヒストグラムから**、**下位・上位の数%を除いた範囲の平均**を求め、**目標の露出**を決めます。

### 時間的な追従

**目標露出に一気に変えず、指数的に近づけます**。

```hlsl
float AdaptExposure(float current, float target, float delta_time, float speed) {
  return current + (target - current) * (1.0 - exp(-delta_time * speed));
}
```

| 点 | 説明 |
| --- | --- |
| **`1 - exp(-dt * speed)`** | **フレームレートに依存しない<strong>、</strong>指数的な追従** |
| **明→暗と暗→明で速度を変える** | **目は暗順応のほうが遅い**ので、**暗くなる方向は、ゆっくり** |
| **露出の範囲を制限** | **最小・最大 EV**で**極端な値を防ぐ** |

## ガンマと sRGB

<strong>トーンマップの出力は、リニア（0〜1）</strong>です。**ディスプレイに出す前に、sRGB 曲線（ガンマ ≒ 2.2）をかける**必要があります。**`R8G8B8A8_UNORM_SRGB` のレンダー ターゲット**に**書けば、ハードウェアが自動で変換**します（**手動で `pow(c, 1/2.2)` する場合は通常の UNORM**）。

| やること | 順序 |
| --- | --- |
| **露出** | **HDR のリニア値に掛ける** |
| **トーンマップ** | **リニア HDR → リニア LDR** |
| **ガンマ変換** | **リニア LDR → sRGB**（**最後**） |

**ガンマ変換をトーンマップの前に行う**と、**暗部が潰れ**ます（**典型的な事故**）。

## HDR ディスプレイへの出力

**HDR 対応ディスプレイ**（HDR10）には、**LDR にせず、広い範囲**を**そのまま出せます**。

| 項目 | 内容 |
| --- | --- |
| **色空間** | **Rec.2020** ＋ **PQ（ST.2084）カーブ**（HDR10） |
| **スワップ チェーン** | **`DXGI_FORMAT_R10G10B10A2_UNORM`**（HDR10）または **`R16G16B16A16_FLOAT`**（scRGB） |
| **トーンマップ** | **ディスプレイの最大輝度（ニト）に合わせた**、**HDR 用のトーンマップ**（SDR 用とは別） |
| **UI** | <strong>UI の輝度（ペーパー ホワイト）</strong>を、**別に調整**して**合成** |

## よくあるミス

??? failure "ガンマ変換を、トーンマップの前にして、暗部が潰れ、全体が眠くなる"
    **リニアで計算 → トーンマップ → 最後に sRGB**。

??? failure "露出を、トーンマップの後で掛けて、明るさ調整が効かない"
    **露出はトーンマップの前**（HDR 値に掛ける）。

??? failure "自動露出が、画面の明るい点（太陽）に引きずられて、シーンが暗くなる"
    **対数平均・ヒストグラム（外れ値除外）・中心重み**を使う。

??? failure "自動露出を、フレームごとに急に変えて、ちらつく"
    **指数的な追従**で**時間をかけて**変える。

??? failure "ブルームを、トーンマップの後に、LDR で掛けて、明るい光がにじまない"
    **ブルームは、HDR（リニア）で**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>露出（EV）</strong> ＝ <strong>光の量への倍率</strong>。<strong>EV 1 つで 2 倍</strong>。<strong>トーンマップの前</strong>に掛ける
    - [x] <strong>トーンマップ ＝ HDR → 0〜1 の単調曲線</strong>。<strong>S 字（フィルミック・ACES・AgX）</strong>が<strong>自然</strong>
    - [x] <strong>Reinhard</strong> は<strong>簡単</strong>だが<strong>低コントラスト</strong>。<strong>色相の保ち方</strong>で<strong>見た目が変わる</strong>
    - [x] <strong>自動露出</strong> ＝ <strong>対数平均（ヒストグラム）→ 目標露出 → 指数的に追従</strong>
    - [x] <strong>ガンマ（sRGB）変換は最後</strong>。<strong>HDR ディスプレイは、別のトーンマップ</strong>

## 参考

- Reinhard et al., "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）
- Hable, "Filmic Tonemapping Operators"（GDC 2010）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering"（SIGGRAPH 2014、EV100 露出）
- Narkowicz, "ACES Filmic Tone Mapping Curve"（2016）

## 関連ページ

- [ポストプロセス](index.md)
- [ブルーム](bloom.md)
- [カラー グレーディング](color-grading.md)
- [PBR](../../3d/pbr.md)
