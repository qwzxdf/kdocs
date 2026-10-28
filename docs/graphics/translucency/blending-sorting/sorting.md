---
title: Sorting
tags:
  - 描画
---

# Sorting

<strong>半透明は奥から手前の順に描かないと、結果が崩れます</strong>。物体単位のソート・パーティクル単位のソート・面ごとのソートなど、粒度があります。このページではソートの方法と、順序の決め方を説明します。

!!! tip "ポイント"
    - 物体の中心のカメラからの距離でソートするのが基本。
    - 物体同士が入り組むと、ソートでは直らない（OIT が必要）。
    - パーティクルは系統ごと・距離でソート。
    - 描画順は不透明 → 半透明（奥から手前）。

!!! info "このページを読む前に"
    - [Alpha Blending and Sorting](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ソート
<strong>奥から手前</strong>の順に描くため、半透明のオブジェクトをカメラからの距離で並べ替えます。

```cpp
struct TransparentDraw {
  float distance_squared;
  uint32_t draw_index;
};

std::vector<TransparentDraw> sorted;
for (uint32_t i = 0; i < transparent_draws.size(); ++i) {
  Vector3 to_object = transparent_draws[i].center - camera_position;
  sorted.push_back({to_object.LengthSquared(), i});
}
std::sort(sorted.begin(), sorted.end(),
          [](const TransparentDraw& a, const TransparentDraw& b) {
            return a.distance_squared > b.distance_squared;
          });
```

| 点 | 説明 |
| --- | --- |
| `LengthSquared` | 距離の比較だけなので、平方根は不要 |
| 降順（遠い順） | 一番遠い物から描く |
| 距離の基準 | オブジェクトの中心（または、カメラの前方ベクトルへの射影（深度））。射影のほうが横に並んだ物の順序が安定 |
| ソートのキー | 透明度の種類（加算など順序不要のもの）を分けて、通常のものだけソート |

カメラの前方ベクトルへの射影（ビュー空間の z）で並べると、カメラが回転しても順序が安定します。

```cpp
float view_depth = Vector3::Dot(center - camera_position, camera_forward);
```

### ソートの限界

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| オブジェクトが交差 | 1 つの順序では、表せない（互いに食い込む） | 分割する・OIT |
| 自己重なり | 1 つのメッシュの手前の面と奥の面（ガラス瓶） | 背面を先、前面を後に描く（2 パス） |
| 大きな物体 | 中心では、順序を決められない | 分割する・OIT |
| パーティクル | 数が多いので、ソートが重い | GPU ソート・加算ブレンドで回避 |
| ポップ | カメラが動くと、順序が突然入れ替わり見た目が変わる | 中心の取り方・OIT |

### 自己重なり（2 パス）

ガラスの瓶のように 閉じたメッシュは、背面（奥の面）を先に描き前面（手前の面）を後に描くと、正しい順序に近づきます。

```cpp
context->RSSetState(cull_front_state);
DrawMesh();
context->RSSetState(cull_back_state);
DrawMesh();
```

2 パス描画の内容です。1 回目は前面カリングで奥の面（背面）を描きます。2 回目は背面カリングで手前の面（前面）を描きます。

<!-- fig:alpha-sort-order:begin -->

<svg class="fig illust motion" data-fig="alpha-sort-order" viewBox="0 0 780 390" role="img"><rect x="0" y="0" width="780" height="390" rx="14" fill="#ffffff"/>
<defs><marker id="arr-alpha-sort-order" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<mask id="as-mask-1-1" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
</mask>
<mask id="as-mask-1-2" maskUnits="userSpaceOnUse" x="420" y="84" width="300" height="220"><rect x="420" y="84" width="300" height="220" fill="#ffffff"/>
<rect x="532" y="168" width="130" height="130" fill="#000000"/>
<rect x="486" y="134" width="130" height="130" fill="#000000"/>
</mask>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">半透明は奥から手前の順に描く。順番を間違えると、透けなくなる</text>
<text x="40" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">正しい順:奥 → 中 → 手前</text>
<rect x="40" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="290" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="60" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><rect x="106" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><rect x="152" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="66" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">間違った順:手前 → 中 → 奥（深度を書く）</text>
<rect x="420" y="84" width="300" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="670" cy="116" r="20" fill="none" stroke="#cbd5e1" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><rect x="532" y="168" width="130" height="130" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-1)"><rect x="486" y="134" width="130" height="130" fill="#2ea043" fill-opacity="0.55" stroke="#2ea043" stroke-width="1.5"/>
</g>
</g>
<g opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000" values="0;0;1;1"/><g mask="url(#as-mask-1-2)"><rect x="440" y="100" width="130" height="130" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
</g>
</g>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 番目:手前（青） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2779;0.2783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 番目:中（緑） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;0.4692;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 番目:奥（赤） を描く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4692;0.4696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="40" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">左:重なりに赤・緑・青が全部透けて見える。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000" values="1;1;0;0"/></text>
<text x="420" y="356" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">右:手前が先に深度を書くので、奥の物が消えて透けない。<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6696;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:alpha-sort-order:end -->

## ブレンド順序の決め方（まとめ）
| 物 | ブレンド | ソート |
| --- | --- | --- |
| ガラス・水面 | 通常 | 必要 |
| 炎・爆発・魔法 | 加算 | 不要 |
| 煙 | 通常（または乗算済み） | 必要 |
| <strong>影の板（ブロブ）</strong> | 乗算 | 不要 |
| UI | 通常 | 描画順をレイヤーで決める |

## なぜソートが必要か

通常の、アルファ ブレンドは <strong>順序に依存</strong>します。奥の物を先に手前の物を後に描かないと正しい色になりません。

```text
赤いガラス（手前）と、青いガラス（奥）を、通して、背景を見るとき:
  正しい順序:  背景 → 青（奥）→ 赤（手前）   → 赤が、手前に、見える
  逆の順序:    背景 → 赤（手前）→ 青（奥）   → 青が、手前に見える（間違い）
```

順序を間違えると 手前と奥が入れ替わったような見た目になります。深度の書き込みをしないので、後から描いた物が常に手前に重なるためです。

## ソートの基本

<strong>カメラからの距離の遠い順</strong>に並べて、描きます（画家のアルゴリズム）。

```cpp
struct TransparentObject {
  float3 position;       // 代表点（中心）
  float sort_key;        // カメラからの距離（の 2 乗）
  // ...
};

// 毎フレーム、カメラからの距離を計算して、遠い順に並べる。
for (auto& o : transparent_objects) {
  const float3 d = o.position - camera_position;
  o.sort_key = Dot(d, d);                              // 距離の 2 乗（sqrt は、順序に影響しないので、省く）
}
std::sort(transparent_objects.begin(), transparent_objects.end(),
          [](const auto& a, const auto& b) { return a.sort_key > b.sort_key; });   // 遠い順

for (const auto& o : transparent_objects) Draw(o);       // 遠い物から、描く
```

### 距離かビュー空間の深度か

| キー | 内容 | 向く場面 |
| --- | --- | --- |
| カメラからの距離 | 位置と、カメラの直線距離 | 球状の、広がり（爆発、パーティクルの群れ） |
| ビュー空間の z 深度 | カメラの前方向に沿った距離 | 平面的な板（ビルボード、ガラス板） |

板のパーティクルは 画面に平行な面を持つので、ビュー空間の z 深度で、ソートするほうが見た目の前後に一致します。

## ソートが破綻する場面

### ① 物体の内部でソートできない

<strong>1 つのメッシュ</strong>（ガラスの瓶、水槽）は 三角形がばらばらの距離にあります。物体の中心の距離だけでソートすると、1 つのメッシュの中の三角形の順序が描画の順（インデックスの順）で決まり、手前と奥が逆に重なることがあります。

| 対策 | 内容 |
| --- | --- |
| 2 パスで描く | 裏面（奥側）を先に描き、表面（手前側）をあとに描く。凸な物（瓶、球）で正しくなる |
| 深度の事前描画 | 手前の面だけを深度に書いて最前面の 1 層だけを描く |
| メッシュを分割 | 三角形をソートする。重い |

```cpp
// 凸な半透明の物: 裏面 → 表面の、順で、2 回描く。
context->RSSetState(rs_cull_front.Get());     // 表面をカリング（裏面だけ）
Draw(mesh);
context->RSSetState(rs_cull_back.Get());      // 裏面をカリング（表面だけ）
Draw(mesh);
```

### ② 物体同士が交差している

2 つの大きな物体が互いに、貫通していると どちらが手前か、場所によって違うので物体単位の、ソートが成立しません。

### ③ 大きな物体と小さな物体

大きな板（地面に広がる水面）と、小さなパーティクルでは中心の距離で、並べると小さな物が大きな物の、手前にあるのに先に描かれることがあります。大きな物は別のパスで先に描きます（水は、不透明の後、半透明の前、など）。

### ④ 同じ距離

距離がほぼ同じの物が フレームごとに順序が入れ替わるとちらつきます。安定したタイブレーク（物の ID など）を加えます。

```cpp
// 距離が同じなら、ID で順序を決める（フレームごとに、順序が揺れない）。
std::sort(objects.begin(), objects.end(), [](const auto& a, const auto& b) {
  if (a.sort_key != b.sort_key) return a.sort_key > b.sort_key;
  return a.id < b.id;
});
```

## パーティクルのソート

パーティクルは <strong>数千〜数万個</strong>あり、毎フレーム、CPU でソートすると重いです。

| 方法 | 内容 |
| --- | --- |
| システム単位でソート | パーティクル システム（炎、煙）を 1 つの物体としてソートする。システムの中は描画の順序のまま（生成順） |
| システムの中もソート | 煙のように、重なりが多い見た目が重要なものだけ、パーティクルごとにソートする |
| GPU でソート | 計算シェーダーで、ビトニック ソートなどを使う。数万個でもミリ秒以下 |
| ソートしない | 加算ブレンド（火花、光）は順序に依存しない。ソート不要 |

### GPU でのソート

```text
① 計算シェーダーで、各パーティクルの、カメラからの距離を、計算する
② ビトニック ソート（または、基数ソート）で、距離の順に、並べ替える
③ 並べ替えた順序で、描く（インデックス バッファを、並べ替える）
```

ビトニック ソートは データ数が 2 の累乗で 並列に実行しやすいソートです。GPU でのソートの定番です（実装は短いが、本書では省略。ライブラリの `FidelityFX Parallel Sort` などを使う方法もある）。

## ソートに頼らない方法

| 方法 | 内容 |
| --- | --- |
| 加算・乗算ブレンド | 順序に依存しない |
| OIT（順序に依存しない、透明） | ソートなしで近似または正確な、結果を得る（[OIT](../oit/index.md)） |
| アルファ テスト系 | 深度に書き込み、ソートが不要（[Alpha Testing](../alpha-test/index.md)） |

## よくあるミス

??? failure "入り組んだ半透明が前後逆に見える"
    <strong>ソートの粒度を細かく</strong>する、または OITを使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 不透明の後に半透明を奥から手前へ
    - [x] 入り組むなら OIT

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）
- Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Carpenter, "The A-buffer, an Antialiased Hidden Surface Method", SIGGRAPH 1984
- Batcher, "Sorting Networks and their Applications", AFIPS Spring Joint Computer Conference, 1968（ビトニック ソートの原典）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [OIT](../oit/index.md)
- [Blend State](blend-state.md)
