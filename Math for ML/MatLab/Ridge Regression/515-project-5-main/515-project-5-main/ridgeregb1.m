function [w,b,xi,nxi,alpha] = ridgeregbv2(X,y,K)
%  Ridge regression 
%  b is not penalized
%  Uses the KKT equations
%  X is an m x n matrix, y a m x 1 colum vector
%  weight vector w, intercept b
%  Solution in terms of the dual variables
%  This version does not display the solution
%

m = size(y,1);
n = size(X,2);
X1 = (X*X.') + (K*eye(m));
A = [X1 ones(m,1); ones(1,m)  0];
B = [y; 0];

alpha_mu = linsolve(A,B);
alpha = alpha_mu(1:m);
mu = alpha_mu(end);

w = X.' * alpha;

b = mu;
xi = K * alpha;

nxi = norm(xi);

% disp(size(b));

end
