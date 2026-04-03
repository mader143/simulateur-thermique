% Extraire le temps et le signal depuis l'objet SimulationOutput
t = out.tout;                % le temps
y = out.Fichier;              % le signal de sortie (adapte le nom si différent)


% Trouver la longueur minimale
n = min(length(t), length(y));

% Tronquer les deux au même nombre de lignes
t_cut = t(1:n);
y_cut = y(1:n, :);   % garde les 2 colonnes

% Exporter avec les 2 signaux (consigne + mesure)
T = table(t_cut, y_cut(:,1),  ...
    'VariableNames', {'time', 'sortie'});
writetable(T, 'donnees.csv');