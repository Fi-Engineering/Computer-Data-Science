%
% Function to convert a 2^m x 2^n matrix A to the matrix U 
% of its Haar coefficients. This is the standard method. 
% Converts all the rows and then all the columns
% This version uses the normalized coefficients. 
%

function U = haar2D_n(A)
sz = size(A);
m = log2(sz(1));
n = log2(sz(2));
U = A;
for i = 1:2^m
    U(i,:) = haar_norm_step(U(i,:),m);
end
for i = 1:2^n
    U(:,i) = haar_norm_step(U(:,i),n);
end
end
