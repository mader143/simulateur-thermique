% CHARGEMENT DES DONNÉES
%
% À partir de vos données, MODIFIER SI NÉCESSAIRE LE CODE SUIVANT
% pour former la  matrice data_id qui doit contenir au moins 3 colonnes:
%
% colonne 1: temps
% colonne 2: entrée u du système
% dernière colonne (3 ou plus): sortie y du système

T1 = load("10_30.csv");% Dans cet exemple le fichier procede1.asc est un fichier
T2 = load("10_30_2.csv")                  % ASCII ne contenant que 2 colonnes:
 
N=size(procede,1); % Nombre de lignes de procede1
t=0:1:N-1; % Création du vecteur temps de la bonne longueur
           % t=[0; 1; 2; .....; N-1]
t=2*t';  % Bon pas d'échantillonnage: t=[0; 2; 4; ...; 2*(N-1)]

dataid=[t procede]; % Création de la matrice dataid qui respecte les normes demandées.


% Le code qui suit va créer les données d'identification en soustrayant
% le premier point aux données d'entrée et de sortie. Les données seront
% également tracées.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% NE RIEN MODIFIER DANS CE QUI SUIT

% création des vecteurs t, u et y
Ncol=size(dataid,2);
t=dataid(:,1);
u=dataid(:,2);
y=dataid(:,Ncol);

% visualisation des données
figure(1);
subplot(211);
plot(t,u,'o');
ylabel('u');
xlabel('t');
title('Données brutes');
subplot(212);
plot(t,y,'o');
ylabel('y');
xlabel('t');

% soustraction des points d'opération
u_id=u-u(1);
y_id=y-y(1);

% visualisation des données sans les points d'opération
figure(2);
subplot(211);
plot(t,u_id,'o');
ylabel('u_i_d');
xlabel('t');
title('Données d''identification');
subplot(212);
plot(t,y_id,'o');
ylabel('y_i_d');
xlabel('t');