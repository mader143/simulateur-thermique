

% Extract signal data (assuming a 'To Workspace' block named 'simout')
T2 = out.T2;
DC = out.dc;
disp(T2);
disp(DC);

opt.InitialCondition = "zero";


% IDENTIFICATION G1 (dcaT2)
data_id1 = iddata(T2, DC, 0.5);

np = 1;
G1 = tfest(data_id1, np, 0, opt); 

disp('G1:');
tf(G1)