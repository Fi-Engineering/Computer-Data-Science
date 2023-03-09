% function to draw a Bezier segment
% using de Casteljau subdivision
% nn = level of subdivision
% used by bspline4_dc
% also plots the Bezier control polygons if drawb = 1
%
function drawbezier_dc(B,nn,drawb)
 % nn is the subdivision level
 hold on
 %%% DRAW CURVE HERE %%%
 % Plot the curve segment as a random color
 [x,y] = decas_subdiv2(B(1,:),B(2,:),nn);
 plot(x,y,'Color',[rand,rand,rand]);
 if drawb == 1 
    %%% Plot the Bezier points and segments  as red + %%%
    plot(B(1,:),B(2,:),'Color','r','LineStyle','-','Marker','+');
 else
    %%% Plot the Bezier points as red + %%%
    plot(B(1,:),B(2,:),'Color','r','LineStyle','none','Marker','+');
 end
end

