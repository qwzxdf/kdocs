---
title: HBAO
tags:
  - 描画
---

# HBAO

**HBAO**（Horizon-Based Ambient Occlusion）は、2008 年に NVIDIA の Bavoil らが発表した方式です。これまでの SSAO が、**ランダムな点を置いて「遮られているか」を数えた**（モンテカルロ法）のに対し、HBAO は**方向を決めて、その方向に深度バッファを歩き、「遮蔽が始まる角度（地平線＝ホライゾン）」を見つけ**て、**その間の角度を式で積分**します。**サンプルを点でなく、「線」で扱う**ので**少ないサンプルでもノイズが小さく**なります。

!!! tip "ポイント"
    - 画素の周りを<strong>N 個の方向（スライス）</strong>に分け、<strong>各方向に深度バッファを数ステップ歩く</strong>。
    - 各方向で<strong>「地平線の角度 h（一番高く見える遮蔽物）」</strong>と、<strong>「面自身の傾き（接線角 t）」</strong>を求める。
    - その方向の遮蔽は、<strong>sin h − sin t</strong>（h と t の間の角度の、積分）。<strong>全方向で平均</strong>したものが AO。
    - <strong>点を数えるのでなく、角度を積分する</strong>ので<strong>少ないサンプルで滑らか</strong>。
    - <strong>距離の減衰 W(r)</strong>を掛けて、遠い遮蔽を弱める。
    - 弱点：<strong>コサイン重みを省略</strong>（立体角の割合）。<strong>GTAO</strong> が修正。

## 発想：地平線を探す

点 p に立って、<strong>ある 1 方向（たとえば右）</strong>を見ます。その方向の**断面**（p とその方向と視線を含む平面）を考えます。

- 面自身は**接線**（面の傾き）を持ちます。
- 近くの物体がその方向に立ちはだかっていれば、**見上げる角度**（地平線の高さ h）が、接線より**高く**なります。
- **接線と地平線の間の角度**が、**遮蔽されている範囲**です。

<svg class="fig illust" viewBox="0 0 764 280" role="img" aria-label="地平線と接線">
<text x="20" y="24" class="fig-title">ある 1 方向の断面：接線角 t から地平線 h までが、遮蔽されている範囲</text>
<line x1="60" y1="220" x2="400" y2="220" stroke="currentColor" stroke-width="4"/>
<polygon points="400,220 400,110 470,110 470,220" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/>
<circle cx="170" cy="220" r="7" fill="currentColor"/><text x="160" y="246" style="font-size:12px">点 p</text>
<line x1="170" y1="220" x2="380" y2="220" stroke="#2ea043" stroke-width="2" stroke-dasharray="5 3"/><text x="300" y="238" style="font-size:12px;fill:#2ea043">接線（t = 0 の例）</text>
<line x1="170" y1="220" x2="400" y2="112" stroke="#e5484d" stroke-width="3"/><text x="290" y="150" style="font-size:12px;fill:#e5484d;font-weight:700">地平線 h</text>
<path d="M230,220 A60,60 0 0 0 220,194" fill="none" stroke="currentColor"/><text x="236" y="206" style="font-size:12px">h</text>
<polygon points="170,220 380,220 400,112" fill="rgba(229,72,77,0.18)"/>
<text x="480" y="130" style="font-weight:700">遮蔽 ＝ sin h − sin t</text>
<text x="480" y="154" style="font-size:12px">（h の上は、空が見えている）</text>
<text x="480" y="184" style="font-size:12px">この 1 方向の結果を、全方向（N 本）で平均する</text>
<text x="20" y="268" style="font-size:12px">壁が高いほど h が大きくなり、遮蔽が増える。壁がなければ h = t で、遮蔽 0</text>
</svg>

<!-- fig:hbao-horizon:begin -->

<svg class="fig illust motion" data-fig="hbao-horizon" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hbao-horizon" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">HBAO:一方向に、地平線（最も高い遮蔽）の角度を探す</text>
<rect x="40" y="330" width="700" height="16" fill="#d6c7a1"/>
<polygon points="200,330 200,330 260,330 310,320 360,330 430,290 490,260 530,260 580,310 630,330 700,330 700,330" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="200" cy="330" r="8" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<text x="172" y="364" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">着色点</text>
<line x1="200" y1="330" x2="300" y2="330" stroke="#e5484d" stroke-width="3.5"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0000;0.0889;0.1556;0.2222;0.2889;0.3556;0.4222;0.4889;0.5556;0.6222" values="300;300;440;439.01;439.01;436.45;433.3;433.3;433.3;433.3;433.3"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0000;0.0889;0.1556;0.2222;0.2889;0.3556;0.4222;0.4889;0.5556;0.6222" values="330;330;330;308.27;308.27;288.88;273.69;273.69;273.69;273.69;273.69"/></line>
<circle cx="260" cy="330" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0886;0.0889;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="260" y2="330" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0886;0.0889;0.1553;0.1556;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="310" cy="320" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="310" y2="320" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;0.2219;0.2222;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="360" cy="330" r="6" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="360" y2="330" stroke="#cbd5e1" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.2886;0.2889;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="430" cy="290" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2886;0.2889;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="430" y2="290" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2886;0.2889;0.3553;0.3556;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="490" cy="260" r="6" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3553;0.3556;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="490" y2="260" stroke="#2ea043" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3553;0.3556;0.4219;0.4222;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="530" cy="260" r="6" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4219;0.4222;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="530" y2="260" stroke="#cbd5e1" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4219;0.4222;0.4886;0.4889;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="580" cy="310" r="6" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4886;0.4889;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="580" y2="310" stroke="#cbd5e1" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4886;0.4889;0.5553;0.5556;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="630" cy="330" r="6" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5553;0.5556;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="630" y2="330" stroke="#cbd5e1" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5553;0.5556;0.6219;0.6222;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="700" cy="330" r="6" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6219;0.6222;1.0000" values="0;0;1;1"/></circle>
<line x1="200" y1="330" x2="700" y2="330" stroke="#cbd5e1" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6219;0.6222;0.6886;0.6889;1.0000" values="0;0;1;1;0;0"/></line>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 1:仰角 0° （更新!） → これまでの最大 0°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0886;0.0889;0.1553;0.1556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 2:仰角 5° （更新!） → これまでの最大 5°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;0.2219;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 3:仰角 0° （低い） → これまでの最大 5°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.2886;0.2889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 4:仰角 10° （更新!） → これまでの最大 10°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2886;0.2889;0.3553;0.3556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 5:仰角 14° （更新!） → これまでの最大 14°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3553;0.3556;0.4219;0.4222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 6:仰角 12° （低い） → これまでの最大 14°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4219;0.4222;0.4886;0.4889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 7:仰角 3° （低い） → これまでの最大 14°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4886;0.4889;0.5553;0.5556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 8:仰角 0° （低い） → これまでの最大 14°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5553;0.5556;0.6219;0.6222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 9:仰角 0° （低い） → これまでの最大 14°<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6219;0.6222;0.6886;0.6889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="66" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">地平線の角度 h = 14° → この方向の遮蔽 ≒ sin h = 0.23<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6886;0.6889;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">赤い線 = これまでに見つけた地平線。遮蔽される範囲は、地平線より下の角度（扇形）。方向を何本か（4〜8）繰り返して平均する。</text>
</svg>

<!-- fig:hbao-horizon:end -->

## 式

半球を**方位角 θ**（画面上の方向）と、**仰角 α**（その方向の断面での持ち上げ角）で表します。**可視な範囲は、t(θ) から h(θ) の「間」ではなく、h(θ) より上**ですが、AO は<strong>「遮蔽されている量」</strong>で書きます。

<div class="formula">AO = 1 − (1 / 2π) · ∫_{θ=−π}^{π} ∫_{α=t(θ)}^{h(θ)} W(θ) · cosα  dα dθ</div>

内側の積分は`∫ cosα dα = sin h − sin t` です。**距離の減衰 W** を方向ごとに一定とみなし、**方向を N 本に離散化**すると、次のとおりです。

<div class="formula">AO ≈ 1 − (1 / N) · Σ_{i=1}^{N} W(θᵢ) · ( sin h(θᵢ) − sin t(θᵢ) )</div>

| 記号 | 意味 |
| --- | --- |
| **N** | 方向（スライス）の数（8 程度） |
| <strong>h(θ)</strong> | 方向 θ での**地平線の角度**（歩いた中で最も高く見えた遮蔽物の仰角） |
| <strong>t(θ)</strong> | 方向 θ での**面自身の接線の角度**（法線から決まる） |
| **W** | 距離の減衰。`W(r) = 1 − r²/R²`（R は影響半径） |

!!! note "コサイン重みが入っていない"
    式は**立体角の割合**（`cosα dα dθ` は、半球上の面積要素）を、**そのまま**積分しています。[理論](theory/index.md)の AO は**法線とのコサイン `n·ω`**を掛けた積分でした。**HBAO はこのコサインを省略**しています（法線に近い遮蔽も横の遮蔽も立体角が同じなら、同じ重み）。そのため、**正確な AO より、少しだけ、横方向の遮蔽が強く**効きます。この点を修正したのが、[GTAO](gtao.md) です。

## 手順

| 手順 | 内容 |
| --- | --- |
| **① 方向を決める** | N 本（8 本など）。**画素ごとにランダムに回転**（4×4 のノイズ）して、ノイズに変える |
| **② 接線角 t を求める** | **法線と方向から**、断面での面の傾きを計算 |
| **③ 歩く** | 各方向に、**M ステップ**（6 程度）進む。**ステップ幅は画面上のピクセルで一定**（**半径 R を画面の大きさに直したもの ÷ M**） |
| **④ 各ステップで遮蔽物の位置 S を読む** | 深度から位置を復元 |
| **⑤ 仰角を求める** | `S − P`（ベクトル H）の**仰角**を計算 |
| **⑥ 地平線を更新** | 今までの最大の仰角より**高ければ**、**差の分だけ AO に足し**、地平線を更新 |
| **⑦ 全方向を平均** | `AO = 1 − 平均` |

### 接線角 t

断面の**面の傾き**です。**法線 N と画面上の方向 d** から求めます。

**面が画面と平行**（法線がカメラの方を向いている）なら、**t = 0**（接線は水平）です。**面が傾いている**と**傾いた分だけ**、<strong>t が負（面が奥へ傾く）</strong>か<strong>正（面が手前へ傾く）</strong>になります。

左手系（カメラが +Z を見る）で、<strong>カメラの方向を「上」</strong>として仰角を測る場合、接線ベクトルと `sin t` は、次のとおりです。

<div class="formula">T = ( d.x , d.y , −(N.x·d.x + N.y·d.y) / N.z )　、　sin t = −T.z / |T|</div>

### 仰角の更新

**地平線の仰角の sin** を、歩きながら**最大値**で更新します。**更新のたびに増えた分を AO に足す**ので、**遠い遮蔽ほど弱く**（距離の減衰を掛けて）なります。

```hlsl
float HorizonAO(float2 uv, float3 p, float3 n, float2 dir_view, float step_uv) {
  float3 t_vec = float3(dir_view, -dot(n.xy, dir_view) / n.z);
  float sin_t = -t_vec.z / length(t_vec);

  float sin_h = sin_t;
  float ao = 0.0;
  for (int i = 1; i <= kSteps; ++i) {
    float2 suv = uv + float2(dir_view.x, -dir_view.y) * (step_uv * i);
    float3 s = ViewPositionFromDepth(suv);
    float3 h = s - p;
    float r2 = dot(h, h);

    float sin_s = -h.z / sqrt(r2);
    if (sin_s > sin_h) {
      float falloff = saturate(1.0 - r2 * inv_radius2);
      ao += (sin_s - sin_h) * falloff;
      sin_h = sin_s;
    }
  }
  return ao;
}
```

| 点 | 説明 |
| --- | --- |
| **`sin_t` で初期化** | 地平線の初期値は、**面自身の高さ**（遮蔽なし）。**それより高い遮蔽物**だけが、AO に寄与 |
| **`−h.z`** | 左手系（+Z が奥）で、<strong>カメラに近い側を「上」</strong>にするため、符号を反転 |
| **`falloff`** | `1 − r²/R²`。**半径 R の外では 0** |
| **ステップの幅** | `step_uv` は、**画面上で一定**。**ビュー空間の半径 R ÷ ステップ数**を、距離で割って画面に直す |
| **`float2(dir.x, -dir.y)`** | 画面の方向（y 下向き）と、ビュー空間（y 上向き）の違い |

全体では画素ごとに N 方向を回します。

```hlsl
float HBAO(float2 uv) {
  float3 p = ViewPositionFromDepth(uv);
  float3 n = ViewNormal(uv);
  float2 noise = noise_tex.Sample(wrap_sampler, uv * noise_scale).xy;
  float step_uv = radius_uv_at(p.z) / kSteps * (0.5 + 0.5 * noise.y);

  float ao = 0.0;
  for (int i = 0; i < kDirections; ++i) {
    float angle = 6.2831853 * (i + noise.x) / kDirections;
    ao += HorizonAO(uv, p, n, float2(cos(angle), sin(angle)), step_uv);
  }
  return saturate(1.0 - ao / kDirections * intensity);
}
```

## ランダム化

N が小さい（8）ので**画素ごとに方向の開始角を回し、ステップの長さにわずかなジッター**を与えます。これで**縞がノイズに変わり**、後で**ぼかして**消します（4×4 のノイズ ＋ ブラー）。

| ランダム化 | 目的 |
| --- | --- |
| **方向の開始角** | 方向の本数の少なさによる、**縞**を消す |
| **ステップ幅のジッター** | ステップ位置の**バンディング**を消す |

## 点を数える方式との比較

| 項目 | 半球 SSAO など（点を数える） | HBAO（地平線を積分） |
| --- | --- | --- |
| **サンプルの単位** | 3D の点（遮られているか 0/1） | **方向（線）。仰角の連続値** |
| **精度 / サンプル数** | 点が少ないと、**0/1 の量子化ノイズ**が大きい | **角度の連続値**なので**少ない方向数でも滑らか** |
| **遮蔽物の厚み** | 点ごとの判定（**厚い・薄いの区別なし**） | 地平線は**最も高い 1 点**で決まる（**厚みの区別なし**。薄い柱は同様に問題） |
| **コサイン重み** | 一様な半球（雑） | **省略**（立体角の割合） |
| **コスト** | N 個の独立サンプル | **N 方向 × M ステップ**（隣接アクセスでキャッシュに優しい面もある） |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **少ないサンプルで滑らか** | **コサイン重みがない**（GTAO で修正） |
| **接線角で面の傾きを正しく扱う**（平らな面で自己遮蔽しにくい） | **ステップ数 × 方向数**で、サンプルが多い（実質 8×6 = 48 回） |
| **距離の減衰が自然に入る** | **ハロー・画面端・薄い物**の問題は、同じ |
| **地平線の考え方が後の方式（GTAO）の基礎** | **法線が必要** |

## 次の方式

| 弱点 | 解決 |
| --- | --- |
| **重く、キャッシュが効かない** | [HBAO+](hbao-plus.md)（フル解像度・デインターリーブ・近似の簡略化） |
| **コサイン重みがない・バウンスがない** | [GTAO](gtao.md) |

## よくあるミス

??? failure "接線角 t を求めず、地平線を 0 から始めて、傾いた面が自己遮蔽する"
    初期値を面自身の `sin t` にします。

??? failure "ステップ幅を、ビュー空間の距離で固定して、遠くの物のサンプルが画面上で潰れる"
    画面上の**ピクセルで一定**の幅にし、半径は距離で割って画面に直します。

??? failure "地平線の更新に、距離の減衰を掛けず、遠い壁で暗くなる"
    更新の増分に、`falloff` を掛けます。

??? failure "y の向き（画面は下向き、ビュー空間は上向き）を取り違える"
    方向を画面（uv）とビュー空間で、**y の符号を反転**して使い分けます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] HBAO ＝ <strong>方向ごとに深度バッファを歩き、地平線の角度を求めて、角度を積分</strong>する
    - [x] AO ≈ <strong>1 − 平均( W · (sin h − sin t) )</strong>。<strong>t は面の接線角、h は地平線</strong>
    - [x] <strong>点を数えず、角度を積分</strong>するので<strong>少ないサンプルでも滑らか</strong>
    - [x] <strong>コサイン重みがない</strong>のが弱点（→ GTAO）
    - [x] ランダムな方向・ステップでノイズに変えてぼかす

## 参考

- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion"（SIGGRAPH 2008 Talks）

## 関連ページ

- [環境光遮蔽（AO）](index.md)
- [HBAO+](hbao-plus.md)
- [GTAO](gtao.md)
- [フィルタ](filtering/index.md)
- [AO の理論](theory/index.md)
