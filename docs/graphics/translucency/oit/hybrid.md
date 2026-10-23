---
title: Hybrid Approaches and Choosing
tags:
  - 描画
---

# Hybrid Approaches and Choosing

<strong>OIT の方式は用途によって向き不向きがあります</strong>。近くの重要な半透明は正確な方式、遠くの煙や粒子は軽い方式、というように組み合わせることも多いです。このページではハイブリッド構成と方式の選び方を説明します。

!!! tip "ポイント"
    - 重要な半透明（ガラス・水）は、ソート ＋ 正確な方式。
    - 煙・粒子は WBOIT。
    - ハードウェアや予算で、選択が変わる。
    - ほとんどのゲームはソート ＋ WBOIT で十分。

!!! info "このページを読む前に"
    - [Order-Independent Transparency (OIT)](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ハイブリッド
<strong>実用では正確な方式と軽い方式を組み合わせ</strong>ます。

ハイブリッドの方式は 3 つです。上位 N 層だけ正確にする方法は手前の数層を PPLL か Peeling で正確に扱い、残りを Weighted Blended で処理します。重要な物だけ OIT にする方法はガラスや髪などは OIT にして、パーティクルは加算ブレンド（順序不要）にします。距離で切り替える方法は近くは正確に遠くは近似にします。

## 方式の選び方
| 状況 | おすすめ |
| --- | --- |
| パーティクルが大量・加算で済む | <strong>加算ブレンド（OIT 不要）</strong> |
| ガラス・水が少数 | ソート ＋ 2 パス（前面・背面） |
| 髪・草など細かい重なり | ハッシュド アルファ ＋ TAA・Weighted Blended |
| 精度が重要（CAD・可視化） | PPLL・Depth Peeling |
| ゲームで広く使える軽い OIT | Weighted Blended OIT |

## 方式の一覧（比べる）

| 方式 | 正確さ | パス数 | メモリ | 速さ | 向く対象 |
| --- | --- | --- | --- | --- | --- |
| ソート + アルファ ブレンド | 物体単位で正確。物体内、交差は不正確 | 1 | 小 | 速い | 少数のガラス、パーティクル |
| デプス ピーリング | 正確 | 層の数 | 中（層ごとにターゲット） | 遅い | 重要な、少数の物 |
| PPLL | 正確（上限まで） | 2（構築 + 解決） | 大（バッファ） | 中 | 重なりが多く、正確さが必要 |
| WBOIT | 近似 | 2（描画 + 合成） | 小（2 枚） | 速い | 煙、霧、パーティクル（色が近い） |
| 確率的透明 | 期待値は正しい | 1 | 中（MSAA） | 速い | TAA ありの髪、葉 |
| アルファ テスト系 | 縁を切り抜く | 1 | 小 | 速い | 葉、草、柵 |

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

<strong>1 つの方式だけ</strong>ですべてをまかなうのは 難しいです。物の種類で使い分けます。

| 物 | 方式 |
| --- | --- |
| 窓ガラス、車の窓（重要で数が少ない） | ソート + アルファ ブレンド（または、デプス ピーリング） |
| 煙、霧、魔法のパーティクル | WBOIT（別のレンダー ターゲットに描いて最後に、合成） |
| 木の葉、草 | アルファ テスト（A2C、ハッシュ） |
| 髪の毛 | ハッシュ アルファ + TAA、または PPLL で手前の数層（[Hair Transparency](../../skin-hair/hair/transparency.md)） |
| 水面 | 専用の水のシェーダー（[Water](../../water/index.md)） |

### 描画の順番

```text
① 不透明（深度を書く）
② アルファ テスト系（葉、草、柵）
③ 水
④ ソートした、半透明（ガラス）
⑤ WBOIT の、パーティクル（別ターゲットに、描いて、合成）
⑥ ポストプロセス
```

各方式の結果を順に画面に重ねるので、方式の間の前後関係は描く順番で、決まります。ガラスの向こうの煙はガラスより先に描く必要があります。1 つの場面に混ざる場合は全体の順番を設計します。

## 手前だけ正確に

<strong>画面の手前の数層</strong>は 見た目の影響が、大きく、奥の層は小さい。この性質を使ったハイブリッドが、あります。

| 層 | 方式 |
| --- | --- |
| 手前の数層（たとえば 4 層） | 正確（PPLL やデプス ピーリング） |
| 奥の残り | 近似（WBOIT で、まとめて 1 つの層に） |

Salvi らの 適応的な透明度（Adaptive Transparency、2011）や マルチレイヤー アルファ ブレンド（2014）は、少数の層で近似する考え方です。メモリを固定できます（PPLL のように溢れない）。

## 実装の現実

| 項目 | 内容 |
| --- | --- |
| まず、測る | 半透明のオーバードローが実際に何層なのか。問題が起きていないなら単純な方式で、十分 |
| まず、単純な方式から | ソート + アルファ ブレンドで問題が出たら、その部分だけ他の方式に |
| 品質設定 | PPLL や WBOIT の層の数、解像度を設定で変えられるようにしておく |
| 対応環境 | PPLL は UAV をピクセル シェーダーで、書ける必要がある（DX11 の機能レベル 11_0 以上） |

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
