---
title: sol2（Lua の組み込み）
tags:
  - 外部ライブラリ
---

# sol2（Lua の組み込み）

敵の動きや会話のイベントを C++ のコードに直接書くと、一行直すたびにビルドし直しです。ビルドに数十秒かかると、パラメーターの調整や、ちょっとした挙動の変更に何十回も待つことになります。

ゲームの中に<strong>スクリプト言語を組み込む</strong>と、ゲームを起動したまま、ファイルを書き換えるだけで、挙動を変えられます。Lua は、小さく速く、ゲーム用のスクリプト言語として長い実績があります。sol2 は、C++ から Lua を呼び、Lua から C++ を呼ぶ橋渡しを短いコードで書けるようにするライブラリです。

!!! tip "ポイント"
    - Lua の C API は低レベルで書きにくい。sol2 は、それを C++ らしい書き方で包む
    - 使う型は、`sol::state`（Lua の世界）、`sol::function`（Lua の関数）、`sol::usertype`（C++ のクラスを見せる）
    - スクリプトは、ファイルから読み込む。ゲームを止めずに、読み込み直せる
    - スクリプトの実行は失敗する前提。`sol::protected_function` で、エラーを受ける
    - 毎フレーム大量に呼ぶと遅い。スクリプトに任せるのは、頻度が低く、変更が多い部分に絞る

!!! info "このページを読む前に"
    - [外部ライブラリの入れ方](../vs/libraries.md)（vcpkg）
    - [リソース管理](../engine/resource.md)（スクリプトも、リソースの 1 つ）

## 導入（Visual Studio） {#setup}

vcpkg で、sol2 と Lua を入れます。

```json
{
  "dependencies": ["sol2", "lua"]
}
```

sol2 は、ヘッダーのみのライブラリで、Lua 本体は別のライブラリです。どちらも `vcpkg.json` に書けば、Visual Studio が自動で入れます。

そのほかの方法（CMake など）は、ライブラリの公式ページを見てください。

## 最小の例 {#minimal}

```cpp
#include <sol/sol.hpp>

int main() {
  sol::state lua;                                   // Lua の世界を作る
  lua.open_libraries(sol::lib::base, sol::lib::math);  // 使う標準ライブラリだけ開く

  lua.script("print('hello from lua')");            // 文字列のスクリプトを実行する

  lua["score"] = 100;                               // C++ から Lua の変数に値を入れる
  lua.script("score = score + 50");                 // Lua 側で変更する
  int score = lua["score"];                         // C++ に読み戻す（150）
}
```

`sol::state` が 1 つの Lua の世界です。`open_libraries` で、スクリプトから使える標準ライブラリを選びます。ゲームのスクリプトにファイル操作（`io`）や OS の呼び出し（`os`）を許すと、危険なので、必要なものだけ開きます。

`lua["score"]` は、グローバル変数への参照のように使えます。代入で書き、変数に代入して読みます。

## C++ の関数を Lua から呼ぶ {#function}

```cpp
// Lua から呼べるように、C++ の関数を登録する
lua.set_function("spawn_enemy", [](const std::string& name, float x, float y) {
  SpawnEnemy(name, x, y);
});
```

```lua
-- Lua のスクリプト
spawn_enemy("slime", 10.0, 5.0)
```

C++ の関数（ラムダも可）を Lua の名前に結びつけます。引数と戻り値の型変換は、sol2 が自動で行います。

## Lua の関数を C++ から呼ぶ {#call}

```cpp
lua.script_file("enemy.lua");                        // ファイルを読み込んで実行する

sol::protected_function update = lua["update"];     // Lua の関数を取り出す
auto result = update(delta_time);                    // 引数を渡して呼ぶ
if (!result.valid()) {
  sol::error err = result;                           // 失敗したら、メッセージを取る
  std::println("Lua error: {}", err.what());
}
```

```lua
-- enemy.lua
function update(dt)
  -- 毎フレーム呼ばれる
end
```

スクリプトは、書き間違いで簡単に失敗します。`sol::function` は、失敗すると例外を投げますが、`sol::protected_function` なら、`valid()` で成功を確かめられます。ゲームがスクリプトのエラーで落ちないように、`protected_function` を使います。

## C++ のクラスを Lua に見せる {#usertype}

```cpp
struct Player {
  int hp = 100;
  void Heal(int amount) { hp += amount; }
};

lua.new_usertype<Player>("Player",
    sol::constructors<Player()>(),   // Lua から Player.new() で作れるようにする
    "hp", &Player::hp,               // メンバー変数
    "heal", &Player::Heal);          // メンバー関数
```

```lua
local p = Player.new()
p:heal(20)
print(p.hp)     -- 120
```

`new_usertype` で、クラスのメンバーに Lua での名前を付けます。Lua 側では、`:` でメソッドを呼び、`.` でメンバー変数にアクセスします。

C++ のオブジェクトの寿命に注意します。Lua が、C++ のオブジェクトへの参照を持ったまま、C++ 側が先に破棄すると、参照先が無効になり、クラッシュします。敵のような、消えるかもしれないオブジェクトは、直接のポインタではなく、[ハンドル](../engine/handle.md)で渡す設計が安全です。

## スクリプトを読み込み直す {#reload}

ファイルの更新時刻を毎秒チェックし、変わっていたら `script_file` を再実行します。関数が上書きされるだけなので、ゲームを止めずに挙動を変えられます。状態をスクリプトの変数に持たせていると、読み込み直しで失われるので、状態は C++ 側のオブジェクトに持たせます。

## 速度 {#perf}

Lua は、スクリプト言語としては速いですが、C++ に比べると遅く、C++ と Lua の境界を越える呼び出しにも、コストがかかります。1 フレームに数千回、境界を越える呼び出しをすると、目立ちます。

方針は、<strong>重い処理は C++、決め事や流れはスクリプト</strong>です。敵の移動の計算は C++ で、「敵がどの状況でどう振る舞うか」の決定はスクリプトで、と分けます。

## よくあるミス {#mistakes}

??? failure "スクリプトの書き間違いで、ゲームが落ちる"
    `sol::function` で呼んでいます。`protected_function` を使い、エラーはログに出して続行します。

??? failure "`io` や `os` が使えて、危険"
    `open_libraries` で、必要なものだけ開きます。

??? failure "Lua が持つオブジェクトが C++ 側で消えて、クラッシュする"
    ポインタを直接渡さず、ハンドルや ID で渡します。

## これだけ覚える {#summary}

- sol2 は、Lua を C++ から使うための、書きやすい橋渡し
- `protected_function` でエラーを受ける。必要な標準ライブラリだけ開く
- 重い処理は C++、決め事はスクリプト。オブジェクトはハンドルで渡す

## 関連ページ

- [外部ライブラリ](index.md)
- [リソース管理](../engine/resource.md)
- [ハンドルと世代 ID](../engine/handle.md)
