---
title: トーンマッピングと露出
tags:
  - 描画
---

# トーンマッピングと露出

**現実の明るさ**は、**暗い部屋の 0.01 から、太陽の 100,000 まで**、**桁違いの幅**があります。**ディスプレイが出せる範囲**は、<strong>0〜1（LDR）</strong>です。**HDR で計算した光**を、**この狭い範囲に収める**のが**トーンマッピング**で、**その前段で「どれだけ明るく撮るか」＝露出**を決めます。このセクションでは、**露出・各トーンマップ曲線・色相の保ち方・自動露出・ガンマ**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - 流れは<strong>露出（倍率）→ トーンマップ（曲線）→ ガンマ（sRGB）</strong>。<strong>順番を変えない</strong>。
    - <strong>露出</strong> ＝ <strong>光の量への倍率</strong>。<strong>EV が 1 増えると 2 倍</strong>。
    - <strong>トーンマップ</strong> ＝ <strong>HDR → 0〜1 への単調な曲線</strong>。<strong>S 字</strong>が<strong>フィルム</strong>に近い。
    - <strong>曲線の選び方</strong>で<strong>画の性格</strong>（眠い・コントラスト強め・中立）が決まる。
    - <strong>色の保ち方</strong>（チャンネルごと / 輝度ベース）で、<strong>明るい色の見え方</strong>が変わる。
    - <strong>自動露出</strong>は、<strong>平均輝度から目標を決め、時間で滑らかに追従</strong>。

## 流れ

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="トーンマップの流れ">
<text x="20" y="26" class="fig-title">HDR のリニア画像が、画面に出るまで</text>
<defs><marker id="tm-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="13">
<rect x="20" y="60" width="140" height="80" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/>
<text x="90" y="92" text-anchor="middle" style="font-weight:700">HDR の絵</text><text x="90" y="114" text-anchor="middle" style="font-size:11px">0〜数万（リニア）</text>
<rect x="210" y="60" width="140" height="80" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<text x="280" y="92" text-anchor="middle" style="font-weight:700">① 露出</text><text x="280" y="114" text-anchor="middle" style="font-size:11px">× 2^(−EV)</text>
<rect x="400" y="60" width="140" height="80" rx="8" fill="#e5484d" fill-opacity="0.18" stroke="#e5484d" stroke-width="2"/>
<text x="470" y="92" text-anchor="middle" style="font-weight:700">② トーンマップ</text><text x="470" y="114" text-anchor="middle" style="font-size:11px">曲線で 0〜1 へ</text>
<rect x="590" y="60" width="170" height="80" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/>
<text x="675" y="92" text-anchor="middle" style="font-weight:700">③ ガンマ（sRGB）</text><text x="675" y="114" text-anchor="middle" style="font-size:11px">画面へ</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="162" y1="100" x2="208" y2="100" marker-end="url(#tm-arrow)"/><line x1="352" y1="100" x2="398" y2="100" marker-end="url(#tm-arrow)"/><line x1="542" y1="100" x2="588" y2="100" marker-end="url(#tm-arrow)"/></g>
<text x="20" y="176" style="font-size:12px">自動露出は、①の倍率を、画面の明るさから毎フレーム決める。</text>
</svg>

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [露出](exposure.md) | EV・絞り／シャッター／ISO・EV100・露出補正 |
| [Reinhard](reinhard.md) | x/(1+x)・白点付き・もっとも簡単な曲線 |
| [フィルミック（Hable）](filmic-hable.md) | S 字・肩とつま先・Uncharted 2 の式 |
| [ACES](aces.md) | 映画業界の標準・近似式・色の偏り |
| [AgX ほか](agx.md) | AgX・Tony McMapface・Khronos PBR Neutral |
| [色相の保ち方](hue-preservation.md) | チャンネルごと / 輝度ベース / ハイブリッド |
| [自動露出](auto-exposure.md) | 平均輝度・ヒストグラム・時間追従 |
| [ガンマと HDR 出力](gamma-srgb.md) | sRGB・リニア空間・HDR10 への出力 |

## 曲線を動かして比べる

**入力の明るさ x を 0 から増やしたとき、各曲線の出力がどう変わるか**を見ます。

<!-- fig:tonemap-curves:begin -->
<!-- fig:tonemap-curves:end -->

| 見る所 | 内容 |
| --- | --- |
| **クランプ** | **1 で急に頭打ち**。**明部が真っ白に潰れる** |
| **Reinhard** | **なだらかだが中間も持ち上がって低コントラスト** |
| **Hable・ACES** | <strong>暗部を締めて、明部を滑らかにロールオフ（S 字）</strong> |

## どれを選ぶか

| 目的 | 選ぶ曲線 |
| --- | --- |
| **とにかく簡単に** | <strong>Reinhard（白点付き）</strong> |
| **映画のような締まった画** | **ACES 近似・Hable** |
| **色が破綻しにくい中立** | **AgX・Khronos PBR Neutral** |
| **画作りを細かく制御** | **独自の曲線を 3D LUT にする**（[カラー グレーディング](../color-grading/index.md)） |

## 関連ページ

- [ポストプロセス](../index.md)
- [ブルーム](../bloom/index.md)
- [カラー グレーディング](../color-grading/index.md)
- [PBR](../../../3d/pbr.md)
