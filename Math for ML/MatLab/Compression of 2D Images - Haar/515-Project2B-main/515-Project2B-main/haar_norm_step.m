%
% Function to compute the coefficients of a sequence u of length 2^n
% over the Haar basis. Takes the number of averaging steps as parameter
% (level of recursion). This includes normalization.
%  
%
function c = haar_norm_step(u,numstep)
% compute n
n = log2(length(u));
c = u;
% perform computation over Haar Basis
for j = n-1:-1:n-numstep
    for i = 1:2^j
        c(i) = (u(2*i-1) + u(2*i))/sqrt(2);
        c(2^j+i) = (u(2*i-1) - u(2*i))/sqrt(2);
    end
    u = c;
end
end
