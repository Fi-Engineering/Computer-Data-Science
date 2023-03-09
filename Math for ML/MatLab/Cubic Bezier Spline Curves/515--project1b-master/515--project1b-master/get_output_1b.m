% Project 1B
if ~exist('output', 'dir')
    mkdir('output')
    mkdir('output/part1')
    mkdir('output/part2')
    mkdir('output/part3')
    mkdir('output/code')
end
dx = cell(5,1);
dy = cell(5,1);
dx{1}= [3.6942;1.3690;2.9865;5.8509;8.1929;8.2098;6.8281];
dy{1}= [1.2144;3.5925;7.3933;7.9217;6.9665;4.0396;1.5600];
dx{2}= [3.9806;2.2789;3.6942;6.8618;7.1820];
dy{2}= [2.1087;4.2429;7.0884;6.9461;4.3852];
dx{3}= [4.2334;1.0826;1.3016;4.9579;8.2435;4.8062];
dy{3}= [1.0315;3.6941;5.6250;7.9624;5.5640;5.8486];
dx{4}= [4.6040;2.2283;3.3741;2.1609;7.2494;6.8955;9.1702];
dy{4}= [1.3364;1.6616;3.5722;6.8242;8.6535;3.7957;2.8608];
dx{5}= [5.4297;5.2275;2.9865;1.4532;2.1778;3.2898;6.8113;9.0691;7.2999;7.2157;9.2713;7.4853;6.4575];
dy{5}= [4.6494;1.9055;1.7429;3.8974;8.0030;6.7429;9.1209;7.2917;6.4380;2.8404;2.7795;0.9502;1.3974];

showb = 1;
nn = 6;
% Part 1 and 2
for showb = [ false, true ]
    for i = 1:length(dx)
        N = length(dx{i})-1;
        [Bx, By] = bspline2b(dx{i}, dy{i}, N, nn, showb);
        T = table(Bx, By, 'VariableNames', {'Bx', 'By'} );
        % Write data to text file
        fname = ['output' filesep sprintf('part1/%d.txt',i)];
        writetable(T, fname)
        if ishandle(1)
            imname = sprintf('output/part2/showb%d_%d.png', showb, i);
            saveas(gcf, imname);
            close all
        end
    end
end

% Part 3
for i = 1:2
    fprintf(['Please select >= 5 points for the spline ', ...
             '(no requirements on how you pick them)\n'])
    figure;
    [dx, dy] = getpoints;
    N = size(dx,1)-1;
    nn = N;
    fprintf('N = %d \n', N)
    bspline2b(dx,dy,N, nn, showb);
    saveas(gcf, sprintf('output/part3/%d.png', i));
    close all
end
