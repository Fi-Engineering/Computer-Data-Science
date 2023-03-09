function [wps,nw3,bps,xi,nxi] = reglq(X,y)
%  Regression minimizing w and b
%  X is an m x n matrix, y a m x 1 colum vector
%  weight vector w, intercept b
%  Computes the least squares solution using the pseudo inverse
%
m = size(y,1); n = size(X,2);
XX = [X ones(m,1)];

wb = pinv(XX) * y;
wps = wb(1:end-1);
bps = wb(end);

nw3 = norm(wps);
xi = y - (X * wps) - (bps * ones(m,1));
nxi = norm(xi);

end

