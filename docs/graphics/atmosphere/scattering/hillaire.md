---
title: Hillaire 2020: Four LUTs
tags:
  - 描画
---

# Hillaire 2020: Four LUTs

**Hillaire の手法は、4 つの小さな LUT（透過率・多重散乱・空の景色・空気遠近法）に分けて計算する**ことで、**動的な大気**を**リアルタイム**で扱えます。**パラメータを変えても、すぐに反映**されます。このページでは、**4 つの LUT**を説明します。

!!! tip "ポイント"
    - **透過率 LUT**：高さと角度から、透過率。
    - **多重散乱 LUT**：多重散乱の近似。
    - **スカイビュー LUT**：視線の方向ごとの空の色。
    - **空気遠近法 LUT**：カメラからの距離ごとの散乱。
    - **動的に更新できる**（時刻・天候）。

## Hillaire 2020：4 つの LUT
<strong>Hillaire（2020, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"）</strong>は、**軽い LUT を毎フレーム更新する**方式です。**大気の組成（霧の濃さ・時間帯）を動的に変えられる**のが**強み**で、**Unreal Engine の SkyAtmosphere**などに**使われています**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="Hillaire の 4 つの LUT">
<text x="20" y="24" class="fig-title">Hillaire 2020：4 つの LUT</text>
<rect x="30" y="60" width="160" height="70" rx="6" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5"/>
<text x="110" y="88" text-anchor="middle" style="font-size:13px">透過率 LUT</text><text x="110" y="108" text-anchor="middle" style="font-size:11px">256×64（2D）</text>
<rect x="210" y="60" width="160" height="70" rx="6" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043"/>
<text x="290" y="88" text-anchor="middle" style="font-size:13px">多重散乱 LUT</text><text x="290" y="108" text-anchor="middle" style="font-size:11px">32×32（2D）</text>
<rect x="390" y="60" width="160" height="70" rx="6" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28"/>
<text x="470" y="88" text-anchor="middle" style="font-size:13px">スカイビュー LUT</text><text x="470" y="108" text-anchor="middle" style="font-size:11px">192×108（2D）</text>
<rect x="570" y="60" width="180" height="70" rx="6" fill="#e5484d" fill-opacity="0.2" stroke="#e5484d"/>
<text x="660" y="88" text-anchor="middle" style="font-size:13px">空気遠近法 LUT</text><text x="660" y="108" text-anchor="middle" style="font-size:11px">32×32×32（3D）</text>
<text x="110" y="160" text-anchor="middle" style="font-size:11px">高さ × 太陽角 →</text><text x="110" y="176" text-anchor="middle" style="font-size:11px">太陽までの透過率</text>
<text x="290" y="160" text-anchor="middle" style="font-size:11px">高さ × 太陽角 →</text><text x="290" y="176" text-anchor="middle" style="font-size:11px">多重散乱の寄与</text>
<text x="470" y="160" text-anchor="middle" style="font-size:11px">視線の向き →</text><text x="470" y="176" text-anchor="middle" style="font-size:11px">空の色（全天）</text>
<text x="660" y="160" text-anchor="middle" style="font-size:11px">カメラ前方の froxel →</text><text x="660" y="176" text-anchor="middle" style="font-size:11px">散乱光と透過率</text>
<text x="390" y="230" text-anchor="middle" style="font-size:13px">毎フレーム、順に更新：透過率 → 多重散乱 → スカイビュー → 空気遠近法</text>
</svg>

4 つの LUT は、それぞれ役割が違います。<strong>透過率 LUT</strong>は、高さと太陽の天頂角から、大気の外までの透過率を引く表で、ほぼ固定で、大気の組成が変わると更新します。<strong>多重散乱 LUT</strong>は、高さと太陽の天頂角から、多重散乱の寄与を引く表で、近似です。<strong>スカイビュー LUT</strong>は、カメラ位置での全方向の空の色で、緯度経度で圧縮し、地平線付近を細かく取ります。<strong>空気遠近法 LUT</strong>は、カメラ前方の froxel（視錐台の 3D 格子）ごとの散乱光と透過率で、物体への霞に使います（[Aerial Perspective and Fog](../aerial-fog/index.md)）。

### スカイビュー LUT の工夫

**空の色は地平線付近で急に変わります**。**天頂角をそのまま格子にすると、地平線の解像度が足りません**。**非線形な割り当て**で**地平線付近を細かく取ります**。

```hlsl
float SkyViewV(float view_zenith_cos, float horizon_cos) {
  float v;
  if (view_zenith_cos > horizon_cos) {
    float t = (view_zenith_cos - horizon_cos) / (1.0 - horizon_cos);
    v = 0.5 + 0.5 * sqrt(t);
  } else {
    float t = (horizon_cos - view_zenith_cos) / (horizon_cos + 1.0);
    v = 0.5 - 0.5 * sqrt(t);
  }
  return v;
}
```

**平方根で割り当てる**ことで、**地平線の周り（v = 0.5）が細かく**なります。

### 実行時の流れ

実行時の流れは 4 段階です。最初に、透過率・多重散乱・スカイビュー・空気遠近法の LUT を、コンピュート シェーダーで更新します。次に、空を描くときは、ピクセルの視線からスカイビュー LUT を 1 回引くだけです。太陽の円盤は、透過率 LUT で減衰させて足します。最後に、物体には、空気遠近法 LUT で色を霞ませます（[Aerial Perspective and Fog](../aerial-fog/index.md)）。

原典は、Hillaire の "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（Eurographics Symposium on Rendering 2020）です。この方式の特長は、Bruneton の 4D テーブルを、毎フレーム更新できる小さな LUT に分解したことです。LUT が小さいので、大気の組成（ミーの密度、オゾンの量）をリアルタイムに変えて、天候の変化も表現できます。モバイルから高性能 PC まで、LUT の解像度を変えるだけで対応でき、Unreal Engine の Sky Atmosphere などに採用されています。

**LUT は小さい**ので<strong>毎フレーム更新しても軽く（0.1〜0.3 ms 程度）</strong>、**時刻・天気・大気の濃さを動的に変えられます**。

## よくあるミス

??? failure "LUT の解像度が低く、空にバンディング"
    **解像度を上げる**・**非線形のマッピング**を**使う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **4 つの小さな LUT で、動的な大気**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Multiple Scattering](multiple-scattering.md)
- [空気遠近法](../aerial-fog/index.md)
