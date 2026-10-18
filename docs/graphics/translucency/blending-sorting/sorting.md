---
title: Sorting
tags:
  - 描画
---

# Sorting

<strong>半透明は、奥から手前の順に描かないと、結果が崩れます</strong>。<strong>物体単位のソート・パーティクル単位のソート・面ごとのソート</strong>など、粒度があります。このページでは、ソートの方法と、順序の決め方を説明します。

!!! tip "ポイント"
    - 物体の中心の、カメラからの距離でソートするのが基本。
    - 物体同士が入り組むと、ソートでは直らない（OIT が必要）。
    - パーティクルは、系統ごと・距離でソート。
    - 描画順は、不透明 → 半透明（奥から手前）。

## ソート
<strong>奥から手前</strong>の順に描くため、<strong>半透明のオブジェクトを、カメラからの距離で並べ替えます</strong>。

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
| <strong>降順（遠い順）</strong> | 一番遠い物から描く |
| 距離の基準 | オブジェクトの中心（または、<strong>カメラの前方ベクトルへの射影（深度）</strong>）。射影のほうが、横に並んだ物の順序が安定 |
| ソートのキー | 透明度の種類（加算など順序不要のもの）を分けて、通常のものだけソート |

<strong>カメラの前方ベクトルへの射影（ビュー空間の z）</strong>で<strong>並べる</strong>と、<strong>カメラが回転しても、順序が安定</strong>します。

```cpp
float view_depth = Vector3::Dot(center - camera_position, camera_forward);
```

### ソートの限界

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| オブジェクトが交差 | 1 つの順序では、表せない（互いに食い込む） | 分割する・OIT |
| 自己重なり | 1 つのメッシュの手前の面と奥の面（ガラス瓶） | <strong>背面を先、前面を後に描く（2 パス）</strong> |
| 大きな物体 | 中心では、順序を決められない | 分割する・OIT |
| パーティクル | 数が多いので、ソートが重い | GPU ソート・加算ブレンドで回避 |
| ポップ | カメラが動くと、順序が突然入れ替わり、見た目が変わる | 中心の取り方・OIT |

### 自己重なり（2 パス）

<strong>ガラスの瓶</strong>のように、<strong>閉じたメッシュ</strong>は、背面（奥の面）を先に描き、前面（手前の面）を後に描くと、正しい順序に近づきます。

```cpp
context->RSSetState(cull_front_state);
DrawMesh();
context->RSSetState(cull_back_state);
DrawMesh();
```

2 パス描画の内容です。1 回目は前面カリングで、奥の面（背面）を描きます。2 回目は背面カリングで、手前の面（前面）を描きます。

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
| UI | 通常 | 描画順を、レイヤーで決める |

## なぜ、ソートが、必要か

通常の、アルファ ブレンドは、<strong>順序に、依存</strong>します。<strong>奥の物を、先に、手前の物を、後に</strong>、描かないと、正しい色になりません。

```text
赤いガラス（手前）と、青いガラス（奥）を、通して、背景を見るとき:
  正しい順序:  背景 → 青（奥）→ 赤（手前）   → 赤が、手前に、見える
  逆の順序:    背景 → 赤（手前）→ 青（奥）   → 青が、手前に見える（間違い）
```

順序を、間違えると、<strong>手前と奥が、入れ替わった</strong>ような、見た目になります。<strong>深度の書き込みを、しない</strong>ので、後から描いた物が、常に、手前に重なるためです。

## ソートの、基本

<strong>カメラからの、距離の、遠い順</strong>に、並べて、描きます（<strong>画家のアルゴリズム</strong>）。

```cpp
struct TransparentObject {
  float3 position;       // 代表点（中心）
  float sort_key;        // カメラからの距離（の 2 乗）
  // ...
};

// 毎フレーム、カメラからの距離を計算して、遠い順に、並べる。
for (auto& o : transparent_objects) {
  const float3 d = o.position - camera_position;
  o.sort_key = Dot(d, d);                              // 距離の 2 乗（sqrt は、順序に影響しないので、省く）
}
std::sort(transparent_objects.begin(), transparent_objects.end(),
          [](const auto& a, const auto& b) { return a.sort_key > b.sort_key; });   // 遠い順

for (const auto& o : transparent_objects) Draw(o);       // 遠い物から、描く
```

### 距離か、ビュー空間の、深度か

| キー | 内容 | 向く場面 |
| --- | --- | --- |
| カメラからの距離 | 位置と、カメラの、直線距離 | 球状の、広がり（爆発、パーティクルの、群れ） |
| ビュー空間の z 深度 | カメラの前方向に、沿った距離 | 平面的な、板（ビルボード、ガラス板） |

板の、パーティクルは、<strong>画面に、平行な面</strong>を持つので、<strong>ビュー空間の z 深度</strong>で、ソートするほうが、見た目の、前後に、一致します。

## ソートが、破綻する場面

### ① 物体の、内部で、ソートできない

<strong>1 つのメッシュ</strong>（ガラスの瓶、水槽）は、<strong>三角形が、ばらばらの距離</strong>に、あります。物体の、中心の距離だけで、ソートすると、1 つのメッシュの中の、三角形の順序が、描画の順（インデックスの順）で、決まり、手前と奥が、逆に重なることがあります。

| 対策 | 内容 |
| --- | --- |
| 2 パスで描く | 裏面（奥側）を、先に、描き、表面（手前側）を、あとに描く。凸な物（瓶、球）で、正しくなる |
| 深度の、事前描画 | 手前の面だけを、深度に書いて、最前面の、1 層だけを、描く |
| メッシュを、分割 | 三角形を、ソートする。重い |

```cpp
// 凸な半透明の物: 裏面 → 表面の、順で、2 回描く。
context->RSSetState(rs_cull_front.Get());     // 表面をカリング（裏面だけ）
Draw(mesh);
context->RSSetState(rs_cull_back.Get());      // 裏面をカリング（表面だけ）
Draw(mesh);
```

### ② 物体同士が、交差している

<strong>2 つの、大きな物体が、互いに、貫通</strong>していると、<strong>どちらが、手前</strong>か、場所によって違うので、物体単位の、ソートが、成立しません。

### ③ 大きな物体と、小さな物体

<strong>大きな板</strong>（地面に、広がる、水面）と、<strong>小さなパーティクル</strong>では、中心の距離で、並べると、小さな物が、大きな物の、手前にあるのに、先に描かれることがあります。大きな物は、別のパスで、先に描きます（水は、不透明の後、半透明の前、など）。

### ④ 同じ距離

<strong>距離が、ほぼ同じ</strong>の物が、<strong>フレームごとに、順序が、入れ替わる</strong>と、ちらつきます。安定した、タイブレーク（物の ID など）を、加えます。

```cpp
// 距離が、同じなら、ID で順序を決める（フレームごとに、順序が揺れない）。
std::sort(objects.begin(), objects.end(), [](const auto& a, const auto& b) {
  if (a.sort_key != b.sort_key) return a.sort_key > b.sort_key;
  return a.id < b.id;
});
```

## パーティクルの、ソート

パーティクルは、<strong>数千〜数万個</strong>あり、毎フレーム、CPU で、ソートすると、重いです。

| 方法 | 内容 |
| --- | --- |
| システム単位でソート | パーティクル システム（炎、煙）を、1 つの物体として、ソートする。システムの中は、描画の順序のまま（生成順） |
| システムの中も、ソート | 煙のように、重なりが、多い、見た目が、重要なものだけ、パーティクルごとに、ソートする |
| GPU でソート | 計算シェーダーで、ビトニック ソートなどを、使う。数万個でも、ミリ秒以下 |
| ソートしない | 加算ブレンド（火花、光）は、順序に、依存しない。ソート不要 |

### GPU での、ソート

```text
① 計算シェーダーで、各パーティクルの、カメラからの距離を、計算する
② ビトニック ソート（または、基数ソート）で、距離の順に、並べ替える
③ 並べ替えた順序で、描く（インデックス バッファを、並べ替える）
```

ビトニック ソートは、<strong>データ数が、2 の累乗</strong>で、<strong>並列に実行しやすい</strong>ソートです。GPU での、ソートの、定番です（実装は、短いが、本書では、省略。ライブラリの、`FidelityFX Parallel Sort` などを使う方法もある）。

## ソートに、頼らない方法

| 方法 | 内容 |
| --- | --- |
| 加算・乗算ブレンド | 順序に、依存しない |
| OIT（順序に、依存しない、透明） | ソートなしで、近似または、正確な、結果を得る（[OIT](../oit/index.md)） |
| アルファ テスト系 | 深度に書き込み、ソートが、不要（[Alpha Testing](../alpha-test/index.md)） |

## よくあるミス

??? failure "入り組んだ半透明が、前後逆に見える"
    <strong>ソートの粒度を細かく</strong>する、または <strong>OIT</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 不透明の後に、半透明を奥から手前へ
    - [x] 入り組むなら、OIT

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）
- Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Carpenter, "The A-buffer, an Antialiased Hidden Surface Method", SIGGRAPH 1984
- Batcher, "Sorting Networks and their Applications", AFIPS Spring Joint Computer Conference, 1968（ビトニック ソートの原典）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [OIT](../oit/index.md)
- [Blend State](blend-state.md)
