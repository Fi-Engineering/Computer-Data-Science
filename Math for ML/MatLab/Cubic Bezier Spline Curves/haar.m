%
% Function to compute the coefficients of a sequence u of length 2^n
% over the Haar basis.
%
function c = haar(u)
% compute n
n = log2(length(u));
c = u;
% perform computation over Haar Basis
for i = n:-1:1
    for j = 1:2:2^i-1
        c((j+1)/2) = (u(j)+u(j+1))/2;
        c(2^(i-1)+(j+1)/2) = (u(j)-u(j+1))/2;
    end
    u = c;
end
end
