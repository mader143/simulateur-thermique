% IDENTIFICATION G1
opt = tfestOptions;
opt.InitialCondition = "zero";

% Extraire les données
t = T3{:,1};  % temps
y1 = T3{:,2};  % température
y_id1 = y1 - y1(1);  % température relative à T0

% Définir l'entrée réelle : échelon de 7.8%
u = 7.8 * ones(size(t));  % échelon de 7.8%


%IDENTIFICATION G3
y3 = T3{:,2}; 
y_id3 = y3 - y3(1);

data_id3 = iddata(y_id3, u, 0.5);

np = 2;

G3 = tfest(data_id3, np, opt); 

disp('G3:');
tf(G3)


% Comparer la réponse du modèle avec les données
figure;
compare(data_id3, G3);
title('Validation du modèle identifié');

%figure;
%plot(t, y_id1);hold on
%plot(t, y_id2);hold on
%plot(t, y_id3);
%title("Température des thermistances par rapport au PO");