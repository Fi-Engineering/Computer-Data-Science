function  plotplane(w,b,ll,mm,C1)
% 
% This function plots a plane of equation
% z = (x, y)*w + b 
% ll(1) <= x <= mm(1)
% ll(2) <= y <= mm(2)
%
% C1 = color

% ll
% mm
% u = ll(1):0.5:mm(1);
% v = ll(2):0.5:mm(2);
u = [ll(1) mm(1)];
v = [ll(2) mm(2)];
[U, V] = meshgrid(u,v);
m = size(U,1);
n = size(U,2);
for i  = 1:m
   for j = 1:n
       W(i,j) = w'*[U(i,j); V(i,j)] +b;
   end
end
Z = W;
% C1 = [1 0 1];  % magenta

plane = surf(U,V,Z);
set(plane,'facecolor',C1);

end

