---
title: ホワイト バランス
tags:
  - 描画
---

# ホワイト バランス

**同じ白い紙でも晴天の下では青白く、白熱灯の下では黄色く見えます**。**人間の目はこれを自動で補正して、「白い紙は白い」と感じます**（**色の恒常性**）。**カメラはこの補正を「ホワイト バランス」で行い**、**ゲームでも画面全体の色温度を調整して、「暖かい夕暮れ」や「冷たい夜」を作る**ために**使います**。このページでは、**色温度（ケルビン）と色合い・光源の色を打ち消す考え方・簡易実装（LMS 空間）・ゲームでの使い方・注意点**を説明します。

!!! tip "ポイント"
    - ホワイト バランス ＝ <strong>光源の色を打ち消して、白を白く見せる</strong>。<strong>全体の色味を暖色〜寒色にずらす</strong>。
    - <strong>色温度（K）</strong>：<strong>低い（約 2000 K）は橙、高い（約 10000 K）は青</strong>。<strong>6500 K 前後が日中の昼光（D65）</strong>。
    - <strong>色合い（Tint）</strong>：<strong>緑〜マゼンタの軸</strong>。
    - <strong>実装</strong>：<strong>LMS（錐体）空間で白点の比率で割る</strong>のが<strong>標準的</strong>。
    - <strong>ゲームでは「補正」ではなく、「演出」に使う</strong>こと<strong>が多い</strong>。
    - <strong>トーンマップの前（リニア）で行う</strong>と<strong>自然</strong>。

## 色温度と見た目

**物体を熱すると温度に応じた色で光ります**（**黒体放射**）。<strong>この温度（ケルビン）が「色温度」</strong>で、**光源の色を表す**のに**使われます**。

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="色温度">
<text x="20" y="26" class="fig-title">色温度：低いほど橙（暖色）、高いほど青（寒色）</text>
<defs><linearGradient id="wb-g" x1="0" x2="1"><stop offset="0" stop-color="#ff7a1a"/><stop offset="0.25" stop-color="#ffb35c"/><stop offset="0.5" stop-color="#fff4e6"/><stop offset="0.72" stop-color="#e9f1ff"/><stop offset="1" stop-color="#9ec3ff"/></linearGradient></defs>
<rect x="40" y="56" width="700" height="40" fill="url(#wb-g)" stroke="#94a3b8"/>
<g font-size="12" text-anchor="middle"><text x="60" y="116">1900 K</text><text x="60" y="134" style="font-size:11px">ろうそく</text>
<text x="210" y="116">2700 K</text><text x="210" y="134" style="font-size:11px">白熱電球</text>
<text x="390" y="116">5000 K</text><text x="390" y="134" style="font-size:11px">昼白色</text>
<text x="540" y="116">6500 K</text><text x="540" y="134" style="font-size:11px">昼光（D65）</text>
<text x="720" y="116">10000 K</text><text x="720" y="134" style="font-size:11px">青空の日陰</text></g>
</svg>

| 光源 | 色温度 |
| --- | --- |
| **ろうそくの炎** | **約 1900 K**（**橙**） |
| **白熱電球** | **約 2700 K**（**暖かい黄色**） |
| **朝・夕方の日光** | **約 3500〜4500 K** |
| **正午の日光** | **約 5500〜6500 K**（**ほぼ白**） |
| **曇り・日陰** | **約 7000〜10000 K**（**青白い**） |

## 白を白に戻す考え方

**光源が橙（低い色温度）のとき、白い物は橙に映ります**。<strong>その橙を打ち消す（青を足す・橙を減らす）</strong>と、**白が白に戻ります**。**これがホワイト バランスの補正**です。

| 操作 | 結果 |
| --- | --- |
| **光源の色温度を指定** | **その光源の色が白になる**ように補正（**画面全体が逆の色へ**） |
| <strong>ホワイト バランスの温度を「上げる」</strong> | <strong>画面が暖かく（橙）</strong>なる（**青い光源を想定して、補正しすぎ**） |
| <strong>「下げる」</strong> | <strong>画面が青く（寒色）</strong>なる |

<strong>ゲームでは、「補正」というより、画面の色味を作る「演出」</strong>として**使います**。**温度を上げて暖かく・下げて冷たく**調整します。

## 実装（LMS 空間）

**人間の錐体（L・M・S）の反応**を**表す LMS 空間**で、**光源の白点を基準の白に合わせる**のが**標準的**です。

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

| 点 | 説明 |
| --- | --- |
| **`temperature`・`tint`** | **−1〜+1 のつまみ**（<strong>色温度（暖〜寒）と、色合い（緑〜マゼンタ）</strong>） |
| **`x, y`** | **色度座標**。**D65 の白（0.31271, 0.32902）を基準にずらす** |
| **`white_lms / lms`** | <strong>光源の LMS で割る比率（ゲイン）</strong> |
| **`kRgbToLms` など** | **色空間変換の 3×3 行列**（**公開されている値**） |

**もっと簡単な近似**は、**RGB にゲインを掛けるだけ**です。

```hlsl
float3 SimpleWhiteBalance(float3 color, float temperature) {
  float3 warm = float3(1.0, 0.9, 0.75);
  float3 cool = float3(0.8, 0.9, 1.0);
  float3 gain = lerp(warm, cool, saturate(0.5 - temperature * 0.5));
  return color * gain;
}
```

| 方式 | 精度 | 手軽さ |
| --- | --- | --- |
| <strong>LMS 空間（本格）</strong> | **高い** | **行列を使う** |
| <strong>RGB ゲイン（簡易）</strong> | <strong>粗い（明るさが変わる）</strong> | **1 行** |

## 色合い（Tint）

**色温度が「橙〜青」の軸**だとすると**色合いは「緑〜マゼンタ」の軸**です。**蛍光灯の緑かぶり**を**打ち消したり**、**ファンタジーな色味**を**作るのに使います**。

| つまみ | 軸 |
| --- | --- |
| <strong>温度（Temperature）</strong> | **橙 ⇔ 青** |
| <strong>色合い（Tint）</strong> | **緑 ⇔ マゼンタ** |

## ゲームでの使い方

| 使い方 | 内容 |
| --- | --- |
| **時間帯の演出** | **朝：暖かく、昼：中立、夕方：橙、夜：青** |
| **場所の演出** | **洞窟：冷たい青、火山：暖かい橙** |
| **状態の演出** | **体力が低い：色が冷える・彩度が下がる** |
| **光源との整合** | **画面の主光源の色とホワイト バランスで調和させる** |

**時間帯の変化**に**合わせて、色温度を補間**すると**自然な移り変わり**になります（[空と大気](../../atmosphere/sky-models.md)）。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **リニア空間でトーンマップの前** | **物理的に自然**（**HDR の値で比率を保つ**） |
| **LMS（錐体）空間で** | **より自然な補正** |
| **LUT に焼く** | **ほかの調整と一緒に 1 つに**（[3D LUT](lut-3d.md)） |
| **ボリュームで補間** | **場所ごとに温度を変えて、境で滑らかに** |
| **ライトの色と合わせる** | **光源の色（ライト）と、ホワイト バランスで二重に偏らない** |

## よくあるミス

??? failure "ホワイト バランスと、ライトの色の両方を動かして、色かぶりが強すぎる"
    **ライトの色と全体のホワイト バランスの役割を分ける**（**光源は物理的に全体の色味は演出**）。

??? failure "RGB ゲインで調整したら、全体の明るさも変わった"
    **LMS で輝度を保つ**、または**簡易版の後に輝度を補正**する。

??? failure "ガンマ空間でホワイト バランスして、色が不自然"
    **リニア空間**で行う。

??? failure "場所の切り替えで、色温度が急に変わる"
    **ボリュームで補間**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ホワイト バランス ＝ <strong>光源の色を打ち消して、全体の色味をずらす</strong>
    - [x] <strong>色温度（K）</strong>：<strong>低い ＝ 橙、高い ＝ 青</strong>。<strong>色合い</strong>は<strong>緑〜マゼンタ</strong>
    - [x] <strong>LMS 空間で、白点の比で割る</strong>のが<strong>本格的</strong>。<strong>RGB ゲインは簡易</strong>
    - [x] <strong>ゲームでは「演出」</strong>に使う（<strong>時間帯・場所・状態</strong>）
    - [x] <strong>リニア・トーンマップの前</strong>で行う

## 参考

- CIE, "Colorimetry"（色度図・色温度）
- Selan, "Cinematic Color: From Your Monitor to the Big Screen"（SIGGRAPH 2012）
- Bruce Lindbloom, "RGB/XYZ Matrices"

## 関連ページ

- [カラー グレーディング](index.md)
- [基本の調整](basic-adjustments.md)
- [リフト・ガンマ・ゲイン](lift-gamma-gain.md)
- [空のモデル](../../atmosphere/sky-models.md)
