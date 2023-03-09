% Project 2A
if ~exist('output', 'dir')
    % Create output directories
    mkdir('output')
    mkdir(['output', filesep, 'part1'])
    mkdir(['output', filesep, 'part2'])
    mkdir(['output', filesep, 'part3'])
    mkdir(['output', filesep, 'part4'])
    mkdir(['output', filesep, 'report'])
    mkdir(['output', filesep, 'code'])
end

test_val = cell(6,1);

test_val{1} = [0, 1];
test_val{2} = [0, 1, 2, 3];
test_val{3} = [2, 1, 0, -1, 0, 2, 3, 4];
test_val{4} = [0, 1, 0, -1, 0, 1, 0, -1];
% Large tests
test_val{5} = [ 3, 1, -5, 2, -3, 3, 4, 4, ... 
                0, -6, -4, 7, -5, 6, 1, 8, ...
                -6, 0, -6, 8, -7, 5, 6, 6, ...
                -6, -1, -3, 5, -1, 7, -5, -3 ];
test_val{6} = [ 8, -7, 0, -1, 5, 5, -5, 0, ...
                0, 3, 4, 5, -3, 3, 3, -5, ...
                -6, 0, 8, -2, 2, -4, 5, -3, ...
                1, 4, 7, 8, 1, -5, -5, -3, ...
                6, -3, 6, -4, 7, -2, -4, -3, ...
                2, 0, -2, 6, 2, 1, 7, -3, ...
                5, 5, -1, 2, -6, -7, 1, 5, ...
                7, -5, 2, 0, -7, -2, -5, 5 ];
% Tests from Document
u = [0, 2, 4, 6, 6, 4, 2, 1, -1, -2, -4, -6, -6, -4, -2, 0];
u2 = [ u, u ];
u3 = [ u2, u2 ];
w = [ u3, u3 ];
test_val{7} = u;
test_val{8} = w;

%% Part 1
for i = 1:length(test_val)
    % If you want to see the windows pop up, change visible to true
    fig = figure('Visible', false);
    drawplf(test_val{i})
    saveas(fig, ['output', filesep, 'part1', filesep, sprintf('%d.png',i)]);
    close
end

%% Part 2
dirname = ['output' filesep 'part2' filesep ];
for i = 1:length(test_val)
    haar_val = haar(test_val{i});
    % It doesn't actually make sense to run haar_inv on the inputs
    %  as these are not haar coefficients, but it will be used for testing
    haar_inv_val = haar_inv(test_val{i});
    iden = haar_inv(haar(test_val{i}));
    if norm(iden - test_val{i}) > eps
        warning(['Identity function not working - ', ...
                'something is wrong with your haar or', ...
                'haar_inv.' ])
    end
    T = table(haar_val, 'VariableNames', {'haar'} );
    fname = sprintf('%shaar_%d.txt',dirname,i);
    writetable(T, fname)
    T = table(haar_inv_val, 'VariableNames', {'haar_inv'} );
    fname = sprintf('%shaar_inv_%d.txt',dirname,i);
    writetable(T, fname)
    T = table(iden, 'VariableNames', {'iden'} );
    fname = sprintf('%siden_%d.txt',dirname,i);
    writetable(T, fname)
end

%% Part 3
dirname = ['output' filesep 'part3' filesep ];
for i = 1:length(test_val)
    n = length(test_val{i});
    for k = 1:log2(n)
        haar_steps_k = haar_step(test_val{i}, k);
        T = table(haar_steps_k,'VariableNames', {'haar_steps'} );
        fname = sprintf('%shaar_step_%d_%d.txt',dirname,i,k);
        writetable(T, fname)
    end
end

%% Part 4
dirname = ['output' filesep 'part4' filesep ];
for i = 1:length(test_val)
    n = length(test_val{i});
    for k = 1:log2(n)
        haar_inv_steps_k = haar_inv_step(test_val{i}, k);
        iden_steps_k = haar_inv_step(haar_step(test_val{i}, k), k);
        if norm(iden_steps_k - test_val{i}) > eps
            warning(['Identity function not working - ', ...
                    'something is wrong with your haar_step or ', ...
                    'haar_inv_step.' ])
        end
        T = table(haar_inv_steps_k,'VariableNames', {'haar_inv_steps'} );
        fname = [sprintf('%shaar_inv_step_%d_%d.txt', dirname, i, k)];
        writetable(T, fname)
        T = table(iden_steps_k,'VariableNames', {'iden_steps'} );
        fname = [sprintf('%siden_step_%d_%d.txt', dirname, i, k)];
        writetable(T, fname)
    end
end


