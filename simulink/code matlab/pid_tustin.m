Gc = tf([2169.8 10.849],[200 0])

Gz = c2d(Gc, 0.5, 'tustin');
disp('Gz:');
tf(Gz)