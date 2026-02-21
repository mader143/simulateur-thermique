%% ================== TEST PID DISCRETISE (TUSTIN) ==================
clear; clc;

% ---- Tes paramètres (forme Ideal/Standard du bloc Simulink) ----
P = 182.300315921991;          % Proportional (Kp)
I = 0.0162226181568747;        % Integrator (affiché comme 1/Ti)
D = 9.89747852512141;          % Derivative (Td)
N = 0.481257498954388;         % Filter coeff (Td/Tf)
Ts = 0.1;                      % échantillonnage [s] (à adapter)

% ---- Appel : retourne la structure avec les coeffs et fonctions d'update
pid_d = pid_discretise_from_simulink(P,I,D,N,Ts);

disp(pid_d)    % affiche Kp, Ki, Kd, Tf, ad, bd, etc.

% ---- Petit test sur un step d'erreur e[k]
pid_d.resetFcn();
K = 100;
e = [ones(1,50), zeros(1,K-50)];   % erreur 1 pendant 50 pas, puis 0
u = zeros(1,K);
for k = 1:K
    u(k) = pid_d.updateFcn(e(k));
end

figure;
subplot(2,1,1); plot(e,'LineWidth',1.2); grid on; title('Erreur e[k]');
subplot(2,1,2); plot(u,'LineWidth',1.2); grid on; title('Commande u[k] - PID discret (Tustin)');

%% ================== LOCAL FUNCTION ==================
function pidd = pid_discretise_from_simulink(P, I, D, N, Ts)
% PID_DISCRETISE_FROM_SIMULINK
% Entrées (forme "Ideal/Standard" du bloc Simulink) :
%   P = Proportional (Kp)
%   I = 1/Ti (en s^-1)
%   D = Td (en s)
%   N = coeff du filtre dérivatif (Td/Tf)
%   Ts = période d’échantillonnage (s)
%
% Sortie :
%   structure avec Kp, Ki, Kd, Tf, ad, bd, IgainTustin
%   + 2 fonctions : updateFcn(e) et resetFcn()

% --- 1) Conversions Standard -> Parallel
Kp = P;
Ti = 1./I;                 % I affiché = 1/Ti
Td = D;
Tf = Td./N;                % constante de temps du filtre dérivatif

Ki = Kp./Ti;
Kd = Kp.*Td;

% --- 2) Discrétisation Tustin (Trapézoïdal)
IgainTustin = Ki*Ts/2;                     % Intégrateur
ad = (Ts - 2*Tf) / (Ts + 2*Tf);            % Dérivé filtré
bd = (2*Kd) / (Ts + 2*Tf);

% --- 3) Etats + closures
Ik = 0; Dk = 0; uk = 0; ekm1 = 0;

    function u = updateFcn(e)
        % Intégrale (Tustin)
        Ik_new = Ik + IgainTustin*(e + ekm1);
        % Dérivée filtrée (Tustin)
        Dk_new = ad*Dk + bd*(e - ekm1);
        % Commande
        u = Kp*e + Ik_new + Dk_new;

        % (option anti-windup/saturation ici si besoin)

        % MAJ états
        Ik = Ik_new; Dk = Dk_new; ekm1 = e; uk = u;
    end

    function resetFcn()
        Ik = 0; Dk = 0; uk = 0; ekm1 = 0;
    end

% --- 4) Pack
pidd = struct( ...
    'Kp',Kp, 'Ki',Ki, 'Kd',Kd, 'Tf',Tf, ...
    'ad',ad, 'bd',bd, 'IgainTustin',IgainTustin, ...
    'updateFcn',@updateFcn, 'resetFcn',@resetFcn, ...
    'info',struct('Ti',Ti,'Td',Td,'Ts',Ts) ...
);
end