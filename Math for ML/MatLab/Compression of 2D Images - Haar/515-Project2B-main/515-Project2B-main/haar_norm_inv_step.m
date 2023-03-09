%
%  Program to compute the coefficients of a sequence of length 2^n given its
%  coefficients over the Haar basis; takes the number of averaging steps
%  as parameter (level of recursion). This includes normalization.
%    

function u = haar_norm_inv_step(c,numstep)
% compute n
n = log2(length(c));
u = c;
% perform computation over Haar coefficients to get Haar Basis
for j = n-numstep:1:n-1
    for i = 1:2^j
        u(2*i-1) = (c(i) + c(2^j+i))/sqrt(2);
        u(2*i) = (c(i) - c(2^j+i))/sqrt(2);
    end
    c = u;
end
