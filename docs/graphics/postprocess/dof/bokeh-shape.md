---
title: Bokeh Shape
tags:
  - 描画
---

# Bokeh Shape

<strong>ボケの「形」</strong>は、写真・映画の「味」を決める大切な要素です。実際のレンズでは、絞りの羽根の枚数でボケの円が多角形になり、レンズの設計で縁が明るかったり、中心が明るかったりします。ゲームの DOF でも、サンプルの配置・重み付けでこの形を作り分けられます。このページでは、円・多角形・ボケの明るさの分布・猫の目（口径食）・サンプル配置・ブルーム的な玉ボケを説明します。

!!! tip "ポイント"
    - ボケの形 ＝ <strong>レンズの絞りの形</strong>。<strong>円・五角形・六角形（羽根の枚数）</strong>。
    - サンプルの配置と重みで形を作る。円盤は螺旋、多角形は辺に沿って配置。
    - ボケの中の明るさ：均一・縁が明るい（リング状）・中心が明るい。レンズの個性。
    - 口径食（猫の目）：画面の端でボケが楕円に欠ける。映画的な味。
    - 明るい点ほど形がはっきり見える。HDR で処理する。
    - 形を凝るほど、サンプル数が増える。コストと相談。

## 形の種類

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="ボケの形">
<text x="20" y="26" class="fig-title">ボケの形：絞り羽根の枚数で決まる</text>
<g fill="#fff7d1" stroke="#f59e0b" stroke-width="3">
<circle cx="110" cy="120" r="56"/>
<polygon points="300,64 354,103 333,166 267,166 246,103"/>
<polygon points="520,64 568,92 568,148 520,176 472,148 472,92"/>
<polygon points="690,64 730,80 750,120 730,160 690,176 650,160 630,120 650,80"/>
</g>
<g font-size="12" text-anchor="middle"><text x="110" y="204">円（羽根が丸い）</text><text x="300" y="204">五角形</text><text x="520" y="204">六角形</text><text x="690" y="204">八角形</text></g>
</svg>

| 形 | 由来 | 見た目 |
| --- | --- | --- |
| 円 | 丸い絞り・多枚羽根 | 滑らか・柔らかい |
| 多角形 | 5〜9 枚の絞り羽根を絞った状態 | 角張った玉ボケ。写真っぽい |
| <strong>ドーナツ（リング）</strong> | 反射望遠レンズ | 中央が欠けた、輪っかのボケ |

## サンプルの配置で形を作る

### 円盤

<strong>ヴォーゲル螺旋</strong>（[Gather Method](gather.md)）がそのまま円盤を作ります。

### 多角形

円盤を多角形の領域に押し込む関数でサンプルを写します。

```hlsl
float2 MapDiskToPolygon(float2 p, int sides, float rotation) {
  float r = length(p);
  float angle = atan2(p.y, p.x);
  float sector = 6.28318530718 / sides;
  float local = fmod(angle - rotation + sector * 100.0, sector) - sector * 0.5;
  float polygon_radius = cos(sector * 0.5) / cos(local);
  return p * polygon_radius;
}
```

| 点 | 説明 |
| --- | --- |
| `sides` | 羽根の枚数（5〜9） |
| `rotation` | 多角形の向き |
| `cos(半角) / cos(局所角)` | 円の半径を多角形の辺までの距離に置き換える |
| サンプルをこの関数で円盤から多角形に写す | ギャザーのサンプル位置として使う |

## ボケの中の明るさ

<strong>実際のレンズ</strong>では、ボケの円盤の内側が均一ではありません。

| 明るさの分布 | レンズの性質 | 見た目 |
| --- | --- | --- |
| 均一 | 理想的な絞り | 平らな円盤 |
| 縁が明るい | 球面収差の補正不足（古い・安いレンズ） | 縁取りのある玉ボケ。ソープ バブル風 |
| 中心が明るい | 球面収差の過剰補正 | 柔らかい、なだらかなボケ |

サンプルの重みに円の中心からの距離を反映すると、この分布を作れます。

```hlsl
float BokehWeight(float2 sample_offset, float edge_boost) {
  float r = length(sample_offset);
  return lerp(1.0, 1.0 + edge_boost, smoothstep(0.6, 1.0, r));
}
```

`edge_boost` の値による見た目です。0 なら均一な円盤です。正の値なら縁が明るくなります（ソープ バブル）。負の値なら中心が明るくなります。

<!-- fig:bokeh-shapes-anim:begin -->

<svg class="fig illust motion" data-fig="bokeh-shapes-anim" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bokeh-shapes-anim" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ボケの形: 絞りの羽根の枚数が、点の光のぼけの形になる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">15×15 画素の点光源のぼけ。羽根 5・6・8 枚と、円(羽根が多い)を、実際に計算して並べる</text>
<rect x="30" y="110" width="231.0" height="231.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">羽根 5 枚</text>
<rect x="33.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="108.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="123.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="138.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="153.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="168.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="183.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="198.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="108.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="123.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="138.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="153.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="168.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="183.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="198.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="108.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="123.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="138.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="198.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="93.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="213.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="93.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="213.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="93.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="213.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="228.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="93.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="213.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="228.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="243.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="93.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="213.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="228.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="93.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="213.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="93.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="213.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="108.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="123.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="138.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="198.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="108.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="123.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="138.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#fde68a"/></rect>
<rect x="153.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#fde68a"/></rect>
<rect x="168.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#fde68a"/></rect>
<rect x="183.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="198.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="108.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="123.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="138.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="153.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="168.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="183.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="198.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="33.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="48.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="63.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="78.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="93.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="108.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="123.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="138.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="153.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="168.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="183.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="198.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="213.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="228.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="243.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1161;0.1163;1.0000" values="0;0;1;1"/><text x="30" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光の当たる画素 94 個</text>
<text x="30" y="392" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">角が 5 つ。羽根の数が少ない</text>
</g>
<rect x="255" y="110" width="231.0" height="231.0" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="255" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">羽根 6 枚</text>
<rect x="258.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="333.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="348.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="363.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="378.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="393.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="408.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="423.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="333.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="348.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="363.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="378.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="393.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="408.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="423.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2577" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2577" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="318.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="438.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="303.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="318.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="438.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="453.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="303.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="318.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2479" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="438.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="453.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="288.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="303.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="318.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2479" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2465" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2479" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="438.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="453.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="468.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="303.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="318.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2479" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="438.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="453.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="303.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="318.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2493" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="438.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="453.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="318.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2507" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="438.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2521" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2577" values="#0f172a;#fde68a"/></rect>
<rect x="333.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="348.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="363.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2535" values="#0f172a;#fde68a"/></rect>
<rect x="378.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2549" values="#0f172a;#fde68a"/></rect>
<rect x="393.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2563" values="#0f172a;#fde68a"/></rect>
<rect x="408.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2577" values="#0f172a;#fde68a"/></rect>
<rect x="423.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="333.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="348.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="363.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="378.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="393.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="408.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="423.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="258.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="273.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="288.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="303.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="318.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="333.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="348.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="363.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="378.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="393.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="408.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="423.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="438.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="453.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="468.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2928;0.2930;1.0000" values="0;0;1;1"/><text x="255" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光の当たる画素 103 個</text>
<text x="255" y="392" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">六角形</text>
</g>
<rect x="480" y="110" width="231.0" height="231.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="480" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">羽根 8 枚</text>
<rect x="483.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="543.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="558.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="573.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="588.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="603.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="618.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="633.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="648.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="663.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="543.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="558.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="573.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="588.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="618.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="633.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="648.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="663.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="543.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="558.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="648.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="663.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4344" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4344" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="528.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="678.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="528.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4247" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="678.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="513.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="528.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4247" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4247" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="678.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="693.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="528.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4247" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="678.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="528.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="678.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4274" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4344" values="#0f172a;#fde68a"/></rect>
<rect x="543.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="558.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="648.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4344" values="#0f172a;#fde68a"/></rect>
<rect x="663.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="543.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="558.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="573.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="588.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="618.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4330" values="#0f172a;#fde68a"/></rect>
<rect x="633.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="648.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="663.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="543.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="558.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="573.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="588.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#0f172a;#fde68a"/></rect>
<rect x="603.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="618.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="633.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="648.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="663.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="483.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="498.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="513.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="528.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="543.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="558.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="573.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="588.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="603.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="618.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="633.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="648.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="663.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="678.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="693.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4696;0.4698;1.0000" values="0;0;1;1"/><text x="480" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光の当たる画素 105 個</text>
<text x="480" y="392" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">八角形。丸に近い</text>
</g>
<rect x="705" y="110" width="231.0" height="231.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="705" y="100" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">円(羽根が多い・丸い絞り)</text>
<rect x="708.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="768.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="783.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="798.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="813.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="828.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="843.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="858.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="873.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="888.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="113.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="768.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="783.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="798.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="858.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="873.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="888.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="128.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="768.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="888.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="143.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="158.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="753.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="903.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="173.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="753.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="903.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="188.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="738.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="753.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6014" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="903.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="918.0" y="203.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="738.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="753.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6014" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6000" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6014" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="903.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="918.0" y="218.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="738.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="753.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6014" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="903.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="918.0" y="233.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="753.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6028" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="903.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="248.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="753.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6042" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="903.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="263.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="768.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6056" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="888.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="278.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="768.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="783.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="798.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6070" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="858.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6112" values="#0f172a;#fde68a"/></rect>
<rect x="873.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="888.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="293.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="768.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="783.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="798.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="813.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6084" values="#0f172a;#fde68a"/></rect>
<rect x="828.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6098" values="#0f172a;#fde68a"/></rect>
<rect x="843.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="858.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="873.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="888.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="308.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="708.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="723.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="738.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="753.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="768.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="783.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="798.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="813.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="828.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="843.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="858.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="873.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="888.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="903.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<rect x="918.0" y="323.0" width="15.3" height="15.3" fill="#0f172a"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6463;0.6465;1.0000" values="0;0;1;1"/><text x="705" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光の当たる画素 121 個</text>
<text x="705" y="392" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">丸い(理想)</text>
</g>
<rect x="30" y="420" width="900" height="60" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="410" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">夜景の光点 5 つを、羽根 6 枚のボケで描くと(1 列に簡略)</text>
<rect x="44.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="58.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="72.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8037" values="#0f172a;#6b674f"/></rect>
<rect x="86.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8056" values="#0f172a;#6b674f"/></rect>
<rect x="100.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8074" values="#0f172a;#6b674f"/></rect>
<rect x="114.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8093" values="#0f172a;#6b674f"/></rect>
<rect x="128.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8112" values="#0f172a;#6b674f"/></rect>
<rect x="142.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8130" values="#0f172a;#6b674f"/></rect>
<rect x="156.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8149" values="#0f172a;#6b674f"/></rect>
<rect x="170.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8167" values="#0f172a;#6b674f"/></rect>
<rect x="184.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8186" values="#0f172a;#6b674f"/></rect>
<rect x="198.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8205" values="#0f172a;#6b674f"/></rect>
<rect x="212.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8223" values="#0f172a;#6b674f"/></rect>
<rect x="226.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8242" values="#0f172a;#ab9e69"/></rect>
<rect x="240.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8260" values="#0f172a;#ab9e69"/></rect>
<rect x="254.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8279" values="#0f172a;#4f4f44"/></rect>
<rect x="268.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8298" values="#0f172a;#4f4f44"/></rect>
<rect x="282.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8316" values="#0f172a;#4f4f44"/></rect>
<rect x="296.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8335" values="#0f172a;#4f4f44"/></rect>
<rect x="310.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8353" values="#0f172a;#4f4f44"/></rect>
<rect x="324.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8372" values="#0f172a;#4f4f44"/></rect>
<rect x="338.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8391" values="#0f172a;#4f4f44"/></rect>
<rect x="352.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8409" values="#0f172a;#4f4f44"/></rect>
<rect x="366.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8428" values="#0f172a;#4f4f44"/></rect>
<rect x="380.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8447" values="#0f172a;#4f4f44"/></rect>
<rect x="394.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8465" values="#0f172a;#4f4f44"/></rect>
<rect x="408.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="422.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8502" values="#0f172a;#6b674f"/></rect>
<rect x="436.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8521" values="#0f172a;#6b674f"/></rect>
<rect x="450.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8540" values="#0f172a;#6b674f"/></rect>
<rect x="464.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8558" values="#0f172a;#6b674f"/></rect>
<rect x="478.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8577" values="#0f172a;#6b674f"/></rect>
<rect x="492.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8595" values="#0f172a;#6b674f"/></rect>
<rect x="506.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8614" values="#0f172a;#6b674f"/></rect>
<rect x="520.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8633" values="#0f172a;#988e61"/></rect>
<rect x="534.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8651" values="#0f172a;#988e61"/></rect>
<rect x="548.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8670" values="#0f172a;#988e61"/></rect>
<rect x="562.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8688" values="#0f172a;#988e61"/></rect>
<rect x="576.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8707" values="#0f172a;#988e61"/></rect>
<rect x="590.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8726" values="#0f172a;#988e61"/></rect>
<rect x="604.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8744" values="#0f172a;#3d3f3c"/></rect>
<rect x="618.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8763" values="#0f172a;#3d3f3c"/></rect>
<rect x="632.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8781" values="#0f172a;#3d3f3c"/></rect>
<rect x="646.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8800" values="#0f172a;#3d3f3c"/></rect>
<rect x="660.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8819" values="#0f172a;#3d3f3c"/></rect>
<rect x="674.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8837" values="#0f172a;#3d3f3c"/></rect>
<rect x="688.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8856" values="#0f172a;#867e5a"/></rect>
<rect x="702.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8874" values="#0f172a;#585748"/></rect>
<rect x="716.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8893" values="#0f172a;#585748"/></rect>
<rect x="730.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8912" values="#0f172a;#585748"/></rect>
<rect x="744.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8930" values="#0f172a;#585748"/></rect>
<rect x="758.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8949" values="#0f172a;#585748"/></rect>
<rect x="772.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8967" values="#0f172a;#585748"/></rect>
<rect x="786.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8986" values="#0f172a;#585748"/></rect>
<rect x="800.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.9005" values="#0f172a;#585748"/></rect>
<rect x="814.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.9023" values="#0f172a;#585748"/></rect>
<rect x="828.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.9042" values="#0f172a;#585748"/></rect>
<rect x="842.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.9060" values="#0f172a;#585748"/></rect>
<rect x="856.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.9079" values="#0f172a;#585748"/></rect>
<rect x="870.0" y="440.0" width="14.3" height="14.3" fill="#0f172a"/>
<rect x="44" y="440" width="840.0" height="14.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">本物のカメラの絞りは、羽根を重ねた多角形<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">点の光は、その多角形の形のまま、ぼける<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.7998;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ゲームでは、フィルターの形を変えるだけで、カメラの個性(五角形・円形)が出せる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7998;0.8000;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bokeh-shapes-anim:end -->

## 口径食（猫の目ボケ）

<strong>画面の端</strong>ではレンズの筒の影響でボケが丸くなく、楕円形（猫の目）に欠けることがあります。映画的な味として人気があります。

猫の目ボケの作り方です。画面中心からの距離に応じて、円を欠きます。端のサンプルを、画面中心に向かってずらしたもう 1 つの円との交差領域に限定します。欠けた円の向きは、画面中心の方向に揃います。

```hlsl
float2 ApplyCatEye(float2 offset_in_disk, float2 screen_uv, float strength) {
  float2 from_center = screen_uv - 0.5;
  float distance_from_center = length(from_center);
  float2 axis = from_center / max(distance_from_center, 1e-4);
  float shift = distance_from_center * strength;
  float2 other_center = axis * shift;
  bool inside_other = length(offset_in_disk - other_center) <= 1.0;
  return inside_other ? offset_in_disk : float2(10000.0, 10000.0);
}
```

欠けたサンプルは使わず（重み 0 に）、残りのサンプル数で割り直す必要があります。

## 玉ボケをブルームと兼ねる

<strong>明るい点が大きなボケの円盤になる</strong>ので、ブルームと DOF の見た目は近いです。重複して、ぼけすぎないよう：

明るい点が大きなボケの円盤になるので、ブルームと DOF の見た目は近くなります。重複してぼけすぎないための工夫です。DOF の後にブルームをかけて、DOF でぼけた玉ボケをさらに柔らかくします。ブルームのしきい値を調整します（DOF で広がって薄くなった光は、しきい値を超えにくいため）。スキャッター方式なら、面積で割りつつ HDR の明るさを残して、玉ボケの明るさを保ちます。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 形をパラメータにする | 羽根の枚数・回転・縁の明るさ・猫の目の強さをスライダーに |
| サンプル配置を事前計算 | 多角形・形ごとにサンプルを事前に作り、定数バッファへ |
| ブルー ノイズで回転 | 少ないサンプルで滑らかに |
| ボケの小さい所は円で十分 | 形が見えるのは、大きな明るいボケだけ。そこだけ凝る |
| スキャッターで形を正確に | 玉ボケの形を重視するなら、スプライトに形のテクスチャを貼る（[Scatter Method](scatter.md)） |

## よくあるミス

??? failure "多角形のボケにしたら、サンプルが偏って、片側が薄い"
    <strong>サンプルを多角形の中に均等に</strong>配置する。重みをサンプル数で正規化。

??? failure "猫の目で欠けたサンプルを使い続け、暗くなる"
    欠けたサンプルの重みを 0 に、合計の重みで割る。

??? failure "ボケの形が、小さい画素ではまったく見えない"
    形が見えるのは、大きなボケだけ。小さいボケは円で十分。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボケの形 ＝ <strong>絞りの形</strong>。円・多角形（羽根の枚数）
    - [x] サンプルの配置・重みで形と明るさの分布を作る
    - [x] 縁が明るい・中心が明るいなどレンズの個性
    - [x] 猫の目（口径食）は画面の端でボケが楕円に欠ける
    - [x] 形はパラメータ化し、大きなボケだけ凝る

## 参考

- McIntosh et al., "Efficiently Simulating the Bokeh of Polygonal Apertures in a Post-Process Depth of Field Shader"（Computer Graphics Forum 2012）
- Abadie, "A Life of a Bokeh"（SIGGRAPH 2018）
- Wikipedia, "Bokeh"

## 関連ページ

- [Depth of Field (DOF)](index.md)
- [Gather Method](gather.md)
- [Scatter Method](scatter.md)
- [Bloom](../bloom/index.md)
