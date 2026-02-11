% Identification de la fonction de transfert
% Extraire les données
t = T135_55{:,1};  % temps
y = T135_55{:,2};  % température

% Créer un objet iddata (Input-Output Data)
% échelon unitaire comme entrée
u = ones(size(t));  % échelon
data_id = iddata(y, u, t(2)-t(1));

np = 1;    % 1er ordre suffit probablement
nz = 0;    % pas de zéro
iodelay = NaN;  % estimation automatique pour delay

% Identifier un système du premier ordre avec retard
sys_id = tfest(data_id, np, nz, 'IODelay', iodelay);

% Afficher la fonction de transfert identifiée
disp('Fonction de transfert identifiée:');
tf(sys_id)

% Calculer les paramètres caractéristiques
pole = pole(sys_id);
tau = -1/pole;  % constante de temps
K = dcgain(sys_id);  % gain statique

fprintf('Gain statique K = %.4f\n', K);
fprintf('Constante de temps τ = %.4f s\n', tau);
fprintf('Temps de réponse (3τ) = %.4f s\n', 3*tau);
fprintf('Temps de réponse (5τ) = %.4f s\n', 5*tau);

% Comparer la réponse du modèle avec les données
figure;
compare(data_id, sys_id);
title('Validation du modèle identifié');