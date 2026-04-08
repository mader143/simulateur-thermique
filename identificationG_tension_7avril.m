opt = tfestOptions;
opt.InitialCondition = "zero";

% Extraire les données
%t = out.tout;
V1 = pwm20_16_tension(:,1);    
V_id1 = V1 - V1(1); 
V2 = pwm20_16_tension(:,2); 
V_id2 = V2 - V2(1); 
V3 = pwm20_16_tension(:,3);             
V_id3 = V3 - V3(1); 

disp(size(V_id1));

T0 = 16;
% Définir l'entrée réelle : échelon de 7.8%
u = (20/255) * 100 * ones(size(V1));  % en duty cycle
p = 11.380*exp(0.0186*u)-0.1467*T0-8.0154;
disp(p);


% IDENTIFICATION
data_id1 = iddata(V_id1, p, 0.5);     

np = 1;

G1 = tfest(data_id1, np, 0, opt); 

disp('G1:');
tf(G1)

data_id2 = iddata(V_id2, V_id1, 0.5);     

np = 1;

G2 = tfest(data_id2, np, 0, opt); 

disp('G2:');
tf(G2)

data_id3 = iddata(V_id3, V_id2, 0.5);     

np = 1;

G3 = tfest(data_id3, np, 0, opt); 

disp('G3:');
tf(G3)

%   step(G1)
step(G2)
step(G3)




% Trouver la longueur minimale
%n = min(length(t), length(y));

% Tronquer les deux au même nombre de lignes
%t_cut = t(1:n);
%y_cut = y(1:n, :);   % garde les 2 colonnes

% Exporter avec les 2 signaux (consigne + mesure)
%T = table(t_cut, y_cut(:,1), y_cut(:,2), ...
 %   'VariableNames', {'time', 'signal1', 'signal2'});
%writetable(T, 'simulation5.csv');