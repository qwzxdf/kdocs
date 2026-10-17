---
title: Hi-Z SSR
tags:
  - 描画
---

# Hi-Z SSR

[SSR の基礎](ssr-basics.md)の線形マーチ（1 ピクセルずつ進む）は、**遠くまで進むとステップが何十〜何百回**にもなり、**重く**なります。**Hi-Z SSR**は、<strong>階層的な深度バッファ（Hi-Z）</strong>を使って、**空いている領域を一気に飛ばす**ことで、**少ないステップで遠くまでレイを進めます**。**粗い反射・長いレイ・精度の高い当たり判定**が要る、現在の主流の方式です。このページでは、**Hi-Z の作り方・探索のアルゴリズム・精度の工夫**を順に説明します。

!!! tip "ポイント"
    - <strong>Hi-Z</strong> ＝ <strong>各セルが、「その範囲で最も手前の深度（最小）」を持つミップ チェーン</strong>。
    - レイを進めるとき、<strong>粗いミップで大きなセルごとに</strong>、<strong>「レイはこのセルの中のどの面よりも手前にいる」</strong>なら、<strong>セルの端まで一気に飛ばす</strong>。
    - 当たりそうな所では、<strong>ミップを下りて、細かく</strong>確かめる。
    - 画面空間では、<strong>レイは、(x, y, 深度) の空間で直線</strong>。<strong>深度（z/w）は、画面上で線形</strong>なので計算が簡単。
    - <strong>ステップ数が距離に依存せず、数十回に収まる</strong>。
    - 終盤に<strong>厚み（thickness）の検証</strong>が必要。

## なぜ速くなるか

線形マーチは**空いている空間でも、1 ピクセルずつ**進みます。**レイの周りに何も遮る物がない**と分かれば、**一気に進める**はずです。

<svg class="fig illust" viewBox="0 0 780 290" role="img" aria-label="Hi-Z でレイを飛ばす">
<text x="20" y="24" class="fig-title">粗いミップ（大きなセル）で、空いている領域を一気に飛ばし、近づいたら細かいミップへ下りる</text>
<line x1="60" y1="240" x2="720" y2="240" stroke="currentColor" stroke-width="2"/>
<g stroke="currentColor" stroke-width="1" fill="rgba(76,139,245,0.15)"><rect x="60" y="150" width="160" height="90"/><rect x="220" y="150" width="160" height="90"/><rect x="380" y="100" width="160" height="140"/><rect x="540" y="150" width="180" height="90"/></g>
<text x="64" y="144" style="font-size:12px">セルの「最小深度」（最も手前の面）</text>
<polyline points="80,60 220,100 380,140" fill="none" stroke="#e5484d" stroke-width="3"/>
<g fill="#e5484d"><circle cx="80" cy="60" r="5"/><circle cx="220" cy="100" r="5"/><circle cx="380" cy="140" r="5"/></g>
<text x="90" y="52" style="font-size:12px;fill:#e5484d;font-weight:700">大きなセルを、1 ステップで飛ばす</text>
<polyline points="380,140 420,155 460,170 480,182" fill="none" stroke="#2ea043" stroke-width="3"/>
<g fill="#2ea043"><circle cx="420" cy="155" r="4"/><circle cx="460" cy="170" r="4"/><circle cx="480" cy="182" r="4"/></g>
<text x="400" y="272" style="font-size:12px;fill:#2ea043;font-weight:700">近づいたら、細かいセルで確かめる</text>
</svg>

| 方式 | ステップ数 |
| --- | --- |
| **線形マーチ** | 距離（ピクセル）に比例（数百回） |
| **Hi-Z** | **距離の対数に比例**（数十回）。空いている所は、一気に飛ぶ |

## Hi-Z の作り方

**深度バッファから、ミップ チェーン**を作ります。<strong>各ミップの 1 画素は、下のミップの 2×2 画素の「最小」</strong>（最も手前＝**標準 Z では最小値**）です。

<div class="formula">HiZ[level + 1](x, y) = min( HiZ[level](2x, 2y), HiZ[level](2x+1, 2y), HiZ[level](2x, 2y+1), HiZ[level](2x+1, 2y+1) )</div>

| 点 | 説明 |
| --- | --- |
| <strong>最小（最も手前）</strong> | 「**このセルの中で最も手前の面**」の深度。**これより手前にいるレイは、このセルの中のどの面にも当たらない** |
| **reverse-Z** | 深度が反転しているので、**最大値**を取る |
| **平均ではない** | [SAO のミップ](../ao/sao.md)は、境界の嘘の深度を避けるための選択でしたが、Hi-Z は**保守的な判定**のため、<strong>最小（または最大）</strong>が正しい |
| **非 2 の冪の画面** | 端の画素を取りこぼさない（切り上げ） |
| **作成コスト** | <strong>コンピュート 1 回（複数ミップをグループ内で一度に）</strong>で、0.1〜0.3 ms 程度 |

```hlsl
float HiZMin(Texture2D<float> src, int2 pixel) {
  float a = src.Load(int3(pixel * 2 + int2(0, 0), 0));
  float b = src.Load(int3(pixel * 2 + int2(1, 0), 0));
  float c = src.Load(int3(pixel * 2 + int2(0, 1), 0));
  float d = src.Load(int3(pixel * 2 + int2(1, 1), 0));
  return min(min(a, b), min(c, d));
}
```

## 画面空間でのレイ

Hi-Z の探索は、**ビュー空間ではなく、(画面 x, 画面 y, 深度) の空間**で行います。**透視投影の性質**：**画面上の直線は、ビュー空間の直線**であり、**非線形深度 z/w（NDC の z）も、画面上で線形に変化します**。つまり、**レイは (x, y, z_ndc) の空間で直線**です。

| 空間 | レイの形 |
| --- | --- |
| **ビュー空間** | 直線（ただし、画面上の歩幅が不均一） |
| <strong>(画面 xy, NDC の z)</strong> | <strong>直線（均一な補間）</strong> |

```hlsl
float3 origin_ss = float3(uv0, ndc_z0);
float3 end_ss = float3(uv1, ndc_z1);
float3 dir_ss = end_ss - origin_ss;
```

**始点と終点をそれぞれ射影して**画面空間に変換し、その間を直線で結びます（`uv` は 0〜1、`ndc_z` は深度バッファの値と同じ）。**深度バッファの値と直接比べられる**のが利点です。

## 探索アルゴリズム

**ミップ レベルを上げ下げしながら**、レイを進めます。

| 状態 | 動作 |
| --- | --- |
| **レイが現在のセルの最小深度より手前**（空いている） | **セルの端まで進む**。**ミップを上げる**（次はもっと大きく飛べる） |
| **レイがセルの内部で最小深度の面に届く** | **届く位置まで進み、ミップを下げて**精査 |
| **ミップ 0 に達して、まだ当たり** | **交点**（**厚みを検証**） |

```hlsl
bool TraceHiZ(float3 origin, float3 dir, out float3 hit) {
  int level = kStartLevel;
  float t = 0.0;
  float2 inv_dir = 1.0 / dir.xy;
  int2 step_dir = int2(dir.x > 0 ? 1 : 0, dir.y > 0 ? 1 : 0);

  for (int i = 0; i < kMaxIterations && level >= 0; ++i) {
    float3 p = origin + dir * t;
    if (any(p.xy < 0.0) || any(p.xy > 1.0)) return false;

    float2 dims = hiz_size >> level;
    int2 cell = int2(p.xy * dims);
    float min_z = hiz.Load(int3(cell, level)).r;

    float2 boundary = (cell + step_dir) / dims;
    float2 t_xy = (boundary - origin.xy) * inv_dir;
    float t_boundary = min(t_xy.x, t_xy.y);

    float t_z = (min_z - origin.z) / dir.z;

    if (p.z < min_z) {
      if (t_z < t_boundary) {
        t = t_z;
        level -= 1;
      } else {
        t = t_boundary + kEpsilon;
        level = min(level + 1, kMaxLevel);
      }
    } else {
      level -= 1;
    }
  }
  hit = origin + dir * t;
  return level < 0;
}
```

| 点 | 説明 |
| --- | --- |
| **`cell + step_dir`** | レイの進む向きの**セルの境界**（右・下なら、次のセルの端） |
| **`t_boundary`** | レイが**セルの境界に達する時刻 t**（x・y のうち早い方） |
| **`t_z`** | レイが**セルの最小深度の面に達する時刻** |
| **`p.z < min_z`** | **レイがこのセルの全ての面より手前**（空いている） |
| **`t_z < t_boundary`** | **セルの中で最小深度の面に届く**（当たりの候補） → 下りて精査 |
| **それ以外** | **セルを抜ける**（何にも当たらない） → 端まで進み、**上がる** |
| **`level < 0`** | **ミップ 0 の最も細かいセルで当たり** |

!!! note "アルゴリズムは、実装で細部が違う"
    境界の扱い（epsilon）、**レイの向きによる、セルの選び方**、**ミップ 0 での終了条件**など、**細部は実装ごとに異なります**。ここは**考え方**を示したものです。**詳しい実装**は参考の資料（Stachowiak の講演、Uludag の章）を参照してください。

## 厚みの検証

Hi-Z は**レイが最も細かいセルで深度に達した**所を当たりとします。<strong>この点が本当に「その物体の表面」</strong>かを**厚み**で検証します。

| 判定 | 内容 |
| --- | --- |
| **深度の差** | 当たった位置の**レイのビュー空間の奥行き**と、**その画素の深度**の差が**厚み以内**か |
| **範囲外なら** | **薄い物のはるか後ろ**に突き抜けたとみなし、**当たりとしない**。**レイを続ける**（またはその方向は諦める） |

```hlsl
float ray_z = LinearizeDepth(hit.z);
float scene_z = LinearizeDepth(depth_tex.Load(int3(hit_pixel, 0)).r);
bool valid = (ray_z - scene_z) < thickness;
```

**単純に諦める**と**手前の細い物の後ろにある面が、反射に映らず**、**穴**が開きます。**厚みで弾かれたら、探索を続ける**実装もあります（**手前の物体を飛び越えて**、奥を探す）。

## 精度とアーティファクト

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| **セルの境界の取りこぼし** | 浮動小数点の誤差で**境界のすぐ手前で止まる**（無限ループ・飛び越し） | **epsilon を境界に足す**（`t_boundary + eps`）。反復回数の上限 |
| **斜めのレイが深度の面に平行** | `dir.z` が 0 に近い（0 除算） | `dir.z` の符号・大きさをチェック |
| **画面外** | レイが画面の範囲を出た | 範囲外で打ち切り（当たりなし） |
| **ミップ 0 以外で誤った当たり** | 最小深度は**保守的**（実際の面より手前） | **ミップ 0 で必ず確かめる** |
| **ミップの精度** | 低い精度の深度 | 32 ビット浮動小数点の深度 |
| **ステップ数の上限** | 複雑なシーンで収束しない | **上限**を設けて、**当たらなかった**扱い（または近似） |

## Hi-Z SSR の全体像

| パス | 内容 |
| --- | --- |
| **① Hi-Z の作成** | 深度の最小ミップ チェーン |
| **② 反射方向（レイ）の生成** | G-Buffer の法線・粗さから |
| **③ Hi-Z トレース** | ビュー → 画面空間に変換して、探索 |
| **④ 色の取得** | 当たった画素の色（前フレーム・動きベクトル） |
| **⑤ フェード・合成** | 信頼度でフォールバックと混ぜる（[フォールバック](ssr-fallback.md)） |

## 線形マーチ（DDA）との使い分け

| 状況 | おすすめ |
| --- | --- |
| **短いレイ・粗いレイ・単純な実装** | 画面空間の DDA |
| **長いレイ・多くの粗い反射・精度が要る** | **Hi-Z** |
| <strong>確率的 SSR（粗さでサンプルが多様）</strong> | **Hi-Z**（レイ長さがばらつく） |
| **モバイル** | 軽い DDA か、SSR を省く |

**併用**する実装もあります（**近距離は DDA、遠距離は Hi-Z**）。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **遠くまでのレイが少ないステップ** | **Hi-Z の作成コスト**（小さい） |
| **取りこぼしが少ない**（セルの最小深度で保守的） | **実装が複雑**（境界・epsilon・ミップの上下） |
| **確率的 SSR と相性が良い** | 厚みの扱いは基礎の SSR と同じ課題 |
| **ステップ数が距離に依存しない** | 画面外・裏側が映らない限界は同じ |

## よくあるミス

??? failure "Hi-Z を、平均でミップ化して、誤った当たりが出る"
    <strong>最小（reverse-Z なら最大）</strong>で作ります。

??? failure "reverse-Z なのに、最小のままで探索して、全く当たらない"
    深度の向きに合わせます（**reverse-Z は、最大値のミップ**）。

??? failure "セルの境界で止まって、無限ループ・飛び越し"
    **epsilon**を足し、**反復回数の上限**を設けます。

??? failure "ミップ 0 の確認を省いて、粗いセルの当たりをそのまま採用"
    最後は**ミップ 0 で必ず確認**します。

??? failure "ビュー空間と画面空間の、座標を混ぜる"
    探索は、<strong>(画面 xy, NDC の z)</strong> で一貫させます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Hi-Z SSR ＝ <strong>階層的な最小深度で、空いている領域を一気に飛ばす</strong>レイ探索
    - [x] Hi-Z ＝ <strong>各セルが、範囲内の最も手前の深度（最小）</strong>のミップ。<strong>reverse-Z は最大</strong>
    - [x] <strong>空いていれば端まで進んで、ミップを上げ</strong>、<strong>当たりそうなら下りて精査</strong>
    - [x] 探索は<strong>(画面 xy, NDC の z) の直線</strong>。<strong>最後に厚みで検証</strong>
    - [x] <strong>ステップ数が、距離に依存しない</strong>。<strong>確率的 SSR の基盤</strong>

## 参考

- Uludag, "Hi-Z Screen-Space Cone-Tracing"（GPU Pro 5, 2014）
- Stachowiak, Uludag, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015 Advances in Real-Time Rendering、Frostbite）

## 関連ページ

- [反射](index.md)
- [SSR の基礎](ssr-basics.md)
- [確率的 SSR](ssr-stochastic.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
- [SAO（ミップとの違い）](../ao/sao.md)
