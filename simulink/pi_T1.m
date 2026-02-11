s = tf("s");
K_p = 10.92;
T_p = 83.69;

G_p = (K_p)/(T_p * s + 1);

T_H = T_p; %temps de reponse boucle ferme

T_i = T_p;
K_c = (T_i)/(K_p * T_H);

G_c = (K_c * (T_i * s + 1))/(T_i * s);

%Discretisation

T = 0.1;

num = 1 -exp(-T/T_i);
den =-exp(-T/T_i);

disp('num:');
tf(num)

disp('den:');
tf(den)

disp(K_c);