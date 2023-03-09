%
% plots a piecewise linear function corresponding to 
% a vector u = (u_1, ..., u_n)
%

function drawplf(u)
%     disp(u);
    x = 0:length(u);
    x = x/length(u);
    x = repelem(x,2);
    x = x(2:2*length(u)+1);
    u = repelem(u,2);
    figure
    graph = plot(x,u,'r');
    title('Plot of the vector u')
    graph.LineWidth = 2
end
