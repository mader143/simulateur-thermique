%% Standalone identification of G(s) = K / (1 + T s)^2

% -----------------------------
% Load experimental data
% -----------------------------
t = out.tout(:);
y = out.allo(:);

% Make output relative to initial value
y_id = y - y(2);

% Input step amplitude
U = 20;

% Shift time so that it starts at zero
t = t - t(1);

% Keep only nonnegative time values
idx = t >= 0;
t = t(idx);
y_id = y_id(idx);

% -----------------------------
% Initial parameter guesses
% -----------------------------
K0 = (y_id(end) - y_id(1)) / U;
if abs(K0) < 1e-12
    K0 = 1e-3;
end

% Rough guess for T: around 1/4 to 1/3 of total duration
T0 = max(t(end) / 4, eps);

theta0 = [K0, T0];   % theta = [K, T]

% -----------------------------
% Parameter estimation
% -----------------------------
cost_fun = @(theta) sum((y_id - model_response(theta, t, U)).^2);

options = optimset( ...
    'Display', 'iter', ...
    'TolX', 1e-10, ...
    'TolFun', 1e-10, ...
    'MaxFunEvals', 5000, ...
    'MaxIter', 5000);

theta_est = fminsearch(cost_fun, theta0, options);

K_est = theta_est(1);
T_est = theta_est(2);

% Enforce positive T in the reported result
T_est = abs(T_est);

% Recompute fitted output with positive T
y_fit = model_response([K_est, T_est], t, U);

% -----------------------------
% Display results
% -----------------------------
fprintf('\nEstimated parameters:\n');
fprintf('K = %.8f\n', K_est);
fprintf('T = %.8f s\n', T_est);

fprintf('\nEstimated transfer function:\n');
fprintf('          %.8f\n', K_est);
fprintf('G(s) = -------------------\n');
fprintf('       (1 + %.8f s)^2\n\n', T_est);

% Equivalent polynomial form
a = T_est^2;
b = 2 * T_est;
c = 1;

fprintf('Equivalent form:\n');
fprintf('              %.8f\n', K_est);
fprintf('G(s) = -------------------------\n');
fprintf('       %.8f s^2 + %.8f s + %.8f\n\n', a, b, c);

% -----------------------------
% Goodness of fit
% -----------------------------
sse = sum((y_id - y_fit).^2);
sst = sum((y_id - mean(y_id)).^2);
r2 = 1 - sse / sst;

fprintf('Fit quality:\n');
fprintf('SSE = %.8e\n', sse);
fprintf('R^2 = %.6f\n\n', r2);

% -----------------------------
% Plot
% -----------------------------
figure;
plot(t, y_id, 'b', 'LineWidth', 1.5);
hold on;
plot(t, y_fit, 'r--', 'LineWidth', 1.8);
grid on;
xlabel('Time (s)');
ylabel('Output');
legend('Experimental data', 'Fitted model', 'Location', 'best');
title('Identification of G(s) = K / (1 + T s)^2');

% -----------------------------
% Local model function
% Step response of:
% G(s) = K / (1 + T s)^2
% for an input step of amplitude U
%
% y(t) = U * K * [1 - (1 + t/T) * exp(-t/T)]
% -----------------------------
function y = model_response(theta, t, U)
    K = theta(1);
    T = abs(theta(2));

    % Protect against T = 0
    T = max(T, 1e-12);

    y = U * K * (1 - (1 + t ./ T) .* exp(-t ./ T));
end