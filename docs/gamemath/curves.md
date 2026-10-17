---
title: 曲線とパス
tags:
  - ゲーム数学
---

# 曲線とパス

カメラのレール・敵の移動経路・弾の軌道・アニメーションのカーブ・道路や川の形など、ゲームでは**なめらかな曲線**を扱う場面が多くあります。曲線は**少ない数の点（制御点）から、なめらかな線を作る**ための数式です。このページでは、ゲームでよく使う**ベジェ曲線・Hermite・Catmull-Rom・B スプライン**の違いと、**一定の速さでパスを進む**ための弧長パラメータ化を説明します。

!!! tip "ポイント"
    - 曲線は<strong>パラメータ t（0〜1）</strong>で、位置を返す関数。<strong>lerp を重ねた</strong>ものと考えられる。
    - <strong>ベジェ</strong>：制御点を<strong>通らず</strong>、引き寄せられる。<strong>デザイン向き</strong>。
    - <strong>Catmull-Rom</strong>：制御点を<strong>必ず通る</strong>。<strong>パス・レール</strong>に向く。
    - <strong>B スプライン</strong>：なめらかさが高い。通らない。
    - <strong>t を一定に進めても、速さは一定にならない</strong>。<strong>弧長パラメータ化</strong>で直す。
    - 3D の曲線は、<strong>x・y・z それぞれに同じ式</strong>を適用するだけ。

## 補間の重ね合わせとしての曲線

曲線の多くは、**lerp を何段階か重ねたもの**として理解できます。

### 2 次ベジェ曲線（制御点 3 つ）

点 P0・P1・P2 があるとき、**P0→P1 の lerp と、P1→P2 の lerp を、さらに lerp** します。

```text
A = lerp(P0, P1, t)
B = lerp(P1, P2, t)
Q = lerp(A, B, t)
```

```cpp
Vector2 QuadraticBezier(Vector2 p0, Vector2 p1, Vector2 p2, float t) {
  Vector2 a = Vector2::Lerp(p0, p1, t);
  Vector2 b = Vector2::Lerp(p1, p2, t);
  return Vector2::Lerp(a, b, t);
}
```

### 3 次ベジェ曲線（制御点 4 つ）

最も標準的なベジェです。P0 が始点、P3 が終点、<strong>P1・P2 が「形を決める引っ張り」</strong>です。

```cpp
Vector2 CubicBezier(Vector2 p0, Vector2 p1, Vector2 p2, Vector2 p3, float t) {
  float u = 1.0f - t;
  return p0 * (u * u * u) + p1 * (3.0f * u * u * t) + p2 * (3.0f * u * t * t) + p3 * (t * t * t);
}
```

<svg class="fig illust" viewBox="0 0 640 260" role="img" aria-label="3 次ベジェ曲線">
<text x="20" y="24" class="fig-title">3 次ベジェ：P0 から P3 へ。P1・P2 に引っ張られる（通らない）</text>
<polyline points="60,200 160,60 400,40 580,190" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4" opacity="0.6"/>
<path d="M60,200 C160,60 400,40 580,190" fill="none" stroke="#4c8bf5" stroke-width="4"/>
<circle cx="60" cy="200" r="8" fill="#e5484d"/><text x="40" y="226" style="font-size:12px">P0（始点）</text>
<circle cx="160" cy="60" r="7" fill="currentColor"/><text x="170" y="56" style="font-size:12px">P1</text>
<circle cx="400" cy="40" r="7" fill="currentColor"/><text x="410" y="36" style="font-size:12px">P2</text>
<circle cx="580" cy="190" r="8" fill="#e5484d"/><text x="540" y="216" style="font-size:12px">P3（終点）</text>
</svg>

| 性質 | 説明 |
| --- | --- |
| **始点・終点を通る** | `t = 0` で P0、`t = 1` で P3 |
| **途中の点は通らない** | P1・P2 は「引っ張る方向」を決める |
| **P0→P1 が出発の方向** | 始点での接線は、P0 から P1 への向き |
| **凸包の中に収まる** | 制御点で囲んだ範囲から、はみ出さない |
| **曲線の接続** | 2 本をつなぐときは、**つなぎ目の前後の制御点を一直線に**すると滑らか |

### デザイン向けの使い道

| 使いどころ | 説明 |
| --- | --- |
| **アニメーション カーブ** | 時間（x）と値（y）の関係をベジェで描く。**CSS の `cubic-bezier`** もこれ |
| **道路・川・パスの形** | エディタで制御点を動かして、形を作る |
| **弾の軌道** | 発射点・目標点・曲がる方向 |
| **UI の軌跡** | アイテムが画面の隅へ飛んでいく |

## Hermite 曲線

<strong>始点・終点の位置とその点での速度（接線）</strong>で曲線を決めます。ベジェの制御点 P1・P2 を、「接線」の形に言い換えたものです。

```text
P1 = P0 + (m0 / 3)
P2 = P3 - (m1 / 3)
```

| 点 | 説明 |
| --- | --- |
| **位置 ＋ 速度で指定** | アニメーションのキーフレームで、「値」と「傾き」を持たせる形 |
| **キー間の補間** | 隣り合うキーを、Hermite でつなぐと、**速度が連続**して滑らか |
| **ベジェと同じ曲線** | 表現が違うだけ |

## Catmull-Rom スプライン

**与えた点をすべて通る**滑らかな曲線です。**点の並びを渡すだけ**でなめらかな経路が作れるので、**カメラのレールや敵の巡回路**に向いています。

4 つの連続する点 P0〜P3 があるとき、**P1 から P2 の間**を描きます。

```cpp
Vector2 CatmullRom(Vector2 p0, Vector2 p1, Vector2 p2, Vector2 p3, float t) {
  float t2 = t * t;
  float t3 = t2 * t;
  return (p1 * 2.0f + (p2 - p0) * t + (p0 * 2.0f - p1 * 5.0f + p2 * 4.0f - p3) * t2 +
          (p1 * 3.0f - p0 - p2 * 3.0f + p3) * t3) * 0.5f;
}
```

| 点 | 説明 |
| --- | --- |
| **点を必ず通る** | 渡した点を全部通る |
| **前後の点が必要** | P1〜P2 の区間に、P0 と P3 が必要。**両端は端の点を重複させる**などで補う |
| **接線の自動決定** | 各点での接線は、**前後の点の差**で決まる（Hermite の特別な場合） |
| **オーバーシュート** | 点の間隔が不揃いだと膨らむことがある（**Centripetal 版**で軽減） |
| **向き** | 接線（微分）が、進行方向になる |

### パスの接線（進行方向）

曲線の**微分**がその点での進む向きです。**カメラやキャラをパスに沿って向かせる**ときに使います。

```cpp
Vector2 Tangent(Vector2 p0, Vector2 p1, Vector2 p2, Vector2 p3, float t) {
  Vector2 a = CatmullRom(p0, p1, p2, p3, t + 0.001f);
  Vector2 b = CatmullRom(p0, p1, p2, p3, t - 0.001f);
  return (a - b).Normalized();
}
```

微小に前後の点を取って、その差を使う**数値微分**で十分です。

## B スプライン

制御点を**通らず**、**制御点でゆるく引かれる**曲線です。**非常になめらか**（曲率も連続）で、道路や車の形のように**角が出てはいけない**ものに向いています。

| 点 | 説明 |
| --- | --- |
| **局所的** | 1 つの制御点を動かしても、近くしか変わらない |
| **なめらか** | 2 回微分まで連続（カメラのレールでガクッとしない） |
| **点を通らない** | 制御点は「引き寄せる」だけ |
| **NURBS** | 重みを付けた B スプライン。CAD で使われる。ゲームでは少なめ |

## 曲線の選び方

| 種類 | 点を通る | 局所性 | 向いている用途 |
| --- | --- | --- | --- |
| <strong>ベジェ（3 次）</strong> | 両端のみ | 1 区間ごと | デザイン・アニメーション カーブ・弾の軌道 |
| **Hermite** | すべて | 1 区間ごと | キーフレーム補間（位置と速度） |
| **Catmull-Rom** | すべて | 4 点ごと | カメラのレール・巡回パス |
| **B スプライン** | 通らない | 局所的 | 道路・滑らかな形 |

## 弧長パラメータ化：一定の速さで進む

曲線の `t` を**一定の速さで増やしても**、**実際の移動距離は一定になりません**。制御点が密な所では t が進んでも距離は小さく、疎な所では大きくなります。

<svg class="fig illust" viewBox="0 0 680 200" role="img" aria-label="t の等間隔と、弧長の等間隔">
<text x="20" y="24" class="fig-title">t を等間隔に刻むと、曲線上の間隔はばらつく（上）。弧長で刻むと一定（下）</text>
<path d="M40,100 C160,20 300,170 640,90" fill="none" stroke="currentColor" stroke-width="2" opacity="0.4" transform="translate(0,-30)"/>
<g fill="#e5484d"><circle cx="40" cy="70" r="5"/><circle cx="95" cy="52" r="5"/><circle cx="150" cy="46" r="5"/><circle cx="205" cy="56" r="5"/><circle cx="262" cy="86" r="5"/><circle cx="330" cy="102" r="5"/><circle cx="420" cy="88" r="5"/><circle cx="540" cy="68" r="5"/><circle cx="640" cy="60" r="5"/></g>
<path d="M40,170 C160,90 300,240 640,160" fill="none" stroke="currentColor" stroke-width="2" opacity="0.4" transform="translate(0,-30)"/>
<g fill="#2ea043"><circle cx="40" cy="140" r="5"/><circle cx="112" cy="116" r="5"/><circle cx="185" cy="124" r="5"/><circle cx="262" cy="156" r="5"/><circle cx="350" cy="160" r="5"/><circle cx="440" cy="148" r="5"/><circle cx="535" cy="136" r="5"/><circle cx="640" cy="130" r="5"/></g>
</svg>

### 作り方：距離のテーブル

| 手順 | 内容 |
| --- | --- |
| **① 曲線を細かく刻む** | `t` を 0〜1 で 100 分割などして、各点の位置を求める |
| **② 累積距離を計算** | 隣り合う点の距離を足して、<strong>始点からの距離（弧長）</strong>のテーブルを作る |
| **③ 距離から t を引く** | 欲しい距離 d に対し、テーブルを**二分探索**して、その前後の t を線形補間する |

```cpp
class ArcLengthTable {
 public:
  template <typename Curve>
  void Build(const Curve& curve, int segments) {
    t_values_.clear();
    lengths_.clear();
    Vector2 prev = curve(0.0f);
    float total = 0.0f;
    t_values_.push_back(0.0f);
    lengths_.push_back(0.0f);
    for (int i = 1; i <= segments; ++i) {
      float t = static_cast<float>(i) / static_cast<float>(segments);
      Vector2 p = curve(t);
      total += (p - prev).Length();
      t_values_.push_back(t);
      lengths_.push_back(total);
      prev = p;
    }
  }

  float TotalLength() const { return lengths_.back(); }

  float TFromDistance(float distance) const {
    auto it = std::lower_bound(lengths_.begin(), lengths_.end(), distance);
    if (it == lengths_.begin()) return 0.0f;
    if (it == lengths_.end()) return 1.0f;
    size_t i = static_cast<size_t>(it - lengths_.begin());
    float span = lengths_[i] - lengths_[i - 1];
    float k = span > 0.0f ? (distance - lengths_[i - 1]) / span : 0.0f;
    return std::lerp(t_values_[i - 1], t_values_[i], k);
  }

 private:
  std::vector<float> t_values_;
  std::vector<float> lengths_;
};
```

**ビルド時やパスの作成時に 1 回作って**、移動中は `TFromDistance(speed × time)` を呼ぶだけにします。

## パス追従

| 使い方 | 説明 |
| --- | --- |
| **一定の速さで進む** | 距離 `d += speed × dt` → `t = TFromDistance(d)` → 位置 |
| **向きを合わせる** | 位置の微分（接線）を、前方向にする |
| <strong>先読み（ルックアヘッド）</strong> | 少し先の位置を見て、向きを決める（自然なカーブ） |
| **ループ** | 距離を全長で `fmod` する |
| **カメラのレール** | 位置はパス、向きは別のパスか、目標を見る |
| **ジェットコースター** | 勾配から、速さを変える（位置エネルギー） |

## 3D の曲線

**x・y・z の 3 成分に同じ式を適用**するだけです。`Vector2` を `Vector3` に置き換えます。向き（姿勢）を滑らかに変えたいときは、位置とは別に**クォータニオンを slerp・squad** で補間します（[3D：回転](rotation.md)）。

## よくあるミス

??? failure "t を一定に進めて、速さがばらつく"
    弧長パラメータ化をします。

??? failure "Catmull-Rom の両端で、前後の点が足りない"
    端の点を重複させて、仮の前後の点を作ります。

??? failure "接線を正規化せず、速さが不安定になる"
    進行方向だけが必要なら、`Normalized()` します。

??? failure "弧長テーブルを、毎フレーム作り直す"
    パスが変わらないなら、1 回だけ作って保存します。

??? failure "ベジェが制御点を通ると思って、形が思い通りにならない"
    通るのは両端だけです。途中は引き寄せられるだけです。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 曲線は<strong>lerp を重ねたもの</strong>。<strong>ベジェ・Hermite・Catmull-Rom・B スプライン</strong>
    - [x] <strong>ベジェ</strong>はデザイン向き（両端のみ通る）。<strong>Catmull-Rom</strong> は点を通る（レール・パス）
    - [x] <strong>接線（微分）</strong>が進行方向
    - [x] <strong>t 一定 ≠ 速さ一定</strong>。<strong>弧長テーブル</strong>で距離から t を引く
    - [x] 3D は<strong>各成分に同じ式</strong>。姿勢は<strong>slerp</strong>

## 関連ページ

- [ゲーム数学](index.md)
- [補間（lerp）](interpolation.md)
- [イージング](easing.md)
- [ゲームでよく使うベクトル公式](vector-recipes.md)
- [3D：回転](rotation.md)
