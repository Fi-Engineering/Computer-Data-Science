%
%  Program to compute the coefficients of a sequence of length 2^n given its
%  coefficients over the Haar basis
%
function u = haar_inv(c)
% compute n
n = log2(length(c));
u = c;
% perform computation over Haar coefficients to get Haar Basis
for j = 1:n-1
    for i = 1:2^j
        u(2*i-1) = c(i) + c(2^j+i);
        u(2*i) = c(i) - c(2^j+i);
    end
    c = u;
%     for i = 1:n
%     for j = 1:2^i/2
% %         fprintf('j: %f | ',j)
%         u(j*2-1) = c(j) + c(j+(2^i/2));
%         u(j*2) = c(j) - c(j+(2^i/2))
%     end
%     c = u;
end
