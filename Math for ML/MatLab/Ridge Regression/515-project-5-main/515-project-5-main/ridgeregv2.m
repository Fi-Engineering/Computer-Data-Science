function [w,nw2,b,xi,nxi] = ridgeregv2(X,y,K)
%  Ridge regression minimizing w and b
%  b is penalized
%  X is an m x n matrix, y a m x 1 colum vector
%  weight vector w, intercept b
%  Solution in terms of the primal variables
%  And also in terms of the dual variable alpha
%

m = size(y,1); n = size(X,2);
XX = [X ones(m,1)];

alpha = ((XX * XX.') + K * eye(m)) \ y;
wb = XX.' * alpha;
xi = K * alpha;
b = ones(m,1).' * alpha;
w = wb(1:end-1);

nw2 = norm(w);
nxi = norm(xi);

end

