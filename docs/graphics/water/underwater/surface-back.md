---
title: The Underside of the Surface and Crossing It
tags:
  - 描画
---

# The Underside of the Surface and Crossing It

<strong>水中から水面を見上げると水面は、鏡のように反射する部分と空が見える部分（スネルの窓）に分かれます</strong>。<strong>カメラが水面をまたぐ時の見た目の切り替え</strong>にも注意が必要です。このページでは水面の裏側の見え方と、またぐ処理を説明します。

!!! tip "ポイント"
    - 水面の裏側は全反射とスネルの窓。
    - 水面を描く時、裏面も描く（カリングを切る）。
    - カメラが水面をまたぐ瞬間は、画面の半分が水中になる。
    - またぐ時は水面の位置で、画面を上下に分ける。

<!-- fig:snell-window:begin -->

<svg class="fig illust motion" data-fig="snell-window" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-snell-window" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">水中から見上げる:一定の角度の内側は空、外側は水面が鏡になる</text>
<rect x="40" y="80" width="700" height="110" fill="#e0f2fe" fill-opacity="0.5"/>
<rect x="40" y="190" width="700" height="130" fill="#7dd3fc" fill-opacity="0.35"/>
<line x1="40" y1="190" x2="740" y2="190" stroke="#0284c7" stroke-width="3"/>
<text x="50" y="104" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">空</text>
<circle cx="390" cy="300" r="11" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<text x="406" y="305" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">水中の目</text>
<polygon points="390,300 264.55,190 515.45,190" fill="#e5aa28" fill-opacity="0.12" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="390" y="182" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">スネルの窓（約 49°）</text>
<line x1="390" y1="300" x2="390" y2="190" stroke="#2ea043" stroke-width="3"><animate attributeName="x2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="390;390;394.2;398.42;402.65;406.93;411.26;415.65;420.12;424.68;429.36;434.16;439.12;444.25;449.57;455.12;460.92;467.02;473.46;480.27;487.53;495.3;503.66;512.7;522.55;533.35;545.29;558.58;573.52;590.5;610.02;632.78;659.71;692.22;692.22"/></line>
<line x1="390" y1="190" x2="390" y2="100" stroke="#2ea043" stroke-width="3"><animate attributeName="x1" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="390;390;394.2;398.42;402.65;406.93;411.26;415.65;420.12;424.68;429.36;434.16;439.12;444.25;449.57;455.12;460.92;467.02;473.46;480.27;487.53;495.3;503.66;512.7;522.55;533.35;545.29;558.58;573.52;590.5;610.02;632.78;659.71;692.22;692.22"/><animate attributeName="x2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="390;390;398.78;407.59;416.5;425.52;434.73;444.16;453.88;463.95;474.47;485.51;497.21;509.71;523.23;538.02;554.49;573.21;595.1;621.75;656.3;706.14;795.93;1154.89;645.68;660.29;675.85;692.58;710.76;730.78;753.14;778.51;807.87;842.57;842.57"/><animate attributeName="y2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0932;0.1198;0.1464;0.1729;0.1995;0.2260;0.2526;0.2792;0.3057;0.3323;0.3589;0.3854;0.4120;0.4385;0.4651;0.4917;0.5182;0.5448;0.5714;0.5979;0.6245;0.6510;0.6776;0.7042;0.7307;0.7573;0.7839;0.8104;0.8370;0.8635;0.8901;0.9167;1.0000" values="100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;100;292.18;287.4;282.49;277.43;272.26;266.96;261.55;256.03;250.42;244.72;244.72"/><animate attributeName="stroke" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0000;0.6587" values="#2ea043;#2ea043;#e5484d"/></line>
<text x="40" y="52" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">窓の内側を見る:屈折して、空が見える<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6583;0.6587;1.0000" values="1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">窓の外側を見る:全反射して、水中（海底）の景色が映る<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6583;0.6587;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="406" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">見上げる角度が大きくなる（横を向く）と、ある角度から先は、水面が鏡になる。これが水中の「天井」の見え方。</text>
</svg>

<!-- fig:snell-window:end -->

## 水面の裏側
<strong>水中から水面を見上げる</strong>と、<strong>水面は「鏡」と「窓」の両方</strong>になります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="水中から見上げる窓">
<text x="20" y="24" class="fig-title">水中から見上げる：臨界角の内側だけ空が見え、外側は全反射</text>
<rect x="40" y="110" width="700" height="130" fill="#4c8bf5" fill-opacity="0.2"/>
<line x1="40" y1="110" x2="740" y2="110" stroke="#4c8bf5" stroke-width="3"/>
<circle cx="390" cy="225" r="7" fill="#e5484d"/>
<text x="402" y="230" style="font-size:12px">カメラ</text>
<line x1="390" y1="225" x2="390" y2="110" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
<line x1="390" y1="225" x2="505" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="390" y1="225" x2="275" y2="110" stroke="#2ea043" stroke-width="3"/>
<line x1="505" y1="110" x2="610" y2="60" stroke="#2ea043" stroke-width="3"/>
<line x1="275" y1="110" x2="170" y2="60" stroke="#2ea043" stroke-width="3"/>
<text x="612" y="62" style="font-size:12px">空が見える</text>
<line x1="390" y1="225" x2="610" y2="110" stroke="#e5aa28" stroke-width="3"/>
<line x1="610" y1="110" x2="690" y2="215" stroke="#e5aa28" stroke-width="3"/>
<text x="600" y="172" style="font-size:12px">全反射</text>
<text x="400" y="170" style="font-size:12px">臨界角 約 49°</text>
</svg>

<strong>水から空気へ出る光は臨界角（約 49°）より浅い角度だと屈折せずに全反射</strong>します。

<div class="formula">臨界角 θc = asin( n₂ / n₁ ) = asin( 1.0 / 1.33 ) ≈ 48.8°</div>

水中から水面を見上げると見え方が範囲で変わります。真上に近い範囲（円の内側）では、空が見えます（窓）。空は円形に縮んで見えます（スネルの窓）。円の外側では全反射が起きて水中の景色が水面に鏡のように映ります。

```hlsl
float3 refracted = refract(-view_dir, -normal, 1.33 / 1.0);
bool total_internal_reflection = dot(refracted, refracted) < 0.001;

float3 color = total_internal_reflection
             ? SampleUnderwaterReflection(reflect(-view_dir, -normal))
             : SampleSky(refracted);
```

コードの要点です。`refract` の戻り値が 0 なら全反射（屈折できない）です。水中側から見るので法線を反転します。水面の下側のシェーディングは、水中側の屈折率でフレネルを計算します。

## 水面をまたぐ処理
<strong>水面ぎりぎりにカメラがあるとき、画面の上半分は水の外、下半分は水の中</strong>になります。

| 工夫 | 内容 |
| --- | --- |
| 近い面を塞ぐ | カメラ前方の水面に細い帯（水中のフォグ色）を描き、境目の隙間をなくす |
| 水位線の描画 | ポストプロセスで水位の画面上の位置を求め、上下で別の処理 |
| 体積の判定 | 水のボリューム（メッシュ）を描き、前面・裏面で内外を決める |
| 遷移 | 水に入る瞬間は、フェードで急変を隠す |

## 水中から水面を見上げる

水面を <strong>下から</strong>見上げると見え方が、<strong>上から見たときとまったく違います</strong>。

| 見る角度 | 見え方 |
| --- | --- |
| 真上（水面にほぼ垂直） | 水面が透けて空が、見える。明るい円（スネルの窓） |
| 浅い角度 | 水面が鏡のように、水中の景色を反射する（全反射） |
| その間 | 窓の縁。空の景色が圧縮されて映る |

## スネルの窓

水中から水面を見ると <strong>空が見える範囲が円形に、限られます</strong>。この円を <strong>スネルの窓</strong>と呼びます。

```text
水中から見上げる
          空（全体が、窓の中に、圧縮されて見える）
         ╱  ╲
       ╱      ╲        ← 窓の外側は、水面が、鏡のように、水中を映す
      │  窓    │
       ╲      ╱
         ╲  ╱
          ●  カメラ（水中）
```

| 項目 | 値 |
| --- | --- |
| 臨界角 | `θ_c = asin(1 / 1.33) ≈ 48.6°`（真上から測った角度） |
| 窓の開き角 | `2 × 48.6° ≈ 97.2°`（円錐） |
| 窓の内側 | 空の全体（180°）が、97.2° に圧縮されて見える |
| 窓の外側 | 全反射で水中の景色が、水面に映る |

窓の<strong>縁</strong>に近づくほど <strong>水平に近い空の景色</strong>が、見えます。窓の縁で空の地平線が見えます。

## 全反射

光が <strong>水から空気へ</strong>出るとき（`n₁ = 1.33`、`n₂ = 1.0`）、<strong>入射角が臨界角より大きい</strong>と光は、外へ出られずすべて反射します。スネルの法則を満たす屈折角が、存在しない（`sin θₜ > 1`）ためです。

```hlsl
// 水中から、水面を見上げるとき、屈折ベクトルを求める（HLSL の refract）。
// eta = n_水 / n_空気 = 1.33。屈折できないとき（全反射）、refract は、ゼロ ベクトルを返す。
float3 refracted = refract(view_dir, -wave_normal, 1.33);     // 水面の法線は、下向きに（水中から見る向き）
bool total_internal_reflection = dot(refracted, refracted) < 1e-5;
```

| 結果 | 意味 |
| --- | --- |
| `refracted` が有効 | 空が見える（窓の中）。`refracted` の向きで空を読む |
| `refracted` がゼロ | 全反射。水面が鏡。反射ベクトル `reflect(view_dir, -wave_normal)` で水中の景色（水底、水中の物）を読む |

```hlsl
// 水中から見た、水面の色。
float3 N = -wave_normal;                                     // 下向き（水中から見た、法線）
float3 refracted = refract(view_dir, N, 1.33);
float3 color;
if (dot(refracted, refracted) < 1e-5) {
  // 全反射: 水中の景色を、映す（水中の霧で、暗く青い）
  float3 r = reflect(view_dir, N);
  color = SampleUnderwaterReflection(r);
} else {
  // 窓の内側: 空が、見える
  float F = FresnelExact(saturate(dot(-view_dir, N)), 1.0 / 1.33);   // 水から空気への、反射率
  float3 sky = SampleSky(refracted);
  float3 refl = SampleUnderwaterReflection(reflect(view_dir, N));
  color = lerp(sky, refl, F);
}
```

窓の内側でも <strong>一部は反射</strong>します（フレネル）。窓の縁に近づくほど反射の割合が、<strong>1 に近づく</strong>（全反射へなめらかに、つながる）。フレネルの式を正しく使うと窓の縁が、なめらかに自然に見えます（[Water Fresnel](../shading/fresnel.md)）。

## 水面を下から描く

水面のメッシュを <strong>裏側から</strong>描く必要があります。

| 項目 | 内容 |
| --- | --- |
| カリング | 通常、水面は上から見る前提で裏面を、描かない。水中では裏面を描く（カリングを、切り替えるまたは無効にする） |
| 法線 | 水面の法線を反転する（水中から見ると、下向きが表） |
| シェーダー | 水中用の、別のシェーダーを使う（反射、屈折、フレネルの向きが逆） |
| 霧 | 水面の手前（カメラ側）は、水中なので水中の霧をかける |

```cpp
// カメラが、水の中にあるか。波の高さを、カメラの位置で調べる。
bool IsUnderwater(const float3& camera_position) {
  return camera_position.y < WaterHeightAt({camera_position.x, camera_position.z}, time);
}

// 水中なら、水面を、裏から、描く（ラスタライザー ステートを切り替える）。
context->RSSetState(underwater ? rs_cull_front.Get() : rs_cull_back.Get());
```

`rs_cull_front` は <strong>表面をカリング</strong>する（裏面だけを描く）ステートです。

## 水面をまたぐ

カメラが <strong>水面を通り抜ける</strong>とき、<strong>画面の半分が水中、半分が空気中</strong>になります。

```text
  ──────────────  空気中（画面の上半分）
  ~~~~~~~~~~~~~~  ← 水面の線（カメラが、水面にある）
  ──────────────  水中（画面の下半分）
```

| 問題 | 内容 |
| --- | --- |
| 画面の半分に水中の霧が必要 | 水中の霧は、カメラが水の中にあるときに全画面に、かける。半分だけはできない |
| 近クリップ面 | 近クリップ面が水面を切ると水面が、一瞬消える（近クリップで切れる）。水面のメッシュがカメラの前を、通過する |
| 水面のメッシュの厚み | 水面が、薄い面だと近クリップ面に切断される。切断された部分は水面が見えなくなり、水中と空気中の境目が見える |

### 対策：水面のボリューム

水面の下に <strong>水のボリューム（箱、またはメッシュ）</strong>を置きます。カメラが水面をまたいでいるとき、<strong>カメラの前の近クリップ面が、水のボリュームの中にある</strong>部分だけを、水中の霧で塗ります。

| 方法 | 内容 |
| --- | --- |
| ステンシル | 水のボリュームの裏面と表面を、ステンシルに描く。水の中にいる画素を判定して水中の霧を、かける |
| 水面の高さで判定 | 画素ごとに視線と、水面の交点を求め水面より手前が、水の中か判定する |
| 水面の線を描く | 画面に、水面の線（ウォーターライン）を描く。上は空気、下は水中の見た目。画面の水平の線ではなく波の形で |

```hlsl
// ポストプロセス: 各画素の、視線方向の点が、水面の下か上かで、水中の霧を、かけ分ける。
float3 world_pos = ReconstructWorldPosition(uv, depth);
float surface_y = WaterHeightAt(world_pos.xz);

if (camera_position.y < surface_y) {
  // カメラは、水中: 全画素に、水中の霧（距離に応じて）をかける。
} else {
  // カメラは、水面の上: 水面の、手前の画素は、空気中。水面より、下にある、水中の画素に、水中の霧をかける。
  // 画素が、水の下にある（world_pos.y < surface_y）なら、水中の霧を、水に入った距離ぶん、かける。
}
```

水面をまたぐ瞬間の <strong>画面のきれいな切り替え</strong>は、<strong>難しい</strong>ので実際の作品でも、わずかなごまかし（短いフェード、水面の線の強調）が使われています。

## 水面のすぐ下

水面のすぐ下にいるとき <strong>水面の波が、天井のように</strong>見えます。

| 要素 | 内容 |
| --- | --- |
| 揺れる光 | 水面を通った光が、コースティクスとして水中の物に、映る（[Caustics](caustics.md)） |
| 水面の裏の色 | 空が見える（窓の中）。窓の外は水中の景色が映る |
| 泡 | 水に入った泡が水面の、すぐ下にたまり白い層になる |
| 水面の法線 | 波で細かく傾く。窓の形が揺れて歪む |

## よくあるミス

??? failure "水に入る瞬間、画面がちらつく"
    <strong>水面のメッシュは裏面も描き</strong>、<strong>水中の判定をなめらかに</strong>切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 裏面も描く
    - [x] またぐ瞬間の処理に注意

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018
- Hecht, "Optics", 5th Edition, Pearson, 2016（スネルの法則、全反射、スネルの窓）
- Lynch, Livingston, "Color and Light in Nature", 2nd Edition, Cambridge University Press, 2001（水中から見た景色）
- Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes（水平変位と、波頭の折れ）

## 関連ページ

- [Underwater Rendering](index.md)
- [Underwater Fog](fog.md)
