function [dx, dy, Bx, By] = interpnatxy(x,y, show_plot)
% This version uses the natural end condition
% Uses Matlab \ to solve linear systems
% Input points: two column vectors of x and y coordinates of dim N+1
%
%  This version uses x_0, x_1, ..., x_{N-1}, x_N to compute the Bezier
%  points and the subdivision version of the de Casteljau algorithm
%  to plot the Bezier segments (bspline2b and drawbezier_dc)
%
%  This version outputs the x and y coordinates dx and dy of the de Boor control
%  points d_{-1}, d_0, d_1, ..., d_{N+1} as column vectors
%  and the x and y coordinates of the Bezier control polygons
%  Bx and By
%
% Uses bspline2b from project 1b



N = size(x);

N = N(1) - 1;

diag_ones = ones([N-2,1]);

Id = 4 * eye(N-1);

Id_up = diag(diag_ones, 1);

Id_down = diag(diag_ones,-1);

A = Id + Id_up + Id_down;

B = A;

b = zeros([N-1,1]);
b(1) = 6*x(2) - x(1);
b(end) = 6*x(N)-x(N+1);
b(2:end-1) = 6*x(3:N-1);

dx = linsolve(A,b);

d_neg1 = x(1);
d_Nplus1 = x(N+1);
d_0 = (2/3)*x(1) + (1/3)*dx(1);
d_N = (1/3)*dx(end) + (2/3)*x(N+1);

dx = [d_neg1; d_0; dx; d_N; d_Nplus1];


c = zeros([N-1,1]);
c(1) = 6*y(2) - y(1);
c(end) = 6*y(N)-y(N+1);
c(2:end-1) = 6*y(3:N-1);

dy = linsolve(B,c);

d_neg1 = y(1);
d_Nplus1 = y(N+1);
d_0 = (2/3)*y(1) + (1/3)*dy(1);
d_N = (1/3)*dy(end) + (2/3)*y(N+1);

dy = [d_neg1; d_0; dy; d_N; d_Nplus1];


% Plots the spline
if show_plot
  Nx = size(dx,1)-1;
  fprintf('Nx = %d \n', Nx)
  nn = 6; % subdivision level
  drawb = true;
  [Bx, By] = bspline2b(dx,dy,Nx,nn,true);
   hold on
  plot(x,y,'b+'); % Plot x's as blue +
  hold off;
end
end
