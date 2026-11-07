// テンプレート・オーバーロード解決・concepts
#include <algorithm>
#include <map>
#include <string>
#include <type_traits>
#include <vector>

template <typename T>
T Max(T a, T b) { return a > b ? a : b; }

struct NoCompare { int v; };

template <typename T>
concept Number = std::is_arithmetic_v<T>;

template <Number T>
T Twice(T v) { return v * 2; }

void Templates() {
  Max(1, 2.5);                           // C2672: T が曖昧
  Max(NoCompare{1}, NoCompare{2});       // C2676: > が使えない
  Twice(std::string("a"));               // 制約を満たさない
  std::vector<NoCompare> v;
  std::sort(v.begin(), v.end());         // テンプレート内部の長いエラー
  std::map<NoCompare, int> m;
  m[NoCompare{1}] = 2;                   // operator< がない
  std::vector<int> w;
  w.push_back("a", 2);                   // 引数の数
  w.nosuch();                            // C2039
  Max<>();                               // C2672
}
