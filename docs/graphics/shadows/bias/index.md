---
title: Shadow Bias
tags:
  - 描画
---

# Shadow Bias

<strong>シャドウ マップの深度は解像度と精度が有限</strong>なので、そのまま比べると光が当たっている面が自分自身の影になり、縞模様（シャドウ アクネ）になります。これを防ぐのがバイアスですが、大きくしすぎると影が物から離れて浮いて見えます（ピーター パンニング）。このセクションではアクネの原因・定数バイアス・スロープ スケール・法線オフセット・受け手平面・前面カリング・ピーター パンニングを 1 つずつ別のページで説明します。

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
シャドウ マップの 1 テクセルは、<strong>光から見たとき面の上の「ある大きさの領域」</strong>に対応しますが保存される深度は 1 つです。面が斜めだとその領域の中で面の本当の深度は、一定ではなく傾いています。

<svg class="fig illust" viewBox="0 0 780 290" role="img" aria-label="アクネの原因">
<text x="20" y="24" class="fig-title">1 テクセルの深度は 1 つ。斜めの面では、面の本当の深度がテクセルの中でずれる</text>
<line x1="60" y1="240" x2="720" y2="70" stroke="currentColor" stroke-width="4"/><text x="560" y="66" style="font-size:12px">斜めの面（光に対して傾いている）</text>
<g stroke="currentColor" stroke-width="1"><line x1="140" y1="240" x2="140" y2="40" stroke-dasharray="3 3"/><line x1="260" y1="240" x2="260" y2="40" stroke-dasharray="3 3"/><line x1="380" y1="240" x2="380" y2="40" stroke-dasharray="3 3"/><line x1="500" y1="240" x2="500" y2="40" stroke-dasharray="3 3"/><line x1="620" y1="240" x2="620" y2="40" stroke-dasharray="3 3"/></g>
<text x="165" y="262" style="font-size:12px">テクセル</text>
<g stroke="#e5484d" stroke-width="3"><line x1="140" y1="212" x2="260" y2="212"/><line x1="260" y1="182" x2="380" y2="182"/><line x1="380" y1="152" x2="500" y2="152"/></g>
<text x="396" y="144" style="font-size:12px;fill:#e5484d;font-weight:700">保存される深度（テクセルの代表値）</text>
<circle cx="320" cy="168" r="6" fill="currentColor"/><text x="326" y="164" style="font-size:12px">面の点（本当の深度）</text>
<text x="40" y="280" style="font-size:12px">点が保存された深度より奥（図では下）にある所が出る → 自分自身に遮られたと誤判定 → 縞（アクネ）</text>
</svg>

テクセルの代表深度より 面の点の方が奥にある場所（上の図でテクセルの下側）では「自分より手前に何かある」と誤判定されて、影になります。これが縞模様（アクネ）です。

### ずれの大きさ

1 テクセルのワールドでの大きさを `s`、光の向きと面の法線のなす角を `θ` とします。面が傾いているほどテクセルの中での深度のずれが大きくなります。

<div class="formula">深度のずれ ≈ s · tan θ　（θ：法線と光の向きのなす角）</div>

| θ | tan θ | ずれ |
| --- | --- | --- |
| 0°（光が真上から） | 0 | ほぼ無い |
| 45° | 1 | s と同じ |
| 80°（ほぼ水平） | 約 5.7 | s の 5.7 倍（アクネが激しい） |

斜めの面ほど大きなバイアスが要ることが分かります。一定のバイアスでは斜めの面に足りません。

## 組み合わせの設計
| 目的 | 推奨の組み合わせ |
| --- | --- |
| 平らな面のアクネを防ぐ | スロープ スケール ＋ 小さな定数 |
| 斜めの面・曲面のアクネを防ぐ | 法線オフセット |
| PCF で広くぼかす | 受け手平面バイアス（サンプルごとの補正） |
| 閉じた厚い物体 | 裏面レンダリング（併用） |
| ピーター パンニングを抑える | 各バイアスを最小限に。調整は明るい光・斜めの光で確認 |

## 調整の手順
| 手順 | 内容 |
| --- | --- |
| ① アクネが出る状態を作る | 光を低い角度（斜め）にして、平らな面・曲面を見る |
| ② スロープ スケールから足す | アクネが消える最小の値 |
| ③ 法線オフセットを足す | 曲面・角で残ったアクネを消す |
| ④ ピーター パンニングを確認 | 物体の接地部で影が離れていないか |
| ⑤ 光の角度を変えて再確認 | 全ての角度で破綻しないか |
| ⑥ カスケードごとに調整 | 解像度（テクセルの大きさ）が違うのでカスケードごとにバイアスを変える |

<strong>テクセルの大きさに比例</strong>するように、ワールド単位でバイアスを決めると、解像度・カスケードを変えても安定します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Constant Bias](constant-bias.md) | 比較の深度に一定の値を足す |
| [Slope-Scale Bias](slope-scale-bias.md) | 面の傾きに比例して、バイアスを増やす |
| [Normal Offset](normal-offset.md) | 受け手の位置を法線方向にずらす |
| [Receiver Plane Bias](receiver-plane-bias.md) | 受け手の平面から、深度の傾きを求める |
| [Front-Face Culling](front-face-culling.md) | 裏面だけを描いて、アクネを避ける |
| [Peter Panning](peter-panning.md) | バイアスが大きすぎて、影が浮く問題 |

## なぜバイアスが必要か

シャドウ マップでは <strong>画素の、光からの深度</strong>と シャドウ マップに保存された深度を比べます。自分自身の面（光に向いた地面）を描いているときこの 2 つは理論上、同じ値のはずです。ところが、実際には微小な誤差で画素の深度がわずかに大きく（遠く）なり「自分自身が自分の影の中」と判定されます。これがシャドウ アクネ（縞状の、自己影）です。

```text
              光
              ↓
 ─────────────────────────  地面
   保存された深度（4 画素に 1 つ）：階段状
   画素の深度：斜面に沿って、連続的に変わる

 階段より、上の画素 → 光が当たる、階段より下の画素 → 影（自分の影）  → 縞模様
```

シャドウ マップの 1 画素は 面の、ある範囲を代表する 1 つの深度です。斜めの面ではその範囲の中で深度が変わっているので画素ごとの深度と、保存された 1 つの深度は必ず、ずれます。そのずれをあらかじめ許容するのが、バイアスです。

## バイアスの基本の考え方

<strong>画素の深度から少し引く</strong>（光に近づける）と自分自身の面が影にならなくなります。

```text
比較:  画素の深度 − バイアス <= 保存された深度  なら、光が当たる
```

## 問題：バイアスの大小の、トレードオフ

| バイアス | 結果 |
| --- | --- |
| 小さすぎる | シャドウ アクネ（縞模様の、自己影） |
| 大きすぎる | ピーター パンニング（影が物から離れて、浮く）。薄い物の影が消える |
| ちょうどよい | 自己影なし影が物にしっかり接地する |

<strong>ちょうど</strong>の値は 光の角度、面の傾きシャドウ マップの解像度、カメラの距離で変わります。1 つの固定値ではすべての場面で、うまくいきません。

## 4 つのバイアス

| 方式 | 内容 | ページ |
| --- | --- | --- |
| 定数バイアス | 深度に一定の値を引く | [Constant Bias](constant-bias.md) |
| 傾き依存バイアス | 面が光に対して斜めなほど大きく | [Slope-Scale Bias](slope-scale-bias.md) |
| 法線オフセット | 面の法線の向きに、ずらしてからシャドウ マップを引く | [Normal Offset](normal-offset.md) |
| レシーバー平面バイアス | 画素の周りの平面を推定して平面に沿った深度で比べる | [Receiver Plane Bias](receiver-plane-bias.md) |
| 表面のカリング | シャドウ パスで、裏面を描く（物の厚みがバイアス） | [Front-Face Culling](front-face-culling.md) |

<strong>組み合わせて</strong>使うのが普通です。定数 + 傾き依存（ハードウェアの、バイアス）と法線オフセットが最も、一般的な組み合わせです。

## どれを選ぶか

| 状況 | おすすめ |
| --- | --- |
| まず、動かしたい | 定数 + 傾き依存（ラスタライザー ステート）。簡単 |
| 斜めの面でシャドウ アクネが残る | 法線オフセットを足す |
| 広い範囲（カスケード）で、バイアスが変わる | カスケードごとに、バイアスをスケール |
| 高品質（PCF を広くとる） | レシーバー平面バイアス（PCF の範囲に合わせた補正） |
| 薄い物、接地が重要 | 表面の描画（バイアス小）+ 法線オフセット |

<strong>1 つの方式だけでは足りない</strong>ことが多く、併用しながら場面に合わせて、調整するのが現実です。

## 調べ方

バイアスの調整は <strong>目で見て</strong>行います。調整用の場面（急な斜面、薄い板、光が地面にほぼ平行）を用意して、変えながら見ます。

| 場面 | 見るもの |
| --- | --- |
| 光が地面にほぼ平行（朝夕） | シャドウ アクネが出やすい。最も厳しい条件 |
| 薄い板（壁、床） | ピーター パンニングで影が消えないか |
| 球、円筒 | 曲面での影のなめらかさ |
| 影が接する場所（足元） | 影が物から、離れていないか |

## よくあるミス

??? failure "バイアスを大きくしてアクネを消したら、影が浮いた"
    <strong>複数の方法を少しずつ</strong>組み合わせる。1 つを極端に大きくしない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アクネは、深度の離散化と斜めの面から起きる
    - [x] 5 つの対策を組み合わせ、浮き（ピーター パンニング）とのバランスを取る

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978（シャドウ マップの原典）
- Brabec, Annen, Seidel, "Practical Shadow Mapping", Journal of Graphics Tools, Vol. 7, No. 4, 2002
- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）

## 関連ページ

- [Shadows](../index.md)
- [Shadow Map Basics](../shadow-map-basics/index.md)
- [PCF](../pcf.md)
