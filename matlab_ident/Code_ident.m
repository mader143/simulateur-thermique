T1 = readtable('10_30.csv');
save('10_30.mat', 'T1');

T2 = readtable('10_30_2.csv');
save('10_30_2.mat', 'T2');

temp1 = T1(4:end,2);
temp2 = T2(4:end,2);
disp(temp1);

np = 2;   % poles
nz = 1;   % zeros
iodelay = NaN; % retard inconnu

sys = tfest(temp1, temp2, np, nz, iodelay);

N = sys.Numerator;
D = sys.Denominator;

