%
%  To display a cubic B-sline given by de Boor control points
%   d_0, ..., d_N  
%
% Input points: left click for the d's then press enter (or return, or right click)  
%
%  Performs a loop from 1 to N - 2 to compute the Bezier
%  points using de Casteljau subdivision
%  nn is the subdivision level
%
%  This version also outputs the x-coodinates and the y-coordinates
%  of all the control points of the Bezier segments stored in
%  Bx(N-2,4) and By(N-2,4)
%

function [Bx, By] = bspline2b(dx,dy,N,nn,drawb)
% Works if N >= 4.

 %%% COMPUTE Bx AND By HERE %%%
 Bx = zeros(N-2, 4);
 By = zeros(N-2, 4);
 clooper = 1;
 for i = 1:N+1
    Cx = [];
    Cy = [];
    % the "1/2"s of the rule
    if (i == 2) || (i == N-1)
        bx = (dx(i,:) + dx(i+1,:)) / 2;
        by = (dy(i,:) + dy(i+1,:)) / 2;
        if (i == 2)
            % C is the segment
            % composed of i-1, i, and i+1 "d" points
            % plus our b0 point between
            Cx = [dx(i-1,:), dx(i,:), bx, dx(i+1,:)];
            Cy = [dy(i-1,:), dy(i,:), by, dy(i+1,:)];
        else
            Cx = [dx(i,:), bx, dx(i+1,:), dx(i+2,:)];
            Cy = [dy(i,:), by, dy(i+1,:), dy(i+2,:)];
        end
     elseif (i > 2) && (i < N-1)
         bx1 = (2/3) * dx(i,:) + (1/3) * dx(i+1,:);
         by1 = (2/3) * dy(i,:) + (1/3) * dy(i+1,:);
         bx2 = (1/3) * dx(i,:) + (2/3) * dx(i+1,:);
         by2 = (1/3) * dy(i,:) + (2/3) * dy(i+1,:);
         Cx = [dx(i,:), bx1, bx2, dx(i+1,:)];
         Cy = [dy(i,:), by1, by2, dy(i+1,:)];         
    end
    if (isempty(Cx) == 0)
        Bx(clooper,:) = Cx;
        By(clooper,:) = Cy;
        clooper = clooper+1;
    end
 end
 
 for i = 1:N-2
     if (i ~= N-2)
         x1 = Bx(i,3);
         y1 = By(i,3);
         x2 = Bx(i+1,2);
         y2 = By(i+1,2);
         sharedx = (x1+x2)/2;
         sharedy = (y1+y2)/2;
         Bx(i,4) = sharedx;
         By(i,4) = sharedy;
         Bx(i+1,1) = sharedx;
         By(i+1,1) = sharedy;
     end
 end
 
% nn is the subdivision level
% fprintf('numpt = %d \n', numpt)
figure;
dim_data = 2;
B = zeros(dim_data,4);
plot(dx,dy,'or-');   % plots d's as red circles
hold on;
for i = 1:N-2       
    B(1,:) = Bx(i,:);
    B(2,:) = By(i,:);
    drawbezier_dc(B,nn,drawb);
end
hold off;
end

