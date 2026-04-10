T_init = 23;
Consigne = 30;


Rf_1 = 3300;
Rg_1 = 5600;
R1_1 = 3300;
V1_1 = 1.774;
V2_1 = 5.0;
B1  = 4010;

Rf_2 = 6300;
Rg_2 = 5600;
R1_2 = 3300;
V1_2 = 1.80;
V2_2 = 5.0;
B2  = 3984;

Rf_3 = 6300;
Rg_3 = 5600;
R1_3 = 3300;
V1_3 = 1.79;
V2_3 = 5.0;
B3  = 3700;

% Variables pour les fonctions de transfert des thermistances
K1 = 0.007628;
T1 = 0.01103;
K2 = 0.03405;
T2 = 0.03035;
K3 = 0.04391;
T3 = 0.04924;
az = 0.01084;
bz = -0.9757;

pertub_1 = 0;
pertub_2 = 0;
pertub_3 = 0;
t_pertub_1 = 30;
t_pertub_2 = 30;
t_pertub_3 = 30;

nb_bits = 10;
Ts = 0.5;

%variables pour les pid
%chaud
Kc = 9.2;
Tic = 250;
Tdc = 35;

%froid
Kf = 10.5;
Tif = 230;
Tdf = 40;
