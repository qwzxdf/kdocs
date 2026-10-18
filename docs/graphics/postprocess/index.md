---
title: Post-Processing
tags:
  - 描画
---

# Post-Processing

3D の描画が終わった<strong>画像（HDR のカラー バッファ）</strong>に、**画面全体への加工**を重ねて、**最終的な見た目**を作るのが**ポストプロセス**です。**ブルーム（光のにじみ）・被写界深度（ピンぼけ）・モーション ブラー・アンチエイリアシング・トーンマッピング・カラー グレーディング**など、**ゲームの「絵作り」の、大半**がここで決まります。**ライティングが「物理的な光」を計算する**のに対し、**ポストプロセスは「カメラ（レンズ・フィルム・目）」を模擬する**と考えると整理しやすくなります。

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [Tone Mapping and Exposure](tonemapping/index.md) | HDR → LDR。露出・Reinhard・フィルミック・ACES・AgX・色相の保ち方・自動露出・ガンマ |
| [Bloom](bloom/index.md) | 明るい部分のにじみ。しきい値・ダウンサンプル・ガウス・Dual Filter・Karis・合成 |
| [Depth of Field (DOF)](dof/index.md) | 錯乱円・ギャザー・スキャッター・前景と背景・ボケの形 |
| [Motion Blur](motion-blur/index.md) | 速度バッファ・カメラ・オブジェクト・ぼかしの実装・タイル最大速度・強さと TAA |
| [Anti-Aliasing](antialiasing/index.md) | MSAA・FXAA・SMAA・TAA・TAA の課題・比較 |
| [Color Grading](color-grading/index.md) | 基本の調整・リフト/ガンマ/ゲイン・ホワイト バランス・3D LUT・LUT の作り方 |
| [Lens Effects](lens-effects/index.md) | 色収差・ビネット・フィルム グレイン・レンズ フレア |
| [Outlines and Toon](stylized/index.md) | 背面法・画面空間エッジ・セル シェーディング・ポスタライズとハーフトーン |

## Order of Processing {#処理の順序}

**ポストプロセスは、順序を間違える**と**見た目が不自然**になります。**典型的な並び**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="ポストプロセスの順序">
<text x="20" y="24" class="fig-title">HDR（リニア）のうちに、空間的な効果 → トーンマップ → LDR で仕上げ</text>
<g stroke="currentColor" stroke-width="2"><rect x="20" y="50" width="110" height="44" rx="6" fill="rgba(76,139,245,0.18)"/><rect x="146" y="50" width="110" height="44" rx="6" fill="rgba(76,139,245,0.18)"/><rect x="272" y="50" width="110" height="44" rx="6" fill="rgba(76,139,245,0.18)"/><rect x="398" y="50" width="110" height="44" rx="6" fill="rgba(76,139,245,0.18)"/><rect x="524" y="50" width="110" height="44" rx="6" fill="rgba(229,170,40,0.3)"/><rect x="650" y="50" width="110" height="44" rx="6" fill="rgba(46,160,67,0.22)"/></g>
<g style="font-size:12px"><text x="32" y="76">TAA／AA</text><text x="158" y="76">DOF</text><text x="278" y="76">モーション</text><text x="410" y="76">ブルーム</text><text x="534" y="76">トーンマップ</text><text x="660" y="76">グレーディング</text></g>
<g stroke="currentColor" stroke-width="2" fill="none"><line x1="130" y1="72" x2="146" y2="72"/><line x1="256" y1="72" x2="272" y2="72"/><line x1="382" y1="72" x2="398" y2="72"/><line x1="508" y1="72" x2="524" y2="72"/><line x1="634" y1="72" x2="650" y2="72"/></g>
<text x="20" y="130" style="font-size:12px">リニア HDR（光の量そのもの）</text><line x1="20" y1="136" x2="508" y2="136" stroke="currentColor" stroke-width="3"/>
<text x="524" y="130" style="font-size:12px">LDR（表示用）</text><line x1="524" y1="136" x2="760" y2="136" stroke="currentColor" stroke-width="3"/>
<text x="20" y="170" style="font-size:12px">LDR 側で：色収差・ビネット・グレイン・シャープ・FXAA など（最後に UI を重ねる）</text>
<text x="20" y="196" style="font-size:12px">※ 実際の並びは、エンジン・目的で変わる。基本は「光の物理が成り立つ段階（HDR）で、光学的な効果を」</text>
</svg>

| 段階 | 効果 | 理由 |
| --- | --- | --- |
| <strong>HDR（リニア）</strong> | **TAA・DOF・モーション ブラー・ブルーム** | **光の「量」を平均・拡散する効果**は、**物理的に正しいリニア値**で行う（**LDR でぼかすと明るい点が暗く潰れる**） |
| **トーンマップ** | **HDR → LDR** | **ここで表示可能な範囲に収める** |
| **LDR** | **カラー グレーディング・色収差・ビネット・グレイン・FXAA・シャープ** | **見た目の調整**は、**表示を基準**に行う |
| **最後** | **UI・ガンマ（sRGB）変換** | **UI はポストプロセスの影響を受けさせない** |

最初が <strong>HDR（リニア）</strong>の段階で、TAA・被写界深度・モーション ブラー・ブルームを行います。これらは、光の「量」を平均したり拡散したりする効果なので、物理的に正しいリニアな値で行う必要があります。LDR（表示用の 0〜1 に収めた値）でぼかすと、明るい点が暗く潰れて、光の量が保存されません。次が<strong>トーンマップ</strong>で、HDR を LDR に変換して、表示可能な範囲に収めます。その後の <strong>LDR</strong> の段階で、カラー グレーディング・色収差・ビネット・グレイン・FXAA・シャープを行います。これらは見た目の調整なので、表示を基準にして行います。<strong>最後</strong>に、UI を描き、ガンマ（sRGB）変換を行います。UI はポストプロセスの影響を受けさせないためです。

最初が <strong>HDR（リニア）</strong>の段階で、TAA・被写界深度・モーション ブラー・ブルームを行います。これらは、光の「量」を平均したり拡散したりする効果なので、物理的に正しいリニアな値で行う必要があります。LDR（表示用の 0〜1 に収めた値）でぼかすと、明るい点が暗く潰れて、光の量が保存されません。次が<strong>トーンマップ</strong>で、HDR を LDR に変換して、表示可能な範囲に収めます。その後の <strong>LDR</strong> の段階で、カラー グレーディング・色収差・ビネット・グレイン・FXAA・シャープを行います。これらは見た目の調整なので、表示を基準にして行います。<strong>最後</strong>に、UI を描き、ガンマ（sRGB）変換を行います。UI はポストプロセスの影響を受けさせないためです。

**例外**：**グレーディングをトーンマップの前に行う**（**ACES の流れ**）・**ブルームをトーンマップ後に重ねる**など、**エンジンごとの流儀**があります。

## Shared Techniques {#共通の技術}

| 技術 | 内容 |
| --- | --- |
| **フルスクリーン トライアングル** | **画面全体を覆う 1 枚の三角形**で、**ピクセル シェーダーを走らせる**（**四角形 2 枚より、斜めの継ぎ目がなく効率的**） |
| **コンピュート シェーダー** | **共有メモリを使い、ぼかしなどを高速に**（**ブラーのタイル処理**） |
| **ダウンサンプル／アップサンプル** | **半解像度・1/4 解像度**で**重い効果**を**安く** |
| **HDR フォーマット** | <strong>R11G11B10_FLOAT（軽い）</strong>・<strong>R16G16B16A16_FLOAT（高精度）</strong> |
| **ping-pong** | **2 枚のバッファを交互に入出力**にして**連鎖** |

### Full-Screen Triangle {#フルスクリーン-トライアングル}

**頂点バッファなし**で、**`SV_VertexID`** から**3 頂点**を作ります。

```hlsl
struct VsOutput {
  float4 position : SV_Position;
  float2 uv : TEXCOORD0;
};

VsOutput FullscreenVS(uint vertex_id : SV_VertexID) {
  VsOutput output;
  output.uv = float2((vertex_id << 1) & 2, vertex_id & 2);
  output.position = float4(output.uv * float2(2.0, -2.0) + float2(-1.0, 1.0), 0.0, 1.0);
  return output;
}
```

コードの要点です。`uv` は `(0,0)`・`(2,0)`・`(0,2)` で、画面を覆う大きな三角形になります。`position` は uv を NDC に変換したもので、y は D3D のテクスチャ座標（上が 0）に合わせて反転します。描画は `Draw(3, 0)` で、インデックスも頂点バッファも不要です。

## Related Pages {#関連ページ}

- [描画](../index.md)
- [ポストプロセスの最適化](../../rendering/postprocess.md)
- [TAA・アップスケール](../../rendering/taa-upscaling.md)
- [低解像度エフェクト](../../rendering/low-res-effects.md)
- [Reflections](../reflections/index.md)
