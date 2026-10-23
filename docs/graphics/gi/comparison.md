---
title: GI Comparison
tags:
  - 描画
---

# GI Comparison

ここまで<strong>ライトマップ・ライト プローブ・SSGI・ボクセル GI・DDGI・レイトレ GI</strong>を見てきました。どれか 1 つが万能ということはなく、実際のゲームは、複数を組み合わせています。このページでは、比較表・組み合わせ方・状況別の選び方をまとめます。

!!! tip "ポイント"
    - <strong>静的なシーン</strong>：<strong>ライトマップ ＋ プローブ</strong>が、最も安く、高品質。
    - 動的なシーン：DDGI・Lumen 的・レイトレ GI。HW RT の有無で分かれる。
    - SSGI は補助：近距離の細かい間接光。単独では不安定。
    - 間接光の拡散は低周波：粗い保存で十分。細かい接触の暗さは AO。
    - 鏡面の間接光は別（反射の手法）。
    - ベースの GI ＋ AO ＋ 反射を、三位一体で設計する。

!!! info "このページを読む前に"
    - [Global Illumination (GI)](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 全方式の比較

| 方式 | 動くライト | 動く物 | 画面外 | ノイズ | 実行コスト | 事前計算 | 必要な HW |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ライトマップ | ✕ | ✕（背景のみ） | ○ | なし | 極小 | <strong>必要（重い）</strong> | なし |
| ベイク済みプローブ | ✕ | ○（受ける側） | ○ | なし | 極小 | 必要 | なし |
| SSGI | ○ | ○ | ✕ | あり（大） | 中 | なし | なし |
| ボクセル GI | ○ | ○ | ○ | 少ない | 大 | なし | 中程度 |
| DDGI | ○ | ○ | ○ | 時間蓄積で小 | 中 | なし | DXR |
| レイトレ GI（ReSTIR） | ○ | ○ | ○ | あり（デノイズ） | 大 | なし | DXR |
| Lumen 的（SW） | ○ | ○ | ○ | 小〜中 | 大 | なし（メッシュ SDF） | 中程度 |
| Radiance Cascades | ○ | ○ | ○ | なし | 中 | なし | なし（2D 向き） |


ライトマップは、動くライトにも動く物にも対応できませんが（背景のみ）、ノイズがなく、実行コストが極小で、画面外も正しく反映されます。代償は、重い事前計算が必要なことです。ベイク済みプローブは、受ける側の動く物には対応でき、同じく実行コストは極小です。SSGI は、動くライトにも動く物にも対応し、事前計算も不要ですが、画面外の情報を持たず、ノイズが大きいのが弱点です。ボクセル GI は、すべての条件に対応しますが、実行コストが大きく、ある程度の GPU 性能が必要です。DDGI は、時間蓄積でノイズが小さく、コストは中程度ですが、DXR（ハードウェア レイトレ）が必要です。レイトレ GI（ReSTIR）は、最も正確ですが、ノイズがありデノイズが必須で、コストも大きいです。Lumen 的（ソフトウェア）は、メッシュ SDF を作る以外に事前計算がなく、ノイズは小〜中、コストは大きめです。Radiance Cascades は、ノイズがなく、中程度のコストで動きますが、2D 向きです。

ライトマップは、動くライトにも動く物にも対応できませんが（背景のみ）、ノイズがなく、実行コストが極小で、画面外も正しく反映されます。代償は、重い事前計算が必要なことです。ベイク済みプローブは、受ける側の動く物には対応でき、同じく実行コストは極小です。SSGI は、動くライトにも動く物にも対応し、事前計算も不要ですが、画面外の情報を持たず、ノイズが大きいのが弱点です。ボクセル GI は、すべての条件に対応しますが、実行コストが大きく、ある程度の GPU 性能が必要です。DDGI は、時間蓄積でノイズが小さく、コストは中程度ですが、DXR（ハードウェア レイトレ）が必要です。レイトレ GI（ReSTIR）は、最も正確ですが、ノイズがありデノイズが必須で、コストも大きいです。Lumen 的（ソフトウェア）は、メッシュ SDF を作る以外に事前計算がなく、ノイズは小〜中、コストは大きめです。Radiance Cascades は、ノイズがなく、中程度のコストで動きますが、2D 向きです。

## 選び方

| 状況 | おすすめ |
| --- | --- |
| モバイル・低スペック | ライトマップ ＋ ベイク済みプローブ（動的 GI は避ける） |
| 静的な屋内・屋外が中心 | ライトマップ ＋ プローブ（最高品質・最小コスト） |
| 昼夜サイクルのある開放世界 | 動的 GI（DDGI・Lumen 的・SDFGI） |
| HW RT 対応のハイエンド | <strong>レイトレ GI（ReSTIR）</strong>・DDGI |
| HW RT なしで動的 GI | Lumen 的・SDFGI・ボクセル GI |
| 2D ゲーム | Radiance Cascades・距離場ベースの 2D GI |
| プロトタイプ・簡易 | SSGI ＋ アンビエント（定数） |

## 組み合わせの例

### 静的 ＋ 動的の混合

| 対象 | 方式 |
| --- | --- |
| 静的な背景 | ライトマップ（高品質） |
| 動く物体・キャラ | ライト プローブ（ライトマップとそろえる） |
| <strong>動的な光（懐中電灯・爆発）</strong> | 直接光のみ（間接光は無視・フェイク） |
| 接触部の暗さ | AO（[AO](../ao/index.md)） |
| 鏡面の間接光 | 反射プローブ ＋ SSR（[Reflections](../reflections/index.md)） |

### 動的 GI の階層（Lumen 的）

| 距離・用途 | 方式 |
| --- | --- |
| ごく近距離 | 画面空間トレース（SSGI 的） |
| 中距離 | 距離場トレース ＋ サーフェス キャッシュ |
| 遠距離 | 世界空間プローブ（粗い） |
| ノイズ処理 | 時間蓄積 ＋ 空間フィルタ |

## 「GI」を構成する要素

<strong>実際の画面の明るさ</strong>は、複数の要素の合計です。

| 要素 | 担当する手法 | 参照 |
| --- | --- | --- |
| 直接光 | ライティング ＋ 影 | [Shadows](../shadows/index.md) |
| 間接拡散光 | GI（このセクション） | — |
| 接触部の暗さ（微細な遮蔽） | AO | [AO](../ao/index.md) |
| 鏡面の間接光 | 反射 | [Reflections](../reflections/index.md) |
| 自己発光 | エミッシブ | — |

```hlsl
float3 color = direct_light * shadow
             + indirect_diffuse * albedo * ao
             + indirect_specular * specular_color * specular_occlusion
             + emissive;
```

AO は間接光（拡散）に掛けるのが原則です（直接光には掛けない）。鏡面の間接光には、鏡面オクルージョンを掛けます（[AO Artifacts](../ao/artifacts/index.md)）。

## デバッグのヒント

| 症状 | 確認すること |
| --- | --- |
| 暗い部屋が真っ黒 | 間接光（GI）が効いているか・アンビエント（環境光）の最低値 |
| 壁越しに光が漏れる | プローブの可視性・配置・ボクセル解像度・壁の厚み |
| 動く物体だけ、背景と明るさが違う | プローブとライトマップの、整合 |
| 画面端で間接光が変わる | SSGI の画面外・ベースの GI へのフォールバック |
| ノイズ・チラつき | デノイズ・時間蓄積・ブルー ノイズ |
| ライトを動かしても反応しない | ベイク済みの GI は、固定。動的な方式が必要 |
| 間接光が二重に効いている | ライトマップと動的 GI の重複・AO の二重掛け |

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>静的は、ライトマップ ＋ プローブ</strong>（最安・高品質）。動的は、DDGI・Lumen 的・レイトレ
    - [x] SSGI は補助。単独では画面外・視点依存で不安定
    - [x] HW RT の有無で、動的 GI の選択肢が分かれる
    - [x] ベースの GI ＋ AO ＋ 反射を組み合わせ、重複（二重掛け）に注意
    - [x] AO は間接拡散光に、鏡面オクルージョンは間接鏡面光に掛ける

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明の章）
- Wright, Narkowicz, Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games
- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019（DDGI）
- Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011)
- Ouyang, Liu, Kettunen, Pharr, Pantaleoni, "ReSTIR GI: Path Resampling for Real-Time Path Tracing", Computer Graphics Forum (High-Performance Graphics 2021)

## 関連ページ

- [Global Illumination (GI)](index.md)
- [Lightmaps](lightmaps/index.md)
- [Probe GI](probes/index.md)
- [DDGI](ddgi.md)
- [AO](../ao/index.md)
- [Reflections](../reflections/index.md)
