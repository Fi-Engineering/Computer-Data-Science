% Project 2
if ~exist('output', 'dir')
    mkdir('output')
    mkdir(['output' filesep 'part2i'])
    mkdir(['output' filesep 'part2ii'])
    mkdir(['output' filesep 'part2iii'])
    mkdir(['output' filesep 'report'])
    mkdir(['output' filesep 'code'])
end

% Test points
x = cell(5,1);
y = cell(5,1);
x{1} = [3.6942;1.3690;2.9865;5.8509;8.1929;8.2098;6.8281];
y{1} = [1.2144;3.5925;7.3933;7.9217;6.9665;4.0396;1.5600];
x{2} = [3.9806;2.2789;3.6942;6.8618;7.1820];
y{2} = [2.1087;4.2429;7.0884;6.9461;4.3852];
x{3} = [4.2334;1.0826;1.3016;4.9579;8.2435;4.8062];
y{3} = [1.0315;3.6941;5.6250;7.9624;5.5640;5.8486];
x{4} = [4.6040;2.2283;3.3741;2.1609;7.2494;6.8955;9.1702];
y{4} = [1.3364;1.6616;3.5722;6.8242;8.6535;3.7957;2.8608];
x{5} = [5.4297;5.2275;2.9865;1.4532;2.1778;3.2898;6.8113;9.0691;7.2999;7.2157;9.2713;7.4853;6.4575];
y{5} = [4.6494;1.9055;1.7429;3.8974;8.0030;6.7429;9.1209;7.2917;6.4380;2.8404;2.7795;0.9502;1.3974];
% More teste points

%% Part 2i and 2ii
show_plot = true;
for i = 1:length(x)
    [dx, dy, Bx, By] = interpnatxy(x{i}, y{i}, show_plot);
    % Part 2i Tables
    T = table(dx, dy, 'VariableNames', {'dx', 'dy'} );
    % Write data to text file
    fname = ['output' filesep 'part2i' filesep sprintf('%d.txt',i)];
    writetable(T, fname)
    % Part 2ii
    T = table(Bx, By, 'VariableNames', {'Bx', 'By'} );
    % Write data to text file
    fname = ['output' filesep 'part2ii' filesep sprintf('%d.txt',i)];
    writetable(T, fname)
    % Part 2ii Images
    if ishandle(1)
        imname = ['output' filesep 'part2ii' filesep sprintf('img%d.png',i)];
        saveas(gcf, imname);
        close all
    end
end

%% Part 2iii
for i = 1:2
    fprintf(['Please select >= 5 points for the spline ', ...
             '(no requirements on how you pick them)\n'])
    figure;
    [x_, y_] = getpoints;
    [dx, dy, Bx, By] = interpnatxy(x_, y_, true);
    imname = ['output' filesep 'part2iii' filesep sprintf('img%d.png',i)];
    saveas(gcf, (imname));
    close all
end


