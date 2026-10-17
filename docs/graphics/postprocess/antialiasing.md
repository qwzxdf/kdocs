---
title: アンチエイリアシング
tags:
  - 描画
---

# アンチエイリアシング

**画面は画素（ピクセル）の格子**なので**斜めの線や物体の縁**は、<strong>階段状（ジャギー）</strong>に見えます。これが**エイリアシング**です。**アンチエイリアシング**（AA）は、**これを滑らかにする**技術の総称で、**原理の違う複数の方式**があります。<strong>サンプル数を増やす（MSAA・SSAA）</strong>、<strong>画像を後から滑らかにする（FXAA・SMAA）</strong>、<strong>フレームをまたいでサンプルを集める（TAA）</strong>。このページでは、**エイリアシングの原因・各方式の原理・長所短所・選び方**を説明します。

!!! tip "ポイント"
    - エイリアシング ＝ <strong>連続した絵を、離散的なサンプル（画素）で切り取る</strong>ときの<strong>標本化の誤差</strong>。
    - <strong>SSAA</strong>：<strong>高解像度で描いて縮小</strong>。<strong>最も綺麗・最も重い</strong>。
    - <strong>MSAA</strong>：<strong>縁（ジオメトリの境界）だけ、サンプルを増やす</strong>。<strong>シェーディングは 1 回</strong>。<strong>ディファード・シェーダー内のエイリアシングに弱い</strong>。
    - <strong>FXAA・SMAA</strong>：<strong>完成した画像から、縁を検出してぼかす</strong>（<strong>ポスト AA</strong>）。<strong>安い</strong>が<strong>ぼける・細部が取れない</strong>。
    - <strong>TAA</strong>：<strong>フレームごとにサンプル位置をずらし（ジッター）、過去のフレームと混ぜる</strong>。<strong>シェーダー内のエイリアシングも消える</strong>。<strong>現代の標準</strong>。
    - <strong>TAA の課題</strong>：<strong>ゴースト・ぼけ・細い物のちらつき</strong>。<strong>履歴の検証（クランプ）</strong>が重要。

## エイリアシングの原因

**画素の中心の 1 点だけ**で、<strong>「そこに物体があるか」</strong>を**判定**すると**物体の縁が画素ごとに「ある・ない」の 2 択**になります（**階段状**）。

| 種類 | 内容 |
| --- | --- |
| **ジオメトリのエイリアシング** | **ポリゴンの縁**の**ジャギー** |
| **シェーダーのエイリアシング** | **スペキュラの細かいハイライト・法線マップ・細かい模様**の**ちらつき**（**縁でなくても起こる**） |
| **時間的エイリアシング** | **動いたとき**に**細い線がちらつく・途切れる** |
| **テクスチャのエイリアシング** | **ミップ・異方性フィルタ**で**対処**（AA とは別） |

**理想的な解決**は、**画素あたりのサンプルを増やして、平均する**ことです。**どこにどれだけサンプルを増やすか**で**方式が分かれます**。

## SSAA（スーパー サンプリング）

**画面を縦横 2 倍（または 4 倍）の解像度で描き、縮小**します。**全ての画素・全ての種類のエイリアシングが減る**、**最も確実な方式**です。

| 項目 | 内容 |
| --- | --- |
| **コスト** | **2×2 SSAA で描画コストが 4 倍**。**非常に重い** |
| **品質** | **最高**（ジオメトリ・シェーダー・テクスチャ全て） |
| **用途** | **オフライン・スクリーンショット・古いゲームの高品質モード** |

## MSAA（マルチ サンプル）

**MSAA**は**ジオメトリの縁**だけ、**サンプルを増やします**。<strong>1 画素に複数のサンプル点（4x なら 4 点）</strong>を持ち、**深度・カバレッジ（どのサンプルが三角形に覆われるか）は、サンプルごと**に**判定**しますが、**ピクセル シェーダーは、画素ごとに 1 回**しか**実行しません**。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="MSAA">
<text x="20" y="24" class="fig-title">サンプル点は複数、シェーディングは 1 回（画素の中心）</text>
<rect x="40" y="60" width="140" height="140" fill="none" stroke="currentColor" stroke-width="2"/>
<polygon points="40,200 180,60 180,200" fill="rgba(76,139,245,0.35)" stroke="currentColor" stroke-width="2"/>
<g fill="currentColor"><circle cx="75" cy="95" r="5"/><circle cx="145" cy="95" r="5"/><circle cx="75" cy="165" r="5"/><circle cx="145" cy="165" r="5"/></g>
<text x="200" y="100" style="font-size:12px">4x MSAA：4 つのサンプル点</text><text x="200" y="124" style="font-size:12px">三角形に覆われたサンプル → 3 つ</text><text x="200" y="148" style="font-size:12px">画素の色 ＝ 三角形の色 × 3/4 ＋ 背景 × 1/4</text>
<text x="200" y="180" style="font-size:12px">シェーディングは 1 回だけ → 安い（縁だけ AA）</text>
<text x="480" y="100" style="font-size:12px">縁のジャギーは消える</text><text x="480" y="124" style="font-size:12px">ただし、面の内側のシェーダーの</text><text x="480" y="148" style="font-size:12px">ちらつきは、消えない</text>
</svg>

| 項目 | 内容 |
| --- | --- |
| **コスト** | **サンプル数に比例して、深度・カラー バッファのメモリと帯域が増える**（4x で約 4 倍）。**ピクセル シェーダーは、増えない** |
| **品質** | **ジオメトリの縁**は**綺麗** |
| **弱点** | **シェーダー内のエイリアシング**（スペキュラ・法線マップ）は**消えない**。**ディファード レンダリングと相性が悪い**（**G バッファがサンプルごとに必要**になる）。**ポストプロセスの後の画像は、通常の画像** |
| <strong>解決（リゾルブ）</strong> | **描画後にサンプルを平均して 1 画素にまとめる**（`ResolveSubresource`）。**HDR のリゾルブは、トーンマップ後に行うのが望ましい**（**明るい点が平均で薄まる**ため） |

**フォワード レンダリング**では、**MSAA が有効**ですが、**ディファード**・**ポストプロセス多用**・**高い画質のシェーダー**では、**TAA が主流**になりました。

## FXAA

**FXAA**（Fast Approximate AA）は、**完成した LDR 画像**から、**輝度の変化が大きい縁を検出し、その方向に沿って、ぼかします**。

| 項目 | 内容 |
| --- | --- |
| **入力** | **LDR の最終画像のみ**（深度・速度などが不要） |
| **手順** | **① 輝度から、縁を検出** → **② 縁の向き（水平・垂直）と長さを推定** → **③ 縁に沿って、サンプルを混ぜる** |
| **コスト** | **非常に安い**（1 パス・十数タップ） |
| **品質** | **ジャギーは減るが画像全体が少しぼける**。**細い線・テクスチャの細部もぼける** |
| **用途** | **低スペック・モバイル・簡易** |

## SMAA

**SMAA**（Subpixel Morphological AA）は、<strong>縁の形状（L 字・Z 字・U 字などのパターン）</strong>を**認識**し、**パターンに応じて、適切な重みでブレンド**します。**FXAA より、細部を保つ**、**より精度の高いポスト AA** です。

| 段階 | 内容 |
| --- | --- |
| **① 縁の検出** | <strong>輝度（または色・深度）</strong>の**差**から、**縁**を**検出** |
| **② ブレンドの重みの計算** | **縁のパターン**（**事前計算された、面積テクスチャ**を引く）から、**ブレンド量**を**求める** |
| **③ 近傍のブレンド** | **重みに従って、隣の画素と混ぜる** |

| 項目 | 内容 |
| --- | --- |
| **品質** | **FXAA より、細部を保ちつつ、ジャギーを除く** |
| **コスト** | **3 パス**。**FXAA より重い**が、**MSAA・TAA より安い** |
| **T2x / S2x / 4x** | **時間的な再投影（T2x）や、MSAA との併用**の**バリエーション** |

**ポスト AA の限界**：**画像に既にある情報**だけで**処理**するので、**サンプルが欠落した細い線**（1 画素以下の線）は、**復元できません**。**時間的なちらつき**にも**対処できません**。

## TAA

**TAA**（Temporal Anti-Aliasing）は、<strong>フレームごとにサンプル位置を微小にずらし（ジッター）</strong>、**過去のフレームの結果を、現在のフレームと混ぜる**ことで、**時間をかけて、画素あたりの多数のサンプル**を**集めます**。**ジオメトリ・シェーダー・細い線・時間的なちらつき**の**全てに効果がある**ため、**現代のゲームの標準**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="TAA">
<text x="20" y="24" class="fig-title">フレームごとにサンプル位置をずらし（ジッター）、履歴と混ぜて、サンプルを蓄積する</text>
<g stroke="currentColor" stroke-width="2" fill="none"><rect x="40" y="60" width="100" height="100"/><rect x="170" y="60" width="100" height="100"/><rect x="300" y="60" width="100" height="100"/></g>
<g fill="currentColor"><circle cx="70" cy="90" r="5"/><circle cx="235" cy="125" r="5"/><circle cx="330" cy="130" r="5"/></g>
<text x="52" y="180" style="font-size:12px">フレーム 0</text><text x="182" y="180" style="font-size:12px">フレーム 1</text><text x="312" y="180" style="font-size:12px">フレーム 2</text>
<text x="430" y="90" style="font-size:12px">サンプル位置が、毎フレーム、画素内でずれる</text><text x="430" y="114" style="font-size:12px">↓</text>
<text x="430" y="138" style="font-size:12px">履歴（再投影）と、現在のフレームを混ぜる</text><text x="430" y="162" style="font-size:12px">↓</text><text x="430" y="186" style="font-size:12px">蓄積された結果 ≒ 多数サンプルの平均</text>
<text x="40" y="224" style="font-size:12px">静止した物は、数フレームで高品質に収束。動く物は、動きのベクトルで履歴を追従させる</text>
</svg>

### ジッター

**投影行列にサブピクセルの微小なオフセット**を**加え**、**毎フレーム、画素内の違う位置**をサンプルします。**Halton 数列**などの**低食い違い列**が**標準的**（**8〜16 フレームで一巡**）。

```cpp
float Halton(uint32_t index, uint32_t base) {
  float result = 0.0f;
  float f = 1.0f / base;
  uint32_t i = index;
  while (i > 0) {
    result += f * (i % base);
    i /= base;
    f /= base;
  }
  return result;
}

DirectX::XMFLOAT2 JitterOffset(uint32_t frame_index, uint32_t width, uint32_t height) {
  uint32_t index = (frame_index % 8) + 1;
  float jitter_x = (Halton(index, 2) - 0.5f) * 2.0f / width;
  float jitter_y = (Halton(index, 3) - 0.5f) * 2.0f / height;
  return {jitter_x, jitter_y};
}
```

```cpp
DirectX::XMMATRIX jittered_projection = projection;
jittered_projection.r[2] = DirectX::XMVectorAdd(
    jittered_projection.r[2], DirectX::XMVectorSet(jitter.x, jitter.y, 0.0f, 0.0f));
```

| 点 | 説明 |
| --- | --- |
| <strong>Halton(2, 3)</strong> | **2 次元に均一に分布**する、**低食い違い列** |
| **`2.0 / width`** | **NDC は幅が 2**なので、**1 画素 ＝ `2/width`** |
| **`r[2]` に足す** | **行ベクトル規約の射影行列**で、**x・y の同次座標が、z（w）に比例してずれる**ように**加える**（**透視でもサブピクセルのずれが一定**になる）。**符号は座標系・行列の規約に合わせて確認** |
| **8 フレームで一巡** | **周期が短すぎるとパターンが見える**。**8〜16** |

### 履歴の再投影と合成

**現フレームの画素**に対し、**速度バッファ**から、**前フレームでの位置**を**求め**、**履歴をサンプル**して、**現在の色と混ぜます**。

```hlsl
float3 TAA(float2 uv) {
  float3 current = current_color.SampleLevel(point_sampler, uv, 0).rgb;
  float2 velocity = velocity_texture.SampleLevel(point_sampler, uv, 0).rg;
  float2 history_uv = uv - velocity;
  float3 history = history_color.SampleLevel(linear_sampler, history_uv, 0).rgb;

  float3 neighbor_min = current;
  float3 neighbor_max = current;
  [unroll] for (int y = -1; y <= 1; ++y) {
    [unroll] for (int x = -1; x <= 1; ++x) {
      float3 neighbor =
          current_color.SampleLevel(point_sampler, uv + float2(x, y) * texel_size, 0).rgb;
      neighbor_min = min(neighbor_min, neighbor);
      neighbor_max = max(neighbor_max, neighbor);
    }
  }

  float3 clamped_history = clamp(history, neighbor_min, neighbor_max);
  float blend = 0.1;
  return lerp(clamped_history, current, blend);
}
```

| 点 | 説明 |
| --- | --- |
| **`history_uv = uv - velocity`** | <strong>速度は「現在 − 前」</strong>なので**引いて、前フレームの位置**を得る |
| **近傍クランプ** | **現在の画素の周囲 3×3 の、色の最小・最大**の**範囲**に**履歴の色をクランプ**。**範囲外の履歴（ゴースト）を、現在の近傍に引き戻す** |
| **`blend = 0.1`** | **現在のフレームの寄与は 10%**。<strong>小さいほど滑らか（蓄積が長い）</strong> |

### TAA の課題

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| <strong>ゴースト（残像）</strong> | **履歴が現在の内容と合わない**（**物の後ろから出てきた背景・動く物の跡**） | **近傍クランプ**・**速度の大きさで履歴の重みを下げる**・<strong>分散クリッピング（AABB を分散から決める）</strong> |
| **ぼけ** | **履歴のバイリニア サンプルの繰り返しで、ぼける** | **バイキュービック（Catmull-Rom）で履歴をサンプル**・**シャープ フィルタ** |
| **細い物のちらつき** | **1 画素以下の線**が**サンプルのずれで出たり消えたり** | **ジッターの範囲**・**クランプの調整** |
| **半透明・パーティクル** | **速度・深度がない** | **別途、AA を調整**・**TAA の後に描く** |
| **動きの速い物** | **速度バッファの精度** | **速度の高精度化**・**深度が近い画素の速度**（**最も手前の画素の速度を使う**） |
| **カメラのカット** | **履歴が無効** | **履歴をリセット** |

**TAA の品質**は、**履歴のクランプ・速度・シャープネス**の**調整**で**決まります**。**調整の積み重ね**が**必要**で、**ゲームごとに独自のチューニング**が**施されています**。

### アップスケールとの統合

**TAA の発展**として、**低解像度でレンダリングして、時間的に蓄積しながら高解像度に拡大する**手法（**TAAU・FSR2・DLSS・XeSS**）があります（[TAA・アップスケール](../../rendering/taa-upscaling.md)）。**ジッターと速度バッファを使う**点は**TAA と同じ**です。

## 方式の比較

| 方式 | ジオメトリの縁 | シェーダーのエイリアシング | 時間的ちらつき | コスト | 備考 |
| --- | --- | --- | --- | --- | --- |
| **なし** | ✕ | ✕ | ✕ | 0 | — |
| **SSAA** | ◎ | ◎ | ○ | **極大** | オフライン |
| **MSAA** | ◎ | ✕ | ✕ | 中〜大（帯域） | フォワード向け |
| **FXAA** | ○（ぼける） | △ | ✕ | 極小 | 簡易 |
| **SMAA** | ◎ | △ | ✕ | 小 | 画質重視のポスト AA |
| **TAA** | ◎ | ◎ | ◎ | 小〜中 | **標準**。ゴースト・ぼけに注意 |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| **ディファード・多数のポストプロセス・現代的な 3D** | **TAA**（＋シャープ） |
| **フォワード・VR・低遅延** | **MSAA**（VR は時間的な手法が酔いやすい） |
| **低スペック・モバイル** | **FXAA・SMAA・MSAA 2x/4x**（**タイルベースで MSAA が安い**） |
| **2D・ピクセル アート** | **AA 不要**・**ニアレスト** |
| **高画質・アップスケールしたい** | **DLSS・FSR・XeSS**（TAA 系） |

## よくあるミス

??? failure "TAA のジッターを、速度バッファに混ぜて、静止した物がゆらぐ"
    **ジッターを除いた位置**で**速度を計算**する。

??? failure "近傍クランプをせず、ゴーストが尾を引く"
    **履歴を近傍の色の範囲にクランプ**する。

??? failure "MSAA のリゾルブを、トーンマップ前の HDR で線形に平均して、明るい縁がジャギーに見える"
    **トーンマップ後にリゾルブ**、または**トーンマップしてから平均**する（**カスタム リゾルブ**）。

??? failure "カメラ カットで、履歴をリセットせず、前のシーンが残る"
    **カット時は履歴を破棄**する。

??? failure "FXAA を、ブルーム・グレイン・UI の後にかけて、グレインや文字がぼける"
    **FXAA は、UI・グレインの前**に**かける**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エイリアシング ＝ <strong>連続した絵を、画素で標本化する誤差</strong>。<strong>対策はサンプルを増やす／集める</strong>
    - [x] <strong>MSAA</strong>：<strong>縁だけサンプル増</strong>、<strong>シェーダーは 1 回</strong>。<strong>ディファード・シェーダー内のエイリアシングに弱い</strong>
    - [x] <strong>FXAA・SMAA</strong>：<strong>完成画像から縁を検出してぼかす</strong>。<strong>安い</strong>が<strong>細部・ちらつきに弱い</strong>
    - [x] <strong>TAA</strong>：<strong>ジッター ＋ 履歴の再投影 ＋ 近傍クランプ</strong>。<strong>現代の標準</strong>。<strong>ゴースト・ぼけに注意</strong>
    - [x] <strong>状況（レンダリング方式・VR・モバイル）で選ぶ</strong>。<strong>TAA はアップスケールの土台</strong>にもなる

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Lottes, "FXAA"（NVIDIA、2009）
- Jimenez et al., "SMAA: Enhanced Subpixel Morphological Antialiasing"（Eurographics 2012）
- Salvi, "An Excursion in Temporal Supersampling"（GDC 2016）
- Pedersen, "Temporal Reprojection Anti-Aliasing in INSIDE"（GDC 2016）

## 関連ページ

- [ポストプロセス](index.md)
- [モーション ブラー（速度バッファ）](motion-blur.md)
- [TAA・アップスケール](../../rendering/taa-upscaling.md)
- [AO のフィルタ（時間蓄積）](../ao/filtering.md)
