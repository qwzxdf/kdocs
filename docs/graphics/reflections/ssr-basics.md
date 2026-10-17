---
title: SSR の基礎
tags:
  - 描画
---

# SSR の基礎

**SSR**（Screen-Space Reflections、スクリーン空間反射）は、**画面に映っている物だけ**を使って、反射を作る方式です。**深度バッファの上で反射方向にレイを進め**、**面に当たった所の色**をすでに描き終えた**画面の画像から取って**きます。**追加のジオメトリ描画が要らず**、**どんな形の面にも動く物にも**使えるので**ゲームで最も普及している反射**の 1 つです。このページでは、**レイの進め方・当たり判定・厚み・端の処理**など、**SSR の基礎**を順に説明します。

!!! tip "ポイント"
    - 入力は<strong>深度・法線・（粗さ）・シーンの色</strong>。<strong>追加のシーン描画なし</strong>。
    - 反射方向 R に<strong>画面空間でレイを進め</strong>、<strong>各ステップで深度を比べる</strong>。<strong>レイが面の奥に入ったら、当たり</strong>。
    - 当たった画素の<strong>色を、反射として使う</strong>（前フレームか、反射を除いた今のシーン色）。
    - <strong>厚み（thickness）</strong>を設けて、<strong>「薄い物のはるか後ろ」を、当たりにしない</strong>。
    - <strong>画面端・レイが画面外に出る・裏側</strong>は反射できない。<strong>フェードして、フォールバック</strong>。
    - <strong>画面空間の DDA（均等なピクセル歩幅）</strong>が、効率的で標準的。

## 発想

[反射](index.md)で見たとおり、鏡面反射は「**反射方向 R に何が見えるか**」です。SSR は、**R の方向にレイを飛ばして**、**画面の深度バッファを「簡易なシーン」とみなして**、**レイが当たる所**を探します。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="SSR のレイ進行">
<text x="20" y="24" class="fig-title">反射方向のレイを、画面の深度バッファの上で進める。面の奥に入った所が「当たり」</text>
<polygon points="60,230 300,230 300,150 420,150 420,230 720,230 720,270 60,270" fill="rgba(150,150,150,0.3)" stroke="currentColor" stroke-width="2"/>
<text x="330" y="140" style="font-size:12px">壁（深度バッファに映る面）</text>
<circle cx="150" cy="230" r="7" fill="currentColor"/><text x="130" y="254" style="font-size:12px">p（反射する点）</text>
<line x1="150" y1="230" x2="395" y2="120" stroke="#e5484d" stroke-width="3"/>
<g fill="#e5484d"><circle cx="190" cy="212" r="4"/><circle cx="230" cy="194" r="4"/><circle cx="270" cy="176" r="4"/><circle cx="310" cy="158" r="4"/><circle cx="350" cy="140" r="4"/></g>
<circle cx="372" cy="152" r="7" fill="none" stroke="#2ea043" stroke-width="3"/><text x="380" y="190" style="font-size:12px;fill:#2ea043;font-weight:700">当たり（レイ ＞ 面の深度）</text>
<text x="20" y="288" style="font-size:12px">各ステップで、レイの奥行きと、その画素の深度を比べる。レイが面の奥へ潜ったところが交点</text>
</svg>

## 手順

| 手順 | 内容 |
| --- | --- |
| **① 反射方向を求める** | 法線と視線から `R = reflect(視線, 法線)`（ビュー空間） |
| **② レイを作る** | 始点 P（その画素の位置）、方向 R |
| **③ レイを進める** | 画面空間で、**1 ステップずつ**進む |
| **④ 各ステップで当たり判定** | レイの奥行きとその画素の深度を比べる |
| **⑤ 当たった画素の色を取る** | 反射として使う |
| **⑥ 端・粗さ・向きでフェード** | 信頼できない反射を弱める |

## レイの進め方

### 方法 1：ビュー空間の線形マーチ

**ビュー空間**で**一定の長さ**ずつレイを進め、**各点を画面に投影**して深度を比べます。

```hlsl
float3 pos = origin_vs;
for (int i = 0; i < kMaxSteps; ++i) {
  pos += dir_vs * step_length;
  float4 clip = mul(float4(pos, 1.0), projection);
  float2 uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
  float scene_z = LinearDepth(uv);
  if (pos.z > scene_z && pos.z < scene_z + thickness) { hit = true; break; }
}
```

| 問題 | 説明 |
| --- | --- |
| **ステップ長の選択** | 長いと**薄い物を飛び越し**、短いと**ステップ数が増えて重い** |
| **画面上の歩幅が不均一** | **ビュー空間で一定**の長さは、**画面では遠いほど短く、近いほど長い**。無駄・取りこぼし |
| **画面外に出た後も進む** | 無駄な計算 |

### 方法 2：画面空間の DDA（推奨）

**画面上で、1 ピクセルずつ**進みます。**全ての画素を、1 回ずつ確認**でき、**取りこぼしがなく**、**無駄もありません**。McGuire と Mara の方法（「Efficient GPU Screen-Space Ray Tracing」、JCGT 2014）が、標準です。

**透視投影では画面上の直線がビュー空間の直線に対応します**。ただし、**奥行きの補間**は、<strong>`1/z`（または `Q/w`）</strong>で行う必要があります（透視補正）。

| 量 | 補間方法 |
| --- | --- |
| <strong>画面座標 (x, y)</strong> | **線形**（DDA で、1 ピクセルずつ） |
| **`k = 1/w`**（`w` ＝ ビュー空間の `z`） | **線形** |
| **`Q = P_view × k`** | **線形** |
| **レイの奥行き `z`** | `z = Q.z / k` |

```hlsl
bool TraceSSR(float3 origin_vs, float3 dir_vs, float2 jitter,
              out float2 hit_pixel, out float3 hit_vs) {
  float ray_length = (origin_vs.z + dir_vs.z * max_distance < near_z)
      ? (near_z - origin_vs.z) / dir_vs.z : max_distance;
  float3 end_vs = origin_vs + dir_vs * ray_length;

  float4 h0 = mul(float4(origin_vs, 1.0), projection);
  float4 h1 = mul(float4(end_vs, 1.0), projection);
  float k0 = 1.0 / h0.w;
  float k1 = 1.0 / h1.w;
  float3 q0 = origin_vs * k0;
  float3 q1 = end_vs * k1;
  float2 p0 = (h0.xy * k0 * float2(0.5, -0.5) + 0.5) * screen_size;
  float2 p1 = (h1.xy * k1 * float2(0.5, -0.5) + 0.5) * screen_size;

  float2 delta = p1 - p0;
  bool permute = abs(delta.x) < abs(delta.y);
  if (permute) {
    delta = delta.yx; p0 = p0.yx; p1 = p1.yx;
  }

  float step_dir = sign(delta.x);
  float inv_dx = step_dir / delta.x;
  float2 dp = float2(step_dir, delta.y * inv_dx) * stride;
  float3 dq = (q1 - q0) * inv_dx * stride;
  float dk = (k1 - k0) * inv_dx * stride;

  float2 p = p0 + dp * jitter.x;
  float3 q = q0 + dq * jitter.x;
  float k = k0 + dk * jitter.x;

  float prev_z_max = origin_vs.z;
  for (int i = 0; i < kMaxSteps && p.x * step_dir <= p1.x * step_dir; ++i) {
    p += dp; q += dq; k += dk;

    float ray_z_min = prev_z_max;
    float ray_z_max = (dq.z * 0.5 + q.z) / (dk * 0.5 + k);
    prev_z_max = ray_z_max;
    if (ray_z_min > ray_z_max) { float t = ray_z_min; ray_z_min = ray_z_max; ray_z_max = t; }

    hit_pixel = permute ? p.yx : p;
    float scene_z = LinearDepth(hit_pixel);

    if (ray_z_max >= scene_z && ray_z_min <= scene_z + thickness) {
      hit_vs = q * (1.0 / k);
      return true;
    }
  }
  return false;
}
```

| 点 | 説明 |
| --- | --- |
| **近クリップ面の処理** | レイが**カメラの後ろ**（`z < near`）に出ないよう、**近クリップ面で切る** |
| **`permute`** | **x と y のうち、変化が大きい方**を主軸にする（DDA の歩幅を 1 にするため） |
| **`stride`** | **歩幅**（ピクセル）。1 より大きくすると速いが、**薄い物を飛び越す**。**ジッター**で縞を消す |
| **`ray_z_min/max`** | **1 ステップの間のレイの奥行きの範囲**。画素の深度との**区間の重なり**で判定 |
| **`ray_z_max >= scene_z`** | レイが面の**奥**に達した（左手系・+Z が前なので奥ほど z が大きい） |
| **`ray_z_min <= scene_z + thickness`** | レイが面から**厚みの範囲内**にある（はるか後ろではない） |

## 厚み（thickness）

深度バッファには、**面の手前側の位置しか**ありません。**面の「厚み」が分かりません**。レイが**面の奥に入った**とき、それが**本当にその物体に当たった**のか、**物体の向こう側へ抜けた**のかを、区別できません。

| 厚みの設定 | 結果 |
| --- | --- |
| **無限大** | レイが面の奥に入ったら、**常に当たり**。**柱の向こうの別の物を柱の反射として表示** |
| <strong>有限（一定値）</strong> | 面の奥 **thickness 以内**に入ったときだけ、当たり。**薄い物の後ろへ抜けるレイ**は、当たらない |
| **薄すぎる** | **厚みのある物体**でもレイが**深く入った**と判定され、**取りこぼす**（穴が開く） |

**厚みはシーンの大きさ**（メートル単位）**に合わせた値**にします（0.1〜1 m 程度から調整）。**距離に応じて増やす**（遠いほど、画素が大きいので厚みも大きく）と、安定します。

!!! note "厚みの限界"
    **一定の厚み**は**近似**です。**薄い物体**（柵）と**厚い物体**（壁）を、同じ値で扱えません。**限界**として、受け入れる設計です。

## 当たりの精密化

**歩幅が 1 より大きい**と、**当たりの位置が粗く**（歩幅分のずれ）なります。**当たった後**に**区間を二分探索**で精密化します。

```hlsl
float2 RefineHit(float2 p_before, float2 p_after, int steps) {
  float2 lo = p_before;
  float2 hi = p_after;
  for (int i = 0; i < steps; ++i) {
    float2 mid = (lo + hi) * 0.5;
    if (RayIsBehindSurface(mid)) hi = mid; else lo = mid;
  }
  return hi;
}
```

**2〜5 回**の二分探索で、**歩幅の誤差がほぼ無くなります**。

## 色の取得

**当たった画素の色**を反射として使います。**どの画像から取るか**が重要です。

| 取得元 | 利点 | 欠点 |
| --- | --- | --- |
| **今のフレームの、SSR を除いたシーン色** | 最新 | **SSR を適用する前の画像**が必要（**反射のパスの前**の色を残す） |
| **前フレームの最終画像** | 手軽（すでに反射・ポストが乗っている） | **1 フレーム遅れる**（動く物にずれ）。**反射の反射**が入る（二重） |
| **前フレームを動きベクトルで再投影** | 遅れの補正 | 動きベクトルが必要 |

**多くの実装は前フレームの最終画像**（**ブルーム前**の HDR）を使い、**動きベクトルで再投影**します。

## フェード：信頼できない反射を弱める

SSR は**画面にあるものしか映せません**。**信頼できない反射**は、**フェード**して、**フォールバック**（[フォールバック](ssr-fallback.md)）に任せます。

| 要因 | 内容 |
| --- | --- |
| **画面端** | 当たりが**画面の端に近い**ほど、弱める（`edge_fade = saturate((0.5 − |uv − 0.5|) / margin)`） |
| **レイの長さ** | 遠いほど、弱める（遠くの当たりは不確か） |
| **粗さ** | 粗いほど、弱める（SSR はくっきりした反射が得意） |
| **向き** | **反射がカメラの方へ戻る**（`R·V` が負で大きい）場合は**画面に映っていない面**を指す。弱める |
| **厚みの検証** | 当たった場所の**深度差**が、不自然なら、弱める |
| **当たらなかった** | 信頼度 0（フォールバックのみ） |

```hlsl
float SSRConfidence(float2 hit_uv, float ray_length, float roughness, float3 R_vs) {
  float2 d = abs(hit_uv - 0.5) * 2.0;
  float edge = 1.0 - smoothstep(0.8, 1.0, max(d.x, d.y));
  float distance_fade = 1.0 - saturate(ray_length / max_distance);
  float rough_fade = 1.0 - saturate(roughness / max_roughness);
  float facing = saturate(1.0 + R_vs.z * 4.0);
  return edge * distance_fade * rough_fade * facing;
}
```

## 解像度とコスト

| 方式 | 内容 |
| --- | --- |
| **フル解像度** | 高品質。重い |
| **半分の解像度** | **レイを半分の解像度**で飛ばし、**拡大**（バイラテラル）。**4 分の 1 のコスト** |
| **ステップ数の上限** | 32〜64 程度。**1 ステップが深度のテクスチャ読み込み 1 回** |
| **歩幅 stride** | 大きいと速い（薄い物を飛ぶ）。**ジッターで縞を分散** |
| **粗い面はレイを減らす** | 粗さがしきい値以上の画素は、**SSR をやめる**（プローブへ） |
| **マスク** | 反射しない面（粗さ 1・非金属で粗い）を、**ステンシルやタイル分類**で除外 |

## 問題点（アーティファクト）

| 症状 | 原因 | 対策 |
| --- | --- | --- |
| **反射が画面の端で消える・切れる** | 画面外のものは、映らない | エッジ フェード・フォールバック |
| <strong>反射に、「穴」「縞」</strong> | 歩幅が大きすぎて、薄い物を飛び越す | 歩幅を小さく・厚みの調整・Hi-Z（[Hi-Z SSR](ssr-hiz.md)） |
| **反射が物の裏側を映さない** | 深度バッファは、手前の面だけ | 仕様。フォールバック |
| **物の反射が引き伸ばされる** | 厚みが大きすぎて、手前の物に当たり続ける | 厚みの調整 |
| **動く物体にずれ・ゴースト** | 前フレームの色を使う | 動きベクトルで再投影 |
| **反射する物体自身が映る** | レイが自分の面に当たる | 始点を法線方向に少しずらす |
| **透明物が映らない** | 半透明は深度に書かれない | 仕様。別扱い |
| **粗い面の反射がくっきりしすぎる** | 粗さを考慮していない | ぼかし・確率的 SSR（[確率的 SSR](ssr-stochastic.md)） |

## 粗さへの簡易対応

**粗い面**の反射は、**ぼやけるべき**です。**簡易的**には次のようにします。

| 方法 | 内容 |
| --- | --- |
| <strong>色のミップ（ぼかしピラミッド）</strong> | シーン色の**ミップ**を作り、**粗さ**または**レイの長さ**に応じて、**ミップを選ぶ**（距離が遠く、粗いほど、ぼけた色） |
| **コーン トレース風** | **レイの距離に応じて、反射の円錐が広がる**ことを、ミップ選択で表す |
| **ぼかし** | 反射の画像全体を粗さでぼかす（境界のにじみ） |

**確率的な方式**（[確率的 SSR](ssr-stochastic.md)）は、**GGX の分布からレイをサンプル**して、**ぼけを物理的に正しく**得ます。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **追加のシーン描画なし**（軽い） | **画面に映らない物は、反射しない** |
| **あらゆる形の面・動く物に使える** | **厚み・歩幅の調整**が難しい |
| **接地の細かい反射**（足元）に強い | 画面端・視点の変化で**反射が現れたり消えたり** |
| **深度・法線・色があれば作れる** | **ノイズ・にじみ**（粗い面） |

## よくあるミス

??? failure "歩幅を大きくして、薄い物を飛び越して、反射に穴が開く"
    歩幅を小さくするか、**Hi-Z**（[Hi-Z SSR](ssr-hiz.md)）にします。

??? failure "厚みを無限にして、手前の物の反射に後ろの物が引き伸ばされて映る"
    **有限の厚み**を設定します。

??? failure "画面外に出たレイの結果を、そのまま使い、画面の端で破綻する"
    **エッジ フェード**し、**フォールバック**に任せます。

??? failure "SSR 適用後の画像を、同じフレームの反射の入力にして、無限にループする"
    **SSR を適用する前の色**（または前フレーム）を入力にします。

??? failure "レイの始点が、面にめり込んで自分自身に当たる"
    始点を法線方向に少しずらします（バイアス）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSR ＝ <strong>深度バッファの上で、反射方向にレイを進め、当たった画素の色を反射にする</strong>
    - [x] <strong>画面空間の DDA</strong>（1 ピクセルずつ）が標準。<strong>透視補正（`1/w`）</strong>が必要
    - [x] <strong>厚み</strong>で<strong>薄い物の向こう側への誤った当たり</strong>を防ぐ
    - [x] <strong>画面端・遠さ・粗さ・向き</strong>で<strong>フェード</strong>し、フォールバックへ
    - [x] 弱点は<strong>画面に無い物が映らない</strong>こと。<strong>プローブ・平面反射と組み合わせる</strong>

## 参考

- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing"（Journal of Computer Graphics Techniques, 2014）
- Sousa et al., "CryEngine 3 Graphics Gems"（SIGGRAPH 2013、SSR の実用化）

## 関連ページ

- [反射](index.md)
- [Hi-Z SSR](ssr-hiz.md)
- [確率的 SSR](ssr-stochastic.md)
- [SSR のフォールバックと合成](ssr-fallback.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
