% IDENTIFICATION G1
opt = tfestOptions;
opt.InitialCondition = "zero";
% Extraire les données
t = T1{:,1};  % temps
y1 = T1{:,2};  % température
y_id1 = y1- y1(1);


% Créer un objet iddata (Input-Output Data)
% échelon unitaire comme entrée
u = ones(size(t));  % échelon
data_id1 = iddata(y_id1, u, 0.5);

np = 1;    % 1er ordre suffit probablement

% Identifier un système du premier ordre avec retard
G1 = tfest(data_id1, np, opt); %forcer depart a zero

% Afficher la fonction de transfert identifiée
disp('G1:');
tf(G1)

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