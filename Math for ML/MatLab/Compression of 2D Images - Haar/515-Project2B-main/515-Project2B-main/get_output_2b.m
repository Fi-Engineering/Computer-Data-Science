%% Initializiation
% Create output directories
if ~exist('output', 'dir')
    mkdir('output')
    mkdir(['output', filesep, 'part1'])
    mkdir(['output', filesep, 'part3'])
    mkdir(['output', filesep, 'report'])
end

test_val = cell(6,1);

% For your convenience we have written out the matrices here from parts 1 and 3.
% We will test the results of your code in the autograder, as well

% From Part 1
T = [
    1212,  -306,  -146,   -54,   -24,   -68,   -40,     4;
      30,    36,   -90,    -2,     8,   -20,     8,    -4;
     -50,   -10,   -20,   -24,     0,    72,   -16,   -16;
      82,    38,   -24,    68,    48,   -64,    32,     8;
       8,     8,   -32,    16,   -48,   -48,   -16,    16;
      20,    20,   -56,   -16,   -16,    32,   -16,   -16;
      -8,     8,   -48,     0,   -16,   -16,   -16,   -16;
      44,    36,     0,     8,    80,   -16,   -16,     0; 
];

Pbad = [
    576, 704, 1152, 1280, 1344, 1472, 1536, 1536;
    704, 640, 1156, 1088, 1344, 1408, 1536, 1600;
    768, 832, 1216, 1472, 1472, 1536, 1600, 1600;
    832, 832,  960, 1344, 1536, 1536, 1600, 1536;
    832, 832,  960, 1216, 1536, 1600, 1536, 1536;
    960, 896,  896, 1088, 1600, 1600, 1600, 1536;
    768, 768,  832,  832, 1280, 1472, 1600, 1600;
    448, 768,  704,  640, 1280, 1408, 1600, 1600;
];

% From Part 3
A = [
    100, 103,  99,  97,  93,  94, 78, 73;
    102,  97, 100, 111, 113, 104, 96, 82;
     99, 109, 104,  95,  93,  92, 88, 76;
    114, 104,  99, 102,  93,  82, 74, 74;
     96,  91,  91,  87,  79,  78, 77, 76;
     90,  88,  83,  78,  77,  74, 76, 76;
     92,  81,  73,  72,  69,  65, 66, 62;
     75,  70,  69,  65,  60,  55, 61, 65;
];


A2 = [
    100, 100,  95,  95,  92,  92, 76, 76;
    103, 103,  98,  98, 106, 106, 90, 90;
     99, 109,  99,  99,  96,  96, 81, 81;
    114, 104, 104, 104,  91,  91, 76, 76;
     91,  91,  86,  86,  76,  76, 76, 76;
     91,  91,  86,  86,  76,  76, 76, 76;
     82,  82,  76,  76,  66,  66, 66, 66;
     74,  74,  69,  69,  58,  58, 59, 59;
];

C1 = [
  255, 52, 15, 21, 0, 0, 0, 0;
   78,  0,  0, 22, 0, 0, 0, 0; 
    0,  0,  0,  0, 0, 0, 0, 0;
   38,  0,  0,  0, 0, 0, 0, 0;
    0, 11,  0,  0, 0, 0, 0, 0;
    0,  0,  0,  0, 0, 0, 0, 0;
    0,  0,  0,  0, 0, 0, 0, 0;
   15,  0,  0,  0, 0, 0, 0, 0;
];


% Autograde test values
% From questions
test_val{1} = T;
test_val{2} = Pbad;
test_val{3} = A;
test_val{4} = A2;
test_val{5} = C1;
% Random values
test_val{6} = [
    6, 3, 1, 8, 2, 8, 3, 1;
    3, 4, 5, 1, 2, 2, 1, 7;
    8, 4, 3, 6, 8, 1, 3, 8;
    1, 7, 2, 6, 1, 3, 1, 5;
    8, 7, 2, 5, 2, 4, 5, 1;
    5, 1, 8, 2, 1, 1, 7, 7;
    6, 2, 6, 5, 4, 8, 6, 3;
    8, 3, 4, 3, 1, 3, 1, 3;
];
test_val{7} = [
    6, 5, 6, 6, 3, 1, 7, 2, 2, 7, 1, 2, 1, 4, 5, 2;
    1, 6, 1, 5, 2, 8, 6, 2, 5, 3, 1, 1, 5, 3, 6, 6;
    1, 1, 1, 7, 5, 2, 2, 3, 8, 6, 3, 7, 3, 7, 8, 3;
    6, 2, 6, 3, 1, 3, 2, 3, 2, 3, 3, 2, 5, 2, 4, 7;
    5, 5, 3, 2, 4, 7, 1, 2, 3, 5, 6, 2, 4, 1, 1, 6;
    5, 4, 6, 1, 1, 4, 1, 3, 4, 7, 8, 6, 4, 7, 7, 5;
    6, 8, 6, 7, 1, 7, 4, 8, 1, 5, 8, 8, 2, 6, 6, 2;
    6, 7, 5, 2, 7, 4, 6, 6, 6, 3, 4, 5, 3, 6, 3, 8;
    7, 6, 6, 4, 3, 3, 6, 5, 4, 3, 2, 6, 1, 6, 8, 3;
    3, 1, 2, 5, 5, 1, 5, 2, 8, 4, 7, 2, 8, 4, 2, 8;
    6, 1, 6, 2, 8, 6, 1, 2, 4, 4, 7, 8, 6, 4, 6, 2;
    5, 1, 8, 6, 4, 4, 6, 1, 5, 3, 6, 5, 8, 7, 5, 3;
    4, 7, 7, 4, 6, 4, 2, 8, 2, 5, 6, 6, 2, 3, 4, 1;
    1, 8, 1, 2, 7, 5, 2, 6, 4, 6, 1, 1, 8, 7, 2, 6;
    7, 6, 3, 7, 4, 1, 1, 5, 2, 4, 6, 7, 7, 7, 1, 2;
    3, 2, 3, 1, 6, 3, 2, 3, 7, 4, 4, 6, 5, 7, 4, 1;
];
test_val{8} = kron(test_val{6}, test_val{7});


%% Part 1
dirname = ['output' filesep 'part1' filesep ];
for i = 1:length(test_val)
    haar2d_val = haar2D(test_val{i});
    % It doesn't actually make sense to run haar_inv on the inputs
    %  as these are not haar coefficients, but it will be used for testing
    haar2d_inv_val = haar_inv2D(test_val{i});
    iden = haar_inv2D(haar2D(test_val{i}));
    if norm(iden - test_val{i}) > eps
        warning(['Identity function not working - ', ...
                'something is wrong with your haar2D or ', ...
                'haar_inv2D.' ])
    end
    T = table(haar2d_val, 'VariableNames', {'haar2d'} );
    fname = sprintf('%shaar_%d.txt',dirname,i);
    writetable(T, fname)
    T = table(haar2d_inv_val, 'VariableNames', {'haar_inv2d'} );
    fname = sprintf('%shaar_inv_%d.txt',dirname,i);
    writetable(T, fname)
    T = table(iden, 'VariableNames', {'iden'} );
    fname = sprintf('%siden_%d.txt',dirname,i);
    writetable(T, fname)
end

%% Part 3
dirname = ['output' filesep 'part3' filesep ];
for i = 1:length(test_val)
    haar2d_val = haar2D_n(test_val{i});
    % It doesn't actually make sense to run haar_inv on the inputs
    %  as these are not haar coefficients, but it will be used for testing
    haar2d_inv_val = haar_inv2D_n(test_val{i});
    iden = haar_inv2D_n(haar2D_n(test_val{i}));
    if norm(iden - test_val{i}) > 1e-10 
        % We use a larger error value tolerance due to sqrt precision
        disp(norm(iden - test_val{i}))
        warning([sprintf('%d: Identity function not working - ', i), ...
                'something is wrong with your haar2D_n or ', ...
                'haar_inv2D_n.' ])
    end
    T = table(haar2d_val, 'VariableNames', {'haar2d_n'} );
    fname = sprintf('%shaar_%d.txt',dirname,i);
    writetable(T, fname)
    T = table(haar2d_inv_val, 'VariableNames', {'haar_inv2d_n'} );
    fname = sprintf('%shaar_inv_%d.txt',dirname,i);
    writetable(T, fname)
    T = table(iden, 'VariableNames', {'iden'} );
    fname = sprintf('%siden_%d.txt',dirname,i);
    writetable(T, fname)
end




