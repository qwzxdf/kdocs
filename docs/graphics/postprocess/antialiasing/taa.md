---
title: TAA
tags:
  - 描画
---

# TAA

<strong>TAA（Temporal Anti-Aliasing）</strong>は、**フレームごとにサンプル位置を画素内で少しずつずらし（ジッター）、過去のフレームの結果と混ぜて、時間方向にサンプルを蓄積する**方式です。<strong>事実上「複数フレームで SSAA をしている」</strong>ことになり、**ジオメトリの縁・シェーダー内のエイリアシング・時間的なちらつき**の**全部に効きます**。**現代のゲームの標準**で、**DLSS・FSR・TSR などのアップスケーラーの土台**でもあります。このページでは、**基本の仕組み・ジッター（Halton 列）・再投影・履歴のクランプ・合成の係数・実装の全体**を説明します。

!!! tip "ポイント"
    - TAA ＝ <strong>毎フレーム、サブピクセルだけずらして描き、前フレームの結果（履歴）と混ぜる</strong>。
    - <strong>ジッター</strong>：<strong>投影行列にサブピクセルの微小オフセット</strong>（<strong>Halton(2,3)・8〜16 フレーム周期</strong>）。
    - <strong>再投影</strong>：<strong>速度バッファで前フレームの画面位置を求め、履歴を読む</strong>。
    - <strong>履歴のクランプ</strong>：<strong>現在の画素の周囲 3×3 の色の範囲に、履歴を押し込む</strong>。<strong>ゴーストの主な対策</strong>。
    - <strong>合成</strong>：<strong>履歴 90 %・現在 10 %</strong> が<strong>目安</strong>。<strong>小さいほど滑らか・ゴースト増</strong>。
    - <strong>必要なもの</strong>：<strong>速度バッファ・前フレームの結果・ジッター</strong>。

## 基本の考え方

**1 フレームでは、1 画素につき 1 つのサンプル**しか取れません。**毎フレーム、サンプルの位置を画素内でずらし**、**過去のフレームの結果を、動きに合わせて持ってきて、平均**します。**静止した物なら、数フレームで複数のサンプルが蓄積**され、**SSAA のような画質**になります。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="TAA のジッター">
<text x="20" y="26" class="fig-title">サンプル位置を毎フレームずらして、結果を蓄積する</text>
<g transform="translate(40,56)">
<g stroke="#94a3b8" fill="#f8fafc"><rect x="0" y="0" width="100" height="100"/><rect x="130" y="0" width="100" height="100"/><rect x="260" y="0" width="100" height="100"/><rect x="390" y="0" width="100" height="100"/></g>
<polygon points="0,100 100,100 100,0" fill="#2563eb" fill-opacity="0.25"/><polygon points="130,100 230,100 230,0" fill="#2563eb" fill-opacity="0.25"/><polygon points="260,100 360,100 360,0" fill="#2563eb" fill-opacity="0.25"/><polygon points="390,100 490,100 490,0" fill="#2563eb" fill-opacity="0.25"/>
<circle cx="30" cy="35" r="5" fill="#e5484d"/><circle cx="170" cy="70" r="5" fill="#e5484d"/><circle cx="330" cy="30" r="5" fill="#e5484d"/><circle cx="420" cy="80" r="5" fill="#e5484d"/>
<text x="20" y="124" style="font-size:12px">フレーム 0</text><text x="150" y="124" style="font-size:12px">フレーム 1</text><text x="280" y="124" style="font-size:12px">フレーム 2</text><text x="410" y="124" style="font-size:12px">フレーム 3</text>
</g>
<g font-size="13"><text x="40" y="206">サンプル（赤）が、毎フレーム画素内の違う位置 → 縁をまたぐ画素では、内側・外側の結果が混ざる</text>
<text x="40" y="228">混ぜるたびに、縁の画素が「何割内側か」に収束 → 滑らかな縁（SSAA と同じ）</text></g>
</svg>

## ジッター

**投影行列にサブピクセルの微小なオフセット**を**加え**、**毎フレーム、画素内の違う位置**を**サンプル**します。**位置の列には低食い違い列の Halton(2, 3) が一般的**です。

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
| <strong>Halton(2, 3)</strong> | **2 次元に均一に近く分布する列** |
| **`2.0 / width`** | **NDC は幅が 2**。**1 画素 ＝ `2 / width`** |
| **`r[2]` に足す** | **行ベクトル規約**で、**x・y の同次座標が、z（w）に比例してずれる** |
| **8 フレームで一巡** | **周期が短すぎるとパターンが見える**。**8〜16** |

## 履歴の再投影と合成

**現フレームの画素について、速度バッファから、前フレームの画面位置を求め、履歴を読み、現在と混ぜます**。

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
      float3 neighbor = current_color.SampleLevel(point_sampler, uv + float2(x, y) * texel_size, 0).rgb;
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
| **`history_uv = uv − velocity`** | <strong>速度は「現在 − 前」</strong>なので**引いて前の位置** |
| **近傍クランプ** | **周囲 3×3 の最小・最大の色の範囲に履歴を押し込む**（**ゴースト対策**） |
| **`blend = 0.1`** | **現在の寄与は 10 %**。**小さいほど滑らか・ゴースト増** |
| **履歴はリニア サンプル** | **バイリニアで読む**（**ぼけの原因にもなる**） |

<!-- fig:taa-history-clamp:begin -->

<svg class="fig illust motion" data-fig="taa-history-clamp" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-taa-history-clamp" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">履歴のクランプ:近傍の範囲に収めて、ゴーストを消す</text>
<rect x="50" y="70" width="480" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="170.0" y1="70" x2="170.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="130.0" x2="530" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="290.0" y1="70" x2="290.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="530" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="410.0" y1="70" x2="410.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="250.0" x2="530" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="530" y="330" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">フレーム</text>
<text x="50" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">明るさ</text>
<path d="M50.0,242.8 L84.29,242.8 L118.57,242.8 L152.86,242.8 L187.14,74.8 L221.43,74.8 L255.71,74.8 L290.0,74.8 L324.29,74.8 L358.57,74.8 L392.86,74.8 L427.14,74.8 L461.43,74.8 L495.71,74.8 L530.0,74.8 L530.0,113.2 L495.71,113.2 L461.43,113.2 L427.14,113.2 L392.86,113.2 L358.57,113.2 L324.29,113.2 L290.0,113.2 L255.71,113.2 L221.43,113.2 L187.14,113.2 L152.86,281.2 L118.57,281.2 L84.29,281.2 L50.0,281.2 Z" fill="#e5aa28" fill-opacity="0.25" stroke="none"/>
<path d="M50.0,262.0 L84.29,262.0 L118.57,262.0 L152.86,262.0 L187.14,94.0 L221.43,94.0 L255.71,94.0 L290.0,94.0 L324.29,94.0 L358.57,94.0 L392.86,94.0 L427.14,94.0 L461.43,94.0 L495.71,94.0 L530.0,94.0" fill="none" stroke="#1f2937" stroke-width="3"/>
<text x="60.29" y="284.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">今のフレームの色（物体が明るくなる）</text>
<text x="310.57" y="90.8" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">近傍の範囲（橙の帯）</text>
<path d="M50.0,262.0 L84.29,262.0 L118.57,262.0 L152.86,262.0 L187.14,241.84 L221.43,224.1 L255.71,208.49 L290.0,194.75 L324.29,182.66 L358.57,172.02 L392.86,162.66 L427.14,154.42 L461.43,147.17 L495.71,140.79 L530.0,135.17" fill="none" stroke="#e5484d" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/></path>
<path d="M50.0,262.0 L84.29,262.0 L118.57,262.0 L152.86,262.0 L187.14,110.9 L221.43,108.87 L255.71,107.08 L290.0,105.51 L324.29,104.13 L358.57,102.92 L392.86,101.85 L427.14,100.9 L461.43,100.08 L495.71,99.35 L530.0,98.71" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;1.0000" values="0;0;1;1"/></path>
<circle cx="50.0" cy="262.0" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1104;0.1408;0.1712;0.2016;0.2320;0.2624;0.2928;0.3232;0.3536;0.3840;0.4144;0.4448;0.4752;0.5056;1.0000" values="50;50;84.29;118.57;152.86;187.14;221.43;255.71;290;324.29;358.57;392.86;427.14;461.43;495.71;530;530"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1104;0.1408;0.1712;0.2016;0.2320;0.2624;0.2928;0.3232;0.3536;0.3840;0.4144;0.4448;0.4752;0.5056;1.0000" values="262;262;262;262;262;241.84;224.1;208.49;194.75;182.66;172.02;162.66;154.42;147.17;140.79;135.17;135.17"/></circle>
<circle cx="50.0" cy="262.0" r="7" fill="#2ea043" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.5264;0.5568;0.5872;0.6176;0.6480;0.6784;0.7088;0.7392;0.7696;0.8000;0.8304;0.8608;0.8912;0.9216;1.0000" values="50;50;84.29;118.57;152.86;187.14;221.43;255.71;290;324.29;358.57;392.86;427.14;461.43;495.71;530;530"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.5264;0.5568;0.5872;0.6176;0.6480;0.6784;0.7088;0.7392;0.7696;0.8000;0.8304;0.8608;0.8912;0.9216;1.0000" values="262;262;262;262;262;110.9;108.87;107.08;105.51;104.13;102.92;101.85;100.9;100.08;99.35;98.71;98.71"/></circle>
<text x="560" y="120" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">クランプなし<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.4957;0.4960;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="120" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">クランプあり<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="560" y="150" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">履歴（赤）が古い明るさに残り、<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.4957;0.4960;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="150" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">履歴（緑）は範囲の端へ寄せられ、<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="560" y="172" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ゆっくり追いつく ＝ ゴースト<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.4957;0.4960;1.0000" values="0;0;1;1;0;0"/></text>
<text x="560" y="172" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">すぐ新しい色に追いつく<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="50" y="350" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">物体が明るくなった時、履歴が古い色のままだと、尾を引く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;1.0000" values="1;1;0;0"/></text>
<text x="50" y="350" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">履歴を「近傍の最小〜最大」にクランプすると、尾を引かない<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4957;0.4960;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:taa-history-clamp:end -->

## なぜクランプするのか

**履歴は前のフレームの結果**です。<strong>物が動いて、別の物が現れた画素の履歴は、「前に別の物が見えていた色」</strong>で**間違っています**。<strong>そのまま混ぜるとゴースト（残像）</strong>になります。**現在の周囲の色の範囲（最小〜最大）に、履歴を押し込む**と**周囲の色と大きく違う履歴は、範囲内に引き戻され**、**ゴーストが抑えられます**。

| 状況 | クランプの効果 |
| --- | --- |
| **静止した物** | **履歴は範囲内にあるので、そのまま蓄積** |
| **新しく現れた物** | **履歴（前の物）は範囲外 → 範囲に引き戻される** |
| **急に暗くなった所** | **履歴の明るい色が範囲に押し込まれる** |

## 流れのまとめ

| 手順 | 内容 |
| --- | --- |
| **① ジッター** | **投影行列に毎フレーム違うオフセット** |
| **② 描画** | <strong>ジッターした行列でシーンを描く（速度バッファも）</strong> |
| **③ TAA パス** | **速度で履歴を再投影、クランプして、現在と合成** |
| **④ 履歴の更新** | **合成結果を次フレームの履歴として保存**（**2 枚をスワップ**） |
| **⑤ 後処理** | **ブルーム・トーンマップなどは、TAA の後** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **バイキュービック（Catmull-Rom）で履歴を読む** | **ぼけを減らす**（[TAA の課題](taa-challenges.md)） |
| **YCoCg 色空間でクランプ** | **色の範囲がより自然**になり、**ゴーストが減る** |
| <strong>分散クリップ（variance clipping）</strong> | **最小・最大の代わりに平均と分散から範囲を決める** |
| **速度の大きさでブレンド率を変える** | **動く所は現在を多めに** |
| **シャープ化を併用** | **TAA のぼけを戻す** |
| <strong>履歴の拒否（リセット）</strong> | **カット・テレポート・露出の急変で履歴を捨てる** |
| **ジッターを速度から除く** | **静止した物がぶれない**（[速度バッファ](../motion-blur/velocity-buffer.md)） |

## よくあるミス

??? failure "静止した物が、ぼやける・ちらつく"
    **ジッターが速度に混ざっている**。**速度から、ジッターを除く**。

??? failure "動く物体の後ろに、ゴースト（残像）が出る"
    **近傍クランプ**を入れる。**速度の精度**を上げる。

??? failure "画面全体が、少しぼやけて見える"
    **バイリニアの履歴読み出しが原因**。**バイキュービック**・**シャープ化**。

??? failure "カット・瞬間移動の後、前の絵が残る"
    **履歴をリセット**（**ブレンド率を 1 に**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] TAA ＝ <strong>毎フレーム サブピクセルずらして描き、履歴と混ぜて、時間方向に蓄積</strong>
    - [x] <strong>ジッター（Halton）</strong>＋<strong>再投影（速度バッファ）</strong>＋<strong>履歴クランプ</strong>＋<strong>合成</strong>
    - [x] <strong>縁・シェーダー内・時間のちらつき</strong>の<strong>すべてに効く</strong>
    - [x] <strong>ゴースト対策がクランプ</strong>。<strong>履歴 90 %・現在 10 %</strong>
    - [x] <strong>ジッターを速度から除く</strong>。<strong>カットで履歴をリセット</strong>

## 参考

- Karis, "High Quality Temporal Supersampling"（SIGGRAPH 2014）
- Salvi, "An Excursion in Temporal Supersampling"（GDC 2016）
- Yang et al., "A Survey of Temporal Antialiasing Techniques"（Eurographics 2020）

## 関連ページ

- [アンチエイリアシング](index.md)
- [TAA の課題](taa-challenges.md)
- [速度バッファ](../motion-blur/velocity-buffer.md)
- [TAA とアップスケール（最適化）](../../../rendering/taa-upscaling.md)
