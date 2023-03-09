function [x,u,nr,ns,k] = qsolve1(P, q, A, b, rho, tolr, tols, iternum)
%  Solve a quadratic programming problem
%  min (1/2) x^T P x + x^T q + r
%  subject to Ax = b, x >= 0  using ADMM
%  P n x n,   q, r, in R^n, A m x n,  b in R^m
%  A of rank m

m = size(A,1); fprintf('m =  %d ',m)
n = size(P,1); fprintf('    n =  %d \n',n)
u = ones(n,1); u(1,1) = 0; % to initialize u
z = ones(n,1);             % to initialize z
% iternum = maximum number of iterations; 
% iternum = 80000 works well 
k = 0; nr= 1; ns = 1;
%  typically tolr = 10^(-10); tols = 10^(-10);
%  Convergence is controlled by the norm nr of the primal residual r
%  and the norm ns of the dual residual s

while (k <= iternum) && (ns > tols || nr > tolr) 
    z0 = z;
    k = k+1;
    %  Makes KKT matrix
    KK = [P + rho* eye(n) A'; A zeros(m,m)];
    % Makes right hand side of KKT equation
    bb = [-q + rho*(z - u); b];
    % Solves KKT equation
    xx = KK\bb;
    %  update x, z, u (ADMM update steps)
    x = xx(1:n);
    z = poslin(x + u);
    u = u + x - z; 
    %  to test stopping criterion
    r = x - z;                    % primal residual
    nr = sqrt(r'*r);              % norm of primal residual
    s = rho*(z - z0);             % dual residual
    ns = sqrt(s'*s);              % norm of dual residual
end
end

