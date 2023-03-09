%  To input data points from a window on the screen
%  Left click on mouse to input points
%  middle, right or return to end input



function [x, y] = getpoints

cla
%plot(0:10, zeros(11,1));
axis([0 10 0 10])
hold on
quit = 1;
x = [];
y = [];
 while quit == 1 
   [px, py, quit] = ginput(1);
   if quit == 1
      plot(px,py, '*');
      x = [x;px];
      y = [y;py];
   end
 end
hold off
% Checking that x, y are column vectors
%p = size(x,1)
%q = size(x,2)
end