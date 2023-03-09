function [ll,mm] = showpoints(X,y,offset)
%
%  Displays the graph {(x_1,y_1),...,(x_m,y_m)} 
%


%  Finds the smallest x and y coordinates
[xym,I] = min(X);
ll = xym;
ll = ll - offset;
%  Finds the largest x and y coordinates
[xyM,J] = max(X);
mm = xyM;
mm = mm + offset;
Y = X';
Z = [Y;y'];
x = Z(1,:);
y = Z(2,:);
z = Z(3,:);

%close 
figure
% grid on
% hold on
% plot3(x, y, z,'*','Color',[0.9290,0.6940,0.1250])       %  plots points (orange)
plot3(x, y, z,'b*')       %  plots points (blue)

hold on
end

