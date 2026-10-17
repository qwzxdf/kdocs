---
title: Velocity Buffer
tags:
  - 描画
---

# Velocity Buffer

<strong>モーション ブラーは、「各画素が前フレームからどう動いたか」</strong>という**情報**に**頼ります**。<strong>これを画素ごとに保存した画像が速度バッファ（Velocity Buffer）</strong>です。**TAA・モーション ブラー・時間的なノイズ除去・アップスケール**など、**時間方向の処理すべてが使う**、**現代の描画の共通インフラ**です。このページでは、**速度の定義・書き込み方法・精度と形式・ジッターの扱い・動かない物の扱い**を説明します。

!!! tip "ポイント"
    - 速度 ＝ <strong>この画素の点が、前フレームでは画面のどこにいたか、との差</strong>（<strong>`現在位置 − 前フレームの位置`</strong>）。
    - <strong>動く物体は、描画時に速度を書く</strong>。<strong>静止した物はカメラ移動分だけ</strong>（<strong>深度から計算</strong>できる）。
    - 保存は <strong>`R16G16_FLOAT`</strong>（<strong>UV 単位または画素単位</strong>）。
    - <strong>前フレームのワールド行列</strong>が<strong>必要</strong>（<strong>物体ごとに保存</strong>）。
    - <strong>TAA のジッターを、速度に混ぜない</strong>。
    - <strong>アニメーション・スキニング</strong>は<strong>前フレームの姿勢</strong>で<strong>頂点位置を計算</strong>する。

<!-- fig:velocity-buffer:begin -->

<svg class="fig illust motion" data-fig="velocity-buffer" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-velocity-buffer" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">速度バッファ:今のフレームと前のフレームの位置の差を、画素に書く</text>
<rect x="40" y="90" width="340" height="240" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<text x="210" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">画面（描画した絵）</text>
<rect x="400" y="90" width="340" height="240" fill="#808080" stroke="#94a3b8" stroke-width="1.5"/>
<text x="570" y="80" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">速度バッファ（色 = 速度の向きと大きさ）</text>
<circle cx="110" cy="210" r="30" fill="#fca5a5" fill-opacity="0.4" stroke="#e5484d" stroke-width="2" stroke-dasharray="4 3"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.3200;0.6000;0.7600;0.8640;1.0000" values="110;110;140;260;260;110;110"/></circle>
<circle cx="110" cy="210" r="30" fill="#e5484d" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.3200;0.6000;0.7600;0.8640;1.0000" values="110;110;200;320;320;110;110"/></circle>
<line x1="110" y1="210" x2="110" y2="210" stroke="#1f2937" stroke-width="3.5"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.3200;0.6000;0.7600;0.8640;1.0000" values="110;110;140;260;260;110;110"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.3200;0.6000;0.7600;0.8640;1.0000" values="110;110;200;320;320;110;110"/></line>
<circle cx="470" cy="210" r="30" fill="#808080"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.3200;0.6000;0.7600;0.8640;1.0000" values="470;470;525.8;600.2;600.2;470;470"/><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0000;0.1200;0.7600" values="#808080;#808080;#ff9030;#808080"/></circle>
<line x1="470" y1="210" x2="470" y2="210" stroke="#1f2937" stroke-width="3"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.3200;0.6000;0.7600;0.8640;1.0000" values="470;470;488.6;563;563;470;470"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.3200;0.6000;0.7600;0.8640;1.0000" values="470;470;525.8;600.2;600.2;470;470"/></line>
<text x="40" y="366" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">各画素に、「前のフレームの位置 → 今の位置」の差（2D ベクトル）を書く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">動いていない物は 0（灰色）。動く物の画素だけ、速度が入る。モーション ブラーや TAA の再投影が、この速度を読む。</text>
</svg>

<!-- fig:velocity-buffer:end -->

## 速度とは

**画素 P が表す 3D の点が、前フレームでは画面のどこにいたか**を**求め、現在位置との差**を**速度**とします。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="速度の定義">
<text x="20" y="26" class="fig-title">速度 ＝ 今のフレームの画面位置 − 前のフレームの画面位置</text>
<g transform="translate(40,56)">
<rect x="0" y="0" width="320" height="150" fill="#f8fafc" stroke="#94a3b8"/>
<circle cx="90" cy="95" r="10" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3"/><text x="70" y="124" style="font-size:12px">前フレームの位置</text>
<circle cx="220" cy="60" r="10" fill="#2563eb"/><text x="190" y="40" style="font-size:12px">今フレームの位置</text>
<line x1="100" y1="90" x2="208" y2="64" stroke="#e5484d" stroke-width="3" marker-end="url(#vb-arrow)"/>
<defs><marker id="vb-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#e5484d"/></marker></defs>
<text x="130" y="68" style="font-size:12px;fill:#e5484d;font-weight:700">速度</text>
</g>
<g font-size="13"><text x="400" y="90" style="font-weight:700">速度バッファの中身</text>
<text x="400" y="116">各画素に、(vx, vy)（2 要素）を保存</text>
<text x="400" y="140">動く物体 → 大きな値、静止した物 → カメラの動き分だけ</text>
<text x="400" y="164">この画像を、ブラー・TAA・アップスケールが読む</text></g>
</svg>

## 書き込み（動く物体）

**物体を描くときに、「今の位置」と「前フレームの位置」を、両方計算**して、**差を出力**します。

```hlsl
cbuffer PerObject : register(b0) {
  float4x4 world;
  float4x4 previous_world;
  float4x4 view_projection;
  float4x4 previous_view_projection;
  float2 jitter_current;
  float2 jitter_previous;
};

struct VSOutput {
  float4 position : SV_POSITION;
  float4 current_clip : TEXCOORD0;
  float4 previous_clip : TEXCOORD1;
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  float4 world_position = mul(float4(input.position, 1.0), world);
  float4 previous_world_position = mul(float4(input.position, 1.0), previous_world);
  output.current_clip = mul(world_position, view_projection);
  output.previous_clip = mul(previous_world_position, previous_view_projection);
  output.position = output.current_clip;
  return output;
}

float2 PSMain(VSOutput input) : SV_Target {
  float2 current_ndc = input.current_clip.xy / input.current_clip.w;
  float2 previous_ndc = input.previous_clip.xy / input.previous_clip.w;
  current_ndc -= jitter_current;
  previous_ndc -= jitter_previous;
  float2 velocity = (current_ndc - previous_ndc) * float2(0.5, -0.5);
  return velocity;
}
```

| 点 | 説明 |
| --- | --- |
| **`previous_world`** | **前フレームのワールド行列**（**物体ごとに、1 フレーム前を覚えておく**） |
| **`previous_view_projection`** | **前フレームのカメラ**（**ジッターなしのもの**） |
| **NDC → UV の差** | **`× (0.5, −0.5)`**（**NDC の Y 向きと、UV の Y 向きは逆**） |
| **ジッターを引く** | **TAA のサブピクセル ジッター**を**差し引いてから比較** |

## カメラの動き（静止した物）

**静止している物体は、カメラが動いたぶんだけ、画面で動く**ので**描画時に書かなくても深度から計算**できます（[Camera Motion Blur](camera-blur.md)）。**動く物体だけが速度バッファに書き込み、書かれていない画素は、カメラの速度**を**使います**。

| 画素 | 速度の出どころ |
| --- | --- |
| **動く物体** | <strong>速度バッファ（書き込み）</strong> |
| <strong>静止した物（書かれていない）</strong> | **深度から再構成したカメラの速度** |

## 精度と形式

| 項目 | 内容 |
| --- | --- |
| **形式** | **`R16G16_FLOAT`**（**2 要素・半精度**） |
| **単位** | **UV（0〜1）または画素**。**UV 単位が解像度に依らない** |
| **精度** | **0.5 画素以下の速度が、区別できる**ことが**重要**（**TAA のため**） |
| **範囲** | **画面を横切る速度（±1 UV）まで** |

**8 ビットは不十分**です（**小さな速度が量子化で消える**）。

## ジッターの扱い

<strong>TAA は毎フレーム、サブピクセル単位でカメラを揺らします（ジッター）</strong>。**速度を揺らした位置どうしで比べる**と、**ジッターの差がすべての画素の速度に混ざり、静止した物がブレます**。

| 対処 | 内容 |
| --- | --- |
| **ジッターを引く** | **現在・前フレームの NDC それぞれから、そのフレームのジッターを引く** |
| **ジッターなしの行列を別に持つ** | **速度計算用の `view_projection`** を**ジッターなし**で作る |

## スキニング・アニメーション

**キャラクターの手足**などは、**前フレームの姿勢**で**頂点位置**を**再計算**する必要があります。

| 方式 | 内容 |
| --- | --- |
| **前フレームのボーン行列を保存** | **スキニングを 2 回（今・前）行う** |
| **前フレームの頂点位置をバッファに保存** | **スキニング後の頂点位置を、スワップして使う** |
| **メッシュ シェーダー** | **頂点位置を今・前で両方計算** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **動く物体だけ書く** | **静止した物は深度から計算**（**帯域節約**） |
| **フラグで書き込みを切る** | **動かない物体は、速度の書き込みを省略** |
| **前フレームの行列をバッファで管理** | **物体ごとに前の行列を保持して、更新** |
| **R16G16 ＋ UV 単位** | **精度と解像度非依存** |
| **TAA・ブラー・アップスケールで共有** | **1 枚を作り、複数の効果が読む** |
| **新しく現れた物体は速度 0** | **初出のフレームで前の行列がないと速度が壊れるので現在 = 前にする** |

## よくあるミス

??? failure "静止している物が、ブラーやゴーストでぼける"
    **ジッターを速度に混ぜている**。**ジッターを引く**。

??? failure "動く物体にだけブラーがかかって、カメラを動かしても背景が流れない"
    **静止した物の速度（カメラ分）が、入っていない**。**深度から再構成**。

??? failure "出現したばかりの物体が、画面を横切る大きな速度で、ひどくぼける"
    **前フレームの行列が無い**。**初出は前の行列 ＝ 現在の行列**にする。

??? failure "速度を 8 ビットで保存して、小さな動きが 0 になる"
    **`R16G16_FLOAT`** にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 速度 ＝ <strong>今の画面位置 − 前フレームの画面位置</strong>
    - [x] <strong>動く物体は描画時に書き込み</strong>、<strong>静止した物は深度から計算</strong>
    - [x] <strong>`R16G16_FLOAT`</strong>。<strong>TAA・ブラーで共有</strong>
    - [x] <strong>ジッターは引く</strong>。<strong>前フレームの行列を保持</strong>
    - [x] <strong>スキニングは前フレームの姿勢で</strong>

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）

## 関連ページ

- [Motion Blur](index.md)
- [Camera Motion Blur](camera-blur.md)
- [Object Motion Blur](object-blur.md)
- [TAA](../antialiasing/taa.md)
