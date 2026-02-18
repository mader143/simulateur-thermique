% IDENTIFICATION G1
opt = tfestOptions;
opt.InitialCondition = "zero";

% Extraire les données
t = T1{:,1};  % temps
y1 = T1{:,2};  % température
y_id1 = y1 - y1(1);  % température relative à T0

% Définir l'entrée réelle : échelon de 7.8%
u = 7.8 * ones(size(t));  % échelon de 7.8%

% Créer l'objet iddata
data_id1 = iddata(y_id1, u, 0.5);

np = 1;  % 1er ordre

% Identifier la fonction de transfert
G1 = tfest(data_id1, np, opt);

% Afficher sous forme normalisée K/(τs + 1)
disp('G1 sous forme normalisée:');
G1_normalized = tf(G1);
G1_normalized.Variable = 's';

% Extraire les paramètres
num = G1_normalized.Numerator{1};
den = G1_normalized.Denominator{1};

% Normaliser pour avoir la forme K/(τs + 1)
K = num(end) / den(end);      % Gain statique
tau = den(1) / den(end);      % Constante de temps

fprintf('K = %.4f °C/%%\n', K);
fprintf('τ = %.4f s\n', tau);
fprintf('\nG1(s) = %.4f / (%.4f s + 1)\n\n', K, tau);

% Recréer la fonction de transfert normalisée
G1_norm = tf(K, [tau 1]);
disp('Fonction de transfert normalisée:');
G1_norm

% Validation visuelle
figure;
compare(data_id1, G1_norm);
% Calculer les paramètres caractéristiques


%fprintf('Gain statique K = %.4f\n', K);
%fprintf('Constante de temps τ = %.4f s\n', tau);
%fprintf('Temps de réponse (3τ) = %.4f s\n', 3*tau);
%fprintf('Temps de réponse (5τ) = %.4f s\n', 5*tau);


%discretization
G1d = c2d(G1, 0.1);
disp("discretizé:");
tf(G1d)


%IDENTIFICATION G2
y2 = T2{:,2}; 
y_id2 = y2 - y2(1);

data_id2 = iddata(y_id2, y_id1, 0.5);

np = 1;

G2 = tfest(data_id2, np, opt); 

disp('G2:');
tf(G2)



%IDENTIFICATION G3
y3 = T3{:,2}; 
y_id3 = y3 - y3(1);

data_id3 = iddata(y_id3, y_id2, 0.5);

np = 1;

G3 = tfest(data_id3, np, opt); 

disp('G3:');
tf(G3)


% Comparer la réponse du modèle avec les données
figure;
compare(data_id2, G2);
title('Validation du modèle identifié');

%figure;
%plot(t, y_id1);hold on
%plot(t, y_id2);hold on
%plot(t, y_id3);
%title("Température des thermistances par rapport au PO");