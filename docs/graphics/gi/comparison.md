---
title: GI 手法の比較
tags:
  - 描画
---

# GI 手法の比較

ここまで**ライトマップ・ライト プローブ・SSGI・ボクセル GI・DDGI・レイトレ GI**を見てきました。**どれか 1 つが万能**ということは**なく**、**実際のゲームは、複数を組み合わせて**います。このページでは、**比較表・組み合わせ方・状況別の選び方**をまとめます。

!!! tip "ポイント"
    - <strong>静的なシーン</strong>：<strong>ライトマップ ＋ プローブ</strong>が、<strong>最も安く、高品質</strong>。
    - <strong>動的なシーン</strong>：<strong>DDGI・Lumen 的・レイトレ GI</strong>。<strong>HW RT の有無</strong>で分かれる。
    - <strong>SSGI は補助</strong>：<strong>近距離の細かい間接光</strong>。<strong>単独では不安定</strong>。
    - <strong>間接光の拡散は低周波</strong>：<strong>粗い保存で十分</strong>。<strong>細かい接触の暗さは AO</strong>。
    - <strong>鏡面の間接光は別</strong>（<strong>反射</strong>の手法）。
    - <strong>ベースの GI ＋ AO ＋ 反射</strong>を、<strong>三位一体</strong>で設計する。

## 全方式の比較

| 方式 | 動くライト | 動く物 | 画面外 | ノイズ | 実行コスト | 事前計算 | 必要な HW |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **ライトマップ** | ✕ | ✕（背景のみ） | ○ | なし | **極小** | <strong>必要（重い）</strong> | なし |
| **ベイク済みプローブ** | ✕ | ○（受ける側） | ○ | なし | **極小** | 必要 | なし |
| **SSGI** | ○ | ○ | **✕** | <strong>あり（大）</strong> | 中 | なし | なし |
| **ボクセル GI** | ○ | ○ | ○ | 少ない | 大 | なし | 中程度 |
| **DDGI** | ○ | ○ | ○ | 時間蓄積で小 | 中 | なし | **DXR** |
| <strong>レイトレ GI（ReSTIR）</strong> | ○ | ○ | ○ | あり（デノイズ） | **大** | なし | **DXR** |
| <strong>Lumen 的（SW）</strong> | ○ | ○ | ○ | 小〜中 | 大 | なし（メッシュ SDF） | 中程度 |
| **Radiance Cascades** | ○ | ○ | ○ | **なし** | 中 | なし | なし（2D 向き） |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| **モバイル・低スペック** | **ライトマップ ＋ ベイク済みプローブ**（動的 GI は避ける） |
| **静的な屋内・屋外が中心** | **ライトマップ ＋ プローブ**（**最高品質・最小コスト**） |
| **昼夜サイクルのある開放世界** | **動的 GI**（DDGI・Lumen 的・SDFGI） |
| **HW RT 対応のハイエンド** | <strong>レイトレ GI（ReSTIR）</strong>・**DDGI** |
| **HW RT なしで動的 GI** | **Lumen 的**・**SDFGI**・**ボクセル GI** |
| **2D ゲーム** | **Radiance Cascades**・**距離場ベースの 2D GI** |
| **プロトタイプ・簡易** | <strong>SSGI ＋ アンビエント（定数）</strong> |

## 組み合わせの例

### 静的 ＋ 動的の混合

| 対象 | 方式 |
| --- | --- |
| **静的な背景** | **ライトマップ**（高品質） |
| **動く物体・キャラ** | **ライト プローブ**（ライトマップと**そろえる**） |
| <strong>動的な光（懐中電灯・爆発）</strong> | **直接光のみ**（間接光は無視・フェイク） |
| **接触部の暗さ** | **AO**（[AO](../ao/index.md)） |
| **鏡面の間接光** | **反射プローブ ＋ SSR**（[反射](../reflections/index.md)） |

### 動的 GI の階層（Lumen 的）

| 距離・用途 | 方式 |
| --- | --- |
| **ごく近距離** | <strong>画面空間トレース（SSGI 的）</strong> |
| **中距離** | **距離場トレース ＋ サーフェス キャッシュ** |
| **遠距離** | <strong>世界空間プローブ（粗い）</strong> |
| **ノイズ処理** | **時間蓄積 ＋ 空間フィルタ** |

## 「GI」を構成する要素

**実際の画面の明るさ**は、**複数の要素の合計**です。

| 要素 | 担当する手法 | 参照 |
| --- | --- | --- |
| **直接光** | ライティング ＋ **影** | [影](../shadows/index.md) |
| **間接拡散光** | <strong>GI（このセクション）</strong> | — |
| <strong>接触部の暗さ（微細な遮蔽）</strong> | **AO** | [AO](../ao/index.md) |
| **鏡面の間接光** | **反射** | [反射](../reflections/index.md) |
| **自己発光** | エミッシブ | — |

```hlsl
float3 color = direct_light * shadow
             + indirect_diffuse * albedo * ao
             + indirect_specular * specular_color * specular_occlusion
             + emissive;
```

**AO は間接光（拡散）に掛ける**のが**原則**です（**直接光には掛けない**）。**鏡面の間接光には、鏡面オクルージョン**を**掛け**ます（[AO のアーティファクト](../ao/artifacts/index.md)）。

## デバッグのヒント

| 症状 | 確認すること |
| --- | --- |
| **暗い部屋が真っ黒** | **間接光（GI）が効いているか**・**アンビエント（環境光）の最低値** |
| **壁越しに光が漏れる** | **プローブの可視性・配置**・**ボクセル解像度・壁の厚み** |
| **動く物体だけ、背景と明るさが違う** | **プローブとライトマップの、整合** |
| **画面端で間接光が変わる** | **SSGI の画面外**・**ベースの GI へのフォールバック** |
| **ノイズ・チラつき** | **デノイズ・時間蓄積・ブルー ノイズ** |
| **ライトを動かしても反応しない** | **ベイク済みの GI は、固定**。**動的な方式**が必要 |
| **間接光が二重に効いている** | **ライトマップと動的 GI の重複**・**AO の二重掛け** |

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

- [間接光（GI）](index.md)
- [ライトマップ](lightmaps/index.md)
- [ライト プローブ](probes/index.md)
- [DDGI](ddgi.md)
- [AO](../ao/index.md)
- [反射](../reflections/index.md)
