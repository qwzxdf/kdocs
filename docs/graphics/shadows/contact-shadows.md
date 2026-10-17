---
title: Contact Shadows
tags:
  - 描画
---

# Contact Shadows

シャドウ マップは、**解像度に限りがあり**、**バイアスで少し浮かせる**ので**物体が地面に接する付近の細かい影**が**欠けたり、浮いて見えたり**します（ピーター パンニング）。**コンタクト シャドウ**（Contact Shadows）は、<strong>画面空間（深度バッファ）</strong>で、**画素から光の方向へ短いレイを進め**、**手前にある物に当たるか**を調べる方式です。**接触部の細かい影**を**シャドウ マップを補って**、**安く**描きます。

!!! tip "ポイント"
    - <strong>画素から、光の方向へ深度バッファの上で短いレイ</strong>を進める。
    - <strong>レイの深度が深度バッファより奥に入ったら、遮蔽された</strong>。
    - <strong>距離は短い</strong>（数十 cm〜1 m）。<strong>シャドウ マップの接触部の欠けを補う</strong>のが目的。
    - 欠点：<strong>見えている面しか、知らない</strong>（画面外・裏側は遮蔽物にならない）。<strong>厚み</strong>の仮定。
    - <strong>画素ごとにジッター</strong>して、<strong>サンプル数を減らし</strong>、ノイズを<strong>時間蓄積</strong>で消す。
    - <strong>[SSR](../reflections/ssr-basics/index.md)・[SSAO](../ao/ssao-hemisphere.md) と同じ「画面空間」の方式</strong>で<strong>同じ限界</strong>を持つ。

## なぜ接触部で影が欠けるのか

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="接触部の影の欠け">
<text x="20" y="24" class="fig-title">シャドウ マップは、接触部で影が浮く・欠ける（ピーター パンニング）</text>
<line x1="60" y1="200" x2="720" y2="200" stroke="currentColor" stroke-width="4"/>
<rect x="150" y="150" width="70" height="50" fill="rgba(150,150,150,0.8)" stroke="currentColor" stroke-width="2"/><text x="140" y="140" style="font-size:12px">物体（地面に接している）</text>
<rect x="220" y="196" width="140" height="8" fill="#111" opacity="0.85"/><rect x="220" y="196" width="22" height="8" fill="#e5484d" opacity="0.5"/>
<text x="250" y="226" style="font-size:12px;fill:#e5484d;font-weight:700">接触部の影が欠ける</text>
<text x="420" y="70" style="font-size:13px">原因：</text><text x="420" y="94" style="font-size:12px">・バイアスで深度を浮かせる → 近い所は影が出ない</text><text x="420" y="114" style="font-size:12px">・シャドウ マップの 1 テクセルが、物の大きさに比べて粗い</text>
<text x="420" y="152" style="font-size:13px">解決：</text><text x="420" y="176" style="font-size:12px">画面の深度で、短い距離を調べる → 接触部だけ、細かく影を補う</text>
</svg>

<!-- fig:contact-shadow-march:begin -->

<svg class="fig illust motion" data-fig="contact-shadow-march" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-contact-shadow-march" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">コンタクト シャドウ:接触部の短い影を、画面空間のレイマーチで補う</text>
<rect x="40" y="280" width="700" height="18" fill="#d6c7a1"/>
<rect x="300" y="170" width="70" height="110" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<text x="335" y="162" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">物体</text>
<circle cx="670" cy="70" r="14" fill="#e5aa28"/>
<text x="690" y="64" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">光</text>
<rect x="272" y="280" width="28" height="18" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3677;0.3680;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="60" y="318" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">接触部の影が欠けている →（シャドウ マップの解像度不足）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3677;0.3680;1.0000" values="0;0;1;1;0;0"/></text>
<circle cx="286" cy="276" r="6" fill="#2563eb" stroke="#ffffff" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3677;0.3680;1.0000" values="0;0;1;1"/></circle>
<circle cx="298.8" cy="266.4" r="5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4357;0.4360;1.0000" values="0;0;1;1"/></circle>
<circle cx="311.6" cy="256.8" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4717;0.4720;1.0000" values="0;0;1;1"/></circle>
<circle cx="324.4" cy="247.2" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5077;0.5080;1.0000" values="0;0;1;1"/></circle>
<circle cx="337.2" cy="237.6" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5437;0.5440;1.0000" values="0;0;1;1"/></circle>
<circle cx="350.0" cy="228.0" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5797;0.5800;1.0000" values="0;0;1;1"/></circle>
<circle cx="362.8" cy="218.4" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6157;0.6160;1.0000" values="0;0;1;1"/></circle>
<circle cx="375.6" cy="208.8" r="5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6517;0.6520;1.0000" values="0;0;1;1"/></circle>
<circle cx="388.4" cy="199.2" r="5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6877;0.6880;1.0000" values="0;0;1;1"/></circle>
<circle cx="401.2" cy="189.6" r="5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7237;0.7240;1.0000" values="0;0;1;1"/></circle>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">まず、シャドウ マップで影を求める<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">接触部に、影の隙間ができる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3677;0.3680;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">その画素から、光の方向へ、画面上で少しずつ進む（レイマーチ）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3677;0.3680;0.7237;0.7240;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">深度バッファの物体に当たった → 影！ 隙間が埋まる<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7237;0.7240;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="350" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">緑 = 光が届く点、赤 = 物体の中に入った点（影）。進む距離は短くてよい（10〜20 歩）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7237;0.7240;1.0000;1.0000" values="0;0;1;1;0"/></text>
<rect x="272" y="280" width="28" height="18" fill="#334155" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7237;0.7240;1.0000;1.0000" values="0;0;1;1;0"/></rect>
</svg>

<!-- fig:contact-shadow-march:end -->

## 原理：画面空間のレイマーチ

**画素のビュー空間位置** `P` から、**光の方向** `L` へ**短いレイ**を**少しずつ進め**ます。**各ステップの位置を画面に投影**し、**その画素の深度**と比べます。**レイが深度バッファの面より奥に入った**ら、**面の裏側に潜った＝遮蔽**されたと判断します。

手順は 4 つです。レイの端点として、`P` と `P + L · max_distance`（ビュー空間）を求めます。両端をスクリーン座標へ投影します（[SSR](../reflections/ssr-basics/index.md) と同じです）。各ステップで、レイの深度が深度バッファより大きければ遮蔽とします。深度の差が大きすぎる場合は、遠くの面の手前を通っただけとして無視します（厚みの考慮）。

```hlsl
float ContactShadow(float3 view_pos, float3 light_dir_view, float2 pixel, float jitter) {
  float3 ray_end = view_pos + light_dir_view * kContactDistance;
  float2 uv0 = ProjectToUV(view_pos);
  float2 uv1 = ProjectToUV(ray_end);
  float z0 = view_pos.z;
  float z1 = ray_end.z;

  float shadow = 1.0;
  [loop] for (int i = 1; i <= kContactSteps; ++i) {
    float t = (i - 1.0 + jitter) / kContactSteps;
    float2 uv = lerp(uv0, uv1, t);
    float ray_z = 1.0 / lerp(1.0 / z0, 1.0 / z1, t);
    float scene_z = LinearDepth(depth_tex.SampleLevel(point_sampler, uv, 0).r);
    float diff = ray_z - scene_z;
    if (diff > kBias && diff < kThickness) {
      shadow = 0.0;
      break;
    }
  }
  return shadow;
}
```

コードの要点です。`1/z` で補間するのは、透視投影では 1/z が画面上で線形になるためです（[SSR](../reflections/ssr-basics/index.md)）。`jitter` は、画素ごとのステップ位置のずらし（IGN）で、ステップ数が少なくても、縞をノイズに変えられます。`kBias` は自己遮蔽（面自身）を避ける小さな許容値です。`kThickness` は厚みで、これ以上遮蔽物の奥にあるものは遮蔽物ではないとして扱います。`kContactDistance` は短い距離（0.1〜1 m 程度）です。

## 厚みの問題

**深度バッファは、「一番手前の面」の深度しか持たない**ので、**その面の厚み**（裏側までの奥行き）が、**分かりません**。

厚みの設定による結果です。薄すぎると、細い物（柵・草）をすり抜けることがあります。厚すぎると、遠くの面の手前を通っただけでも遮蔽扱いになり、誤った影が出ます。適度な値は、シーンに合わせて調整し、距離や物のスケールで変えます。

**完全な解決はなく**、**パラメータの調整**で**妥当な見た目**に寄せます。

## シャドウ マップとの合成

**コンタクト シャドウ**は、**単独ではなく、シャドウ マップを補う**ために使います。

コンタクト シャドウは、単独でなく、シャドウ マップを補うために使います。合成は、暗い方を取る `shadow = min(shadow_map, contact)` が一般的です。コンタクト シャドウは近くだけで使うので、距離でフェードアウトさせます。接触部をコンタクト シャドウが担当してくれるので、シャドウ マップのバイアスは安全側（アクネを避ける方）に振れます。

## コストと工夫

コストと工夫です。ステップ数は 8〜16 で、多いほど細部を捉えます。レイの距離は短いほど安くなります。ジッターと時間蓄積で、少ないステップのノイズを TAA が消します。遠くはコンタクト シャドウを省略して、画面中心と近景に限定します。通常は主ライト（太陽）だけに適用します。コンピュート シェーダーで、グループ共有メモリに深度を読み込み、キャッシュ効率を上げる実装もあります。

## 画面空間の限界

画面空間の限界です。画面外の遮蔽物は、深度バッファにないので遮蔽物として使えません。見えない面の裏側は、厚みを知りません。視点依存で、カメラが動くと影が変わって見えることがあります。画面端では、サンプルが画面外に出ると情報がありません。

**そのため、あくまで補助**で**シャドウ マップの代わりには、できません**。

## 長所と短所

コンタクト シャドウの長所は、接触部の細かい影が出ること、短いレイで安いこと、シャドウ マップのバイアスの問題を補えること、細い物（草・髪・ディテール）にもある程度効くことです。短所は、画面にある物だけが遮蔽物になること、厚みの扱いが難しいこと、画面外・裏側は扱えないこと、ジッターを使うとノイズが出ることです。

## よくあるミス

??? failure "自己遮蔽で、面全体が暗くなる"
    **小さなバイアス**を入れる、**レイの開始位置を法線方向に少しずらす**。

??? failure "遠くの面の手前を通っただけで、影になる"
    **厚み**（`kThickness`）を、設定します。

??? failure "非線形の深度のまま比べて、距離でおかしくなる"
    **線形な深度**（ビュー空間の z）で、比べます。

??? failure "全画面・長い距離で計算して、重い"
    **近景だけ・短い距離**にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンタクト シャドウ ＝ <strong>画素から光の方向へ、深度バッファ上で短いレイを進め</strong>、<strong>遮蔽</strong>を調べる
    - [x] <strong>シャドウ マップの、接触部の欠け・ピーター パンニングを補う</strong>
    - [x] <strong>厚み</strong>の仮定が必要（<strong>薄すぎ → すり抜け、厚すぎ → 誤った影</strong>）
    - [x] <strong>画面にある物しか見えない</strong>（<strong>補助</strong>として使う）
    - [x] <strong>ジッター ＋ 時間蓄積</strong>で、<strong>ステップ数を減らす</strong>

## 参考

- Sousa, "Secrets of CryEngine 3 Graphics Technology"（2011、画面空間の影）
- Bend Studio, "Screen Space Shadows"（GDC 2023 など）

## 関連ページ

- [Shadows](index.md)
- [Shadow Bias](bias/index.md)
- [SSR（画面空間の反射）](../reflections/ssr-basics/index.md)
- [SSAO](../ao/ssao-hemisphere.md)
