# 3D ゲーム

3D ゲームの画面は、<strong>「3D の世界にある物体を、カメラから見た 2D の絵にする」</strong>計算でできています。この計算の中心にあるのが、**座標をいくつもの「空間」に順番に変換していく**流れです。モデルの中の座標 → 世界の座標 → カメラから見た座標 → 画面に映る座標、という具合です。それを行うのが**ベクトルと行列**でその最後の大事な段階が<strong>投影（プロジェクション）</strong>です。このカテゴリでは、3D ゲームを作るために必要な、**数学・カメラ・描画のしくみ・当たり判定**を順に説明します。数式はゲームで使う形に絞り、**なぜそうなるのか**を図とコードで説明します。

!!! tip "ポイント"
    - 3D の描画は、<strong>座標を空間から空間へ変換する流れ</strong>（ローカル → ワールド → ビュー → クリップ → 画面）。
    - 変換は<strong>行列</strong>で表す。<strong>MVP</strong>（モデル・ビュー・プロジェクション）の 3 つの行列を掛ける。
    - まず<strong>座標系の決まり</strong>（左手系か右手系か、Y が上か）と、<strong>行列の規約</strong>（行ベクトルか列ベクトルか）をそろえる。ここがずれるとすべてが狂う。
    - 回転には<strong>クォータニオン</strong>を使う（オイラー角はジンバルロックがある）。
    

## 描画の流れ（座標の旅）

3D ゲームの 1 つの頂点は、画面に出るまでに次の「空間」を順に通ります。

<svg class="fig flow" viewBox="0 0 954 112" role="img" aria-label="頂点が、画面に出るまでの旅"><defs><marker id="fl64292" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">頂点が、画面に出るまでの旅</text><line x1="141.0" y1="64.0" x2="199.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl64292)"/><text x="170.0" y="58.0" text-anchor="middle" style="font-size:12px">ワールド行列</text><line x1="315.0" y1="64.0" x2="373.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl64292)"/><text x="344.0" y="58.0" text-anchor="middle" style="font-size:12px">ビュー行列</text><line x1="475.0" y1="64.0" x2="533.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl64292)"/><text x="504.0" y="58.0" text-anchor="middle" style="font-size:12px">プロジェクション行列</text><line x1="649.0" y1="64.0" x2="707.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl64292)"/><text x="678.0" y="58.0" text-anchor="middle" style="font-size:12px">w で割る</text><line x1="789.0" y1="64.0" x2="847.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl64292)"/><text x="818.0" y="58.0" text-anchor="middle" style="font-size:12px">ビューポート変換</text><rect x="28.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="83.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ローカル空間</text><rect x="202.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="257.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ワールド空間</text><rect x="376.0" y="44.0" width="96" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="424.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ビュー空間</text><rect x="536.0" y="44.0" width="110" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="591.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">クリップ空間</text><rect x="710.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="748.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">NDC</text><rect x="850.0" y="44.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="888.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">画面</text></svg>

| 空間 | 何を原点・基準にするか | どの行列で次へ |
| --- | --- | --- |
| **ローカル**（モデル） | モデル自身の中心 | **ワールド行列**（モデル行列） |
| **ワールド** | ゲームの世界の原点 | **ビュー行列** |
| **ビュー**（カメラ） | カメラの位置（原点）と向き（+Z が前） | **プロジェクション行列** |
| **クリップ** | 見える範囲の箱（視錐台）が、直方体になった空間 | **w で割る**（透視除算） |
| **NDC**（正規化デバイス座標） | x、y が −1〜1（z は 0〜1 か −1〜1） | **ビューポート変換** |
| **スクリーン** | 画面のピクセル（左上が原点が多い） | （GPU がここに描く） |

## ページ一覧

ベクトル・行列・回転・座標系・SimpleMath / DirectXMath は、[ゲーム数学](../gamemath/index.md)のセクションに移しました。このセクションは、それらを使った 3D の仕組みを扱います。

| ページ | 内容 |
| --- | --- |
| [MVP 変換](transforms-mvp.md) | モデル・ワールド・ビュー・プロジェクションの掛け方と使い方 |
| [投影（プロジェクション）](projection.md) | 透視投影と正射投影、視野角、near / far、NDC、深度の非線形 |
| [カメラ](camera.md) | ビュー行列、LookAt、FPS カメラ、軌道カメラ、追従カメラ |
| [深度バッファとカリング](depth-culling.md) | 深度テスト、z-fighting、reverse-Z、視錐台カリング |
| [ピッキングとレイキャスト](picking-raycast.md) | マウスの位置から 3D の世界を指す、レイと交差判定 |
| [法線とライティング](lighting-normals.md) | 法線、拡散反射、鏡面反射、シェーダーでの計算 |
| [PBR（物理ベースレンダリング）](pbr.md) | マイクロファセット、BRDF、金属度と粗さ、IBL。原理から |
| [3D モデルの基礎](model-basics.md) | メッシュ・頂点・三角形・テクスチャ・バッファ。ゼロから |
| [メッシュとテクスチャ](mesh-textures.md) | 頂点、インデックス、UV、ミップマップ、サンプラー |
| [3D の当たり判定](collision-3d.md) | 球、AABB、OBB、カプセル、判定の組み合わせ |
| [スキニング（スケルトンアニメーション）](skinning-animation.md) | ボーン、スキン ウェイト、アニメーションの補間 |

## 数学ライブラリ

3D の数学は、**自作せずにライブラリを使う**のが基本です。

| ライブラリ | 特徴 |
| --- | --- |
| <strong>[DirectXMath](../gamemath/directxmath.md)</strong>（`<DirectXMath.h>`） | Windows の標準（Visual Studio に付属）。**行ベクトル**。左手系（`LH`）と右手系（`RH`）の**両方の関数**がある（**このサイトは `LH`**）。SIMD で速い。型が 2 種類（保存用・計算用）で、書き方が独特 |
| <strong>[SimpleMath](../gamemath/simplemath.md)</strong>（DirectX Tool Kit） | DirectXMath の**ラッパー**。`Vector3`、`Matrix`、`Quaternion` を、演算子とメンバ関数で書ける。型は手系に依存しないが、`Create…` 関数は右手系。**このサイトは型を使い、ビュー・射影は DirectXMath の `LH` 関数** |
| **glm** | OpenGL 風の数学。ヘッダだけ。**列ベクトル**、既定は右手系（このサイトでは使わない） |
| **Eigen** | 線形代数が中心。大きな行列に強い |
| **自作** | 学習用に、`Vec3`、`Mat4` を 1 度は自作すると、理解が深まる |

### このカテゴリの決まり

| 項目 | 決まり |
| --- | --- |
| 描画 API | **DirectX 11**（Direct3D 11）。描画のコードは、DX11 で書く |
| シェーダー | **HLSL**（Shader Model 5） |
| 数学ライブラリ | **SimpleMath**（DirectX Tool Kit）。速さが必要な所だけ DirectXMath |
| 座標系 | **左手系・Y-up**（DirectX の流儀） |
| 前方向 | **+Z**（自前の `kForward` ＝ `(0, 0, 1)`。SimpleMath の `Vector3::Forward` は −Z なので使わない） |
| 行列の規約 | **行ベクトル**（`v * M`）。掛け順は**左から右**（拡大 → 回転 → 平行移動） |
| 三角形の表 | <strong>時計回り（CW）</strong>が表（Direct3D の既定の `FrontCounterClockwise = FALSE`） |
| 角度 | ラジアン |
| 単位 | 1 ＝ 1 メートル |

## 学ぶ順番のおすすめ

1. [DirectXMath](../gamemath/directxmath.md)・[SimpleMath](../gamemath/simplemath.md)：使う道具
2. [座標系](../gamemath/coordinate-systems.md) → [ベクトル](../gamemath/vectors.md) → [行列](../gamemath/matrices.md)：土台
3. [MVP 変換](transforms-mvp.md) → [投影](projection.md) → [カメラ](camera.md)：描画の流れ
   - 描画全体の流れは [描画の流れ（入門）](render-flow/index.md)（図で最初から最後まで追う）
4. [回転とクォータニオン](../gamemath/rotation.md)：向きの扱い
5. 必要に応じて：[深度とカリング](depth-culling.md)、[ピッキング](picking-raycast.md)、[ライティング](lighting-normals.md)、[当たり判定](collision-3d.md)、[スキニング](skinning-animation.md)

## 関連ページ

- [SIMD（ベクトル化）](../optimize/simd.md)
- [描画の最適化](../rendering/index.md)
- [Dear ImGui（ギズモ）](../libs/imgui/imguizmo.md)
- [Jolt Physics（物理演算）](../libs/jolt/index.md)
