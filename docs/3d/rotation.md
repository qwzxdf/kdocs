---
title: 回転とクォータニオン
tags:
  - 3Dゲーム
---

# 回転とクォータニオン

3D の**回転**の表し方は、いくつかあります。一番分かりやすいのは、**オイラー角**（X 軸まわりに何度、Y 軸まわりに何度、Z 軸まわりに何度）ですが、**ジンバルロック**という欠点があり、**回転の補間（滑らかな途中経過）が、うまくいきません**。そこで、ゲームでは、**クォータニオン**（四元数）で回転を持つのが、標準です。クォータニオンは、`x, y, z, w` の 4 つの数字で、**ジンバルロックがなく、補間も滑らか**で、行列より小さく、合成も速いです。仕組み（四元数の数学）は難しいですが、**使い方は、簡単**です。このページは、オイラー角の問題、クォータニオンの使い方、補間（Slerp）、よくある操作をまとめます。

!!! tip "ポイント"
    - <strong>ゲーム内の回転は、クォータニオンで持つ</strong>（`Quaternion`）。<strong>オイラー角は、入力・表示・エディターだけ</strong>。
    - <strong>オイラー角</strong>は、<strong>ジンバルロック</strong>（2 つの軸が重なって、自由度が 1 つ失われる）と、<strong>補間が不自然</strong>という欠点がある。
    - クォータニオンは<strong>「軸と角度」</strong>から作る（`CreateFromAxisAngle`）。<strong>ベクトルを回す</strong>のは `Vector3::Transform(v, q)`。
    - <strong>回転の合成は、掛け算</strong>（`q1 * q2`）。<strong>順番</strong>がある（行ベクトル規約：先に q1、次に q2）。
    - <strong>補間は `Slerp`</strong>（球面線形補間）。アニメーション、カメラ、振り向きに使う。
    - <strong>ときどき正規化</strong>する（掛け算を重ねると、長さが 1 からずれる）。

## 回転の表し方

| 表し方 | 数字の数 | 長所 | 短所 |
| --- | --- | --- | --- |
| **オイラー角**（yaw, pitch, roll） | 3 | 直感的。入力・エディターで使いやすい | **ジンバルロック**。補間が不自然。軸の順序で結果が変わる |
| **回転行列** | 9（3×3）または 16（4×4） | 頂点の変換に直接使える。GPU に渡せる | 大きい。補間できない。累積で歪む |
| **軸と角度** | 4（軸 3 + 角度 1） | 分かりやすい | 合成・補間が面倒 |
| **クォータニオン** | **4** | **ジンバルロックなし。補間が滑らか。小さい。合成が速い** | 数字を見ても、意味が分からない |

## オイラー角の問題

### ジンバルロック

**オイラー角で、3 つの回転を順に行うと、特定の姿勢で、2 つの軸が重なって、自由度が 1 つ失われます**。たとえば、「Y → X → Z」の順で、X 軸（pitch）を ±90° にすると、Y 軸（yaw）と Z 軸（roll）の回転が、**同じ軸まわりの回転**になってしまいます。

| 場面 | 症状 |
| --- | --- |
| 飛行機が、真上を向いたとき | 左右に回しても、横に傾くだけ。思った方向に回れない |
| カメラが、真上を見たとき | 画面が、急にぐるっと回る |
| アニメーションの補間 | 回転の途中経過が、変な方向にねじれる |

### 補間が不自然

オイラー角 `(0, 0, 0)` から `(180, 0, 180)` へ、各成分を線形補間すると、**意図しない経路**を通ります。軸ごとに補間するので、最短の回転にならないのです。

### 順序の問題

オイラー角は、**回す軸の順序**（Y → X → Z など）で、結果が変わります。エンジンごとに、順序が違うので、**どれを使っているか**を、必ず確認します。

オイラー角は、**FPS カメラの yaw・pitch のように、軸を制限して使う**（roll を使わない）ときだけ、安全です（[カメラ](camera.md)）。

## クォータニオン

**クォータニオン**は、`(x, y, z, w)` の 4 つの数字で、<strong>「ある軸のまわりに、ある角度だけ回す」</strong>を表します。

```text
軸 n（長さ 1）のまわりに、角度 θ だけ回すクォータニオン：

q = ( n.x * sin(θ/2),  n.y * sin(θ/2),  n.z * sin(θ/2),  cos(θ/2) )
      ───────────  xyz（軸の成分）  ───────────────       w（角度の成分）
```

<strong>数字の中身を、直接触る必要はありません。</strong>軸と角度で作り、関数で操作します。

### 作る

```cpp
#include <SimpleMath.h>
using namespace DirectX::SimpleMath;

// 軸と角度（ラジアン）から
Quaternion q1 = Quaternion::CreateFromAxisAngle(Vector3::UnitY, DirectX::XMConvertToRadians(90.0f));

// オイラー角（ラジアン）から。入力・エディターの値を、クォータニオンにするとき
Quaternion q2 = Quaternion::CreateFromYawPitchRoll(yaw, pitch, roll);

// 回転行列から
Quaternion q3 = Quaternion::CreateFromRotationMatrix(rotation_matrix);

// 「回転なし」
Quaternion none = Quaternion::Identity;
```

### 使う

```cpp
// ベクトルを回す
Vector3 rotated = Vector3::Transform(Vector3::Forward, q1);

// 行列にする（ワールド行列の回転の部分）
Matrix r = Matrix::CreateFromQuaternion(q1);
Matrix world = Matrix::CreateScale(scale) * Matrix::CreateFromQuaternion(q1) * Matrix::CreateTranslation(pos);

// 回転後の「前」「右」「上」の向き
Vector3 forward = Vector3::Transform(Vector3::Forward, q1);
Vector3 right = Vector3::Transform(Vector3::Right, q1);
```

## 回転の合成

**回転を重ねる**には、クォータニオンを**掛け算**します。**順序**があります。

```cpp
// 行ベクトル規約：q1 の回転をしたあとに、q2 の回転をする
Quaternion combined = q1 * q2;
```

| 書き方 | 意味 |
| --- | --- |
| `q1 * q2`（SimpleMath、行ベクトル） | **先に q1、次に q2**（行列の `R1 * R2` と同じ順） |
| 数学の教科書（列ベクトル） | `q2 * q1` と書く（逆の順に見える） |

### 現在の向きに、さらに回す

```cpp
// 現在の回転 current に、「Y 軸まわりに delta 度」の回転を、さらに加える（ワールド軸まわり）
Quaternion delta = Quaternion::CreateFromAxisAngle(Vector3::UnitY, delta_angle);
current = current * delta;     // 先に今の回転、次にワールドの Y 軸まわり（行ベクトル規約）
current.Normalize();           // 誤差を直す
```

| どの軸まわりか | 掛け方（行ベクトル規約） |
| --- | --- |
| **ワールド軸**まわりに、さらに回す | `current * delta` |
| **物体自身の軸**（ローカル軸）まわりに、さらに回す | `delta * current` |

どちらが、意図した動きかを、小さなテスト（物体が、どう回るか）で確かめます。

### 逆回転と、差

```cpp
Quaternion inverse = q.Inverse();                       // 逆回転（元に戻す）
Quaternion difference = from.Inverse() * to;             // from から to へ行く回転
```

## 補間（Slerp）

**2 つの回転の途中**を求めるのが、<strong>球面線形補間（Slerp：スラープ）</strong>です。**一定の速さで、最短の経路**で、回転が変わります。

```cpp
Quaternion mid = Quaternion::Slerp(from, to, 0.5f);     // 半分のところ
```

| 補間 | 特徴 | 使いどころ |
| --- | --- | --- |
| **`Slerp`** | **一定の角速度**。最短の経路。少し重い（`sin`、`acos`） | アニメーション、カメラ、**きれいな補間が必要なとき** |
| **`Lerp`**（+ 正規化） | **速い**。角速度は一定でない（途中が速い）。角度が小さければ、ほぼ同じ | 毎フレームの小さな補間（追従、振り向き） |
| オイラー角の補間 | **不自然**（ジンバルロックの影響） | 使わない |

```cpp
// 振り向き：現在の向きを、目標の向きに、少しずつ近づける（フレームレート非依存）
float t = 1.0f - std::exp(-turn_speed * dt);
current = Quaternion::Slerp(current, target, t);
```

### 最短経路

クォータニオンは、**`q` と `−q` が、同じ回転**を表します。補間で、**遠回りになる**ことがあります。`Slerp` は、内積が負のとき、片方を反転して、**最短の経路**を通ります（SimpleMath の `Slerp` は、処理してくれます）。自作する場合は、注意が必要です。

## ある方向を向く回転

**ある方向（ターゲット）を向く回転**を作りたい場面は、非常に多いです（敵が、プレイヤーを向く、砲台が狙う）。

```cpp
// 「ある前方向を向く」回転を、行列から作る
Quaternion LookRotation(const Vector3& forward, const Vector3& up) {
  // CreateWorld は、位置と向きから、ワールド行列を作る（前は -Z）
  Matrix m = Matrix::CreateWorld(Vector3::Zero, forward, up);
  return Quaternion::CreateFromRotationMatrix(m);
}

// 敵がプレイヤーを向く（Y 軸まわりのみ、地面に水平な向き）
Vector3 to_player = player.position - enemy.position;
to_player.y = 0.0f;
if (to_player.LengthSquared() > 0.0001f) {
  to_player.Normalize();
  Quaternion target = LookRotation(to_player, Vector3::Up);
  enemy.rotation = Quaternion::Slerp(enemy.rotation, target, t);   // 滑らかに向く
}
```

### 2 つのベクトルの間の回転

「ベクトル `a` を、ベクトル `b` に重ねる回転」を求めます。

```cpp
Quaternion RotationBetween(Vector3 a, Vector3 b) {
  a.Normalize();
  b.Normalize();
  float dot = a.Dot(b);
  if (dot > 0.9999f) {
    return Quaternion::Identity;                      // ほぼ同じ向き
  }
  if (dot < -0.9999f) {                                // ほぼ逆向き：回転軸が決まらないので、任意の垂直な軸
    Vector3 axis = Vector3::UnitX.Cross(a);
    if (axis.LengthSquared() < 0.0001f) axis = Vector3::UnitY.Cross(a);
    axis.Normalize();
    return Quaternion::CreateFromAxisAngle(axis, DirectX::XM_PI);
  }
  Vector3 axis = a.Cross(b);
  Quaternion q(axis.x, axis.y, axis.z, 1.0f + dot);    // 半角の公式を使った、簡易な作り方
  q.Normalize();
  return q;
}
```

## クォータニオンの注意

| 注意 | 説明 |
| --- | --- |
| **正規化する** | 掛け算を重ねると、長さが 1 からずれる。**ときどき `Normalize()`**。長さが 1 でないと、回転が歪む |
| **`q` と `−q` は同じ回転** | 比較するなら、内積の**絶対値**で近さを見る（`abs(q1.Dot(q2))`） |
| **角度を直接取り出さない** | 角度が欲しい（UI 表示）ときだけ、`ToEuler()` で、オイラー角に変換する |
| **`ToEuler()` は、ジンバルロックの近くで不安定** | 表示用に限る。値を保存や補間に使わない |
| **保存** | クォータニオン（4 つの `float`）のまま保存。オイラー角に変換して保存しない（情報が失われる） |
| **座標系の変換** | 左手系 ⇔ 右手系で、符号の反転が必要（[座標系](coordinate-systems.md)） |

## ゲームでの使いどころ

| 場面 | 回転の扱い |
| --- | --- |
| オブジェクトの向き | `Quaternion` で持つ。ワールド行列を作るときに、行列に |
| FPS カメラ | yaw・pitch の角度で持つ（roll なし）。ビュー行列は、そこから作る |
| 敵が、プレイヤーの方を向く | `LookRotation` + `Slerp` で、滑らかに |
| アニメーション（ボーンの回転） | キーフレームの間を `Slerp`（[スキニング](skinning-animation.md)） |
| エディターの回転入力 | オイラー角（度）で入力・表示。内部でクォータニオンに変換 |
| ギズモ（ImGuizmo） | 行列で受け渡し。`Decompose` で、クォータニオンに戻す（[ImGuizmo](../libs/imgui/imguizmo.md)） |
| 物理エンジン | クォータニオンで受け渡し（[Jolt](../libs/jolt/index.md)） |
| 重力の方向に合わせる（惑星） | `RotationBetween(今の上, 重力の逆方向)` |

## よくあるミス

??? failure "オイラー角を、そのまま補間する"
    ジンバルロックと、遠回りの原因です。クォータニオンに変換して、`Slerp` します。

??? failure "角度を度のまま渡す"
    `CreateFromAxisAngle` は、ラジアンです。`XMConvertToRadians` で変換します。

??? failure "掛け順を逆にして、回転が逆の順になる"
    `q1 * q2` は「先に q1、次に q2」（行ベクトル規約）です。意図と逆なら、`q2 * q1` にします。ワールド軸まわりか、ローカル軸まわりかも、確認します。

??? failure "正規化せず、回転が歪む"
    毎フレーム掛け算を重ねると、長さが 1 からずれます。`Normalize()` を、ときどき呼びます。

??? failure "ほぼ逆向きの 2 つのベクトルの間の回転で、NaN になる"
    外積が 0 になり、回転軸が決まりません。上のように、特別に扱います。

??? failure "`ToEuler()` の結果を保存して、補間に使う"
    ジンバルロックの近くで、不安定です。クォータニオンのまま持ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 回転は<strong>クォータニオン</strong>で持つ。<strong>オイラー角は、入力・表示だけ</strong>（ジンバルロック・補間の問題）
    - [x] 作るのは<strong>`CreateFromAxisAngle`</strong>（軸と角度・ラジアン）。<strong>ベクトルを回す</strong>のは `Vector3::Transform(v, q)`
    - [x] 合成は<strong>`q1 * q2`</strong>（行ベクトル規約：先に q1）。<strong>ときどき正規化</strong>
    - [x] 補間は<strong>`Slerp`</strong>（毎フレームの小さな追従は `Lerp` + 正規化でもよい）
    - [x] 「ある方向を向く」は <strong>`LookRotation` + `Slerp`</strong>

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [行列](matrices.md)
- [カメラ](camera.md)
- [スキニング](skinning-animation.md)
- [SimpleMath](simplemath.md)
