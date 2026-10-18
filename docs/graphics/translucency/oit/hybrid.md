---
title: Hybrid Approaches and Choosing
tags:
  - 描画
---

# Hybrid Approaches and Choosing

<strong>OIT の方式は、用途によって向き不向きがあります</strong>。<strong>近くの重要な半透明は正確な方式、遠くの煙や粒子は軽い方式</strong>、というように、組み合わせることも多いです。このページでは、ハイブリッド構成と、方式の選び方を説明します。

!!! tip "ポイント"
    - 重要な半透明（ガラス・水）は、ソート ＋ 正確な方式。
    - 煙・粒子は、WBOIT。
    - ハードウェアや予算で、選択が変わる。
    - ほとんどのゲームは、ソート ＋ WBOIT で十分。

## ハイブリッド
<strong>実用では、正確な方式と、軽い方式を、組み合わせ</strong>ます。

ハイブリッドの方式は 3 つです。上位 N 層だけ正確にする方法は、手前の数層を PPLL か Peeling で正確に扱い、残りを Weighted Blended で処理します。重要な物だけ OIT にする方法は、ガラスや髪などは OIT にして、パーティクルは加算ブレンド（順序不要）にします。距離で切り替える方法は、近くは正確に、遠くは近似にします。

## 方式の選び方
| 状況 | おすすめ |
| --- | --- |
| パーティクルが大量・加算で済む | <strong>加算ブレンド（OIT 不要）</strong> |
| ガラス・水が少数 | <strong>ソート ＋ 2 パス（前面・背面）</strong> |
| 髪・草など、細かい重なり | ハッシュド アルファ ＋ TAA・Weighted Blended |
| <strong>精度が重要（CAD・可視化）</strong> | PPLL・Depth Peeling |
| ゲームで、広く使える軽い OIT | Weighted Blended OIT |

## 方式の、一覧（比べる）

| 方式 | 正確さ | パス数 | メモリ | 速さ | 向く対象 |
| --- | --- | --- | --- | --- | --- |
| ソート + アルファ ブレンド | 物体単位で、正確。物体内、交差は、不正確 | 1 | 小 | 速い | 少数の、ガラス、パーティクル |
| デプス ピーリング | 正確 | 層の数 | 中（層ごとに、ターゲット） | 遅い | 重要な、少数の物 |
| PPLL | 正確（上限まで） | 2（構築 + 解決） | 大（バッファ） | 中 | 重なりが、多く、正確さが、必要 |
| WBOIT | 近似 | 2（描画 + 合成） | 小（2 枚） | 速い | 煙、霧、パーティクル（色が、近い） |
| 確率的透明 | 期待値は、正しい | 1 | 中（MSAA） | 速い | TAA ありの、髪、葉 |
| アルファ テスト系 | 縁を、切り抜く | 1 | 小 | 速い | 葉、草、柵 |

## 選び方

```text
半透明の物が、少ない（数個）？
   └ Yes → ソート + アルファ ブレンド（物体内の、問題があれば、裏面 → 表面の 2 パス）
   └ No ↓
重なりが、多い（数十層）？
   ├ 縁を、切り抜く物（葉、草、髪）？ → アルファ テスト系（A2C、ハッシュ アルファ + TAA）
   ├ ぼんやりした、物（煙、霧、パーティクル）？ → WBOIT
   └ 正確さが、必要（ガラス、水中の物）？ → PPLL、または、少数層に、デプス ピーリング
```

## ハイブリッド

<strong>1 つの方式だけ</strong>で、すべてを、まかなうのは、<strong>難しい</strong>です。物の種類で、使い分けます。

| 物 | 方式 |
| --- | --- |
| 窓ガラス、車の窓（重要で、数が少ない） | ソート + アルファ ブレンド（または、デプス ピーリング） |
| 煙、霧、魔法のパーティクル | WBOIT（別のレンダー ターゲットに、描いて、最後に、合成） |
| 木の葉、草 | アルファ テスト（A2C、ハッシュ） |
| 髪の毛 | ハッシュ アルファ + TAA、または、PPLL で、手前の数層（[Hair Transparency](../../skin-hair/hair/transparency.md)） |
| 水面 | 専用の、水のシェーダー（[Water](../../water/index.md)） |

### 描画の順番

```text
① 不透明（深度を書く）
② アルファ テスト系（葉、草、柵）
③ 水
④ ソートした、半透明（ガラス）
⑤ WBOIT の、パーティクル（別ターゲットに、描いて、合成）
⑥ ポストプロセス
```

<strong>各方式の、結果を、順に、画面に、重ねる</strong>ので、<strong>方式の間の、前後関係</strong>は、描く順番で、決まります。ガラスの向こうの、煙は、ガラスより先に、描く必要があります。1 つの、場面に、混ざる場合は、全体の、順番を、設計します。

## 手前だけ、正確に

<strong>画面の、手前の、数層</strong>は、<strong>見た目の影響が、大きく</strong>、奥の層は、小さい。この性質を、使った、ハイブリッドが、あります。

| 層 | 方式 |
| --- | --- |
| 手前の、数層（たとえば、4 層） | 正確（PPLL や、デプス ピーリング） |
| 奥の、残り | 近似（WBOIT で、まとめて、1 つの層に） |

Salvi らの、<strong>適応的な透明度</strong>（Adaptive Transparency、2011）や、<strong>マルチレイヤー アルファ ブレンド</strong>（2014）は、少数の層で、近似する考え方です。メモリを、固定できます（PPLL のように、溢れない）。

## 実装の、現実

| 項目 | 内容 |
| --- | --- |
| まず、測る | 半透明の、オーバードローが、実際に、何層なのか。問題が、起きていないなら、単純な方式で、十分 |
| まず、単純な方式から | ソート + アルファ ブレンドで、問題が、出たら、その部分だけ、他の方式に |
| 品質設定 | PPLL や、WBOIT の、層の数、解像度を、設定で、変えられるように、しておく |
| 対応環境 | PPLL は、UAV をピクセル シェーダーで、書ける必要がある（DX11 の、機能レベル 11_0 以上） |

## よくあるミス

??? failure "すべてを PPLL にして、重くなる"
    <strong>重要な所だけ</strong>正確な方式にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重要度で、方式を使い分ける

## 参考

- Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016
- Salvi, Montgomery, Lefohn, "Adaptive Transparency", High-Performance Graphics 2011
- Salvi, Vaidyanathan, "Multi-Layer Alpha Blending", Symposium on Interactive 3D Graphics and Games 2014
- McGuire, Bavoil, "Weighted Blended Order-Independent Transparency", Journal of Computer Graphics Techniques, Vol. 2, No. 2, 2013
- Münstermann, Krumpen, Klein, Peters, "Moment-Based Order-Independent Transparency", High-Performance Graphics 2018

## 関連ページ

- [OIT](index.md)
- [WBOIT](wboit.md)
- [PPLL](ppll.md)
