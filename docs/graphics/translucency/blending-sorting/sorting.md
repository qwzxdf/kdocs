---
title: ソート
tags:
  - 描画
---

# ソート

**半透明は、奥から手前の順に描かないと、結果が崩れます**。**物体単位のソート・パーティクル単位のソート・面ごとのソート**など、**粒度**があります。このページでは、**ソートの方法と、順序の決め方**を説明します。

!!! tip "ポイント"
    - **物体の中心の、カメラからの距離でソート**するのが**基本**。
    - **物体同士が入り組むと、ソートでは直らない**（OIT が必要）。
    - **パーティクルは、系統ごと・距離でソート**。
    - **描画順は、不透明 → 半透明（奥から手前）**。

## ソート
**奥から手前**の順に描くため、**半透明のオブジェクトを、カメラからの距離で並べ替えます**。

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
| **`LengthSquared`** | **距離の比較だけ**なので、**平方根は不要** |
| <strong>降順（遠い順）</strong> | **一番遠い物から**描く |
| **距離の基準** | **オブジェクトの中心**（または、<strong>カメラの前方ベクトルへの射影（深度）</strong>）。**射影のほうが、横に並んだ物の順序が安定** |
| **ソートのキー** | **透明度の種類（加算など順序不要のもの）を分けて**、**通常のものだけソート** |

<strong>カメラの前方ベクトルへの射影（ビュー空間の z）</strong>で**並べる**と、**カメラが回転しても、順序が安定**します。

```cpp
float view_depth = Vector3::Dot(center - camera_position, camera_forward);
```

### ソートの限界

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **オブジェクトが交差** | **1 つの順序では、表せない**（互いに食い込む） | **分割する**・**OIT** |
| **自己重なり** | **1 つのメッシュの手前の面と奥の面**（ガラス瓶） | <strong>背面を先、前面を後に描く（2 パス）</strong> |
| **大きな物体** | **中心では、順序を決められない** | **分割する**・**OIT** |
| **パーティクル** | **数が多い**ので、**ソートが重い** | **GPU ソート・加算ブレンドで回避** |
| **ポップ** | **カメラが動くと、順序が突然入れ替わり、見た目が変わる** | **中心の取り方・OIT** |

### 自己重なり（2 パス）

**ガラスの瓶**のように、**閉じたメッシュ**は、**背面（奥の面）を先に描き、前面（手前の面）を後に描く**と、**正しい順序**に近づきます。

```cpp
context->RSSetState(cull_front_state);
DrawMesh();
context->RSSetState(cull_back_state);
DrawMesh();
```

| パス | カリング | 描く面 |
| --- | --- | --- |
| **1 回目** | **前面カリング** | <strong>奥の面（背面）</strong> |
| **2 回目** | **背面カリング** | <strong>手前の面（前面）</strong> |

## ブレンド順序の決め方（まとめ）
| 物 | ブレンド | ソート |
| --- | --- | --- |
| **ガラス・水面** | 通常 | **必要** |
| **炎・爆発・魔法** | 加算 | **不要** |
| **煙** | 通常（または乗算済み） | **必要** |
| <strong>影の板（ブロブ）</strong> | 乗算 | **不要** |
| **UI** | 通常 | **描画順を、レイヤーで決める** |

## よくあるミス

??? failure "入り組んだ半透明が、前後逆に見える"
    **ソートの粒度を細かく**する、または **OIT**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **不透明の後に、半透明を奥から手前へ**
    - [x] **入り組むなら、OIT**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [アルファ ブレンドとソート](index.md)
- [OIT](../oit/index.md)
- [ブレンド ステート](blend-state.md)
