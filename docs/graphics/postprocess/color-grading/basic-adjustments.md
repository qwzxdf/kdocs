---
title: 基本の調整
tags:
  - 描画
---

# 基本の調整

**カラー グレーディングの土台**は、**露出・コントラスト・彩度・色相**という**4 つの基本操作**です。<strong>それぞれが「画素の色を変える関数」</strong>で、**組み合わせれば、ほとんどのルックを作れます**。このページでは、**各操作の式と効き方・どの空間で行うか（リニアか、ガンマか）・ピボットの選び方・彩度の注意点・調整の順序**を説明します。

!!! tip "ポイント"
    - <strong>露出</strong>：<strong>全体に倍率</strong>（<strong>2^EV</strong>）。
    - <strong>コントラスト</strong>：<strong>ピボット（中間灰）を中心に広げる・縮める</strong>。
    - <strong>彩度</strong>：<strong>輝度（モノクロ）と元の色を補間</strong>。<strong>0 でモノクロ、1 で元、1 超で鮮やか</strong>。
    - <strong>色相</strong>：<strong>色相環上で回す</strong>。
    - <strong>計算する空間</strong>：<strong>リニアで行うか、見た目に近いガンマ（または対数）で行うか</strong>で<strong>効き方が変わる</strong>。
    - <strong>順序で結果が変わる</strong>（<strong>非可換</strong>）。<strong>一定の順序を決める</strong>。

## 4 つの基本操作

| 操作 | 内容 | 式 |
| --- | --- | --- |
| **露出** | **全体の明るさ** | **色 × 2^EV** |
| **コントラスト** | **明暗の差** | <strong>(色 − ピボット) × 係数 + ピボット</strong> |
| **彩度** | **鮮やかさ** | <strong>lerp(輝度, 色, 彩度)</strong> |
| **色相** | **色の種類** | **色相環で回転** |

## コントラスト

**ピボット（中心）より明るい部分はより明るく、暗い部分はより暗く**します。

<div class="formula">c' = (c − pivot) × contrast + pivot</div>

```hlsl
float3 ApplyContrast(float3 color, float contrast, float pivot) {
  return (color - pivot) * contrast + pivot;
}
```

| 点 | 説明 |
| --- | --- |
| **`contrast > 1`** | **コントラストが強くなる**（メリハリ） |
| **`contrast < 1`** | **弱くなる**（眠い・フラット） |
| **`pivot`** | **変わらない点**。**リニアなら約 0.18（中間灰）、ガンマ空間なら約 0.5** |

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="コントラスト">
<text x="20" y="26" class="fig-title">コントラスト：ピボットを中心に、傾きを変える</text>
<line x1="80" y1="200" x2="420" y2="200" stroke="currentColor" stroke-opacity="0.5"/><line x1="80" y1="50" x2="80" y2="200" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4" points="80,200 420,50"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="80,200 150,196 250,125 350,64 420,56"/>
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="80,180 250,125 420,70"/>
<circle cx="250" cy="125" r="5" fill="#1f2937"/><text x="258" y="146" style="font-size:12px">ピボット</text>
<text x="440" y="90" style="font-size:12px;fill:#e5484d">赤：コントラスト強（S 字）</text>
<text x="440" y="116" style="font-size:12px;fill:#2563eb">青：コントラスト弱</text>
<text x="440" y="142" style="font-size:12px;fill:#64748b">灰色の点線：変化なし</text>
</svg>

**線形のコントラスト**は、**0〜1 の外にはみ出す**ことがあるので、<strong>S 字（シグモイド）</strong>や**クランプ**で**抑える**ことが**あります**。

## 彩度

```hlsl
float3 ApplySaturation(float3 color, float saturation) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  return lerp(float3(luma, luma, luma), color, saturation);
}
```

| `saturation` | 見た目 |
| --- | --- |
| **0** | **モノクロ** |
| **1** | **そのまま** |
| **> 1** | **鮮やか**（**1.2〜1.5 がよく使われる**） |

**注意**：**彩度を上げすぎるとすでに鮮やかな色が範囲外（> 1）に出たり、色が不自然**になります。<strong>「鮮やかな色ほど効きにくい」振る舞い（バイブランス）</strong>にすると**自然**です。

```hlsl
float3 ApplyVibrance(float3 color, float vibrance) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float max_c = max(color.r, max(color.g, color.b));
  float min_c = min(color.r, min(color.g, color.b));
  float current_saturation = max_c - min_c;
  float amount = vibrance * (1.0 - current_saturation);
  return lerp(float3(luma, luma, luma), color, 1.0 + amount);
}
```

| 方式 | 内容 |
| --- | --- |
| <strong>彩度（Saturation）</strong> | **全体を同じ割合で** |
| <strong>バイブランス（Vibrance）</strong> | **もともと地味な色をより強く鮮やかに**（**肌の色などを不自然にしない**） |

## 色相

**色相環（色の輪）の上で色を回転**させます。**RGB を直接回すより、色相・彩度・明度（HSV）や YCoCg に変換して回す**のが**一般的**です。

```hlsl
float3 RotateHue(float3 color, float angle_radians) {
  float c = cos(angle_radians);
  float s = sin(angle_radians);
  float3x3 m = {
    0.299 + 0.701 * c + 0.168 * s, 0.587 - 0.587 * c + 0.330 * s, 0.114 - 0.114 * c - 0.497 * s,
    0.299 - 0.299 * c - 0.328 * s, 0.587 + 0.413 * c + 0.035 * s, 0.114 - 0.114 * c + 0.292 * s,
    0.299 - 0.300 * c + 1.250 * s, 0.587 - 0.588 * c - 1.050 * s, 0.114 + 0.886 * c - 0.203 * s
  };
  return mul(m, color);
}
```

**色相の回転**は**ゲームでは特殊効果（毒・凍結・サイケデリック）や、全体の色味の調整**に**使われます**。

## 計算する空間

| 空間 | 特徴 |
| --- | --- |
| <strong>リニア（光の量）</strong> | **物理的に正しい**。**コントラストの効きが暗部に弱く、明部に強い** |
| <strong>ガンマ（sRGB）</strong> | **見た目に近い**。**画像編集ソフトの感覚と合う** |
| <strong>対数（Log）</strong> | **広いダイナミック レンジを、均等に扱える**。**映画のグレーディングで標準** |

**アーティストが写真編集ソフトの感覚で調整できる**ように、**ガンマ空間か、対数空間で調整**する**のが一般的**です（[3D LUT](lut-3d.md)）。

## 調整の順序

**これらの調整は、順序を入れ替えると結果が変わります**（**非可換**）。**ゲーム（エンジン）で順序を決めて固定**します。

| 順序の例 | 内容 |
| --- | --- |
| **① 露出** | **全体の明るさ** |
| **② ホワイト バランス** | **光源の色を打ち消す** |
| **③ リフト/ガンマ/ゲイン** | **暗部・中間・明部** |
| **④ コントラスト** | **ピボット中心で** |
| **⑤ 彩度** | **最後に鮮やかさ** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **LUT に焼く** | **すべての調整を、1 つの 3D LUT に**（[3D LUT](lut-3d.md)） |
| **ガンマ・対数空間で調整** | **見た目に近い感覚で** |
| **バイブランスを併用** | **鮮やかになりすぎない** |
| **範囲外をクランプ** | **0〜1 に収める** |
| **順序を固定** | **結果を再現できる** |
| **パラメータをボリュームで管理** | **場所ごとに補間**（[LUT の作り方](lut-authoring.md)） |

## よくあるミス

??? failure "コントラストを強くしたら、暗部が真っ黒、明部が真っ白"
    <strong>S 字（シグモイド）</strong>にする、**ピボットを正しく**、**適度に**。

??? failure "彩度を上げたら、色が派手すぎて不自然"
    **バイブランス**にする、**上げ幅を抑える**。

??? failure "リニア空間でコントラストを掛けて、見た目が思ったのと違う"
    **ピボットを 0.18**にする、または**ガンマ・対数空間で調整**。

??? failure "調整の順序を変えて、ルックが変わった"
    **順序を固定**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基本は<strong>露出・コントラスト・彩度・色相</strong>
    - [x] <strong>コントラスト</strong> ＝ <strong>ピボットを中心に傾きを変える</strong>。<strong>彩度</strong> ＝ <strong>輝度と元の色の補間</strong>
    - [x] <strong>バイブランス</strong>で<strong>鮮やかな色を、増やしすぎない</strong>
    - [x] <strong>リニア・ガンマ・対数</strong>で<strong>効き方が違う</strong>。<strong>ピボットを合わせる</strong>
    - [x] <strong>順序を固定</strong>。<strong>LUT に焼く</strong>

## 参考

- Hable, "Color Grading with Look-Up Tables"（解説）
- Colourist Guide, "Color Grading Fundamentals"
- Selan, "Cinematic Color: From Your Monitor to the Big Screen"（SIGGRAPH 2012）

## 関連ページ

- [カラー グレーディング](index.md)
- [リフト・ガンマ・ゲイン](lift-gamma-gain.md)
- [3D LUT](lut-3d.md)
- [露出](../tonemapping/exposure.md)
