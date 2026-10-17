---
title: SSGI
tags:
  - 描画
---

# SSGI

**SSGI**（Screen-Space Global Illumination、画面空間 GI）は、<strong>[SSAO](../ao/ssao-hemisphere.md) と同じ発想</strong>を、<strong>「暗さ」だけでなく「光（色）」にまで広げた</strong>ものです。**画素の周りの半球にレイを飛ばし**（深度バッファ上で）、<strong>当たった画素の「色（その画素の出射光）」</strong>を、**間接光として集めます**。**事前計算が不要**で**動く物・動くライト**も**自動的に反映**されます。ただし、**画面に映っているものしか見えない**という**画面空間の限界**があります。

!!! tip "ポイント"
    - <strong>画素から半球方向にレイ</strong>を飛ばし（<strong>深度バッファ上</strong>）、<strong>当たった点の色</strong>を<strong>間接光</strong>として<strong>平均</strong>。
    - <strong>SSAO は「遮られた量」</strong>、<strong>SSGI は「当たった先の色」</strong>。
    - <strong>前フレームの最終画像（ライティング済み）</strong>を<strong>光源として使う</strong>と<strong>多バウンス</strong>が<strong>ほぼ無料</strong>で得られる。
    - <strong>少ないレイ ＋ ノイズ ＋ デノイズ（時間・空間）</strong>が<strong>必須</strong>。
    - 限界：<strong>画面外・裏側・隠れた面</strong>は<strong>見えない</strong>。<strong>画面端でゲインが変わる</strong>。
    - <strong>他の GI（プローブ等）の補助</strong>として、<strong>近距離の細かい間接光</strong>を足す使い方が多い。

## 原理

**SSAO**は<strong>半球に飛ばしたレイが「遮られたか」</strong>だけを見ました。**SSGI**は<strong>レイが当たった画素の「光（色）」</strong>を**読みます**。

SSAO と SSGI を並べると、違いがはっきりします。レイの結果は、SSAO が「遮られたか（0 か 1）」、SSGI が「当たった点の色（RGB）」です。出力は、SSAO が暗さ（スカラー）、SSGI が間接光（RGB）です。SSGI は色を読むので、カラー ブリーディングが出ますが、SSAO には色の効果がありません。

<!-- fig:ssgi-bounce:begin -->

<svg class="fig illust motion" data-fig="ssgi-bounce" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ssgi-bounce" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">SSGI:画面の中の明るい物から、色を借りて、間接光にする</text>
<rect x="60" y="320" width="640" height="18" fill="#e5e7eb" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="540" y="140" width="22" height="182" fill="#e5484d"/>
<text x="551" y="128" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">赤い壁（光が当たっている）</text>
<circle cx="620" cy="70" r="14" fill="#e5aa28"/>
<text x="640" y="66" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">光</text>
<circle cx="400" cy="316" r="9" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<text x="370" y="354" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">着色点（床）</text>
<line x1="400" y1="310" x2="451.79" y2="263.97" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></line>
<circle cx="451.79" cy="263.97" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="424.33" y2="239.63" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1145;0.1148;1.0000" values="0;0;1;1"/></line>
<circle cx="424.33" cy="239.63" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1145;0.1148;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="507.69" y2="284.49" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;1.0000" values="0;0;1;1"/></line>
<circle cx="507.69" cy="284.49" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1553;0.1556;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="244.83" y2="262.73" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1960;0.1963;1.0000" values="0;0;1;1"/></line>
<circle cx="244.83" cy="262.73" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1960;0.1963;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="337.09" y2="253.26" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;1.0000" values="0;0;1;1"/></line>
<circle cx="337.09" cy="253.26" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2370;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="389.58" y2="220.6" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2775;0.2778;1.0000" values="0;0;1;1"/></line>
<circle cx="389.58" cy="220.6" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2775;0.2778;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="460.93" y2="274.35" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;1.0000" values="0;0;1;1"/></line>
<circle cx="460.93" cy="274.35" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3182;0.3185;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="535.35" y2="196.47" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></line>
<circle cx="535.35" cy="196.47" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="263.46" y2="223.61" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></line>
<circle cx="263.46" cy="223.61" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="333.76" y2="262.5" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4404;0.4407;1.0000" values="0;0;1;1"/></line>
<circle cx="333.76" cy="262.5" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4404;0.4407;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="475.67" y2="196.42" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/></line>
<circle cx="475.67" cy="196.42" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="291.34" y2="183.82" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5219;0.5222;1.0000" values="0;0;1;1"/></line>
<circle cx="291.34" cy="183.82" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5219;0.5222;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="335.61" y2="285.44" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></line>
<circle cx="335.61" cy="285.44" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></circle>
<line x1="400" y1="310" x2="354.49" y2="175.89" stroke="#cbd5e1" stroke-width="1.8" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6034;0.6037;1.0000" values="0;0;1;1"/></line>
<circle cx="354.49" cy="175.89" r="5" fill="#cbd5e1" stroke="#64748b" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6034;0.6037;1.0000" values="0;0;1;1"/></circle>
<rect x="300" y="322" width="200" height="14" fill="#e5e7eb" opacity="1"/>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">着色点から、画面（深度バッファ）に沿って、サンプルを取る<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプルの色を、明るさ・向きの重みで集める<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.6441;0.6444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">赤い壁のサンプルが混ざり → 床がほんのり赤い（カラー ブリーディング）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6441;0.6444;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">画面に映っていない物は拾えない（画面外・背面の光は、無し）。拾った色は、前フレームの結果を使うと、多重バウンスにもなる。</text>
</svg>

<!-- fig:ssgi-bounce:end -->

### 手順

手順は次のとおりです。最初に、画素の法線を中心とする半球で、余弦重み付きのランダムな方向を作ります。次に、深度バッファ上でレイを進めます（[SSR](../reflections/ssr-basics/index.md) や [Hi-Z](../reflections/ssr-hiz.md) と同じ方法です）。レイの深度が深度バッファの奥に入ったらヒットと判定します。ヒットした画素の出射光（前フレームの最終色）を読みます。最後に、全レイの色を平均して間接光とします。

```hlsl
float3 SSGI(float3 view_pos, float3 view_normal, float2 pixel) {
  float3 sum = 0.0;
  [loop] for (int i = 0; i < kRayCount; ++i) {
    float3 dir = CosineSampleHemisphere(view_normal, Hash(pixel, i));
    float2 hit_uv;
    float hit_depth;
    if (ScreenSpaceTrace(view_pos, dir, hit_uv, hit_depth)) {
      float3 radiance = prev_frame_color.SampleLevel(linear_sampler, hit_uv, 0).rgb;
      sum += radiance;
    }
  }
  return sum / kRayCount;
}
```

コードの要点です。`prev_frame_color` は、前フレームの最終的な画像（ライティング済み、ポストプロセス前）で、間接光も含んでいるので多バウンスになります。余弦重み付きのサンプルは、`(n·ω)/pdf` が定数になり、単純な平均で済みます。`ScreenSpaceTrace` は、画面空間のレイマーチです（[SSR](../reflections/ssr-basics/index.md)、[Hi-Z トレース](../reflections/ssr-hiz.md)）。

## 多バウンスの得かた

**前フレームの最終画像に、前フレームの SSGI の結果が含まれている**ので、**フレームを重ねるごとに**、**バウンスが増える**ように見えます。

バウンス数は、何を読むかで決まります。現在のフレームの直接光だけを読めば、1 バウンスです。前フレームの最終画像（間接光を含む）を読めば、フレームごとに 1 バウンスずつ蓄積するので、多バウンスが無料で得られます。注意すべきは、ゲインが 1 を超えると発散する（明るくなり続ける）ことです。必ず 1 未満の減衰を掛けます。

## ノイズとデノイズ

**画素あたり 1〜数本**のレイでは、**ノイズ**が**非常に目立ちます**。

デノイズの手法を挙げます。<strong>時間蓄積</strong>は、前フレームの結果を再投影して混ぜます（動きベクトルが必要）。<strong>空間フィルタ</strong>は、バイラテラルや À-trous で、法線と深度を手がかりに、エッジを保ってぼかします。<strong>半分の解像度</strong>で計算し、バイラテラルでアップサンプルすると、コストが 1/4 になります。<strong>ブルー ノイズ</strong>や IGN を使うと、ノイズの質が良くなります。TAA を使っているなら、TAA が時間方向の平均を取るのも助けになります。

ノイズが大きいので、時間蓄積と空間フィルタの組み合わせは、ほぼ必須です。

**ノイズが大きい**ので**時間蓄積と空間フィルタ**の**組み合わせ**が、**ほぼ必須**です。

## 画面空間の限界

画面空間の限界を整理します。**画面外の光源や面**は見えないので、間接光に寄与しません。カメラの向きで、明るさが変わります。**隠れた面の裏側**は、深度バッファが一番手前の面だけを持つため、遮蔽物の向こう側も不明です。**画面端**では、サンプルが画面外へ出るので暗くなり、フェードが必要です。**厚み**の情報がないので、薄い物の背後を通過できなかったり、遠くの面の手前を誤ってヒットしたりします。そして**視点依存**で、カメラを動かすと間接光が変わって見える破綻が出ます。

そのため、SSGI 単体では、安定した GI になりません。プローブやライトマップなどのベースの GI に、近距離の細かい間接光とカラー ブリーディングを足す使い方が、一般的です。

**そのため、SSGI 単体で安定した GI にはなりません**。**プローブやライトマップなどの、ベースの GI**に**近距離の細かい間接光・カラー ブリーディングを足す**使い方が、一般的です。

## コストと工夫

コストの調整は、いくつかの手があります。レイ数は画素あたり 1〜4 本で、多いほどきれいですが重くなります。レイの距離は短いほど安いので、近距離のみを対象にします。半解像度で計算すれば、計算量が 1/4 になります。Hi-Z トレースを使えば、遠くまで少ないステップで届きます。法線と深度の事前フィルタは、ノイズの低減に有利です。

## 長所と短所

SSGI の長所は、事前計算が不要で動く物や動くライトを反映できること、SSAO や SSR の拡張なので実装が比較的簡単なこと、カラー ブリーディングが出ること、多バウンスがほぼ無料なこと、他の GI の補助として優れることです。短所は、画面にあるものしか見えないこと、ノイズとデノイズが必須なこと、視点依存でカメラによって変わること、画面外の光源が効かないこと、そして単独では安定しないことです。

### より良いやり方

SSGI の弱点は、「画面外が見えない」の一点に集約されます。そのため、より良い設計は、SSGI を単独で使わずに、<strong>見えなかった分を別の GI に任せる</strong>ことです。レイが画面外に出たり、深度バッファで当たらなかったりしたとき、その方向の光を、ライト プローブや DDGI のような世界空間の GI から読みます。つまり、<strong>SSGI は近距離の細部を担当し、遠くと画面外は世界空間の GI が担当する</strong>階層にします。Lumen が、画面空間トレースを最初の手段として使い、外れたら距離場、さらに外れたらワールド プローブ、と順に落ちていく設計は、まさにこの考え方です（[Lumen-Style Approaches](rt-gi/lumen-style.md)）。

## よくあるミス

??? failure "画面端で、間接光が急に暗くなる"
    **画面端付近をフェード**させる・**ベースの GI にフォールバック**します。

??? failure "前フレームの色を、再投影せずに読んで動くとずれる"
    **動きのベクトル**で**再投影**します。

??? failure "前フレーム色を、減衰なしで読み続けて、発散して明るくなる"
    **減衰**（1 未満）を掛けます。

??? failure "ノイズが残って、チラつく"
    **時間蓄積 ＋ 空間フィルタ**を強め、**ブルー ノイズ**を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSGI ＝ <strong>SSAO の拡張</strong>。<strong>半球レイが当たった画素の「色」</strong>を、<strong>間接光</strong>として集める
    - [x] <strong>前フレームの最終画像</strong>を光源にすると、<strong>多バウンスがほぼ無料</strong>
    - [x] <strong>少ないレイ ＋ 時間・空間デノイズ</strong>が<strong>必須</strong>
    - [x] <strong>画面外・裏側は見えない</strong>。<strong>視点依存</strong>。<strong>単独は不安定</strong>
    - [x] <strong>ベースの GI ＋ SSGI（近距離の補助）</strong>が、実用的

## 参考

- Ritschel, Grosch, Seidel, "Approximating Dynamic Global Illumination in Image Space"（I3D 2009）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015、レイ再利用の手法）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（GTAO）

## 関連ページ

- [Global Illumination (GI)](index.md)
- [GI Theory](theory/index.md)
- [SSAO](../ao/ssao-hemisphere.md)
- [SSR の基礎](../reflections/ssr-basics/index.md)
- [Hi-Z トレース](../reflections/ssr-hiz.md)
- [AO Filtering](../ao/filtering/index.md)
