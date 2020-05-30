int gcd(int x, int y) {
    if (y!=0) { return gcd(y, x%y); }
    else { return x; }
}

int main() {
    int x = readInt();
    int y = readInt();
    printInt(gcd(x, y));
    return 0;
}