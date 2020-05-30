int f(int x) {
    if(x<=2) { return 1; }
    else { return f(x-1)+f(x-2); }
}

int main() {
    int a = readInt();
    printInt(f(a));
    return 0;
}