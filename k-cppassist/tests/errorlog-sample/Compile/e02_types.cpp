// 型の不一致・変換できない
#include <memory>
#include <string>
#include <vector>

struct Point { int x; int y; };
void TakePoint(Point p) { (void)p; }
void TakeRef(int& r) { r = 0; }

void Types() {
  int n = "hello";                       // C2440: const char* から int
  std::string s = 42;                    // C2440
  Point p = 5;                           // C2440
  TakePoint(1, 2);                       // C2660: 引数の数
  TakePoint("a");                        // C2664
  TakeRef(10);                           // C2664: 右辺値を非 const 参照に
  std::vector<int> v = {1, 2, "three"};  // C2440
  std::unique_ptr<int> a = std::make_unique<int>(1);
  std::unique_ptr<int> b = a;            // C2280: コピー不可
  int* ptr = 3.14;                       // C2440
  (void)n; (void)s; (void)p; (void)b; (void)ptr; (void)v;
}
