opt = tfestOptions;
opt.InitialCondition = "zero";

% Extraire les données
t = out.tout;
y1 = out.sortie;              % le signal de sortie (adapte le nom si différent)
y_id1 = y1 - y1(2);  % température relative à T0



% Définir l'entrée réelle : échelon de 7.8%
u = 20 * ones(size(t));  % échelon de 7.8%


% IDENTIFICATION UT1
data_id1 = iddata(y_id1, u, 0.5);

np = 2;

G1 = tfest(data_id1, np, 0, opt); 

disp('G1:');
tf(G1);

step(G1)




% Trouver la longueur minimale
n = min(length(t), length(y));

% Tronquer les deux au même nombre de lignes
t_cut = t(1:n);
y_cut = y(1:n, :);   % garde les 2 colonnes

% Exporter avec les 2 signaux (consigne + mesure)
T = table(t_cut, y_cut(:,1), y_cut(:,2), ...
    'VariableNames', {'time', 'signal1', 'signal2'});
writetable(T, 'simulation5.csv');