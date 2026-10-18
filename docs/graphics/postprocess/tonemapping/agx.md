---
title: AgX and Others
tags:
  - 描画
---

# AgX and Others

**フィルミックや ACES は、明るく鮮やかな色が白や別の色へ偏る**欠点があります。**近年はこの「色相の破綻」を抑える、新しいトーンマップ**が**増えました**。このページでは、**AgX・Tony McMapface・Khronos PBR Neutral** の**考え方・特徴・使い分け**を説明します。

!!! tip "ポイント"
    - 新しい方式の狙い ＝ <strong>明るい彩度の高い色でも、色相が変わらず、自然に白へ向かう</strong>。
    - <strong>AgX</strong>：<strong>中立寄りのフィルミック</strong>。<strong>広い色域を扱い、Blender の標準</strong>。<strong>パラメータが少なく、使いやすい</strong>。
    - <strong>Tony McMapface</strong>：<strong>3D LUT ベース</strong>。<strong>ブルームとの相性が良い</strong>。
    - <strong>Khronos PBR Neutral</strong>：<strong>商品の色をできるだけ忠実に</strong>（<strong>E コマース向け</strong>）。
    - <strong>選ぶ基準</strong>：<strong>色の再現（忠実）か、映画的な絵（フィルム）か</strong>。
    - <strong>どれも露出の後・ガンマの前</strong>。

## 何が改善されたか

**ACES や Hable では**、**R・G・B に別々に曲線を掛ける**ため、**明るい色の比率が崩れます**（**青い光が紫に赤が黄色に**）。**新しい方式は色空間を工夫したり、LUT で調整したり**して、**これを緩和**します。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="色の偏りの比較">
<text x="20" y="26" class="fig-title">同じ青い強い光を、トーンマップすると</text>
<g font-size="13">
<text x="40" y="62" style="font-weight:700">入力（HDR）</text>
<rect x="40" y="72" width="190" height="40" fill="#2563eb"/><text x="40" y="132" style="font-size:12px">明るさを上げていく →</text>
<text x="280" y="62" style="font-weight:700">ACES 近似</text>
<defs><linearGradient id="ag-aces" x1="0" x2="1"><stop offset="0" stop-color="#1d4ed8"/><stop offset="0.6" stop-color="#8b5cf6"/><stop offset="1" stop-color="#f5e9ff"/></linearGradient>
<linearGradient id="ag-agx" x1="0" x2="1"><stop offset="0" stop-color="#1d4ed8"/><stop offset="0.6" stop-color="#5b8def"/><stop offset="1" stop-color="#eef5ff"/></linearGradient></defs>
<rect x="280" y="72" width="190" height="40" fill="url(#ag-aces)"/><text x="280" y="132" style="font-size:12px">紫がかって白へ</text>
<text x="520" y="62" style="font-weight:700">AgX など</text>
<rect x="520" y="72" width="190" height="40" fill="url(#ag-agx)"/><text x="520" y="132" style="font-size:12px">青のまま白へ</text>
</g>
<text x="40" y="180" style="font-size:13px">色相を保つ方式は、強い光（ネオン・魔法・炎）の色が、意図どおりに見える。</text>
<text x="40" y="204" style="font-size:13px">一方、フィルムのような「ハイライトの色飛び」は弱くなる（好みで選ぶ）。</text>
</svg>

## AgX

**AgX** は、**Troy Sobotka** が設計した、**フィルム風でありつつ色相が安定**するトーンマップです。**Blender 4.0 から標準**になりました。

AgX の特徴は 4 つあります。作業を広い色空間で行い、最後に出力へ変換します。露出の幅（ダイナミック レンジ）を、対数空間で受けて、S 字の曲線で圧縮します。色相を保ちつつ、ハイライトの色飛びが穏やかに白へ向かいます。そして、ルック（見た目）を、後段で選べます（Punchy＝強め、Golden など）。

**実装の流れ**（概略）です。

```hlsl
float3 AgXTonemap(float3 color) {
  color = mul(kAgXInputMatrix, color);
  color = max(color, 1e-10);
  color = clamp(log2(color), kMinEV, kMaxEV);
  color = (color - kMinEV) / (kMaxEV - kMinEV);
  color = AgXContrastCurve(color);
  color = ApplyLook(color);
  color = mul(kAgXOutputMatrix, color);
  return pow(max(color, 0.0), 2.2);
}
```

処理の段階を順に説明します。入力行列で、作業用の広い色空間へ変換します。次に `log2` で EV 単位の範囲にして、最小・最大 EV で正規化します（だいたい −12.5〜+4 EV）。コントラスト曲線として S 字（6 次の多項式など）を掛けます。ルックで彩度やコントラストの好みを調整します。最後に、出力行列とガンマで sRGB へ戻します。

**行列と多項式の係数は、公開されている実装**（Blender の OCIO 設定・各種 HLSL 移植）を**そのまま使う**のが**確実**です。**自分で一から作る必要はありません**。

## Tony McMapface

**Tomasz Stachowiak** による、**3D LUT ベース**の**トーンマップ**です。**あらかじめ作った 48×48×48 の LUT を、表引き**するだけで**使えます**。

Tony McMapface の特徴です。計算が軽く、LUT の 1 回の参照だけで済み、シェーダーが単純です。色相が破綻しにくく、ブルームの白い光や鮮やかなエフェクトが自然に出ます。ブルームのにじみが、色付きの光として自然に出る相性の良さがあります。LUT を自分の画作りのものに差し替えれば、別のルックにもなります。

```hlsl
Texture3D<float3> tony_lut : register(t5);

float3 TonyMcMapface(float3 color) {
  float3 encoded = color / (color + 1.0);
  float3 uvw = encoded * (47.0 / 48.0) + 0.5 / 48.0;
  return tony_lut.SampleLevel(linear_clamp, uvw, 0);
}
```

コードの要点です。`x / (x + 1)` で入力を 0〜1 にして、LUT の入力範囲に収めます（LUT 側の前提です）。半テクセルのずらし（`* (47/48) + 0.5/48`）で、3D LUT の端で補間が正しくなります。`linear_clamp` で、LUT の外に出ないよう端で止めます。

## Khronos PBR Neutral

**Khronos が、E コマース（商品の 3D 表示）向けに作った**、<strong>「色を変えない」</strong>トーンマップです。

Khronos PBR Neutral の特徴です。暗部から中間は曲線を掛けず、ほぼ素通しなので、商品の色が正確です。明部だけ、ある閾値（約 0.8）を超えた部分を滑らかに圧縮します。圧縮するときに、白へ向かう量を調整して色相を保ちます。

**映画的な絵ではなく、「見たままの色」が大切な場面**（**商品・建築・カスタマイズ画面**）に**向きます**。**ゲームでも色の正確さが大事な UI の 3D 表示**に**使えます**。

## 使い分け

4 つの方式の使い分けです。ACES 近似は、強いコントラストの映画的な絵で、色相が偏りますが軽く、映画風の標準です。AgX は、中立寄りのフィルミックで、色相が安定し、コストは中程度、色を壊したくない本格的な画作りに向きます。Tony McMapface は、自然でブルームと好相性、色相が安定し、LUT なので軽く、エフェクトの多いゲームに向きます。PBR Neutral は、ほぼ素通しで忠実、色相もほぼ保たれ、軽く、商品や色の正確さが必要な場面に向きます。

## より良いやり方

より良いやり方を挙げます。ルックはトーンマップの後に分け、AgX の「ルック」やグレーディングを別の LUT にします（[Color Grading](../color-grading/index.md)）。ACES・AgX・Neutral を設定で切り替えられるようにして、ユーザーの好みやステージごとに使い分けます。HDR ディスプレイ用は、SDR の曲線をそのまま使わず、別に用意します（[Gamma and HDR Output](gamma-srgb.md)）。選んだ曲線を通した見た目で、火や魔法の色を確認します。

## よくあるミス

??? failure "AgX の行列や係数を、自分で書き写して、一部間違える"
    **公開されている実装をそのまま使う**。**テスト画像（グレースケールと彩度のグラデーション）で、確認**する。

??? failure "Tony McMapface の LUT の端で、色がずれる"
    **半テクセルのずらし**を入れ、**`linear_clamp`** を使う。

??? failure "PBR Neutral を、映画的な絵に使って、地味になる"
    **用途に合った曲線**を選ぶ。**映画的なら、ACES・AgX**。

??? failure "曲線を切り替えたら、全体の明るさが変わって、露出がずれる"
    **各曲線の中間灰の出力が違う**。**切り替えたら、露出補正で合わせる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 新しい方式の狙い ＝ <strong>明るい彩度の高い色でも、色相が破綻しない</strong>
    - [x] <strong>AgX</strong> ＝ <strong>中立寄りのフィルミック</strong>。<strong>公開実装をそのまま使う</strong>
    - [x] <strong>Tony McMapface</strong> ＝ <strong>3D LUT</strong>。<strong>軽く、ブルームと好相性</strong>
    - [x] <strong>PBR Neutral</strong> ＝ <strong>色の忠実さ重視</strong>（商品向け）
    - [x] <strong>曲線を替えたら、露出も見直す</strong>

## 参考

- Sobotka, "AgX"（GitHub: sobotka/AgX）
- Stachowiak, "Tony McMapface"（GitHub: h3r2tic/tony-mc-mapface）
- Khronos, "PBR Neutral Tone Mapper"（KhronosGroup/ToneMapping）
- Blender Foundation, "Color Management: AgX"

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [ACES](aces.md)
- [Preserving Hue](hue-preservation.md)
- [Bloom](../bloom/index.md)
