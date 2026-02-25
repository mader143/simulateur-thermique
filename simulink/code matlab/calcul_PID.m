s = tf("s");
K_p = 10.92;
T_p = 83.69;

G_p = (K_p)/(T_p * s + 1);

T_H = T_p/2; %temps de reponse boucle ferme

T_i = T_p;
K_c = (T_i)/(K_p * T_H);

G_c = (K_c * (T_i * s + 1))/(T_i * s);

%Discretisation

T = 0.1;

num = 1 -exp(-T/T_i);
den =-exp(-T/T_i);

disp('num:');
tf(num)

disp('den:');
tf(den)

disp("u");
G_c


%% DÉFINIR xInitial AVANT LA SIMULATION

% Paramètres
T_initiale = 23.6;  % °C

% Créer le vecteur d'états initiaux
% Pour un système 1er ordre (Transfer Fcn) + PIDF, tu as plusieurs états:
% État 1: Sortie du Transfer Fcn (température)
% États 2-4: États internes du PID (intégrateur, dérivateur, filtre)

xInitial = [T_initiale;  % État du Transfer Fcn
            0;           % Intégrateur du PID
            0;           % Dérivateur du PID
            0];          % Filtre du PID (si PIDF)

% Maintenant lance la simulation
sim('test_pid');