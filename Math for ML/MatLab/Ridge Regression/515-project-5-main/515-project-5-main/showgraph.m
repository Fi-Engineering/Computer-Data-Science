function [ll,mm] = showgraph(X,y)
%
%  Displays the graph {(x_1,y_1),...,(x_m,y_m)} 
%

Y = [X';y'];

%  Finds the smallest x and y coordinates
[xym,I] = min(Y');
ll = xym;
ll = ll - 0.5;
%  Finds the largest x and y coordinates
[xyM,J] = max(Y');
mm = xyM;
mm = mm + 0.5;

%close 
figure
hold on
plot(ll(1),ll(2))
plot(mm(1),mm(2))
plot(Y(1,:), Y(2,:),'b*')       %  plots points
end

