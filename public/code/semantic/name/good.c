int main()
{
    int a = 10;
    a = a + 1;
    int b = 20;

    {
        int a = 9;
        a = a + b;
    }
}