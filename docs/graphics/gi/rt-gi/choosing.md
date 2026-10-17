---
title: Choosing a Method
tags:
  - 描画
---

# Choosing a Method

**動的な GI の手法は、品質・コスト・必要なハードウェアで、向き不向きがあります**。このページでは、**手法の選び方の目安と、長所・短所**を説明します。

!!! tip "ポイント"
    - **ハードウェア RT が使える → レイトレ GI ＋ ReSTIR**。
    - **使えない → Lumen 的な方式・DDGI・SSGI**。
    - **2D やステージ制 → Radiance Cascades**。
    - **予算が厳しい → SSGI やプローブ**。

## 手法の選び方（動的 GI）
状況別の選び方です。ハードウェア レイトレース対応で最高品質を求めるなら、<strong>レイトレ GI ＋ ReSTIR ＋ デノイズ</strong>、あるいは <strong>DDGI</strong> です。ハードウェア RT のない一般向け環境なら、<strong>Lumen 的な方式</strong>（距離場とプローブ）や SDFGI が選べます。2D ゲームなら、<strong>Radiance Cascades</strong> や距離場ベースの 2D GI が向きます。モバイルでは、動的 GI は避けて、<strong>ライトマップとプローブ</strong>の組み合わせにします。

## 長所と短所
動的 GI の長所は、ジオメトリそのものを使うので正確なこと、画面外や裏側も反映されること、動く物や動くライトに自然に対応すること、そして ReSTIR などで年々効率が向上していることです。短所は、ノイズが出てデノイズが必須なこと、レイ・デノイズ・加速構造のためコストが高いこと、ハードウェア レイトレース対応の GPU が必要なこと（ソフトウェア方式は品質が劣る）、そして ReSTIR やデノイザの実装が複雑なことです。

### 選ぶときの順番

方式の選択は、技術の新しさでなく、<strong>制約から逆算</strong>して決めます。まず、対象のハードウェアを決めます（PC のみか、コンソールか、モバイルか）。次に、動的な変化がどれだけ必要かを決めます。昼夜サイクルや破壊がなく、光が固定なら、ライトマップとプローブで十分で、最も軽くて高品質です。動的な光が必要でも、変化がゆっくりなら、DDGI のようなプローブの更新で足ります。ジオメトリが大きく変わる、あるいは画面外の光が重要なら、Lumen 的な方式やレイトレ GI が選択肢に入ります。最後に、開発の人手を考えます。ReSTIR やデノイザは、自前で作るには負担が大きく、既存のエンジンや SDK（Unreal、NRD、RTXGI）を使うほうが現実的です。

## よくあるミス

??? failure "最新の手法を選んで、対象機種で動かない"
    **対象のハードウェア**から**逆算して選ぶ**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ハードウェアと予算から、手法を選ぶ**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [GI の比較](../comparison.md)
- [DDGI](../ddgi.md)
