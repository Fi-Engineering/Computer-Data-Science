function get_output_5
% Project 4
if ~exist('output', 'dir')
    mkdir('output')
    mkdir(['output' filesep 'part1'])
    mkdir(['output' filesep 'part2'])
    mkdir(['output' filesep 'part3'])
    mkdir(['output' filesep 'part4'])
    mkdir(['output' filesep 'images'])
    mkdir(['output' filesep 'code'])
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This part is vital for the autograder so everyone gets the same results
% Comment out this part below if using this for the report
rng(97922758)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

X3 = [-10; -8; -6; -4; -2; 2; 4; 6; 8; 10; -9; -7; -5; -3; -1; 1; 3; 5; 7; 9];
y3 = [-3; 1; 0; 0; 1.5; 4; 6; 5; 1; 8; -2.5; 0.5; 1.5; -1; -0.5; 3.5; 5.5; 2.5; 4.5; 5];

X13 = 15*randn(50,1);
ww13 = 1;
y13 = X13*ww13 + 10*randn(50,1) + 20;

X = [-10, 11; -6, 5; -2, 4; 0, 0; 1, 2; 2, -5; 6, -4; 10, -6];
y = [0; -2.5; 0.5; -2; 2.5; -4.2; 1; 4];

X8 = 10*randn(50,2);
ww = [1; 2];
y8 = X8*ww + 10*randn(50,1) + 10;

X10 = 10*randn(100,2);
ww2 = [1; 2];
y10 = X10*ww2 + 10*randn(100,1) + 15;

X20 = randn(50,30);
ww20 = [0; 2; 0; -3; 0; -4; 1; 0; 2; 0; 2; 3; 0; -5; 6; 0; 1; 2; 0; 10; 0; 0; 3; 4; 5; 0; 0; -6; -8; 0];
y20 = X20*ww20 + randn(50,1)*0.1 + 5;

X_test = cell(6,1);
y_test = cell(6,1);
X_test{1} = X3;
y_test{1} = y3;
X_test{2} = X13;
y_test{2} = y13;
X_test{3} = X;
y_test{3} = y;
X_test{4} = X8;
y_test{4} = y8;
X_test{5} = X10;
y_test{5} = y10;
X_test{6} = X20;
y_test{6} = y20;


%% Autograded part
rho = 10;
for k = [ -2, -1, 0, 1, 2, 3 ]
    K = 10^k;
    for i = 1:length(X_test)
        [w1,b1,xi1,w2,b2,xi2,alpha2,w3,b3,xi3,w4,b4,xi4] = reg3(X_test{i},y_test{i},K);
        % For autograder
        % Part 1
        T = table([w1(:);b1(:);xi1(:)], 'VariableNames', {'vars'});
        fname = ['output' filesep 'part1' filesep sprintf('ridgeregv1_%d_%d.txt',k+2, i)];
        writetable(T, fname)
        % Part 2
        T = table([w2(:);b2(:);xi2(:);alpha2(:)], 'VariableNames', {'vars'});
        fname = ['output' filesep 'part2' filesep sprintf('ridgeregb1_%d_%d.txt',k+2, i)];
        writetable(T, fname)
        % Part 3
        T = table([w3(:);b3(:);xi3(:)], 'VariableNames', {'vars'});
        fname = ['output' filesep 'part3' filesep sprintf('ridgeregv2_%d_%d.txt',k+2, i)];
        writetable(T, fname)
        % Part 4
        if k == 0 % No regularizaiton by K in part 4
            T = table([w4(:);b4(:);xi4(:)], 'VariableNames', {'vars'});
            fname = ['output' filesep 'part4' filesep sprintf('reglq_%d.txt', i)];
            writetable(T, fname)
        end
        % Write data to text file
        if ishandle(1)
            imname = ['output' filesep 'images' filesep sprintf('img_%d_%d.png',k+2,i)];
            saveas(gcf, imname);
            close all
        end
    end
end


end % function



% function [w1,w2,w3,w4] = reg3(X,y,K)
function [w1,b1,xi1,w2,b2,xi2,alpha2,w3,b3,xi3,w4,b4,xi4] = reg3(X,y,K)
% Calls four regression methods
% Ridge regression minimizing w, b, not penalizing b
% Ridge regression minimizing w, b, not penalizing b, using the KKT eqs
% Ridge regression minimizing w, b, penalizing b
% Least squares, penalizing b
% X is an m x n matrix, y a m x 1 column vector
% weight vector w, intercept b
%
m = size(y,1); n = size(X,2);
[w1,~,b1,xi1,~] = ridgeregv1(X,y,K);
[w2,b2,xi2,~,alpha2] = ridgeregb1(X,y,K);
[w3,~,b3,xi3,~] = ridgeregv2(X,y,K);
[w4,~,b4,xi4,~] = reglq(X,y);
fprintf('b1 = %.15f \n',b1)
fprintf('b2 = %.15f \n',b2)
fprintf('b3 = %.15f \n',b3)
fprintf('b4 = %.15f \n',b4)

if n == 1
    [ll,mm] = showgraph(X,y);
    hold off
    [ll,mm] = showgraph(X,y);
    ww1 = [w1;-1]; ww3 = [w3;-1];
    ww4 = [w4;-1];
    n1 = sqrt(ww1'*ww1); n3 = sqrt(ww3'*ww3);
    n4 = sqrt(ww4'*ww4);
    l1 = makeline(ww1,-b1,ll,mm,n1);
    % best fit, ridge 1
    l2 = makeline(ww3,-b3,ll,mm,n3);
    % best fit,
    % ridge penalizing b
    l3 = makeline(ww4,-b4,ll,mm,n4);
    % best fit, least squares
    plot(l1(1,:),l1(2,:),'-m','LineWidth',1.2) % magenta best
    plot(l2(1,:),l2(2,:),'-r','LineWidth',1.2) % red
    plot(l3(1,:),l3(2,:),'-b','LineWidth',1.2) % blue
    hold off
elseif n == 2
    offset = 5;
    [ll,mm] = showpoints(X,y,offset);
    axis equal
    axis([ll(1) mm(1) ll(2) mm(2)]);
    view([-1 -1 1]);
    xlabel('X','fontsize',14);ylabel('Y','fontsize',14);
    zlabel('Z','fontsize',14);
    hold off
    [ll,mm] = showpoints(X,y,offset);
    C3= [0 0 1]; % blue
    C1 = [1 0 1]; % magenta
    C2 = [1 0 0]; % red
    plotplane(w1,b1,ll,mm,C1)    % best fit, ridge 1, magenta
    plotplane(w3,b3,ll,mm,C2)    % best fit, ridge
                                 % penalizinbg b, red
    plotplane(w4,b4,ll,mm,C3)    % best fit, least squares, blue
    axis equal
    axis([ll(1) mm(1) ll(2) mm(2)]);
    view([-1 -1 1]);
    xlabel('X','fontsize',14);
    ylabel('Y','fontsize',14);
    zlabel('Z','fontsize',14);
    hold off
end

end
