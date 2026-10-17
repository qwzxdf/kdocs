---
title: レイトレ GI・Radiance Cascades
tags:
  - 描画
---

# レイトレ GI・Radiance Cascades

ここまでの動的 GI は、<strong>画面空間（SSGI）</strong>・**ボクセル**・<strong>プローブ（DDGI）</strong>と、<strong>何らかの「中間表現」</strong>に**光を保存**していました。**レイトレ GI**は、**画素から、直接レイを飛ばして**、**ヒット点の光**を**集める**方式で、**最も素直で正確**です。**ただし、1 画素 1 本のレイでは、ノイズが膨大**なので<strong>デノイズ・サンプルの再利用（ReSTIR）</strong>が**不可欠**です。さらに**ハードウェア レイトレースが無くても使える**、**Lumen 的なソフトウェア方式**や、**Radiance Cascades**という**新しい方式**もあります。

!!! tip "ポイント"
    - <strong>画素から半球にレイ</strong>を飛ばし、<strong>ヒット点の光</strong>を<strong>集める</strong>（パス トレースの 1〜2 バウンス）。
    - <strong>ヒット点の光</strong>は、<strong>直接光（影付き）＋ 別のキャッシュ（プローブ・前フレーム）</strong>から得て、<strong>再帰を避ける</strong>。
    - <strong>ノイズ</strong>が<strong>最大の敵</strong>：<strong>重要度サンプリング・時間蓄積・空間フィルタ・ReSTIR</strong>。
    - <strong>ReSTIR GI</strong>：<strong>近い画素・前フレームの良いサンプルを再利用</strong>して、<strong>少ないレイで高品質</strong>。
    - <strong>Lumen 的</strong>：<strong>サーフェス キャッシュ ＋ 距離場トレース ＋ プローブ</strong>。<strong>HW RT なしでも動く</strong>。
    - <strong>Radiance Cascades</strong>：<strong>空間と方向の解像度を階層的に変えて</strong>、<strong>全点の放射照度</strong>を<strong>ノイズなしで</strong>計算。

## 素直なレイトレ GI

**画素のワールド位置と法線**から、**余弦重み付き**で**ランダムな方向**にレイを飛ばし、**ヒット点の放射輝度**を**集めます**。

```hlsl
float3 PathTraceGI(float3 pos, float3 normal, uint2 pixel) {
  float3 dir = CosineSampleHemisphere(normal, BlueNoise2D(pixel));
  Hit hit = TraceRay(pos + normal * kRayBias, dir);
  if (!hit.valid) return SampleSky(dir);
  float3 direct = EvaluateDirectLight(hit);
  float3 indirect = ReadIrradianceCache(hit.position, hit.normal);
  return hit.albedo * (direct + indirect);
}
```

| 点 | 説明 |
| --- | --- |
| **余弦重み付き方向** | **`(n·ω)/pdf` が定数**になり、**平均**だけでよい |
| **ヒット点の直接光** | **ライトを評価**し、**シャドウ レイ**（またはシャドウ マップ）で**影** |
| **ヒット点の間接光** | **再帰しない**（**重い**）。**キャッシュ**（**プローブ・前フレームのスクリーン**・**世界空間のキャッシュ**）から**読む**＝**無料の多バウンス** |
| **ミス** | **空の光**（環境マップ） |

**再帰を避ける**ことが**リアルタイム化の鍵**です。<strong>1 回のレイでヒット点の光を「キャッシュから読む」</strong>ことで**バウンスを重ねる**代わりに、**フレームを重ねて**蓄積します。

## ノイズとの戦い

**画素あたり 1 本**のレイでは、**非常にノイズが多い**です。

### 重要度サンプリング

**光の寄与が大きい方向**を、**多めにサンプル**します。

| 方法 | 内容 |
| --- | --- |
| **余弦重み付き** | **BRDF の余弦**に従う（基本） |
| <strong>ライトのサンプリング（NEE）</strong> | **ヒット点でライトを直接サンプル**（**Next Event Estimation**） |
| **ブルー ノイズ** | **サンプルの偏りを画面全体で均す** |

### デノイズ

| 手法 | 内容 |
| --- | --- |
| **時間蓄積** | **前フレームの結果**を**再投影**して**混ぜる** |
| **空間フィルタ** | **法線・深度**を**手がかり**に**エッジ保存**で**ぼかす** |
| <strong>分散ガイド（SVGF 系）</strong> | **分散**を推定して、**ノイズの多い画素**を**強くぼかす** |
| **専用デノイザ** | <strong>NVIDIA NRD（ReBLUR・ReLAX）</strong>・**AMD FidelityFX Denoiser**・**OIDN**（オフライン向け） |
| **機械学習** | **DLSS Ray Reconstruction** など、**ニューラル ネットワークで、デノイズとアップスケールを同時に** |

## ReSTIR GI

**ReSTIR**（Reservoir-based Spatiotemporal Importance Resampling）は、<strong>「良いサンプルを近い画素・前フレームから借りる」</strong>ことで、**1 画素あたりの有効なサンプル数**を**大幅に増やす**手法です。

| 概念 | 内容 |
| --- | --- |
| **リザーバー** | <strong>画素ごとに、「これまでで最良のサンプル 1 つ」</strong>と**重みの合計**を保持（**重み付きリザーバー サンプリング**） |
| **時間的な再利用** | **前フレームの同じ位置のリザーバー**と**マージ** |
| **空間的な再利用** | **近隣の画素のリザーバー**と**マージ** |
| **バイアスの補正** | **他の画素のサンプル**が**この画素にとって有効か**（**可視性・ヤコビアン**）を**補正** |
| **効果** | <strong>少ないレイ（1 本）</strong>で、**多数のレイを飛ばしたような**品質 |

**ReSTIR DI**（直接光）から、**ReSTIR GI**（間接光）、**ReSTIR PT**（パス全体）へと**発展**しています。**NVIDIA RTXDI・RTXGI** などに**採用**されています。

## Lumen 的な方式

**Unreal Engine 5 の Lumen**は、**ハードウェア レイトレースが無くても**動く**GI**です。**複数の手法を階層的に組み合わせて**います。

| 要素 | 内容 |
| --- | --- |
| **サーフェス キャッシュ** | <strong>メッシュの表面を小さな「カード」</strong>に**キャプチャ**し、**各カードに直接光・間接光を保存**（**ヒット点の光を安く得る**ため） |
| **距離場によるトレース** | **メッシュごとの SDF**と**グローバル SDF**で、**ソフトウェア レイトレース**（[距離場の影](../shadows/sdf-shadows.md)） |
| <strong>画面空間トレース（最初の手段）</strong> | **近距離は画面の深度バッファ**で**精密に**トレース（[SSGI](ssgi.md)） |
| **スクリーン プローブ** | **画面上に間引いて置いた**プローブから、**レイ**を飛ばし、**画素へ補間**（**画素ごとにレイを飛ばさない**） |
| <strong>ワールド プローブ（遠距離）</strong> | **遠くの光**は**世界空間の粗いプローブ**から |
| **HW RT モード** | **対応 GPU**では、**距離場の代わりにハードウェア レイトレース** |

<strong>「画素ごと」ではなく「間引いたプローブ」からレイを飛ばす</strong>ことで、**コストを大幅に下げ**ています。

## Radiance Cascades

**Radiance Cascades**（Alexander Sannikov、2023〜）は、**ノイズのない、全画素の放射照度**を**階層的な構造**で**効率よく計算する**方式です。

### 発想：空間と方向のトレードオフ

**ある点が受け取る光**を**正確に知る**には、<strong>「点を細かく」×「方向を細かく」</strong>の**積**だけ**サンプル**が要りそうです。しかし、<strong>「近い距離の光」と「遠い距離の光」では必要な精度が違います</strong>。

| 距離 | 必要な精度 |
| --- | --- |
| <strong>近い光（短いレイ）</strong> | **点（空間）は細かく**、**方向は粗くてよい**（近い物は角度が大きく見える） |
| <strong>遠い光（長いレイ）</strong> | **点は粗くてよい**、**方向は細かく**（遠い物は角度が小さく、位置が変わっても見える向きが同じ） |

### カスケード

<strong>複数の「カスケード」</strong>を用意します。

| カスケード | プローブの密度（空間） | 方向の数 | 担当する距離 |
| --- | --- | --- | --- |
| **0** | **最も細かい** | **少ない** | **近距離** |
| **1** | **半分** | **倍** | **やや遠く** |
| **2** | **さらに半分** | **さらに倍** | **さらに遠く** |
| … | … | … | … |

<strong>各カスケードは、自分の担当する距離の「区間」</strong>だけを**レイでトレース**します。**最後にカスケードをマージ**（**遠い方の結果を近い方に伝える**）して、**全画素の全距離にわたる放射照度**を得ます。

| 性質 | 内容 |
| --- | --- |
| **ノイズなし** | **ランダム性を使わず、規則的なサンプル**で**ノイズがない** |
| **計算量** | **カスケードごとのレイ数がほぼ一定**（空間が半分・方向が倍で**総数はあまり変わらない**）。**画素数 × 定数** |
| **2D で成功** | **2D ゲームの GI**で、**非常に有効**（**Radiance Cascades の 2D 版**） |
| **3D への拡張** | **研究・実装が進行中**（**3D は方向が球面（2 次元）で、重い**） |

**まだ発展途中**の技術ですが、**ノイズのない GI**として、**注目**されています。

## 手法の選び方（動的 GI）

| 状況 | 方式 |
| --- | --- |
| **HW RT 対応・最高品質** | **レイトレ GI ＋ ReSTIR ＋ デノイズ**、**DDGI** |
| **HW RT なしの一般向け** | **Lumen 的**（距離場 ＋ プローブ）、**SDFGI** |
| **2D ゲーム** | **Radiance Cascades**・**距離場ベースの 2D GI** |
| **モバイル** | **ライトマップ ＋ プローブ**（動的 GI は避ける） |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **正確**（ジオメトリそのもの） | **ノイズ** ＋ **デノイズ**が必須 |
| **画面外・裏側**も**反映** | **コストが高い**（レイ・デノイズ・加速構造） |
| **動く物・動くライトに自然に対応** | **HW RT 対応 GPU**（ソフトウェア方式は、品質が劣る） |
| **ReSTIR などで年々、効率が向上** | **実装が複雑**（ReSTIR・デノイザ） |

## よくあるミス

??? failure "ヒット点で、再帰的にバウンスを追って、コストが爆発する"
    <strong>キャッシュ（プローブ・前フレーム）</strong>から**読む**。

??? failure "ノイズのまま、出力して、チラつく"
    **時間蓄積 ＋ 空間フィルタ ＋ 専用デノイザ**。

??? failure "ReSTIR で、他の画素のサンプルを可視性チェックなしで再利用して、光漏れ"
    **再利用時に可視性・ヤコビアン**を**補正**する。

??? failure "全画素にレイを飛ばして、重い"
    <strong>間引き（スクリーン プローブ）</strong>・**半解像度**・**ReSTIR**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レイトレ GI ＝ <strong>画素から半球にレイを飛ばし、ヒット点の光を集める</strong>。<strong>ヒット点の光は、キャッシュから読んで再帰を避ける</strong>
    - [x] <strong>ノイズ</strong>は<strong>重要度サンプリング・デノイズ・ReSTIR</strong>で<strong>消す・減らす</strong>
    - [x] <strong>ReSTIR</strong> ＝ <strong>近隣・前フレームの良いサンプルを、リザーバーで再利用</strong>
    - [x] <strong>Lumen 的</strong> ＝ <strong>サーフェス キャッシュ ＋ 距離場 ＋ 間引いたプローブ</strong>（HW RT なしでも動く）
    - [x] <strong>Radiance Cascades</strong> ＝ <strong>近距離は細かい点・粗い方向、遠距離は粗い点・細かい方向</strong>の<strong>階層</strong>で<strong>ノイズなし</strong>に

## 参考

- Ouyang et al., "ReSTIR GI: Path Resampling for Real-Time Path Tracing"（HPG 2021）
- Bitterli et al., "Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting"（SIGGRAPH 2020）
- Wright et al., "Lumen: Real-time Global Illumination in Unreal Engine 5"（SIGGRAPH 2022）
- Sannikov, "Radiance Cascades"（2023）

## 関連ページ

- [間接光（GI）](index.md)
- [GI の理論](theory.md)
- [SSGI](ssgi.md)
- [DDGI](ddgi.md)
- [距離場の影](../shadows/sdf-shadows.md)
- [RT 反射](../reflections/rt-reflections.md)
