%
%  Function to reconstruct a 2^m x 2^n matrix A from its
%  matrix of Haar coefficients. This version uses normalized
%  coefficients
%  Converts all the columns and then all the rows
%
function A = haar_inv2D_n(U)
sz = size(U);
m = log2(sz(1));
n = log2(sz(2));
A = U;
for i = 1:2^m
    A(i,:) = haar_norm_inv_step(A(i,:),m);
end
for i = 1:2^n
    A(:,i) = haar_norm_inv_step(A(:,i),n);
end
% disp(A);
end
