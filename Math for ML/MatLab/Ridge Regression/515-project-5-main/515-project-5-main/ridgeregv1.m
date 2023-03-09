function [w,nw1,b,xi,nxi] = ridgeregv1(X,y,K)
%  Ridge regression with centered data
%  b is not penalized
%  X is an m x n matrix, y a m x 1 colum vector
%  weight vector w, intercept b
%  Solution in terms of the primal variables
%

m = size(y,1);
n = size(X,2);

% Solve for w

Xmean = mean(X);
Xbar = repelem(Xmean,m,1);
Xhat = X - Xbar;

ybar = mean(y);
yhat = y - (ybar * ones(m,1));
% ybar = repelem(ymean,m,1);

Im = eye(m);

w = Xhat.' * ((Xhat * Xhat.' + (K * Im)) \ yhat);
% disp(size(w));

% Solve for b
b = ybar - (Xmean * w);
% disp(size(b));

nw1 = norm(w);
xi = yhat - (Xhat*w);
nxi = norm(xi);

end
