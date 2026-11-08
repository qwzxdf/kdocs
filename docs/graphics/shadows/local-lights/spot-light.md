---
title: Spot Lights
tags:
  - 描画
---

# Spot Lights

懐中電灯や街灯のような光は円錐の中だけを照らします。円錐の外には光が届かないので、影も円錐の中だけ作れば足ります。光の位置から円錐の中心を向いた、透視投影の 1 枚のシャドウ マップです。平行光（太陽）の正射影と違って、光から遠い所ほど 1 テクセルが大きくなり影の粗さが距離で変わります。

このページではスポットライトのシャドウ マップの作り方、視野角の決め方、距離による解像度の変化、深度の精度とバイアス、複数のスポットライトの置き方を説明します。

!!! tip "ポイント"
    - スポットライトの影は透視投影の 1 枚のシャドウ マップです。
    - 視野角は円錐の全角（外側の角度）にします。縁で影が切れないように少し余裕を持たせます。
    - 透視投影の深度は距離に対して非線形です。近い所に精度が集まるので近クリップ面を小さくしすぎないことが大切です。
    - 近い面・遠い面はライトの範囲に合わせます。

!!! info "このページを読む前に"
    - [Point and Spot Light Shadows](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

## スポットライトの影は 1 枚

スポットライトの光は位置・向き・円錐の角度で決まります。円錐の外には光が届かないので、円錐を覆う透視投影のシャドウ マップ 1 枚で済みます。シャドウ マップは正方形の 1 枚です。

ビュー行列はライトの位置と向きから作ります。射影行列は視野角を円錐の全角、アスペクト比を 1、近遠をライトの範囲にして作ります。

スポットライトの影は 1 枚で済むので、ローカル ライトの影の中では最も安く、品質も安定しています。そのため、点光源を向きの違う複数のスポットライトで近似したりどうしても点光源の影が必要な所だけキューブ マップを使ったりする設計もよく行われます（[Point Lights: Cube Maps](point-cubemap.md)）。

<svg class="fig illust" viewBox="0 0 640 240" role="img" aria-label="スポットライトの円錐と、シャドウ マップの視錐台">
<text x="20" y="24" class="fig-title">円錐を覆う透視投影が、シャドウ マップの視錐台になる</text>
<polygon points="80,120 540,30 540,210" fill="rgba(229,170,40,0.22)" stroke="currentColor" stroke-width="2"/>
<polygon points="80,120 480,56 480,184" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/>
<line x1="80" y1="120" x2="540" y2="120" stroke="currentColor" stroke-width="1" stroke-dasharray="4 4"/>
<circle cx="80" cy="120" r="7" fill="rgba(229,170,40,0.8)" stroke="currentColor"/>
<text x="40" y="146" style="font-size:12px">光の位置</text>
<text x="400" y="26" style="font-size:12px">視錐台(fov = 外側の角 × 2 + 余裕)</text>
<text x="330" y="106" style="font-size:12px">円錐(光が当たる範囲)</text>
<text x="20" y="222" style="font-size:12px">視錐台が円錐より少し広い → 縁のぎりぎりまで、影が切れずに判定できる</text>
</svg>

### 光の行列を作る

```cpp
using namespace DirectX::SimpleMath;

// スポットライトの、光の行列(左手系、行ベクトル)。
Matrix SpotLightMatrix(const SpotLight& spot) {
  Vector3 position = spot.position;                      // 光の位置(ビューの原点)
  Vector3 target = spot.position + spot.direction;       // 光の向きの先(direction は単位ベクトル)
  // 上方向は、光の向きと平行にならない軸を選ぶ(平行だとビュー行列が作れない)。
  Vector3 up = (std::abs(spot.direction.y) > 0.99f) ? Vector3::UnitZ : Vector3::UnitY;
  Matrix view = DirectX::XMMatrixLookAtLH(position, target, up);   // ワールド → 光のビュー

  // 視野角 = 外側の円錐の全角。170° を超えない(透視投影が破綻する)。
  float fov = std::min(2.0f * spot.outer_angle, DirectX::XMConvertToRadians(170.0f));
  Matrix proj = DirectX::XMMatrixPerspectiveFovLH(fov, 1.0f, spot.near_z, spot.range);   // アスペクト比 1
  return view * proj;                                    // 行ベクトルなので view → proj の順
}
```

このコードはコンパイルして確かめていません。`SpotLight` は説明のための構造体で位置・向き・外側の角度（半角、ラジアン）・近クリップ面・到達距離を持つものとして扱います。

上方向の選び方に注意します。真上を向くスポットライト（街灯やスタジオのライト）の向きは、Y 軸とほぼ平行です。そのまま Y を上にすると `XMMatrixLookAtLH` は外積が 0 になって、行列が壊れます。そこで、向きの Y 成分の絶対値が 0.99 を超えたら、Z 軸を上にします。

視野角を 170° で止めるのは、透視投影の `tan(fov/2)` が 180° で発散するからです。広い円錐のスポットライトは 170° に収まらない範囲をキューブ マップに切り替えるほうが安全です。

3 つの値の目安を整理します。

- `fov` は外側の円錐の半角の 2 倍にします。円錐がちょうどシャドウ マップに収まります。
- `near_z` は 0.1 から 1 m です。できるだけ大きくして深度の精度を守ります。
- `range` は光の到達距離でファー面にします。これを超えた所は光が当たりません。

## 距離による解像度の変化

透視投影のシャドウ マップは光から遠いほど 1 テクセルが世界で広い範囲を覆います。距離を d、視野角を fov、解像度を R とすると距離 d での 1 テクセルの大きさは、次の式です。

> 1 テクセルの世界での大きさ ＝ 2 × d × tan(fov / 2) ÷ R

視野角 90° のスポットライトで、解像度が 1024 のとき距離 5 m で約 0.0098 m（約 1 cm）、10 m で約 0.0195 m（約 2 cm）、20 m で約 0.039 m（約 4 cm）です。距離に比例してテクセルが大きくなります。同じ 1024 でも視野角が 60° なら 10 m で約 0.0113 m、120° なら約 0.0338 m です。広い円錐ほど同じ解像度で粗くなります。

解像度を 2048 に上げれば、テクセルの大きさは半分になります。ただし、メモリは 4 倍で 32 ビット深度なら 1024² が 4 MiB、2048² が 16 MiB です。16 ビット深度ならそれぞれ 2 MiB、8 MiB です（上の数字は Python で計算した値です）。

円錐の外に出さないというのがスポットライトの利点です。円錐の外側が無駄になる点光源のキューブ マップより同じ解像度で細かい影が作れます。

## 深度の精度とバイアス

透視投影の深度は非線形で近くで精度が高く、遠くで粗くなります。近クリップ面 0.1、遠クリップ面 50 の場合、深度の値（0〜1）は距離 0.2 で約 0.50、1 で約 0.90、5 で約 0.98、20 で約 0.997 です。値の範囲の 9 割が最初の 1 m に使われています。

24 ビット深度の場合、隣り合う値の間の距離は距離 1 m で約 0.0000006 m、10 m で約 0.00006 m、50 m で約 0.0015 m です。16 ビット深度の場合は 10 m で約 1.5 cm、50 m で約 38 cm にもなります。遠くの影が荒れるのはこのためです。

同じバイアスでも距離によって世界での大きさが違うので、調整が難しくなります。対策は 4 つあります。

1. `near_z` を大きくします。ニア面をできるだけ遠くに置くと精度の無駄が減ります。
2. 線形深度で比べます。シャドウ パスで距離（線形）を書き込んで比較します（[Point and Spot Light Shadows](index.md) の距離の保存）。
3. 法線オフセットを使います。深度をいじらず位置をずらします。距離に応じてずらす量をスケールします（[Normal Offset](../bias/normal-offset.md)）。
4. ハードウェアの傾き依存バイアス `SlopeScaledDepthBias` を使います（[Slope-Scale Bias](../bias/slope-scale-bias.md)）。

## スポットライトの影の判定

```hlsl
Texture2D<float> g_spot_shadow : register(t0);               // スポットライトのシャドウ マップ
SamplerComparisonState g_shadow_sampler : register(s0);      // 比較サンプラー(PCF の 2x2 を自動で行う)

cbuffer SpotCB : register(b0) {
  float4x4 g_spot_view_proj;        // 光の view * proj
  float3 g_spot_pos;                // 光の位置
  float g_spot_range;               // 到達距離
  float g_tan_half_fov;             // tan(fov / 2)
  float g_shadow_resolution;        // シャドウ マップの解像度(正方形の 1 辺)
  float2 pad;                       // 16 バイト境界にそろえる詰め物
};

float SpotShadow(float3 world_pos, float3 world_normal) {
  // 法線オフセット。テクセルの大きさに比例してずらす(足した: 係数 1.5 は一例)。
  float dist = length(world_pos - g_spot_pos);                                  // 光からの距離
  float texel_world = 2.0 * dist * g_tan_half_fov / g_shadow_resolution;        // 1 テクセルの世界での大きさ
  float3 p = world_pos + world_normal * (texel_world * 1.5);                    // 法線の向きに 1.5 テクセルずらす
  float4 clip = mul(float4(p, 1.0), g_spot_view_proj);                          // 光のクリップ空間へ

  // 光の後ろ側(w が 0 以下)は、円錐の外なので光が当たらない。割る前に弾く。
  if (clip.w <= 0.0) return 1.0;

  float3 ndc = clip.xyz / clip.w;                                               // 透視投影なので w で割る(正射影では w = 1)
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;                                 // NDC → UV(Y は反転)
  if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;                               // 円錐の外
  if (ndc.z > 1.0) return 1.0;                                                  // 遠クリップ面の外
  return g_spot_shadow.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z);         // 1 = 光が当たる、0 = 影
}
```

`fxc` で `ps_5_0` にコンパイルして、エラーが出ないことを確かめました。GPU では動かしていません。

`w` で割ることを忘れないでください。太陽の正射影では `w = 1` なので割り算が要りませんが、透視投影では割らないと影の位置が大きくずれます。割る前に `w <= 0` を弾くのは光の後ろ側の画素が、割り算で符号が反転して円錐の中の画素と同じ位置に写ってしまうからです。

`SampleCmpLevelZero` はシャドウ マップの値と `ndc.z` を比較して、1（光が当たる）か 0（影）を返します。比較サンプラーのフィルターを `COMPARISON_MIN_MAG_LINEAR_MIP_POINT` にしておくと近傍 4 テクセルの比較結果を線形補間した、なめらかな影の縁になります。

## 効率

- 円錐に収まる物だけを描きます。光の視錐台で物をカリングします。
- 解像度を光の画面上の大きさに合わせます。画面で小さい光はシャドウ マップも小さく（512×512 など）、大きな光は大きく（2048×2048）します。512² の 32 ビット深度は 1 MiB です。
- 更新を間引きます。静止した光と静止した物なら一度作って保存（キャッシュ）して、動く物だけを毎フレーム足します（[Shadows for Many Lights](many-lights.md)）。
- 光の範囲外では影を省きます。画面に映らない光の影は描きません。

## 複数のスポットライト

複数のスポットライトのシャドウ マップは、1 枚の大きなテクスチャ（アトラス）に並べるかテクスチャ配列にまとめます。

- アトラスは 1 枚の大きなテクスチャに各ライトのシャドウ マップをタイルとして配置します。1 つのテクスチャをシェーダーに渡せますが、ライトごとに UV の変換が要ります。たとえば 4096² の 1 枚に 1024² のタイルが 4×4 = 16 枚入ります。32 ビット深度で 64 MiB です。
- テクスチャ配列は `Texture2DArray` で、スライス番号でライトを選びます。全スライスが同じ解像度になります。

どちらも、ライトごとに解像度を変えたいときはアトラスが向いています。

## よくあるミス

??? failure "円錐の縁で、影が切れる"
    視野角が円錐ぴったりだと縁の画素の UV が範囲外になり `return 1.0` で影が消えます。外側の角度に少し余裕（数度）を足します。PCF のフィルターが縁をまたぐ分もこの余裕で受け止められます。

??? failure "真上を向くスポットライトで、影が出ない"
    光の向きと上方向が平行だとビュー行列が壊れます。向きの Y 成分の絶対値が 0.99 を超えたら、上方向を Z 軸にします。

??? failure "光の後ろにも影が出る"
    `w` が 0 以下の画素を弾いていません。割り算で符号が反転し円錐の中と同じ位置に写って、背後の物に影が付きます。

??? failure "遠くの影だけがガタガタになる"
    `near_z` が小さすぎて遠くの深度の精度が足りません。`near_z` を上げるか距離の線形深度で比べます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スポットの影は透視投影 1 枚です。
    - [x] 視野角・近い面・遠い面をライトの範囲に合わせます。視野角には少し余裕を持たせます。
    - [x] 透視投影では `w` で割ります。光の後ろ（`w ≤ 0`）は先に弾きます。
    - [x] 1 テクセルの大きさは、距離に比例して大きくなります。

## 参考

このページは次の資料を読まずに書きました。内容は一般に知られている説明と手元で計算した数字に基づいています。

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978。未読。
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"。未読。
- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012。未読。
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）。未読。

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Point Lights: Cube Maps](point-cubemap.md)
- [The Light Matrix](../shadow-map-basics/light-matrix.md)
