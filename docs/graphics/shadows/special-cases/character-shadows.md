---
title: Character Shadows and Color
tags:
  - 描画
---

# Character Shadows and Color

**キャラクターの影は、ゲームで最も目立ちます**。**顔に変な影が出たり、髪や肌の影が汚くなる**と、**絵が崩れます**。**キャラクター専用の影の設定（専用のバイアス・専用のライト・影の色と濃さの調整）**で**品質を上げます**。このページでは、**キャラクターの影の注意点・髪や肌の影・影の色と濃さの調整**を説明します。

!!! tip "ポイント"
    - **キャラクターは、専用のバイアス・解像度**にして、**影を綺麗に**する。
    - **顔の影は、目立つので、法線オフセットや専用ライト**で**制御**する。
    - **髪・肌**は**光が透ける（散乱）**ので、**影の色を、少し暖かく・薄く**する。
    - **影の色と濃さ**：**真っ黒でなく、環境光の色を残す**。

## キャラクターの影
**キャラクター**は、**画面の主役**で**影の品質**が**目立ち**ます。**専用の工夫**がよく使われます。

キャラクターの影の工夫は 4 つあります。<strong>専用のシャドウ マップ</strong>は、キャラクターだけを高解像度のシャドウ マップに描く方法で、カスケードとは別に持ち、顔や手の細部まで鋭くできます。<strong>カプセル シャドウ</strong>は、骨にカプセル（線分と半径）を割り当てて、解析的な柔らかい影を作る方法で、変形するキャラクターにも安く使えます（[Distance Field Shadows](../sdf-shadows.md)）。<strong>コンタクト シャドウ</strong>は、足元や細部の接触を補います（[Contact Shadows](../contact-shadows.md)）。<strong>フェイク ライト</strong>は、キャラクター用に専用のライトを置き、リム ライトや影の向きを演出的に調整する方法です。

### 髪・肌の影

**髪**は**細い**ので**シャドウ マップ**では**ほぼ点**になります。**髪専用の深いシャドウ（Deep Opacity Maps）・近似的な、半透明の影**が使われます（[Hair Shadows](../../skin-hair/hair/shadows.md) と [Skin and Hair](../../skin-hair/index.md) を参照）。

## 影の色・濃さの調整
影の色と濃さの調整です。影の色は、真っ黒でなく、環境光の色（空の青）に寄せます。間接光が影の中にも届くからです。影の濃さは、0〜1 の係数で調整し（`lerp(1, shadow, strength)`）、シーンの雰囲気に合わせます。AO と併用すれば、シャドウ マップが覆えない細かい隙間の暗さを補えます（[AO](../../ao/index.md)）。

```hlsl
float3 direct = sun_color * n_dot_l * shadow;
float3 ambient = sky_ambient * ao;
float3 lit = direct + ambient;
```

**影の中も環境光で少し明るい**ので**影を完全な黒にしない**ことが、**自然な見た目**の基本です。

## よくあるミス

??? failure "顔に、鼻や顎の汚い影が出る"
    **顔の専用バイアス**・**専用ライト**・**影の濃さを下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **キャラクターは、専用の影の設定を持つ**
    - [x] **影の色と濃さを調整**して**真っ黒にしない**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Special Cases](index.md)
- [Shadow Bias](../bias/index.md)
- [Cel Shading](../../postprocess/stylized/cel-shading.md)
