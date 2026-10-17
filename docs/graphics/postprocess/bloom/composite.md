---
title: 合成と強さ
tags:
  - 描画
---

# 合成と強さ

**ブルームの最後の工程**は、**できあがったにじみを元の絵に足す**ことです。**足す強さ・足す位置（トーンマップの前）・段ごとの重み・レンズ ダート（汚れ）との組み合わせ・コスト**で**見た目**と**重さ**が**決まります**。このページでは、**合成の式・強さの決め方・エネルギー保存・レンズ ダート・コスト・パスの統合**を説明します。

!!! tip "ポイント"
    - 合成 ＝ <strong>元の HDR 画像 + ブルーム × 強さ</strong>。<strong>トーンマップの前</strong>に足す。
    - <strong>強さは小さく</strong>（<strong>0.04〜0.2</strong>）。<strong>かけすぎると眠い絵</strong>になる。
    - <strong>エネルギー保存型</strong>：<strong>元 × (1−強さ) + ブルーム × 強さ</strong>。<strong>明るさが増えない</strong>。
    - <strong>段ごとの重み</strong>で<strong>すそ野の形</strong>を調整。
    - <strong>レンズ ダート</strong>：<strong>汚れのテクスチャでブルームの強さを画面の場所ごとに変える</strong>。
    - <strong>コスト</strong>は<strong>帯域が支配的</strong>。<strong>半解像度・パスの統合</strong>で下げる。

## 合成の式

<strong>元の絵に足す（加算）</strong>のが**基本**です。

<div class="formula">最終 = 元 + ブルーム × 強さ</div>

```hlsl
float3 CompositeBloom(float3 scene, float3 bloom, float intensity) {
  return scene + bloom * intensity;
}
```

| 方式 | 式 | 特徴 |
| --- | --- | --- |
| **加算** | **元 + ブルーム × 強さ** | **明るさが増える**。**簡単・標準** |
| **エネルギー保存** | **元 × (1 − 強さ) + ブルーム × 強さ** | **全体の明るさが保たれ、眠くなりにくい** |
| **スクリーン** | <strong>1 − (1−元)(1−ブルーム)</strong> | **LDR 向き**（HDR では使わない） |

<!-- fig:bloom-intensity:begin -->
<!-- fig:bloom-intensity:end -->

## 強さの決め方

| 強さ | 見た目 |
| --- | --- |
| **0.0** | **ブルームなし** |
| **0.04〜0.08** | **上品なにじみ**（**現代的な、控えめな標準**） |
| **0.1〜0.2** | **はっきり光る** |
| **0.3 以上** | **夢のような、ぼんやりした絵**（**意図的な表現**） |

**強さ**は**ステージや演出ごとに変える**のが**自然**です（**夜のネオン街は強め、昼の砂漠は控えめ**）。

## 足す位置

**ブルームは、HDR のリニア画像に足し、その後でトーンマップ**します。

| 順序 | 結果 |
| --- | --- |
| **ブルーム → トーンマップ** | **明るい光のにじみがトーンマップで自然に白へ**。**正しい** |
| **トーンマップ → ブルーム** | **LDR（0〜1）の絵にぼかしを足す**ので、**明るさが足りず、にじまない**。**誤り** |

## エネルギー保存

**単純に足す**と**画面全体が少し明るくなります**。**足す分だけ元を減らす**と、**全体の明るさが保たれます**。

```hlsl
float3 CompositeEnergyConserving(float3 scene, float3 bloom, float intensity) {
  return lerp(scene, bloom, intensity);
}
```

| 点 | 説明 |
| --- | --- |
| **`lerp(元, ブルーム, 強さ)`** | **元 × (1−強さ) + ブルーム × 強さ** |
| **注意** | <strong>ブルームが「ぼかした全体の画像」</strong>（**しきい値なし**）のとき**だけ**使う。**しきい値で抜き出した光だけを足す**場合は、**単純な加算** |

**しきい値なしのブルーム**（全画素をぼかす）と**この合成**の組み合わせは、**物理的**にも**自然**です。

## 段ごとの重み

**ミップ チェーンの各段を足し合わせるとき、重みを付ける**と**すそ野の形が変わります**。

| 工夫 | 見た目 |
| --- | --- |
| **均等** | **標準** |
| **細かい段を強く** | **くっきり・シャープなにじみ** |
| **粗い段を強く** | <strong>広い、柔らかい「もや」</strong> |

```hlsl
float3 CombineLevels(float3 l0, float3 l1, float3 l2, float3 l3, float3 l4, float4 weights_a, float weight_e) {
  return l0 * weights_a.x + l1 * weights_a.y + l2 * weights_a.z + l3 * weights_a.w + l4 * weight_e;
}
```

## レンズ ダート

**カメラのレンズに付いた汚れ・傷**に**強い光が当たると汚れが光って見えます**。**汚れのテクスチャをブルームに掛ける**と、**この効果**が**出ます**。

```hlsl
float3 ApplyLensDirt(float3 bloom, float2 uv, Texture2D dirt, float dirt_intensity) {
  float3 d = dirt.SampleLevel(linear_clamp, uv, 0).rgb;
  return bloom * (1.0 + d * dirt_intensity);
}
```

| 点 | 説明 |
| --- | --- |
| **汚れ マスク** | <strong>ふつうの絵（白黒〜淡い色）</strong> のテクスチャ。**画面全体に貼る** |
| **ブルームに掛ける** | **ブルームが強い所ほど、汚れが目立つ** |
| **用途** | **戦争ゲームの爆風・SF の宇宙船・FPS のカメラ** |

詳しい演出は[レンズ効果](../lens-effects/index.md)も参照してください。

## コストと最適化

**ブルームは画面全体を何度も読み書きする**ので、**帯域が支配的**です。

| 項目 | 目安 | 対策 |
| --- | --- | --- |
| **最初の縮小** | <strong>フル解像度の読み込み（重い）</strong> | **最初から半解像度**・**13 タップを 1 回** |
| **各段の読み書き** | **小さいので安い** | **段数を 5〜6 に** |
| **最終合成** | **フル解像度の読み書き** | **トーンマップと同じパスにまとめる** |
| **フォーマット** | **R16G16B16A16_FLOAT** | <strong>R11G11B10_FLOAT（半分のメモリ）</strong> |

### パスの統合

**ブルームの最後の足し算**は、**トーンマップ・ビネット・色収差などの画面全体のパス**と**同じシェーダーにまとめる**ことが**できます**。

```hlsl
float3 FinalPass(float2 uv) {
  float3 scene = hdr_color.SampleLevel(point_clamp, uv, 0).rgb;
  float3 bloom = bloom_chain.SampleLevel(linear_clamp, uv, 0).rgb;
  float3 color = scene + bloom * bloom_intensity;
  color = ApplyExposure(color);
  color = Tonemap(color);
  color = ApplyVignette(color, uv);
  return LinearToSRGB(color);
}
```

**フル解像度のパスを 1 回に減らす**だけで、**帯域が大きく減ります**。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **強さは小さく** | **0.04〜0.1 を出発点**に、**ステージで調整** |
| **トーンマップ・ビネットと 1 パスに** | **フル解像度のパスを減らす** |
| **半解像度から始める** | **フル解像度の最初の縮小を避ける** |
| **段ごとの重みで形を調整** | **見た目をアーティストが制御できるようにする** |
| **品質設定で段数を変える** | **低スペックでは 4 段、高スペックでは 7 段** |
| **画面の明るさに合わせる** | **露出が変わる場面では、ブルームの強さも追従**させる |

## よくあるミス

??? failure "ブルームを強くしすぎて、画面全体が眠く、ぼんやりする"
    **強さを 0.05〜0.1 に**。**しきい値なしなら、エネルギー保存**。

??? failure "トーンマップの後でブルームを足して、にじまない"
    **ブルームは HDR のうちに、トーンマップの前**に足す。

??? failure "フル解像度のパスが多くて、帯域で重い"
    **合成・トーンマップ・ビネットを 1 パスに**まとめる。

??? failure "レンズ ダートを強くしすぎて、汚れが常に見える"
    **強い光のときだけ見える**よう、**強さを弱く**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 合成 ＝ <strong>元 + ブルーム × 強さ</strong>。<strong>HDR のうちにトーンマップの前</strong>
    - [x] <strong>強さは小さく</strong>（<strong>0.04〜0.1</strong>）。<strong>エネルギー保存</strong>も選べる
    - [x] <strong>段ごとの重み</strong>で<strong>すそ野の形</strong>を調整
    - [x] <strong>レンズ ダート</strong>で<strong>場所ごとの強さ</strong>を<strong>演出</strong>
    - [x] <strong>パスを統合</strong>して<strong>帯域を節約</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Unity, "Post-processing: Bloom, Lens Dirt"
- Epic Games, "Unreal Engine: Bloom"

## 関連ページ

- [ブルーム](index.md)
- [しきい値](threshold.md)
- [Dual Filter](dual-filter.md)
- [レンズ効果](../lens-effects/index.md)
- [トーンマッピングと露出](../tonemapping/index.md)
