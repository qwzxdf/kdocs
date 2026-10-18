---
title: Scattering Color (SSS-Like)
tags:
  - 描画
---

# Scattering Color (SSS-Like)

**波頭などの薄い部分では、光が水の中で散乱して、明るい緑〜水色に透けて見えます**。**これを SSS 風の近似で表せます**。このページでは、**散乱の色の足し方**を説明します。

!!! tip "ポイント"
    - **波頭（高い所）が、明るく透ける**。
    - **光の方向と視線が近い時に、強くなる**。
    - **高さと太陽方向から、近似で計算**する。
    - **入れすぎると、水が発光して見える**。

## 散乱の色（SSS 風）
**波頭に光が透けて、明るい青緑に光って見える**ことがあります（**太陽を背にして波を見たとき**）。**波の高い所ほど、水が薄く、光が通り抜ける**ためです。

```hlsl
float wave_height_factor = saturate(height_offset / max_wave_height);
float sun_behind = pow(saturate(dot(view_dir, -light_dir)), 4.0);
float3 scatter = scatter_color * wave_height_factor * sun_behind * sun_intensity;
```

コードの要点です。波の高さが高い波頂ほど、散乱の寄与が強くなります。太陽が水面の向こう（視線と反対）にあるときにも強く出ます。色は、明るい青緑（例：(0.1, 0.5, 0.45)）です。

### なぜ波頂が透けて光るのか

波頂では水の層が薄く、背後から来た太陽光が水の中を通り抜けて、目に届きます。このとき、水が光を散乱して青緑に光るので、波頂が内側から光っているような透け感が出ます。これを SSS（表面下散乱）風と呼びますが、実際には皮膚や大理石のような本格的な SSS 計算ではなく、「波の高さ」「太陽の向き」「視線」の 3 つから決める、簡易な近似です。

式の形は、`散乱の色 × 波頂の高さ × max(0, dot(視線, 太陽方向)) ^ k × 太陽の強さ` のようになります。dot の項は、太陽が視線の向こう側にあるときに大きくなり、k で広がりを絞ります。この項を、屈折の色に足せば、波が逆光で光る効果が出ます。夕方の海で、波の向こうに太陽があるとき、波の頂が緑色に透けて光るのは、この効果です。

## 水の色は、どこから来るのか

水を通して見える色は、**底から来る光が、減ったもの**と、**水自体から返ってくる光**の、足し算でした（[Color by Water Depth](depth-color.md)）。後者は、**水の中で、光が、散乱**して、目に届く光です。この光が、**水の色**を作っています。

| 現象 | 内容 |
| --- | --- |
| 吸収 | 光が、水に、吸い取られる。赤が先に消える。係数 `a`（1/m） |
| 散乱 | 光が、水の中で、向きを変える。係数 `b`（1/m） |
| 後方散乱 | 散乱のうち、**来た方向へ、戻る**成分。係数 `b_b`。目に届く光の、源 |

海が、**青く見える**のは、赤が吸収され、**青い光が、後方散乱で、返ってくる**ためです。

## 水の色を、計算する

Gordon ら（1975）は、**深い水の、水面から出てくる光の割合**を、吸収と、後方散乱から、次の式で、近似しました。

```text
R ≈ f × b_b / (a + b_b)         f ≈ 0.33
```

`R` は、**入ってきた光の、何割が、水面から、戻ってくるか**を表します（**体積反射率**）。

| 水 | `a`（RGB） | `b_b` | `R`（RGB） |
| --- | --- | --- | --- |
| 澄んだ海 | (0.45, 0.07, 0.03) | 0.005 | (0.004, 0.023, 0.048) |
| 濁った、緑の湖 | (0.8, 0.3, 0.3) | 0.02 | (0.008, 0.021, 0.021) |
| プール（白いタイル） | 底の色が、見える。ここでは、深い水の色の話 | — | — |

`b_b` が、`a` に比べて、小さいので、**R は、小さい値**です。**海は、暗い**のが、普通です。値が、青の成分が、最も大きい（`a` が、青で最小）ことが、**海が、青く見える**理由です。

```hlsl
// 深い水の色（体積反射率）。吸収 a（RGB）と、後方散乱 bb（スカラー）から計算する。
float3 DeepWaterColor(float3 absorption, float backscatter, float3 incident_light) {
  float3 R = 0.33 * backscatter / (absorption + backscatter);
  return incident_light * R;
}
```

`incident_light` は、**水面に降り注ぐ光**（空の光と、太陽光）です。昼と夜、晴れと曇りで、**水の色**も、変わります。

```hlsl
// 水面に降り注ぐ光 = 空の光 + 太陽光。
float3 irradiance = sky_irradiance + sun_color * saturate(sun_dir.y);
float3 water_color = DeepWaterColor(absorption, 0.005, irradiance / 3.14159265);
```

## 波頭が、透けて光る

太陽を背にして、波を見ると、**波頭が、明るい青緑に、光って見える**ことがあります。波頭では、**水の層が薄く**、**背後から、来た太陽光が、水を通り抜けて**、目に届くためです。

**簡単な近似**は、次のとおりです。

```hlsl
// 波頭の透過光（SSS 風）。
float height_factor = saturate((wave_height - sss_height_start) / sss_height_range);   // 高い波頭ほど 1
float sun_behind = pow(saturate(dot(view_dir, -sun_dir)), 4.0);                         // 太陽が、波の向こう側のときだけ
float3 sss = scatter_color * height_factor * sun_behind * sun_intensity;
```

| 要素 | 内容 |
| --- | --- |
| `height_factor` | 波の、**高さ**（または、波の傾きが大きい場所）。**波頭に、近いほど、強い** |
| `sun_behind` | 視線と、太陽の向きが、**逆向き（太陽が、水面の向こう側）**のときだけ、光る |
| `scatter_color` | 青緑の、明るい色（水が、薄い所を、通る光の色） |

波の**頂点の高さ**を、使うので、**波が大きい（荒れた）日ほど、強く**出ます。

!!! warning "入れすぎると、水が、発光する"
    この項は、**足し算**です。強くしすぎると、**水面全体が、ぼんやり光って**見えます。**波頭の、一部だけが、ほんのり光る**くらいに、抑えます。

## 浅瀬の、散乱

浅い場所の、水の色は、**水の散乱の色**と、**底の色**の、混ざったものです。底の色が、白い砂だと、**散乱した光が、明るく、水が、鮮やかな水色**になります。

| 底の色 | 浅い水の見え方 |
| --- | --- |
| 白い砂 | 明るい、水色（南国の海） |
| 暗い岩・泥 | 暗い、濃い色（北の海、沼） |
| 緑の藻 | 緑がかった色 |

**底のテクスチャの色**を、**屈折で、読み**、**水の色と混ぜる**ことで、この違いが、自然に出ます（[Color by Water Depth](depth-color.md)）。

## よくあるミス

??? failure "水がぼんやり光って見える"
    **散乱の強さを抑える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **波頭の透け感を、近似で足す**

## 参考

- Gordon, Brown, Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics, Vol. 14, No. 2, 1975（水中の散乱と吸収から、水の色を求める式）
- Jerlov, "Marine Optics", Elsevier, 1976（海水の水質の分類 Jerlov water types）
- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997（純水の吸収係数の測定値）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes

## 関連ページ

- [Water Shading](index.md)
- [Color by Water Depth](depth-color.md)
