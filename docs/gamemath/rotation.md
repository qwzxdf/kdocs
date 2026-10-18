---
title: 回転とクォータニオン
tags:
  - 3Dゲーム
---

# 回転とクォータニオン

3D の**回転**の表し方は、いくつかあります。一番分かりやすいのは、**オイラー角**（X 軸まわりに何度、Y 軸まわりに何度、Z 軸まわりに何度）ですが**ジンバルロック**という欠点があり、**回転の補間（滑らかな途中経過）が、うまくいきません**。そこでゲームでは**クォータニオン**（四元数）で回転を持つのが標準です。クォータニオンは、`x, y, z, w` の 4 つの数字で、**ジンバルロックがなく、補間も滑らか**で行列より小さく、合成も速いです。仕組み（四元数の数学）は難しいですが**使い方は簡単**です。このページはオイラー角の問題、クォータニオンの使い方、補間（Slerp）、よくある操作をまとめます。

!!! tip "ポイント"
    - <strong>ゲーム内の回転は、クォータニオンで持つ</strong>（`Quaternion`）。<strong>オイラー角は入力・表示・エディターだけ</strong>。
    - <strong>オイラー角</strong>は、<strong>ジンバルロック</strong>（2 つの軸が重なって、自由度が 1 つ失われる）と、<strong>補間が不自然</strong>という欠点がある。
    - クォータニオンは<strong>「軸と角度」</strong>から作る（`CreateFromAxisAngle`）。<strong>ベクトルを回す</strong>のは `Vector3::Transform(v, q)`。
    - <strong>回転の合成は、掛け算</strong>（`q1 * q2`）。<strong>順番</strong>がある（行ベクトル規約：先に q1、次に q2）。
    - <strong>補間は `Slerp`</strong>（球面線形補間）。アニメーション、カメラ、振り向きに使う。
    - <strong>ときどき正規化</strong>する（掛け算を重ねると長さが 1 からずれる）。

## 回転の表し方

| 表し方 | 数字の数 | 長所 | 短所 |
| --- | --- | --- | --- |
| **オイラー角**（yaw, pitch, roll） | 3 | 直感的。入力・エディターで使いやすい | **ジンバルロック**。補間が不自然。軸の順序で結果が変わる |
| **回転行列** | 9（3×3）または 16（4×4） | 頂点の変換に直接使える。GPU に渡せる | 大きい。補間できない。累積で歪む |
| **軸と角度** | 4（軸 3 + 角度 1） | 分かりやすい | 合成・補間が面倒 |
| **クォータニオン** | **4** | **ジンバルロックなし。補間が滑らか。小さい。合成が速い** | 数字を見ても意味が分からない |

## オイラー角の問題 {#euler}

<svg class="fig" viewBox="0 0 650 230" role="img" aria-label="ジンバルロック"><defs><marker id="g1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">ふつうの姿勢：3 つの軸が、独立に回せる</text><line x1="120" y1="130" x2="120" y2="50" stroke="currentColor" stroke-width="2" marker-end="url(#g1)" /><text x="126" y="56">Y（yaw）</text><line x1="120" y1="130" x2="200" y2="130" stroke="currentColor" stroke-width="2" marker-end="url(#g1)" /><text x="204" y="134">X（pitch）</text><line x1="120" y1="130" x2="70" y2="175" stroke="currentColor" stroke-width="2" marker-end="url(#g1)" /><text x="30" y="190">Z（roll）</text><text x="20" y="215">どの軸まわりにも、自由に回せる</text><text x="330" y="20" class="fig-title">pitch を 90°にすると</text><line x1="430" y1="160" x2="430" y2="60" stroke="currentColor" stroke-width="2" marker-end="url(#g1)" /><text x="436" y="66">yaw の軸</text><line x1="430" y1="160" x2="430" y2="90" stroke="currentColor" stroke-width="2" marker-end="url(#g1)" stroke-dasharray="4 3"/><text x="436" y="120">roll の軸（同じ向き）</text><text x="330" y="190">2 つの軸が重なり、回せる自由度が 1 つ消える</text><text x="330" y="212">→ ジンバルロック（クォータニオンなら起きない）</text></svg>

### ジンバルロック

**オイラー角で、3 つの回転を順に行うと、特定の姿勢で、2 つの軸が重なって、自由度が 1 つ失われます**。たとえば、「Y → X → Z」の順で、X 軸（pitch）を ±90° にすると、Y 軸（yaw）と Z 軸（roll）の回転が**同じ軸まわりの回転**になってしまいます。

| 場面 | 症状 |
| --- | --- |
| 飛行機が真上を向いたとき | 左右に回しても横に傾くだけ。思った方向に回れない |
| カメラが真上を見たとき | 画面が急にぐるっと回る |
| アニメーションの補間 | 回転の途中経過が変な方向にねじれる |

### 補間が不自然

オイラー角 `(0, 0, 0)` から `(180, 0, 180)` へ、各成分を線形補間すると、**意図しない経路**を通ります。軸ごとに補間するので最短の回転にならないのです。

### 順序の問題

オイラー角は**回す軸の順序**（Y → X → Z など）で、結果が変わります。エンジンごとに順序が違うので**どれを使っているか**を必ず確認します。

オイラー角は、**FPS カメラの yaw・pitch のように軸を制限して使う**（roll を使わない）ときだけ、安全です（[カメラ](../3d/camera.md)）。

## クォータニオン {#quaternion}

<svg class="fig" viewBox="0 0 679 220" role="img" aria-label="軸と角度による回転"><defs><marker id="a1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">回転 ＝「軸」と「角度」</text><line x1="150" y1="190" x2="150" y2="40" stroke="currentColor" stroke-width="3" marker-end="url(#a1)" /><text x="158" y="50">軸 n（長さ 1）</text><ellipse cx="150" cy="130" rx="85" ry="26" fill="none" stroke="currentColor" stroke-dasharray="4 4"/><circle cx="235" cy="130" r="6" fill="currentColor"/><text x="240" y="120">回す前</text><circle cx="190" cy="153" r="6" fill="currentColor"/><text x="125" y="175">回した後</text><path d="M 232 136 A 85 26 0 0 1 196 155" fill="none" stroke="currentColor" marker-end="url(#a1)"/><text x="215" y="160">θ</text><text x="340" y="90">クォータニオン q ＝ ( n × sin(θ/2) , cos(θ/2) )</text><text x="340" y="120">軸 n のまわりに、角度 θ だけ回す</text><text x="340" y="150">4 つの数字で、向きを表す</text></svg>

**クォータニオン**は、`(x, y, z, w)` の 4 つの数字で<strong>「ある軸のまわりにある角度だけ回す」</strong>を表します。

軸 n（長さ 1）のまわりに角度 θ だけ回すクォータニオンは、次の形です。

<div class="formula">q ＝ ( n.x · sin(θ/2) ,　n.y · sin(θ/2) ,　n.z · sin(θ/2) ,　cos(θ/2) )</div>

| 部分 | 意味 |
| --- | --- |
| 軸 n（長さ 1） | 回転の軸 |
| θ | 回す角度 |
| **x, y, z** | 軸の成分に `sin(θ/2)` を掛けたもの |
| **w** | 角度の成分 `cos(θ/2)` |

<strong>数字の中身を直接触る必要はありません。</strong>軸と角度で作り、関数で操作します。

### 作る {#create}

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
Vector3 rotated = Vector3::Transform(kForward, q1);

// 行列にする（ワールド行列の回転の部分）
Matrix r = Matrix::CreateFromQuaternion(q1);
Matrix world = Matrix::CreateScale(scale) * Matrix::CreateFromQuaternion(q1) * Matrix::CreateTranslation(pos);

// 回転後の「前」「右」「上」の向き
Vector3 forward = Vector3::Transform(kForward, q1);
Vector3 right = Vector3::Transform(Vector3::Right, q1);
```

## 回転の合成 {#compose}

**回転を重ねる**には、クォータニオンを**掛け算**します。**順序**があります。

```cpp
// 行ベクトル規約：q1 の回転をしたあとに、q2 の回転をする
Quaternion combined = q1 * q2;
```

| 書き方 | 意味 |
| --- | --- |
| `q1 * q2`（SimpleMath、行ベクトル） | **先に q1、次に q2**（行列の `R1 * R2` と同じ順） |
| 数学の教科書（列ベクトル） | `q2 * q1` と書く（逆の順に見える） |

### 現在の向きにさらに回す

```cpp
// 現在の回転 current に、「Y 軸まわりに delta 度」の回転を、さらに加える（ワールド軸まわり）
Quaternion delta = Quaternion::CreateFromAxisAngle(Vector3::UnitY, delta_angle);
current = current * delta;     // 先に今の回転、次にワールドの Y 軸まわり（行ベクトル規約）
current.Normalize();           // 誤差を直す
```

| どの軸まわりか | 掛け方（行ベクトル規約） |
| --- | --- |
| **ワールド軸**まわりにさらに回す | `current * delta` |
| **物体自身の軸**（ローカル軸）まわりにさらに回す | `delta * current` |

どちらが意図した動きかを小さなテスト（物体がどう回るか）で確かめます。

### 逆回転と差 {#inverse}

```cpp
Quaternion inverse = q.Inverse();                       // 逆回転（元に戻す）
Quaternion difference = from.Inverse() * to;             // from から to へ行く回転
```

## 補間（Slerp） {#slerp}

<svg class="fig" viewBox="0 0 640 240" role="img" aria-label="Slerp と Lerp"><defs><marker id="s1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs><text x="20" y="20" class="fig-title">Slerp：円弧に沿って、一定の速さで</text><path d="M 40 190 A 150 150 0 0 1 220 60" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="40" cy="190" r="5" fill="currentColor"/><circle cx="73" cy="130" r="5" fill="currentColor"/><circle cx="130" cy="83" r="5" fill="currentColor"/><circle cx="220" cy="60" r="5" fill="currentColor"/><text x="25" y="212">from</text><text x="215" y="50">to</text><text x="30" y="232">等間隔に動く（回転の速さが一定）</text><text x="330" y="20" class="fig-title">Lerp：弦に沿って（正規化が必要）</text><path d="M 350 190 A 150 150 0 0 1 530 60" fill="none" stroke="currentColor" stroke-dasharray="4 4"/><line x1="350" y1="190" x2="530" y2="60" stroke="currentColor" stroke-width="2"/><circle cx="350" cy="190" r="5" fill="currentColor"/><circle cx="409" cy="148" r="5" fill="currentColor"/><circle cx="468" cy="105" r="5" fill="currentColor"/><circle cx="530" cy="60" r="5" fill="currentColor"/><text x="335" y="212">from</text><text x="525" y="50">to</text><text x="340" y="232">等間隔だが、正規化すると、速さが不均一になる</text></svg>

**2 つの回転の途中**を求めるのが、<strong>球面線形補間（Slerp：スラープ）</strong>です。**一定の速さで最短の経路**で回転が変わります。

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

クォータニオンは、**`q` と `−q` が同じ回転**を表します。補間で**遠回りになる**ことがあります。`Slerp` は、内積が負のとき、片方を反転して、**最短の経路**を通ります（SimpleMath の `Slerp` は、処理してくれます）。自作する場合は、注意が必要です。

## ある方向を向く回転 {#look-rotation}

**ある方向（ターゲット）を向く回転**を作りたい場面は、非常に多いです（敵がプレイヤーを向く、砲台が狙う）。

```cpp
// 「ある前方向を向く」回転を、行列から作る
Quaternion LookRotation(const Vector3& forward, const Vector3& up) {
  Matrix m = MakeWorld(Vector3::Zero, forward, up);
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

「ベクトル `a` をベクトル `b` に重ねる回転」を求めます。

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
| **正規化する** | 掛け算を重ねると長さが 1 からずれる。**ときどき `Normalize()`**。長さが 1 でないと回転が歪む |
| **`q` と `−q` は同じ回転** | 比較するなら、内積の**絶対値**で近さを見る（`abs(q1.Dot(q2))`） |
| **角度を直接取り出さない** | 角度が欲しい（UI 表示）ときだけ、`ToEuler()` で、オイラー角に変換する |
| **`ToEuler()` は、ジンバルロックの近くで不安定** | 表示用に限る。値を保存や補間に使わない |
| **保存** | クォータニオン（4 つの `float`）のまま保存。オイラー角に変換して保存しない（情報が失われる） |
| **座標系の変換** | 左手系 ⇔ 右手系で符号の反転が必要（[座標系](coordinate-systems.md)） |

## ゲームでの使いどころ

| 場面 | 回転の扱い |
| --- | --- |
| オブジェクトの向き | `Quaternion` で持つ。ワールド行列を作るときに、行列に |
| FPS カメラ | yaw・pitch の角度で持つ（roll なし）。ビュー行列はそこから作る |
| 敵がプレイヤーの方を向く | `LookRotation` + `Slerp` で、滑らかに |
| アニメーション（ボーンの回転） | キーフレームの間を `Slerp`（[スキニング](../3d/skinning-animation.md)） |
| エディターの回転入力 | オイラー角（度）で入力・表示。内部でクォータニオンに変換 |
| ギズモ（ImGuizmo） | 行列で受け渡し。`Decompose` で、クォータニオンに戻す（[ImGuizmo](../libs/imgui/imguizmo.md)） |
| 物理エンジン | クォータニオンで受け渡し（[Jolt](../libs/jolt/index.md)） |
| 重力の方向に合わせる（惑星） | `RotationBetween(今の上, 重力の逆方向)` |

<!-- fig:nlerp-vs-slerp:begin -->

<svg class="fig illust motion" data-fig="nlerp-vs-slerp" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-nlerp-vs-slerp" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">2 つの向きの間を補間: lerp は途中が速く、slerp は一定の速さ（150 度離れた場合）</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">回った角度 (度)</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">補間の t</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="230.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.25</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.5</text>
<text x="550.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.75</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<path d="M70.0,310.0 L80.67,306.0 L91.33,302.0 L102.0,298.0 L112.67,294.0 L123.33,290.0 L134.0,286.0 L144.67,282.0 L155.33,278.0 L166.0,274.0 L176.67,270.0 L187.33,266.0 L198.0,262.0 L208.67,258.0 L219.33,254.0 L230.0,250.0 L240.67,246.0 L251.33,242.0 L262.0,238.0 L272.67,234.0 L283.33,230.0 L294.0,226.0 L304.67,222.0 L315.33,218.0 L326.0,214.0 L336.67,210.0 L347.33,206.0 L358.0,202.0 L368.67,198.0 L379.33,194.0 L390.0,190.0 L400.67,186.0 L411.33,182.0 L422.0,178.0 L432.67,174.0 L443.33,170.0 L454.0,166.0 L464.67,162.0 L475.33,158.0 L486.0,154.0 L496.67,150.0 L507.33,146.0 L518.0,142.0 L528.67,138.0 L539.33,134.0 L550.0,130.0 L560.67,126.0 L571.33,122.0 L582.0,118.0 L592.67,114.0 L603.33,110.0 L614.0,106.0 L624.67,102.0 L635.33,98.0 L646.0,94.0 L656.67,90.0 L667.33,86.0 L678.0,82.0 L688.67,78.0 L699.33,74.0 L710.0,70.0" fill="none" stroke="#2ea043" stroke-width="4" opacity="1"/>
<path d="M70.0,310.0 L76.4,309.53 L82.8,309.05 L89.2,308.54 L95.6,308.02 L102.0,307.47 L108.4,306.9 L114.8,306.31 L121.2,305.69 L127.6,305.05 L134.0,304.37 L140.4,303.67 L146.8,302.93 L153.2,302.15 L159.6,301.34 L166.0,300.49 L172.4,299.59 L178.8,298.65 L185.2,297.65 L191.6,296.6 L198.0,295.5 L204.4,294.33 L210.8,293.09 L217.2,291.77 L223.6,290.38 L230.0,288.9 L236.4,287.33 L242.8,285.65 L249.2,283.86 L255.6,281.94 L262.0,279.89 L268.4,277.7 L274.8,275.34 L281.2,272.81 L287.6,270.09 L294.0,267.17 L300.4,264.02 L306.8,260.62 L313.2,256.96 L319.6,253.02 L326.0,248.78 L332.4,244.23 L338.8,239.35 L345.2,234.14 L351.6,228.6 L358.0,222.75 L364.4,216.6 L370.8,210.19 L377.2,203.58 L383.6,196.83 L390.0,190.0 L396.4,183.17 L402.8,176.42 L409.2,169.81 L415.6,163.4 L422.0,157.25 L428.4,151.4 L434.8,145.86 L441.2,140.65 L447.6,135.77 L454.0,131.22 L460.4,126.98 L466.8,123.04 L473.2,119.38 L479.6,115.98 L486.0,112.83 L492.4,109.91 L498.8,107.19 L505.2,104.66 L511.6,102.3 L518.0,100.11 L524.4,98.06 L530.8,96.14 L537.2,94.35 L543.6,92.67 L550.0,91.1 L556.4,89.62 L562.8,88.23 L569.2,86.91 L575.6,85.67 L582.0,84.5 L588.4,83.4 L594.8,82.35 L601.2,81.35 L607.6,80.41 L614.0,79.51 L620.4,78.66 L626.8,77.85 L633.2,77.07 L639.6,76.33 L646.0,75.63 L652.4,74.95 L658.8,74.31 L665.2,73.69 L671.6,73.1 L678.0,72.53 L684.4,71.98 L690.8,71.46 L697.2,70.95 L703.6,70.47 L710.0,70.0" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<text x="569.2" y="144.8" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">slerp（一定）</text>
<text x="102.0" y="283.47" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">lerp + 正規化</text>
<circle cx="70.0" cy="310.0" r="7" fill="#2ea043"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0944;0.1088;0.1232;0.1376;0.1520;0.1664;0.1808;0.1952;0.2096;0.2240;0.2384;0.2528;0.2672;0.2816;0.2960;0.3104;0.3248;0.3392;0.3536;0.3680;0.3824;0.3968;0.4112;0.4256;0.4400;0.4544;0.4688;0.4832;0.4976;0.5120;0.5264;0.5408;0.5552;0.5696;0.5840;0.5984;0.6128;0.6272;0.6416;0.6560;0.6704;0.6848;0.6992;0.7136;0.7280;0.7424;0.7568;0.7712;0.7856;0.8000;1.0000" values="70;70;82.8;95.6;108.4;121.2;134;146.8;159.6;172.4;185.2;198;210.8;223.6;236.4;249.2;262;274.8;287.6;300.4;313.2;326;338.8;351.6;364.4;377.2;390;402.8;415.6;428.4;441.2;454;466.8;479.6;492.4;505.2;518;530.8;543.6;556.4;569.2;582;594.8;607.6;620.4;633.2;646;658.8;671.6;684.4;697.2;710;710"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0944;0.1088;0.1232;0.1376;0.1520;0.1664;0.1808;0.1952;0.2096;0.2240;0.2384;0.2528;0.2672;0.2816;0.2960;0.3104;0.3248;0.3392;0.3536;0.3680;0.3824;0.3968;0.4112;0.4256;0.4400;0.4544;0.4688;0.4832;0.4976;0.5120;0.5264;0.5408;0.5552;0.5696;0.5840;0.5984;0.6128;0.6272;0.6416;0.6560;0.6704;0.6848;0.6992;0.7136;0.7280;0.7424;0.7568;0.7712;0.7856;0.8000;1.0000" values="310;310;305.2;300.4;295.6;290.8;286;281.2;276.4;271.6;266.8;262;257.2;252.4;247.6;242.8;238;233.2;228.4;223.6;218.8;214;209.2;204.4;199.6;194.8;190;185.2;180.4;175.6;170.8;166;161.2;156.4;151.6;146.8;142;137.2;132.4;127.6;122.8;118;113.2;108.4;103.6;98.8;94;89.2;84.4;79.6;74.8;70;70"/></circle>
<circle cx="70.0" cy="310.0" r="7" fill="#e5484d"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0944;0.1088;0.1232;0.1376;0.1520;0.1664;0.1808;0.1952;0.2096;0.2240;0.2384;0.2528;0.2672;0.2816;0.2960;0.3104;0.3248;0.3392;0.3536;0.3680;0.3824;0.3968;0.4112;0.4256;0.4400;0.4544;0.4688;0.4832;0.4976;0.5120;0.5264;0.5408;0.5552;0.5696;0.5840;0.5984;0.6128;0.6272;0.6416;0.6560;0.6704;0.6848;0.6992;0.7136;0.7280;0.7424;0.7568;0.7712;0.7856;0.8000;1.0000" values="70;70;82.8;95.6;108.4;121.2;134;146.8;159.6;172.4;185.2;198;210.8;223.6;236.4;249.2;262;274.8;287.6;300.4;313.2;326;338.8;351.6;364.4;377.2;390;402.8;415.6;428.4;441.2;454;466.8;479.6;492.4;505.2;518;530.8;543.6;556.4;569.2;582;594.8;607.6;620.4;633.2;646;658.8;671.6;684.4;697.2;710;710"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0944;0.1088;0.1232;0.1376;0.1520;0.1664;0.1808;0.1952;0.2096;0.2240;0.2384;0.2528;0.2672;0.2816;0.2960;0.3104;0.3248;0.3392;0.3536;0.3680;0.3824;0.3968;0.4112;0.4256;0.4400;0.4544;0.4688;0.4832;0.4976;0.5120;0.5264;0.5408;0.5552;0.5696;0.5840;0.5984;0.6128;0.6272;0.6416;0.6560;0.6704;0.6848;0.6992;0.7136;0.7280;0.7424;0.7568;0.7712;0.7856;0.8000;1.0000" values="310;310;309.05;308.02;306.9;305.69;304.37;302.93;301.34;299.59;297.65;295.5;293.09;290.38;287.33;283.86;279.89;275.34;270.09;264.02;256.96;248.78;239.35;228.6;216.6;203.58;190;176.42;163.4;151.4;140.65;131.22;123.04;115.98;109.91;104.66;100.11;96.14;92.67;89.62;86.91;84.5;82.35;80.41;78.66;77.07;75.63;74.31;73.1;71.98;70.95;70;70"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">t が小さいうち: lerp は slerp より遅れる(0.1 で 約 4 度)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3197;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">t = 0.5 付近: lerp が急に回る(中央付近が速い)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.5597;0.5600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">t = 1: 両方とも 150 度。経路は同じで、速さだけ違う<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5597;0.5600;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:nlerp-vs-slerp:end -->

## よくあるミス

??? failure "オイラー角を、そのまま補間する"
    ジンバルロックと遠回りの原因です。クォータニオンに変換して、`Slerp` します。

??? failure "角度を度のまま渡す"
    `CreateFromAxisAngle` は、ラジアンです。`XMConvertToRadians` で変換します。

??? failure "掛け順を逆にして、回転が逆の順になる"
    `q1 * q2` は「先に q1、次に q2」（行ベクトル規約）です。意図と逆なら、`q2 * q1` にします。ワールド軸まわりか、ローカル軸まわりかも確認します。

??? failure "正規化せず、回転が歪む"
    毎フレーム掛け算を重ねると、長さが 1 からずれます。`Normalize()` を、ときどき呼びます。

??? failure "ほぼ逆向きの 2 つのベクトルの間の回転で、NaN になる"
    外積が 0 になり、回転軸が決まりません。上のように特別に扱います。

??? failure "`ToEuler()` の結果を保存して、補間に使う"
    ジンバルロックの近くで、不安定です。クォータニオンのまま持ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 回転は<strong>クォータニオン</strong>で持つ。<strong>オイラー角は入力・表示だけ</strong>（ジンバルロック・補間の問題）
    - [x] 作るのは<strong>`CreateFromAxisAngle`</strong>（軸と角度・ラジアン）。<strong>ベクトルを回す</strong>のは `Vector3::Transform(v, q)`
    - [x] 合成は<strong>`q1 * q2`</strong>（行ベクトル規約：先に q1）。<strong>ときどき正規化</strong>
    - [x] 補間は<strong>`Slerp`</strong>（毎フレームの小さな追従は `Lerp` + 正規化でもよい）
    - [x] 「ある方向を向く」は <strong>`LookRotation` + `Slerp`</strong>

## 関連ページ

- [3D ゲーム（目次）](../3d/index.md)
- [行列](matrices.md)
- [カメラ](../3d/camera.md)
- [スキニング](../3d/skinning-animation.md)
- [SimpleMath](simplemath.md)
