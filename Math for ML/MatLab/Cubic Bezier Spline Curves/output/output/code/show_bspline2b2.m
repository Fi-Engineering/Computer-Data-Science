function [Bx, By] = show_bspline2b2(dx,dy)
%
% This is an auxilary function designed to output Bx and By
% for the version that uses dx and dy as input instead of
% screen input
%
% To plot a B-spline curve given by de Boor control points
% d_0, ..., d_N.
% Works if N >= 4
% This version uses the de Casteljau algorithm to plot the
% Bezier segments
%
%  drawb = 1, shows Bezier control polygons
%
% nn = subdivision level for de Casteljau 
nn = 6;

N = size(dx,1)-1;
fprintf('N = %d \n', N)
drawb = 1;
%
[Bx, By] = bspline2b(dx,dy,N,nn,drawb);
hold off
% Bx
% By
end
