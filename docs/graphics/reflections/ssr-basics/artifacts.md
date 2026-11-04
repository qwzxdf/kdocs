---
title: Artifacts and Evaluation
tags:
  - 描画
---

# Artifacts and Evaluation

SSR を入れるとまず見た目の不具合に悩まされます。反射が画面の端で切れる柱の裏に穴があく、細い手すりが映らない動くと反射がちらつく。SSR は画面に映っている深度と色だけで反射を作るので、不具合には決まった原因があります。原因が分かればデバッグ表示で見分けて、直す場所も決まります。

このページは SSR の代表的な不具合を症状ごとに説明して、原因と対処を数字つきで書きます。最後に、不具合の原因を見分けるためのデバッグ表示つきの HLSL を載せます。

!!! tip "ポイント"
    最大の弱点は画面に映らない物や物の裏側が反射に映らないことです。ここから画面端の欠け反射の穴、薄い物の取りこぼし縁の引き伸ばしが出ます。動くとちらつくのは時間方向の問題です。代わりにシーンが複雑でもコストがほぼ一定という大きな長所があります。弱点はフォールバックで補います。

!!! info "このページを読む前に"
    - [SSR Basics](index.md)（このセクション全体の地図と読む順番）
    - [Linear Marching](linear-march.md)（レイを進める方法。歩幅と歩数の考え方）
    - [Thickness](thickness.md)（当たりの判定に使う厚み）

## 症状から原因をたどる

不具合はデバッグ表示を見ると原因を絞れます。次の図は症状ごとに何を見るかをまとめたものです。表示の番号はこの後の HLSL の `DEBUG_VIEW` の番号です。

<svg class="fig flow" viewBox="0 0 680 330" role="img" aria-label="症状から、見るデバッグ表示と原因をたどる"><defs><marker id="sA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">症状 → 見る表示 → 原因</text><rect x="14" y="40" width="200" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="114.0" y="61.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">画面端で反射が切れる</text><line x1="214" y1="61" x2="244" y2="61" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="246" y="40" width="180" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="336.0" y="61.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">表示 1：青</text><line x1="426" y1="61" x2="456" y2="61" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="458" y="40" width="210" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="563.0" y="61.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">レイが画面の外へ出た</text><rect x="14" y="94" width="200" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="114.0" y="115.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">反射に穴・縞</text><line x1="214" y1="115" x2="244" y2="115" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="246" y="94" width="180" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="336.0" y="115.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">表示 3：白に近い</text><line x1="426" y1="115" x2="456" y2="115" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="458" y="94" width="210" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="563.0" y="115.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">厚みが合っていない</text><rect x="14" y="148" width="200" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="114.0" y="169.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">細い物が映らない</text><line x1="214" y1="169" x2="244" y2="169" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="246" y="148" width="180" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="336.0" y="169.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">表示 2：白に近い</text><line x1="426" y1="169" x2="456" y2="169" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="458" y="148" width="210" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="563.0" y="169.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">歩幅が粗い／歩数切れ</text><rect x="14" y="202" width="200" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="114.0" y="223.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">自分の面が映る</text><line x1="214" y1="223" x2="244" y2="223" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="246" y="202" width="180" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="336.0" y="223.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">表示 1：緑が近距離</text><line x1="426" y1="223" x2="456" y2="223" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="458" y="202" width="210" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="563.0" y="223.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">始点のずらし不足</text><rect x="14" y="256" width="200" height="42" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="114.0" y="277.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ちらつく・ゴースト</text><line x1="214" y1="277" x2="244" y2="277" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="246" y="256" width="180" height="42" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="336.0" y="277.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">表示 1 を数フレーム</text><line x1="426" y1="277" x2="456" y2="277" stroke="currentColor" stroke-width="2" marker-end="url(#sA)"/><rect x="458" y="256" width="210" height="42" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="563.0" y="277.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ジッター／履歴の古さ</text></svg>

## 症状ごとの説明

### 画面の端で反射が切れる

レイが画面の外に出るとそこには深度も色もありません。画面の端に近い反射ほどレイがすぐ外へ出るので、反射が欠けたり急に消えたりします。

対処は 2 つあります。1 つ目はエッジ フェードで、当たり点が端に近いほど信頼度を下げます。端から画面幅の 10 % でフェードするなら 1920 画素の画面で約 192 画素です。急に切り替えると境目が見えるので、`smoothstep` でなめらかに落とします。2 つ目はフォールバックで信頼度が落ちた分をプローブなどで補います（[SSR Fallback and Compositing](../ssr-fallback.md)）。

### 反射の穴

反射する面の前に物があるとその物の裏側にあるはずの景色は、画面に映っていません。深度バッファは手前の面しか持たないからです。レイが物の前面の後ろに入ると、そこは「物の内部」で裏側の景色の情報はなく、反射は欠けて黒くなったり背景が見えたりします。

これは SSR の根本的な限界で、レイを賢くしても直りません。プローブなど画面の外の情報を持つ手段で埋めます（[Combining with SSR](../probes/combine-ssr.md)）。

### 薄い物を飛び越す

レイを一定の歩幅で進めると歩幅より細い物は、標本点の間に入ると見えません。次の図は幅 2 画素の物と歩幅 4 画素の標本点です。

<svg class="fig flow" viewBox="0 0 680 250" role="img" aria-label="歩幅 4 画素の標本点は、幅 2 画素の物を飛び越す。歩幅 1 画素なら 3 点が入る"><text x="14" y="22" class="fig-title">歩幅と、薄い物の取りこぼし（横軸＝画面の画素）</text><line x1="40" y1="90" x2="616" y2="90" stroke="#94a3b8" stroke-width="2"/><rect x="274" y="62" width="36" height="28" fill="rgba(229,170,40,0.35)" stroke="#e5aa28" stroke-width="2"/><text x="292" y="52" text-anchor="middle" style="font-size:12px;font-weight:600">幅 2 画素の物（13〜15）</text><text x="14" y="112" style="font-size:12px;font-weight:600">歩幅 4 画素</text><circle cx="40" cy="130" r="5" fill="#4c8bf5"/><text x="40" y="152" text-anchor="middle" style="font-size:10px">0</text><circle cx="112" cy="130" r="5" fill="#4c8bf5"/><text x="112" y="152" text-anchor="middle" style="font-size:10px">4</text><circle cx="184" cy="130" r="5" fill="#4c8bf5"/><text x="184" y="152" text-anchor="middle" style="font-size:10px">8</text><circle cx="256" cy="130" r="5" fill="#4c8bf5"/><text x="256" y="152" text-anchor="middle" style="font-size:10px">12</text><circle cx="328" cy="130" r="5" fill="#4c8bf5"/><text x="328" y="152" text-anchor="middle" style="font-size:10px">16</text><circle cx="400" cy="130" r="5" fill="#4c8bf5"/><text x="400" y="152" text-anchor="middle" style="font-size:10px">20</text><circle cx="472" cy="130" r="5" fill="#4c8bf5"/><text x="472" y="152" text-anchor="middle" style="font-size:10px">24</text><circle cx="544" cy="130" r="5" fill="#4c8bf5"/><text x="544" y="152" text-anchor="middle" style="font-size:10px">28</text><circle cx="616" cy="130" r="5" fill="#4c8bf5"/><text x="616" y="152" text-anchor="middle" style="font-size:10px">32</text><text x="184" y="112" style="font-size:12px;fill:#e5484d;font-weight:600">13〜15 に点がない → 飛び越す</text><text x="14" y="182" style="font-size:12px;font-weight:600">歩幅 1 画素</text><circle cx="40" cy="200" r="3" fill="#4c8bf5"/><circle cx="58" cy="200" r="3" fill="#4c8bf5"/><circle cx="76" cy="200" r="3" fill="#4c8bf5"/><circle cx="94" cy="200" r="3" fill="#4c8bf5"/><circle cx="112" cy="200" r="3" fill="#4c8bf5"/><circle cx="130" cy="200" r="3" fill="#4c8bf5"/><circle cx="148" cy="200" r="3" fill="#4c8bf5"/><circle cx="166" cy="200" r="3" fill="#4c8bf5"/><circle cx="184" cy="200" r="3" fill="#4c8bf5"/><circle cx="202" cy="200" r="3" fill="#4c8bf5"/><circle cx="220" cy="200" r="3" fill="#4c8bf5"/><circle cx="238" cy="200" r="3" fill="#4c8bf5"/><circle cx="256" cy="200" r="3" fill="#4c8bf5"/><circle cx="274" cy="200" r="3" fill="#e5aa28"/><circle cx="292" cy="200" r="3" fill="#e5aa28"/><circle cx="310" cy="200" r="3" fill="#e5aa28"/><circle cx="328" cy="200" r="3" fill="#4c8bf5"/><circle cx="346" cy="200" r="3" fill="#4c8bf5"/><circle cx="364" cy="200" r="3" fill="#4c8bf5"/><circle cx="382" cy="200" r="3" fill="#4c8bf5"/><circle cx="400" cy="200" r="3" fill="#4c8bf5"/><circle cx="418" cy="200" r="3" fill="#4c8bf5"/><circle cx="436" cy="200" r="3" fill="#4c8bf5"/><circle cx="454" cy="200" r="3" fill="#4c8bf5"/><circle cx="472" cy="200" r="3" fill="#4c8bf5"/><circle cx="490" cy="200" r="3" fill="#4c8bf5"/><circle cx="508" cy="200" r="3" fill="#4c8bf5"/><circle cx="526" cy="200" r="3" fill="#4c8bf5"/><circle cx="544" cy="200" r="3" fill="#4c8bf5"/><circle cx="562" cy="200" r="3" fill="#4c8bf5"/><circle cx="580" cy="200" r="3" fill="#4c8bf5"/><circle cx="598" cy="200" r="3" fill="#4c8bf5"/><circle cx="616" cy="200" r="3" fill="#4c8bf5"/><text x="14" y="232" style="font-size:12px">物の幅（画素）が歩幅より小さいと、標本点が物に入らないことがある。</text></svg>

歩幅 4 画素の標本点は 0、4、8、12、16 の位置で 13 から 15 に入った物には 1 点も当たりません。歩幅 1 画素なら 13、14、15 の 3 点が物に入ります。一方で、レイの長さを 512 画素とすると、歩数は歩幅 4 なら 128 歩、歩幅 1 なら 512 歩で、コストは 4 倍です。歩幅を細かくするほど確実に当たる代わりにコストが増えます。

直し方は 3 つです。歩幅を細かくする二分探索で当たりの位置を詰める（[Linear Marching](linear-march.md)）、Hi-Z で大きな歩幅でも物を飛び越さないようにする（[Hi-Z SSR](../ssr-hiz.md)）。歩数切れ（`MAX_STEPS` を使い切る）で外れになる場合も薄い物が映らないように見えるので、歩数の表示で見分けます。

### 縁の引き伸ばし

当たりの判定はレイ上の点の深度が、その画素の深度より奥にあり差が厚み以内なら当たりというものです。厚みが大きすぎると物の縁のすぐ後ろにある遠い背景まで、同じ物に当たったと誤認します。結果、物の色が縞のように背景へ引き伸ばされます。

直し方は厚みを小さくすることです。ただし小さくしすぎると厚みのある物の内側を通り抜けて、穴が増えます。厚みは距離に比例させるのが目安で、遠くのほうが 1 画素が表す距離が大きいからです（[Thickness](thickness.md)）。当たった面の法線を確認して反射レイの方を向いている面だけを有効にする方法もあります。

### 自分の面に当たる

レイの始点が反射する面そのものの上にあると、最初の 1 歩で自分に当たり反射する物自身が映ります。始点を法線方向に少しずらします。ずらしすぎると接地部が浮くので、距離の 1 % 程度（コードでは `0.01 * depth`）を一例にして、画面で見ながら調整します。

### 地面に突き抜ける

視線と面のなす角が浅いと反射ベクトルがほぼ面と平行になりレイが面の下に入ったり、歩数を使い切ったりします。反射ベクトルを法線側へ押し戻すか始点を面から少し離します。浅い角度ではフレネルで反射が強く出るので、欠けが目立ちます。

### 動く物のゴーストと遅れ

反射の色を前フレームの画像から読むと動く物の反射が遅れます。60 fps なら 1 フレームは約 16.7 ms で、物が 1 フレームで 10 画素動けば、反射は 10 画素ぶん古い位置に残ります。動きベクトルで再投影して前フレームの位置を読むか今フレームの色を読みます。再投影しても履歴が古くなるので、履歴を現在の近傍の最小値と最大値でクランプします。

### ちらつきとノイズ

歩幅の開始位置や反射方向をフレームごとにずらすと反射がちらつきます。ブルー ノイズとフレーム番号でずらして、TAA か時間蓄積で平均します。粗い面で確率的に反射方向を選ぶとざらつきが出ます。時間蓄積と空間フィルタで減らします（[Stochastic SSR](../ssr-stochastic.md)）。

### 半透明が映らない

半透明は深度に書かれないので、SSR には映りません。ガラスや水の反射は専用の手段（平面反射やプローブ）でシェーダーの中に作ります。

## 長所と短所

長所はシーンが複雑でもコストがほぼ一定なことです。レイトレーシングは三角形が増えるほど遅くなりますが、SSR は画素数と歩数で決まります。1920 × 1080 を半分の解像度でトレースすると 960 × 540 = 518,400 本のレイで、最大 64 歩なら深度の読み出しは 33,177,600 回、フル解像度だと 2,073,600 本で 132,710,400 回です。接地した足元の細かい反射に強く、あらゆる形の面と動く物に使えます。追加の描画も要りません。

短所は画面に映らない物を反射しないことです。画面端や視点の変化で反射が現れたり消えたりします。厚みと歩幅の調整は難しく粗い面ではノイズやにじみが出ます。

## デバッグ表示つきの SSR

ここから不具合の原因を見分けるためのコードを載せます。画面空間でレイを進める最小の実装と 4 つのデバッグ表示です。`fxc`（`ps_5_0`）で 5 つの `DEBUG_VIEW` すべてを警告なしでコンパイルして確かめました。実行はしていません。実際のシーンでの見た目の確認は自分のシーンで行ってください。

### 入力とパラメーター

```hlsl
// ssr_debug.hlsl : 画面空間のレイ進め（簡易）と、アーティファクトの原因を見分けるデバッグ表示。
// DEBUG_VIEW: 0=通常 1=結果（緑=当たり 赤=外れ 青=画面の外） 2=歩数 3=当たり点の厚み誤差 4=信頼度
#ifndef DEBUG_VIEW
#define DEBUG_VIEW 0
#endif
#define MAX_STEPS 64

Texture2D<float>  g_depth  : register(t0);   // 線形のビュー深度（カメラからの距離。大きいほど遠い）
Texture2D<float4> g_normal : register(t1);   // xyz = ビュー空間の法線
Texture2D<float4> g_color  : register(t2);   // シーンの色
SamplerState g_point       : register(s0);

cbuffer SsrParams : register(b0) {
  float4x4 g_proj;           // ビュー → クリップ
  float2   g_inv_focal;      // (1 / proj[0][0], 1 / proj[1][1])。UV からビュー空間へ戻す
  float    g_step_px;        // 1 歩の長さ（画素）。大きいほど速いが、薄い物を飛び越す
  float    g_thickness;      // 厚み（ビュー空間の単位）。当たりと見なす深度差の幅
  float    g_max_dist;       // レイの最大の長さ（ビュー空間の単位）
  float3   g_pad;
};
```

深度はカメラからの距離で表した線形のビュー深度です。非線形の深度バッファの値をそのまま比べると、厚みの意味が距離で変わってしまうので、先に線形化しておきます。`g_step_px` と `g_thickness` が前の節の「歩幅」と「厚み」です。画面上の歩幅は画素で厚みはビュー空間の単位なので、単位が違う点に注意してください。

### 座標変換とレイを進める関数

```hlsl
float3 ViewPos(float2 uv, float depth) {
  float2 ndc = float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  return float3(ndc * g_inv_focal * depth, depth);   // 左手系・+Z が前。z = 線形深度
}

float2 ToUv(float3 v) {
  float4 c = mul(float4(v, 1.0), g_proj);
  return float2(c.x / c.w * 0.5 + 0.5, 0.5 - c.y / c.w * 0.5);
}

struct Hit { bool hit; bool off; float2 uv; uint steps; float depth_error; };

Hit March(float3 origin, float3 dir, float2 screen) {
  Hit h = (Hit)0;
  // 始点を法線方向へ少しずらす（足した処理）。自分の面に当たる「自己交差」を防ぐ。
  float3 p = origin;
  float3 step_v = dir * (g_step_px / screen.y) * 2.0 * origin.z / g_proj._22;   // 1 歩 ≒ g_step_px 画素
  for (uint i = 0; i < MAX_STEPS; ++i) {
    p += step_v;
    h.steps = i + 1;
    if (p.z <= 0.0 || length(p - origin) > g_max_dist) { h.off = true; return h; }   // カメラの後ろ・遠すぎ
    float2 uv = ToUv(p);
    if (any(uv < 0.0) || any(uv > 1.0)) { h.off = true; return h; }                // 画面の外
    float scene = g_depth.SampleLevel(g_point, uv, 0);
    float diff = p.z - scene;                    // 正 = レイが面の奥にある
    if (diff > 0.0 && diff < g_thickness) {      // 面の裏へ厚み以内に入った = 当たり
      h.hit = true; h.uv = uv; h.depth_error = diff; return h;
    }
  }
  return h;                                      // 歩数切れ: 外れとして扱う
}
```

`ViewPos` は UV と線形深度からビュー空間の位置を戻し、`ToUv` は逆にビュー空間の点を UV へ射影します。`March` はビュー空間で一定の長さずつ進み各歩で射影して深度を読みます。1 歩の長さは始点の深度で見たときに画面上で約 `g_step_px` 画素になるように決めた近似です。遠くへ進むほど画面上の歩幅は縮みます。これが [Linear Marching](linear-march.md) の「3D では不均等」の理由です。

当たりの判定は `0 < diff < thickness` です。`diff` が負ならレイは面の手前にいて、まだ当たっていません。`diff` が厚みを超えるとレイは面を通り抜けた（その奥にいる）ので、当たりではありません。戻り値の `off` は画面の外・カメラの後ろ・遠すぎのいずれかで終わったことを表し、歩数切れの外れと区別します。デバッグ表示で青（画面の外）と赤（歩数切れや通り抜け）を分けて見るためです。

### 呼び出しとデバッグ表示

```hlsl
float4 main(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float2 screen = float2(1920.0, 1080.0);        // 実際は定数で渡す
  float depth = g_depth.SampleLevel(g_point, uv, 0);
  float3 n = normalize(g_normal.SampleLevel(g_point, uv, 0).xyz);
  float3 p = ViewPos(uv, depth);
  float3 r = reflect(normalize(p), n);           // 視線を法線で反射
  Hit h = March(p + n * 0.01 * depth, r, screen);

  float2 e = abs((h.hit ? h.uv : uv) - 0.5) * 2.0;
  float conf = h.hit ? (1.0 - smoothstep(0.85, 1.0, max(e.x, e.y))) : 0.0;   // 端のフェード

#if DEBUG_VIEW == 1
  return h.hit ? float4(0, 1, 0, 1) : (h.off ? float4(0, 0, 1, 1) : float4(1, 0, 0, 1));
#elif DEBUG_VIEW == 2
  return float4((h.steps / (float)MAX_STEPS).xxx, 1);     // 白に近い = 歩数をほぼ使い切った
#elif DEBUG_VIEW == 3
  return float4((h.depth_error / g_thickness).xxx, 1);    // 白 = 厚みの縁ぎりぎりで当たった（疑わしい）
#elif DEBUG_VIEW == 4
  return float4(conf.xxx, 1);
#else
  float3 refl = h.hit ? g_color.SampleLevel(g_point, h.uv, 0).rgb : float3(0, 0, 0);
  return float4(refl, conf);                              // rgb = 反射色、a = 信頼度
#endif
}
```

反射ベクトルはビュー空間では視線が `normalize(p)`（原点から点へ）なので、`reflect` でそのまま求められます。始点を法線方向へ `0.01 * depth` ずらしているのは、自己交差の対策です。エッジ フェードの信頼度 `conf` は当たり点の座標（画面中心 0、端 1）が 0.85 を超えると 0 へ向かいます。1920 画素の幅なら片側で端から約 144 画素です。

デバッグ表示は 4 つです。表示 1 は当たり（緑）・画面の外（青）・外れ（赤）です。画面端で青が増えていれば端の欠けです。表示 2 は歩数の使用率で白に近い画素は歩数切れが疑わしい場所です。表示 3 は当たり点の深度誤差を厚みで割った値で、白に近い画素は厚みの縁ぎりぎりで当たった偽の当たりの候補です。表示 4 は信頼度でフェードが効きすぎ・足りないかを確かめます。

## よくあるミス

??? failure "画面の端で、反射が途切れる"
    レイが画面の外に出た画素が、そのまま黒になっています。表示 1 で青い範囲を確かめエッジ フェードの信頼度を下げて、フォールバックのプローブとなだらかにつなぎます。

??? failure "細い手すりが反射に映らない"
    歩幅が手すりの幅より粗いか歩数切れです。表示 2 が白に近ければ歩数切れで、歩数を増やすか Hi-Z にします。そうでなければ歩幅を細かくして、映るか確かめます。

??? failure "反射に縞が出る"
    厚みが大きすぎます。表示 3 が白に近い画素が縞に重なっていれば、厚みの縁での偽の当たりです。厚みを小さくして距離に比例させます。

??? failure "デバッグ表示を本番の設定で見ている"
    解像度を半分にしたりジッターをかけたりした状態で表示を見ると、画面がまだらで原因が分かりません。デバッグ中はジッターを止めて、フル解像度で固定します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSR の最大の弱点は、画面に映らない物と物の裏側が映らないこと
    - [x] 歩幅が物の幅より粗いと飛び越し、厚みが大きいと縁が引き伸ばされる
    - [x] 症状ごとにデバッグ表示を見て、原因を絞る
    - [x] 弱点はフォールバックで補う

## 参考

このページは同じセクションの各ページ（SSR Basics、Linear Marching、Thickness、Color Lookup and Fading、Cost and Roughness）をもとに症状ごとにまとめ直したものです。次の資料はこのページを書くために読み直していません。歩数・読み出し回数・動きの画素数はこのページで計算した一例です。

- Morgan McGuire, Michael Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014.（画面空間のレイ進めと厚み）
- Tomasz Stachowiak, Yasin Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games.（Frostbite の SSR）
- Bart Valient, "Reflections and Volumetrics of Killzone Shadow Fall", SIGGRAPH 2014, Advances in Real-Time Rendering in Games.
- Yasin Uludag, "Hi-Z Screen-Space Cone-Traced Reflections", GPU Pro 5, CRC Press, 2014.
- Tomas Akenine-Möller, Eric Haines, Naty Hoffman, Angelo Pesce, Michał Iwanicki, Sébastien Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018.（反射と IBL の章）

## 関連ページ

- [SSR Basics](index.md)
- [SSR Fallback and Compositing](../ssr-fallback.md)
- [Reflection Comparison](../comparison.md)
- [Linear Marching](linear-march.md)
- [Thickness](thickness.md)
