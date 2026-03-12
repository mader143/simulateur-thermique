% IDENTIFICATION G1
opt = tfestOptions;
opt.InitialCondition = "zero";

% Extraire les données
t = T1{:,1};  % temps
y1 = T1{:,2};  % température
y_id1 = y1 - y1(2);  % température relative à T0

% Définir l'entrée réelle : échelon de 7.8%
u = 7.8 * ones(size(t));  % échelon de 7.8%

data_id1 = iddata(y_id1, u, 0.5);

np = 1;

G1 = tfest(data_id1, np, opt); 

disp('G1:');
tf(G1)


% Extraire les données
y3 = T3{:,2};  % température
y_id3 = y3 - y3(2);  % température relative à T0

% Définir l'entrée réelle : échelon de 7.8%
u = 7.8 * ones(size(t));  % échelon de 7.8%

data_id3 = iddata(y_id3, y_id1, 0.5);

np = 1;

G3 = tfest(data_id3, np, opt); 

disp('G3:');
tf(G3)

Gz = c2d(G3, 0.5, 'tustin');
disp('Gz:');
tf(Gz)

%figure;
%plot(t, y_id1);hold on
%plot(t, y_id2);hold on
%plot(t, y_id3);
%title("Température des thermistances par rapport au PO");