// モダン C++ の機能まわり
#include <array>
#include <optional>
#include <string>
#include <variant>

static_assert(sizeof(int) == 8, "int が 8 バイトではない");  // C2338

struct Base {
  virtual void Run() {}
  virtual void Stop() final {}
};

struct Derived : Base {
  void Run(int) override {}              // override するものがない
  void Stop() override {}                // final を上書き
};

enum class Color { Red, Green };

void Modern() {
  Color c = 0;                           // C2440: enum class に int は入らない
  int n = Color::Red;                    // C2440
  std::array<int, 3> a = {1, 2, 3, 4};   // 初期化子が多い
  auto x;                                // C3531: 初期化子がない
  auto [p, q] = 5;                       // 構造化束縛できない
  std::optional<int> o = "a";            // C2440
  int arr[2] = {1, 2, 3};                // C2078
  int narrow{3.5};                       // C2397: 縮小変換
  for (auto e : 5) {}                    // 範囲 for できない
  (void)c; (void)n; (void)a; (void)o; (void)arr; (void)narrow;
}

int main() { return 0; }
