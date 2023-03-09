%
% Function to convert a 2^m x 2^n matrix A to the matrix U 
% of its Haar coefficients. This is the standard method. 
% Converts all the rows and then all the columns
%

function U = haar2D(A)
sz = size(A);
m = log2(sz(1));
n = log2(sz(2));
U = A;
for i = 1:2^m
    U(i,:) = haar_step(U(i,:),m);
end
for i = 1:2^n
    U(:,i) = haar_step(U(:,i),n);
end
% disp(U);
end
