function [lamb,mu,w,b] = SVMhard2(rho,u,v)
%  
%   Runs hard margin SVM version 2   
%
%   p green vectors u_1, ..., u_p in n x p array u
%   q red   vectors v_1, ..., v_q in n x q array v
%
%   First builds the matrices for the dual program
%
p = size(u,2); q = size(v,2); n = size(u,1);
[A,c,X,Pa,qa] = buildhardSVM2(u,v);
%
%  Runs quadratic solver
%
tolr = 10^(-10); tols = 10^(-10); iternum = 180000;
[lam,U,nr,ns,kk] = qsolve1(Pa, qa, A, c, rho, tolr, tols, iternum);
fprintf('steps =  %d ',kk)
if kk > iternum
   fprintf('** qsolve did not converge. Problem not solvable ** \n')
end

%%%%%%
%%% Solve for w and b here
%%%%%%

% Solve for w
w = -X * lam;

% Build lambda and mu vectors for equation
lamb = lam(1:p,1); % slice lambda and mu
mu = lam(p+1:p+q,1);

lamb = lamb.';
mu = mu.';

% Find no./index of positive values of lam and mu
lamPos = find(lamb > 0.0001);
numsvl1 = size(lamPos,2);
muPos = find(mu > 0.0001);
numsvm1 = size(muPos,2);

% Get corresponding elements from u and v
uPos = u(:,lamPos);
uPos = uPos.';
uPos = [zeros([1,n]); uPos];

vPos = v(:,muPos);
vPos = vPos.';
vPos = [zeros([1,n]); vPos];

if numsvl1 == 0 % Account for edge case where no positive values found
    numsvl1 = 1;
    uPos = zeros([1,n]);
end
if numsvm1 == 0
    numsvm1 = 1;
    vPos = zeros([1,n]);
end

% Solve for b (w --> 1 by n, averaged sum --> n by 1), 
% result should be scalar

avgSum = ((sum(uPos,1)/numsvl1) + (sum(vPos,1)/numsvm1)).';
disp(size(avgSum));
disp(avgSum);

b = (w.' * avgSum)/2;

% compute norm of w
nw = norm(w);

if n == 2
   [ll,mm] = showdata(u,v);
   if numsvl1 > 0 && numsvm1 > 0 
      showSVMs2(w,b,1,ll,mm,nw)
   end
end
end

