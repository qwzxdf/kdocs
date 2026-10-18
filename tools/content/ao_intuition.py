import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

TITLE = "ここで使われる「積分」を、やさしく言うと"


def Box(link, body):
    lines = body.strip("\n").split("\n")
    return '!!! info "%s"\n%s\n\n    <strong>数式を使わない、くわしい説明</strong>は [Integrals and Elevation Angles in Plain Words](%s) です。\n' % (
        TITLE, "\n".join("    " + l if l.strip() else "" for l in lines), link)


pg.Add("ao/hbao.md", Box("theory/integral-intuition.md", """
HBAO の積分は、<strong>「断面の中で、空が見えている角度の範囲を、足す」</strong>ことです。

1. 画面の 1 方向（たとえば右）を決めて、その方向の<strong>断面</strong>を考える。
2. その方向に歩いて、<strong>一番高く見えた遮蔽物の仰角</strong>（地面から見上げる角度）を探す。これが<strong>地平線の仰角 h</strong>。
3. 面が傾いていなければ、仰角が 0° から h までが、壁に遮られた範囲。それより上は、空が見えている。
4. 断面の中の「見えている割合」は、<strong>仰角から式 1 つで</strong>出る（平らな地面なら、左右の地平線の仰角が分かれば、`(sin h₁ + sin h₂) / 2`）。方向を細かく刻んで足す必要がない。
5. 方向（断面）を 4〜8 枚、向きを変えて繰り返し、<strong>平均</strong>したものが AO。

つまり、下の式の `sin h − sin t` は、「面の傾き `t` から地平線の仰角 `h` までを、コサイン重みで足した結果」です。壁が高い（`h` が大きい）ほど、AO は暗くなります。
"""), before="## 式")

pg.Add("ao/gtao.md", Box("theory/integral-intuition.md", """
GTAO も、HBAO と同じく、<strong>断面ごとに、仰角（地平線）を 2 つ探して、見えている割合を、式で出す</strong>方式です。違いは、<strong>足すときの重み</strong>です。

- AO では、真上に近い方向ほど、重く足す（コサイン重み）のが正しい。
- HBAO は、この重みを、省略した式を使っていた。
- GTAO は、コサイン重みも含めて、<strong>正確に積分した式</strong>（下の `â`）を使う。

断面の中で、方向を刻まずに済むのは、コサインの積分が、サインや、コサインの式に、なるからです。仰角が 2 つ分かれば、式 1 回で、答えが出ます。断面を何枚も、平均するのは、HBAO と同じです。
"""), before="## 理論：スライスに分けた積分")

pg.Add("ao/ssao-crytek.md", Box("theory/integral-intuition.md", """
Crytek SSAO の積分は、<strong>くじ引き</strong>です。

- 半球の全方向を、細かく調べる代わりに、<strong>球の中に、ランダムな点を 16 個ほど撒く</strong>。
- 各点が、物の裏側に入っていれば（遮られていれば）1、そうでなければ 0 と数える。
- 遮られた点の<strong>割合</strong>が、AO。

点の数が少ないので、ざらざらしたノイズが出ます。これを、ぼかしで、ならします。この「ランダムに選んで、平均する」考え方を、<strong>モンテカルロ法</strong>と呼びます。
"""), before="## 手順")

pg.Add("ao/ssao-hemisphere.md", Box("theory/integral-intuition.md", """
Hemisphere SSAO の積分も、Crytek SSAO と同じ、<strong>ランダムな点を撒いて、遮られた割合を数える</strong>（モンテカルロ法）です。違いは、点を撒く場所が、<strong>法線の向きの半球</strong>だけ、という点です。

- 面の下側に、点を撒かないので、<strong>平らな面が、灰色にならない</strong>。
- 点は、<strong>面の近くに、多く</strong>（`scale` で、近くに寄せる）。近い遮蔽物ほど、AO に効くため。
- 点の数は 16 前後。足りない分は、ノイズとぼかしで、ごまかす。
"""), before="## 半球のサンプルを作る")

pg.Add("ao/alchemy-ao.md", Box("theory/integral-intuition.md", """
Alchemy AO は、方向を刻まず、<strong>「周りの点それぞれが、どれだけ遮るか」の簡単な式を、足し合わせる</strong>方式です。

- 周りの点 `q` について、<strong>`p` から `q` へのベクトル</strong> `v` だけで、遮りの強さを決める。
- 法線の向きに近い方向にある点（`v·n` が大きい）ほど、強く遮る。
- 近い点（`v·v` が小さい）ほど、強く遮る。
- 全部の点の寄与を足して、1 から引く。

もとは、半球全体の積分でしたが、<strong>点ごとの足し算に、書き直した</strong>ことで、サンプルを、数えるだけで済み、ノイズも、少なくなります。
"""), before="## 式")

pg.Add("ao/sao.md", Box("theory/integral-intuition.md", """
SAO は、<strong>Alchemy AO と同じ式</strong>（周りの点ごとの寄与を足す）を使います。違いは、<strong>「点を、どこから読むか」</strong>だけです。

- 遠い点は、細かく読んでも、AO に、ほとんど効かない。
- そこで、遠い点は、<strong>深度のミップ マップ</strong>（縮小した深度）から読む。メモリを、読む量が減り、半径が大きくても、遅くならない。

積分（足し算）の中身は、同じで、<strong>足す材料の、読み方だけを速くした</strong>方式です。
"""), before="## 処理の流れ")

pg.Add("ao/hbao-plus.md", Box("theory/integral-intuition.md", """
HBAO+ の積分は、<strong>HBAO と同じ</strong>（断面ごとに、仰角を探して、式で、見えている割合を出し、平均する）です。違いは、<strong>計算の進め方</strong>だけです。

- ランダムな向きを、毎画素、変えるのをやめて、<strong>決まった模様</strong>で、画面を、分ける（インターリーブ）。キャッシュが、効いて、速くなる。
- 積分の式を、<strong>簡単な形に</strong>して、計算を、減らす。
"""), before="## 改良 1：ランダムをやめて、インターリーブ")

pg.Add("ao/world-space/rtao.md", Box("../theory/integral-intuition.md", """
RTAO の積分も、<strong>くじ引き（モンテカルロ法）</strong>です。

- 画素から、<strong>半球の中のランダムな方向</strong>に、レイを、数本飛ばす。
- 近くで、何かに当たれば 0（遮られた）、当たらなければ 1（空に抜けた）。
- 抜けた割合が、AO。

SSAO との違いは、点を撒く代わりに、<strong>本物のレイ</strong>を飛ばす点です。画面の外や、手前の物の裏側も、正確に、数えられます。レイの数が、少ないと、ノイズが出るので、デノイズが、必要です。
"""), before="## よくあるミス")

pg.Add("ao/world-space/dfao.md", Box("../theory/integral-intuition.md", """
DFAO の積分は、<strong>半球を、数本の円錐に分けて、円錐ごとの、遮られ具合を足す</strong>ことです。

- 法線の向きの半球を、5〜9 本の、円錐に、粗く分ける（方向を、細かく刻む代わりに、<strong>太い束で刻む</strong>）。
- 各円錐に沿って、距離場（物までの距離）を読みながら進み、「円錐の、どれくらいが、物に遮られたか」を、見積もる。
- 円錐ごとの結果を、重みつきで足して、AO にする。

円錐の本数が、少ないので、細かい形は、表せませんが、レイを、何百本も飛ばすより、はるかに、軽く済みます。
"""), before="## よくあるミス")

pg.Add("ao/world-space/vxao.md", Box("../theory/integral-intuition.md", """
VXAO の積分は、DFAO と同じ、<strong>半球を、数本の円錐に分けて、円錐ごとの、遮られ具合を足す</strong>ことです。

- 円錐に沿って、ボクセル（3D の格子）の、<strong>占有度</strong>（どれだけ埋まっているか）を、読みながら進む。
- 円錐が進むほど、太くなるので、<strong>粗いミップ</strong>を読む。
- 占有度を、前から順に、積み重ねて（`occ += (1 − occ) × 占有度`）、円錐が、どれだけふさがれたかを、求める。
"""), before="## よくあるミス")

pg.Add("ao/theory/approximation.md", Box("integral-intuition.md", """
AO の積分は、<strong>「全方向の、見えている度合いを、重みつきで足して、平均する」</strong>ことです。方向は無限にあるので、<strong>刻んで</strong>足します。

- 3 つの近似は、<strong>刻み方の違い</strong>です。方向を、<strong>くじ引きで選ぶ</strong>（①）、<strong>仰角で、断面ごとに、一気に足す</strong>（②）、<strong>点ごとの式を足す</strong>（③）。
- 重みは、<strong>真上ほど大きい</strong>（コサイン重み）。真上から来る光が、面を、最も強く照らすため。
"""), before="## 積分を近似する 3 つのやり方")

pg.Add("ao/theory/from-rendering-equation.md", Box("integral-intuition.md", """
このページの式には、「積分」が出てきます。身構えなくて大丈夫です。AO で、積分と言うときは、<strong>「半球の全方向について、空が見えているか（1）遮られているか（0）を、重みつきで足して、平均する」</strong>という意味です。

先に、[Integrals and Elevation Angles in Plain Words](integral-intuition.md) を読むと、このページの式が、「あの足し算を、式で書いただけ」と分かります。
"""), before="## 出発点：レンダリング方程式")
print("ok")
