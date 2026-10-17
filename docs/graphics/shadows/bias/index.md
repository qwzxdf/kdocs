---
title: Shadow Bias
tags:
  - 描画
---

# Shadow Bias

**シャドウ マップの深度は、解像度と精度が有限**なので、**そのまま比べると、光が当たっている面が自分自身の影になり、縞模様（シャドウ アクネ）**になります。**これを防ぐのがバイアス**ですが、**大きくしすぎると、影が物から離れて浮いて見えます（ピーター パンニング）**。このセクションでは、**アクネの原因・定数バイアス・スロープ スケール・法線オフセット・受け手平面・前面カリング・ピーター パンニング**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **アクネ ＝ 自分自身に落ちる影**（**縞模様**）。**原因は、深度の離散化と斜めの面**。
    - **対策は 5 つ**：**定数・スロープ・法線オフセット・受け手平面・前面カリング**。
    - **大きくしすぎると、影が浮く（ピーター パンニング）**。
    - **組み合わせて**使い、**シーンごとに調整**する。

<!-- fig:shadow-bias-sweep:begin -->

<svg class="fig illust motion" data-fig="shadow-bias-sweep" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-shadow-bias-sweep" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">バイアスを増やすと:シャドウ アクネ → ちょうどよい → ピーター パンニング</text>
<rect x="50" y="250" width="596" height="44" fill="#d6c7a1"/>
<rect x="60" y="250" width="34" height="30" fill="#fde68a"/>
<rect x="96" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="132" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="168" y="250" width="34" height="30" fill="#fde68a"/>
<rect x="204" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="240" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="276" y="250" width="34" height="30" fill="#fde68a"/>
<rect x="312" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="348" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="384" y="250" width="34" height="30" fill="#fde68a"/>
<rect x="420" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="456" y="250" width="34" height="30" fill="#fde68a"/>
<rect x="492" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="528" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="564" y="250" width="34" height="30" fill="#fde68a"/>
<rect x="600" y="250" width="34" height="30" fill="#fde68a"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296" values="#fde68a;#475569;#475569;#fde68a;#fde68a;#fde68a;#fde68a"/></rect>
<rect x="330" y="160" width="90" height="90" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<rect x="420" y="250" width="150" height="30" fill="#334155" opacity="0.75"><animate attributeName="x" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296;1.0000" values="420;420;420;420;420;492;492;492"/><animate attributeName="width" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296;1.0000" values="150;150;150;150;150;78;78;78"/></rect>
<text x="426" y="242" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d"/>
<rect x="60" y="120" width="640" height="10" rx="5" fill="#e2e8f0"/>
<rect x="60.0" y="114" width="192.0" height="22" rx="4" fill="#e5484d" fill-opacity="0.12"/>
<rect x="252.0" y="114" width="192.0" height="22" rx="4" fill="#2ea043" fill-opacity="0.18"/>
<rect x="444.0" y="114" width="256.0" height="22" rx="4" fill="#e5aa28" fill-opacity="0.18"/>
<text x="156.0" y="106" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">小さすぎ</text>
<text x="348.0" y="106" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">ちょうどよい</text>
<text x="572.0" y="106" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">大きすぎ</text>
<circle cx="60" cy="125" r="11" fill="#2563eb" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.1481;0.3259;0.5333;0.7259;0.8296;1.0000" values="60;60;145.76;145.76;346.4;346.4;680.8;680.8;680.8"/></circle>
<text x="60" y="215" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">地面（光が当たる面）</text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">バイアス 0:自分の影を自分に落とす（縞模様）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;1.0000" values="1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">バイアスを上げると、縞が消えていく…<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1479;0.1481;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">ちょうどよい:縞が消え、影は物の足元から始まる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.5330;0.5333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">さらに上げると、影が物から離れていく…<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5330;0.5333;0.7256;0.7259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">大きすぎ:影が浮く（ピーター パンニング）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7256;0.7259;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="372" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">縞（アクネ）は、深度の比較の誤差が原因。バイアスはその誤差より少しだけ大きくする。<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:shadow-bias-sweep:end -->

## アクネの原因
シャドウ マップの 1 テクセルは、<strong>光から見たとき、面の上の「ある大きさの領域」</strong>に対応しますが**保存される深度は 1 つ**です。**面が斜め**だと**その領域の中で面の本当の深度は、一定ではなく、傾いて**います。

<svg class="fig illust" viewBox="0 0 780 290" role="img" aria-label="アクネの原因">
<text x="20" y="24" class="fig-title">1 テクセルの深度は 1 つ。斜めの面では、面の本当の深度が、テクセルの中でずれる</text>
<line x1="60" y1="240" x2="720" y2="70" stroke="currentColor" stroke-width="4"/><text x="560" y="66" style="font-size:12px">斜めの面（光に対して傾いている）</text>
<g stroke="currentColor" stroke-width="1"><line x1="140" y1="240" x2="140" y2="40" stroke-dasharray="3 3"/><line x1="260" y1="240" x2="260" y2="40" stroke-dasharray="3 3"/><line x1="380" y1="240" x2="380" y2="40" stroke-dasharray="3 3"/><line x1="500" y1="240" x2="500" y2="40" stroke-dasharray="3 3"/><line x1="620" y1="240" x2="620" y2="40" stroke-dasharray="3 3"/></g>
<text x="165" y="262" style="font-size:12px">テクセル</text>
<g stroke="#e5484d" stroke-width="3"><line x1="140" y1="212" x2="260" y2="212"/><line x1="260" y1="182" x2="380" y2="182"/><line x1="380" y1="152" x2="500" y2="152"/></g>
<text x="396" y="144" style="font-size:12px;fill:#e5484d;font-weight:700">保存される深度（テクセルの代表値）</text>
<circle cx="320" cy="168" r="6" fill="currentColor"/><text x="326" y="164" style="font-size:12px">面の点（本当の深度）</text>
<text x="40" y="280" style="font-size:12px">点が、保存された深度より奥（図では下）にある所が出る → 自分自身に遮られたと誤判定 → 縞（アクネ）</text>
</svg>

テクセルの代表深度より、**面の点の方が奥**にある場所（上の図でテクセルの下側）では<strong>「自分より手前に何かある」</strong>と誤判定されて、**影になります**。これが<strong>縞模様（アクネ）</strong>です。

### ずれの大きさ

**1 テクセルのワールドでの大きさ**を `s`、**光の向きと面の法線のなす角**を `θ` とします。**面が傾いている**ほど、テクセルの中での深度のずれが大きくなります。

<div class="formula">深度のずれ ≈ s · tan θ　（θ：法線と光の向きのなす角）</div>

具体例です。光が真上から当たる（θ = 0°）と、tan θ は 0 で、ずれはほぼありません。θ = 45° では tan θ が 1 で、ずれは s と同じです。ほぼ水平（θ = 80°）では tan θ が約 5.7 になり、ずれは s の 5.7 倍に達して、アクネが激しく出ます。

**斜めの面ほど、大きなバイアスが要る**ことが分かります。**一定のバイアス**では、**斜めの面に足りません**。

## 組み合わせの設計
バイアスは、目的ごとに組み合わせを選びます。平らな面のアクネを防ぐには、スロープ スケールに小さな定数を足します。斜めの面や曲面のアクネには、法線オフセットが効きます。PCF で広くぼかす場合は、サンプルごとの補正になる受け手平面バイアスを使います。閉じた厚い物体では、裏面レンダリングを併用できます。ピーター パンニングを抑えるには、各バイアスを最小限にして、調整を明るい光・斜めの光で確認します。

## 調整の手順
調整の手順は 6 段階です。最初に、光を低い角度（斜め）にして、平らな面と曲面でアクネが出る状態を作ります。次に、スロープ スケールから足し、アクネが消える最小の値を探します。3 番目に、法線オフセットを足して、曲面や角に残ったアクネを消します。4 番目に、ピーター パンニングを確認し、物体の接地部で影が離れていないかを見ます。5 番目に、光の角度を変えて、すべての角度で破綻しないかを再確認します。最後に、カスケードごとに調整します。解像度（テクセルの大きさ）が違うので、カスケードごとにバイアスを変える必要があります。

**テクセルの大きさに比例**するように、**ワールド単位で**バイアスを決めると、**解像度・カスケードを変えても安定**します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Constant Bias](constant-bias.md) | 比較の深度に、一定の値を足す |
| [Slope-Scale Bias](slope-scale-bias.md) | 面の傾きに比例して、バイアスを増やす |
| [Normal Offset](normal-offset.md) | 受け手の位置を、法線方向にずらす |
| [Receiver Plane Bias](receiver-plane-bias.md) | 受け手の平面から、深度の傾きを求める |
| [Front-Face Culling](front-face-culling.md) | 裏面だけを描いて、アクネを避ける |
| [Peter Panning](peter-panning.md) | バイアスが大きすぎて、影が浮く問題 |

## よくあるミス

??? failure "バイアスを大きくしてアクネを消したら、影が浮いた"
    **複数の方法を少しずつ**組み合わせる。**1 つを極端に大きくしない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **アクネは、深度の離散化と斜めの面から起きる**
    - [x] **5 つの対策を組み合わせ、浮き（ピーター パンニング）とのバランスを取る**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadows](../index.md)
- [Shadow Map Basics](../shadow-map-basics/index.md)
- [PCF](../pcf.md)
