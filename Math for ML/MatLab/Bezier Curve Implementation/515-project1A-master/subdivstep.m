
%SUBDIVSTEP Summary of this function goes here
%   takes a 2 × 4 × l array lpoly consisting of l control polygons and 
%   produces a 2 × 4 × 2l array sdpoly in which each control polygon lpoly(:,:,i) 
%   is subdivided into two control polygons using subdecas function. Here,
%   l is some power of 2.
function [cpolyResult] = subdivstep(cpoly)
    [r,l] = size(cpoly);
    n = 2;
    j = 1;
    figure;
    hold on;
    cpolyResult = cell(r,2*l);
    for i=1:l
        A = cpoly{1,i};
        [u,l] = subdecas(A,n);
        B = [u,l];
        %subplot(5,2,i);plot(B(1,:),B(2,:))
        plot(B(1,:),B(2,:));
        cpolyResult{1,j} = u;
        cpolyResult{1,j+1} = l;
        j = j+2;
    end
    hold off
end


%function sdpoly = subdivstep(lpoly)
%SUBDIVSTEP Summary of this function goes here
%   takes a 2 × 4 × l array lpoly consisting of l control polygons and 
%   produces a 2 × 4 × 2l array sdpoly in which each control polygon lpoly(:,:,i) 
%   is subdivided into two control polygons using subdecas function. Here,
%   l is some power of 2.
%[x,y,l] = size(lpoly);
%sdpoly = zeros(x,y,2*l);
%for i=1:l

%  (sdpoly(:,:,i),sdpoly(:,:,l+i) = subdecas(lpoly(:,:,i));
%end
%end
%___________________________
%SUBDIVSTEP Summary of this function goes here
%   takes a 2 × 4 × l array lpoly consisting of l control polygons and 
%   produces a 2 × 4 × 2l array sdpoly in which each control polygon lpoly(:,:,i) 
%   is subdivided into two control polygons using subdecas function. Here,
%   l is some power of 2.




