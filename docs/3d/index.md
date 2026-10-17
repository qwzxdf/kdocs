# 3D ゲーム

3D ゲームの画面は、<strong>「3D の世界にある物体を、カメラから見た 2D の絵にする」</strong>計算でできています。この計算の中心にあるのが、**座標を、いくつもの「空間」に順番に変換していく**流れです。モデルの中の座標 → 世界の座標 → カメラから見た座標 → 画面に映る座標、という具合です。それを行うのが、**ベクトルと行列**で、その最後の大事な段階が<strong>投影（プロジェクション）</strong>です。このカテゴリでは、3D ゲームを作るために必要な、**数学・カメラ・描画のしくみ・当たり判定**を、順に説明します。数式は、ゲームで使う形に絞り、**なぜそうなるのか**を、図とコードで説明します。

!!! tip "ポイント"
    - 3D の描画は、<strong>座標を、空間から空間へ変換する流れ</strong>（ローカル → ワールド → ビュー → クリップ → 画面）。
    - 変換は<strong>行列</strong>で表す。<strong>MVP</strong>（モデル・ビュー・プロジェクション）の 3 つの行列を掛ける。
    - まず<strong>座標系の決まり</strong>（左手系か右手系か、Y が上か）と、<strong>行列の規約</strong>（行ベクトルか列ベクトルか）をそろえる。ここがずれると、すべてが狂う。
    - 回転には<strong>クォータニオン</strong>を使う（オイラー角はジンバルロックがある）。
    

## 描画の流れ（座標の旅）

3D ゲームの 1 つの頂点は、画面に出るまでに、次の「空間」を順に通ります。

<div class="anim" data-type="graph" data-label="頂点が、画面に出るまでの旅">
n local ローカル空間 0 0 hit
n world ワールド空間 1 0
n view ビュー空間 2 0
n clip クリップ空間 3 0
n ndc NDC 4 0
n screen 画面 5 0
l local world
l world view
l view clip
l clip ndc
l ndc screen
# 1. ローカル空間：モデルの中心を原点にした、モデル自身の座標（モデリング ソフトで作った形）
---
n local ローカル空間 0 0
n world ワールド空間 1 0 hit
n view ビュー空間 2 0
n clip クリップ空間 3 0
n ndc NDC 4 0
n screen 画面 5 0
l local world hit ワールド行列
l world view
l view clip
l clip ndc
l ndc screen
# 2. ワールド空間：ゲームの世界の座標。モデルを、位置・回転・拡大で、世界に置く（ワールド行列）
---
n local ローカル空間 0 0
n world ワールド空間 1 0
n view ビュー空間 2 0 hit
n clip クリップ空間 3 0
n ndc NDC 4 0
n screen 画面 5 0
l local world
l world view hit ビュー行列
l view clip
l clip ndc
l ndc screen
# 3. ビュー空間：カメラを原点にした座標。カメラの位置・向きを打ち消す（ビュー行列）
---
n local ローカル空間 0 0
n world ワールド空間 1 0
n view ビュー空間 2 0
n clip クリップ空間 3 0 hit
n ndc NDC 4 0
n screen 画面 5 0
l local world
l world view
l view clip hit プロジェクション行列
l clip ndc
l ndc screen
# 4. クリップ空間：遠近感をつける（プロジェクション行列）。ここで、見える範囲かどうかが決まる
---
n local ローカル空間 0 0
n world ワールド空間 1 0
n view ビュー空間 2 0
n clip クリップ空間 3 0
n ndc NDC 4 0 hit
n screen 画面 5 0
l local world
l world view
l view clip
l clip ndc hit w_で割る
l ndc screen
# 5. NDC：w で割って、x・y が -1〜1 の正規化された座標になる（透視除算）
---
n local ローカル空間 0 0
n world ワールド空間 1 0
n view ビュー空間 2 0
n clip クリップ空間 3 0
n ndc NDC 4 0
n screen 画面 5 0 hit
l local world
l world view
l view clip
l clip ndc
l ndc screen hit ビューポート変換
# 6. 画面：ピクセルの座標（0〜幅、0〜高さ）に変換されて、画面に描かれる
</div>

| 空間 | 何を原点・基準にするか | どの行列で次へ |
| --- | --- | --- |
| **ローカル**（モデル） | モデル自身の中心 | **ワールド行列**（モデル行列） |
| **ワールド** | ゲームの世界の原点 | **ビュー行列** |
| **ビュー**（カメラ） | カメラの位置（原点）と向き（−Z や +Z が前） | **プロジェクション行列** |
| **クリップ** | 見える範囲の箱（視錐台）が、直方体になった空間 | **w で割る**（透視除算） |
| **NDC**（正規化デバイス座標） | x、y が −1〜1（z は 0〜1 か −1〜1） | **ビューポート変換** |
| **スクリーン** | 画面のピクセル（左上が原点が多い） | （GPU が、ここに描く） |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [DirectXMath](directxmath.md) | DirectXMath の型・関数・ロードとストア・行ベクトル |
| [SimpleMath](simplemath.md) | DirectXMath を、普通の C++ で書けるようにしたラッパー（このカテゴリで使う） |
| [座標系](coordinate-systems.md) | 左手系と右手系、Y が上か Z が上か、各エンジンの違い |
| [ベクトル](vectors.md) | 長さ、正規化、内積、外積、反射、射影 |
| [行列](matrices.md) | 平行移動・回転・拡大、同次座標、合成の順番、逆行列、行ベクトルと列ベクトル |
| [MVP 変換](transforms-mvp.md) | モデル・ワールド・ビュー・プロジェクションの、掛け方と使い方 |
| [投影（プロジェクション）](projection.md) | 透視投影と正射投影、視野角、near / far、NDC、深度の非線形 |
| [カメラ](camera.md) | ビュー行列、LookAt、FPS カメラ、軌道カメラ、追従カメラ |
| [回転とクォータニオン](rotation.md) | オイラー角、ジンバルロック、クォータニオン、補間 |
| [深度バッファとカリング](depth-culling.md) | 深度テスト、z-fighting、reverse-Z、視錐台カリング |
| [ピッキングとレイキャスト](picking-raycast.md) | マウスの位置から 3D の世界を指す、レイと交差判定 |
| [法線とライティング](lighting-normals.md) | 法線、拡散反射、鏡面反射、シェーダーでの計算 |
| [メッシュとテクスチャ](mesh-textures.md) | 頂点、インデックス、UV、ミップマップ、サンプラー |
| [3D の当たり判定](collision-3d.md) | 球、AABB、OBB、カプセル、判定の組み合わせ |
| [スキニング（骨格アニメーション）](skinning-animation.md) | ボーン、スキン ウェイト、アニメーションの補間 |

## 数学ライブラリ

3D の数学は、**自作せずに、ライブラリを使う**のが基本です。

| ライブラリ | 特徴 |
| --- | --- |
| <strong>[DirectXMath](directxmath.md)</strong>（`<DirectXMath.h>`） | Windows の標準（Visual Studio に付属）。**行ベクトル**。左手系（`LH`）と右手系（`RH`）の**両方の関数**がある。SIMD で速い。型が 2 種類（保存用・計算用）で、書き方が独特 |
| <strong>[SimpleMath](simplemath.md)</strong>（DirectX Tool Kit） | DirectXMath の**ラッパー**。`Vector3`、`Matrix`、`Quaternion` を、演算子とメンバ関数で書ける。**右手系が既定**。**このカテゴリはこれを使う** |
| **glm** | OpenGL 風の数学。ヘッダだけ。**列ベクトル**、既定は右手系 |
| **Eigen** | 線形代数が中心。大きな行列に強い |
| **自作** | 学習用に、`Vec3`、`Mat4` を 1 度は自作すると、理解が深まる |

### このカテゴリの決まり

| 項目 | 決まり |
| --- | --- |
| 描画 API | **DirectX 11**（Direct3D 11）。描画のコードは、DX11 で書く |
| シェーダー | **HLSL**（Shader Model 5） |
| 数学ライブラリ | **SimpleMath**（DirectX Tool Kit）。速さが必要な所だけ DirectXMath |
| 座標系 | **右手系・Y-up**（SimpleMath の既定） |
| 前方向 | **−Z**（`Vector3::Forward` ＝ `(0, 0, -1)`） |
| 行列の規約 | **行ベクトル**（`v * M`）。掛け順は**左から右**（拡大 → 回転 → 平行移動） |
| 三角形の表 | <strong>反時計回り（CCW）</strong>が表（Direct3D では `FrontCounterClockwise = TRUE`） |
| 角度 | ラジアン |
| 単位 | 1 ＝ 1 メートル |

## 学ぶ順番のおすすめ

1. [DirectXMath](directxmath.md)・[SimpleMath](simplemath.md)：使う道具
2. [座標系](coordinate-systems.md) → [ベクトル](vectors.md) → [行列](matrices.md)：土台
3. [MVP 変換](transforms-mvp.md) → [投影](projection.md) → [カメラ](camera.md)：描画の流れ
4. [回転とクォータニオン](rotation.md)：向きの扱い
5. 必要に応じて：[深度とカリング](depth-culling.md)、[ピッキング](picking-raycast.md)、[ライティング](lighting-normals.md)、[当たり判定](collision-3d.md)、[スキニング](skinning-animation.md)

## 関連ページ

- [SIMD（ベクトル化）](../optimize/simd.md)
- [描画の最適化](../optimize/rendering.md)
- [Dear ImGui（ギズモ）](../libs/imgui/imguizmo.md)
- [Jolt Physics（物理演算）](../libs/jolt/index.md)
