---
title: オーバードロー
tags:
  - 最適化
  - 3Dゲーム
---

# オーバードロー

**オーバードロー**は、同じピクセルに何度も色を計算して、書くことです。手前の物体で隠れてしまう、奥の物体のピクセルシェーダーは、結果が捨てられるのでまるごと無駄です。ピクセル処理・帯域幅がボトルネックのときに効きます。このページはオーバードローの何が無駄なのか、Early-Z・Z プリパス・並べ替え、小さな三角形の無駄（quad overdraw） を、説明します。

!!! tip "ポイント"
    - <strong>オーバードロー</strong> ＝ <strong>1 ピクセルに、複数回、ピクセルシェーダーを動かす</strong>。最後に見える、1 回以外は無駄。
    - Early-Z：ピクセルシェーダーの前に、深度テスト。隠れていれば、シェーダーを動かさない（ハードウェアの自動の最適化）。
    - Early-Z が、効く条件：手前から奥の順に描く。`discard`・深度の書き換えがない。
    - Z プリパス：先に深度だけを描き、次に色のパスで隠れた所をシェーダーに通さない。オーバードローがほぼ、1 になる。
    - 半透明はオーバードローが避けられない。パーティクルは、特に重い。
    - 小さな三角形は、2×2 ピクセル単位の実行のため、無駄が大きい（quad overdraw）。

## 何が無駄なのか

<svg class="fig illust" viewBox="0 0 800 260" role="img" aria-label="オーバードローの例">
<text x="20" y="24" class="fig-title">奥から手前の順に描くと、隠れるものも、全部、シェーダーが動く</text>
<rect x="60" y="60" width="200" height="130" fill="rgba(76,139,245,0.4)" stroke="currentColor" stroke-width="2"/><text x="68" y="82" style="font-size:11px">奥：山（シェーダー実行）</text>
<rect x="120" y="100" width="180" height="110" fill="rgba(229,170,40,0.5)" stroke="currentColor" stroke-width="2"/><text x="128" y="122" style="font-size:12px">中：建物（実行）</text>
<rect x="180" y="140" width="160" height="90" fill="rgba(229,72,77,0.5)" stroke="currentColor" stroke-width="2"/><text x="188" y="162" style="font-size:12px">手前：壁（実行）</text>
<text x="400" y="80" style="font-weight:700">重なった所：3 回、計算される</text>
<text x="400" y="104" style="font-size:12px">最後に見えるのは、手前の壁だけ</text>
<text x="400" y="124" style="font-size:12px">奥の 2 回は、結果が捨てられる（無駄）</text>
<text x="400" y="164" style="font-weight:700">対策</text>
<text x="400" y="188" style="font-size:12px">手前から描く（Early-Z が、効く）</text>
<text x="400" y="208" style="font-size:12px">Z プリパス（深度だけ先に）</text>
<text x="400" y="228" style="font-size:12px">カリング（そもそも、描かない）</text>
</svg>

**オーバードロー率**（1 ピクセルあたりの平均実行回数）が、2〜3 倍なら、ピクセル処理が、2〜3 倍の無駄です。可視化ツール（PIX・RenderDoc・エンジンのオーバードロー表示）で、確認できます。

## Early-Z

**GPU は通常、ピクセルシェーダーの「前」に、深度テスト**を行います。すでに手前のものが描かれていれば、シェーダーを動かさずに捨てます。

| 点 | 説明 |
| --- | --- |
| 自動 | 特別なコードは、不要 |
| 描く順番に依存 | 奥から描くと効かない（まだ、深度が書かれていないため） |
| 効かなくなる条件 | シェーダー内の `discard`（クリップ）・`SV_Depth` の書き込み・UAV への書き込み（Early-Z を無効化することがある） |

不透明物を手前から奥へおおまかにソートすると、Early-Z がよく効きます（ドロー コールのソートとの兼ね合い。[ドロー コール](draw-calls.md)）。

## Z プリパス（深度プリパス）

<strong>まず、全不透明物を、「深度だけ」</strong>描き（ピクセルシェーダーなし、非常に軽い）、次に色のパスで深度テストを「等しい（`EQUAL`）」にして、描きます。

| 段階 | 内容 |
| --- | --- |
| ① 深度パス | 頂点シェーダーのみ。深度バッファを完成させる |
| ② 色のパス | 深度が完成済みなので見える面だけ、ピクセルシェーダーが動く（オーバードロー ≒ 1） |

| 利点 | 欠点 |
| --- | --- |
| ピクセルシェーダーが重いとき、大きく減る | ジオメトリを、2 回、処理する（頂点・ドロー コールが増える） |
| Forward+ でほぼ、必須（深度がライト カリングに必要） | 頂点処理が重いとき、逆効果 |
| Deferred の、G-Buffer 書き込みも、減る | |

Tiled / Clustered（[ライトのカリング](light-culling.md)）は、深度を先に使うので、Z プリパスと自然に組み合わさります。

## 半透明のオーバードロー

**半透明**（煙・炎・ガラス・パーティクル）は、奥の物を見せる必要があり、Early-Z で捨てられません。重なった数だけ、計算されます。

| 問題 | 対策 |
| --- | --- |
| 大きな、パーティクルが画面を覆う | 縮小バッファに描く（[縮小バッファの効果](low-res-effects.md)） |
| 枚数が多い | 枚数を減らす・小さくする |
| 透明部分が多い（四角の板に小さな煙） | ポリゴンを形に沿って、切り詰める（トリミングしたメッシュ） |
| シェーダーが重い | 軽いシェーダーを使う（パーティクルは、安く） |

半透明のオーバードローを色で可視化（重なるほど、明るく）すると重い場所が一目で分かります。

## 小さな三角形の無駄（Quad Overdraw）

**GPU はピクセルを、2×2 の、4 ピクセル（クアッド）単位で実行**します（微分＝ミップ選択のため）。三角形が小さいと、4 ピクセルのうち、実際に三角形に入るのは、1〜2 個で残りは捨てられる、無駄な計算です。

| 三角形の大きさ | 無駄 |
| --- | --- |
| 大きい（数十ピクセル） | ほぼ、なし |
| 1〜数ピクセル | 最大 4 倍の無駄（1 ピクセルの三角形でも、4 ピクセル分、実行） |

| 対策 | 説明 |
| --- | --- |
| LOD | 遠い物は三角形を減らす（[カリング](culling.md)） |
| Visibility Buffer | ID パスのシェーダーを、軽く（[Visibility Buffer](visibility-buffer.md)） |
| ソフトウェア ラスタライズ | コンピュートで小さな三角形を直接、描く（Nanite） |
| メッシュの設計 | 細長い三角形を避ける（クアッドを無駄にしやすい） |

## タイル型 GPU（モバイル）

**モバイルのタイル型 GPU**は、タイル内で隠面除去（HSR・TBDR）を行う機種があり、オーバードローのコストが小さいです。ただし、半透明は同じく重い（[メモリ帯域幅](bandwidth.md)）。

<!-- fig:overdraw-order:begin -->

<svg class="fig illust motion" data-fig="overdraw-order" viewBox="0 0 780 480" role="img"><rect x="0" y="0" width="780" height="480" rx="14" fill="#ffffff"/>
<defs><marker id="arr-overdraw-order" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">描く順で、書き込み回数が変わる: 手前から描くと、奥は捨てられる</text>
<text x="70" y="82" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">奥から描く（Z テストなし）</text>
<rect x="150" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="206" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="262" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="318" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="374" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="430" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="486" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="542" y="100" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="176.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="232.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="288.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="344.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="456.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="568.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="176.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="232.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="288.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="344.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="456.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="568.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="176.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="232.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="288.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="344.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="400.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="456.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="512.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="568.0" y="132.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="144" y="174" text-anchor="start" style="font-size:1px;font-weight:700;fill:#64748b"/>
<text x="144" y="174" text-anchor="start" style="font-size:1px;font-weight:700;fill:#64748b"/>
<text x="144" y="174" text-anchor="start" style="font-size:1px;font-weight:700;fill:#64748b"/>
<text x="150" y="178" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">各マス = 1 画素に書き込んだ回数</text>
<text x="70" y="242" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">手前から描く（早期 Z で、奥を捨てる）</text>
<rect x="150" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="206" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="262" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="318" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="374" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="430" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="486" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="542" y="260" width="52" height="52" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="176.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="232.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="288.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="344.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="456.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="568.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="176.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="232.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="288.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="344.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="400.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="456.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="568.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">0<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="176.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="232.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="288.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="344.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="400.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="456.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="512.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="568.0" y="292.0" text-anchor="middle" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000" values="0;0;1;1"/></text>
<text x="144" y="334" text-anchor="start" style="font-size:1px;font-weight:700;fill:#64748b"/>
<text x="144" y="334" text-anchor="start" style="font-size:1px;font-weight:700;fill:#64748b"/>
<text x="144" y="334" text-anchor="start" style="font-size:1px;font-weight:700;fill:#64748b"/>
<text x="150" y="338" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">各マス = 1 画素に書き込んだ回数</text>
<text x="390" y="440" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 枚の四角形が重なる(奥から A, B, C)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="440" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 枚目を描いた<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2578;0.2581;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="440" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 枚目を描いた<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2578;0.2581;0.4514;0.4516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="440" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 枚目まで描くと、書き込みは 16 回 vs 8 回(下は、全画素 1 回)<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4514;0.4516;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:overdraw-order:end -->

## よくあるミス

??? failure "奥から手前へ、不透明物を描いている"
    **Early-Z が効きません**。手前から（おおまかに）描きます。

??? failure "全ての物に、`discard` を使って、Early-Z が無効になる"
    アルファ テストの物だけ、別に、最後に描きます。

??? failure "頂点が、ボトルネックなのに、Z プリパスを入れる"
    頂点処理が、2 倍になり、逆効果です。測ってから。

??? failure "半透明の、パーティクルが画面全体を覆って、重い"
    縮小バッファに描き、枚数を減らします。

??? failure "オーバードローを、見ずにシェーダーだけ、最適化する"
    オーバードロー表示で重い場所を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] オーバードロー ＝ <strong>同じピクセルを、何度も計算する無駄</strong>
    - [x] Early-Z（自動）：手前から描くと効く。`discard`・深度書き換えで無効化
    - [x] Z プリパス：深度だけ先に描き、オーバードロー ≒ 1。頂点処理が増える代償
    - [x] 半透明は、避けられない：縮小バッファ・枚数削減
    - [x] 小さな三角形は、クアッド単位で無駄：LOD・Visibility Buffer・ソフトウェア ラスタライズ

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [何が重いのか](bottlenecks.md)
- [Forward と Deferred](forward-deferred.md)
- [縮小バッファの効果](low-res-effects.md)
- [Visibility Buffer](visibility-buffer.md)
- [深度とカリング](../3d/depth-culling.md)
- [Translucency](../graphics/translucency/index.md)
