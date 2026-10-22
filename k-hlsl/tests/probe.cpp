#include "local.h"
#pragma once
namespace ns { int gv = 1; enum Color { Red, Green = 2 }; }
static const int kLimit = 8;
int g_counter;
struct Base { int field; int Get() const { return field; } };
class Shape : public Base
{
public:
    void Draw(int count) { for (int k = 0; k < count; ++k) { field += k; } }
private:
    int hidden;
protected:
    float weight;
};
[[nodiscard]] int Compute(int a, float b)
{
    Shape s;
    s.Draw(a);
    int r = s.Get() + ns::gv + g_counter + kLimit;
    ns::Color c = ns::Red;
    do { r++; } while (r < 3);
    if (r > 1) { goto done; } else if (r < 0) { throw 1; }
    try { r = 0; } catch (...) { r = 1; }
    bool t = true && !false;
    auto p = &s;
    r = p->field ? 1 : 2;
done:
    return r;
}
