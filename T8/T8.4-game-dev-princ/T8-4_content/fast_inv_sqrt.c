#include <stdint.h>
#include <stdio.h>
#include <string.h>

float Q_rsqrt(float number)
{
    int32_t i;
    float x2, y;
    const float threehalfs = 1.5F;

    x2 = number * 0.5F;
    y = number;
    memcpy(&i, &y, sizeof(i));
    i = 0x5f3759df - (i >> 1);
    memcpy(&y, &i, sizeof(y));
    y = y * (threehalfs - (x2 * y * y));

    return y;
}

int main(void)
{
    float values[] = {0.25F, 1.0F, 4.0F, 100.0F};
    int n = sizeof(values) / sizeof(values[0]);

    for (int k = 0; k < n; k++)
    {
        printf("%.4f -> %.6f\n",
               values[k], Q_rsqrt(values[k]));
    }

    return 0;
}
