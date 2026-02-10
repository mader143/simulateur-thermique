data = load("file name");

t = data(1);
T = data(2);

np = 2;   % poles
nz = 1;   % zeros
iodelay = NaN % retard inconnu

sys = tfest(data, np, nz, iodelay);

N = sys.Numerator;
D = sys.Denominator;

