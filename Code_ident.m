data = load("file name");

t = data(1);
T = data(2);

sys = tfest();

N = sys.Numerator;
D = sys.Denominator;

