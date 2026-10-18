---
title: TAA・アップスケーラ・VRS
tags:
  - 最適化
  - 3Dゲーム
---

# TAA・アップスケーラ・VRS

ピクセル処理が重いとき、最も直接的な解決策は**ピクセルの数を減らす**ことです。しかし、単に解像度を下げると画面がぼやけます。**TAA（時間的アンチエイリアシング）・アップスケーラ・VRS**は見た目の品質をなるべく保ちながら、実際に計算するピクセルを減らす手法です。このページでは、それぞれの仕組みと注意点を説明します。

!!! tip "ポイント"
    - 目的は<strong>ピクセルシェーダーの計算量を減らす</strong>こと。
    - <strong>TAA</strong>は過去のフレームを混ぜて、ギザギザとノイズを減らす。
    - <strong>アップスケーラ</strong>（DLSS・FSR・TAAU）は、低解像度で描いて、時間情報も使って高解像度にする。
    - <strong>VRS</strong>は画面の場所ごとにシェーディングの細かさを変える（DX12 Ultimate）。
    - 動きベクトルの精度が品質を決める。<strong>ゴースト（残像）</strong>に注意。
    - <strong>動的解像度</strong>と組み合わせて、フレーム時間を一定に保つ。

## TAA（時間的アンチエイリアシング）

### 仕組み

MSAA は、1 フレームの中でサンプルを増やします。TAA は**複数のフレームにまたがってサンプルを集めます**。

| 手順 | 内容 |
| --- | --- |
| **① ジッター** | 毎フレーム、投影行列をサブピクセル単位でずらす（Halton 列など） |
| **② 描画** | 通常どおり描く。フレームごとに少しずつ違う位置をサンプルする |
| **③ 履歴の再投影** | 動きベクトルで前フレームの同じ点を探す |
| **④ 混ぜる** | 現在の色と履歴を混ぜる（履歴を 90% など） |
| **⑤ 履歴の検証** | 履歴が古い・不正なら、混ぜる量を減らす（クランプ） |

### 何が改善するのか

| 改善 | 説明 |
| --- | --- |
| **エッジの滑らかさ** | 数フレーム分のサンプルが混ざるので、MSAA より品質が高い |
| **Deferred と相性が良い** | MSAA は G-Buffer が重くなるが、TAA は後処理で済む |
| **ノイズの平均化** | AO・SSR・影のサンプル数を減らしても、時間で平均されて滑らかになる |
| **鏡面のちらつき** | 細かいハイライトが安定する |

### 注意点

| 問題 | 対策 |
| --- | --- |
| <strong>ゴースト（残像）</strong> | 速く動く物の履歴を捨てる。速度と深度の差で検出する |
| **ぼやけ** | 混ぜすぎない。シャープ処理を後で足す |
| **動きベクトル** | スキニング・頂点アニメ・パーティクルの動きも正しく出力する |
| **透明物** | 深度がないので履歴が不正になりやすい。TAA の後に描く |
| **画面外から入る部分** | 履歴がないので混ぜる量を減らす |

## アップスケーラ

**低い解像度で描いて、高い解像度に拡大**します。単純な拡大と違い、TAA と同じく**過去のフレームの情報**を使うので、細部をある程度復元できます。

| 方式 | 仕組み |
| --- | --- |
| **TAAU** | TAA の延長。低解像度のジッター付きサンプルを、高解像度に蓄積する |
| <strong>FSR（AMD）</strong> | 空間・時間情報を使うアルゴリズム。ほぼ全ての GPU で動く |
| <strong>DLSS（NVIDIA）</strong> | ニューラルネットワークで復元する。専用ハードウェア（Tensor コア）を使う |
| <strong>XeSS（Intel）</strong> | 同様の機械学習ベース |

| 設定 | 内部解像度（出力 4K の場合） | 負荷の目安 |
| --- | --- | --- |
| **品質** | 約 67%（2560×1440） | 約 45% |
| **バランス** | 約 58% | 約 34% |
| **パフォーマンス** | 50%（1920×1080） | 25% |

内部解像度に比例して、ピクセルシェーダーとレンダーターゲットの帯域が減ります。ただし、UI は出力解像度で描きます。

## 動的解像度

負荷に応じて、**描画解像度をフレームごとに変える**方法です。

| 点 | 説明 |
| --- | --- |
| **目的** | フレーム時間を一定に保つ（重い場面で少し解像度を下げる） |
| **制御** | 直近の GPU 時間から、次のフレームの解像度を決める |
| **UI** | 出力解像度のまま（ぼやけさせない） |
| **ポストプロセス** | 低解像度で描いた結果を、最後に拡大する |

## VRS（可変レート シェーディング）

画面の全ピクセルで同じ細かさでシェーダーを実行するのは、無駄なことがあります。**VRS**は**場所ごとにシェーディングのレートを変えます**（例：2×2 ピクセルを 1 回の計算で）。

| 方式 | 説明 |
| --- | --- |
| **ドロー コールごと** | 物体単位でレートを指定（遠景・暗い物体） |
| **画像ベース** | 画面上のタイルごとにレートを書いた画像を渡す |
| **向く場所** | 暗い領域・動きが速い領域・周辺視野（VR のフォービエイテッド） |
| **対応** | DX12 Ultimate（Tier 1 / 2）。DX11 では使えない |

エッジやハイライトのある場所は、細かいレートのまま残し、平坦な場所だけを粗くするのがコツです。

<!-- fig:halton-jitter:begin -->

<svg class="fig illust motion" data-fig="halton-jitter" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-halton-jitter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">TAA のジッター: フレームごとに、1 画素の中の別の位置で描く(Halton 2,3)</text>
<rect x="240" y="90" width="300" height="300" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<line x1="390.0" y1="90" x2="390.0" y2="390" stroke="#e2e8f0" stroke-width="1"/>
<line x1="240" y1="240.0" x2="540" y2="240.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="240" y="80" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">1 画素の内側（正方形）。点 = そのフレームのサンプル位置</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><circle cx="390.0" cy="290.0" r="9" fill="#2563eb" opacity="0.9"/>
<text x="390.0" y="294.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/><circle cx="315.0" cy="190.0" r="9" fill="#2ea043" opacity="0.9"/>
<text x="315.0" y="194.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2516;0.2519;1.0000" values="0;0;1;1"/><circle cx="465.0" cy="356.66666666666663" r="9" fill="#e5aa28" opacity="0.9"/>
<text x="465.0" y="360.66666666666663" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">3</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3404;0.3407;1.0000" values="0;0;1;1"/><circle cx="277.5" cy="256.6666666666667" r="9" fill="#e5484d" opacity="0.9"/>
<text x="277.5" y="260.6666666666667" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/><circle cx="427.5" cy="156.66666666666669" r="9" fill="#7c3aed" opacity="0.9"/>
<text x="427.5" y="160.66666666666669" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;1.0000" values="0;0;1;1"/><circle cx="352.5" cy="323.33333333333337" r="9" fill="#2563eb" opacity="0.9"/>
<text x="352.5" y="327.33333333333337" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">6</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6071;0.6074;1.0000" values="0;0;1;1"/><circle cx="502.5" cy="223.33333333333331" r="9" fill="#2ea043" opacity="0.9"/>
<text x="502.5" y="227.33333333333331" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">7</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6960;0.6963;1.0000" values="0;0;1;1"/><circle cx="258.75" cy="123.33333333333334" r="9" fill="#e5aa28" opacity="0.9"/>
<text x="258.75" y="127.33333333333334" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">8</text>
</g>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">毎フレーム、カメラをほんの少し(1 画素以内)ずらす<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1〜4 フレーム目: 離れた位置を順に使う<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3701;0.3704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8 フレームで、画素の中をまんべんなく巡る。これを平均して高精細にする<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:halton-jitter:end -->

## よくあるミス

??? failure "動きベクトルを出さずに TAA を入れて、ゴーストが出る"
    動く物・スキニングの動きベクトルを、必ず出力します。

??? failure "TAA を入れて、全体がぼやける"
    混ぜる量とシャープ処理を調整します。

??? failure "UI まで低解像度で描いて、文字がぼやける"
    UI は出力解像度で描きます。

??? failure "透明物を TAA の前に描いて、ゴーストが出る"
    TAA の後に描く、または専用のマスクを使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>TAA</strong> は、過去のフレームを混ぜて品質を上げる。<strong>動きベクトルが肝</strong>
    - [x] <strong>アップスケーラ</strong>は、低解像度で描いて高解像度へ。<strong>負荷は内部解像度に比例</strong>
    - [x] <strong>動的解像度</strong>で、フレーム時間を一定に
    - [x] <strong>VRS</strong> は、場所ごとにシェーディングを粗く（DX12 Ultimate）
    - [x] UI とポストの順序に注意

## 関連ページ

- [描画最適化](index.md)
- [低解像度のエフェクト](low-res-effects.md)
- [フレーム時間の設計](../optimize/frame-budget.md)
- [ポストプロセス](postprocess.md)
