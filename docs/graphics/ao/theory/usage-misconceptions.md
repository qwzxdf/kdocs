---
title: Usage and Misconceptions of AO
tags:
  - 描画
---

# Usage and Misconceptions of AO

<strong>AO は間接光の「拡散」を暗くするもの</strong>で、直接光には掛けません。これを間違えると画面が不自然に暗くなります。このページでは AO の正しい適用先・スペキュラ遮蔽・よくある誤解を説明します。

!!! tip "ポイント"
    - AO は環境光（間接拡散）に掛ける。直接光には掛けない。
    - スペキュラの環境光にはスペキュラ遮蔽（別の式）。
    - AO を全体に掛けて、画面を暗くするのは誤用。
    - よくある誤解：AO ＝ 影・AO ＝ 常に暗くなるもの。

!!! info "このページを読む前に"
    - [AO Theory](index.md)（このセクション全体の地図と、読む順番）

## AO の使い方

### 掛ける相手：間接光の拡散項だけ

AO は「環境光（空や周囲から来る間接光）が周囲の物にどれだけ遮られるか」を表します。ライト 1 つ 1 つの向きや位置は考えていない量です。そのため、太陽やスポットライトのような<strong>直接光に掛けてはいけません</strong>。直接光の遮蔽はシャドウ マップなどでライトごとに求めるべきものです。直接光に AO を掛けてしまうとライトが当たっている日向の隅まで暗くなり、絵が不自然に汚れます。

```hlsl
float3 ambient = irradiance * albedo * ao;
float3 color = direct_light + ambient;
```

### スペキュラの環境光

IBL（環境マップ）を使うと環境光は拡散項と鏡面項に分かれます。拡散項には AO をそのまま掛けます。鏡面項（映り込み）に同じ AO を掛けるのは正しくありません。鏡面反射は視線の方向と粗さで決まる狭い方向の光だけを拾うので、拡散用の AO では暗さの程度が合いません。鏡面項には視線方向と粗さを考えたスペキュラ遮蔽という別の式を使います（[GTAO](../gtao.md)）。

### 焼いた AO との併用

メッシュに焼き込んだ AO テクスチャは、マイクロ AO（細かいくぼみ・ひび）の役を担います。スクリーン空間 AO は物体どうしの接触（壁と箱の間など）という マクロ AO の役を担います。両者は役割が違うので掛け合わせて併用します。同じ領域を二重に暗くしすぎないようスクリーン空間の半径は、焼き込みで扱う細かさより大きくしておきます。

### リニア空間で掛ける

AO はリニアな光の量に対する係数です。ガンマ空間（sRGB の色のまま）で掛けると、暗部が潰れて見た目が変わります。ライティングの計算が終わるまで、リニア空間のまま処理します（[色の数学](../../../gamemath/color.md)）。

### 強さの調整

`pow(AO, 指数)` で調整します。指数を大きくすると暗い所がより濃くなって、コントラストが上がります。強くしすぎると画面全体が汚れて見えるので、見た目をアーティストが調整できるようパラメータを公開しておくとよいでしょう。

## 適用のコード

AO は <strong>間接光（環境光）にだけ</strong>掛けます。ライティングのパスで環境光の項に AO を掛けます。

```hlsl
Texture2D<float> g_ao : register(t5);                          // AO（ぼかし・アップサンプル済み）

// GTAO のマルチ バウンス近似: 明るい色の面ほど、隅で、光が回り込むので、AO を弱める（Jimenez 2016）。
float3 MultiBounceAO(float ao, float3 albedo) {
  float3 a = 2.0404 * albedo - 0.3324;
  float3 b = -4.7951 * albedo + 0.6417;
  float3 c = 2.7552 * albedo + 0.6903;
  return max(ao, ((ao * a + b) * ao + c) * ao);               // ao 自身より、暗くならない
}

// スペキュラ遮蔽: 拡散の AO を鏡面反射の、遮蔽に変換する（Lagarde と de Rousiers、2014）。
float SpecularOcclusion(float n_dot_v, float ao, float roughness) {
  return saturate(pow(n_dot_v + ao, exp2(-16.0 * roughness - 1.0)) - 1.0 + ao);
}

float3 AmbientLighting(float3 albedo, float3 f0, float roughness, float n_dot_v, float2 uv,
                       float3 diffuse_irradiance, float3 specular_ibl) {
  float ao = g_ao.SampleLevel(g_linear_clamp, uv, 0);
  float3 diffuse = diffuse_irradiance * albedo * MultiBounceAO(ao, albedo);   // 拡散の環境光に掛ける
  float3 specular = specular_ibl * SpecularOcclusion(n_dot_v, ao, roughness); // 鏡面の環境光には、変換して掛ける
  return diffuse + specular;
}
// 直接光（太陽、ライト）には、AO を掛けない。直接光の影は、シャドウ マップが受け持つ。
```

数行ずつ見ると 拡散の環境光にはアルベドで、補正した `MultiBounceAO` を 鏡面の環境光には、粗さと視線の角度で変換した `SpecularOcclusion` を掛けています。同じ `ao` をそのまま全部に掛けないのがコツです。

| 掛ける相手 | 掛けるもの | 理由 |
| --- | --- | --- |
| 拡散の環境光 | `MultiBounceAO(ao, albedo)` | 明るい面は隅で、光が回り込む。素の AO は暗すぎる |
| 鏡面の環境光 | `SpecularOcclusion(...)` | 鏡面は、反射方向の狭い範囲だけが効く。粗いほど AO に近くつるつるなら効きにくい |
| 直接光 | 掛けない | 直接光の影は、シャドウ マップが担当。二重に暗くなる |
| エミッシブ | 掛けない | 自分で光る物は、遮られない |

## 画面に出して確認する

AO が正しく掛かっているかは <strong>AO だけ</strong>、ライティング済みの画面、AO を掛けない画面をキーで、切り替えて見ます。

```hlsl
// デバッグ表示: 切り替えで、AO だけを白黒で出す。
if (g_debug_mode == kDebugAoOnly) return float4(ao.xxx, 1.0);
if (g_debug_mode == kDebugNoAo) return float4(AmbientLightingWithoutAo(...) + direct, 1.0);
```

隅と接地面が 自然に暗く、日向や大きな面が 暗くなっていないことそして、AO の効きが動いてもちらつかないことを確認します。

## よくある誤解
??? failure "AO はライトの影の代わりになる"
    AO は<strong>ライトを考慮しない</strong>ので、影の向きを表せません。接地感を出すだけで光源の方向による影は、シャドウ マップなどで別に作ります。

??? failure "AO をシーン全体に掛けて、明るい場所まで暗くなる"
    間接光だけに掛けます。直接光に掛けると日向まで暗くなります。

??? failure "半径を大きくして、広い範囲の陰影を出そうとする"
    半径に比例してサンプルの取りこぼしとコストが増えます。大きな陰影は間接光の方式（[GI](../../index.md)）やライトマップの役目です。

## よくあるミス

??? failure "直接光（太陽）に AO を掛けて、日向が暗い"
    <strong>AO は環境光だけ</strong>に掛ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] AO は間接拡散にだけ掛ける
    - [x] スペキュラにはスペキュラ遮蔽

## 参考

- Landis, "Production-Ready Global Illumination", SIGGRAPH 2002 Course 16（ambient occlusion の、映画制作での使われ方）
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（スペキュラ オクルージョン）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）

## 関連ページ

- [AO Theory](index.md)
- [AO Artifacts](../artifacts/index.md)
- [PBR](../../../3d/pbr.md)
