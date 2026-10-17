---
title: 屈折
tags:
  - 描画
---

# 屈折

**ガラスや水を通して見ると、後ろの景色が曲がって見えます**。**これが屈折**で、**ゲームでは「画面空間の屈折」で、安く近似**します。このセクションでは、**原理・画面空間の屈折・境界の問題・フレネル・厚みと色・色収差・薄いガラスと厚いガラス・実装の全体像**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **屈折 ＝ 光が、物質の境界で曲がる現象**（スネルの法則）。
    - **ゲームでは、既に描いた画面を、ずらして読むだけで近似**。
    - **フレネル（見る角度による反射の強さ）**も**組み合わせる**。
    - **厚み・色（吸収）・色収差**で、**リアルさが増す**。

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

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [画面空間の屈折](screen-space.md) | 法線で画面をずらす |
| [境界の問題](boundary.md) | 屈折の先に、手前の物が混ざる問題 |
| [フレネル](fresnel.md) | 反射と屈折の割合 |
| [厚みと色](thickness-color.md) | ビア＝ランバートの法則 |
| [色収差（分散）](dispersion.md) | 色ごとにずらす |
| [薄いガラスと厚いガラス](thin-thick.md) | 窓ガラスと、ガラスの塊 |
| [実装の全体像とコスト](implementation.md) | 手順・限界 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **屈折は、画面をずらして読む近似が基本**
    - [x] **フレネル・厚み・色で、リアルになる**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [半透明](../index.md)
- [水の質感](../../water/shading/index.md)
- [OIT](../oit/index.md)
