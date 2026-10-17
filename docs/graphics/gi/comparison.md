---
title: GI Comparison
tags:
  - 描画
---

# GI Comparison

ここまで**ライトマップ・ライト プローブ・SSGI・ボクセル GI・DDGI・レイトレ GI**を見てきました。**どれか 1 つが万能**ということは**なく**、**実際のゲームは、複数を組み合わせて**います。このページでは、**比較表・組み合わせ方・状況別の選び方**をまとめます。

!!! tip "ポイント"
    - <strong>静的なシーン</strong>：<strong>ライトマップ ＋ プローブ</strong>が、<strong>最も安く、高品質</strong>。
    - <strong>動的なシーン</strong>：<strong>DDGI・Lumen 的・レイトレ GI</strong>。<strong>HW RT の有無</strong>で分かれる。
    - <strong>SSGI は補助</strong>：<strong>近距離の細かい間接光</strong>。<strong>単独では不安定</strong>。
    - <strong>間接光の拡散は低周波</strong>：<strong>粗い保存で十分</strong>。<strong>細かい接触の暗さは AO</strong>。
    - <strong>鏡面の間接光は別</strong>（<strong>反射</strong>の手法）。
    - <strong>ベースの GI ＋ AO ＋ 反射</strong>を、<strong>三位一体</strong>で設計する。

## 全方式の比較

方式を、いくつかの観点で順に比べます。

<strong>ライトマップ</strong>は、動くライトにも動く物にも対応できませんが（背景のみ）、ノイズがなく、実行コストが極小で、画面外も正しく反映されます。代償は、重い事前計算が必要なことです。<strong>ベイク済みプローブ</strong>は、受ける側の動く物には対応でき、同じく実行コストは極小です。<strong>SSGI</strong> は、動くライトにも動く物にも対応し、事前計算も不要ですが、画面外の情報を持たず、ノイズが大きいのが弱点です。<strong>ボクセル GI</strong> は、すべての条件に対応しますが、実行コストが大きく、ある程度の GPU 性能が必要です。<strong>DDGI</strong> は、時間蓄積でノイズが小さく、コストは中程度ですが、DXR（ハードウェア レイトレ）が必要です。<strong>レイトレ GI（ReSTIR）</strong>は、最も正確ですが、ノイズがありデノイズが必須で、コストも大きいです。<strong>Lumen 的（ソフトウェア）</strong>は、メッシュ SDF を作る以外に事前計算がなく、ノイズは小〜中、コストは大きめです。<strong>Radiance Cascades</strong> は、ノイズがなく、中程度のコストで動きますが、2D 向きです。

## 選び方

状況別のおすすめは、次のとおりです。モバイルや低スペック環境では、<strong>ライトマップとベイク済みプローブ</strong>を使い、動的 GI は避けます。静的な屋内・屋外が中心なら、同じく<strong>ライトマップとプローブ</strong>が、最高品質・最小コストです。昼夜サイクルのある開放世界では、<strong>動的 GI</strong>（DDGI・Lumen 的・SDFGI）が必要になります。ハードウェア RT 対応のハイエンドなら、<strong>レイトレ GI（ReSTIR）</strong>か DDGI です。ハードウェア RT なしで動的 GI が必要なら、Lumen 的・SDFGI・ボクセル GI です。2D ゲームなら Radiance Cascades や距離場ベースの 2D GI、プロトタイプや簡易な用途なら、SSGI にアンビエント（定数）を足す程度で十分です。

## 組み合わせの例

### 静的 ＋ 動的の混合

静的と動的を混合する例です。静的な背景は<strong>ライトマップ</strong>で高品質に仕上げます。動く物体やキャラクターは<strong>ライト プローブ</strong>で、ライトマップと見た目を揃えます。動的な光（懐中電灯や爆発）は、直接光のみを計算し、間接光は無視するか、フェイクで足します。接触部の暗さは [AO](../ao/index.md) が、鏡面の間接光は反射プローブと SSR（[Reflections](../reflections/index.md)）が担当します。

### 動的 GI の階層（Lumen 的）

動的 GI を階層にした例（Lumen 的）は、距離で方式を使い分けます。ごく近距離は<strong>画面空間トレース</strong>（SSGI 的）、中距離は<strong>距離場トレースとサーフェス キャッシュ</strong>、遠距離は<strong>粗い世界空間プローブ</strong>です。ノイズは、時間蓄積と空間フィルタで処理します。

## 「GI」を構成する要素

**実際の画面の明るさ**は、**複数の要素の合計**です。

画面の明るさは、複数の要素の合計です。<strong>直接光</strong>は、ライティングと影が担当します（[Shadows](../shadows/index.md)）。<strong>間接拡散光</strong>が、このセクションの GI の役割です。<strong>接触部の暗さ</strong>（微細な遮蔽）は AO（[AO](../ao/index.md)）、<strong>鏡面の間接光</strong>は反射（[Reflections](../reflections/index.md)）、<strong>自己発光</strong>はエミッシブが担当します。

```hlsl
float3 color = direct_light * shadow
             + indirect_diffuse * albedo * ao
             + indirect_specular * specular_color * specular_occlusion
             + emissive;
```

**AO は間接光（拡散）に掛ける**のが**原則**です（**直接光には掛けない**）。**鏡面の間接光には、鏡面オクルージョン**を**掛け**ます（[AO Artifacts](../ao/artifacts/index.md)）。

## デバッグのヒント

症状別の確認事項を挙げます。暗い部屋が真っ黒なら、間接光（GI）が効いているか、アンビエントの最低値があるかを見ます。壁越しに光が漏れるなら、プローブの可視性と配置、ボクセル解像度と壁の厚みを疑います。動く物体だけ背景と明るさが違うなら、プローブとライトマップの整合を確認します。画面端で間接光が変わるなら、SSGI の画面外処理と、ベースの GI へのフォールバックを見直します。ノイズやチラつきには、デノイズ、時間蓄積、ブルー ノイズが効きます。ライトを動かしても反応しないなら、ベイク済みの GI は固定なので、動的な方式が必要です。間接光が二重に効いているなら、ライトマップと動的 GI の重複、あるいは AO の二重掛けを疑います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>静的は、ライトマップ ＋ プローブ</strong>（最安・高品質）。<strong>動的は、DDGI・Lumen 的・レイトレ</strong>
    - [x] <strong>SSGI は補助</strong>。<strong>単独では画面外・視点依存で不安定</strong>
    - [x] <strong>HW RT の有無</strong>で、<strong>動的 GI の選択肢</strong>が分かれる
    - [x] <strong>ベースの GI ＋ AO ＋ 反射</strong>を<strong>組み合わせ</strong>、<strong>重複（二重掛け）</strong>に注意
    - [x] <strong>AO は間接拡散光に</strong>、<strong>鏡面オクルージョンは間接鏡面光に</strong>掛ける

## 参考

- Wright et al., "Lumen: Real-time Global Illumination in Unreal Engine 5"（SIGGRAPH 2022）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Global Illumination (GI)](index.md)
- [Lightmaps](lightmaps/index.md)
- [ライト プローブ](probes/index.md)
- [DDGI](ddgi.md)
- [AO](../ao/index.md)
- [Reflections](../reflections/index.md)
